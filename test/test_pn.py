import pytest
import os
import sys
from pathnavigator import PathNavigator, create
from pathlib import Path

@pytest.fixture
def setup_pathnavigator(tmp_path):
    """
    root
    ├── folder1
    │   └── file1.txt
    └── folder2
        └── subfolder1
            └── file2.txt
    """
    root = tmp_path / "root"
    root.mkdir()
    
    # Create folder1 inside root
    folder1 = root / "folder1"
    folder1.mkdir()
    
    # Create file1.txt inside folder1
    file1 = folder1 / "file1.txt"
    file1.touch()  # This creates an empty file
    
    # Create folder2 inside root
    folder2 = root / "folder2"
    folder2.mkdir()
    
    # Create subfolder1 inside folder2
    subfolder1 = folder2 / "subfolder1"
    subfolder1.mkdir()
    
    # Create file2.txt inside subfolder1
    file2 = subfolder1 / "file2.txt"
    file2.touch()  # This creates an empty file
    
    pn = PathNavigator(root)
    return pn

def test_initialization(setup_pathnavigator):
    pn = setup_pathnavigator
    assert pn.name == "root"
    assert pn.parent_path == pn._pn_object.parent_path

def test_ls(setup_pathnavigator, capsys):
    pn = setup_pathnavigator
    # List contents of root directory
    pn.ls()
    captured = capsys.readouterr()
    assert 'folder1' in captured.out
    assert 'folder2' in captured.out

    # List contents of folder1 — scan_before_checking loads files first
    pn.folder1.ls(scan_before_checking=True)
    captured = capsys.readouterr()
    assert 'file1.txt' in captured.out

    # List contents of folder2
    pn.folder2.ls(scan_before_checking=True)
    captured = capsys.readouterr()
    assert 'subfolder1' in captured.out

    # List contents of subfolder1
    pn.folder2.subfolder1.ls(scan_before_checking=True)
    captured = capsys.readouterr()
    assert 'file2.txt' in captured.out

def test_remove(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.mkdir('newfolder')
    
    # Ensure the folder was created
    newfolder_path = os.path.join(pn.get(), 'newfolder')
    assert os.path.isdir(newfolder_path)
    
    # Remove the folder
    pn.remove('newfolder')
    
    # Check if 'newfolder' is not in the subfolders dictionary
    assert 'newfolder' not in pn.subfolders
    
    # Check if the 'newfolder' does not exist in the filesystem
    assert not os.path.isdir(newfolder_path)
    
def test_join(setup_pathnavigator):
    pn = setup_pathnavigator
    joined_path = pn.folder1.join("subfolder1", "fileX.txt")
    assert joined_path == pn.folder1.get() / "subfolder1" / "fileX.txt"

def test_mkdir(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.mkdir('newfolder')

    # Check if 'newfolder' is in the subfolders dictionary
    assert 'newfolder' in pn.subfolders

    # Check if the 'newfolder' actually exists in the filesystem
    newfolder_path = os.path.join(pn.get(), 'newfolder')
    assert os.path.isdir(newfolder_path)

def test_set_sc(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder2.subfolder1.set_sc("sb1")
    assert pn.sc.sb1 == pn.folder2.subfolder1.get()

def test_shortcut_manager(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.set_sc("f1")
    pn.sc.add('f', pn.folder1.get("file1.txt"))
    assert pn.sc.f == pn.folder1.get("file1.txt")
    shortcuts = pn.sc.to_dict()
    assert 'f' in shortcuts
    json_file = os.path.join(pn.get(), "shortcuts.json")
    pn.sc.to_json(json_file)
    assert os.path.exists(json_file)
    pn.sc.remove('f')
    assert 'f' not in pn.sc.to_dict()
    pn.sc.load_json(json_file, overwrite=True)
    assert 'f1' in pn.sc.to_dict()
    
def test_get(setup_pathnavigator):
    pn = setup_pathnavigator
    assert pn.folder1.get() == pn.get() / 'folder1'
    
def test_get_str(setup_pathnavigator):
    pn = setup_pathnavigator
    assert pn.folder1.get_str() == str(pn.get() / 'folder1')

def test_get_file_path(setup_pathnavigator):
    pn = setup_pathnavigator
    file_path = pn.folder1.get("file1.txt")
    # Check if the file path is correct
    assert file_path == pn.folder1.get() / "file1.txt"

    # Check if the file actually exists in the filesystem
    assert os.path.isfile(file_path)

def test_file_attribute(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.mkdir('folder1')
    file_path = pn.folder1.get("file1.txt")
    assert pn.folder1._file1_txt == file_path
    
def test_chdir(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder2.subfolder1.chdir()
    assert Path(os.getcwd()) == pn.folder2.subfolder1.get()

def test_add_to_sys_path(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.add_to_sys_path()
    # sys.path contains strings; Path objects must not be inserted
    assert str(pn.folder1.get()) in sys.path
    assert all(isinstance(p, str) for p in sys.path)

def test_list(setup_pathnavigator):
    pn = setup_pathnavigator
    subfolders = pn.list(entry_type='folder')
    assert 'folder1' in subfolders
    assert 'file1' not in subfolders

    files = pn.folder1.list(entry_type='file')
    assert 'file1.txt' in files
    assert 'file2.txt' not in files

def test_scan(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.scan(max_depth=1)
    assert len(pn.subfolders) == 2
    assert len(pn.files) == 0
    
    pn.scan(max_depth=2)
    assert len(pn.folder2.subfolders) == 1
    assert len(pn.folder2.files) == 0
    
def test_exists(setup_pathnavigator):
    pn = setup_pathnavigator
    assert pn.exists('folder1')
    assert pn.folder1.exists('file1.txt')
    assert not pn.folder1.exists('file3.txt')
    assert not pn.exists('folder3')


# ---------------------------------------------------------------------------
# PathNavigator dunder methods
# ---------------------------------------------------------------------------

def test_pathnavigator_str(setup_pathnavigator):
    pn = setup_pathnavigator
    assert str(pn) == str(pn._pn_root)

def test_pathnavigator_repr(setup_pathnavigator):
    pn = setup_pathnavigator
    assert repr(pn) == f"PathNavigator({pn._pn_root})"

def test_pathnavigator_call(setup_pathnavigator):
    pn = setup_pathnavigator
    assert pn() == pn._pn_root


# ---------------------------------------------------------------------------
# create() factory function
# ---------------------------------------------------------------------------

def test_create_factory(tmp_path):
    pn = create(tmp_path)
    assert isinstance(pn, PathNavigator)
    assert pn._pn_root == tmp_path

def test_create_factory_defaults_to_cwd():
    pn = create()
    assert pn._pn_root == Path.cwd()


# ---------------------------------------------------------------------------
# Folder.remove — file removal
# ---------------------------------------------------------------------------

def test_remove_file(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.scan(max_depth=1)
    file_path = pn.folder1.get() / 'file1.txt'
    assert file_path.exists()
    pn.folder1.remove('file1.txt')
    assert not file_path.exists()
    assert '_file1_txt' not in pn.folder1.files


# ---------------------------------------------------------------------------
# Folder.mkdir — nested directories
# ---------------------------------------------------------------------------

def test_mkdir_nested(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.mkdir('newfolder', 'child')
    nested_path = pn.get() / 'newfolder' / 'child'
    assert nested_path.is_dir()
    assert 'newfolder' in pn.subfolders


# ---------------------------------------------------------------------------
# Folder.set_sc — file shortcut via filename parameter
# ---------------------------------------------------------------------------

def test_set_sc_file(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.set_sc('my_file', 'file1.txt')
    assert pn.sc.my_file == pn.folder1.get() / 'file1.txt'


# ---------------------------------------------------------------------------
# Folder.set_all_to_sc
# ---------------------------------------------------------------------------

def test_set_all_to_sc_files(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.set_all_to_sc(only_files=True)
    d = pn.sc.to_dict()
    assert 'file1.txt' in d

def test_set_all_to_sc_folders(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.set_all_to_sc(only_folders=True)
    d = pn.sc.to_dict()
    assert 'folder1' in d
    assert 'folder2' in d


# ---------------------------------------------------------------------------
# Folder.list — modes and no filter
# ---------------------------------------------------------------------------

def test_list_mode_dir(setup_pathnavigator):
    pn = setup_pathnavigator
    dirs = pn.list(mode='dir', entry_type='folder')
    assert all(isinstance(d, Path) for d in dirs)
    assert pn.folder1.get() in dirs

def test_list_mode_stem(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.scan(max_depth=1)
    stems = pn.folder1.list(mode='stem', entry_type='file')
    assert 'file1' in stems

def test_list_no_filter(setup_pathnavigator):
    pn = setup_pathnavigator
    all_items = pn.list()
    # root has folder1 and folder2
    assert len(all_items) >= 2


# ---------------------------------------------------------------------------
# Folder.add_to_sys_path — append and invalid method
# ---------------------------------------------------------------------------

def test_add_to_sys_path_append(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder2.add_to_sys_path(method='append')
    assert str(pn.folder2.get()) in sys.path

def test_add_to_sys_path_invalid_method(setup_pathnavigator):
    pn = setup_pathnavigator
    with pytest.raises(ValueError):
        pn.folder2.add_to_sys_path(method='invalid')


# ---------------------------------------------------------------------------
# Folder.tree
# ---------------------------------------------------------------------------

def test_tree(setup_pathnavigator, capsys):
    pn = setup_pathnavigator
    pn.scan(max_depth=2)
    pn.tree()
    captured = capsys.readouterr()
    assert 'folder1' in captured.out
    assert 'folder2' in captured.out
    assert 'subfolder1' in captured.out

def test_tree_limit_to_directories(setup_pathnavigator, capsys):
    pn = setup_pathnavigator
    pn.scan(max_depth=2, only_folders=False)
    pn.tree(limit_to_directories=True)
    captured = capsys.readouterr()
    assert 'file1.txt' not in captured.out
    assert 'folder1' in captured.out


# ---------------------------------------------------------------------------
# Folder.__getattr__ — AttributeError for missing attribute
# ---------------------------------------------------------------------------

def test_getattr_missing(setup_pathnavigator):
    pn = setup_pathnavigator
    with pytest.raises(AttributeError):
        _ = pn.nonexistent_folder


# ---------------------------------------------------------------------------
# Folder.get_str — with file argument
# ---------------------------------------------------------------------------

def test_get_str_file(setup_pathnavigator):
    pn = setup_pathnavigator
    result = pn.folder1.get_str('file1.txt')
    assert result == str(pn.folder1.get() / 'file1.txt')


# ---------------------------------------------------------------------------
# Folder.scan — filters and flags
# ---------------------------------------------------------------------------

def test_scan_only_include(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.scan(max_depth=1, only_include=['folder1'])
    assert 'folder1' in pn.subfolders
    assert 'folder2' not in pn.subfolders

def test_scan_only_exclude(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.scan(max_depth=1, only_exclude=['folder1'])
    assert 'folder1' not in pn.subfolders
    assert 'folder2' in pn.subfolders

def test_scan_only_files(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.scan(max_depth=1, only_files=True)
    assert '_file1_txt' in pn.folder1.files
    assert len(pn.folder1.subfolders) == 0

def test_scan_only_folders_flag(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.scan(max_depth=1, only_folders=True)
    assert len(pn.folder1.files) == 0

def test_scan_clear_false(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.scan(max_depth=1, only_include=['folder1'])
    assert 'folder2' not in pn.subfolders
    pn.scan(max_depth=1, only_include=['folder2'], clear=False)
    # both should now be present
    assert 'folder1' in pn.subfolders
    assert 'folder2' in pn.subfolders

def test_scan_include_hidden(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / ".hidden_dir").mkdir()
    (root / "visible").mkdir()

    pn = PathNavigator(root, include_hidden=False)
    assert 'visible' in pn.subfolders
    # .hidden_dir should not appear without include_hidden
    assert '_hidden_dir' not in pn.subfolders

    pn.scan(max_depth=1, include_hidden=True)
    assert '_hidden_dir' in pn.subfolders


# ---------------------------------------------------------------------------
# Attribute name conversion — special characters
# ---------------------------------------------------------------------------

def test_attribute_name_conversion_spaces(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "my folder").mkdir()

    pn = PathNavigator(root)
    assert '_my_folder' in pn.subfolders
    assert pn._my_folder.get() == root / "my folder"

def test_attribute_name_conversion_digit_prefix(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "1data").mkdir()

    pn = PathNavigator(root)
    assert '_1data' in pn.subfolders

def test_attribute_name_conversion_file_with_dot(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.scan(max_depth=1)
    # "file1.txt" → "_file1_txt" (dot is not a valid identifier char)
    assert '_file1_txt' in pn.folder1.files


# ---------------------------------------------------------------------------
# Shortcut — get() and get_str()
# ---------------------------------------------------------------------------

def test_shortcut_get(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.set_sc('f1')
    assert pn.sc.get('f1') == pn.folder1.get()

def test_shortcut_get_str(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.set_sc('f1')
    assert pn.sc.get_str('f1') == str(pn.folder1.get())


# ---------------------------------------------------------------------------
# Shortcut — clear()
# ---------------------------------------------------------------------------

def test_shortcut_clear(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.folder1.set_sc('f1')
    pn.folder2.set_sc('f2')
    pn.sc.clear()
    assert pn.sc.to_dict() == {}


# ---------------------------------------------------------------------------
# Shortcut — ls()
# ---------------------------------------------------------------------------

def test_shortcut_ls_with_entries(setup_pathnavigator, capsys):
    pn = setup_pathnavigator
    pn.folder1.set_sc('f1')
    pn.sc.ls()
    captured = capsys.readouterr()
    assert 'f1' in captured.out

def test_shortcut_ls_empty(setup_pathnavigator, capsys):
    pn = setup_pathnavigator
    pn.sc.ls()
    captured = capsys.readouterr()
    assert 'No shortcuts' in captured.out


# ---------------------------------------------------------------------------
# Shortcut — to_yaml() / load_yaml()
# ---------------------------------------------------------------------------

def test_shortcut_yaml_roundtrip(setup_pathnavigator, tmp_path):
    pn = setup_pathnavigator
    pn.folder1.set_sc('f1')
    yaml_file = str(tmp_path / 'shortcuts.yml')
    pn.sc.to_yaml(yaml_file)
    assert os.path.exists(yaml_file)

    pn2 = PathNavigator(pn._pn_root)
    pn2.sc.load_yaml(yaml_file)
    assert 'f1' in pn2.sc.to_dict()
    assert pn2.sc.get('f1') == pn.folder1.get()


# ---------------------------------------------------------------------------
# Shortcut — load_dict()
# ---------------------------------------------------------------------------

def test_shortcut_load_dict(setup_pathnavigator):
    pn = setup_pathnavigator
    data = {'my_folder': str(pn.folder1.get()), 'my file': str(pn.folder2.get())}
    pn.sc.load_dict(data)
    assert pn.sc.get('my_folder') == pn.folder1.get()
    # name with space gets converted to valid attribute
    assert pn.sc.get('my file') == pn.folder2.get()


# ---------------------------------------------------------------------------
# Shortcut — add_all()
# ---------------------------------------------------------------------------

def test_shortcut_add_all_folders(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add_all(pn.get(), only_folders=True)
    d = pn.sc.to_dict()
    assert 'folder1' in d
    assert 'folder2' in d

def test_shortcut_add_all_files(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add_all(pn.folder1.get(), only_files=True)
    d = pn.sc.to_dict()
    assert 'file1.txt' in d

def test_shortcut_add_all_with_prefix(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add_all(pn.get(), only_folders=True, prefix='root_')
    d = pn.sc.to_dict()
    assert 'root_folder1' in d

def test_shortcut_add_all_only_include(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add_all(pn.get(), only_include=['folder1'])
    d = pn.sc.to_dict()
    assert 'folder1' in d
    assert 'folder2' not in d

def test_shortcut_add_all_only_exclude(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add_all(pn.get(), only_exclude=['folder1'])
    d = pn.sc.to_dict()
    assert 'folder1' not in d
    assert 'folder2' in d


# ---------------------------------------------------------------------------
# Shortcut — overwrite protection
# ---------------------------------------------------------------------------

def test_shortcut_overwrite_protection(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add('f1', pn.folder1.get())
    with pytest.raises(AttributeError):
        pn.sc.add('f1', pn.folder2.get())  # duplicate without overwrite

def test_shortcut_overwrite_allowed(setup_pathnavigator):
    pn = setup_pathnavigator
    pn.sc.add('f1', pn.folder1.get())
    pn.sc.add('f1', pn.folder2.get(), overwrite=True)
    assert pn.sc.f1 == pn.folder2.get()


# ---------------------------------------------------------------------------
# Shortcut — missing shortcut raises AttributeError
# ---------------------------------------------------------------------------

def test_shortcut_getattr_missing(setup_pathnavigator):
    pn = setup_pathnavigator
    with pytest.raises(AttributeError):
        _ = pn.sc.nonexistent


# ---------------------------------------------------------------------------
# FileNotFoundError from get()
# ---------------------------------------------------------------------------

def test_get_raises_file_not_found(setup_pathnavigator):
    pn = setup_pathnavigator
    with pytest.raises(FileNotFoundError):
        pn.folder1.get("does_not_exist.txt")

def test_get_raises_file_not_found_nested(setup_pathnavigator):
    pn = setup_pathnavigator
    with pytest.raises(FileNotFoundError):
        pn.get("ghost_folder")


# ---------------------------------------------------------------------------
# add_all with both only_include and only_exclude simultaneously
# ---------------------------------------------------------------------------

def test_shortcut_add_all_include_and_exclude(tmp_path):
    """Both filters must be applied together, not as mutually exclusive."""
    root = tmp_path / "root"
    root.mkdir()
    (root / "data_a.txt").touch()
    (root / "data_b.txt").touch()
    (root / "test_a.txt").touch()

    from pathnavigator.shortcut import Shortcut
    sc = Shortcut()
    # include all .txt files, but exclude those starting with 'test'
    sc.add_all(root, only_include=["*.txt"], only_exclude=["test*"])
    d = sc.to_dict()
    assert "data_a.txt" in d
    assert "data_b.txt" in d
    assert "test_a.txt" not in d








