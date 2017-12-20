import unittest
from unittest import mock
from random import randrange
import io
from base64 import b64decode
from binascii import hexlify

from t1 import Archive, ArchiveUsingDict, ArchiveUsingFile, \
    KeyValueAppendOnly, KVAOUsingDict, KVAOUsingFile, \
    ArF, Index, Volume


class TestArF(unittest.TestCase):
    def setUp(self):
        self.f = io.BytesIO(b"The quick brown fox jumped over the lazy dog.")
        self.f.name = 'foxfile'
        self.arf = ArF(self.f)
        # echo -n 'The quick brown fox jumped over the lazy dog.' | openssl dgst -sha256
        self.hexdigest = b'68b1282b91de2c054c36629cb8dd447f12f096d3e3c587978dc2248444633483'

    def testInit(self):
        self.assertIsInstance(self.arf, ArF)

    def testKey(self):
        k = self.arf.k
        self.assertEqual(hexlify(b64decode(k)), self.hexdigest)

    def testKeyKeepPos(self):
        k = self.arf.k
        self.assertEqual(self.f.read(), b"The quick brown fox jumped over the lazy dog.")

    def testKeyKeepPosPartialRead(self):
        self.f.read(10)
        k = self.arf.k
        self.assertEqual(hexlify(b64decode(k)), self.hexdigest)
        self.assertEqual(self.f.read(), b"The quick brown fox jumped over the lazy dog."[10:])

    def testName(self):
        self.assertEqual('foxfile', self.arf.name)


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

class TestKVAO(unittest.TestCase):
    def setUp(self):
        self.arfile = io.BytesIO()
        self.kvaoUsingFile = KVAOUsingFile(self.arfile)
        self.kvaoUsingDict = KVAOUsingDict()
        self.kvaos = [self.kvaoUsingDict, self.kvaoUsingFile]

    def testInit(self):
        for kv in self.kvaos:
            with self.subTest(kv=kv):
                self.assertIsInstance(kv, KeyValueAppendOnly)

    def testInclude(self):
        for kv in self.kvaos:
            with self.subTest(kv=kv):
                foo = io.BytesIO(b'foo')
                #foo.name = 'foof'
                bar = io.BytesIO(b'bar')
                #bar.name = 'barf'
                blort = io.BytesIO(b'blort')
                #blort.name = 'blortf'
                self.assertFalse(kv.has('fook'))
                self.assertFalse(kv.has('bark'))
                self.assertFalse(kv.has('blortk'))
                self.assertEqual(0, len(kv))
                kv.include('fook', foo)
                self.assertTrue(kv.has('fook'))
                self.assertFalse(kv.has('bark'))
                self.assertFalse(kv.has('blortk'))
                self.assertEqual(b'foo', kv.get('fook').read())
                self.assertEqual(1, len(kv))
                kv.include('fook', foo)         # duplicate include
                self.assertEqual(b'foo', kv.get('fook').read())
                kv.include('bark', bar)
                self.assertTrue(kv.has('fook'))
                self.assertTrue(kv.has('bark'))
                self.assertFalse(kv.has('blortk'))
                self.assertEqual(b'bar', kv.get('bark').read())
                self.assertEqual(2, len(kv))
                kv.include('blortk', blort)
                self.assertTrue(kv.has('fook'))
                self.assertTrue(kv.has('bark'))
                self.assertTrue(kv.has('blortk'))
                self.assertEqual(b'blort', kv.get('blortk').read())
                self.assertEqual(3, len(kv))
                return


class TestArchive(unittest.TestCase):
    def setUp(self):
        self.ar = self.arud = ArchiveUsingDict()
        self.aruf = ArchiveUsingFile(io.BytesIO())
        #self.archives = [self.arud, self.aruf]
        self.archives = [self.arud] # DEBUG
        self.foof = io.BytesIO(b'foo')
        self.foof.name = 'foof'
        self.barf = io.BytesIO(b'bar')
        self.barf.name = 'barf'
        self.blortf = io.BytesIO(b'blort')
        self.blortf.name = 'blortf'

    def testInit(self):
        for ar in self.archives:
            with self.subTest(ar=ar):
                self.assertIsInstance(ar, Archive)

    def testInclude(self):
        for ar in self.archives:
            with self.subTest(ar=ar):
                self.assertFalse(ar.has('foof'))
                ar.include(self.foof)
                self.assertTrue(ar.has('foof'))

    def testGet(self):
        for ar in self.archives:
            with self.subTest(ar=ar):
                ar.include(self.foof)
                f = ar.get('foof')
                self.assertIsInstance(f, io.IOBase)
                self.assertEqual(b'foo', f.read())

    def testHas(self):
        for ar in self.archives:
            with self.subTest(ar=ar):
                self.assertFalse(ar.has('foof'))
                self.assertFalse(ar.has('barf'))
                self.assertFalse(ar.has('blortf'))
                self.assertFalse(ar.has('/the/quick/brown/fox'))
                ar.include(self.foof)
                self.assertTrue(ar.has('foof'))
                self.assertFalse(ar.has('barf'))
                self.assertFalse(ar.has('blortf'))
                self.assertFalse(ar.has('/the/quick/brown/fox'))
                ar.include(self.barf)
                self.assertTrue(ar.has('foof'))
                self.assertTrue(ar.has('barf'))
                self.assertFalse(ar.has('blortf'))
                self.assertFalse(ar.has('/the/quick/brown/fox'))
                ar.include(self.blortf)
                self.assertTrue(ar.has('foof'))
                self.assertTrue(ar.has('barf'))
                self.assertTrue(ar.has('blortf'))
                self.assertFalse(ar.has('/the/quick/brown/fox'))


    def testMore(self):
        for ar in self.archives:
            with self.subTest(ar=ar):
                self.assertFalse(ar.has('foof'))
                self.assertFalse(ar.has('barf'))
                self.assertFalse(ar.has('blortf'))
                ar.include(self.foof)
                self.assertTrue(ar.has('foof'))
                f = ar.get('foof')
                self.assertIsInstance(f, io.IOBase)
                self.assertEqual(b'foo', f.read())
                ar.include(self.barf)
                self.assertTrue(ar.has('barf'))
                f = ar.get('barf')
                self.assertIsInstance(f, io.IOBase)
                self.assertEqual(b'bar', f.read())
                ar.include(self.blortf)
                self.assertTrue(ar.has('blortf'))
                f = ar.get('blortf')
                self.assertIsInstance(f, io.IOBase)
                self.assertEqual(b'blort', f.read())



if __name__ == '__main__':
    unittest.main()
