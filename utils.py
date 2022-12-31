import math
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Rectangle
from kivy.vector import Vector


class CanvasText():
    def __init__(self, *args, **kwargs):
        self.pos = Vector(*kwargs.get('pos',(0,0)))
        self.scale = Vector(*kwargs.get('scale',(1,1)))
        self.label = CoreLabel(text=kwargs.get('text'),font_size=kwargs.get('font_size'), color=(0, 0, 0, 1))
        self.label.refresh()
        self.size = Vector(*self.label.texture.size)
    def draw(self,  size):
        return Rectangle(pos=self.pos, size=(size.x,size.y), texture=self.label.texture)

def convertToRad(deg):
    return (deg*math.pi)/180

def convertCart(val, rad=False):
    if not rad:
        rad = convertToRad(val)
    y = math.sin(val)
    x = math.cos(val)
    return (x,y)

def tickToCart(num):
    ## NOTE: 60 tick equal t0 360 deg
    val = (num * ((-2*math.pi)/60)) + (math.pi/2)
    return val

def getHeight(ang,x,rad=True):
    if not rad:
        ang = convertToRad(ang)
    return math.atan(ang)*x
