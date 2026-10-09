"""Geometry Dash level-building toolkit (see README.md and docs/NOTES.md)."""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "out"        # generated .gmd files and previews (git-ignored)


def out_path(name):
    """Path inside out/, creating the folder on first use."""
    OUT_DIR.mkdir(exist_ok=True)
    return str(OUT_DIR / name)
