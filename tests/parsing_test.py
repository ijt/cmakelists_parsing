#!/usr/bin/env python

import unittest

from cmakelists_parsing.parsing import (
    File, Command, CommentBlock, Comment, Arg, parse, compose)

def command(name, args):
    return Command(args, name=name)

class ParsingTestCase(unittest.TestCase):

    def test_parse_empty_raises_exception(self):
    	self.assertRaises(Exception, parse, '')

    def test_parse_nonempty1(self):
    	input = 'FIND_PACKAGE(ITK REQUIRED)'
    	output = parse(input)
    	expected = File([command('FIND_PACKAGE', [Arg('ITK'), Arg('REQUIRED')])])
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

    	output = parse(input)

    	expected = File([
    		CommentBlock(['# Top level comment']),
    		command('FIND_PACKAGE', [Arg('ITK'), Arg('REQUIRED')]),
    		command('INCLUDE', [Arg('${ITK_USE_FILE}')]),

    		command('ADD_EXECUTABLE', [Arg('CastImageFilter'), Arg('CastImageFilter.cxx')]),
    		command('TARGET_LINK_LIBRARIES', [Arg('CastImageFilter'),
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
		input = '''\
# Top level comment
FIND_PACKAGE(ITK REQUIRED)
INCLUDE(${ITK_USE_FILE})
'''
		round_trip = lambda s: compose(parse(s))
		self.assertEqual(round_trip(input), round_trip(round_trip(input)))

    def test_invalid_format_raises_an_exception(self):
		input = 'FIND_PACKAGE('
		self.assertRaises(Exception, parse, input)

    def test_line_numbers_in_exceptions(self):
		input = '''\
FIND_PACKAGE(ITK)
INCLUDE(
'''
		try:
			parse(input)
			self.fail('Expected an exception, but none was raised.')
		except Exception as e:
			self.assertTrue('line 2' in str(e))

    def test_arg_with_a_slash(self):
        tree = parse('include_directories (${HELLO_SOURCE_DIR}/Hello)')
        expected = File([
            command('include_directories', ['${HELLO_SOURCE_DIR}/Hello'])
            ])
        self.assertEqual(expected, tree)

    def test_command_with_no_args(self):
        tree = parse('cmd()')
        expected = File([command('cmd', [])])
        self.assertEqual(expected, tree)

if __name__ == '__main__':
    unittest.main()

