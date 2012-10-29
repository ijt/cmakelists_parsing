#!/usr/bin/env python

import unittest

from funcparserlib.lexer import Token
from cmakelists_parsing.parsing import File, Command, Comment, Arg, tokenize, \
    parse, CmParsingError

class ParsingTestCase(unittest.TestCase):

    def test_tokenize_empty(self):
        self.assertEqual([], tokenize(''))

    def test_tokenize_nonempty(self):
    	cm_input = '''
		# This is a comment
		link_directories (${HELLO_BINARY_DIR}/Hello # inline comment
		)'''
        output = tokenize(cm_input)
        expected = [
            Token('Comment', '# This is a comment'),
            Token('Word', 'link_directories'),
            Token('LParen', '('),
            Token('Word', '${HELLO_BINARY_DIR}/Hello'),
            Token('Comment', '# inline comment'),
            Token('RParen', ')'),
        ]
        self.assertEqual(expected, output)

    def test_parse_empty_raises_exception(self):
    	self.assertRaises(CmParsingError, parse, [])

    def test_parse_nonempty1(self):
    	input = 'FIND_PACKAGE(ITK REQUIRED)'
    	output = parse(tokenize(input))
    	expected = File([Command('FIND_PACKAGE', [Arg('ITK'), Arg('REQUIRED')])])
    	msg = '\nexpected\n%s\ngot\n%s' % (repr(expected), repr(output))
    	self.assertEqual(expected, output, msg)

    def test_parse_nonempty2(self):
    	input = '''
# Top level comment
FIND_PACKAGE(ITK REQUIRED)
INCLUDE(${ITK_USE_FILE})

ADD_EXECUTABLE(CastImageFilter CastImageFilter.cxx)
TARGET_LINK_LIBRARIES(CastImageFilter # inline comment 1
vtkHybrid   #inline comment 2
ITKIO ITKBasicFilters ITKCommon
)
    	'''

    	output = parse(tokenize(input))

    	expected = File([
    		Comment('# Top level comment'),
    		Command('FIND_PACKAGE', [Arg('ITK'), Arg('REQUIRED')]),
    		Command('INCLUDE', [Arg('${ITK_USE_FILE}')]),

    		Command('ADD_EXECUTABLE', [Arg('CastImageFilter'), Arg('CastImageFilter.cxx')]),
    		Command('TARGET_LINK_LIBRARIES', [Arg('CastImageFilter'),
    										  Comment('# inline comment 1'),
    										  Arg('vtkHybrid'),
    										  Comment('#inline comment 2'),
    										  Arg('ITKIO'),
    										  Arg('ITKBasicFilters'),
    										  Arg('ITKCommon')])
    		])
    	msg = '\nexpected\n%s\ngot\n%s' % (expected, output)
    	self.assertEqual(expected, output, msg)

    def test_idempotency_of_parsing_and_unparsing(self):
		input = '''
# Top level comment
FIND_PACKAGE(ITK REQUIRED)
INCLUDE(${ITK_USE_FILE})
'''
		round_trip = lambda s: str(parse(tokenize(s)))
		self.assertEqual(round_trip(input), round_trip(round_trip(input)))

    def test_invalid_format_raises_an_exception(self):
		input = 'FIND_PACKAGE('
		toks = tokenize(input)
		self.assertRaises(CmParsingError, parse, toks)

if __name__ == '__main__':
    unittest.main()

