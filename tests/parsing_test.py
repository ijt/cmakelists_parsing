#!/usr/bin/env python

import unittest

from cmakelists_parsing.parsing import (
    File, Command, CommentBlock, Comment, Arg, parse, compose)

def command(name, args):
    return Command(args, name=name)

class ParsingTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

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

    def assertStringEqualIgnoreSpace(self, a, b):
        a2 = ' '.join(a.split())
        b2 = ' '.join(b.split())
        msg = '\nExpected\n%s\ngot\n%s\n(ignoring whitespace details)' % (a, b)
        self.assertEqual(a2, b2, msg)

    def test_arg_comments_preserved(self):
        input = '''
some_command (
    x  # inline comment about x
    )
'''
        output = compose(parse(input))

    def test_comments_preserved(self):
        input = '''\
# file comment

# comment above command
command1 (VERSION 2.6) # inline comment for command1

command2 (x  # inline comment about x
    "y"      # inline comment about a quoted string "y"
    ) # inline comment for command2
'''
        output = compose(parse(input))

        self.assertStringEqualIgnoreSpace(input, output)

    def test_multiline_string(self):
        s = '''
string containing
newlines
'''
        input = '''
set (MY_STRING "%s")
''' % s
        tree = parse(input)
        expected = File([command('set', [Arg('MY_STRING'),
                                         QuotedString(s)]))])
        self.assertEqual(expected, tree)

if __name__ == '__main__':
    unittest.main()

