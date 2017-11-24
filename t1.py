# Archive file system of sorts
# just sketching - tas


import base64
import hashlib

class ArF:
    def __init__(self, f):
        self.f = f

    def __getattr__(self, k):
        if 'k' in self.__dict__:
            return self.k
        self.k = self.keyOf(self.f)
        return self.k

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


class Archive:
    def __init__(self, arfile):
        self.arfile = arfile
        self.ix = Index()
        self.vol = Volume(arfile)

    def include(self, f):
        # Make f included in archive
        ffa = ArF(f)
        k = ffa.k
        if k in self.ix:
            return
        start, length = self.vol.append(k, f)
        self.ix[k] = start, length

    def get(self, name):
        # Return a file from name
        raise NotImplementedError

    def has(self, name):
        # Is name in archive?
        raise NotImplementedError


def foo(f):
    ffa = ArF(f)
    a.include(ffa)

def bar(name):
    a.get(name)
