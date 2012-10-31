from collections import namedtuple
import re
import StringIO

QuotedString = namedtuple('QuotedString', 'contents')
Arg = namedtuple('Arg', 'contents')
Command = namedtuple('Command', 'body name')
Comment = namedtuple('Comment', 'contents')
File = namedtuple('File', 'contents')
# TODO: if, else, endif, function, endfunction, macro, endmacro

# TODO: Handle multiline strings.
#
scanner = re.Scanner([
    (r'#.*',            lambda scanner, token: ("COMMENT", token)),
    (r'"[^"]*"',        lambda scanner, token: ("STRING", token)),
    (r"\(",             lambda scanner, token: ("LPAREN", token)),
    (r"\)",             lambda scanner, token: ("RPAREN", token)),
    (r'[^ \t\r\n()#"]+', lambda scanner, token: ("WORD", token)),
    (r"\s+",            None), # skip other whitespace
])

def tokenize_lines(lines):
    """
    tokenize_cmake(lines) returns a list of (line_num, (token_type, token_contents))
    given a list of lines from a CMakeLists file.
    """
    for line_num, line in enumerate(lines):
        toks, remainder = scanner.scan(line)
        if remainder != '':
            msg = 'Unrecognized tokens at line %s: %s' % (line_num, remainder)
            raise ValueError(msg)
        for t in toks:
            yield line_num, t

def parseFile(toks):
    t = toks.next()
    return File([])

def parse(s, path='<string>'):
    toks = tokenize(s)
    return parseFile(toks)
