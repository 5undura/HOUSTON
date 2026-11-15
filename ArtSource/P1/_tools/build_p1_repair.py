"""HOUSTON P1 - 4면 수리 장치 (P1_RepairPanel_01). Blender 안에서 실행.
P2 팀의 houston_lib.py (ArtSource/P2/_tools) 를 그대로 사용한다.
규칙: 1 단위 = 1 m, 앞면은 -Y, 벽에 붙는 면이 y = 0, 바닥이 z = 0, 피벗은 바닥 중앙.
Unity 배치: Position (-1.6, 0, 0), Rotation (0, 90, 0) 이면 블록아웃 4면과 겹친다.
"""
import bpy, os, sys, math, importlib, json
import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
P1DIR = os.path.dirname(TOOLS)
ART = os.path.dirname(P1DIR)
REPO = os.path.dirname(ART)
sys.path.insert(0, os.path.join(ART, "P2", "_tools"))
import houston_lib as H
importlib.reload(H)

OUT = os.path.join(P1DIR, "_build")
MOD = os.path.join(OUT, "Models", "P1"); TEX = os.path.join(OUT, "Textures", "P1")
for d in (MOD, TEX):
    os.makedirs(d, exist_ok=True)

win = bpy.context.window_manager.windows[0]
sc = win.scene
N = "P1_RepairPanel_01"
PLACE_IN_CABIN = True   # 내보낸 뒤 블렌더 안에서 블록아웃 4면 자리에 놓기 (비교용)

R = math.radians
ZC = 1.2          # 조작판 중심 높이
YF = -0.22        # 조작판 앞면
def Z(yb): return ZC + yb

# ---------------- palette (녹슨 금속)
RUST = (120, 82, 60); RUST_D = (66, 44, 34); DARKPL = (58, 44, 38); SLOT = (20, 16, 14)
TRIM = (142, 114, 92); DARK = (42, 34, 30); BEIGE = (198, 178, 140); TXT = (216, 198, 162)
BRASS = (186, 148, 62); RED = (194, 52, 40); RED_D = (132, 36, 30); GREEN = (96, 214, 110); AMBER = (228, 158, 44)
LABEL = (206, 198, 172); STEEL = (110, 104, 98)
W_RED = (190, 44, 38); W_BLUE = (52, 92, 188); W_YEL = (222, 188, 48); W_ORG = (224, 122, 40)

KNOB_X = (-0.60, -0.38, -0.16); SLIDER_X = (0.17, 0.31, 0.45, 0.59); SWITCH_X = (0.20, 0.38, 0.56)
LAMP_X = (0.26, 0.38, 0.50); FUSE_X = (-0.55, -0.30)
ROW_Y = [0.58 - i * 0.06 for i in range(6)]
XL, XR = -0.63, -0.14


def rust(A, name, seed=0, amount=0.3, col=(150, 82, 36)):
    x0, y0, x1, y1 = A.cells[name]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    n = H._hash(xx // 3, yy // 3, seed) * 0.6 + H._hash(xx // 7 + 3, yy // 7 + 1, seed + 5) * 0.4
    m = n > (1 - amount)
    v = A.A[y0:y1, x0:x1, :3]
    v[m] = v[m] * 0.6 + np.array(col, float) * 0.4
    m2 = n < amount * 0.35
    v[m2] = v[m2] * 0.72


def quad_front(m, x0, x1, z0, z1, y, role):
    b = len(m.V)
    m.V += [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    m.face([b, b + 1, b + 2, b + 3], role, [(0, 0), (1, 0), (1, 1), (0, 1)])


def frame_boxes(m, x0, x1, z0, z1, t, y0, y1, role, front=None):
    ov = {"back": None}
    if front:
        ov["front"] = front
    m.box(x0, x0 + t, y0, y1, z0, z1, role, dict(ov))
    m.box(x1 - t, x1, y0, y1, z0, z1, role, dict(ov))
    m.box(x0 + t, x1 - t, y0, y1, z1 - t, z1, role, dict(ov))
    m.box(x0 + t, x1 - t, y0, y1, z0, z0 + t, role, dict(ov))


def ycyl(m, cx, cz, yback, depth, r, side, cap, seg=8, r1=None):
    """벽에서 플레이어 쪽(-Y)으로 튀어나오는 원기둥. 앞면에만 뚜껑."""
    start = len(m.V)
    m.cyl(0, 0, 0, depth, r, side, cap=cap, seg=seg, r1=r1, caps=(False, True), rot=math.pi / seg)
    m.xform(H.mul(H.trans(cx, yback, cz), H.rot_x(math.pi / 2)), start)


def xcyl(m, cx, cy, cz, length, r, side, cap, seg=6):
    start = len(m.V)
    m.cyl(0, 0, -length / 2, length / 2, r, side, cap=cap, seg=seg)
    m.xform(H.mul(H.trans(cx, cy, cz), H.rot_y(math.pi / 2)), start)


def pipe(m, pts, r, role, seg=5):
    """꺾이는 관(전선). 링을 공유해서 이음매가 벌어지지 않는다."""
    P = np.array(pts, float); n = len(P)
    mark = m.begin(); b = len(m.V)
    for i in range(n):
        t = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        t = t / np.linalg.norm(t)
        ref = np.array([0.0, 1.0, 0.0]) if abs(t[1]) < 0.9 else np.array([0.0, 0.0, 1.0])
        u = np.cross(t, ref); u /= np.linalg.norm(u)
        v = np.cross(t, u)
        for k in range(seg):
            a = 2 * math.pi * k / seg
            m.V.append(tuple(P[i] + r * (math.cos(a) * u + math.sin(a) * v)))
    for i in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            m.face([b + i * seg + k, b + i * seg + k2, b + (i + 1) * seg + k2, b + (i + 1) * seg + k], role,
                   [(k / seg, i / (n - 1)), ((k + 1) / seg, i / (n - 1)), ((k + 1) / seg, (i + 1) / (n - 1)), (k / seg, (i + 1) / (n - 1))])
    m.end(mark)


# ================================================================ atlas (128px)
A = H.Atlas(128)
A.cell("front", 0, 0, 96, 96)
A.cell("side", 96, 0, 128, 32).cell("trim", 96, 32, 112, 48).cell("dark", 112, 32, 128, 48)
A.cell("knob", 96, 48, 112, 64).cell("knobside", 112, 48, 128, 56).cell("handle", 112, 56, 128, 64)
A.cell("lever", 96, 64, 104, 80).cell("fuse", 104, 64, 112, 88).cell("fusecap", 112, 64, 120, 72).cell("term", 120, 64, 128, 72)
A.cell("lamp_g", 112, 72, 120, 80).cell("lamp_a", 120, 72, 128, 80).cell("lamp_r", 112, 80, 120, 88).cell("clip", 120, 80, 128, 88)
A.cell("pipe", 96, 80, 104, 88)
A.cell("w_red", 96, 88, 104, 96).cell("w_blue", 104, 88, 112, 96).cell("w_yel", 112, 88, 120, 96).cell("w_org", 120, 88, 128, 96)
A.cell("wirebox", 0, 96, 40, 122).cell("label", 40, 96, 64, 106).cell("plate", 64, 96, 76, 118).cell("hazard", 40, 106, 64, 112)
for i in range(6):
    A.cell("n%d" % (i + 1), 76 + i * 5, 96, 81 + i * 5, 103)


def FX(x): return (x + 0.75) / 1.5
def FY(yb): return (0.75 - yb) / 1.5
def frect(x0, x1, yb0, yb1, color, amp=6):
    A.rect("front", FX(x0), FY(yb1), FX(x1), FY(yb0), color, amp=amp)
def fframe(x0, x1, yb0, yb1, color):
    A.frame("front", FX(x0), FY(yb1), FX(x1), FY(yb0), color)

# ---- 앞판 (96px = 1.5m)
A.fill("front", RUST, amp=10, grad=10, speck=0.06, grime=0.35, seed=11)
rust(A, "front", seed=3, amount=0.3)
A.bevel("front", 22, 26)
A.frame("front", 0.03, 0.03, 0.97, 0.97, RUST_D)
for bx in (0.055, 0.49, 0.925):
    for by in (0.055, 0.925):
        A.dot("front", bx, by, (182, 156, 126), 2)
        A.dot("front", bx + 0.011, by + 0.011, (52, 36, 28), 1)
A.shade("front", FX(0.0), 0.05, FX(0.0) + 0.012, 0.95, -30)
# 노브 눈금 링
for kx in KNOB_X:
    A.circle("front", FX(kx), FY(0.05), 0.072 / 1.5, DARK)
    for ang in range(-135, 136, 45):
        A.dot("front", FX(kx) + math.sin(R(ang)) * 0.092 / 1.5 - 0.005, FY(0.05) - math.cos(R(ang)) * 0.092 / 1.5 - 0.005, TXT, 1)
# 환기구 판 + DANGER 라벨
frect(-0.68, -0.08, -0.40, -0.09, DARKPL); fframe(-0.68, -0.08, -0.40, -0.09, RUST_D)
A.hlines("front", FY(-0.12), FY(-0.25), 2, -26, FX(-0.64), FX(-0.12))
frect(-0.66, -0.27, -0.385, -0.28, RED_D, amp=4)
A.text("front", FX(-0.66) + 0.012, FY(-0.28) + 0.011, "DANGER", (236, 218, 194))
A.text("front", FX(-0.62), FY(-0.412), "FUSE", TXT)
# 전력 쪽: 표시등 자리, POWER, 슬라이더 판
for lx in LAMP_X:
    A.circle("front", FX(lx), FY(0.22), 0.042 / 1.5, DARK)
A.text("front", FX(0.17), FY(0.158), "POWER", TXT)
frect(0.09, 0.67, -0.44, 0.06, DARKPL); fframe(0.09, 0.67, -0.44, 0.06, RUST_D)
for i, sx in enumerate(SLIDER_X):
    frect(sx - 0.012, sx + 0.012, -0.34, 0.04, SLOT, amp=0)
    A.hlines("front", FY(0.04), FY(-0.34), 3, 36, FX(sx + 0.022), FX(sx + 0.05))
    A.text("front", FX(sx) - 0.016, FY(-0.352), str(i + 1), TXT)
A.hazard("front", 0.04, 0.925, 0.96, 0.955, w=3)

# ---- 나머지 셀
A.fill("side", RUST, amp=10, grad=8, speck=0.05, grime=0.4, seed=21); rust(A, "side", seed=8, amount=0.35); A.bevel("side", 18, 22)
A.fill("trim", TRIM, amp=8, grad=6, speck=0.04, grime=0.25, seed=22); rust(A, "trim", seed=9, amount=0.2); A.bevel("trim", 18, 20)
A.fill("dark", DARK, amp=5, grad=4, speck=0.02, grime=0.2, seed=23)
A.fill("knob", (36, 30, 28), amp=4, grad=0, speck=0, grime=0, seed=24)
A.circle("knob", 0.5, 0.5, 0.46, (74, 64, 58)); A.circle("knob", 0.5, 0.5, 0.46, (104, 92, 82), ring=0.07)
A.rect("knob", 0.44, 0.06, 0.57, 0.52, (236, 226, 204), amp=0)
A.fill("knobside", (58, 50, 46), amp=4, grad=6, speck=0, grime=0, seed=25); A.vlines("knobside", 0, 1, 2, -20)
A.fill("handle", BEIGE, amp=6, grad=10, speck=0.03, grime=0.15, seed=26); A.bevel("handle", 20, 30)
A.rect("handle", 0.0, 0.42, 1.0, 0.58, (84, 62, 48), amp=0)
A.fill("lever", (170, 160, 146), amp=6, grad=14, speck=0.02, grime=0.1, seed=27); A.bevel("lever", 22, 30)
A.fill("fuse", (176, 196, 190), amp=4, grad=0, speck=0, grime=0, seed=28)
A.rect("fuse", 0, 0, 1, 0.2, STEEL, amp=6); A.rect("fuse", 0, 0.8, 1, 1, STEEL, amp=6)
A.rect("fuse", 0.4, 0.2, 0.55, 0.8, (70, 60, 52), amp=0)
A.fill("fusecap", STEEL, amp=6, grad=6, speck=0, grime=0, seed=29)
A.fill("term", BRASS, amp=8, grad=10, speck=0.03, grime=0.1, seed=30); A.bevel("term", 26, 34); A.rect("term", 0.38, 0.38, 0.62, 0.62, (60, 46, 26), amp=0)
A.fill("clip", STEEL, amp=6, grad=10, speck=0.03, grime=0.2, seed=31); A.bevel("clip", 20, 26)
A.fill("pipe", (70, 58, 52), amp=6, grad=0, speck=0.03, grime=0, seed=32); A.hlines("pipe", 0, 1, 4, -18)
for nm, c in (("lamp_g", GREEN), ("lamp_a", AMBER), ("lamp_r", RED)):
    A.fill(nm, c, amp=6, grad=20, speck=0, grime=0, seed=33); A.frame(nm, 0, 0, 1, 1, tuple(int(v * 0.55) for v in c))
    A.dot(nm, 0.3, 0.3, (255, 250, 236), 2)
for nm, c in (("w_red", W_RED), ("w_blue", W_BLUE), ("w_yel", W_YEL), ("w_org", W_ORG)):
    A.fill(nm, c, amp=8, grad=0, speck=0, grime=0, seed=34); A.hlines(nm, 0, 1, 3, -26)
A.fill("wirebox", (30, 24, 22), amp=5, grad=4, speck=0.03, grime=0.1, seed=35)
A.hlines("wirebox", 0.06, 0.96, 4, 10)
A.rect("wirebox", 0.0, 0.0, 0.1, 1.0, (48, 40, 36)); A.rect("wirebox", 0.9, 0.0, 1.0, 1.0, (48, 40, 36))
A.fill("label", LABEL, amp=4, grad=4, speck=0.02, grime=0.15, seed=36); A.frame("label", 0, 0, 1, 1, (58, 48, 40))
A.text("label", 0.17, 0.25, "C-07", (40, 34, 30))
A.fill("plate", TRIM, amp=6, grad=6, speck=0.03, grime=0.15, seed=37); A.bevel("plate", 20, 26)
A.text("plate", 0.25, 0.06, "ON", (40, 32, 28)); A.text("plate", 0.09, 0.74, "OFF", (40, 32, 28))
A.rect("plate", 0.34, 0.36, 0.66, 0.62, (34, 28, 26), amp=0)
A.hazard("hazard", 0, 0, 1, 1, w=3)
for i in range(6):
    nm = "n%d" % (i + 1)
    A.fill(nm, LABEL, amp=3, grad=0, speck=0, grime=0, seed=40 + i)
    A.text(nm, 0.2, 0.15, str(i + 1), (40, 34, 30))

img = A.to_image(bpy, "T_" + N, os.path.join(TEX, "T_" + N + ".png"))
MAT = H.make_material(bpy, "M_" + N, img)

# 화면: P2와 같은 공용 화면 텍스처 (Assets/_Project/Textures/Common/T_COM_Screen_01.png)
SCR = H.Atlas(32).cell("scr", 0, 0, 32, 32)
scr_path = os.path.join(REPO, "Assets", "_Project", "Textures", "Common", "T_COM_Screen_01.png")
old = bpy.data.images.get("T_COM_Screen_01")
if old is not None:
    bpy.data.images.remove(old)
scr_img = bpy.data.images.load(scr_path)
scr_img.name = "T_COM_Screen_01"
SCR_MAT = H.make_material(bpy, "M_COM_Screen_01", scr_img, emissive=True)

# ================================================================ 본체 (움직이지 않는 부분)
m = H.Mesh()
m.box(-0.775, 0.775, -0.18, 0.0, 0.425, 1.975, "side", {"back": None})
m.box(-0.75, 0.75, YF, -0.18, 0.45, 1.95, "trim", {"front": "front", "back": None})
# 전선 박스 테두리 + 안쪽
frame_boxes(m, -0.68, -0.08, Z(0.23), Z(0.63), 0.02, -0.25, YF, "trim")
quad_front(m, -0.66, -0.10, Z(0.25), Z(0.61), YF - 0.0005, "wirebox")
# 단자 번호 1~6
for i, yb in enumerate(ROW_Y):
    quad_front(m, -0.057, -0.025, Z(yb) - 0.0225, Z(yb) + 0.0225, YF - 0.0006, "n%d" % (i + 1))
# 화면 테두리
frame_boxes(m, 0.08, 0.68, Z(0.29), Z(0.71), 0.04, -0.255, YF, "trim")
# 스위치 판
for sx in SWITCH_X:
    m.box(sx - 0.055, sx + 0.055, -0.23, YF, Z(-0.65), Z(-0.45), "trim", {"front": "plate", "back": None})
# 퓨즈 소켓 (받침 + 집게)
for fx in FUSE_X:
    m.box(fx - 0.06, fx + 0.06, -0.226, YF, Z(-0.60), Z(-0.50), "dark", {"back": None})
    for dx in (-0.034, 0.034):
        m.box(fx + dx - 0.008, fx + dx + 0.008, -0.258, -0.226, Z(-0.578), Z(-0.522), "clip", {"back": None})
# 위쪽 배관과 덕트, 아래쪽 접속함
m.cyl(-0.52, -0.09, 1.975, 2.40, 0.032, "pipe", cap=None, seg=6)
m.cyl(-0.40, -0.09, 1.975, 2.40, 0.032, "pipe", cap=None, seg=6)
m.box(0.28, 0.60, -0.16, -0.02, 1.975, 2.40, "side", {"top": None, "bottom": None})
m.box(-0.26, 0.26, -0.15, 0.0, 0.24, 0.425, "side", {"back": None, "top": None})
m.cyl(-0.13, -0.075, 0.0, 0.24, 0.036, "pipe", cap=None, seg=6)
m.cyl(0.13, -0.075, 0.0, 0.24, 0.036, "pipe", cap=None, seg=6)

body = H.build_object(bpy, sc, N, m, A, MAT)
objs, meshes = [body], [m]


def part(name, mesh, pivot, atlas=A, mat=MAT):
    o = H.build_object(bpy, sc, name, mesh, atlas, mat, parent=body, pivot=pivot)
    objs.append(o); meshes.append(mesh)
    return o


# ---- 화면 / 번호판
q = H.Mesh(); quad_front(q, 0.12, 0.64, Z(0.33), Z(0.67), -0.228, "scr")
part("Screen_Power", q, (0.38, -0.228, Z(0.50)), SCR, SCR_MAT)
q = H.Mesh(); quad_front(q, -0.66, -0.44, Z(0.63), Z(0.71), YF - 0.0015, "label")
part("Label_PanelNo", q, (-0.55, YF - 0.0015, Z(0.67)))

# ---- 단자
for i, yb in enumerate(ROW_Y):
    t = H.Mesh(); t.box(XR - 0.02, XR + 0.02, -0.26, YF, Z(yb) - 0.02, Z(yb) + 0.02, "term", {"back": None})
    part("Terminal_%d" % (i + 1), t, (XR, YF, Z(yb)))
for i in range(4):
    yb = ROW_Y[i]
    t = H.Mesh(); t.box(XL - 0.02, XL + 0.02, -0.26, YF, Z(yb) - 0.02, Z(yb) + 0.02, "term", {"back": None})
    part("Terminal_L_%02d" % (i + 1), t, (XL, YF, Z(yb)))

# ---- 전선 세트 A (엉킨 상태). 피벗은 왼쪽 끝
#   빨강: L1 -> 4번 / 파랑: L2 -> 1번 / 노랑: L3 -> 2번 / 주황: L4 에서 빠져서 늘어짐 (3, 5, 6번 단자는 비어 있음)
#   겹침 순서: 파랑(맨 아래) < 빨강 < 노랑(맨 위)  -> "빨간 선이 파란 선 위에 있어"
def wire_path(z0, z1, depth, sag):
    pts = [(XL, -0.262, z0)]
    for f in (0.14, 0.32, 0.5, 0.68, 0.86):
        t = f * f * (3 - 2 * f)
        x = XL + (XR - XL) * f
        pts.append((x, depth, z0 + (z1 - z0) * t - sag * math.sin(math.pi * f)))
    pts.append((XR, -0.262, z1))
    return pts

WIRES = (("Wire_Red", "w_red", 0, 3, -0.290, 0.012), ("Wire_Blue", "w_blue", 1, 0, -0.275, -0.010),
         ("Wire_Yellow", "w_yel", 2, 1, -0.305, 0.016))
for nm, cell, a, b, depth, sag in WIRES:
    w = H.Mesh()
    pipe(w, wire_path(Z(ROW_Y[a]), Z(ROW_Y[b]), depth, sag), 0.011, cell, seg=5)
    part(nm, w, (XL, -0.262, Z(ROW_Y[a])))
z3 = Z(ROW_Y[3])
w = H.Mesh()
pipe(w, [(XL, -0.262, z3), (XL + 0.07, -0.300, z3 - 0.012), (XL + 0.125, -0.312, Z(0.30)),
         (XL + 0.145, -0.305, Z(0.21)), (XL + 0.138, -0.288, Z(0.135))], 0.011, "w_org", seg=5)
c = H.Mesh(); c.box(XL + 0.127, XL + 0.149, -0.298, -0.278, Z(0.105), Z(0.135), "term")
w.V += c.V; off = len(w.V) - len(c.V)
for f, r, u in zip(c.F, c.R, c.U):
    w.face([i + off for i in f], r, u)
part("Wire_Orange", w, (XL, -0.262, z3))

# ---- 노브 (회전축 = 벽에 수직인 축)
for i, kx in enumerate(KNOB_X):
    k = H.Mesh(); ycyl(k, kx, Z(0.05), YF, 0.05, 0.06, "knobside", "knob", seg=8, r1=0.05)
    part("Knob_%02d" % (i + 1), k, (kx, YF, Z(0.05)))

# ---- 슬라이더 손잡이 (위아래 이동 범위 약 ±0.165)
for i, sx in enumerate(SLIDER_X):
    s = H.Mesh(); z = Z(-0.15)
    s.box(sx - 0.045, sx + 0.045, -0.272, YF, z - 0.0225, z + 0.0225, "handle", {"back": None})
    part("Slider_%02d" % (i + 1), s, (sx, YF, z))

# ---- 스위치 레버 (피벗 = 판 표면, X축 회전: + 아래(OFF), - 위(ON))
for i, sx in enumerate(SWITCH_X):
    l = H.Mesh(); z = Z(-0.55)
    l.box(sx - 0.015, sx + 0.015, -0.30, -0.23, z - 0.015, z + 0.015, "lever", {"back": None})
    o = part("Switch_%02d" % (i + 1), l, (sx, -0.23, z))
    o.rotation_euler = (R(25), 0, 0)

# ---- 퓨즈
for i, fx in enumerate(FUSE_X):
    f = H.Mesh(); xcyl(f, fx, -0.244, Z(-0.55), 0.09, 0.015, "fuse", "fusecap", seg=6)
    part("Fuse_%02d" % (i + 1), f, (fx, -0.244, Z(-0.55)))

# ---- 전력 표시등
for i, (lx, cell) in enumerate(zip(LAMP_X, ("lamp_g", "lamp_a", "lamp_r"))):
    l = H.Mesh(); ycyl(l, lx, Z(0.22), YF, 0.02, 0.028, cell, cell, seg=6, r1=0.022)
    part("Light_Power_%02d" % (i + 1), l, (lx, YF, Z(0.22)))

# ================================================================ 내보내기 + 정리
col = bpy.data.collections.get(N)
if col is None:
    col = bpy.data.collections.new(N); sc.collection.children.link(col)
for o in objs:
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
bpy.context.view_layer.update()

fbx = os.path.join(MOD, N + ".fbx")
H.export_fbx(bpy, win, sc, objs, fbx)

report = {"name": N, "tris": sum(mm.tris() for mm in meshes), "body_tris": m.tris(), "objects": len(objs),
          "dims": [round(v, 3) for v in body.dimensions], "fbx": fbx, "fbx_bytes": os.path.getsize(fbx),
          "texture": os.path.join(TEX, "T_" + N + ".png"), "parts": [o.name for o in objs[1:]]}
with open(os.path.join(OUT, N + "_report.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
print(json.dumps(report))

if PLACE_IN_CABIN:
    body.location = (1.6, 0.0, 0.0)
    body.rotation_euler = (0, 0, R(-90))
for o in objs:
    o.select_set(False)
