import glob
import os
import unittest

import cmakelists_parsing.parsing as cmp

class FilesTestCase(unittest.TestCase):
    def test_idempotency_of_parse_unparse_on_examples(self):
        round_trip = lambda s, path='<string>': cmp.compose(cmp.parse(s, path))

        paths = glob.glob(os.path.join(os.path.dirname(__file__),
                                       '..', 'example_inputs', '*'))
        for path in paths:
            with open(path) as file:
                contents = file.read()
                self.assertEqual(round_trip(contents, path), round_trip(round_trip(contents, path)),
                    'Failed on %s' % path)
