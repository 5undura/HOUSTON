"""HOUSTON P1 - 2면 외부 카메라 + 센서 (P1_CameraPanel_01). Blender 안에서 실행.
P2 팀의 houston_lib.py (ArtSource/P2/_tools) 를 그대로 사용한다.
규칙: 1 단위 = 1 m, 앞면은 -Y, 벽에 붙는 면이 y = 0, 바닥이 z = 0, 피벗은 바닥 중앙.
Unity 배치: Position (1.6, 0, 0), Rotation (0, 270, 0) 이면 블록아웃 2면과 겹친다.
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
N = "P1_CameraPanel_01"
PLACE_IN_CABIN = True
R = math.radians

PW, PH, ZC = 1.5, 1.3, 1.25      # 패널 폭, 높이, 중심 높이
YF = -0.22                       # 조작판 앞면
CX, SX = -0.32, 0.42             # 왼쪽 열(카메라), 오른쪽 열(센서)
def Z(zb): return ZC + zb

RUST = (120, 82, 60); RUST_D = (66, 44, 34); DARKPL = (58, 44, 38); SLOT = (20, 16, 14)
TRIM = (142, 114, 92); DARK = (42, 34, 30); TXT = (216, 198, 162); INK = (40, 32, 28)
GREEN = (96, 214, 110); AMBER = (228, 158, 44); RED = (194, 52, 40); WHITE = (232, 226, 210)

# ================================================================ atlas (128px)
A = H.Atlas(128)
A.cell("front", 0, 0, 96, 84)
A.cell("side", 96, 0, 128, 32).cell("trim", 96, 32, 112, 48).cell("dark", 112, 32, 128, 48)
A.cell("shoot", 96, 48, 112, 56).cell("delete", 112, 48, 128, 56)
A.cell("ar_u", 96, 56, 104, 64).cell("ar_d", 104, 56, 112, 64).cell("ar_l", 112, 56, 120, 64).cell("ar_r", 120, 56, 128, 64)
A.cell("keyside", 96, 64, 104, 72).cell("redside", 104, 64, 112, 72).cell("scan", 112, 64, 120, 72).cell("lamp_g", 120, 64, 128, 72)
A.cell("lamp_a", 96, 72, 104, 80).cell("lamp_r", 104, 72, 112, 80).cell("pipe", 112, 72, 120, 80).cell("scanside", 120, 72, 128, 80)


def rust(name, seed=0, amount=0.3, col=(150, 82, 36)):
    x0, y0, x1, y1 = A.cells[name]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    n = H._hash(xx // 3, yy // 3, seed) * 0.6 + H._hash(xx // 7 + 3, yy // 7 + 1, seed + 5) * 0.4
    m = n > (1 - amount)
    v = A.A[y0:y1, x0:x1, :3]
    v[m] = v[m] * 0.6 + np.array(col, float) * 0.4
    v[n < amount * 0.35] *= 0.72


def FX(x): return (x + PW / 2) / PW
def FY(zb): return (PH / 2 - zb) / PH
def frect(x0, x1, z0, z1, c, amp=6): A.rect("front", FX(x0), FY(z1), FX(x1), FY(z0), c, amp=amp)
def fframe(x0, x1, z0, z1, c): A.frame("front", FX(x0), FY(z1), FX(x1), FY(z0), c)

# ---- 앞판 (96 x 84 = 1.5 m x 1.3 m)
A.fill("front", RUST, amp=10, grad=10, speck=0.06, grime=0.35, seed=71)
rust("front", seed=12, amount=0.3)
A.bevel("front", 22, 26)
A.frame("front", 0.03, 0.035, 0.97, 0.965, RUST_D)
for bx in (0.055, 0.5, 0.925):
    for by in (0.06, 0.92):
        A.dot("front", bx, by, (182, 156, 126), 2)
        A.dot("front", bx + 0.011, by + 0.012, (52, 36, 28), 1)
A.shade("front", FX(0.04), 0.06, FX(0.04) + 0.012, 0.94, -30)          # 가운데 이음매
frect(CX - 0.40, CX + 0.40, 0.03, 0.63, DARKPL)                          # 카메라 화면 뒤 홈
frect(SX - 0.27, SX + 0.27, 0.19, 0.61, DARKPL)                          # 센서 화면 뒤 홈
frect(SX - 0.27, SX + 0.27, -0.555, -0.165, DARKPL)                      # 탐사 데이터 화면 뒤 홈
A.circle("front", FX(CX), FY(-0.37), 0.205 / PW, DARKPL)                 # 방향 버튼 받침
A.circle("front", FX(CX), FY(-0.37), 0.205 / PW, (84, 62, 50), ring=0.012)
A.text("front", FX(-0.70), FY(-0.34), "CAM", TXT)
for i in range(3):                                                       # 표시등 자리
    A.circle("front", FX(SX - 0.12 + i * 0.12), FY(0.15), 0.044 / PW, DARK)
A.text("front", FX(0.10), FY(-0.02), "SCAN", TXT)
A.circle("front", FX(SX), FY(-0.05), 0.092 / PW, DARK)
A.hazard("front", 0.04, 0.935, 0.96, 0.96, w=3)

# ---- 작은 셀
A.fill("side", RUST, amp=9, grad=8, speck=0.05, grime=0.4, seed=72); rust("side", seed=13, amount=0.35); A.bevel("side", 18, 22)
A.fill("trim", TRIM, amp=8, grad=6, speck=0.04, grime=0.25, seed=73); A.bevel("trim", 18, 20)
A.fill("dark", DARK, amp=5, grad=4, speck=0.02, grime=0.2, seed=74)
A.fill("pipe", (70, 58, 52), amp=6, grad=0, speck=0.03, grime=0, seed=75); A.hlines("pipe", 0, 1, 3, -18)
A.fill("keyside", (60, 56, 52), amp=4, grad=10, speck=0, grime=0, seed=76)
A.fill("redside", (128, 36, 30), amp=4, grad=10, speck=0, grime=0, seed=77)
A.fill("scanside", (150, 104, 30), amp=4, grad=10, speck=0, grime=0, seed=78)
# 촬영 버튼 (카메라 아이콘)
A.fill("shoot", (58, 56, 54), amp=4, grad=12, speck=0, grime=0, seed=79); A.bevel("shoot", 26, 30)
A.rect("shoot", 0.31, 0.3, 0.69, 0.78, WHITE, amp=0); A.rect("shoot", 0.38, 0.17, 0.5, 0.3, WHITE, amp=0)
A.rect("shoot", 0.44, 0.42, 0.56, 0.66, (58, 56, 54), amp=0)
# 삭제 버튼 (휴지통 아이콘)
A.fill("delete", (176, 46, 38), amp=4, grad=12, speck=0, grime=0, seed=80); A.bevel("delete", 26, 30)
A.rect("delete", 0.34, 0.18, 0.66, 0.3, WHITE, amp=0); A.rect("delete", 0.38, 0.36, 0.62, 0.84, WHITE, amp=0)
A.rect("delete", 0.47, 0.42, 0.53, 0.76, (176, 46, 38), amp=0)
# 방향 버튼 (화살표)
for nm in ("ar_u", "ar_d", "ar_l", "ar_r"):
    A.fill(nm, (52, 50, 48), amp=4, grad=12, speck=0, grime=0, seed=81); A.bevel(nm, 26, 30)
for i, (a, b) in enumerate(((0.375, 0.625), (0.25, 0.75), (0.125, 0.875))):
    t0, t1 = 0.25 + i * 0.15, 0.4 + i * 0.15
    A.rect("ar_u", a, t0, b, t1, WHITE, amp=0)
    A.rect("ar_d", a, 1 - t1, b, 1 - t0, WHITE, amp=0)
    A.rect("ar_l", t0, a, t1, b, WHITE, amp=0)
    A.rect("ar_r", 1 - t1, a, 1 - t0, b, WHITE, amp=0)
# 스캔 버튼 (레이더 아이콘)
A.fill("scan", AMBER, amp=4, grad=16, speck=0, grime=0, seed=82)
A.circle("scan", 0.5, 0.5, 0.42, (120, 70, 16), ring=0.12); A.dot("scan", 0.45, 0.45, (120, 70, 16), 1)
for nm, c in (("lamp_g", GREEN), ("lamp_a", AMBER), ("lamp_r", RED)):
    A.fill(nm, c, amp=6, grad=20, speck=0, grime=0, seed=83); A.frame(nm, 0, 0, 1, 1, tuple(int(v * 0.55) for v in c))
    A.dot(nm, 0.3, 0.3, (255, 250, 236), 2)

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


# ================================================================ 본체
m = H.Mesh()
m.box(-PW / 2 - 0.025, PW / 2 + 0.025, -0.18, 0.0, Z(-PH / 2) - 0.025, Z(PH / 2) + 0.025, "side", {"back": None})
m.box(-PW / 2, PW / 2, YF, -0.18, Z(-PH / 2), Z(PH / 2), "trim", {"front": "front", "back": None})
frame_boxes(m, CX - 0.36, CX + 0.36, Z(0.07), Z(0.59), 0.05, YF - 0.04, YF, "trim")       # 카메라 화면 테두리
frame_boxes(m, SX - 0.24, SX + 0.24, Z(0.22), Z(0.58), 0.04, YF - 0.03, YF, "trim")       # 센서 화면 테두리
frame_boxes(m, SX - 0.24, SX + 0.24, Z(-0.52), Z(-0.20), 0.04, YF - 0.03, YF, "trim")     # 탐사 데이터 화면 테두리
m.box(CX - 0.05, CX + 0.05, YF - 0.03, YF, Z(-0.42), Z(-0.32), "keyside", {"back": None})  # 방향 버튼 가운데
# 위쪽 카메라 케이블 배관 + 덕트
m.cyl(-0.55, -0.09, Z(PH / 2) + 0.025, 2.40, 0.035, "pipe", cap=None, seg=6)
m.box(0.10, 0.36, -0.15, -0.02, Z(PH / 2) + 0.025, 2.40, "side", {"top": None, "bottom": None})
m.cyl(0.55, -0.08, 0.0, Z(-PH / 2) - 0.025, 0.03, "pipe", cap=None, seg=6)

body = H.build_object(bpy, sc, N, m, A, MAT)
objs, meshes = [body], [m]


def part(name, mesh, pivot, atlas=A, mat=MAT):
    o = H.build_object(bpy, sc, name, mesh, atlas, mat, parent=body, pivot=pivot)
    objs.append(o); meshes.append(mesh)
    return o


# ---- 화면 (임시 공용 화면 텍스처. UI가 들어갈 자리)
for nm, x, zb, w, h in (("Screen_Camera", CX, 0.33, 0.62, 0.42), ("Screen_Sensor", SX, 0.40, 0.40, 0.28),
                        ("Screen_ScanData", SX, -0.36, 0.40, 0.24)):
    q = H.Mesh(); quad_front(q, x - w / 2, x + w / 2, Z(zb) - h / 2, Z(zb) + h / 2, YF - 0.002, "scr")
    part(nm, q, (x, YF - 0.002, Z(zb)), SCR, SCR_MAT)

# ---- 촬영 / 삭제
for nm, x, cell, side in (("Button_Shoot", CX - 0.15, "shoot", "keyside"), ("Button_Delete", CX + 0.15, "delete", "redside")):
    q = H.Mesh(); z = Z(-0.05)
    q.box(x - 0.105, x + 0.105, YF - 0.045, YF, z - 0.047, z + 0.047, side, {"front": cell, "back": None})
    part(nm, q, (x, YF, z))

# ---- 카메라 방향 버튼
for nm, dx, zb, cell in (("Button_Up", 0.0, -0.25, "ar_u"), ("Button_Down", 0.0, -0.49, "ar_d"),
                         ("Button_Left", -0.12, -0.37, "ar_l"), ("Button_Right", 0.12, -0.37, "ar_r")):
    q = H.Mesh(); x = CX + dx; z = Z(zb)
    q.box(x - 0.047, x + 0.047, YF - 0.045, YF, z - 0.047, z + 0.047, "keyside", {"front": cell, "back": None})
    part(nm, q, (x, YF, z))

# ---- 센서 표시등 (초록 / 주황 / 빨강)
for i, cell in enumerate(("lamp_g", "lamp_a", "lamp_r")):
    q = H.Mesh(); x = SX - 0.12 + i * 0.12
    ycyl(q, x, Z(0.15), YF, 0.02, 0.028, cell, cell, seg=6, r1=0.022)
    part("Light_Sensor_%02d" % (i + 1), q, (x, YF, Z(0.15)))

# ---- 스캔 버튼
q = H.Mesh(); ycyl(q, SX, Z(-0.05), YF, 0.05, 0.07, "scanside", "scan", seg=10, r1=0.062)
part("Button_Scan", q, (SX, YF, Z(-0.05)))

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
    body.location = (-1.6, 0.0, 0.0)
    body.rotation_euler = (0, 0, R(90))
for o in objs:
    o.select_set(False)
