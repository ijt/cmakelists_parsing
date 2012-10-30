# -*- coding: utf-8 -*-

'''A CMakeLists parser using funcparserlib.

The parser is based on [examples of the CMakeLists format][1].

  [1]: http://www.vtk.org/Wiki/CMake/Examples

'''

from __future__ import unicode_literals, print_function
import re
import pypeg2 as p
import list_fix

class Arg(p.str):
    grammar = re.compile(r'[${}_a-zA-Z0-9.]+')

class Comment(p.str):
    grammar = p.comment_sh, p.endl

class Command(list_fix.List):
    grammar = p.name(), '(', p.some([Arg, Comment]), ')', p.endl

class File(list_fix.List):
    grammar = p.some([Command, Comment])

def parse(s):
    return p.parse(s, File)

# Inverse of parse
compose = p.compose

def main():
    import sys
    ENCODING = 'utf-8'
    input = sys.stdin.read().decode(ENCODING)
    tree = parse(input)
    print(compose(tree).encode(ENCODING))

if __name__ == '__main__':
    main()
