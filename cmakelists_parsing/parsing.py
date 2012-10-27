# -*- coding: utf-8 -*-

'''A CMakeLists parser using funcparserlib.

The parser is based on [examples of the CMakeLists format][1].
It is a heavily modified version of the dot.py example in
[the funcparserlib source code][2].

  [1]: http://www.vtk.org/Wiki/CMake/Examples
  [2]: https://code.google.com/p/funcparserlib/

'''

import sys, os
import pprint
from re import MULTILINE
from funcparserlib.util import pretty_tree
from funcparserlib.lexer import make_tokenizer, Token, LexerError
from funcparserlib.parser import (some, a, maybe, many, finished, skip,
    oneplus, forward_decl, NoParseError)
try:
    from collections import namedtuple
except ImportError:
    # Basic implementation of namedtuple for 2.1 < Python < 2.6
    def namedtuple(name, fields):
        'Only space-delimited fields are supported.'
        def prop(i, name):
            return (name, property(lambda self: self[i]))
        methods = dict(prop(i, f) for i, f in enumerate(fields.split(' ')))
        methods.update({
            '__new__': lambda cls, *args: tuple.__new__(cls, args),
            '__repr__': lambda self: '%s(%s)' % (
                name,
                ', '.join('%s=%r' % (
                    f, getattr(self, f)) for f in fields.split(' ')))})
        return type(name, (tuple,), methods)

ENCODING = 'utf-8'

File = namedtuple('File', 'commands_and_comments')
Comment = namedtuple('Comment', 'contents')
Command = namedtuple('Command', 'name args_and_inline_comments')
Arg = namedtuple('Arg', 'contents')

def tokenize(str):
    'str -> Sequence(Token)'
    specs = [
        ('Comment', (r'#.*',)),
        ('NL',      (r'[\r\n]+',)),
        ('Space',   (r'[ \t\r\n]+',)),
        ('Word',    (r'[^\'" \t\r\n()]+',)),
        ('LParen',  (r'\(',)),
        ('RParen',  (r'\)',)),
        ('String',  (r'"[^"]*"',)), # '\"' escapes are ignored
    ]
    junk = ['NL', 'Space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in junk]

def parse(seq):
    'Sequence(Token) -> object'
    def make_command(parts):
        print 'command parts:', parts
        return Command(parts[0], parts[1])
    arg = some(lambda t: t.type == 'Word') >> (lambda w: Arg(w.value))
    comment = some(lambda t: t.type == 'Comment') >> (lambda c: Comment(c.value))
    identifier = some(lambda t: t.type == 'Word') >> (lambda i: i.value)
    lparen = skip(some(lambda t: t.type == 'LParen'))
    rparen = skip(some(lambda t: t.type == 'RParen'))
    command = identifier + lparen + many(arg | comment) + rparen >> (lambda (name, args): Command(name, args))
    cmakelists = many(comment | command) >> (lambda parts: File(parts))
    return cmakelists.parse(seq)

def main():
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
    #import funcparserlib
    #funcparserlib.parser.debug = True
    try:
        stdin = os.fdopen(sys.stdin.fileno(), 'rb')
        input = stdin.read().decode(ENCODING)
        tree = parse(tokenize(input))
        print pprint.pformat(tree).encode(ENCODING)
    except (NoParseError, LexerError), e:
        msg = (u'syntax error: %s' % e).encode(ENCODING)
        print >> sys.stderr, msg
        sys.exit(1)

if __name__ == '__main__':
    main()

