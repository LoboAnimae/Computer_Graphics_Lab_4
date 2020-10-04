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

    def load(self, filename, translate, scale):
        model = Obj(filename)

        light = V3(0, 0, 1)

        for face in model.f:
            vcount = len(face)

            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = V3(model.v[f1][0],
                        model.v[f1][1], model.v[f1][2])
                v2 = V3(model.v[f2][0],
                        model.v[f2][1], model.v[f2][2])
                v3 = V3(model.v[f3][0],
                        model.v[f3][1], model.v[f3][2])

                x1 = round((v1.x * scale.x) + translate.x)
                y1 = round((v1.y * scale.y) + translate.y)
                z1 = round((v1.z * scale.z) + translate.z)

                x2 = round((v2.x * scale.x) + translate.x)
                y2 = round((v2.y * scale.y) + translate.y)
                z2 = round((v2.z * scale.z) + translate.z)

                x3 = round((v3.x * scale.x) + translate.x)
                y3 = round((v3.y * scale.y) + translate.y)
                z3 = round((v3.z * scale.z) + translate.z)

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)

                normal = cross(sub(B, A), sub(C, A))
                intensity = dot(norm(normal), light)
                grey = round(255 * intensity)
                if grey < 0:
                    continue

                intensityColor = color(grey, grey, grey)
                self.drawtriangle(A, B, C, intensityColor)

            else:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                v1 = V3(model.vertices[f1][0],
                        model.vertices[f1][1], model.vertices[f1][2])
                v2 = V3(model.vertices[f2][0],
                        model.vertices[f2][1], model.vertices[f2][2])
                v3 = V3(model.vertices[f3][0],
                        model.vertices[f3][1], model.vertices[f3][2])
                v4 = V3(model.vertices[f4][0],
                        model.vertices[f4][1], model.vertices[f4][2])

                x1 = round((v1.x * scale.x) + translate.x)
                y1 = round((v1.y * scale.y) + translate.y)
                z1 = round((v1.z * scale.z) + translate.z)

                x2 = round((v2.x * scale.x) + translate.x)
                y2 = round((v2.y * scale.y) + translate.y)
                z2 = round((v2.z * scale.z) + translate.z)

                x3 = round((v3.x * scale.x) + translate.x)
                y3 = round((v3.y * scale.y) + translate.y)
                z3 = round((v3.z * scale.z) + translate.z)

                x4 = round((v4.x * scale.x) + translate.x)
                y4 = round((v4.y * scale.y) + translate.y)
                z4 = round((v4.z * scale.z) + translate.z)

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)
                D = V3(x4, y4, z4)

                normal = cross(sub(B, A), sub(C, A))
                intensity = dot(norm(normal), light)
                grey = round(intensity * 255)
                if grey < 0:
                    continue
                intensityColor = color(grey, grey, grey)

                self.drawtriangle(A, B, C, intensityColor)

                self.drawtriangle(A, D, C, intensityColor)
        self.write()
