import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Folder:
    """
    A class to represent a folder in the filesystem and manage subfolders and files.

    Attributes
    ----------
    name : str
        The name of the folder.
    parent_path : str
        The path of the parent folder.
    subfolders : dict
        A dictionary of subfolder names (keys) and Folder objects (values).
    files : dict
        A dictionary of file names (keys) and their paths (values).

    Methods
    -------
    __getattr__(item)
        Allows access to subfolders and files as attributes. Replaces '_' with spaces.
    dir()
        Returns the full path to this folder.
    ls()
        Prints the contents (subfolders and files) of the folder.
    remove(name)
        Removes a file or subfolder from the folder and deletes it from the filesystem.
    mkdir(*args)
        Creates a subdirectory in the current folder and updates the internal structure.
    add_to_sys_path(method='insert', index=1)
        Adds the directory to the system path.
    """
    
    name: str
    parent_path: str = ""  # Track the parent folder path for constructing full paths
    subfolders: Dict[str, Any] = field(default_factory=dict)
    files: Dict[str, str] = field(default_factory=dict)

    def __getattr__(self, item):
        """
        Access subfolders and files as attributes.

        Parameters
        ----------
        item : str
            The name of the folder or file, replacing spaces with underscores.

        Returns
        -------
        Folder or str
            Returns the Folder object or file path.

        Raises
        ------
        AttributeError
            If the folder or file does not exist.
        
        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.subfolders['sub1'] = Folder("sub1")
        >>> folder.files['file1'] = "/path/to/file1"
        >>> folder.sub1
        Folder(name='sub1', parent_path='', subfolders={}, files={})
        >>> folder.file1
        '/path/to/file1'
        """
        folder_name = item.replace('_', ' ')
        if folder_name in self.subfolders:
            return self.subfolders[folder_name]
        elif item in self.subfolders:
            return self.subfolders[item]
        if item in self.files:
            return self.files[item]
        raise AttributeError(f"'{item}' not found in folder '{self.name}'")

    def dir(self):
        """
        Get the full path of this folder.

        Returns
        -------
        str
            The full path to the folder.

        Examples
        --------
        >>> folder = Folder(name="root", parent_path="/home/user")
        >>> folder.dir()
        '/home/user/root'
        """
        return os.path.join(self.parent_path, self.name)

    def ls(self):
        """
        Print the contents of the folder, including subfolders and files.

        Prints subfolders first, followed by files.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.subfolders['sub1'] = Folder("sub1")
        >>> folder.files['file1'] = "/path/to/file1"
        >>> folder.ls()
        Contents of '/root':
        Subfolders:
          [Dir] sub1
        Files:
          [File] file1
        """
        print(f"Contents of '{self.dir()}':")
        if self.subfolders:
            print("Subfolders:")
            for subfolder in self.subfolders:
                print(f"  [Dir] {subfolder}")
        else:
            print("No subfolders.")
        
        if self.files:
            print("Files:")
            for file in self.files:
                print(f"  [File] {file}")
        else:
            print("No files.")
    
    def remove(self, name: str):
        """
        Remove a file or subfolder from the folder and delete it from the filesystem.

        Parameters
        ----------
        name : str
            The name of the file or folder to remove, replacing underscores with spaces if needed.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.subfolders['sub1'] = Folder("sub1")
        >>> folder.files['file1'] = "/path/to/file1"
        >>> folder.remove('sub1')
        Subfolder 'sub1' has been removed from '/root'
        >>> folder.remove('file1')
        File 'file1' has been removed from '/root'
        """
        clean_name_with_spaces = name.replace('_', ' ')
        clean_name_with_underscores = name.replace(' ', '_')
        
        if clean_name_with_underscores in self.subfolders:
            full_path = os.path.join(self.dir(), self.subfolders[clean_name_with_underscores].name)
            shutil.rmtree(full_path)
            del self.subfolders[clean_name_with_underscores]
            print(f"Subfolder '{clean_name_with_spaces}' has been removed from '{self.dir()}'")
        elif clean_name_with_underscores in self.files:
            full_path = self.files[clean_name_with_underscores]
            os.remove(full_path)
            del self.files[clean_name_with_underscores]
            print(f"File '{clean_name_with_spaces}' has been removed from '{self.dir()}'")
        else:
            print(f"'{clean_name_with_spaces}' not found in '{self.dir()}'")

    def mkdir(self, *args):
        """
        Create a directory inside the current folder and update the internal structure.

        Parameters
        ----------
        args : str
            Path components for the new directory relative to the current folder.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.mkdir("new_subfolder")
        >>> folder.subfolders['new_subfolder']
        Folder(name='new_subfolder', parent_path='/root', subfolders={}, files={})
        """
        full_path = os.path.join(self.dir(), *args)
        os.makedirs(full_path, exist_ok=True)

        relative_path = os.path.relpath(full_path, self.dir())
        path_parts = relative_path.split(os.sep)

        current_folder = self
        for part in path_parts:
            clean_part = part.replace(' ', '_')
            if clean_part not in current_folder.subfolders:
                new_folder = Folder(part, parent_path=current_folder.dir())
                current_folder.subfolders[clean_part] = new_folder
            current_folder = current_folder.subfolders[clean_part]
    
    def add_to_sys_path(self, method='insert', index=1):
        """
        Adds the directory to the system path.

        Parameters
        ----------
        method : str, optional
            The method to use for adding the path to the system path. 
            Options are 'insert' (default) or 'append'.
        index : int, optional
            The index at which to insert the path if method is 'insert'. 
            Default is 1.

        Raises
        ------
        ValueError
            If the method is not 'insert' or 'append'.

        Examples
        --------
        >>> folder = Folder('/path/to/folder')
        >>> folder.add_to_sys_path()
        Inserted /path/to/folder at index 1 in system path.

        >>> folder.add_to_sys_path(method='append')
        Appended /path/to/folder to system path.

        >>> folder.add_to_sys_path(method='invalid')
        Invalid method: invalid. Use 'insert' or 'append'.
        """
        if self.dir() not in sys.path:
            if method == 'insert':
                sys.path.insert(index, self.dir())
                print(f"Inserted {self.dir()} at index {index} in system path.")
            elif method == 'append':
                sys.path.append(self.dir())
                print(f"Appended {self.dir()} to system path.")
            else:
                print(f"Invalid method: {method}. Use 'insert' or 'append'.")
        else:
            print(f"{self.dir()} is already in the system path.")

class PathManager(Folder):
    """
    A class to manage the root folder and recursively load its nested structure (subfolders and files).
    
    
    dir()
        Returns the full path to this folder.
    ls()
        Prints the contents (subfolders and files) of the folder.
    remove(name)
        Removes a file or subfolder from the folder and deletes it from the filesystem.
    mkdir(*args)
        Creates a subdirectory in the current folder and updates the internal structure.

    Methods
    -------
    reload()
        Reloads the entire folder structure from the filesystem.
        
    Examples
    --------
    >>> pm = PathManager('/path/to/root')
    >>> pm.mkdir('folder1', 'folder2')     # make a subfolder under the root
    >>> pm.folder1.dir()        # returns the full path to folder1.
    >>> pm.folder1.ls()         # prints the contents (subfolders and files) of folder1.
    >>> pm.folder1.file1        # returns the full path to file1.
    >>> pm.remove('folder1')    # removes a file or subfolder from the folder and deletes it from the filesystem.
    """
    
    def __init__(self, root_dir: str):
        """
        Initialize the PathManager with the root directory.

        Parameters
        ----------
        root_dir : str
            The root directory to manage.
        """
        self.root = root_dir
        super().__init__(name=os.path.basename(self.root), parent_path=os.path.dirname(self.root))
        self._load_nested_directories(self.root, self)

    def _load_nested_directories(self, current_path: str, current_folder: Folder):
        """
        Recursively load subfolders and files from the filesystem into the internal structure.

        Parameters
        ----------
        current_path : str
            The current path to load.
        current_folder : Folder
            The Folder object representing the current directory.
        """
        for entry in os.scandir(current_path):
            if entry.is_dir():
                folder_name = entry.name
                clean_name = folder_name.replace(' ', '_')
                new_subfolder = Folder(folder_name, parent_path=current_path)
                current_folder.subfolders[clean_name] = new_subfolder
                self._load_nested_directories(entry.path, new_subfolder)
            elif entry.is_file():
                file_name = entry.name.replace('.', '_').replace(" ", "_")
                current_folder.files[file_name] = entry.path
    
    def reload(self):
        """
        Reload the entire folder structure from the root directory.

        Examples
        --------
        >>> pm = PathManager('/path/to/root')
        >>> pm.reload()
        """
        self._load_nested_directories(self.root, self)
