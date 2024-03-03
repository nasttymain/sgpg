#_20231106

import pygame
import pygame.locals
import time

class sgpg:
    """PygameのHSP-ishラッパー「sgpg」クラス
    
    PygameをHSPスタイルで取り扱うためのラッパークラスです
    Python 3.7以下では動作しません
    
    """
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
            "act": 0,
            "mesx": 0,
            "mesy": 0
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
        """SGPGのAPIバージョンを返す
        
        SGPGクラスのAPIバージョンを返します
        この値が異なるということは、既存のAPIの仕様に変更が加えられ、前バージョンまでと互換性が無いことを表します
        
        Args:
            なし
        
        Returns:
            float: バージョン番号
        
        """
        return 0.2
    #
    def screen(self, screen_id: int, xsize: int, ysize: int, window_mode: int = 0) -> int:
        """ウィンドウと描画領域を初期化する
        
        指定されたIDのウィンドウを、指定されたサイズ・モードで初期化し、使用できるようにします。
        
        Args:
            screen_id (int): ウィンドウID
                0: 表示されるウィンドウ。Pygameの制限により、ウィンドウID 0しか表示面として指定できません
            xsize (int): 初期化する画面サイズX
            ysize (int): 初期化する画面サイズY
            window_mode (int, optional): 初期化する画面モード
                0(規定): 通常のウィンドウ
                +32: サイズ可変ウィンドウ(最大化も可能になります)
                +64: フルスクリーンウィンドウ
        
        Returns:
            int: ステータス
                0: 成功
                1: 失敗
        
        """
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
        """画面関連情報を取得する
        
        画面に関連するPGINFO情報のうち、指定されたものを返します
        
        Args:
            key (str): 取得するタイプの名称
                "cx": カレントポジションのX座標
                "cy": カレントポジションのY座標
                "act": 現在アクティブなウィンドウID
                    0 - 7: それぞれ対応するウィンドウ
                    -1: どのウィンドウもアクティブになっていない。つまり、SGPGとは関係のないウィンドウがアクティブになっている
                "sx": 現在操作対象となっているウィンドウのXサイズ
                "sy": 現在操作対象となっているウィンドウのYサイズ
                "dispx": ディスプレイのXサイズ
                "dispy": ディスプレイのYサイズ
        
        Returns:
            int|str|None: 各PGINFO情報に対応する値

        """
        if key in self.pginfo:
            self.pginfo["cx"] = self.xpos[self.curw]
            self.pginfo["cy"] = self.ypos[self.curw]
            return self.pginfo[key]
        else:
            return None
    #
    def logmes(self, text: str, errorlevel: int = 0) -> None:
        """ログを表示する
        
        画面またはコマンドラインに、ログを表示します
        画面に表示するかどうかは、属性`sgpg.logmesonscreen`で切り替えできます
        
        Args:
            text (str): ログに記録するメッセージ
            errorlevel (int, optional): エラーレベル
                0(規定): 通常レベル。画面には黒色で表示されます
                1: 警告レベル。画面には黄色で表示されます
                2: 重大レベル。画面には赤色で表示されます
        
        Returns:
            なし
        
        """
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
        """画面上のすべての描画結果を消去する
        
        現在操作対象となっているウィンドウのすべての描画内容を消去し、1色で塗りつぶします。また、カレントポジションやカレントカラーを初期状態に戻します
        
        Args:
            cls_mode (int, optional): クリアするときの色(実装されていません)
                0(規定): 白色(#FFFFFF)
        
        Returns:
            なし
        
        """
        if not (0 <= cls_mode and cls_mode <= 4):
            raise ValueError
        self.clear()
        self.xpos[self.curw] = 0
        self.ypos[self.curw] = 0
        self.colorv = [0, 0, 0, 255]
        self.logmes_ypos = 0
    #
    def pos(self, xposition: int|float, yposition: int|float) -> None:
        """カレントポジションを変更する
        
        現在操作対象となっているウィンドウにおけるカレントポジションを変更します。カレントポジションとは、描画命令の起点となる座標値です
        X座標、Y座標を、左上を(0, 0)とするピクセル単位の値で指定します
        
        Args:
            xposition (int|float): カレントポジションのX座標
            yposition (int|float): カレントポジションのY座標
        
        Returns:
            なし
        
        """
        self.xpos[self.curw] = int(xposition)
        self.ypos[self.curw] = int(yposition)
    #
    def posf(self, xposition: float, yposition: float) -> None:
        """カレントポジションを変更する
        
        現在操作対象となっているウィンドウにおけるカレントポジションを変更します
        X座標、Y座標を、左上を(0.0, 0.0)、右下を(1.0, 1.0)で換算した実数値で指定します
        
        Args:
            xposition (float): カレントポジションのX座標
            yposition (float): カレントポジションのY座標
        
        Returns:
            なし
        
        """
        self.xpos[self.curw] = int(self.surface[self.curw].get_width() * xposition) 
        self.ypos[self.curw] = int(self.surface[self.curw].get_height() * yposition) 
    #
    def pos_shift(self, xshift: int|float = 0, yshift: int|float = 0) -> None:
        """カレントポジションを移動する
        
        現在操作対象となっているウィンドウにおけるカレントポジションを、現在の位置から指定だけ移動します
        正の値を指定すると{右|下}に、負の値を指定すると{左|上}に移動します
        
        Args:
            xposition (int|float, optional): カレントポジションのX移動量
            yposition (int|float, optional): カレントポジションのY移動量
        
        Returns:
            なし
        
        """
        self.xpos[self.curw] += int(xshift)
        self.ypos[self.curw] += int(yshift)
    #
    def pos_shiftf(self, xshift: int|float = 0, yshift: int|float = 0) -> None:
        """カレントポジションを移動する
        
        現在操作対象となっているウィンドウにおけるカレントポジションを、現在の位置から指定だけ移動します
        pos_shiftメソッドのposf版です
        
        Args:
            xposition (float, optional): カレントポジションのX移動量
            yposition (float, optional): カレントポジションのY移動量
        
        Returns:
            なし
        
        """
        self.xpos[self.curw] += int(self.surface[self.curw].get_width() * xshift) 
        self.ypos[self.curw] += int(self.surface[self.curw].get_height() * yshift) 
    #
    def font(self, font_name: str = "", font_size: int = 16) -> None:
        """フォントを設定する
        
        text命令で使用されるテキストのフォント設定を変更します
        
        Args:
            font_name (str): フォントファイル(TTFファイル)のファイル名
                ""(規定): 外部のTTFファイルを使わず、替わりにPygameのSysFontが使われます。このフォントを指定した場合は日本語を表示することができません
            font_size (int, optional): フォントの大きさ
        
        Returns:
            なし
        
        """
        self.fontfamily = font_name
        self.fontsize = font_size
        if font_name == "":
            self.fontobject = pygame.font.SysFont(None, self.fontsize)
        else:
            self.fontobject = pygame.font.Font(self.fontfamily, self.fontsize)
    #
    def text(self, message: object, noreturn_flag: int = 0) -> None:
        """画面にテキストを描画する
        
        現在操作対象となっている画面のカレントポジションにテキストを描画します
        
        Args:
            message (str):  表示するメッセージ、または変数
            noreturn_flag (int, optional): オプション
                0(規定): テキストの末尾に改行を挿入します。カレントポジションは、テキストの最終行の1行下に移動します
                +1: テキストの末尾で改行されません。替わりに、カレントポジションは、テキストの最終行の右側に移動します
        
        Returns:
            なし
        
        """
        if noreturn_flag not in [0, 1]:
            raise ValueError
        for tline in str(message).splitlines():
            t = self.fontobject.render(tline, True, self.colorv)
            self.pginfo["mesx"] = t.get_width()
            self.pginfo["mesy"] = t.get_height()
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
        """揃えモードを変更する
        
        text命令におけるテキストの、揃え方を変更します
        
        Args:
            alignment_value (str, optional): 揃えタイプの名称
                "left"(規定): 左右は左揃え、上下は上揃えで描画します
                "center": 左右・上下ともに中央揃えで描画します
        
        Returns:
            なし
        
        """
        if alignment_value not in ["center", "left"]:
            raise ValueError
        for av in alignment_value.split():
            if av == "left":
                self.xalign = 0
            elif av == "center":
                self.xalign = 1
    #
    def color(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        """カレントカラーを変更する
        
        描画命令で使用する色を変更します。各パラメータは0～255の間の整数値で指定します
        
        Args:
            red (int): 色コード(赤色の輝度)
            green (int): 色コード(緑色の輝度)
            blue (int): 色コード(青色の輝度)
            alpha (int, optional): 透明度
                255(規定): 完全に不透明になります
        
        Returns:
            なし
        
        """
        if not (0 <= red and red <= 255 and 0 <= green and green <= 255 and 0 <= blue and blue <= 255 and 0 <= alpha and alpha <= 255):
            raise ValueError
        self.colorv = [red, green, blue, alpha]
    def rgbcolor(self, rgb: int, alpha: int = 255) -> None:
        """カレントカラーを変更する
        
        描画命令で使用する色を変更します。カラーコードは、#RRGGBB形式の16進数表現で指定します
        
        Args:
            rgb (int): RGB形式 カラーコード値
            alpha (int, optional): 透明度
                255(規定): 完全に不透明になります
        
        Returns:
            なし
        
        """
        if not (0 <= rgb and rgb <= 16777215 and 0 <= alpha and alpha <= 255):
            raise ValueError
        self.colorv = [rgb // 65536, rgb % 65536 // 256, rgb % 256, alpha]
    #
    def pset(self, x: int|float, y: int|float) -> None:
        self.surface[self.curw].set_at((x, y), self.colorv)
    #
    def line(self, x1: int|float, y1: int|float, x2: int|float, y2: int|float, line_width: int = 1) -> None:
        """直線を描画する
        
        指定された2点を結ぶ直線を描画します
        
        Args:
            x1 (int|float): ラインの終点X座標
            y1 (int|float): ラインの終点Y座標
            x2 (int|float): ラインの始点X座標
            y2 (int|float): ラインの始点Y座標
            line_width (int, optional): ラインの太さ(ピクセル単位)
                1(規定): 1ピクセル幅で線を描画します
        
        Returns:
            なし
        
        """
        pygame.draw.line(self.surface[self.curw], self.colorv, (x1, y1), (x2, y2), line_width)
    #
    def box(self, x1: int|float, y1: int|float, x2: int|float, y2: int|float, boxline_width: int = 1, round_corner: int = 0) -> None:
        """矩形を描画する
        
        指定された2点をそれぞれ左上、右下の頂点に持つ、辺がウィンドウの枠と平行になる長方形を描画します
        
        Args:
            x1 (int|float):  矩形の左上X座標
            y1 (int|float):  矩形の左上Y座標
            x2 (int|float):  矩形の右下X座標
            y2 (int|float):  矩形の右下Y座標
            boxline_width (int, optional): 矩形の外枠の太さ
                1(規定): 1ピクセル幅で線を描画します
            round_corner (int, optional): 矩形の角丸の半径
                0(規定): 角丸処理を行わず、角のある長方形を描画します
        
        Returns:
            なし
        
        """
        pygame.draw.rect(self.surface[self.curw], self.colorv, (x1, y1, x2 - x1, y2 - y1), boxline_width, round_corner)
    #
    def clear(self) -> None:
        pygame.draw.rect(self.surface[self.curw], (255, 255, 255), (0, 0, self.surface[self.curw].get_width(), self.surface[self.curw].get_height()))
    #
    def fill(self, x1: int|float = None, y1: int|float = None, x2: int|float = None, y2: int|float = None, round_corner: int = 0) -> None:
        """塗りつぶし矩形を描画する
        
        指定された2点をそれぞれ左上、右下の頂点に持つ、辺がウィンドウの枠と平行になる長方形を描画して塗りつぶします
        
        Args:
            x1 (int|float):  矩形の左上X座標
            y1 (int|float):  矩形の左上Y座標
            x2 (int|float):  矩形の右下X座標
            y2 (int|float):  矩形の右下Y座標
            round_corner (int, optional): 矩形の角丸の半径
                0(規定): 角丸処理を行わず、角のある長方形を描画します
        
        Returns:
            なし
        
        """
        if x1 == y1 == x2 == y2 == None:
            #boxf:
            self.box(0, 0, self.surface[self.curw].get_width(), self.surface[self.curw].get_height(), 0, round_corner)
        else:
            self.box(x1, y1, x2, y2, 0)
    #
    def neweventhandler(self, event_name: str, function_pointer: callable) -> None:
        """イベントハンドラを設定する
        
        あるイベントに対するイベントコールバックを設定します
        イベント処理は、stop命令のイベントループ内で行われます。stop命令以外ではイベントは処理されません
        各イベントのコールバックには、異なる型・数のコールバック引数が返されます
        
        Args:
            event_name (str): イベントの名前
                "PG_TICK": イベントループの1ループ毎に呼び出されます
                "PG_FRAME": 1秒間に62.5回呼び出されます
                "PG_WINDOWRESIZED": サイズ可変ウィンドウにて、ウィンドウサイズが変更されたときに呼び出されます。最大化・最小化・元に戻すでも呼び出されます
                "PG_CHAR": 文字入力により呼び出されます。文字が押された瞬間と、長押しされている場合は一定時間後に連続して呼び出されます
                "PG_KEYDOWN": キーが押下されたときに1回だけ呼び出されます
                "PG_TEXTINPUT: キーボード入力により文字が入力されたときに呼び出されます
                "PG_TEXTEDITING": IMEに入力されている文字列が変更されたときに呼び出されます。このイベントにより返される文字列は未確定の文字列で、確定した場合はPG_TEXTEDITINGに""が、PG_TEXTINPUTに確定した文字列が返されます
                "PG_ACTIVE": アクティブウィンドウが変更されたときに呼び出されます
                "PG_MBUTTONDOWN": マウスの左ボタンが押下されたときに呼び出されます
            function_pointer (callable): コールバック関数
        
        Returns:
            なし
        
        """
        self.eventclbk[event_name] = function_pointer
    #
    def stop(self, loop_type = 1) -> None:
        """プログラムの実行を止め、イベントループに入る
        
        メインプログラムの実行を中断させ、イベントループを開始します
        この関数の実行が終了するのは、SGPGのウィンドウが閉じられるときです
        
        Args:
            loop_type (int): 無限ループの実行種別s
        
        Returns:
            なし
        
        """
        game_close = 0
        pygame.display.flip()
        if loop_type == 1:
            pygame.time.set_timer(25, 16)
        while game_close == 0:
            pygame.event.pump()
            if loop_type == 1:
                evlist = [pygame.event.wait()]
            elif loop_type == 0:
                evlist = pygame.event.get()
            for event in evlist:
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
                        pass
                        #print(event)
            # 1 time for every frame loop
            if loop_type == 0:
                if self.eventclbk.get("PG_FRAME") != None:
                    self.eventclbk["PG_FRAME"]()
                pygame.display.flip()
            #
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
        """ウィンドウのタイトルテキストを設定する
        
        ウィンドウのタイトルバーに表示するテキストを設定します
        
        Args:
            title_text (str, optional): タイトルテキスト
                ""(規定): タイトルバーにテキストを何も表示しません
        
        Returns:
            なし
        
        """
        pygame.display.set_caption(title_text)
        pass
    #
    def redraw_now(self) -> None:
        """強制的に再描画する
        
        ウィンドウを再描画します
        通常ウィンドウの再描画はstopイベントループ中に自動的に行われますが、それ以外の場所で手動で行いたい場合に用います
        
        Args:
            なし
        
        Returns:
            なし
        
        """
        pygame.display.flip()
    #
    def mouse(self, x: int|float|None = None, y: int|float|None = None) -> None:
        """マウスカーソルの状態を変更する
        
        マウスカーソルの座標を、指定した場所に移動させます。x、yのいずれかを負の値に指定した場合、マウスカーソルをSGPGウィンドウ上で表示しないようにします
        x、yの両方に値を指定しなかった場合、マウスカーソルがSGPGウィンドウ上で表示されるようにします
        
        Args:
            x (int|float|None, optional) : 設定するX座標
                None(規定): マウスカーソルの表示状態を表示に変更するときに使います
                <0: マウスカーソルの表示状態を非表示に変更します
                >=0: マウスカーソルを指定した座標に移動します
            y (int|float|None, optional) : 設定するY座標
                None(規定): マウスカーソルの表示状態を表示に変更するときに使います
                <0: マウスカーソルの表示状態を非表示に変更します
                >=0: マウスカーソルを指定した座標に移動します
        
        Returns:
            なし
        
        """
        if x == None and y == None:
            pygame.mouse.set_visible(True)
        elif x < 0 or y < 0:
            pygame.mouse.set_visible(False)
    #
    def end(self):
        """SGPGを終了する
        
        すべてのウィンドウを閉じてSGPGを終了します。再度同じインスタンスを使用するためには、手動で__init__メソッドを実行する必要があります
        
        Args:
            なし
        
        Returns:
            なし
            
        """
        pygame.quit()
