{ lib, buildPythonPackage, requests, rich }: buildPythonPackage rec {
  name = "spotify-dumper";
  version = "1.0.0";
  src = ./.;  
  doCheck = false;
  dependencies = [
    requests
    rich
  ];
  meta.mainProgram = "dump-spotify-data";
}
