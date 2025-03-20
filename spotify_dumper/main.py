#!/bin/python
import argparse
import json
import sys

from datetime import timedelta
from pathlib import Path
from typing import Optional, TextIO, Any

from requests import HTTPError
from rich.console import Console
from rich.progress import Progress, BarColumn, SpinnerColumn, ProgressColumn, Task
from rich.table import Column
from rich.text import Text
from rich.theme import Theme
from spotify_dumper.spotify import SpotifyAPI, NoApiPairError

THEME_DONE = "blue"

# region I want it blue, I get it blue
class TimeElapsedColumnLocal(ProgressColumn):
    """Renders time elapsed."""

    def render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--", style="progress.elapsed")
        delta = timedelta(seconds=int(elapsed))
        return Text(str(delta), style=THEME_DONE if task.finished else "progress.elapsed")

class TextColumnLocal(ProgressColumn):
    """A column containing text."""

    def __init__(
        self,
        text_format: str,
    ) -> None:
        self.text_format = text_format
        super().__init__(table_column=Column(no_wrap=True))

    def render(self, task: "Task") -> Text:
        _text = self.text_format.format(task=task)
        text = Text.from_markup(_text, style=THEME_DONE if task.finished else "none")
        return text

class MofNCompleteColumnLocal(ProgressColumn):
    def __init__(self, separator: str = "/", table_column: Optional[Column] = None):
        self.separator = separator
        super().__init__(table_column=table_column)

    def render(self, task: "Task") -> Text:
        """Show completed/total."""
        completed = int(task.completed)
        total = int(task.total) if task.total is not None else "?"
        total_width = len(str(total))
        return Text(
            f"{completed:{total_width}d}{self.separator}{total}",
            style=THEME_DONE if task.finished else "progress.download",
            justify="right"
        )

theme = Theme(
    {
        "bar.finished": THEME_DONE
    }
)

# endregion


def stylize_path(path: Path) -> Text:
    parent = Text(str(path.parent) + "/")
    parent.stylize("repr.path")
    filename = Text(str(path.name))
    filename.stylize("repr.filename")
    if str(path.parent) == ".": return filename
    return parent.append(filename)

def main() -> None:
    args = parser.parse_args()
    output_file = args.output and args.output != "-" and Path(args.output)

    if output_file:
        if not output_file.parent.is_dir():
            print("File cannot be created", file=sys.stderr)
            exit(1)
        if output_file.exists() and not args.overwrite:
            print("File exists", file=sys.stderr)
            exit(1)
    else:
        # UX or semantics?
        # Hard choice... let's go machine way
        if args.overwrite:
            print("Cannot overwrite the stdout", file=sys.stderr)
            exit(1)

    console = Console(theme=theme, file=sys.stderr)
    with console.status("Authorizing in spotify"):
        try:
            spotify = SpotifyAPI.new(
                client_id=args.client_id, client_secret=args.client_secret, listen_port=args.listen_port, keep=args.keep
            )
        except NoApiPairError:
            console.print("No client id/secret provided! Use --client-id and --client-secret arguments.")
            exit(1)
        user = spotify.get("me")
    console.print(f"⠿ Logged in as {user['display_name']}", style=THEME_DONE)

    # include_user_playlists: True | None
    # include_liked: True | None
    # playlist_uris: list[str] | None
    # excluded_playlist_uris: list[str] | None

    playlists = list()
    with console.status("Fetching playlist data") as status:
        if args.include_user_playlists:
            for response in spotify.iterate("/me/playlists?limit=50"):
                playlists += response["items"]
                status.update(f'Fetching playlist data ({len(playlists)}/{response["total"]})')
        if args.playlist_uris:
            for uri in args.playlist_uris:
                uri: str
                if args.excluded_playlist_uris and uri in args.excluded_playlist_uris:
                    continue
                try:

                    playlist = spotify.get(f"/playlists/{uri.removeprefix("spotify:playlist:")}")
                except HTTPError as e:
                    if e.response.status_code == 404:
                        console.print(f"Playlist {uri} does not exist!", style="red")
                        exit(1)
                    raise
                playlists.append(playlist)
        if args.excluded_playlist_uris:
            playlists = [
                playlist for playlist in playlists if playlist["uri"] not in args.excluded_playlist_uris
            ]
        if len(playlists) > 0:
            console.print(f'⠿ Fetched playlist data ({len(playlists)} playlists)', style=THEME_DONE)

    if not playlists:
        console.print("No playlists to fetch!", style="red")
        exit(1)

    with Progress(
        SpinnerColumn(finished_text=Text("⠿", style=THEME_DONE)),
        TextColumnLocal("[progress.description]{task.description}"),
        MofNCompleteColumnLocal(),
        BarColumn(bar_width=None),
        TimeElapsedColumnLocal(),
        console=console,
        expand=True
    ) as progress:

        # Place individual playlists first
        liked_songs_task = progress.add_task("Liked songs", total=None, visible=False, start=False)
        playlist_tasks = [progress.add_task(
            f"{playlist['name']}",
            total=playlist["tracks"]["total"], visible=False, start=False
        ) for playlist
            in playlists]
        task_playlists_total = progress.add_task("Playlists", total=len(playlists) + args.include_liked)
        task_tracks_total = progress.add_task(
            "Tracks",
            total=None if args.include_liked else sum(map(lambda x: x["tracks"]["total"], playlists))
        )

        if args.include_liked:
            progress.start_task(liked_songs_task)
            progress.update(liked_songs_task, visible=True)
            liked_songs = list()
            for response in spotify.iterate("/me/tracks", {"limit": 50}):
                liked_songs += response["items"]
                progress.update(task_id=liked_songs_task, total=response["total"], completed=len(liked_songs))
                progress.update(
                    task_id=task_tracks_total,
                    total=response["total"] + sum(map(lambda x: x["tracks"]["total"], playlists)),
                    completed=len(liked_songs)
                )
            progress.advance(task_playlists_total, 1)

        for playlist, fetch_playlist_task in zip(playlists, playlist_tasks, strict=True):
            progress.start_task(fetch_playlist_task)
            progress.update(fetch_playlist_task, visible=True)
            items = list()
            for response in spotify.iterate(playlist["tracks"]["href"], {"limit": 100}):
                items += response["items"]
                progress.update(fetch_playlist_task, completed=len(items))
                progress.advance(task_tracks_total, len(response["items"]))
            progress.advance(task_playlists_total, 1)
            playlist["tracks"] = items
        # Fix "pycharm going back in time for type-checking"
        output = playlists
        if args.include_liked:
            output.insert(0, {"name": "Liked songs", "tracks": liked_songs})
    with console.status("Writing dump to %s.." % (output_file if output_file else "stdout")):
        if output_file:
            with open(output_file, "w") as f:
                write_output(f, output, args)
            printout = Text("⠿ Playlist data are written to ", style=THEME_DONE).append(stylize_path(output_file))
        else:
            write_output(sys.__stdout__, output, args)
            printout = Text("⠿ Playlist data are written to stdout", style=THEME_DONE)
    # There's a race condition (I encountered once)
    console.print(printout)

def write_output(f: TextIO, output: list[Any], args: argparse.Namespace) -> None:
    match args.format:
        case "json":
            json.dump(output, f)
        case "txt":
            # https://github.com/caseychu/spotify-backup/blob/d0bb610af74c5845e87d23eaf758c91a51e7b20e/spotify-backup.py#L188-L199
            for playlist in output:
                f.write(playlist["name"] + '\r\n')
                for track in playlist["tracks"]:
                    if track["track"] is None:
                        continue
                    f.write(
                        "{name}\t{artists}\t{album}\t{uri}\r\n".format(
                            uri=track["track"]["uri"],
                            name=track["track"]["name"],
                            artists=", ".join([artist["name"] for artist in track["track"]["artists"]]),
                            album=track["track"]["album"]["name"]
                        )
                    )
                f.write('\r\n')

parser = argparse.ArgumentParser(
    description="Dump spotify playlists to JSON file.\n",
    epilog="Get client ID and secret at https://developer.spotify.com/dashboard/applications.\n"
           "Add http://localhost:30700/callback to Redirect URIs in settings of your application.",
    formatter_class=argparse.RawTextHelpFormatter
)

# Authorisation
parser.add_argument("--client-id", dest="client_id", help="Spotify client id")
parser.add_argument("--client-secret", dest="client_secret", help="Spotify client secret")
parser.add_argument(
    "-k", "--keep", "--keep-auth", dest="keep", action="store_true",
    help="Save authorization token in current working directory "
         "for future use. Default: authorization token forgotten immediately after exit.\n"
         "Required only for first time and intended for long-term usage without attached console, "
         "e.g. backing up your playlist data regularly."
)
parser.add_argument(
    "--listen-port", dest="listen_port", type=int, default=30700,
    help="For advanced users. Change port of internal HTTP server that is responsible for taking auth code."
)

# Output
parser.add_argument("--overwrite", dest="overwrite", action="store_true", help="Overwrite destination file.")
parser.add_argument(
    "-F", "--format", dest="format", help="Output format (default: txt)", default="txt", choices=["json", "txt"]
)
parser.add_argument(
    "output", metavar="output_file",
    help="Write dump to a file", nargs="?"
)

# Playlist selection
parser.add_argument(
    "-u", "--include-user-playlists", dest="include_user_playlists", action='store_true',
    help="Include user's playlists (owned and followed)"
)
parser.add_argument(
    "-l", "--include-liked-tracks", dest="include_liked", action="store_true",
    help="Include liked tracks as a playlist"
)
parser.add_argument(
    "-i", "--include", dest="playlist_uris", action="append", metavar="URI",
    help="Include additional playlists by their URI in the format spotify:playlist:<base64-encoded id>. Can be repeated for multiple playlists"
)
parser.add_argument(
    "-x", "--exclude", dest="excluded_playlist_uris", action="append", metavar="URI",
    help="Exclude playlists by their URI in the format spotify:playlist:<base64-encoded id>. Can be repeated for multiple playlists. This option is evaluated last and overrides all other inclusion rules"
)



if __name__ == "__main__":
    main()
