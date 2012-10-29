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

class CmParsingError(Exception):
    pass

class PrettyRepr(object):
    def __repr__(self):
        import pprint
        return self.__class__.__name__ + '(' + pprint.pformat(vars(self)) + ')'

class Eq(object):
    def __eq__(self, other):
        return vars(self) == vars(other)

class CmObj(PrettyRepr, Eq):
    """
    Base class for syntax tree nodes.
    This gives them pretty printing and equality.
    """
    pass

class File(CmObj):
    """
    Root of the abstract syntax tree for a CMakeLists file
    """
    def __init__(self, contents):
        self.contents = contents

    def __str__(self):
        return '\n'.join(str(c) for c in self.contents) + '\n'

class Comment(CmObj):
    def __init__(self, contents):
        self.contents = contents

    def __str__(self):
        return self.contents

class Command(CmObj):
    # Some of the args for a command can be inline comments.
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        args = [str(a) + '\n' if isinstance(a, Comment) else str(a) for a in self.args]
        return self.name + '(' + ' '.join(args) + ')'

class Arg(CmObj):
    """
    Argument for a command
    """
    def __init__(self, contents):
        self.contents = contents

    def __str__(self):
        return self.contents

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
    cmakelists = oneplus(comment | command) + skip(finished) >> (lambda parts: File(parts))
    try:
        return cmakelists.parse(seq)
    except NoParseError as e:
        raise CmParsingError(str(e))

def main():
    try:
        stdin = os.fdopen(sys.stdin.fileno(), 'rb')
        input = stdin.read().decode(ENCODING)
        tree = parse(tokenize(input))
        print str(tree).encode(ENCODING)
    except (NoParseError, LexerError), e:
        msg = (u'syntax error: %s' % e).encode(ENCODING)
        print >> sys.stderr, msg
        sys.exit(1)

if __name__ == '__main__':
    main()

