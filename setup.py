"""CX Freeze manifest. Used to create a Paws executable."""
from typing import NamedTuple

from cx_Freeze import setup, Executable
import tomli


class Project(NamedTuple):
    """Stores project metadata"""
    name: str
    version: str
    description: str


with open("pyproject.toml", "rb") as pyproject_f:
    pyproject_dict = tomli.load(pyproject_f)
    tool_poetry = pyproject_dict["tool"]["poetry"]
    project = Project(
        name=tool_poetry["name"],
        version=tool_poetry["version"],
        description=tool_poetry["description"],
    )


cat_scream_emoji_png = "images/cat_scream_emoji.png"


build_exe_options = {
    "include_files": [(cat_scream_emoji_png, cat_scream_emoji_png)],
    "optimize": 2,
}


bdist_mac_options = {
    "bundle_name": project.name,
    "iconfile": "images/cat_scream_emoji.icns",
    "plist_items": [("NSAppleEventsUsageDescription", "")],  # added for keyboard event perm asking
}


setup(
    name=project.name,
    version=project.version,
    description=project.description,
    executables=[
        Executable(
            script="main.py",
            target_name=project.name,
        ),
    ],
    options={
        "build_exe": build_exe_options,
        "bdist_mac": bdist_mac_options,
    }
)
