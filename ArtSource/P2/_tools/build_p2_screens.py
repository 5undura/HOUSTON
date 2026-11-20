"""HOUSTON P2 monitor screen graphics (PSX/CRT style). Run: python3 build_p2_screens.py <outdir>"""
import sys, os, math
import numpy as np
from PIL import Image

F = {
 'A':"010101111101101",'B':"110101110101110",'C':"011100100100011",'D':"110101101101110",'E':"111100110100111",
 'F':"111100110100100",'G':"011100101101011",'H':"101101111101101",'I':"111010010010111",'J':"001001001101010",
 'K':"101101110101101",'L':"100100100100111",'M':"101111111101101",'N':"110101101101101",'O':"111101101101111",
 'P':"110101110100100",'Q':"010101101110011",'R':"110101110101101",'S':"011100010001110",'T':"111010010010010",
 'U':"101101101101111",'V':"101101101101010",'W':"101101111111101",'X':"101101010101101",'Y':"101101010010010",
 'Z':"111001010100111",'0':"010101101101010",'1':"010110010010111",'2':"110001010100111",'3':"110001010001110",
 '4':"101101111001001",'5':"111100110001110",'6':"011100111101111",'7':"111001010010010",'8':"111101111101111",
 '9':"111101111001110",'-':"000000111000000",'.':"000000000000010",' ':"000000000000000",'+':"000010111010000",
 '!':"010010010000010",'%':"101001010100101",'/':"001001010100100",':':"000010000010000",'>':"100010001010100",
 '<':"001010100010001",'_':"000000000000111",'?':"110001010000010",'#':"101111101111101",'=':"000111000111000",
 '[':"110100100100110",']':"011001001001011",'(':"010100100100010",')':"010001001001010",'*':"000101010101000",
}


THEME = os.environ.get("HOUSTON_SCREEN_THEME", "mono")


class C:
    def __init__(s, w, h, bg):
        s.w, s.h = w, h
        s.a = np.zeros((h, w, 3), float); s.a[:] = bg

    def px(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h: s.a[y, x] = c

    def rect(s, x0, y0, x1, y1, c):
        s.a[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = c

    def frame(s, x0, y0, x1, y1, c):
        s.rect(x0, y0, x1, y0 + 1, c); s.rect(x0, y1 - 1, x1, y1, c)
        s.rect(x0, y0, x0 + 1, y1, c); s.rect(x1 - 1, y0, x1, y1, c)

    def line(s, x0, y0, x1, y1, c, dash=0):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            if dash and (i // dash) % 2: continue
            s.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def text(s, x, y, t, c, sc=1):
        for ch in t.upper():
            g = F.get(ch, F[' '])
            for i, b in enumerate(g):
                if b == '1': s.rect(x + (i % 3) * sc, y + (i // 3) * sc, x + (i % 3) * sc + sc, y + (i // 3) * sc + sc, c)
            x += 4 * sc
        return x

    def tw(s, t, sc=1): return len(t) * 4 * sc - sc

    def tag(s, x, y, t, c, sc=1):  # inverse highlight: bright block, dark text
        s.rect(x - 2, y - 2, x + s.tw(t, sc) + 2, y + 5 * sc + 2, c)
        return s.text(x, y, t, (4, 8, 6), sc)

    def circle(s, cx, cy, r, c):
        for k in range(int(r * 8)):
            a = 2 * math.pi * k / int(r * 8)
            s.px(round(cx + r * math.cos(a)), round(cy + r * math.sin(a)), c)

    def crt(s, scan=0.82, vign=0.35, glow=True):
        a = s.a.copy()
        if glow:  # cheap phosphor bloom
            b = a.copy()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                b += np.roll(np.roll(a, dx, 1), dy, 0) * 0.18
            a = np.maximum(a, b * 0.85)
        a[1::2] *= scan
        yy, xx = np.mgrid[0:s.h, 0:s.w]
        d = ((xx - s.w / 2) / (s.w / 2)) ** 2 + ((yy - s.h / 2) / (s.h / 2)) ** 2
        a *= (1 - vign * np.clip(d, 0, 1.4) / 1.4)[..., None]
        bay = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 15 - 0.5
        a += (bay[yy % 4, xx % 4] * 6)[..., None]
        s.a = np.clip(a, 0, 255)

    def save(s, path):
        a = s.a
        if THEME == "mono":  # single-phosphor green: brightness = max channel
            v = a.max(axis=2)
            v = np.clip((v - 4) * 1.08, 0, 255)
            a = np.stack([v * 0.16, v, v * 0.42], axis=2) + np.stack([np.clip(v - 200, 0, 55) * 2.2] * 3, axis=2) * np.array([1, 0, 1])
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB').save(path)


GREEN = (90, 235, 120); DGREEN = (30, 90, 45); CYAN = (90, 220, 220); AMBER = (240, 170, 50)
RED = (235, 70, 55); WHITE = (220, 230, 225); BLUE = (80, 140, 230); DIM = (40, 70, 90)


def admin_terminal(out):
    s = C(160, 120, (6, 16, 9))
    s.rect(0, 0, 160, 9, DGREEN); s.text(3, 2, "HOUSTON CTRL", GREEN); s.text(160 - s.tw("B2-07") - 3, 2, "B2-07", GREEN)
    y = 13
    for t, c in (("> LOGIN: ADMIN", GREEN), ("> ACCESS GRANTED", GREEN), ("> SEARCH DEBRIS DB", GREEN)):
        s.text(3, y, t, c); y += 7
    s.frame(2, y + 1, 158, y + 55, DGREEN)
    s.text(5, y + 4, "SECTOR", CYAN); s.text(40, y + 4, "FEATURE", CYAN); s.text(120, y + 4, "SIZE", CYAN)
    s.line(4, y + 10, 155, y + 10, DGREEN)
    rows = [("A-1", "HULL PLATE", "L"), ("A-4", "SOLAR WING", "M"), ("B-3", "RED MARK", "S"), ("C-2", "ANTENNA X3", "M"),
            ("D-5", "FUEL TANK", "L"), ("E-2", "NO DATA", "--")]
    for i, (a, b, m) in enumerate(rows):
        yy = y + 13 + i * 7
        if i == 2: s.rect(3, yy - 1, 157, yy + 6, DGREEN)
        s.text(5, yy, a, GREEN); s.text(40, yy, b, GREEN); s.text(122, yy, m, GREEN)
    y += 59
    s.text(3, y, "> CONN EX-07: SIGNAL WEAK", AMBER); y += 7
    x = s.text(3, y, "> ", GREEN); s.rect(x, y, x + 3, y + 5, GREEN)
    s.crt(); s.save(os.path.join(out, "UI_P2_AdminTerminal_01.png"))


def health_status(out):
    s = C(160, 120, (4, 10, 14))
    s.text(3, 3, "HEALTH STATUS", CYAN); s.tag(160 - s.tw("CREW 00") - 4, 3, "CREW 00", RED)
    s.line(2, 10, 157, 10, DIM)
    gx0, gy0, gx1, gy1 = 3, 14, 157, 54
    for x in range(gx0, gx1, 8): s.line(x, gy0, x, gy1, (14, 34, 30))
    for y in range(gy0, gy1, 8): s.line(gx0, y, gx1, y, (14, 34, 30))
    base = 38; pts = []
    for x in range(gx0, gx1):
        p = (x - gx0) % 34
        v = {8: -2, 9: -4, 10: -2, 13: 3, 14: -18, 15: 10, 16: 2, 22: -3, 23: -5, 24: -3}.get(p, 0)
        pts.append((x, base + v))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]): s.line(x0, y0, x1, y1, GREEN)
    s.rect(gx1 - 12, gy0, gx1, gy1, (4, 10, 14))
    s.text(3, 60, "HR", GREEN); s.text(3, 68, "112", GREEN, 2); s.text(30, 74, "BPM", DGREEN)
    s.text(58, 60, "SPO2", CYAN); s.text(58, 68, "84%", CYAN, 2)
    s.text(110, 60, "O2 TANK", AMBER); s.text(110, 68, "31%", AMBER, 2)
    s.frame(110, 82, 157, 88, AMBER); s.rect(111, 83, 111 + int(45 * 0.31), 87, AMBER)
    s.text(3, 92, "BIO ID:", WHITE); s.tag(36, 92, "NO MATCH", RED)
    s.rect(0, 104, 160, 116, RED); s.text(80 - s.tw("WARNING: O2 LOW") // 2, 107, "WARNING: O2 LOW", (4, 8, 6))
    s.crt(); s.save(os.path.join(out, "UI_P2_HealthStatus_01.png"))


def nav_map(out):
    s = C(256, 144, (6, 12, 30))
    rng = np.random.default_rng(3)
    for _ in range(90): s.px(int(rng.integers(0, 256)), int(rng.integers(0, 144)), (70, 90, 130) if rng.random() > .2 else (180, 190, 220))
    mx, my, cs = 18, 14, 24
    for i in range(6):
        s.line(mx + i * cs, my, mx + i * cs, my + 5 * cs, (30, 60, 110), dash=2)
        s.line(mx, my + i * cs, mx + 5 * cs, my + i * cs, (30, 60, 110), dash=2)
    for i, L in enumerate("ABCDE"): s.text(mx + i * cs + cs // 2 - 1, my - 8, L, BLUE)
    for j in range(5): s.text(mx - 7, my + j * cs + cs // 2 - 2, str(j + 1), BLUE)
    debris = [(0, 0, 'x'), (3, 0, 'x'), (1, 2, 'o'), (2, 1, 'x'), (2, 1, 'x'), (4, 4, 'o'), (1, 4, 'x'), (3, 3, 'x')]
    for k, (cx, cy, kind) in enumerate(debris):
        x = mx + cx * cs + 6 + (k * 5) % 12; y = my + cy * cs + 6 + (k * 7) % 12
        if kind == 'x': s.line(x - 2, y - 2, x + 2, y + 2, AMBER); s.line(x - 2, y + 2, x + 2, y - 2, AMBER)
        else: s.circle(x, y, 2.5, AMBER)
    hx, hy = mx + 5 * cs + 22, my + 2 * cs
    s.line(mx + 5 * cs + 4, hy + 4, mx + 5 * cs - 30, hy + 4, CYAN, dash=3)
    s.text(mx + 5 * cs - 36, hy + 1, "?", RED)
    s.rect(mx + 5 * cs + 2, hy + 2, mx + 5 * cs + 6, hy + 6, CYAN); s.text(mx + 5 * cs - 10, hy + 9, "HQ", CYAN)
    px0 = 150
    s.frame(px0, 8, 250, 136, (30, 60, 110))
    s.text(px0 + 4, 12, "DEEP NAV", WHITE); s.line(px0 + 2, 19, 248, 19, (30, 60, 110))
    info = [("TARGET", "EX-07", RED), ("SECTOR", "?-?", AMBER), ("DIST", "4.2 AU", CYAN), ("HEAD", "217", CYAN), ("SIGNAL", "WEAK", AMBER)]
    for i, (k, v, c) in enumerate(info):
        s.text(px0 + 4, 24 + i * 10, k, BLUE); (s.tag(px0 + 46, 24 + i * 10, v, c) if k == "TARGET" else s.text(px0 + 44, 24 + i * 10, v, c))
    s.text(px0 + 4, 80, "INPUT COORD", WHITE); s.frame(px0 + 4, 88, 246, 100, CYAN)
    x = s.text(px0 + 8, 91, "_-_", CYAN)
    s.text(px0 + 4, 108, "X  DEBRIS", AMBER); s.rect(px0 + 5, 117, px0 + 8, 120, CYAN); s.text(px0 + 16, 116, "HQ", CYAN); s.text(px0 + 4, 124, "? UNKNOWN", RED)
    s.crt(scan=0.86, vign=0.3); s.save(os.path.join(out, "UI_P2_NavMap_01.png"))


def status_board(out):
    s = C(256, 144, (10, 12, 18))
    s.rect(0, 0, 256, 13, (40, 44, 58)); s.text(4, 4, "UNRETURNED VESSELS", WHITE); s.text(256 - s.tw("B2-07") - 4, 4, "B2-07", (150, 160, 180))
    cols = (6, 46, 118, 150)
    for x, h in zip(cols, ("ID", "LAST CONTACT", "CREW", "STATUS")): s.text(x, 18, h, (130, 150, 190))
    s.line(4, 25, 252, 25, (60, 70, 90))
    rows = [("EX-01", "2081.03.14", "4", "LOST", RED), ("EX-02", "2082.11.02", "3", "LOST", RED), ("EX-03", "2084.06.21", "4", "NO SIGNAL", AMBER),
            ("EX-04", "2085.01.09", "2", "LOST", RED), ("EX-05", "2086.08.30", "3", "NO SIGNAL", AMBER), ("EX-06", "2087.04.17", "4", "LOST", RED),
            ("EX-07", "2088.12.03", "0", "ACTIVE?", (255, 200, 80))]
    for i, (a, b, c, st, col) in enumerate(rows):
        y = 30 + i * 15
        if a == "EX-07": s.rect(3, y - 3, 253, y + 9, (60, 44, 16))
        s.text(6, y, a, WHITE); s.text(46, y, b, (170, 180, 200)); (s.tag(122, y, c, RED) if c == "0" else s.text(122, y, c, (170, 180, 200)))
        s.rect(150, y - 2, 150 + s.tw(st) + 6, y + 7, tuple(v * 0.35 for v in col)); s.text(153, y, st, col)
        if i < 6: s.line(4, y + 11, 252, y + 11, (30, 34, 46))
    s.crt(scan=0.86, vign=0.28); s.save(os.path.join(out, "UI_P2_StatusBoard_01.png"))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for f in (admin_terminal, health_status, nav_map, status_board): f(out)
