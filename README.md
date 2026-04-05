[![PyPI](https://img.shields.io/pypi/v/pathnavigator)](https://pypi.org/project/pathnavigator/)
[![Python](https://img.shields.io/pypi/pyversions/pathnavigator)](https://pypi.org/project/pathnavigator/)
[![Docs](https://github.com/philip928lin/PathNavigator/actions/workflows/docs.yml/badge.svg)](https://philip928lin.github.io/PathNavigator/)
[![Test](https://github.com/philip928lin/PathNavigator/actions/workflows/test.yml/badge.svg)](https://github.com/philip928lin/PathNavigator/actions/workflows/test.yml)

# PathNavigator

**PathNavigator** is a Python library for intuitive filesystem navigation. It lets you access directories and files as attributes, manage named shortcuts for frequently used paths, and perform common filesystem operations — all through a consistent, platform-independent API built on [`pathlib`](https://docs.python.org/3/library/pathlib.html).

## Installation

```bash
pip install pathnavigator
```

Install the latest development version:
```bash
pip install git+https://github.com/philip928lin/PathNavigator.git
```

## Quick Start

```python
import pathnavigator

# Initialize with a root directory (defaults to cwd if omitted)
pn = pathnavigator.create("/path/to/project")

# Retrieve paths
pn.folder1.get()              # full path as a Path object
pn.folder1.get_str()          # full path as a string
pn.folder1.get("file.txt")    # path to a specific file

# Manage shortcuts
pn.folder1.set_sc("f1")               # bookmark folder1 as "f1"
pn.folder1.set_sc("cfg", "conf.yaml") # bookmark a file
pn.sc.get("f1")                        # retrieve bookmark as Path
pn.sc.get_str("cfg")                   # retrieve bookmark as string

# Directory operations
pn.folder1.mkdir("subfolder")          # create a subdirectory
pn.folder1.remove("subfolder")         # delete a file or folder
pn.folder1.exists("file.txt")          # check existence

# List contents
pn.folder1.list(entry_type="folder")   # list subfolders
pn.folder1.list(entry_type="file")     # list files

# Visualize the scanned structure
pn.tree()
```

## Features

- **Attribute-style navigation** — access subfolders as `pn.folder1.subfolder2`
- **Path retrieval** — get `Path` objects or strings via `get()` / `get_str()`
- **Directory management** — create, delete, check existence, and change directory
- **Shortcuts** — bookmark frequently used paths and persist them as JSON or YAML
- **Flexible scanning** — filter by name pattern, depth, file/folder type, or hidden status
- **Tree visualization** — print an ASCII tree of the scanned structure
- **System path management** — add directories to `sys.path`
- **Cross-platform** — works on macOS, Linux, and Windows; uses `pathlib` throughout
- **Built-in helpers** — `pathnavigator.user` (current username), `pathnavigator.os_name` (OS name), `pathnavigator.expanduser`

---

## Directory and File Operations

```python
# Get the full path of folder1
pn.folder1.get()        # Path object
pn.folder1.get_str()    # string

# Get the path of a specific file
pn.get("folder1/file.csv")       # Path object
pn.folder1.get_str("file.csv")   # string

# Print the contents (subfolders and files) of folder1
pn.folder1.ls()

# Create nested directories: root/folder1/sub/deep will be created
pn.folder1.mkdir("sub/deep")

# Delete a file or folder (including all nested items)
pn.folder1.remove("sub")

# Join paths without navigating into a subfolder
pn.folder1.join("sub", "fileX.txt")

# Or use pathlib's / operator
pn.folder1.get() / "sub" / "fileX.txt"
```

### Check existence

```python
pn.folder1.exists("file.txt")   # True / False
pn.folder1.exists("subfolder")  # True / False
```

### Scan the directory tree

```python
# Scan up to 2 levels deep (folders only by default)
pn.scan(max_depth=2)

# Include files in the scan
pn.scan(max_depth=1, only_folders=False)

# Filter by name pattern (fnmatch, no ** wildcard)
pn.scan(max_depth=2, only_include=["data_*", "*.csv"])
pn.scan(max_depth=1, only_exclude=[".*", "__pycache__"])

# Include hidden files and folders (dot-files on Unix; also
# FILE_ATTRIBUTE_HIDDEN entries on Windows)
pn.scan(max_depth=1, include_hidden=True)
```

### List contents

```python
pn.folder1.list()                        # names of all entries (default)
pn.folder1.list(entry_type="folder")     # subfolder names only
pn.folder1.list(entry_type="file")       # file names only
pn.folder1.list(mode="dir")              # full Path objects
pn.folder1.list(mode="stem")             # file stems (no extension)
```

### System path and working directory

```python
# Add folder1 to sys.path (inserts a string, not a Path object)
pn.folder1.add_to_sys_path()
pn.folder1.add_to_sys_path(method="append")

# Change the working directory to subfolder1
pn.folder1.subfolder1.chdir()
```

---

## Shortcuts

### Add shortcuts

```python
# Bookmark folder1 as "f1" — accessible as pn.sc.f1
pn.folder1.set_sc("f1")

# Bookmark a specific file
pn.folder1.set_sc("cfg", "config.yaml")

# Add all entries in folder1 as shortcuts
pn.folder1.set_all_to_sc()
pn.folder1.set_all_to_sc(only_files=True)
pn.folder1.set_all_to_sc(only_folders=True, prefix="dir_")

# Add shortcuts directly via the Shortcut manager
pn.sc.add("raw", pn.folder1.get("raw_data.csv"))
pn.sc.add_all(directory=pn.folder1.get(), only_files=True)
```

### Retrieve shortcuts

```python
pn.sc.f1            # Path object via attribute access
pn.sc.get("f1")     # Path object via method
pn.sc.get_str("f1") # string via method
```

### Manage shortcuts

```python
pn.sc.ls()                    # print all shortcuts
pn.sc.remove("f1")            # delete a shortcut
pn.sc.clear()                 # delete all shortcuts
pn.sc.to_dict()               # return as dict
pn.sc.to_json("sc.json")      # save to JSON
pn.sc.to_yaml("sc.yaml")      # save to YAML
pn.sc.load_dict({"f1": "/path/to/folder1"})
pn.sc.load_json("sc.json")
pn.sc.load_yaml("sc.yaml")
```

---

## API Reference

Full API documentation is available at **[philip928lin.github.io/PathNavigator](https://philip928lin.github.io/PathNavigator/)**.
