#!/usr/bin/env python

import unittest

from funcparserlib.lexer import Token
from cmakelists_parsing import parsing as cmpp

class ParsingTestCase(unittest.TestCase):

    def test_tokenize_empty(self):
        self.assertEqual([], cmpp.tokenize(''))

    def test_tokenize_stuff(self):
    	cm_input = '''
		# This is a comment
		link_directories (${HELLO_BINARY_DIR}/Hello # inline comment
		)'''
        output = cmpp.tokenize(cm_input)
        expected = [
            Token('Comment', '# This is a comment'),
            Token('Word', 'link_directories'),
            Token('LParen', '('),
            Token('Word', '${HELLO_BINARY_DIR}/Hello'),
            Token('Comment', '# inline comment'),
            Token('RParen', ')'),
        ]
        self.assertEqual(expected, output)

if __name__ == '__main__':
    unittest.main()

