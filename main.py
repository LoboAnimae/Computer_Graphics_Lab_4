from renderer import *
from obj import Obj
from datamods import *
from linalg import *
from collections import namedtuple

V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])


r = Render(width=500, height=500, ofile='output.bmp')
r.load('E_HH.obj', V3(260, 200, 1), V3(200, 200, 200))
