# -*- coding: utf-8 -*-

'''
A parser for files in CMakeLists.txt format:

http://www.vtk.org/Wiki/CMake/Examples

'''

from __future__ import unicode_literals, print_function
import re
import pypeg2 as p
import list_fix

class QuotedString(p.str):
    grammar = re.compile(r'"[^"]*"')

class Arg(p.str):
    grammar = re.compile(r'[^" \t\r\n()#]+')

class Comment(p.str):
    grammar = p.comment_sh, p.endl

class CommentBlock(list_fix.List):
    grammar = p.endl, p.some(Comment)

class Command(list_fix.List):
    grammar = p.name(), '(', p.maybe_some([Arg, QuotedString, Comment]), ')', p.endl

class File(list_fix.List):
    grammar = p.some([Command, CommentBlock])

def parse(s, filename='<string>'):
    '''
    parse(s, filename) parses a string s in CMakeLists format whose
    contents are assumed to have come from the named file.
    '''
    return p.parse(s, File, filename=filename)

start_rx = re.compile(r'^\s*(if|foreach|macro|function)\s*\(', re.IGNORECASE)
else_rx = re.compile(r'^\s*else\s*\(', re.IGNORECASE)
end_rx = re.compile(r'^\s*(endif|endforeach|endmacro|endfunction)\s*\(', re.IGNORECASE)
def compose_lines(tree, indent):
    '''
    compose_lines(tree, indent) yields indented lines of the
    pretty-print of the given tree.
    '''
    s = p.compose(tree)
    level = 0
    for line in s.splitlines():
        if start_rx.match(line):
            yield level*indent + line
            level += 1
        elif else_rx.match(line):
            yield (level-1)*indent + line
        elif end_rx.match(line):
            level -= 1
            yield level*indent + line
        else:
            yield level*indent + line

def compose(tree, indent='    '):
    '''
    compose(tree, indent) returns the pretty-print string for tree
    with indentation given by the string indent.
    '''
    return '\n'.join(compose_lines(tree, indent)) + '\n'

def main():
    import sys
    files = (open(f) for f in sys.argv[1:]) if sys.argv[1:] else [sys.stdin]
    for f in files:
        with f:
            input = f.read()
            tree = parse(input)
            print(compose(tree))

if __name__ == '__main__':
    main()
