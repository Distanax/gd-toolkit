"""Minimal Geometry Dash 2.2 level builder -> .gmd (GDShare import format).

Coordinates are GD units: 30 units = 1 block. Object x/y are object centres.
Ground-row y and other conventions are verified empirically (see NOTES.md).
"""
import base64, gzip, html

# ---- object IDs -------------------------------------------------------------
BLOCK = 1
SPIKE = 8
HALF_SPIKE = 39
YELLOW_PAD, PINK_PAD, RED_PAD, BLUE_PAD = 35, 140, 1332, 67
YELLOW_ORB, PINK_ORB, RED_ORB, BLUE_ORB, GREEN_ORB, BLACK_ORB, DASH_ORB = 36, 141, 1333, 84, 1022, 1330, 1704
PORTAL = dict(cube=12, ship=13, ball=47, ufo=111, wave=660, robot=745, spider=1331, swing=1933)
GRAV_DOWN, GRAV_UP = 10, 11
MIRROR_ON, MIRROR_OFF = 45, 46
MINI_ON, MINI_OFF = 101, 99
DUAL_ON, DUAL_OFF = 286, 287
SPEED_PORTAL = {0.5: 200, 1: 201, 2: 202, 3: 203, 4: 1334}
TEXT = 914
# triggers
COLOR_T, MOVE_T, PULSE_T, ALPHA_T, TOGGLE_T, SPAWN_T = 899, 901, 1006, 1007, 1049, 1268
ROTATE_T, FOLLOW_T, SHAKE_T, STOP_T, ZOOM_T = 1346, 1347, 1520, 1616, 1913

# speed in units/second for each speed setting (GD 2.2)
SPEEDS = {0.5: 251.16, 1: 311.58, 2: 387.42, 3: 468.0, 4: 576.0}
HEADER_SPEED = {1: 0, 0.5: 1, 2: 2, 3: 3, 4: 4}

# colour channels
BG, GROUND, LINE, OBJ, GROUND2, MG, MG2 = 1000, 1001, 1002, 1004, 1009, 1013, 1014


def _fmt(v):
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, float):
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s if s not in ("", "-0") else "0"
    if isinstance(v, (list, tuple)):
        return ".".join(str(g) for g in v)
    return str(v)


class Level:
    def __init__(self, name, song_id=None, official_song=0, start_speed=1,
                 start_mode=0, description=""):
        self.name = name
        self.song_id = song_id
        self.official_song = official_song
        self.start_speed = start_speed
        self.start_mode = start_mode
        self.description = description
        self.objects = []          # list of dict{key:int -> value}
        self.colors = {}           # channel -> (r,g,b,opacity,blending)

    # -- building ------------------------------------------------------------
    ALIAS = dict(flip_x=4, flip_y=5, rot=6, color=21, detail=22, z_layer=24,
                 z_order=25, scale=32, groups=57, dont_fade=64, dont_enter=67)

    def add(self, oid, x, y, keys=None, **props):
        """props use names from ALIAS; keys is a dict of raw numeric GD keys."""
        o = {1: oid, 2: float(x), 3: float(y)}
        for k, v in props.items():
            o[self.ALIAS[k]] = v
        if keys:
            o.update(keys)
        self.objects.append(o)
        return o

    def raw(self, oid, x, y, keys):
        """Add an object with raw numeric property keys."""
        o = {1: oid, 2: float(x), 3: float(y)}
        o.update(keys)
        self.objects.append(o)
        return o

    def text(self, x, y, s, **props):
        return self.add(TEXT, x, y, keys={31: base64.urlsafe_b64encode(s.encode()).decode()}, **props)

    def set_color(self, ch, r, g, b, opacity=1.0, blending=False):
        self.colors[ch] = (r, g, b, opacity, blending)

    # -- serialising -----------------------------------------------------------
    def _kS38(self):
        parts = []
        for ch, (r, g, b, op, bl) in sorted(self.colors.items()):
            parts.append(f"1_{r}_2_{g}_3_{b}_11_255_12_255_13_255_4_-1_6_{ch}_7_{_fmt(float(op))}_15_1_18_0_8_1"
                         + ("_5_1" if bl else "") + "|")
        return "".join(parts)

    def level_string(self):
        header = (f"kS38,{self._kS38()},kA13,0,kA15,0,kA16,0,kA14,,kA6,0,kA7,0,kA25,0,kA17,0,"
                  f"kA18,0,kS39,0,kA2,{self.start_mode},kA3,0,kA8,0,kA4,{HEADER_SPEED[self.start_speed]},"
                  f"kA9,0,kA10,0,kA22,0,kA23,0,kA24,0,kA27,1,kA40,1,kA41,1,kA42,1,kA28,0,kA29,0,"
                  f"kA31,1,kA32,1,kA36,0,kA43,0,kA44,0,kA45,1,kA33,1,kA34,1,kA35,0,kA37,1,kA38,1,"
                  f"kA39,1,kA19,0,kA26,0,kA20,0,kA21,0,kA11,0;")
        objs = []
        for o in self.objects:
            objs.append(",".join(f"{k},{_fmt(v)}" for k, v in o.items()) + ";")
        return header + "".join(objs)

    def gmd(self):
        enc = base64.urlsafe_b64encode(gzip.compress(self.level_string().encode(), mtime=0)).decode()
        desc = base64.urlsafe_b64encode(self.description.encode()).decode()
        song = (f"<k>k45</k><i>{self.song_id}</i>" if self.song_id
                else f"<k>k8</k><i>{self.official_song}</i>")
        return ('<?xml version="1.0"?><plist version="1.0" gjver="2.0"><dict>'
                f"<k>kCEK</k><i>4</i><k>k2</k><s>{html.escape(self.name)}</s>"
                f"<k>k4</k><s>{enc}</s><k>k3</k><s>{desc}</s>{song}"
                "<k>k13</k><t /><k>k21</k><i>2</i><k>k16</k><i>1</i><k>k50</k><i>45</i>"
                "</dict></plist>")

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.gmd())
        return path


# ---- timing helpers ---------------------------------------------------------
def x_at_time(t, speed=1, x0=0.0):
    """x position the player reaches after t seconds at constant speed from x0."""
    return x0 + SPEEDS[speed] * t


def beat_xs(bpm, n_beats, speed=1, offset=0.0, x0=0.0, subdiv=1):
    """x positions of beats (or subdivisions) at constant speed."""
    step = 60.0 / bpm / subdiv
    return [x_at_time(offset + i * step, speed, x0) for i in range(n_beats * subdiv)]
