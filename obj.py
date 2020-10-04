class Obj(object):
    def __init__(self, ofile):
        with open(ofile) as f:
            self.ls = f.read().splitlines()

        self.v = []
        self.f = []
        self.load()

    def load(self):
        for l in self.ls:
            if l:
                p, val = l.split(' ', 1)

                if p == 'v':
                    self.v.append(list(map(float, val.split(' '))))

                elif p == 'f':
                    self.f.append([list(map(int, sector.split('/')))
                                   for sector in val.split(' ')])
