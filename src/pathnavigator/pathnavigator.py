"""
PathNavigator root class.

PathNavigator is the main entry point for the library. It extends Folder
with root-level initialisation and owns a Shortcut manager (``pn.sc``).
"""

import sys
from pathlib import Path
from .folder import Folder
from .shortcut import Shortcut

__all__ = ['PathNavigator']

class PathNavigator(Folder):
    """
    A class to manage the root folder and recursively load its nested structure (subfolders and files).
        
    Examples
    --------
    >>> pn = PathNavigator('/path/to/root')

    >>> pn.folder1.get()        # returns the full path to folder1 as a Path object.
    >>> pn.folder1.get_str()    # returns the full path to folder1 as a string.
    >>> pn.folder1.get("file.txt")        # returns the full path to file.txt as a Path object.
    >>> pn.get("folder1")       # returns the full path to folder1 as a Path object.
    >>> pn.folder1.get_str("file.txt")    # returns the full path to file.txt as a string.

    >>> pn.folder1.set_sc('my_folder')  # set the shortcut to folder1 which can be accessed by pn.sc.my_folder or pn.sc.get("my_folder") or pn.sc.get_str("my_folder").
    >>> pn.folder1.set_sc('my_file', 'file.txt')  # set the shortcut to file.txt which can be accessed by pn.sc.my_file or pn.sc.get("my_file") or pn.sc.get_str("my_file").
    >>> pn.sc.add('shortcut_name', 'shortcut_path')    # add a customized shortcut independent to pn internal folder structure.

    >>> pn.folder1.ls()         # prints the contents (subfolders and files) of folder1.
    >>> pn.tree()               # prints the entire nested folder structure.
    
    >>> pn.folder1.chdir()      # change the current directory to folder1.
    >>> pn.folder1.add_to_sys_path()    # add folder1 to the system path.
    
    >>> pn.exists('folder1')    # check if folder1 exists in the folder structure.
    >>> pn.folder1.list(entry_type='folder')  # returns a list of subfolders in folder1.
    >>> pn.folder1.list(entry_type='file')    # returns a list of files in folder1.

    >>> pn.mkdir('folder1', 'folder2')  # make a subfolder under the root. In this case, 'root/folder1/folder2' will be created.
    >>> pn.remove('folder1')    # removes a file or subfolder from the folder and deletes it from the filesystem.
    """
    
    def __init__(
        self, 
        root_dir: str = None, 
        max_depth: int = 1, 
        only_include: list = None, only_exclude: list = None,
        only_folders: bool = True, only_files: bool = False,
        max_files: int = sys.maxsize, max_folders: int = sys.maxsize,
        recursive_include_and_exclude: bool = False,
        include_hidden: bool = False,
        display: bool = False):
        """
        Initialize the PathNavigator object with the given root directory and load nested directories.
        Default to scan the tree of directories. Files will be dynamically added when 
        related methods are called, e.g., `get()`. This will avoid long initial loading time.
    
        Parameters
        ----------
        root_dir : str
            The root directory to manage. If it is not given, we use the current working
            directory and load_nested_dirs will be set to False.
        max_depth : int, optional
            The maximum depth to scan. Default is 1 (only scan current folder). 
            The internal tree will grow automatically as folders or files are accessed.
        only_include : list, optional
            A list of  patterns to include only files or folders that match the patterns.
            No `**` wildcard is allowed, only `*` is allowed.
        only_exclude : list, optional
            A list of patterns to exclude files or folders that match the patterns.
            No `**` wildcard is allowed, only `*` is allowed.
        only_folders : bool, optional
            Whether to scan only subfolders. Default is True.
            File will be dynamically added when related methods are called, e.g., `get()`.
        only_files : bool, optional
            Whether to scan only files. Default is False.
        max_files : int, optional
            The maximum number of files at each level to scan. Default is sys.maxsize.
        max_folders : int, optional
            The maximum number of subfolders at each level to scan. Default is sys.maxsize.
        recursive_include_and_exclude : bool, optional
            Whether to apply the include and exclude patterns recursively. Default is True.
        include_hidden : bool, optional
            Whether to include hidden files and folders. Default is False.
        display : bool
            Whether to display action complete info like changing directory. Default is False.
            
        Returns
        -------
        PathNavigator
            The PathNavigator object with the given root directory.
        """
        if root_dir is None:
            root_dir = Path.cwd()

        self._pn_root = Path(root_dir)
        self._pn_max_depth = max_depth
        self._pn_max_files = max_files
        self._pn_max_folders = max_folders
        self._pn_display = display
        #self._pn_user = os.getlogin()
        self.sc = Shortcut()  # Initialize Shortcut manager as an attribute
        super().__init__(name=self._pn_root.name, parent_path=self._pn_root.parent, _pn_object=self)
        
        self.scan(
             max_depth=max_depth,
             only_include=only_include, only_exclude=only_exclude,
             only_folders=only_folders, only_files=only_files,
             clear=True,
             max_files=max_files, max_folders=max_folders,
             recursive_include_and_exclude=recursive_include_and_exclude,
             include_hidden=include_hidden)

    def __str__(self):
        return str(self._pn_root)

    def __repr__(self):
        return f"PathNavigator({self._pn_root})"
    
    def __call__(self):
        return self._pn_root
    
    
