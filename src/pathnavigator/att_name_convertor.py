"""
Attribute name converter for PathNavigator.

Converts arbitrary filesystem names (which may contain spaces, special
characters, or Python keywords) to valid Python identifiers and maintains
bidirectional mappings so original names can always be recovered.
"""

import re
import keyword
from dataclasses import dataclass, field
from .utils import Base

__all__ = ["AttributeNameConverter"]

@dataclass
class AttributeNameConverter(Base):
    """
    A class to convert original names to valid attribute names and store the mapping.

    Methods
    -------
    to_valid_name(name)
        Convert the original name to a valid attribute name.
    get(name)
        Get the valid attribute name for the given original name.
    """
    _pn_org_to_valid_name: dict = field(default_factory=dict)
    _pn_valid_name_to_org: dict = field(default_factory=dict)
    _pn_invalid_name_list: list = field(
        default_factory=lambda: [
            "root_dir", "sc", "ls", "remove", "join", "mkdir", "exists",
            "set_sc", "set_all_to_sc", "get", "get_str",
            "listdirs", "listfiles", "chdir", "add_to_sys_path", "tree",
            "name", "parent_path", "subfolders", "files"]
        )  # Reserved Folder & PathNavigator method and attribute names

    def to_valid_name(self, name: str) -> str:
        """
        Convert the original name to a valid attribute name.
        
        Parameters
        ----------
        name : str
            The original name to convert.
        """
        if self._pn_is_valid_attribute_name(name) is False:
            valid_name = self._pn_convert_to_valid_attribute_name(name)
            #print(f"Convert '{name}' to a valid attribute name, '{valid_name}'.")
            return valid_name
        else:
            return name

    def get_org(self, name: str) -> str:
        """
        Get the valid attribute name for the given original name.
        
        Parameters
        ----------
        name : str
            The original name to get the valid attribute name for.
        """
        if name in self._pn_valid_name_to_org:
            return self._pn_valid_name_to_org[name]
        else:
            return name
    
    def get_valid(self, name: str) -> str:
        """
        Get the valid attribute name for the given original name.
        
        Parameters
        ----------
        name : str
            The original name to get the valid attribute name for.
        """
        if name in self._pn_org_to_valid_name:
            return self._pn_org_to_valid_name[name]
        else:
            return name
    
    def update_invalid_name_list(self, invalid_name_list: list):
        """
        Update the list of invalid names.
        
        Parameters
        ----------
        invalid_name_list : list
            The list of invalid names to update.
        """
        self._pn_invalid_name_list = invalid_name_list
    
    def _pn_is_valid_attribute_name(
            self, name: str
            ) -> bool:
        """
        Check if a given attribute name is valid.
        
        Parameters
        ----------
        name : str
            The attribute name to check.
        """
        invalid_name_list = self._pn_invalid_name_list
        if name.startswith('_pn_'):
            raise ValueError(f"Strings starting with '_pn_' are reserved in PathNavigator. Please modify '{name}' to eligible naming.")
        if name in invalid_name_list:
            raise ValueError(f"Please avoid using reserved names and follow the naming conventions. Reserved names {invalid_name_list}")
        return name.isidentifier() and not keyword.iskeyword(name)

    def _pn_convert_to_valid_attribute_name(self, name: str) -> str:
        """
        Convert ineligible attribute name to a valid one.
        
        Parameters
        ----------
        name : str
            The original name to convert.
        """
        # Replace invalid characters (anything not a letter, digit, or underscore) with underscores
        valid_name = re.sub(r'\W|^(?=\d)', '_', name)  # \W matches non-word characters, ^(?=\d) ensures no starting digit
        
        # Ensure the name starts with an underscore
        if not valid_name.startswith('_'):
            valid_name = '_' + valid_name
        
        # Check if the converted name is a Python keyword and append an underscore if necessary
        if keyword.iskeyword(valid_name):
            valid_name += '_'
        
        # Store the mapping of ineligible to eligible names
        self._pn_org_to_valid_name[name] = valid_name
        self._pn_valid_name_to_org[valid_name] = name
        
        return valid_name

    def _pn_get_name_mapping(self):
        """Return the dictionary that maps ineligible names to eligible names."""
        return self._pn_org_to_valid_name
    
    def remove(self, name: str):
        """
        Remove the mapping for the given name.
        
        Parameters
        ----------
        name : str
            The original name to remove from the mapping.
        """
        if name in self._pn_org_to_valid_name:
            valid_name = self._pn_org_to_valid_name.pop(name)
            self._pn_valid_name_to_org.pop(valid_name, None)
        else:
            pass