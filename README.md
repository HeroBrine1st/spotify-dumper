# Spotify dumper

Fancy utility for dumping playlists and liked songs from your Spotify account into file or stdout.

https://github.com/HeroBrine1st/spotify-dumper/assets/22197536/4edca898-200b-4ae4-a7c0-23b1a905b152

(old video, currently this command is `dump-spotify-data --include-user-playlists --include-liked-tracks`, and assuming it has been called with `--keep` previously in the same directory)

## Installation

1. Install Git
2. Run ``pip install git+https://github.com/HeroBrine1st/spotify-dumper.git``

Also, this tool can be run without installation if you have nix package manager:

```
nix run github:HeroBrine1st/spotify-dumper -- --help
```

## Usage

```
usage: dump-spotify-data [-h] [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET] [-k] [--listen-port LISTEN_PORT] [--overwrite] [-F {json,txt}] [-u] [-l] [-i URI] [-x URI] [output_file]

Dump spotify playlists to JSON file.

positional arguments:
  output_file           Write dump to a file

options:
  -h, --help            show this help message and exit
  --client-id CLIENT_ID
                        Spotify client id
  --client-secret CLIENT_SECRET
                        Spotify client secret
  -k, --keep, --keep-auth
                        Save authorization token in current working directory for future use. Default: authorization token forgotten immediately after exit.
                        Required only for first time and intended for long-term usage without attached console, e.g. backing up your playlist data regularly.
  --listen-port LISTEN_PORT
                        For advanced users. Change port of internal HTTP server that is responsible for taking auth code.
  --overwrite           Overwrite destination file.
  -F {json,txt}, --format {json,txt}
                        Output format (default: txt)
  -u, --include-user-playlists
                        Include user's playlists (owned and followed)
  -l, --include-liked-tracks
                        Include liked tracks as a playlist
  -i URI, --include URI
                        Include additional playlists by their URI in the format spotify:playlist:<base62-encoded id>. Can be repeated for multiple playlists
  -x URI, --exclude URI
                        Exclude playlists by their URI in the format spotify:playlist:<base62-encoded id>. Can be repeated for multiple playlists. This option is evaluated last and overrides all other inclusion rules

Get client ID and secret at https://developer.spotify.com/dashboard/applications.
Add http://127.0.0.1:30700/callback to Redirect URIs in settings of your application.
```

Don't forget to add `http://127.0.0.1:30700/callback` to Redirect URIs in settings of your application.

P.s. run with ``--help`` for actual usage as above may be out of date.

Example command:
``dump-spotify-data --client-id asdfasdfasdf3rge4re_replacethis --client-secret asdfasdfvawerf_replacethis -F txt --include-user-playlists output.txt``

P.s.s. If you're on windows, you probably should use ``python -m spotify_dumper`` with arguments

### I don't get playlists owned by spotify!

<sup>...And they fail to be included by --include</sup>

Starting with December
2024, [Spotify removed algorithmic and Spotify-owned editorial playlists from responses](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api).
If you have no application created before that, you're out of luck.
