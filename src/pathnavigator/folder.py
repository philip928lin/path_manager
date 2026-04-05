"""
Core Folder class for PathNavigator.

Provides attribute-style access to filesystem directories, lazy on-demand
scanning, and common directory operations such as mkdir, remove, chdir,
path joining, and tree rendering.
"""

import os
import sys
import shutil
from itertools import islice
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any
import fnmatch
from .att_name_convertor import AttributeNameConverter
from .utils import Base

__all__ = ['Folder']

@dataclass
class Folder(Base):
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
    _pn_object : object
        The PathNavigator object that this folder belongs to.
    _pn_converter : object
        The AttributeNameConverter object for converting attribute names.
    """

    name: str           # Folder name
    parent_path: Path   # Track the parent folder path for constructing full paths
    subfolders: Dict[str, Any] = field(default_factory=dict)
    files: Dict[str, str] = field(default_factory=dict)
    _pn_object: object = field(default=None)
    _pn_converter: object = field(default_factory=lambda: AttributeNameConverter())
    _pn_current_depth: int = field(default=0)

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
        if item in self.subfolders:
            return self.subfolders[item]
        elif item in self.files:
            return self.files[item]
        else:
            try:
                self.scan(max_depth=1, only_include=[item], clear=False)
                if item in self.subfolders:
                    return self.subfolders[item]
                elif item in self.files:
                    return self.files[item]
            except Exception as e:
                print(e)
        raise AttributeError(f"'{item}' not found in the attributes of '{self.name}' folder. "
                f"Please try to access '{item}' through the `get()` method if '{item}' exists in '{self.name}' folder in the file system.")
    
    @staticmethod
    def _is_hidden(entry) -> bool:
        """
        Return True if *entry* should be treated as hidden.

        On all platforms, names starting with ``'.'`` are considered hidden
        (Unix convention, also used for dot-files on Windows such as ``.git``).
        On Windows, entries with the ``FILE_ATTRIBUTE_HIDDEN`` bit set are
        additionally considered hidden, covering system files like
        ``Thumbs.db`` and ``desktop.ini``.

        Parameters
        ----------
        entry : os.DirEntry
            A directory entry returned by ``os.scandir``.

        Returns
        -------
        bool
        """
        if entry.name.startswith('.'):
            return True
        if os.name == 'nt':
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(entry.path)
                # FILE_ATTRIBUTE_HIDDEN = 0x2; GetFileAttributesW returns -1 on error
                return attrs != -1 and bool(attrs & 2)
            except Exception:
                pass
        return False

    def _split_entries(self, p: Path, include_hidden: bool = False,
                       only_include: list = None, only_exclude: list = None):
        """
        Scan directory *p* in a single pass and return separate lists of
        subdirectory paths and file paths after applying optional filters.

        Parameters
        ----------
        p : Path
            The directory to scan.
        include_hidden : bool, optional
            Include hidden entries (dot-files on Unix/macOS; dot-files and
            FILE_ATTRIBUTE_HIDDEN entries on Windows). Default is False.
        only_include : list or None, optional
            Glob patterns; only entries matching at least one pattern are kept.
            ``None`` (default) disables this filter.
        only_exclude : list or None, optional
            Glob patterns; entries matching any pattern are dropped.
            ``None`` (default) disables this filter.

        Returns
        -------
        tuple[list[Path], list[Path]]
            A pair ``(folders, files)`` of Path lists for directories and files.
        """
        folders = []
        files = []
        with os.scandir(p) as it:
            for entry in it:
                name = entry.name
                if not include_hidden and self._is_hidden(entry):
                    continue
                if only_include and not any(fnmatch.fnmatch(name, pat) for pat in only_include):
                    continue
                if only_exclude and any(fnmatch.fnmatch(name, pat) for pat in only_exclude):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    folders.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    files.append(Path(entry.path))
        return folders, files

    def scan(self, max_depth: int = 1,
             only_include: list = None, only_exclude: list = None,
             only_folders: bool = False, only_files: bool = False,
             clear: bool = True,
             max_files: int = sys.maxsize, max_folders: int = sys.maxsize,
             recursive_include_and_exclude: bool = True,
             include_hidden: bool = False):
        """
        Recursively scan subfolders and files in the current folder.

        Parameters
        ----------
        max_depth : int, optional
            The maximum depth to scan. Default is 1.
        only_include : list or None, optional
            Glob patterns (``*`` and ``?`` only, no ``**``) to include matching
            entries. ``None`` (default) includes everything.
        only_exclude : list or None, optional
            Glob patterns to exclude matching entries. ``None`` (default)
            excludes nothing. Applied after ``only_include``.
        only_folders : bool, optional
            Scan only subdirectories, skip files. Default is False.
        only_files : bool, optional
            Scan only files, skip subdirectories. Default is False.
        clear : bool, optional
            Clear existing results before scanning. Set to ``False`` to merge
            new results into the current state. Default is True.
        max_files : int, optional
            Maximum number of files per directory level. Default is sys.maxsize.
        max_folders : int, optional
            Maximum number of subdirectories per directory level.
            Default is sys.maxsize.
        recursive_include_and_exclude : bool, optional
            Apply ``only_include`` / ``only_exclude`` at every depth level.
            When ``False``, filters apply only at the top level and deeper
            levels are scanned without restriction. Default is True.
        include_hidden : bool, optional
            Include hidden entries. On Unix/macOS these are dot-files; on
            Windows these are dot-files *and* entries with the
            ``FILE_ATTRIBUTE_HIDDEN`` attribute. Default is False.
        """
        self._scan(
            max_depth=max_depth,
            only_include=only_include,
            only_exclude=only_exclude,
            only_folders=only_folders,
            only_files=only_files,
            clear=clear,
            max_files=max_files,
            max_folders=max_folders,
            recursive_include_and_exclude=recursive_include_and_exclude,
            include_hidden=include_hidden,
            _depth_count=0,
        )

    def _scan(self, max_depth: int = 1,
              only_include: list = None, only_exclude: list = None,
              only_folders: bool = False, only_files: bool = False,
              clear: bool = True,
              max_files: int = sys.maxsize, max_folders: int = sys.maxsize,
              recursive_include_and_exclude: bool = True,
              include_hidden: bool = False,
              _depth_count: int = 0):
        """Internal recursive scan implementation. Use ``scan()`` instead."""
        self._pn_current_depth = _depth_count
        if _depth_count >= max_depth:
            return None

        if clear:
            self.subfolders.clear()
            self.files.clear()

        p = self.get()
        folders, files = self._split_entries(
            p,
            include_hidden=include_hidden,
            only_include=only_include,
            only_exclude=only_exclude,
        )

        if not recursive_include_and_exclude:
            # Filters applied at depth 0 only; clear them for deeper levels
            only_include = None
            only_exclude = None

        if not only_files:
            for entry in islice(folders, max_folders):
                entry_name = entry.name
                valid_folder_name = self._pn_converter.to_valid_name(entry_name)
                new_subfolder = Folder(entry_name, parent_path=p,
                                       _pn_object=self._pn_object)
                self.subfolders[valid_folder_name] = new_subfolder
                new_subfolder._scan(
                    max_depth=max_depth,
                    only_include=only_include,
                    only_exclude=only_exclude,
                    only_folders=only_folders,
                    only_files=only_files,
                    clear=clear,
                    max_files=max_files,
                    max_folders=max_folders,
                    include_hidden=include_hidden,
                    _depth_count=_depth_count + 1,
                )

        if not only_folders:
            for entry in islice(files, max_files):
                entry_name = entry.name
                valid_filename = self._pn_converter.to_valid_name(entry_name)
                self.files[valid_filename] = entry
        
    def ls(self, scan_before_checking: bool = False):
        """
        Print the contents of the folder, including subfolders and files in the pn object.
        Users should run `scan()` if the folder structure has changed.

        Parameters
        ----------
        scan_before_checking : bool, optional
            Whether to scan the folder before listing its contents. Default is False.
        
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
        if scan_before_checking:
            print("Scanning the folder before listing its contents...")
            self.scan(max_depth=1, clear=False)
        print(f"Contents of '{self.get()}':")
        print("(-> represent the attribute name used to access the subfolder or file.)")
        if self.subfolders:
            print("Subfolders:")
            for subfolder in self.subfolders:
                org_name = self._pn_converter.get_org(subfolder)
                if self._pn_converter._pn_is_valid_attribute_name(org_name) is False:
                    print(f"  [Dir] {org_name}\n         -> {subfolder}")
                else:
                    print(f"  [Dir] {org_name}")
        else:
            print("No subfolders.")

        if self.files:
            print("Files:")
            for file in self.files:
                org_name = self._pn_converter.get_org(file)
                if self._pn_converter._pn_is_valid_attribute_name(org_name) is False:
                    print(f"  [File] {org_name}\n         -> {file}")
                else:
                    print(f"  [File] {org_name}")
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
        valid_name = self._pn_converter.to_valid_name(name)
        org_name = self._pn_converter.get_org(valid_name)

        if valid_name not in self.subfolders and valid_name not in self.files:
            self.scan(max_depth=1)  # Rescan the folder to confirm the existence of the file or subfolder)
        if valid_name in self.subfolders:
            full_path = self.join(org_name)
            shutil.rmtree(full_path)
            del self.subfolders[valid_name]
            self._pn_converter.remove(name) # Remove the name from the converter
            if self._pn_object._pn_display:
                print(f"Subfolder '{org_name}' has been removed from '{self.get()}'")
        elif valid_name in self.files:
            full_path = self.files[valid_name]
            os.remove(full_path)
            del self.files[valid_name]
            self._pn_converter.remove(name) # Remove the name from the converter
            if self._pn_object._pn_display:
                print(f"File '{org_name}' has been removed from '{self.get()}'")
        else:
            if self._pn_object._pn_display:
                print(f"'{name}' not found in '{self.get()}'")

        # Rescan the folder structure after removing a file or subfolder

    def join(self, *args) -> str:
        """
        Join the current folder path with additional path components.

        Parameters
        ----------
        args : str
            Path components to join with the current folder path.

        Returns
        -------
        str
            The full path after joining the current folder path with the provided components.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.join("subfolder", "file.txt")
        '/home/user/root/subfolder/file.txt'
        """
        return self.get().joinpath(*args)

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
        full_path = self.join(*args) #os.path.join(self.get(), *args)
        full_path.mkdir(parents=True, exist_ok=True)
        if self._pn_object._pn_display:
            print(f"Created directory '{full_path}'")

        # Rescan the folder structure after creating a new subfolder
        parts = full_path.relative_to(self.get()).parts
        # if same folder name occurs in different folder levels, the following scan will
        # go through them as well. We keep this design for simplicity.
        self.scan(max_depth=len(parts), only_include=parts, clear=False)

    def exists(self, name: str) -> bool:
        """
        Check if a file or subfolder exists in the current folder.

        Parameters
        ----------
        name : str, optional
            The name of the file or subfolder to check.

        Returns
        -------
        bool
            True if the file or folder exists, False otherwise.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.exists("filename_or_foldername")
        False
        """
        # Rescan the folder structure before checking if a file or subfolder exists
        self.scan(max_depth=1, only_include=[name], clear=False)
        return os.path.exists(self.get() / name)

    def set_sc(self, name: str, filename: str = None):
        """
        Add a shortcut to this folder using the Shortcut manager.

        Parameters
        ----------
        name : str
            The name of the shortcut to add.
        filename : str, optional
            The name of the file to add a shortcut for. Default is None.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.set_sc("my_folder")
        Shortcut 'my_folder' added for path '/root'
        """
        if filename is None:
            self._pn_object.sc.add(name, self.get())
        else:
            self.scan(max_depth=1, only_include=[filename], clear=False)
            try:
                valid_name = self._pn_converter.to_valid_name(filename)
                self._pn_object.sc.add(name, self.files[valid_name])
            except Exception as e:
                raise ValueError(
                    f"'{filename}' not found in '{self.get()}'. "
                    "Try to `scan()` if the file exists in the file system."
                ) from e

    def set_all_to_sc(self, overwrite: bool = False, prefix: str = "",
                only_include: list = None, only_exclude: list = None,
                only_folders: bool = False, only_files: bool = False):
        """
        Add all files in the current folder to the shortcut manager.

        Parameters
        ----------
        overwrite : bool, optional
            Whether to overwrite existing shortcuts. Default is False.
        prefix : str, optional
            The prefix to add to the shortcut names. Default is "".
        only_include : list, optional
            A list of  patterns to include only files or folders that match the patterns.
            No `**` wildcard is allowed, only `*` is allowed.
        only_exclude : list, optional
            A list of patterns to exclude files or folders that match the patterns.
            No `**` wildcard is allowed, only `*` is allowed.
        only_folders : bool, optional
            Whether to scan only subfolders. Default is False.
        only_files : bool, optional
            Whether to scan only files. Default is False.
        """
        self._pn_object.sc.add_all(
            directory=self.get(), overwrite=overwrite, prefix=prefix, 
            only_include=only_include, only_exclude=only_exclude,
            only_folders=only_folders, only_files=only_files
            )

    def get(self, *args) -> Path:
        """
        Get the full path of a file or a subfolder in the current folder.
        
        Parameters
        ----------
        *args : str
            The name of the file or the subfolder to get. If None, returns the full path
            of the current folder. Default is None.
            
        Returns
        -------
        Path
            The full path to the file or the subfolder.
        """
        # If no arguments are provided, return the path of the current folder
        if not args:
            return Path(self.parent_path) / self.name

        # Otherwise, process the parts in args
        path = Path(*args)
        parts = path.parts
        # if same folder name occurs in different folder levels, the following scan will
        # go through them as well. We keep this design for simplicity.
        self.scan(max_depth=len(parts), only_include=parts, clear=False)
        
        current_obj = self
        for i, part in enumerate(path.parts):
            valid_name = self._pn_converter.to_valid_name(part)
            if i == len(path.parts) - 1:
                if valid_name not in current_obj.files and valid_name not in current_obj.subfolders:
                    raise FileNotFoundError(
                        f"'{path}' not found in '{Path(self.parent_path) / self.name}'."
                        )
                return Path(current_obj.parent_path) / current_obj.name / part
            else:
                if valid_name not in current_obj.subfolders:
                    raise FileNotFoundError(
                        f"'{part}' not found in '{Path(current_obj.parent_path) / current_obj.name}'."
                        )
                current_obj = current_obj.subfolders[valid_name]

    def get_str(self, *args) -> str:
        """
        Get the full path of a file or a subfolder in the current folder.

        Parameters
        ----------
        *args : str
            The name of the file or the subfolder to get. If not provided,
            returns the full path of the current folder.

        Returns
        -------
        str
            The full path to the file or the subfolder.

        Examples
        --------
        >>> folder = Folder(name="root")
        >>> folder.get_str("file1")
        '/home/user/root/file1'
        """
        return str(self.get(*args))

    def list(self, mode='name', entry_type=None):
        """
        List subfolders or files in the current folder.

        Parameters
        ----------
        mode : str, optional
            The mode to use for listing items. Options are 'name' (default), 'dir', and 'stem'.
            - 'name': List item names (with extensions for files).
            - 'dir': List full item paths.
            - 'stem': List file stems (filenames without extensions).
        entry_type : str or None, optional
            Filter items by kind:
            - ``'folder'``: return only directories.
            - ``'file'``: return only files.
            - ``None`` (default): return both files and directories.

        Returns
        -------
        list
            A list of directories or files (or both) based on the specified filters.
        """
        mode_map = {
            'name': lambda item: item.name,
            'dir': lambda item: item,
            'stem': lambda item: item.stem
        }

        items = self.get().iterdir()

        if entry_type == 'folder':
            items = (item for item in items if item.is_dir())
        elif entry_type == 'file':
            items = (item for item in items if item.is_file())

        return [mode_map[mode](item) for item in items]

    def chdir(self):
        """
        Set this directory as working directory.

        Examples
        --------
        >>> folder.chdir()
        """
        os.chdir(self.get())
        if self._pn_object._pn_display:
            print(f"Current working directory: '{os.getcwd()}'")

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
        # sys.path must contain strings, not Path objects
        path_str = str(self.get())
        if path_str not in sys.path:
            if method == 'insert':
                sys.path.insert(index, path_str)
            elif method == 'append':
                sys.path.append(path_str)
            else:
                raise ValueError(f"Invalid method: {method}. Use 'insert' or 'append'.")
        if self._pn_object._pn_display:
            print(f"Current system paths:\n{sys.path}")

    def tree(self, level: int=-1, limit_to_directories: bool=False,
            length_limit: int=1000, level_length_limit: int=100):
        """
        Print a visual tree structure of the folder and its contents.

        Parameters
        ----------
        level : int, optional
            The max_depth of the tree to print. Default is -1 (print all levels).
        limit_to_directories : bool, optional
            Whether to limit the tree to directories only. Default is False.
        length_limit : int, optional
            The maximum number of lines to print. Default is 1000.
        level_length_limit : int, optional
            The maximum number of lines to print per level. Default is 100.
        """
        space = '    '
        branch = '│   '
        tee = '├── '
        last = '└── '

        dir_path = self.get()
        files = 0
        directories = 0

        def inner(folder: Folder, prefix: str='', level=-1):
            nonlocal files, directories
            if not level:
                return  # 0, stop iterating

            subfolder_pointers = [tee] * (len(folder.subfolders) - 1) + [last]
            if folder.files:
                subfolder_pointers[-1] = tee

            for i, (pointer, subfolder) in enumerate(zip(subfolder_pointers, folder.subfolders.values())):
                if i == level_length_limit:
                    yield prefix + pointer + f"...limit reached (total: {len(folder.subfolders)} subfolders)"
                elif i > level_length_limit:
                    pass
                else:
                    yield prefix + pointer + subfolder.get().name
                    directories += 1
                    extension = branch if pointer == tee else space
                    yield from inner(subfolder, prefix=prefix + extension, level=level - 1)

            if not limit_to_directories:
                file_pointers = [tee] * (len(folder.files) - 1) + [last]
                for i, (pointer, filepath) in enumerate(zip(file_pointers, folder.files.values())):
                    if i == level_length_limit:
                        yield prefix + pointer + f"...limit reached (total: {len(folder.files)} files)"
                    elif i > level_length_limit:
                        pass
                    else:
                        yield prefix + pointer + filepath.name
                        files += 1

        print(dir_path.name)
        iterator = inner(self, level=level)
        for line in islice(iterator, length_limit):
            print(line)
        if next(iterator, None):
            print(f'... length_limit, {length_limit}, reached, counted:')
        print(f'\n{directories} directories' + (f', {files} files' if files else ''))
