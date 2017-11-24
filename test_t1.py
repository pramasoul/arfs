import unittest
from unittest import mock
from random import randrange
import io
from base64 import b64decode
from binascii import hexlify

from t1 import Archive, ArF, Index, Volume

class TestArF(unittest.TestCase):
    def setUp(self):
        self.f = io.BytesIO(b"The quick brown fox jumped over the lazy dog.")
        self.a = ArF(self.f)
        # echo -n 'The quick brown fox jumped over the lazy dog.' | openssl dgst -sha25
        self.hexdigest = b'68b1282b91de2c054c36629cb8dd447f12f096d3e3c587978dc2248444633483'

    def testInit(self):
        self.assertIsInstance(self.a, ArF)

    def testKey(self):
        k = self.a.k
        self.assertEqual(hexlify(b64decode(k)), self.hexdigest)


    def testKeyKeepPos(self):
        k = self.a.k
        self.assertEqual(self.f.read(), b"The quick brown fox jumped over the lazy dog.")

    def testKeyKeepPos(self):
        self.f.read(10)
        k = self.a.k
        self.assertEqual(hexlify(b64decode(k)), self.hexdigest)
        self.assertEqual(self.f.read(), b"The quick brown fox jumped over the lazy dog."[10:])


class TestIndex(unittest.TestCase):
    def testInit(self):
        ix = Index()
        self.assertIsInstance(ix, Index)

    def testRecord(self):
        ix = Index()
        ix[b'foo'] = b'bar'
        self.assertEqual(b'bar', ix[b'foo'])

    def testLookup(self):
        ix = Index()
        with self.assertRaises(KeyError):
            ix[b'foo']
        ix[b'foo'] = b'bar'
        self.assertEqual(b'bar', ix[b'foo'])

    def testHas(self):
        ix = Index()
        self.assertFalse(b'foo' in ix)
        ix[b'foo'] = b'bar'
        self.assertTrue(b'foo' in ix)


class TestVolume(unittest.TestCase):
    def setUp(self):
        self.arfile = io.BytesIO()
        self.vol = Volume(self.arfile)

    def testInit(self):
        self.assertIsInstance(self.vol, Volume)

    def testAppend(self):
        vol = self.vol
        s, l = vol.append(b'fookey', io.BytesIO(b'foo'))
        self.assertEqual(s, 0)
        self.assertEqual(l, 3)
        self.assertEqual(self.arfile.getvalue(), b'foo')
        s, l = vol.append(b'barkey', io.BytesIO(b'bartleby'))
        self.assertEqual(s, 3)
        self.assertEqual(l, 8)
        self.assertEqual(self.arfile.getvalue(), b'foobartleby')

class TestArchive(unittest.TestCase):
    def testInit(self):
        ar = Archive('some_filename')
        self.assertIsInstance(ar, Archive)


if __name__ == '__main__':
    unittest.main()
