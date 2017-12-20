# Archive file system of sorts
# just sketching - tas


import base64
import hashlib
import io
from collections import defaultdict

class ArF:
    def __init__(self, f):
        self.f = f

    def __getattr__(self, attr_name):
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]
        try:
            getter_fun = self.__class__.__dict__['_get_' + attr_name]
        except KeyError:
            raise AttributeError
        v = self.__dict__[attr_name] = getter_fun(self)
        return v

    def _get_k(self):
        return self.keyOf(self.f)

    def _get_name(self):
        return self.f.name

    def keyOf(self, f):
        m = hashlib.sha256()
        buf = bytearray(4096)
        pos = f.seek(0, 1)
        f.seek(0)
        n = f.readinto(buf)
        while n == len(buf):
            m.update(buf)
            n = f.readinto(buf)
        m.update(buf[:n])
        f.seek(pos)
        return base64.urlsafe_b64encode(m.digest())


class Index(dict):
    pass

class Volume:
    def __init__(self, arfile):
        self.arfile = arfile

    def append(self, k, f):
        buf = bytearray(4096)
        arf = self.arfile
        start = arf.seek(0,2)
        length = 0
        n = f.readinto(buf)
        while n == len(buf):
            arf.write(buf)
            length += n
        arf.write(buf[:n])
        length += n
        return start, length

    def flush(self):
        self.arfile.flush()


class KeyValueAppendOnly:       # Abstract
    def include(self, key, f):
        # Make file f be included in store
        raise NotImplementedError

    def get(self, key):
        # Return a file from key
        raise NotImplementedError

    def has(self, key):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class KVAOUsingDict(KeyValueAppendOnly):
    def __init__(self):
        self.d = dict()

    def include(self, key, f):
        # Make f included in store
        if key not in self.d:
            self.d[key] = f.read()

    def get(self, key):
        # Return a file from key
        return io.BytesIO(self.d[key])

    def has(self, key):
        return key in self.d

    def __len__(self):
        return len(self.d)


class KVAOUsingFile(KeyValueAppendOnly):
    def __init__(self, arfile):
        self.arfile = arfile
        self.ix = Index()       # FIXME: s/b in file somehow
        self.vol = Volume(arfile)

    def include(self, key, f):
        # Make f included in store
        if key in self.ix:
            return
        start, length = self.vol.append(key, f)
        self.ix[key] = start, length

    def get(self, key):
        # Return a file from key
        raise NotImplementedError

    def has(self, key):
        return key in self.ix

    def __len__(self):
        return len(self.ix)


class Archive:
    def include(self, f):
        # Make f included in store
        raise NotImplementedError

    def get(self, name):
        # Return a file from name
        raise NotImplementedError

    def has(self, name):
        raise NotImplementedError


class ArchiveUsing(Archive):
    def __init__(self):
        self.name2key = defaultdict(list)
        self.key2names = defaultdict(set)

    def include(self, f):
        # Make f included in archive
        ffa = ArF(f)
        k = ffa.k
        self.kvao.include(k, f)
        self.name2key[ffa.name].append(k)
        self.key2names[k].add(ffa.name)

    def get(self, name):
        # Return a file from name
        k = self.name2key[name][-1] # the last one added
        return self.kvao.get(k)

    def has(self, name):
        if name not in self.name2key:
            return False
        k = self.name2key[name][-1] # the last one added
        return self.kvao.has(k)


class ArchiveUsingDict(ArchiveUsing):
    def __init__(self):
        self.kvao = KVAOUsingDict()
        super().__init__()


class ArchiveUsingFile(ArchiveUsing):
    def __init__(self, arfile):
        self.arfile = arfile
        #self.kvao = KVAOUsingDict() # Testing
        self.kvao = KVAOUsingFile(arfile) # Testing
        super().__init__()


def foo(f):
    ffa = ArF(f)
    a.include(ffa)

def bar(name):
    a.get(name)
