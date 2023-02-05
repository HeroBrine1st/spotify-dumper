# Spotify dumper

Fancy utulity for dumping playlists and liked songs from your Spotify account into file or stdout.

## Installation

1. Run ``pip install git+https://github.com/HeroBrine1st/spotify-dumper.git``

## Usage
```
usage: dump-spotify-data [-h] -i CLIENT_ID -s CLIENT_SECRET [-k] [-l] [--listen-port LISTEN_PORT] [--overwrite] [-f FILTER] [-F {json,txt}] [--no-playlists] [output_file]

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
Client ID and secret are required even with --keep because Spotify tokens are valid for only six hours or less, therefore requiring refreshing, which itself requires those tokens.
```
P.s. run with ``--help`` for actual usage as above may be out of date.

Example command: ``dump-spotify-data --client-id asdfasdfasdf3rge4re_replacethis --client-secret asdfasdfvawerf_replacethis -F txt output.txt``
