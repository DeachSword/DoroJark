import json
import math
from PIL import Image, ImageDraw, ImageFont


class Chart:
    def __init__(self, cl, chartData):
        self.cl = cl
        self.chart = self.ChartDataReader(chartData)

        # Settings
        self.APP_VER = "v1.0.6"
        self.FRAME = 2
        self.FRAME_IMG_S = 8
        self.FRAME_IMG_H = 512 * self.FRAME
        self.FRAME_IMG_W = 128
        self.FRAME_IMG_P = 36
        self.LANE_W = self.FRAME_IMG_W / 7
        self.LANE_H = 2
        self.SLIDE_W = int(self.LANE_W / 4)
        self.IMG_PADDING = 50

        # self.BPM = 179
        # self.FRAME_SEC = 60 / BPM
        self.NOW_FRAME = 0
        self.TOTAL_FRAME = 0
        self.BAR_LINE_OFFSET = 0
        self.FRAME_S = 0
        if len(self.chart["BarLineList"]) == 0:
            self.chart["BarLineList"] = []
            for i in range(1, int(self.getLastLaneTime() + 3)):
                self.chart["BarLineList"].append(i)
        self.BAR_LINE_OFFSET = (
            self.chart["BarLineList"][1] - self.chart["BarLineList"][0]
        )
        self.FRAME_S = self.chart["BarLineList"][0] - self.BAR_LINE_OFFSET
        self.FRAME_E = 0
        self.FRAME_N = 0
        self.FRAME_P = 0
        self.FRAME_NOW = 0
        self.PASS_LANE = []
        self.imgs = []

        self.DEBUG_IMG_H = 0

    def renderTo(self, path):
        img = self.newImg()
        img1 = ImageDraw.Draw(img)
        self.DrawLine(img1)
        self.DrawBarLine(img1)
        self.BarLineH = {}
        self.drawText(img1, self.APP_VER, "#A6A6D2")
        self.NOW_FRAME = 1
        self.SaveBarLineH(self.FRAME_S)  # first
        self.drawTimeText(img1, self.FRAME_S)
        for BarLine in self.chart["BarLineList"]:
            INC_NEXT = False
            if self.NOW_FRAME == 0:
                self.drawTimeText(img1, self.FRAME_S)
                self.SaveBarLineH(self.FRAME_S)
                self.FRAME_S = self.getPrevBarLine(self.FRAME_S)
            self.NOW_FRAME += 1
            # FRAME_P = getPrevBarLine(BarLine)
            IS_END = False
            self.FRAME_N = 0
            try:
                self.FRAME_N = self.getNextBarLine(BarLine)
            except:
                IS_END = True
            self.SaveBarLineH(BarLine)
            blh, blw = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
                self.NOW_FRAME
            ) + self.FRAME_IMG_S * 2, 0
            self.drawTimeText(img1, BarLine)
            # v1.0.1: 更新 IS_END 解決最後一節無輸出的問題
            # v1.0.2: 添加滑條判定點
            # v1.0.3: 解決音符錯位問題 (小節切換時)
            # v1.0.4: 解決 IS_END 導致的錯誤判定
            # v1.0.5: 優化浮水印
            # v1.0.6: 支持斜滑條(黃) / 修正bar line為空
            if (self.NOW_FRAME > 0 and self.NOW_FRAME % 4 == 0) or IS_END:
                self.FRAME_E = BarLine
                if self.NOW_FRAME % (self.FRAME * 4) == 0:
                    INC_NEXT = True
                    self.FRAME_E = self.FRAME_N
                    self.NOW_FRAME += 1
                    self.SaveBarLineH(self.FRAME_E)
                for note in self.chart["NoteDataList"]:
                    if note in self.PASS_LANE:
                        if note.get("NextId", 0) == 0:
                            continue
                    _Type = note.get("Type", 0)
                    if note["Time"] >= self.FRAME_S and note["Time"] < self.FRAME_E:
                        FRAME_OUT = self.FRAME_E
                        IS_OUT_RANGE = False
                        INC_PREV = False
                        IS_START_RANGE = False
                        if len(self.BarLineH) >= 5:
                            if self.NOW_FRAME == 4:
                                if (
                                    self.BarLineH[-1] <= note["Time"]
                                    and self.BarLineH[0] > note["Time"]
                                ):
                                    INC_PREV = True
                                    IS_START_RANGE = True
                            elif self.NOW_FRAME == (self.FRAME * 4) + 1:
                                FRAME_OUT = self.BarLineH[(self.FRAME * 4)]
                                IS_OUT_RANGE = note["Time"] > FRAME_OUT
                                IS_START_RANGE = True
                        elif IS_END:
                            if -1 in self.BarLineH:
                                INC_PREV = True
                                IS_START_RANGE = True
                        lw_s = note["LaneId"] * self.LANE_W + self.FRAME_IMG_P
                        lw_e = lw_s + self.LANE_W
                        lh = self.getBarLineTimeOffsetV2(
                            note["Time"],
                            INC_PREV,
                            INC_NEXT and IS_OUT_RANGE,
                            IS_START_RANGE,
                        )
                        lh_s = note["Time"]
                        if lh_s > self.FRAME_IMG_H:
                            lh_s -= self.FRAME_IMG_H
                        lh_s = (self.FRAME_IMG_H) - lh
                        lh_e = lh_s - self.LANE_H
                        if note.get("NextId", 0) != 0:
                            nextNote = self.getNextLane(note["NextId"])
                            IS_OUT_RANGE = nextNote["Time"] > FRAME_OUT
                            _INC_PREV = INC_PREV
                            _IS_START_RANGE = IS_START_RANGE
                            if _INC_PREV:
                                # if 0 in self.BarLineH:
                                if nextNote["Time"] >= self.BarLineH[0]:
                                    _INC_PREV = False
                                    _IS_START_RANGE = False
                            _bt = self.getBarLineTimeOffsetV2(
                                nextNote["Time"],
                                _INC_PREV,
                                INC_NEXT and IS_OUT_RANGE,
                                _IS_START_RANGE,
                            )
                            lh_e = (self.FRAME_IMG_H) - _bt
                            if _Type == 6:
                                if nextNote["LaneId"] != note["LaneId"]:
                                    lw_e = (
                                        nextNote["LaneId"] * self.LANE_W
                                        + self.LANE_W / 2
                                        + self.FRAME_IMG_P
                                    )
                            elif _Type == 9:
                                lw_e = (
                                    nextNote["LaneId"] * self.LANE_W
                                    + self.LANE_W / 2
                                    + self.FRAME_IMG_P
                                )
                                Direction = nextNote.get("Direction", 0)
                                if Direction != 0:
                                    traget_lane = nextNote["LaneId"] + Direction
                                    traget_ws = lw_e + 4
                                    traget_we = (
                                        traget_lane * self.LANE_W
                                        + self.LANE_W / 2
                                        + self.FRAME_IMG_P
                                    )
                                    traget_arrow = "<"
                                    if traget_lane > nextNote["LaneId"]:
                                        traget_arrow = ">"
                                    else:
                                        traget_ws = traget_we + 4
                                    traget_arrow *= abs(Direction) * 2
                                    if len(traget_arrow) >= 5:
                                        traget_arrow += traget_arrow[0] * 2
                                    if len(traget_arrow) >= 4:
                                        traget_arrow += traget_arrow[0]
                                    img1.text(
                                        (traget_ws, lh_e - 5),
                                        traget_arrow,
                                        fill="#D049BE",
                                    )
                        color = self.getLaneColor(_Type)
                        SLIDE_POINT_COLOR = "rgba(219, 62, 140, 255)"
                        if _Type in [6, 9] and (lw_s + self.LANE_W) != lw_e:
                            lw_s = (lw_s * 2 + self.LANE_W) / 2
                            if _Type == 9:
                                img1.line(
                                    [(lw_s, lh_s), (lw_e, lh_e)],
                                    fill=color,
                                    width=self.SLIDE_W,
                                )
                            else:
                                # img1.line([
                                #     (lw_s, lh_s), (lw_e, lh_e)
                                # ], fill=color, width=int(self.LANE_W), joint='curve')
                                img1.polygon(
                                    (
                                        (lw_s - self.LANE_W / 2, lh_s),
                                        (lw_s + self.LANE_W / 2, lh_s),
                                        (lw_e - self.LANE_W / 2, lh_e),
                                    ),
                                    fill=color,
                                )
                                img1.polygon(
                                    (
                                        (lw_s + self.LANE_W / 2, lh_s),
                                        (lw_e - self.LANE_W / 2, lh_e),
                                        (lw_e + self.LANE_W / 2, lh_e),
                                    ),
                                    fill=color,
                                )
                            if _Type == 9:
                                # 滑條判定點
                                for s_point in [(lw_s, lh_s), (lw_e, lh_e)]:
                                    lw_s2, lh_s2 = s_point
                                    lw_s2 = lw_s2 - self.LANE_W / 2
                                    lw_e2 = lw_s2
                                    lh_e2 = lh_s2

                                    lw_s2 += self.LANE_W / 3
                                    lw_e2 += self.LANE_W - self.LANE_W / 3
                                    lh_s2 += self.LANE_H
                                    lh_e2 -= self.LANE_H
                                    img1.rectangle(
                                        [(lw_s2, lh_s2), (lw_e2, lh_e2)],
                                        fill="rgba(219, 62, 140, 255)",
                                        width=0,
                                    )
                        else:
                            if _Type == 9:
                                # 有方向的
                                lw_s += self.LANE_W / 3
                                lw_e -= self.LANE_W / 3
                                lh_s += self.LANE_H
                                lh_e -= self.LANE_H
                                Direction = note.get("Direction", 0)
                                if Direction != 0:
                                    traget_lane = note["LaneId"] + Direction
                                    traget_ws = lw_e + 4
                                    traget_we = (
                                        traget_lane * self.LANE_W
                                        + self.LANE_W / 2
                                        + self.FRAME_IMG_P
                                    )
                                    traget_arrow = "<"
                                    if traget_lane > note["LaneId"]:
                                        traget_arrow = ">"
                                    else:
                                        traget_ws = traget_we + 4
                                    traget_arrow *= abs(Direction) * 2
                                    if len(traget_arrow) >= 5:
                                        traget_arrow += traget_arrow[0] * 2
                                    if len(traget_arrow) >= 4:
                                        traget_arrow += traget_arrow[0]
                                    img1.text(
                                        (traget_ws, lh_e - 2),
                                        traget_arrow,
                                        fill="#D049BE",
                                    )
                                color = SLIDE_POINT_COLOR
                            img1.rectangle(
                                [(lw_s, lh_s), (lw_e, lh_e)], fill=color, width=0
                            )
                self.TOTAL_FRAME += 1
                self.BarLineH = {}
                if self.TOTAL_FRAME % self.FRAME == 0:
                    self.imgs.append(img)
                    img = self.newImg()
                    img1 = ImageDraw.Draw(img)
                    self.DrawLine(img1)
                    self.DrawBarLine(img1)
                    self.NOW_FRAME = -1
                    self.SaveBarLineH(self.getPrevBarLine(BarLine))
                    self.NOW_FRAME = 0
                    self.FRAME_E = BarLine
                    self.PASS_LANE = []
                self.FRAME_S = self.FRAME_E
        if self.NOW_FRAME != 0:
            self.imgs.append(img)
        GLOBA = Image.new(
            "RGBA",
            (
                (self.FRAME_IMG_W + self.IMG_PADDING * 2) * len(self.imgs),
                self.FRAME_IMG_H + self.DEBUG_IMG_H,
            ),
        )
        i = 0
        for _img in self.imgs:
            GLOBA.paste(
                _img,
                (self.IMG_PADDING + (self.FRAME_IMG_W + self.IMG_PADDING * 2) * i, 0),
            )
            i += 1
        fontsize = 1  # starting font size
        font = ImageFont.truetype("arial.ttf", fontsize)
        MARK_TEXT = f"Made by DeachSword\n\nGenerated by D4DJ_CHART.py {self.APP_VER}"

        SIZE_TYPE = 0
        breakpoint = 0.9 * GLOBA.size[SIZE_TYPE]
        jumpsize = 75
        while True:
            if font.getsize(MARK_TEXT)[SIZE_TYPE] < breakpoint:
                fontsize += jumpsize
            else:
                jumpsize = jumpsize // 2
                fontsize -= jumpsize
            font = ImageFont.truetype("arial.ttf", fontsize)
            if jumpsize <= 1:
                break
        W, H = GLOBA.size
        w, h = font.getsize(MARK_TEXT)
        txt = Image.new("RGBA", GLOBA.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(txt)
        w, h = d.textsize(MARK_TEXT, font=font)
        d.text(
            ((W - w) / 2, (H - h) / 2),
            MARK_TEXT,
            fill=(255, 255, 255, 100),
            font=font,
            align="center",
        )
        angle = math.degrees(math.atan(GLOBA.size[1] / GLOBA.size[0]))
        txt = txt.rotate(angle, Image.NEAREST).convert("RGBA")
        GLOBA.paste(txt, (0, 0), mask=txt)
        GLOBA.save(path)

    def newImg(self):
        return Image.new(
            "RGBA",
            (
                self.FRAME_IMG_W + self.FRAME_IMG_P * 2,
                self.FRAME_IMG_H + self.DEBUG_IMG_H,
            ),
        )

    def DrawLine(self, img1):
        w = self.FRAME_IMG_P
        for i in range(6):
            w += self.LANE_W
            img1.line([(w, 0), (w, self.FRAME_IMG_H)], fill="#fff", width=0)

    def DrawBarLine(self, img1):
        for i in range(4 * self.FRAME + 1):
            h, w = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
                i
            ) + self.FRAME_IMG_S, self.FRAME_IMG_W + self.FRAME_IMG_P
            shape = [(self.FRAME_IMG_P, h), (w, h)]
            if h != 0:
                color = "#5B5B5B"
                if i % 4 == 0:
                    color = "#fff"
                img1.line(shape, fill=color, width=0)

    def getNextBarLine(self, time):
        for BarLine in self.chart["BarLineList"]:
            if BarLine > time:
                return BarLine
        raise ValueError

    def getPrevBarLine(self, time):
        prev = 0
        for BarLine in self.chart["BarLineList"]:
            if BarLine < time:
                if BarLine > prev:
                    prev = BarLine
        return prev

    def getNextLane(self, id):
        _i = 0
        for note in self.chart["NoteDataList"]:
            if _i == id:
                self.PASS_LANE.append(note)
                return note
            _i += 1
        raise ValueError

    def getLastLaneTime(self):
        _i = 0
        for note in self.chart["NoteDataList"]:
            if _i < note["Time"]:
                _i = note["Time"]
        return _i

    def getBarLineTimeOffsetV2(self, time, isPrev=False, isNext=False, isStart=True):
        prev = 0, 0
        next = -1, 0
        i = 2
        for BarLine in self.chart["BarLineList"]:
            bt = BarLine
            curr_f = i % (self.FRAME * 4)
            if curr_f == 0 and i != 0 and isStart:
                curr_f = self.FRAME * 4
            if isPrev:
                curr_f = curr_f - (self.FRAME * 4)
            if isNext:
                curr_f = (self.FRAME * 4) + 1
            h, w = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
                curr_f
            ) + self.FRAME_IMG_S, self.FRAME_IMG_W
            if bt == time:
                return h
            elif bt < time:
                if bt > prev[1]:
                    prev = curr_f, bt
            else:
                if next[0] == -1 or bt < next[1]:
                    next = curr_f, bt
            i += 1
        if next[0] != -1:
            p, pt = prev
            n, nt = next
            p = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
                p
            ) + self.FRAME_IMG_S
            n = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
                n
            ) + self.FRAME_IMG_S
            return (n - p) / (nt - pt) * (time - pt) + p
        raise ValueError(f"val is 0: {time} -> {prev}/{next}")

    def SaveBarLineH(self, b):
        _NOW_FRAME = self.NOW_FRAME
        if self.NOW_FRAME > 17:
            _NOW_FRAME = self.NOW_FRAME % 17
        self.BarLineH[_NOW_FRAME] = b

    @staticmethod
    def getLaneColor(_type):
        c = "red"
        if _type == 0:
            c = "#2894FF"
        elif _type == 1:
            c = "#4DFFFF"
        elif _type in [2, 3]:
            c = "#FF8000"
        elif _type in [4, 5]:
            c = "rgba(219, 0, 58, 150)"
        elif _type in [6, 7, 8]:
            c = "rgba(255, 221, 51, 150)"
        elif _type == 9:
            c = "#CA8EC2"
        else:
            print(f"NOT COLOR: {_type}")
        return c

    def drawTimeText(self, img1, _t):
        blh, blw = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
            self.NOW_FRAME
        ) + self.FRAME_IMG_S * 2, 0
        text = f"{_t:.2f}"
        while len(text) < 6:
            text = f"0{text}"
        img1.text((blw, self.FRAME_IMG_H - blh), text)

    def drawText(self, img1, _t, color):
        blh, blw = (self.FRAME_IMG_H - self.FRAME_IMG_S * 2) / (4 * self.FRAME) * (
            self.NOW_FRAME
        ) + self.FRAME_IMG_S * 2, 0
        text = _t
        img1.text((blw, self.FRAME_IMG_H - blh), text, fill=color)

    def ChartCommonDataReader(self, data):
        Decoder = [
            "SDRhythmTimes",
            "SkillTimes",
            "AudienceData",
            "FeverPrepareTime",
            "FeverTime",
            "ClubItemTriggers",
        ]
        return self.cl.readTo(data, Decoder)

    def ChartDataReader(self, data):
        NoteDataDecoder = [
            "LaneId",
            "Type",
            "Time",
            "NextId",
            "Direction",
            "EffectType",
            "EffectParameter",
        ]
        Decoder = [
            "_acbName",
            "SoflanDataList",
            "BarLineList",
            ["NoteDataList", [NoteDataDecoder]],
        ]
        return self.cl.readTo(data, Decoder)
