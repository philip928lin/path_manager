PathNavigator
=============

.. image:: https://img.shields.io/pypi/v/pathnavigator
   :target: https://pypi.org/project/pathnavigator/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pathnavigator
   :target: https://pypi.org/project/pathnavigator/
   :alt: Supported Python versions

.. image:: https://github.com/philip928lin/PathNavigator/actions/workflows/test.yml/badge.svg
   :target: https://github.com/philip928lin/PathNavigator/actions/workflows/test.yml
   :alt: Test status

**PathNavigator** is a Python library for intuitive filesystem navigation.
Access directories and files as attributes, manage named shortcuts, and
perform common filesystem operations through a consistent,
platform-independent API built on :mod:`pathlib`.

.. code-block:: python

   import pathnavigator

   pn = pathnavigator.create("/path/to/project")

   pn.src.get()                   # Path object
   pn.src.get("main.py")          # path to a specific file
   pn.src.set_sc("source")        # bookmark the folder
   pn.sc.get("source")            # retrieve bookmark


Installation
------------

.. code-block:: bash

   pip install pathnavigator

Install the latest development version from GitHub:

.. code-block:: bash

   pip install git+https://github.com/philip928lin/PathNavigator.git


Key Features
------------

- **Attribute-style navigation** — access subfolders as ``pn.folder1.subfolder2``
- **Path retrieval** — get :class:`~pathlib.Path` objects or strings
- **Shortcuts** — bookmark frequently used paths; save and load as JSON or YAML
- **Flexible scanning** — filter by name pattern, depth, file/folder type, or hidden status
- **Tree visualization** — print an ASCII tree of the scanned directory structure
- **Cross-platform** — macOS, Linux, and Windows; Windows hidden-file attributes respected
- **System path management** — safely add directories to ``sys.path`` as strings


API Reference
-------------

.. toctree::
   :maxdepth: 3
   :caption: API

   source/pathnavigator


Changelog
---------

.. toctree::
   :maxdepth: 1
   :caption: About

   changelog


Indices
-------

* :ref:`genindex`
* :ref:`modindex`
