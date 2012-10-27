cmakelists\_parsing
===================

Python module for parsing CMakeLists.txt files.

Installing
----------

    python setup.py install

Usage
-----

    >>> from cmakelists_parsing.parsing import tokenize, parse
    >>> cmakelists_contents = 'FIND_PACKAGE(ITK REQUIRED)  # Hello, CMake!'
    >>> parse(tokenize(cmakelists_contents))
    File(commands_and_comments=[Command(name='FIND_PACKAGE', args_and_inline_comments=[Arg(contents='ITK'), Arg(contents='REQUIRED')]), Comment(contents='# Hello, CMake!')])

