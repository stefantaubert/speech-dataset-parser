import unittest

from speech_dataset_parser.mailabs import parse


class UnitTests(unittest.TestCase):
  def test_all_utterances_are_included(self):
    dest = '/home/mi/data/mailabs'
    res = parse(dest)
    self.assertEqual(len(res), 314990)


if __name__ == '__main__':

  suite = unittest.TestLoader().loadTestsFromTestCase(UnitTests)
  unittest.TextTestRunner(verbosity=2).run(suite)
