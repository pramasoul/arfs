# Archive file system of sorts
# just sketching - tas


class Index:
    def __init__(self):
        self.index = dict()

    def has(self, name):
        return name in self.index

    def lookup(self, name):
        return self.index[name]

    def record(self, name, value):
        self.index[name] = value



class Archive:
    def __init__(self, arfile):
        self.arfile = arfile

    def include(self, f):
        # Make f included in archive
        raise NotImplementedError

    def get(self, name):
        # Return a file from name
        raise NotImplementedError

    def has(self, name):
        # Is name in archive?
        raise NotImplementedError

