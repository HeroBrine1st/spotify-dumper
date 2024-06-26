# Spotify dumper

Fancy utility for dumping playlists and liked songs from your Spotify account into file or stdout.

https://github.com/HeroBrine1st/spotify-dumper/assets/22197536/4edca898-200b-4ae4-a7c0-23b1a905b152

## Installation

1. Install Git
2. Run ``pip install git+https://github.com/HeroBrine1st/spotify-dumper.git``

Also, this tool can be run without installation if you have nix package manager:

```
nix run github:HeroBrine1st/spotify-dumper -- --help
```

## Usage
```
usage: dump-spotify-data [-h] [-i CLIENT_ID] [-s CLIENT_SECRET] [-k] [-l] [--listen-port LISTEN_PORT] [--overwrite] [-f FILTER] [-F {json,txt}] [--no-playlists] [output_file]

Dump spotify playlists to JSON file.

positional arguments:
  output_file           Write dump to a file

options:
  -h, --help            show this help message and exit
  -i CLIENT_ID, --client-id CLIENT_ID
                        Spotify client id
  -s CLIENT_SECRET, --client-secret CLIENT_SECRET
                        Spotify client secret
  -k, --keep, -keep-auth
                        Save authorization token in current working directory for future use. Default: authorization token forgotten immediately after exit.
                        Required only for first time and intended for long-term usage without attached console, e.g. backing up your playlist data regularly.
  -l, --liked, --liked-songs, --liked-tracks
                        Also add liked songs to dump if this flag is present.
  --listen-port LISTEN_PORT
                        For advanced users. Change port of internal HTTP server that is responsible for taking auth code.
  --overwrite           Overwrite destination file.
  -f FILTER, --filter FILTER
                        Filter playlists exactly matching (part of) name, but ignoring case.
  -F {json,txt}, --format {json,txt}
                        Output format (default: txt)
  --no-playlists        Do not include playlists to dump

Get client ID and secret at https://developer.spotify.com/dashboard/applications.
Add http://localhost:30700/callback to Redirect URIs in settings of your application.
```

Don't forget to add `http://localhost:30700/callback` to Redirect URIs in settings of your application.

P.s. run with ``--help`` for actual usage as above may be out of date.

Example command: ``dump-spotify-data --client-id asdfasdfasdf3rge4re_replacethis --client-secret asdfasdfvawerf_replacethis -F txt output.txt``

P.s.s. If you're on windows, you probably should use ``python -m spotify_dumper`` with arguments
