from __future__ import print_function
from collections import namedtuple
import re
import StringIO

from cmakelists_parsing import list_utils

QuotedString = namedtuple('QuotedString', 'contents comments')
_Arg = namedtuple('Arg', 'contents comments')
_Command = namedtuple('Command', 'name body comment')
BlankLine = namedtuple('BlankLine', '')
File = namedtuple('File', 'contents')
# TODO: if, else, endif, function, endfunction, macro, endmacro
class Comment(str):
    def __repr__(self):
        return 'Comment(' + str(self) + ')'

def Arg(contents, comments=None):
    return _Arg(contents, comments or [])

def Command(name, body, comment=None):
    return _Command(name, body, comment)

class CMakeParseError(Exception):
    pass

def parse(s, path='<string>'):
    '''
    parse(s, filename) parses a string s in CMakeLists format whose
    contents are assumed to have come from the named file.
    '''
    toks = tokenize_lines(s.splitlines())
    nums_items = list(parse_file(toks))
    nums_items = attach_comments_to_commands(nums_items)
    items = [item for line_num, item in nums_items]
    return File(items)

def strip_blanks(tree):
    return File([x for x in tree.contents if not isinstance(x, BlankLine)])

def compose(tree, tab='    '):
    '''
    Returns the pretty-print string for tree
    with indentation given by the string tab.
    '''
    return '\n'.join(compose_lines(tree.contents, tab)) + '\n'

def compose_lines(tree_contents, tab):
    level = 0
    for item in tree_contents:
        if isinstance(item, (Comment, str)):
            yield level * tab + item
        elif isinstance(item, BlankLine):
            yield ''
        elif isinstance(item, _Command):
            name = item.name.lower()
            if name in ('endif', 'else'):
                level -= 1
            for line in command_to_lines(item):
                yield level * tab + line
            if name in ('if', 'else'):
                level += 1

def command_to_lines(cmd):
    final_paren = '\n)' if cmd.body and cmd.body[-1].comments else ')'
    comment_part = '  ' + cmd.comment if cmd.comment else ''
    yield cmd.name + '(' + ' '.join(map(arg_to_str, cmd.body)) + final_paren + comment_part

def arg_to_str(arg):
    comment_part = '  ' + '\n'.join(arg.comments) + '\n' if arg.comments else ''
    return arg.contents + comment_part

def parse_file(toks):
    '''
    Yields line number ranges and top-level elements of the syntax tree for
    a CMakeLists file, given a generator of tokens from the file.

    toks must really be a generator, not a list, for this to work.
    '''
    for line_num, (typ, tok_contents) in toks:
        if typ == 'comment':
            yield ([line_num], Comment(tok_contents))
        elif typ == 'blank line':
            yield ([line_num], BlankLine())
        elif typ == 'word':
            line_nums, cmd = parse_command(line_num, tok_contents, toks)
            yield (line_nums, cmd)

def attach_comments_to_commands(nodes):
    return list_utils.merge_pairs(nodes, command_then_comment, attach_comment_to_command)

def command_then_comment(a, b):
    line_nums_a, thing_a = a
    line_nums_b, thing_b = b
    return (isinstance(thing_a, _Command) and
            isinstance(thing_b, Comment) and
            set(line_nums_a).intersection(line_nums_b))

def attach_comment_to_command(lnums_command, lnums_comment):
    command_lines, command = lnums_command
    _, comment = lnums_comment
    return command_lines, Command(command.name, command.body[:], comment)

def parse_command(start_line_num, command_name, toks):
    cmd = Command(name=command_name, body=[], comment=None)
    expect('left paren', toks)
    for line_num, (typ, tok_contents) in toks:
        if typ == 'right paren':
            line_nums = range(start_line_num, line_num + 1)
            return line_nums, cmd
        elif typ == 'left paren':
            raise ValueError('Unexpected left paren at line %s' % line_num)
        elif typ in ('word', 'string'):
            cmd.body.append(Arg(tok_contents, []))
        elif typ == 'comment':
            c = Comment(tok_contents)
            if cmd.body:
                cmd.body[-1].comments.append(c)
            else:
                cmd.comments.append(c)
    msg = 'File ended while processing command "%s" started at line %s' % (
        command_name, start_line_num)
    raise CMakeParseError(msg)

def expect(expected_type, toks):
    line_num, (typ, tok_contents) = toks.next()
    if typ != expected_type:
        msg = 'Expected a %s, but got "%s" at line %s' % (
            expected_type, tok_contents, line_num)
        raise CMakeParseError(msg)

# http://stackoverflow.com/questions/691148/pythonic-way-to-implement-a-tokenizer
# TODO: Handle multiline strings.
scanner = re.Scanner([
    (r'#.*',                lambda scanner, token: ("comment", token)),
    (r'"[^"]*"',            lambda scanner, token: ("string", token)),
    (r"\(",                 lambda scanner, token: ("left paren", token)),
    (r"\)",                 lambda scanner, token: ("right paren", token)),
    (r'[^ \t\r\n()#"]+',    lambda scanner, token: ("word", token)),
    (r"\s+",                None), # skip other whitespace
])

def tokenize_lines(lines):
    """
    Returns a list of (line_num, (token_type, token_contents))
    given a list of lines from a CMakeLists file.
    """
    for line_num, line in enumerate(lines, start=1):
        toks, remainder = scanner.scan(line)
        if remainder != '':
            msg = 'Unrecognized tokens at line %s: %s' % (line_num, remainder)
            raise ValueError(msg)
        if not toks:
            yield line_num, ('blank line', '')
        for t in toks:
            yield line_num, t

def main():
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Pretty-print CMakeLists files.')
    parser.add_argument('files', type=str, nargs='*',
                        help='files to pretty print (default is stdin)')
    parser.add_argument('-t', '--tree', action='store_true',
                        help='print out the syntax trees')
    args = parser.parse_args()
    filenames = args.files
    files = (open(f) for f in filenames) if filenames else [sys.stdin]
    for f in files:
        with f:
            input = f.read()
            tree = parse(input)
            if args.tree:
                # Print out AST
                print(str(tree))
            else:
                # Pretty print
                print(compose(tree), end='')

if __name__ == '__main__':
    main()
