from collections import namedtuple
import re
import StringIO

QuotedString = namedtuple('QuotedString', 'contents comments')
_Arg = namedtuple('Arg', 'contents comments')
_Command = namedtuple('Command', 'name body comments')
BlankLine = namedtuple('BlankLine', '')
File = namedtuple('File', 'contents')
# TODO: if, else, endif, function, endfunction, macro, endmacro
class Comment(str): pass

def Arg(contents, comments=None):
    return _Arg(contents, comments or [])

def Command(name, body, comments=None):
    return _Command(name, body, comments or [])

class CMakeParseError(Exception):
    pass

def parse(s, path='<string>'):
    '''
    parse(s, filename) parses a string s in CMakeLists format whose
    contents are assumed to have come from the named file.
    '''
    toks = tokenize_lines(s.splitlines())
    return File(list(parseFile(toks)))

def strip_blanks(tree):
    return File([x for x in tree.contents if not isinstance(x, BlankLine)])

def compose(tree, indent='    '):
    '''
    compose(tree, indent) returns the pretty-print string for tree
    with indentation given by the string indent.
    '''
    return '\n'.join(compose_lines(tree.contents, indent))

def compose_lines(tree_contents, indent):
    for item in tree_contents:
        if isinstance(item, (Comment, str)):
            yield item
        elif isinstance(item, BlankLine):
            yield ''
        elif isinstance(item, _Command):
            for line in command_to_lines(item):
                yield line

def command_to_lines(cmd):
    yield cmd.name + '(' + ' '.join(map(arg_to_str, cmd.body)) + ')'

def arg_to_str(arg):
    return arg.contents

def parseFile(toks):
    '''
    parseFile(toks) yields top-level elements of the syntax tree for
    a CMakeLists file, given a generator of tokens from the file.
    '''
    for line_num, (typ, tok_contents) in toks:
        if typ == 'comment':
            yield Comment(tok_contents)
        elif typ == 'blank line':
            yield BlankLine()
        elif typ == 'word':
            yield parseCommand(line_num, tok_contents, toks)

def parseCommand(start_line_num, command_name, toks):
    cmd = Command(name=command_name, body=[], comments=[])
    expect('left paren', toks)
    for line_num, (typ, tok_contents) in toks:
        if typ == 'right paren':
            return cmd
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
    tokenize_cmake(lines) returns a list of (line_num, (token_type, token_contents))
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
    import sys
    files = (open(f) for f in sys.argv[1:]) if sys.argv[1:] else [sys.stdin]
    for f in files:
        with f:
            input = f.read()
            tree = parse(input)
            print(compose(tree))

if __name__ == '__main__':
    main()
