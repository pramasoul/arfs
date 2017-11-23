import unittest
from unittest import mock
from random import randrange

from t1 import Archive, Index

class TestIndex(unittest.TestCase):
    def testInit(self):
        ix = Index()
        self.assertIsInstance(ix, Index)

    def testRecord(self):
        ix = Index()
        ix.record(b'foo', b'bar')
        self.assertEqual(b'bar', ix.lookup(b'foo'))

    def testLookup(self):
        ix = Index()
        with self.assertRaises(KeyError):
            ix.lookup(b'foo')
        ix.record(b'foo', b'bar')
        self.assertEqual(b'bar', ix.lookup(b'foo'))

    def testHas(self):
        ix = Index()
        self.assertFalse(ix.has(b'foo'))
        ix.record(b'foo', b'bar')
        self.assertTrue(ix.has(b'foo'))


class TestArchive(unittest.TestCase):
    def testInit(self):
        ar = Archive('some_filename')
        self.assertIsInstance(ar, Archive)


if __name__ == '__main__':
    unittest.main()
