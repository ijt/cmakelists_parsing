cmakelists\_parsing
===================

Python module for parsing CMakeLists.txt files.

Installing
----------

    python setup.py install

or

    sudo pip install cmakelists_parsing

Usage
-----

    >>> import cmakelists_parsing.parsing as cmp
    >>> cmakelists_contents = 'FIND_PACKAGE(ITK REQUIRED)  # Hello, CMake!'
    >>> cmp.parse(cmakelists_contents)
    File([Command([u'ITK', u'REQUIRED']), CommentBlock([u'# Hello, CMake!'])])

