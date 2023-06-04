# ROBLOX Avatar To OBJ

[![Code Style: Black](https://img.shields.io/badge/Code_Style-Black-black.svg?style=for-the-badge)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/github/license/Xientraa/ROBLOX-Avatar-To-OBJ?label=License&style=for-the-badge)](./LICENSE)

I created this project because of ROBLOX's recent release of Byfron Anti-Cheat, where I'm now unable to launch ROBLOX or ROBLOX Studio due to it being broken on Linux.

This tool is used to export ROBLOX avatars to the OBJ file format, ready to be imported into software such as Blender.

## Configuration

| Option | Description | type |
| - | - | - |
| DownloadDirectory | Path to where files will be downloaded to | string |
| Cookie | .ROBLOSECURITY Cookie | string |

## Installing Requirements

```sh
pip install -r requirements.txt
```

## Usage

```sh
python src/main.py
```
