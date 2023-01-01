from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '330')
Config.set('graphics', 'height', '800')
import kivy
from kivy.app import App
import math
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import (ObjectProperty, NumericProperty, ListProperty, StringProperty)
from kivy.core.text import Label as CoreLabel
from time import time, localtime
from kivy.clock import Clock as Timer
from kivy.uix.popup import Popup
from kivy.graphics import *
# from kivy.graphics.context_instructions import (Transform)
from kivy.vector import Vector
from utils import *


class AnchorableButton(AnchorLayout):
    customizing = ObjectProperty()
    text = StringProperty()
    callback = ObjectProperty()
    settingsMain = ObjectProperty()
    # showSettings = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def showSettings(self, *args, **kwargs):
        self.settingsMain.showColorPicker(callback=self.callback)

class CustomizableListPopUp(Popup):
    customizing = ObjectProperty()# TODO: change to customizables
    buttonsgrid = ObjectProperty()
    settingsMain = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_customizing(self, *args, **kwargs):
        if self.buttonsgrid:
            self.buttonsgrid.clear_widgets()
            for key in self.customizing:
                self.buttonsgrid.add_widget(AnchorableButton(text=key, callback=self.customizing[key], settingsMain=self.settingsMain))

    def save(self, *args, **kwargs):
        self.dismiss()
        pass
class ColorPickerModal(Popup):
    dismissColor = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def save(self, *args, **kwargs):
        self.dismissColor(obj=self)
        super().dismiss()

    def dismiss(self, *args, **kwargs):
        self.dismissColor()
        super().dismiss()

class CustomizeFloatLayout(FloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clr_popup = ColorPickerModal(dismissColor=self.dismisColorPicker)
        self.popup_main = CustomizableListPopUp(settingsMain=self)

    def showColorPicker(self, *args, **kwargs):
        self.popup_main.dismiss()
        self.clr_popup.callback = kwargs.get('callback')
        self.clr_popup.open()

    def dismisColorPicker(self,*args, **kwargs):
        colrwhl = kwargs.get('obj')
        if colrwhl:
            self.clr_popup.callback(colrwhl.clrpckr.color)
        self.popup_main.open()
        pass


    def openPopUp(self, *args, **kwargs):
        def setAttr(obj, attr):
            def changeAttrVal(val):
                setattr(obj, attr, val)
            return changeAttrVal
        self.popup_main.customizing = {
            'Pendulum': setAttr(self.pendulum,'pendulumcolor'),
            'Wood': setAttr(self.clockcase, "woodcolor"),
            'Sides':setAttr(self.clockcase, "woodbordercolor"),
            'Clock': setAttr(self.clock, "clockcolor"),
            "Digital Background": setAttr(self.pendulum, "digitalBackgroundColor"),
            'Clock Frame Border': setAttr(self.clock, "clockframebordercolor"),

        }
        self.popup_main.open()
        pass


class ClockCase(FloatLayout):
    clockSize = ListProperty([50,50])
    woodbordercolor = ListProperty([0.8,0.3,0.1])
    woodcolor = ListProperty([1,0.5,0.2])
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass


class Pendulum(AnchorLayout):
    ANGLE = NumericProperty((math.pi)+(math.pi/3))
    ANGLEVEL = NumericProperty(math.pi/180)
    INTERVAL = ListProperty([(math.pi)+(math.pi/3), (2*math.pi)-(math.pi/3)])
    PENDULUMRAD = NumericProperty(0.3)
    pendulumcolor = ListProperty([1,0,0])
    clockcase = ObjectProperty()
    digitalBackgroundColor = ListProperty([0,0,0])
    clock = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind(size=self.draw)
        self.timer = Timer.schedule_interval(self.update, 0.01)
    def update(self, *args, **kwargs):
        if self.ANGLE > self.INTERVAL[1]:
            self.ANGLEVEL *=-1
        elif self.ANGLE < self.INTERVAL[0]:
            self.ANGLEVEL *=-1
        self.ANGLE += self.ANGLEVEL

    def on_ANGLE(self, *args, **kwargs):
        self.draw()
    def drawPendulum(self, cnv_center, cnv_size):
        x,y = convertCart(self.ANGLE, rad=True)
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y)
        sc = Scale(cnv_size.x/2.2)
        Color(1, 1, 1)
        Line(points=(0,1.1,x,y))
        Color(*self.pendulumcolor)
        # print(self.pendulumcolor)
        Ellipse(pos=(x-(self.PENDULUMRAD/2),y-(self.PENDULUMRAD/2)), size=(self.PENDULUMRAD, self.PENDULUMRAD))
        PopMatrix()

    def draw(self, *args, **kwargs):
        pos = Vector(*self.pos)
        cnv_center = pos + Vector(self.size[0]//2, self.size[1]//2)
        cnv_size = Vector(min(*self.size),min(*self.size))
        # cnv_size = Vector(min(*self.size),min(*self.size))
        self.canvas.before.clear()
        with self.canvas.before:
            self.drawPendulum(cnv_center,cnv_size)

class Clock(AnchorLayout):
    TIME = ObjectProperty({
        'SECOND': 50,
        'MINUTE': 5,
        'HOUR': 2
    })
    time = NumericProperty()
    TOTSEC = NumericProperty()
    clockwidth = ListProperty()
    clockframebordercolor = ListProperty([0,0,0])
    clockcolor = ListProperty([0.9,0.9,0.99])
    digital = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cnv_center = None
        self.cnv_size = None
        self.bind(size=self.drawOnResize)
        if not self.TOTSEC:
            t = localtime(time())
            tot_sec = (t.tm_hour*3600) + (t.tm_min*60) + t.tm_sec
            self.TOTSEC = tot_sec
        self.timer = Timer.schedule_interval(self.update, 1)

    def on_TOTSEC(self, *args, **kwargs):
        t_tot = self.TOTSEC
        self.TIME = {
            'SECOND': ((t_tot%3600)%60)%60,
            'MINUTE': (t_tot%3600)//60,
            'HOUR': t_tot//3600
        }
        self.draw()
    def on_clockcolor(self, *args, **kwargs):
        self.drawOnResize()
        pass
    def on_clockframebordercolor(self, *args, **kwargs):
        self.drawOnResize()
        pass
    def on_TIME(self, *args, **kwargs):
        if getattr(self,'digital'):
            self.digital.display.text = str(abs(self.TIME['HOUR']%12)).rjust(2,'0')+":"+str(self.TIME['MINUTE']).rjust(2,'0')+":"+str(self.TIME['SECOND']).rjust(2,'0')+str(' PM' if self.TIME['HOUR']>12 else " AM")
    def update(self, *args, **kwargs):
        self.TOTSEC += 1

    def drawOnResize(self,*args, **kwargs):
        pos = Vector(*self.pos)
        self.cnv_center = pos + Vector(self.size[0]//2, self.size[1]//2)
        self.cnv_size = Vector(min(*self.size),min(*self.size))
        self.clockwidth = [self.cnv_size.x,self.cnv_size.y]
        self.canvas.clear()
        with self.canvas:
            self.drawClock(self.cnv_center, self.cnv_size)
            self.drawTicks(self.cnv_center, self.cnv_size)
            self.drawNums(self.cnv_center, self.cnv_size)
            self.draw()
            # self.drawSecArm(cnv_center, cnv_size)
            # self.drawMinArm(cnv_center, cnv_size)
            # self.drawHrArm(cnv_center, cnv_size)

    def drawClock(self, cnv_center, cnv_size):
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y)
        sc = Scale(cnv_size.x/2)
        Color(*self.clockframebordercolor)
        Ellipse(pos=(-1.05,-1.05), size=(2.1,2.1))
        Color(*self.clockcolor)
        Ellipse(pos=(-1,-1), size=(2,2))
        PopMatrix()

    def drawTicks(self, cnv_center, cnv_size):
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y)
        sc = Scale((cnv_size.x/2)*0.9)
        for tick in range(1,61):
            rad = tickToCart(tick)
            x,y = convertCart(rad, rad=True)
            Color(0.5, 0.5, 0.5)
            Ellipse(pos=(x,y), size=(0.01,0.01))
        PopMatrix()

    def drawNums(self, cnv_center, cnv_size):
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y-10)
        # rot = Rotate(angle=-270, axis=(0,0,1))
        sc = Scale((cnv_size.x/2)*0.92)
        for hr in range(1,13):
            tick = hr*5
            rad = tickToCart(tick)
            x,y = convertCart(rad, rad=True)
            Color(0, 0, 0)
            m = CanvasText(pos=(x,y), font_size=50, text=str(hr))
            m.draw(m.size/cnv_size.x)
        PopMatrix()

    def drawSecArm(self, cnv_center, cnv_size):
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y-10)
        # rot = Rotate(angle=-270, axis=(0,0,1))
        sc = Scale((cnv_size.x/2)*0.85)
        tick = self.TIME['SECOND']
        rad = tickToCart(tick)
        x,y = convertCart(rad, rad=True)
        Color(0, 0, 0)
        Line(points=[0,0,x,y])
        PopMatrix()
        pass

    def drawMinArm(self, cnv_center, cnv_size):
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y-10)
        # rot = Rotate(angle=-270, axis=(0,0,1))
        sc = Scale((cnv_size.x/2)*0.75)
        tick = self.TIME['MINUTE']
        rad = tickToCart(tick)
        x,y = convertCart(rad, rad=True)
        Color(0, 0, 0)
        Line(points=[0,0,x,y],width=0.005)
        PopMatrix()
        pass

    def drawHrArm(self, cnv_center, cnv_size):
        PushMatrix()
        trans = Translate(cnv_center.x,cnv_center.y-10)
        # rot = Rotate(angle=-270, axis=(0,0,1))
        sc = Scale((cnv_size.x/2)*0.60)
        tick = self.TIME['HOUR']*5
        rad = tickToCart(tick)
        x,y = convertCart(rad, rad=True)
        Color(0, 0, 0)
        Line(points=[0,0,x,y],width=0.009)
        PopMatrix()
        pass

    def draw(self, *args, **kwargs):
        if not self.cnv_center and not self.cnv_size:
            return
        # pos = Vector(*self.pos)
        # cnv_center = pos + Vector(self.size[0]//2, self.size[1]//2)
        # cnv_size = Vector(min(*self.size),min(*self.size))
        # self.clockwidth = [cnv_size.x,cnv_size.y]
        self.canvas.after.clear()
        with self.canvas.after:
            # self.drawClock(cnv_center, cnv_size)
            # self.drawTicks(cnv_center, cnv_size)
            # self.drawNums(cnv_center, cnv_size)
            self.drawSecArm(self.cnv_center, self.cnv_size)
            self.drawMinArm(self.cnv_center, self.cnv_size)
            self.drawHrArm(self.cnv_center, self.cnv_size)

class ClockWindow(GridLayout):
    pass


class Main(App):
    def build(self):
        return ClockWindow()


if __name__ == '__main__':
    Main().run()
