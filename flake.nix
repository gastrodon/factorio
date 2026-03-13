{
  description = "Factorio development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python3
            uv
          ];

          shellHook = ''
            # Create a project-local venv managed by uv
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              uv venv .venv
            fi
            source .venv/bin/activate

            # Install packages if not already present
            if ! python -c "import factompile" 2>/dev/null || \
               ! python -c "import draftsman" 2>/dev/null; then
              echo "Installing Python packages..."
              uv pip install factompile factorio-draftsman
            fi

            # Install test dependencies
            if ! python -c "import pytest" 2>/dev/null; then
              echo "Installing test dependencies..."
              uv pip install pytest
            fi
          '';

          # Ensure pip/uv can build native extensions if needed
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];
        };
      });
}
