#_20231106

import pygame
import pygame.locals
import time

class sgpg:
    #
    def __init__(self) -> None:
        pygame.init()
        if pygame.joystick.get_count() >= 1:
            self.js = pygame.joystick.Joystick(0)
            self.jstickinfo = {"axis": [0.0] * self.js.get_numaxes(), "button": [0] * self.js.get_numbuttons(), "hat": [0] * self.js.get_numhats()}
            print("Joystick Initialized: ", self.jstickinfo)
        else:
            self.js = None
        self.xpos = [0] * 8
        self.ypos = [0] * 8
        self.fontsize = 16
        self.fontobject = pygame.font.SysFont(None, self.fontsize)
        self.colorv = [0, 0, 0, 255]
        self.xalign = 0
        self.eventclbk = dict()
        self.pginfo = {
            "sx": 0,
            "sy": 0,
            "dispx": pygame.display.Info().current_w,
            "dispy": pygame.display.Info().current_h,
            "act": 0
        }
        self.curw = 0
        self.surface: list[pygame.SurfaceType|None] = [None] * 8
        self.fontfamily = None
        self.drawlasttime = time.time_ns() // 1000000 

        self.objsize = [80, 24]

        #stick命令用。
        self.stickv = {
            "left" : 0,
            "up": 0,
            "right": 0,
            "down": 0,
            "space": 0,
            "ctrl": 0,
            "z": 0,
            "x": 0,
            "c": 0,
            "shift": 0,
        }

        self.logmesonscreen = 0
        self.logmes_ypos = 0
        self.pushedkeylist = dict()
        self.debug_uncaught_events = 0
    def version(self) -> float:
        return 0.1
    #
    def screen(self, screen_id: int, xsize: int, ysize: int, window_mode: int = 0) -> int:
        if screen_id != 0:
            return 1
        option = 0
        if (window_mode & 32) == 32:
            option += pygame.DOUBLEBUF + pygame.RESIZABLE
        if (window_mode & 64) == 64:
            option += pygame.FULLSCREEN
        self.surface[0] = pygame.display.set_mode((xsize,ysize), option)
        self.surface[0].fill([255,255,255])
        self.pginfo["sx"] = self.surface[0].get_width()
        self.pginfo["sy"] = self.surface[0].get_height()
        self.xshift = 0
        self.yshift = 0
        return 0
    #
    def ginfo(self, key: str) -> int|str|None:
        if key in self.pginfo:
            self.pginfo["cx"] = self.xpos[self.curw]
            self.pginfo["cy"] = self.ypos[self.curw]
            return self.pginfo[key]
        else:
            return None
    #
    def logmes(self, text: str, errorlevel: int = 0) -> None:
        for tline in str(text).splitlines():
            print(tline)
            if self.surface[0] != None and self.logmesonscreen != 0:
                if errorlevel == 2:
                    c = [255, 0, 0]
                elif errorlevel == 1:
                    c = [224, 152, 0]
                else:
                    c = [64, 64, 64]
                t = pygame.font.SysFont("monospace", 13).render(tline, False, c)
                pygame.draw.rect(self.surface[0], [255, 255, 255], (0, self.logmes_ypos, t.get_width(), t.get_height()), 0)
                self.surface[0].blit(t, (0, self.logmes_ypos))
                self.logmes_ypos = (self.logmes_ypos + t.get_height()) % self.surface[0].get_height()
                self.redraw_now()
    #
    def cls(self, cls_mode: int = 0) -> None:
        self.clear()
        self.logmes_ypos = 0
    #
    def pos_shift(self, xshift: int|float = 0, yshift: int|float = 0) -> None:
        self.xpos[self.curw] += int(xshift)
        self.ypos[self.curw] += int(yshift)
    #
    def pos_shiftf(self, xshift: int|float = 0, yshift: int|float = 0) -> None:
        self.xpos[self.curw] += int(self.surface[self.curw].get_width() * xshift) 
        self.ypos[self.curw] += int(self.surface[self.curw].get_height() * yshift) 
    #
    def pos(self, xposition: int|float, yposition: int|float) -> None:
        self.xpos[self.curw] = int(xposition)
        self.ypos[self.curw] = int(yposition)
    #
    def posf(self, xposition: float, yposition: float) -> None:
        self.xpos[self.curw] = int(self.surface[self.curw].get_width() * xposition) 
        self.ypos[self.curw] = int(self.surface[self.curw].get_height() * yposition) 
    #
    def font(self, font_name: str = "", font_size: str = 16) -> None:
        self.fontfamily = font_name
        self.fontsize = font_size
        if font_name == "":
            self.fontobject = pygame.font.SysFont(None, self.fontsize)
        else:
            self.fontobject = pygame.font.Font(self.fontfamily, self.fontsize)
    #
    def text(self, message: object, noreturn_flag: int = 0) -> None:
        for tline in str(message).splitlines():
            t = self.fontobject.render(tline, True, self.colorv)
            #pygame.draw.rect(self.surface, [255,192,192], (self.xpos, self.ypos, t.get_width(), t.get_height()), 0)
            if self.xalign == 0:
                #LEFT
                self.surface[self.curw].blit(t, (self.xpos[self.curw], self.ypos[self.curw]))
            elif self.xalign == 1:
                #CENTER
                self.surface[self.curw].blit(t, (self.xpos[self.curw] - t.get_width() / 2, self.ypos[self.curw] - t.get_height() / 2))
            if noreturn_flag == 0:
                self.ypos[self.curw] += t.get_height()
            elif noreturn_flag == 1:
                self.xpos[self.curw] += t.get_width()
            elif noreturn_flag == 2:
                pass
    #
    def align(self, alignment_value: str = "left") -> None:
        for av in alignment_value.split():
            if av == "left":
                self.xalign = 0
            elif av == "center":
                self.xalign = 1
    #
    def color(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        self.colorv = [red, green, blue, alpha]
    def rgbcolor(self, rgb: int, alpha: int = 255) -> None:
        self.colorv = [rgb // 65536, rgb % 65536 // 256, rgb % 256, alpha]
    #
    def line(self, x1: int|float, y1: int|float, x2: int|float, y2: int|float, line_width: int = 1) -> None:
        pygame.draw.line(self.surface[self.curw], self.colorv, (x1, y1), (x2, y2), line_width)
    #
    def box(self, x1: int|float, y1: int|float, x2: int|float, y2: int|float, boxline_width: int = 1, round_corner: int = 0) -> None:
        pygame.draw.rect(self.surface[self.curw], self.colorv, (x1, y1, x2 - x1, y2 - y1), boxline_width, round_corner)
    #
    def clear(self) -> None:
        pygame.draw.rect(self.surface[self.curw], (255, 255, 255), (0, 0, self.surface[self.curw].get_width(), self.surface[self.curw].get_height()))
    #
    def fill(self, x1: int|float = None, y1: int|float = None, x2: int|float = None, y2: int|float = None, round_corner: int = 0) -> None:
        if x1 == y1 == x2 == y2 == None:
            #boxf:
            self.box(0, 0, self.surface[self.curw].get_width(), self.surface[self.curw].get_height(), 0, round_corner)
        else:
            self.box(x1, y1, x2, y2, 0)
    #
    def neweventhandler(self, event_name: str, function_pointer: callable) -> None:
        self.eventclbk[event_name] = function_pointer
    #
    def stop(self) -> None:
        game_close = 0
        pygame.display.flip()
        pygame.time.set_timer(25, 16)
        while game_close == 0:
            pygame.event.pump()
            for event in [pygame.event.wait()]:
                # ALT + F4
                if event.type == pygame.locals.QUIT:
                    game_close = 1
                # マウスボタンが押された
                elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                    self._proc_pg_mousebuttondown(event)
                # マウスボタンが離された
                elif event.type == pygame.locals.MOUSEBUTTONUP:
                    self._proc_pg_mousebuttonup(event)
                elif event.type == pygame.locals.MOUSEMOTION:
                    self._proc_pg_mousemotion(event)
                # キーが押された
                elif event.type == pygame.locals.KEYDOWN:
                    self._proc_pg_keydown(event)
                # キーが離された
                elif event.type == pygame.locals.KEYUP:
                    self._proc_pg_keyup(event)
                # ウィンドウサイズ変更
                elif event.type == pygame.locals.WINDOWRESIZED:
                    self._proc_pg_windowresized(event)
                # ウィンドウのアクティブ化・非アクティブ化
                elif event.type == pygame.locals.ACTIVEEVENT:
                    self._proc_pg_activeevent(event)
                # ジョイスティックの軸値の変更
                elif event.type == pygame.JOYAXISMOTION:
                    if abs(self.jstickinfo["axis"][event.axis] - event.value) >= 0.1:
                        self.jstickinfo["axis"][event.axis] = event.value
                        print(event.axis, event.value)
                elif event.type == pygame.JOYBUTTONDOWN:
                    print(event)
                elif event.type == pygame.JOYBUTTONUP:
                    print(event)
                elif event.type == pygame.JOYHATMOTION:
                    print(event)
                #テキスト入力関連
                elif event.type == pygame.TEXTINPUT:
                    print(event)
                    if self.eventclbk.get("PG_TEXTINPUT") != None:
                        self.eventclbk["PG_TEXTINPUT"](event.text)
                elif event.type == pygame.TEXTEDITING:
                    print(event)
                    if self.eventclbk.get("PG_TEXTEDITING") != None:
                        self.eventclbk["PG_TEXTEDITING"](event.text)
                # フレーム(ユーザーイベント)
                elif event.type == 25:
                    if self.eventclbk.get("PG_FRAME") != None:
                        self.eventclbk["PG_FRAME"]()
                    pygame.display.flip()
                # その他(ハンドルされていないイベント)
                else:
                    if self.debug_uncaught_events != 0:
                        print(event)
            # 1 time for every frame loop
            for pkk in self.pushedkeylist.keys():
                if time.time_ns() // 1000000 - self.pushedkeylist[pkk]["holdtime"] >= 450:
                    if (time.time_ns() // 1000000 - self.pushedkeylist[pkk]["holdtime"]) // 75 > self.pushedkeylist[pkk]["holdcounter"]:
                        self.pushedkeylist[pkk]["holdcounter"] = (time.time_ns() // 1000000 - self.pushedkeylist[pkk]["holdtime"]) // 75
                        if "PG_CHAR" in self.eventclbk:
                            self.eventclbk["PG_CHAR"](self.pushedkeylist[pkk]["unicode"], pkk)
            if self.eventclbk.get("PG_TICK") != None:
                self.eventclbk["PG_TICK"]()
    #
    def _proc_pg_mousebuttondown(self, event):
        if event.button == 1:
            #LEFT
            if self.eventclbk.get("PG_MBUTTONDOWN") != None:
                self.eventclbk["PG_MBUTTONDOWN"](event.pos[0], event.pos[1])
    #
    def _proc_pg_mousebuttonup(self, event):
        pass
    #
    def _proc_pg_mousemotion(self, event):
        pass
    #
    def _proc_pg_keydown(self, event):
        if event.dict["scancode"] in self.pushedkeylist.keys():
            self.pushedkeylist[event.dict["scancode"]]["holdtime"] = time.time_ns() // 1000000
            self.pushedkeylist[event.dict["scancode"]]["holdcounter"] = 6
        else:
            self.pushedkeylist[event.dict["scancode"]] = dict()
            self.pushedkeylist[event.dict["scancode"]]["unicode"] = event.dict["unicode"]
            self.pushedkeylist[event.dict["scancode"]]["holdtime"] = time.time_ns() // 1000000
            self.pushedkeylist[event.dict["scancode"]]["holdcounter"] = 6
        if self.eventclbk.get("PG_CHAR") != None:
            self.eventclbk["PG_CHAR"](self.pushedkeylist[event.dict["scancode"]]["unicode"], event.dict["scancode"])
        if self.eventclbk.get("PG_KEYDOWN") != None:
            self.eventclbk["PG_KEYDOWN"](self.pushedkeylist[event.dict["scancode"]]["unicode"], event.dict["scancode"])
    #
    def _proc_pg_keyup(self, event):
        if event.dict["scancode"] in self.pushedkeylist.keys():
            self.pushedkeylist.pop(event.dict["scancode"])
        else:
            pass
    #
    def _proc_pg_windowresized(self, event):
        self.pginfo["sx"] = self.surface[0].get_width()
        self.pginfo["sy"] = self.surface[0].get_height()
        if self.eventclbk.get("PG_WINDOWRESIZED") != None:
            self.eventclbk["PG_WINDOWRESIZED"](self.surface[0].get_width(), self.surface[0].get_height())
    #
    def _proc_pg_activeevent(self, event):
        if (event.state, event.gain) == (2, 1):
            self.pginfo["act"] = 0
        elif (event.state, event.gain) == (2, 0):
            self.pushedkeylist = dict()
            self.pginfo["act"] = -1
        #
        if self.eventclbk.get("PG_ACTIVE") != None:
            self.eventclbk["PG_ACTIVE"](self.pginfo["act"])
    #
    def title(self, title_text: str = "") -> None:
        pygame.display.set_caption(title_text)
        pass
    #
    def redraw_now(self) -> None:
        pygame.display.flip()
    #
    def mouse(self, x: int|float|None = None, y: int|float|None = None) -> None:
        if x == None and y == None:
            pygame.mouse.set_visible(True)
        elif x < 0 or y < 0:
            pygame.mouse.set_visible(False)
    #
    def end(self):
        pygame.quit()

