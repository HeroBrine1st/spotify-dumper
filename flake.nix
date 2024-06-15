{
  description = "Fancy utility for dumping your playlists and liked songs from spotify";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem(system: {
    packages = let
      pkgs = import nixpkgs { inherit system; };
    in {
      default = pkgs.python3Packages.callPackage ./default.nix {};
    };
  });
}
