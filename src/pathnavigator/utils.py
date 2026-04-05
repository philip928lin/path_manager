"""
Base utilities for PathNavigator classes.

Provides the Base class which supplies a ``help()`` class method for
displaying available public methods and their docstrings.
"""


class Base:
    @classmethod
    def help(cls, method_name=None, show_doc=True):
        """
        Display all methods in the class with their docstrings.
        
        Parameters
        ==========
        method_name : str, optional
            Name of the method to display. If not specified, all methods will be displayed.
        show_doc : bool, optional
            If True, show the docstring of the method. Default is True.
            
        Returns
        =======
        None
        """
        print(f"Available methods in {cls.__name__} class:\n")
        if method_name:
            method = getattr(cls, method_name, None)
            if method and callable(method):
                if show_doc:
                    print(f"{method_name}:\n{method.__doc__}\n")
                else:
                    print(method_name)
            else:
                print(f"Method '{method_name}' not found in {cls.__name__} class.")
        else:
            # Display all methods in the class
            for method_name in dir(cls):
                if (callable(getattr(cls, method_name))
                        and not method_name.startswith("_")):
                    method = getattr(cls, method_name)
                    if show_doc:
                        print(f"{method_name}:\n{method.__doc__}\n")
                    else:
                        print(method_name)