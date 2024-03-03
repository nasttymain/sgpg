import sgpg
import time
import random

class appdata():
    def __init__(self) -> None:
        self.d = dict()

def gui_init():
#    g.screen(0, g.ginfo("dispx"), g.ginfo("dispy"), 64)
    g.screen(0, 800, 480, 32)

    g.pos(0, 0)
    g.text("LEFT UPPER CORNER")
    g.text("It's OK to auto-return")

    g.pos(40, 40)
    g.text("pixel-based positioning is also OK")

    g.pos(60, 40)
    g.font("", 32)
    g.text("Font Size Changed!",1)
    g.text(" and this text should be on same line as \"Font Size Changed!\"")

    g.font()
    g.color(255, 0, 0)
    g.box(70, 70, 100, 100, 4)
    g.color(0, 255, 0)
    g.fill(100, 70, 130, 100)

    g.title("Title Text")

    for i in range(10):
        g.rgbcolor(0x888888)
        g.posf(i / 10, 0.2)
        g.text(str(i) + " / 10")

        g.pos_shift(5, 30)
        g.text("POS_SHIFT")

        g.pos_shiftf(0.05, -0.1)
        g.text("POS_SHIFTF")

    g.color(0, 0, 255)
    g.align("center")
    g.posf(0.5, 0.5)
    g.text("This text should be on center!")

    g.color(192, 192, 192)
    g.fill(g.ginfo("sx") * 0.2, g.ginfo("sy") * 0.7, g.ginfo("sx") * 0.2 + 180, g.ginfo("sy") * 0.7 + 30)

    g.posf(0.2, 0.7)
    g.color(0, 0, 0)
    g.font("", 24)
    g.align("left")
    g.text("Press any key: " + str(a.d["pressedkey"]))

    g.neweventhandler("PG_MBUTTONDOWN", mbtn)
    g.neweventhandler("PG_KEYDOWN", kdn)
    g.neweventhandler("PG_KEYUP", kup)
    g.neweventhandler("PG_CHAR", char)
    g.neweventhandler("PG_FRAME", tick)

    g.debug_uncaught_events = 1


    g.stop(0)


def draw_imetest() -> None:
    g.color(192, 192, 192)
    g.fill(g.ginfo("sx") * 0.6, g.ginfo("sy") * 0.6, g.ginfo("sx") * 0.6 + 180, g.ginfo("sy") * 0.6 + 30)
    g.posf(0.6, 0.6)
    g.font("", 24)
    g.align("left")
    g.text("IMETEST: ")
    

def mbtn(mousex, mousey) -> None:
    g.pos(mousex, mousey)
    g.align("left")
    g.rgbcolor(0xFF00FF)
    g.font("", 24)
    g.text("^Clicked Here!")

def kdn(unicode, scancode) -> None:
    a.d["pressedkey"] = unicode
    g.color(192, 192, 192)
    g.fill(g.ginfo("sx") * 0.2, g.ginfo("sy") * 0.7, g.ginfo("sx") * 0.2 + 180, g.ginfo("sy") * 0.7 + 30)
    g.posf(0.2, 0.7)
    g.color(0, 0, 0)
    g.font("", 24)
    g.align("left")
    g.text("Press any key: " + str(a.d["pressedkey"]))
    print("KEYDOWN =>", unicode, scancode)

def kup(unicode, scancode) -> None:
    print(unicode, scancode)

def char(unicode, scancode) -> None:
    print("char =>", unicode, scancode)


def tick() -> None:
    g.pos(random.randint(0, 800), random.randint(0, 480))
    #g.text("Hello")
    g.pset(random.randint(0, 800), random.randint(0, 480))
    pass

if __name__ == "__main__":
    a = appdata()
    a.d["pressedkey"] = ""
    g = sgpg.sgpg()
    gui_init()