"""HOUSTON P1 - 3면 시스템 PC (P1_SystemPC_01). Blender 안에서 실행.
P2 팀의 houston_lib.py (ArtSource/P2/_tools) 를 그대로 사용한다.
규칙: 1 단위 = 1 m, 앞면은 -Y, 벽에 붙는 면이 y = 0, 바닥이 z = 0, 피벗은 바닥 중앙.
Unity 배치: Position (0, 0, -1.6), Rotation (0, 0, 0) 이면 블록아웃 3면과 겹친다.
책상 위 부품(코드 칸, 키패드, 상태등, 재시작 버튼)은 조작판 기울기(40도)에 맞춰 회전돼 있다.
  -> 부품의 로컬 +Y = 조작판 안쪽(누르는 방향), 로컬 Z = 조작판 위쪽
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
N = "P1_SystemPC_01"
PLACE_IN_CABIN = True
R = math.radians

# ---------------- 치수 (블록아웃과 동일)
W = 1.7                          # 콘솔 폭
TILT = 40.0
CU = (math.sin(R(TILT)), math.cos(R(TILT)))
CN = (-math.cos(R(TILT)), math.sin(R(TILT)))
PF = (-0.36 + 0.02 * CN[0], 1.10 + 0.02 * CN[1])
DESK_H = 0.5
UPW, UPH, UPZ, UPD = 1.2, 0.5, 1.80, 0.12        # 위쪽 벽 패널: 폭, 높이, 중심 높이, 깊이

COLS = (-0.30, -0.20, -0.10, 0.0)                # 코드 칸 / 키패드 열
ROWS = (0.02, -0.08, -0.18)                      # 키패드 행
LX = 0.22                                        # 상태등 x
LIGHTS = (("Light_Power", "PWR", 0.14), ("Light_Comm", "COMM", 0.05),
          ("Light_Camera", "CAM", -0.04), ("Light_Move", "MOVE", -0.13))
RX = 0.65                                        # 재시작 버튼 x

# ---------------- palette (다른 면과 동일)
RUST = (120, 82, 60); RUST_D = (66, 44, 34); DARKPL = (58, 44, 38); SLOT = (20, 16, 14)
TRIM = (142, 114, 92); DARK = (42, 34, 30); TXT = (216, 198, 162); INK = (40, 32, 28)
KEYG = (150, 146, 136); RED = (194, 52, 40)

# ================================================================ atlas (128px)
A = H.Atlas(128)
A.cell("desk", 0, 0, 128, 40).cell("upper", 0, 40, 96, 80).cell("basefront", 0, 80, 64, 118)
KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "C", "E"]
for i, k in enumerate(KEYS):
    A.cell("key_" + k, 64 + 8 * (i % 8), 80 + 8 * (i // 8), 72 + 8 * (i % 8), 88 + 8 * (i // 8))
A.cell("side", 96, 40, 112, 56).cell("cheek", 112, 40, 128, 56)
A.cell("trim", 96, 56, 104, 64).cell("dark", 104, 56, 112, 64).cell("bezel", 112, 56, 120, 64).cell("pipe", 120, 56, 128, 64)
A.cell("keyside2", 96, 64, 104, 72).cell("digit", 104, 64, 112, 72).cell("lamp_r", 112, 64, 120, 72).cell("redbtn", 120, 64, 128, 72)
A.cell("redside", 96, 72, 104, 80).cell("collar", 104, 72, 112, 80)


def rust(name, seed=0, amount=0.3, col=(150, 82, 36)):
    x0, y0, x1, y1 = A.cells[name]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    n = H._hash(xx // 3, yy // 3, seed) * 0.6 + H._hash(xx // 7 + 3, yy // 7 + 1, seed + 5) * 0.4
    m = n > (1 - amount)
    v = A.A[y0:y1, x0:x1, :3]
    v[m] = v[m] * 0.6 + np.array(col, float) * 0.4
    m2 = n < amount * 0.35
    v[m2] = v[m2] * 0.72


def bolts(name, pts):
    for bx, by in pts:
        A.dot(name, bx, by, (182, 156, 126), 2)
        A.dot(name, bx + 0.008, by + 0.03, (52, 36, 28), 1)


# ---- 책상 조작판 (128 x 40 = 1.7 m x 0.5 m)
def DX(x): return (x + W / 2) / W
def DY(sz): return (DESK_H / 2 - sz) / DESK_H
def drect(x0, x1, z0, z1, c, amp=6): A.rect("desk", DX(x0), DY(z1), DX(x1), DY(z0), c, amp=amp)
def dframe(x0, x1, z0, z1, c): A.frame("desk", DX(x0), DY(z1), DX(x1), DY(z0), c)

A.fill("desk", RUST, amp=9, grad=8, speck=0.06, grime=0.25, seed=91)
rust("desk", seed=21, amount=0.28)
A.bevel("desk", 22, 26)
A.hazard("desk", 0.0, 0.93, 1.0, 1.0, w=3)
bolts("desk", [(0.008, 0.06), (0.985, 0.06), (0.008, 0.8), (0.985, 0.8)])
# 오류 화면 구역
drect(-0.81, -0.43, -0.16, 0.16, DARKPL); dframe(-0.81, -0.43, -0.16, 0.16, RUST_D)
# 코드 + 키패드 구역
drect(-0.37, 0.07, -0.235, 0.205, DARKPL); dframe(-0.37, 0.07, -0.235, 0.205, RUST_D)
A.shade("desk", DX(-0.37), DY(0.095), DX(0.07), DY(0.09), -30)            # 코드 칸 / 키패드 구분선
# 상태등 구역
drect(0.15, 0.48, -0.18, 0.18, DARKPL); dframe(0.15, 0.48, -0.18, 0.18, RUST_D)
for nm, lab, sz in LIGHTS:
    A.circle("desk", DX(LX), DY(sz), 0.036 / W, DARK)
    A.text("desk", DX(0.27), DY(sz + 0.031), lab, TXT)
# 재시작 버튼 구역 (경고 줄무늬 테두리)
A.hazard("desk", DX(RX - 0.13), DY(0.13), DX(RX + 0.13), DY(-0.13), w=3)
drect(RX - 0.105, RX + 0.105, -0.105, 0.105, DARK, amp=3)
A.text("desk", DX(RX - 0.155), DY(-0.142), "REBOOT", TXT)
for sx in (-0.42, 0.11, 0.50):
    A.shade("desk", DX(sx), 0.08, DX(sx) + 0.008, 0.9, -28)

# ---- 위쪽 벽 패널 (96 x 40 = 1.2 m x 0.5 m): 환풍구 + 이름판
def UX(x): return (x + UPW / 2) / UPW
def UY(zl): return (UPH / 2 - zl) / UPH
A.fill("upper", RUST, amp=9, grad=10, speck=0.06, grime=0.3, seed=92)
rust("upper", seed=22, amount=0.32)
A.bevel("upper", 22, 26)
bolts("upper", [(0.015, 0.07), (0.975, 0.07), (0.015, 0.86), (0.975, 0.86)])
A.rect("upper", UX(-0.52), UY(0.17), UX(0.10), UY(-0.17), DARKPL, amp=4)       # 환풍구
A.hlines("upper", UY(0.15), UY(-0.15), 2, -34, UX(-0.50), UX(0.08))
A.rect("upper", UX(0.18), UY(0.12), UX(0.52), UY(0.01), (206, 198, 172), amp=3)  # 이름판
A.frame("upper", UX(0.18), UY(0.12), UX(0.52), UY(0.01), (58, 48, 40))
A.text("upper", UX(0.205), UY(0.098), "SYSTEM", INK)
A.hazard("upper", UX(0.18), UY(-0.06), UX(0.52), UY(-0.16), w=3)

# ---- 받침 앞면 (64 x 38 = 1.7 m x 0.87 m)
A.fill("basefront", RUST, amp=9, grad=12, speck=0.05, grime=0.45, seed=93)
rust("basefront", seed=23, amount=0.33)
A.bevel("basefront", 20, 24)
A.rect("basefront", 0.08, 0.16, 0.92, 0.5, DARKPL, amp=4)
A.hlines("basefront", 0.2, 0.47, 2, -26, 0.11, 0.89)
A.hazard("basefront", 0.0, 0.88, 1.0, 1.0, w=3)
A.vlines("basefront", 0.5, 0.505, 1, -26, 0.55, 0.86)
A.dot("basefront", 0.04, 0.05, (182, 156, 126), 1).dot("basefront", 0.94, 0.05, (182, 156, 126), 1)

# ---- 작은 셀
A.fill("side", RUST, amp=9, grad=8, speck=0.05, grime=0.4, seed=94); rust("side", seed=24, amount=0.35); A.bevel("side", 18, 22)
A.fill("cheek", (104, 72, 54), amp=8, grad=10, speck=0.05, grime=0.4, seed=95); rust("cheek", seed=25, amount=0.3); A.bevel("cheek", 16, 20)
A.fill("trim", TRIM, amp=8, grad=6, speck=0.04, grime=0.25, seed=96); A.bevel("trim", 18, 20)
A.fill("bezel", (88, 80, 72), amp=6, grad=8, speck=0.02, grime=0.1, seed=97); A.bevel("bezel", 20, 24)
A.fill("dark", DARK, amp=5, grad=4, speck=0.02, grime=0.2, seed=98)
A.fill("collar", (60, 54, 50), amp=5, grad=10, speck=0.02, grime=0.1, seed=99)
A.fill("pipe", (70, 58, 52), amp=6, grad=0, speck=0.03, grime=0, seed=100); A.hlines("pipe", 0, 1, 3, -18)
A.fill("keyside2", (104, 100, 94), amp=4, grad=10, speck=0, grime=0, seed=101)
A.fill("redside", (128, 36, 30), amp=4, grad=10, speck=0, grime=0, seed=102)
# 코드 칸: 어두운 초록 유리 + 가운데 대시 (숫자는 Unity UI/텍스트로 올림)
A.fill("digit", (16, 34, 22), amp=3, grad=8, speck=0, grime=0, seed=103); A.frame("digit", 0, 0, 1, 1, (8, 16, 10))
A.rect("digit", 0.3, 0.45, 0.7, 0.58, (60, 150, 80), amp=0)
A.fill("lamp_r", RED, amp=6, grad=20, speck=0, grime=0, seed=104); A.frame("lamp_r", 0, 0, 1, 1, (110, 30, 24)); A.dot("lamp_r", 0.3, 0.3, (255, 236, 226), 2)
A.fill("redbtn", (206, 48, 38), amp=4, grad=18, speck=0, grime=0, seed=105)
A.circle("redbtn", 0.5, 0.5, 0.36, (150, 30, 24), ring=0.08); A.dot("redbtn", 0.32, 0.3, (255, 200, 190), 2)
for k in KEYS:
    nm = "key_" + k
    A.fill(nm, KEYG, amp=4, grad=10, speck=0, grime=0, seed=106)
    A.bevel(nm, 24, 30)
    A.text(nm, 0.3, 0.2, k, INK)

img = A.to_image(bpy, "T_" + N, os.path.join(TEX, "T_" + N + ".png"))
MAT = H.make_material(bpy, "M_" + N, img)

SCR = H.Atlas(32).cell("scr", 0, 0, 32, 32)
scr_path = os.path.join(REPO, "Assets", "_Project", "Textures", "Common", "T_COM_Screen_01.png")
old = bpy.data.images.get("T_COM_Screen_01")
if old is not None:
    bpy.data.images.remove(old)
scr_img = bpy.data.images.load(scr_path); scr_img.name = "T_COM_Screen_01"
SCR_MAT = H.make_material(bpy, "M_COM_Screen_01", scr_img, emissive=True)


# ================================================================ 도우미
def quad_front(m, x0, x1, z0, z1, y, role):
    b = len(m.V)
    m.V += [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    m.face([b, b + 1, b + 2, b + 3], role, [(0, 0), (1, 0), (1, 1), (0, 1)])


def frame_boxes(m, x0, x1, z0, z1, t, y0, y1, role):
    ov = {"back": None}
    m.box(x0, x0 + t, y0, y1, z0, z1, role, dict(ov))
    m.box(x1 - t, x1, y0, y1, z0, z1, role, dict(ov))
    m.box(x0 + t, x1 - t, y0, y1, z1 - t, z1, role, dict(ov))
    m.box(x0 + t, x1 - t, y0, y1, z0, z0 + t, role, dict(ov))


def ycyl(m, cx, cz, yback, depth, r, side, cap, seg=8, r1=None):
    start = len(m.V)
    m.cyl(0, 0, 0, depth, r, side, cap=cap, seg=seg, r1=r1, caps=(False, True), rot=math.pi / seg)
    m.xform(H.mul(H.trans(cx, yback, cz), H.rot_x(math.pi / 2)), start)


DESK_M = H.mul(H.trans(0, PF[0], PF[1]), H.rot_x(-R(TILT)))


def desk_point(x, y, z):
    v = np.array(DESK_M) @ np.array([x, y, z, 1.0])
    return tuple(v[:3])


# ================================================================ 본체
m = H.Mesh()
bot = (PF[0] - DESK_H / 2 * CU[0], PF[1] - DESK_H / 2 * CU[1])
top = (PF[0] + DESK_H / 2 * CU[0], PF[1] + DESK_H / 2 * CU[1])
prof = [(0.0, 0.0), (-0.6, 0.0), (-0.6, 0.87), bot, top, (0.0, top[1])]
m.extrude_profile(prof, -W / 2, W / 2, "side", cap="cheek", closed=True)
quad_front(m, -W / 2, W / 2, 0.0, 0.87, -0.6005, "basefront")
s0 = len(m.V)
quad_front(m, -W / 2, W / 2, -DESK_H / 2, DESK_H / 2, -0.0006, "desk")
frame_boxes(m, -0.79, -0.45, -0.135, 0.135, 0.03, -0.03, 0.0, "trim")       # 오류 화면 테두리
ycyl(m, RX, 0.0, 0.0, 0.02, 0.095, "collar", "collar", seg=12)             # 재시작 버튼 받침
m.xform(DESK_M, s0)
m.box(-W / 2 + 0.02, W / 2 - 0.02, -0.62, -0.6, 0.0, 0.07, "dark", {"back": None})   # 발판 홈

# 위쪽 벽 패널 + 배관
m.box(-UPW / 2, UPW / 2, -UPD, 0.0, UPZ - UPH / 2, UPZ + UPH / 2, "side", {"front": "upper", "back": None})
for px in (-0.45, -0.35):
    m.cyl(px, -0.07, UPZ + UPH / 2, 2.40, 0.03, "pipe", cap=None, seg=6)
m.box(0.25, 0.50, -0.11, -0.02, UPZ + UPH / 2, 2.40, "side", {"top": None, "bottom": None})
m.cyl(0.74, -0.06, top[1], 2.40, 0.03, "pipe", cap=None, seg=6)           # 콘솔에서 천장까지 케이블관

body = H.build_object(bpy, sc, N, m, A, MAT)
objs, meshes = [body], [m]


def add(name, mesh, pivot, atlas=A, mat=MAT, rot_x=0.0, loc=None):
    o = H.build_object(bpy, sc, name, mesh, atlas, mat, parent=body, pivot=pivot)
    if loc is not None:
        o.location = loc
    o.rotation_euler = (R(rot_x), 0, 0)
    objs.append(o); meshes.append(mesh)
    return o


def desk_part(name, mesh_fn, sx, sz, atlas=A, mat=MAT):
    q = H.Mesh(); mesh_fn(q)
    return add(name, q, (sx, 0.0, sz), atlas, mat, rot_x=-TILT, loc=desk_point(sx, 0.0, sz))


# ---- 오류 화면 (임시 공용 화면 텍스처)
desk_part("Screen_Error", lambda q: quad_front(q, -0.76, -0.48, -0.105, 0.105, -0.002, "scr"), -0.62, 0.0, SCR, SCR_MAT)

# ---- 코드 표시 칸 4개
for i, sx in enumerate(COLS):
    desk_part("CodeDigit_%02d" % (i + 1), lambda q, sx=sx: q.box(sx - 0.035, sx + 0.035, -0.012, 0.0, 0.15 - 0.032, 0.15 + 0.032, "dark",
                                                                 {"front": "digit", "back": None}), sx, 0.15)

# ---- 키패드 (1~9, 0, C, E)
ORDER = [("Key_1", "1"), ("Key_2", "2"), ("Key_3", "3"), ("Key_4", "4"), ("Key_5", "5"), ("Key_6", "6"),
         ("Key_7", "7"), ("Key_8", "8"), ("Key_9", "9"), ("Key_0", "0"), ("Key_Clear", "C"), ("Key_Enter", "E")]
for i, (nm, k) in enumerate(ORDER):
    sx = COLS[i % 4]; sz = ROWS[i // 4]
    desk_part(nm, lambda q, sx=sx, sz=sz, k=k: q.box(sx - 0.036, sx + 0.036, -0.026, 0.0, sz - 0.036, sz + 0.036, "keyside2",
                                                      {"front": "key_" + k, "back": None}), sx, sz)

# ---- 상태등 4개 (전력 / 통신 / 카메라 / 이동)
for nm, lab, sz in LIGHTS:
    desk_part(nm, lambda q, sz=sz: ycyl(q, LX, sz, 0.0, 0.025, 0.03, "lamp_r", "lamp_r", seg=8, r1=0.024), LX, sz)

# ---- 재시작 버튼
desk_part("Button_Restart", lambda q: ycyl(q, RX, 0.0, -0.02, 0.04, 0.075, "redside", "redbtn", seg=12, r1=0.068), RX, 0.0)

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
          "dims": [round(v, 3) for v in body.dimensions], "fbx_bytes": os.path.getsize(fbx), "parts": [o.name for o in objs[1:]]}
with open(os.path.join(OUT, N + "_report.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
print(json.dumps(report))

if PLACE_IN_CABIN:
    body.location = (0.0, 1.6, 0.0)
    body.rotation_euler = (0, 0, 0)
for o in objs:
    o.select_set(False)
