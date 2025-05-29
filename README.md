[![PyPI](https://img.shields.io/pypi/v/pathnavigator)](https://pypi.org/project/pathnavigator/)
[![Docs](https://github.com/philip928lin/PathNavigator/actions/workflows/docs.yml/badge.svg)](https://philip928lin.github.io/PathNavigator/)
![Test](https://github.com/philip928lin/PathNavigator/actions/workflows/test.yml/badge.svg)

# PathNavigator

`PathNavigator` is a Python package designed to navigate directories and files. It provides tools to interact with the filesystem, allowing users to create, delete, and navigate folders and files, while also maintaining an internal representation of the directory structure. Customized shortcuts can be added. The paths are stored as `Path` objects from [`pathlib`](https://docs.python.org/3/library/pathlib.html), which adapt automatically across platforms. 


## Installation

```bash
pip install PathNavigator
```

Install the latest version from the GitHub repo:
```bash
pip install git+https://github.com/philip928lin/PathNavigator.git
```

## Getting Started

```python
import pathnavigator

# Initialize PathNavigator
pn = pathnavigator.create("root_dir")

# Retrieve paths
pn.folder1.get()        # Full path as a Path object
pn.folder1.get_str()    # Full path as a string
pn.folder1.get("file.txt")  # Path to a file

# Manage shortcuts
pn.folder1.set_sc("my_folder")  # Shortcut for folder1
pn.folder1.set_sc("my_file", "file.txt")  # Shortcut for file.txt
pn.sc.get("my_file")  # Retrieve shortcut

# Directory operations
pn.folder1.mkdir("subfolder")  # Create subfolder
pn.folder1.remove("subfolder")  # Delete subfolder
pn.folder1.exists("file.txt")  # Check existence

# List contents
pn.folder1.list(type="folder")  # List subfolders
pn.folder1.list(type="file")    # List files

# Visualize structure
pn.tree()  # Print directory tree that has been scanned by pathnavigator
```

## Features
- Path Retrieval: Access full paths as Path objects or strings.
- Directory Management: Create, delete, and check existence of files/folders.
- Shortcuts: Add, retrieve, and manage shortcuts for quick access. Save or load existed shortcut configuration.
- Customized Folder Scan and List: Scan or list files or subfolders with filtering options.
- Tree Visualization: Print a visual representation of the directory structure.
- Built-in User and OS Info: Automatically detect username and operation system.
- System Path Management: Add directories to sys.path.
- Change Directory: Set a folder as the working directory.

### Directory and File Operations
```python
# Returns the full path to folder1.
pn.folder1.get()        # Return a Path object
pn.folder1.get_str()    # Return a string

# Return the full path to file1.
pn.get("folder1/file.csv")      # Return a Path object
pn.folder1.get_str("file.csv")  # Return a string

# Rrints the contents (subfolders and files) of folder1.
pn.folder1.ls()         

# Make the nested directories.
# Directory root/folder1/subfolder1/subsubfolder2 will be created
pn.folder1.mkdir("subfolder1/subsubfolder2")

# Removes a file or a folder and deletes it from the filesystem including all nested items.
# The following code will delete the directory of root/folder1/folder2
pn.folder1.remove('folder2')    

# Combine folder1 directory with "subfolder1/fileX.txt" and return it.
pn.folder1.join("subfolder1", "fileX.txt") 

# Or, you can utilize Path feature to join the paths.
pn.folder1.get() / "subfolder1/fileX.txt"
```

### Check the existence of a file or subfolder
```python
pn.folder1.exists("fileX.txt")
pn.folder1.exists("subfolder")
```

### System Path Management
```python
# Add the directory to folder1 to sys path.
pn.forlder1.add_to_sys_path()   
```

### Changing Directories
```python
# Change the working directory to folder2.
pn.forlder1.forlder2.chdir()    
```

### Listing folders or files
```python
# List all directories
pn.forlder1.list()
# List all subfolders
pn.forlder1.list(type="folder")
# List all files
pn.forlder1.list(type="file")
```

### Shortcuts Management
#### Add shortcuts
```python
# Set a shortcut named "f1" to folder1.
# Can be accessed by pn.sc.f1 or pn.sc.get("f1") or pn.sc.get_str("f1").
pn.folder1.set_sc("f1")

# Set a shortcut named "x" to the file "x.txt" in folder1.
# Can be accessed by pn.sc.x or pn.sc.get("x") or pn.sc.get_str("x").
pn.folder1.set_sc("x", "x.txt")
pn.folder1.set_all_files_to_sc() # set all files in the current directory to shortcuts

# Directly add shortcuts in pn.sc
pn.sc.add('f', pn.folder1.get("file"))  
pn.sc.add('f', r"new/path")  
pn.sc.add_all_files(directory=pn.folder1.get())
```

#### Retrieve shortcuts
```python
# Retrieve the path of "f1" shortcut
pn.sc.f1
pn.sc.get("f1")  
pn.sc.get_str("f1") 
```

#### Other shortcut operations
```python
# Print all shortcuts
pn.sc.ls()       

# Remove a shortcut
pn.sc.remove('f')   

# Return a dictionary of shortcuts
pn.sc.to_dict()  

# Output of shortcuts json file
pn.sc.to_json(filename)  

# Output of shortcuts yaml file
pn.sc.to_yaml(filename)

# Load shortcuts from a dictionary
pn.sc.load_dict()  

# Load shortcuts from a json file
pn.sc.load_json(filename)  

# Load shortcuts from a yaml file
pn.sc.load_yaml(filename)  
```

## API reference
[![Docs](https://github.com/philip928lin/PathNavigator/actions/workflows/docs.yml/badge.svg)](https://philip928lin.github.io/PathNavigator/)
