'''
TODO ESTA FILE ESTÁ DISEÑADA A PARTIR DE LO QUE HIZO DENNIS EN CLASE.
PARTES PUEDEN (Y VAN A) PARECERSE POR ESTO.

Andrés Quan-Littow
17652
'''


from obj import Obj
from datamods import *
from linalg import *
from collections import namedtuple

V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])


class Render(object):
    def __init__(self, width=1000, height=1000, ofile='out.bmp'):
        self.framebuffer = []
        self.zbuffer = []
        self.ofile = ofile
        self.createFrame(width, height)
        self.clear()

    def clear(self, r=0, g=0, b=0):
        self.framebuffer = [
            [color(r, g, b) for x in range(self.width)]
            for y in range(self.height)
        ]

        self.zbuffer = [
            [-float('inf') for x in range(self.width)]
            for y in range(self.height)
        ]

    def setColor(self, r, g, b):
        r = 0 if r < 0 else r
        g = 0 if g < 0 else g
        b = 0 if b < 0 else b

        r = 255 if r > 255 else r
        g = 255 if g > 255 else g
        b = 255 if b > 255 else b
        self.clear(r, g, b)

    def color(self, r, g, b):
        r = round(r*255)
        g = round(g*255)
        b = round(b*255)
        return color(r, g, b)

    def createFrame(self, width=1000, height=1000):
        self.width = width
        self.height = height

    def viewPort(self, x, y, width, height):
        self.viewPortWidth = width
        self.viewPortHeight = height
        self.xViewPort = x
        self.yViewPort = y

    def setVertex(self, x, y):
        calcX = round((x+1)*(self.viewPortWidth/2)+self.xViewPort)
        calcY = round((y+1)*(self.viewPortHeight/2)+self.yViewPort)
        self.setpoint(calcX, calcY)

    def write(self, ):
        f = open(self.ofile, 'bw')
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        for x in range(self.width):
            for y in range(self.height):
                f.write(self.framebuffer[y][x])

        f.close()

    def setpoint(self, x, y, mycolor=None):
        try:
            self.framebuffer[x][y] = mycolor
        except:
            pass

    def drawline(self, x_beg, y_beg, x_end, y_end):
        dy = abs(y_end - y_beg)
        dx = abs(x_end - x_beg)
        st = dy > dx

        if st:
            x_beg, y_beg = y_beg, x_beg
            x_end, y_end = y_end, x_end

        if x_beg > x_end:
            x_beg, x_end = x_end, x_beg
            y_beg, y_end = y_end, y_beg

        dy = abs(y_end - y_beg)
        dx = abs(x_end - x_beg)

        of = 0
        th = dx

        y = y_beg
        for x in range(x_beg, x_end):
            if st:
                self.setpoint(y, x)
            else:
                self.setpoint(x, y)

            of += dy * 2
            if of >= th:
                y += 1 if y_beg < y_end else -1
                th += dx * 2

    def drawtriangle(self, A, B, C, selectColor):
        xMin, xMax, yMin, yMax = bbox(A, B, C)
        for x in range(xMin, xMax + 1):
            for y in range(yMin, yMax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue

                z = A.z * w + B.z * u + C.z * v

                try:
                    if z > self.zbuffer[x][y]:
                        self.setpoint(x, y, selectColor)
                        self.zbuffer[x][y] = z
                except:
                    pass

    def load(self, ofile, trans, size):
        model = Obj(ofile)

        ilum = V3(0, 0, 1)

        for fc in model.f:
            vcount = len(fc)

            if vcount == 3:
                fc1 = fc[0][0] - 1
                fc2 = fc[1][0] - 1
                fc3 = fc[2][0] - 1

                vt1 = V3(model.v[fc1][0],
                         model.v[fc1][1], model.v[fc1][2])
                vt2 = V3(model.v[fc2][0],
                         model.v[fc2][1], model.v[fc2][2])
                vt3 = V3(model.v[fc3][0],
                         model.v[fc3][1], model.v[fc3][2])

                a1 = round((vt1.x * size.x) + trans.x)
                b1 = round((vt1.y * size.y) + trans.y)
                c1 = round((vt1.z * size.z) + trans.z)

                a2 = round((vt2.x * size.x) + trans.x)
                b2 = round((vt2.y * size.y) + trans.y)
                c2 = round((vt2.z * size.z) + trans.z)

                a3 = round((vt3.x * size.x) + trans.x)
                b3 = round((vt3.y * size.y) + trans.y)
                c3 = round((vt3.z * size.z) + trans.z)

                vx1 = V3(a1, b1, c1)
                vx2 = V3(a2, b2, c2)
                vx3 = V3(a3, b3, c3)

                normvar = cross(sub(vx2, vx1), sub(vx3, vx1))
                ints = dot(norm(normvar), ilum)
                grays = round(255 * ints)
                if grays < 0:
                    continue

                intensityColor = color(grays, grays, grays)
                self.drawtriangle(vx1, vx2, vx3, intensityColor)

            else:
                fc1 = fc[0][0] - 1
                fc2 = fc[1][0] - 1
                fc3 = fc[2][0] - 1
                fc4 = fc[3][0] - 1

                vt1 = V3(model.vertices[fc1][0],
                         model.vertices[fc1][1], model.vertices[fc1][2])
                vt2 = V3(model.vertices[fc2][0],
                         model.vertices[fc2][1], model.vertices[fc2][2])
                vt3 = V3(model.vertices[fc3][0],
                         model.vertices[fc3][1], model.vertices[fc3][2])
                vt4 = V3(model.vertices[fc4][0],
                         model.vertices[fc4][1], model.vertices[fc4][2])

                a1 = round((vt1.x * size.x) + trans.x)
                b1 = round((vt1.y * size.y) + trans.y)
                c1 = round((vt1.z * size.z) + trans.z)

                a2 = round((vt2.x * size.x) + trans.x)
                b2 = round((vt2.y * size.y) + trans.y)
                c2 = round((vt2.z * size.z) + trans.z)

                a3 = round((vt3.x * size.x) + trans.x)
                b3 = round((vt3.y * size.y) + trans.y)
                c3 = round((vt3.z * size.z) + trans.z)

                a4 = round((vt4.x * size.x) + trans.x)
                b4 = round((vt4.y * size.y) + trans.y)
                c4 = round((vt4.z * size.z) + trans.z)

                vx1 = V3(a1, b1, c1)
                vx2 = V3(a2, b2, c2)
                vx3 = V3(a3, b3, c3)
                D = V3(a4, b4, c4)

                normvar = cross(sub(vx2, vx1), sub(vx3, vx1))
                ints = dot(norm(normvar), ilum)
                grays = round(ints * 255)
                if grays < 0:
                    continue
                intensityColor = color(grays, grays, grays)

                self.drawtriangle(vx1, vx2, vx3, intensityColor)

                self.drawtriangle(vx1, D, vx3, intensityColor)
        self.write()
