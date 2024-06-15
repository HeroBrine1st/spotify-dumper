#!/usr/bin/env python
import os
from distutils.core import setup

# https://stackoverflow.com/a/53069528
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(
    name="spotify_dumper",
    version="1.0",
    description="Dump your playlists from spotify",
    author="HeroBrine1st Erquilenne",
    url="https://github.com/HeroBrine1st/nmssoundunpack",
    packages=["spotify_dumper"],
    install_requires=install_requires,
    scripts=['bin/dump-spotify-data'],
)
