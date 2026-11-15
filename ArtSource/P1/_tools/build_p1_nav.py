"""HOUSTON P1 - 1면 조종 장치 (P1_NavConsole_01). Blender 안에서 실행.
P2 팀의 houston_lib.py (ArtSource/P2/_tools) 를 그대로 사용한다.
규칙: 1 단위 = 1 m, 앞면은 -Y, 벽에 붙는 면이 y = 0, 바닥이 z = 0, 피벗은 바닥 중앙.
Unity 배치: Position (0, 0, 1.6), Rotation (0, 180, 0) 이면 블록아웃 1면과 겹친다.
책상 위 부품(키패드, 동서남북 버튼, 상태등)은 조작판 기울기(40도)에 맞춰 회전돼 있다.
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
N = "P1_NavConsole_01"
PLACE_IN_CABIN = True
R = math.radians

# ---------------- 치수 (블록아웃과 동일)
W = 1.6                          # 콘솔 폭
TILT = 40.0                      # 조작판 기울기
CU = (math.sin(R(TILT)), math.cos(R(TILT)))      # 조작판 위쪽 방향 (y, z)
CN = (-math.cos(R(TILT)), math.sin(R(TILT)))     # 조작판 법선 (플레이어 쪽)
PF = (-0.36 + 0.02 * CN[0], 1.10 + 0.02 * CN[1]) # 조작판 앞면 중심 (y, z)
DESK_H = 0.5
UPZ, UPH, UPD = 1.68, 0.62, 0.14                 # 위쪽 화면 패널: 중심 높이, 높이, 벽에서 앞면까지
UF = -UPD

# ---------------- palette (4면과 동일)
RUST = (120, 82, 60); RUST_D = (66, 44, 34); DARKPL = (58, 44, 38); SLOT = (20, 16, 14)
TRIM = (142, 114, 92); DARK = (42, 34, 30); BEIGE = (198, 178, 140); TXT = (216, 198, 162)
GREEN = (96, 214, 110); KEYG = (150, 146, 136); INK = (40, 32, 28); STEEL = (110, 104, 98)

# ================================================================ atlas (128px)
A = H.Atlas(128)
A.cell("desk", 0, 0, 128, 40).cell("upper", 0, 40, 128, 90).cell("basefront", 0, 90, 64, 128)
KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "C", "E", "N", "S", "W", "E2"]
for i, k in enumerate(KEYS):
    A.cell("key_" + k, 64 + 8 * (i % 8), 90 + 8 * (i // 8), 72 + 8 * (i % 8), 98 + 8 * (i // 8))
A.cell("side", 64, 106, 80, 122).cell("cheek", 80, 106, 96, 122)
A.cell("trim", 96, 106, 104, 114).cell("dark", 104, 106, 112, 114).cell("lamp_g", 112, 106, 120, 114).cell("keyside", 120, 106, 128, 114)
A.cell("bezel", 96, 114, 104, 122).cell("pipe", 104, 114, 112, 122).cell("keyside2", 112, 114, 120, 122)


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


# ---- 책상 조작판 (128 x 40 = 1.6 m x 0.5 m)
def DX(x): return (x + W / 2) / W
def DY(sz): return (DESK_H / 2 - sz) / DESK_H
def drect(x0, x1, z0, z1, c, amp=6): A.rect("desk", DX(x0), DY(z1), DX(x1), DY(z0), c, amp=amp)
def dframe(x0, x1, z0, z1, c): A.frame("desk", DX(x0), DY(z1), DX(x1), DY(z0), c)

A.fill("desk", RUST, amp=9, grad=8, speck=0.06, grime=0.25, seed=51)
rust("desk", seed=4, amount=0.28)
A.bevel("desk", 22, 26)
A.hazard("desk", 0.0, 0.93, 1.0, 1.0, w=3)
bolts("desk", [(0.012, 0.06), (0.975, 0.06), (0.012, 0.8), (0.975, 0.8)])
# 항로 입력 구역
drect(-0.665, -0.245, -0.215, 0.225, DARKPL); dframe(-0.665, -0.245, -0.215, 0.225, RUST_D)
A.text("desk", DX(-0.475), DY(-0.165), "NAV", TXT)
# 동서남북 구역
drect(-0.08, 0.32, -0.205, 0.205, DARKPL); dframe(-0.08, 0.32, -0.205, 0.205, RUST_D)
A.circle("desk", DX(0.12), DY(0.0), 0.165 / W, (84, 62, 50), ring=0.012)
# 상태등 구역
A.circle("desk", DX(0.58), DY(0.07), 0.062 / W, DARK)
A.circle("desk", DX(0.58), DY(0.07), 0.062 / W, TRIM, ring=0.008)
drect(0.46, 0.70, -0.185, -0.075, (206, 198, 172), amp=3); dframe(0.46, 0.70, -0.185, -0.075, (58, 48, 40))
A.text("desk", DX(0.485), DY(-0.093), "MOVE", INK)
A.shade("desk", DX(-0.2), 0.08, DX(-0.2) + 0.008, 0.9, -28)
A.shade("desk", DX(0.40), 0.08, DX(0.40) + 0.008, 0.9, -28)

# ---- 위쪽 화면 패널 (128 x 50 = 1.6 m x 0.62 m)
def UX(x): return (x + W / 2) / W
def UY(zl): return (UPH / 2 - zl) / UPH
A.fill("upper", RUST, amp=9, grad=10, speck=0.06, grime=0.3, seed=52)
rust("upper", seed=6, amount=0.3)
A.bevel("upper", 22, 26)
bolts("upper", [(0.012, 0.06), (0.975, 0.06), (0.012, 0.86), (0.975, 0.86), (0.495, 0.06), (0.495, 0.86)])
A.rect("upper", UX(-0.71), UY(0.245), UX(-0.05), UY(-0.245), DARKPL, amp=5)
A.text("upper", UX(-0.54), UY(0.296), "POSITION", TXT)
A.circle("upper", UX(0.38), UY(0.0), 0.285 / W, DARKPL)
for ang in range(0, 360, 30):
    A.dot("upper", UX(0.38 + math.cos(R(ang)) * 0.285) - 0.004, UY(math.sin(R(ang)) * 0.285) - 0.01, TXT, 1)
A.shade("upper", UX(-0.005), 0.08, UX(-0.005) + 0.008, 0.92, -28)

# ---- 받침 앞면 (64 x 38 = 1.6 m x 0.87 m)
A.fill("basefront", RUST, amp=9, grad=12, speck=0.05, grime=0.45, seed=53)
rust("basefront", seed=7, amount=0.33)
A.bevel("basefront", 20, 24)
A.rect("basefront", 0.08, 0.16, 0.92, 0.5, DARKPL, amp=4)
A.hlines("basefront", 0.2, 0.47, 2, -26, 0.11, 0.89)
A.hazard("basefront", 0.0, 0.88, 1.0, 1.0, w=3)
A.vlines("basefront", 0.5, 0.505, 1, -26, 0.55, 0.86)
A.dot("basefront", 0.04, 0.05, (182, 156, 126), 1).dot("basefront", 0.94, 0.05, (182, 156, 126), 1)

# ---- 작은 셀
A.fill("side", RUST, amp=9, grad=8, speck=0.05, grime=0.4, seed=54); rust("side", seed=8, amount=0.35); A.bevel("side", 18, 22)
A.fill("cheek", (104, 72, 54), amp=8, grad=10, speck=0.05, grime=0.4, seed=55); rust("cheek", seed=9, amount=0.3); A.bevel("cheek", 16, 20)
A.fill("trim", TRIM, amp=8, grad=6, speck=0.04, grime=0.25, seed=56); A.bevel("trim", 18, 20)
A.fill("bezel", (88, 80, 72), amp=6, grad=8, speck=0.02, grime=0.1, seed=57); A.bevel("bezel", 20, 24)
A.fill("dark", DARK, amp=5, grad=4, speck=0.02, grime=0.2, seed=58)
A.fill("pipe", (70, 58, 52), amp=6, grad=0, speck=0.03, grime=0, seed=59); A.hlines("pipe", 0, 1, 3, -18)
A.fill("keyside", (120, 108, 92), amp=4, grad=10, speck=0, grime=0, seed=60)
A.fill("keyside2", (104, 100, 94), amp=4, grad=10, speck=0, grime=0, seed=61)
A.fill("lamp_g", GREEN, amp=6, grad=20, speck=0, grime=0, seed=62); A.frame("lamp_g", 0, 0, 1, 1, (52, 118, 60)); A.dot("lamp_g", 0.3, 0.3, (240, 255, 236), 2)
for k in KEYS:
    nm = "key_" + k
    big = k in ("N", "S", "W", "E2")
    A.fill(nm, BEIGE if big else KEYG, amp=4, grad=10, speck=0, grime=0, seed=63)
    A.bevel(nm, 24, 30)
    A.text(nm, 0.3, 0.2, "E" if k == "E2" else k, INK)

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


def ring_front(m, cx, cz, y, r_out, r_in, role, seg=16):
    """앞을 보는 고리 면 (원형 베젤 앞면)."""
    mark = m.begin(); b = len(m.V)
    for k in range(seg):
        a = 2 * math.pi * k / seg
        m.V.append((cx + r_out * math.cos(a), y, cz + r_out * math.sin(a)))
        m.V.append((cx + r_in * math.cos(a), y, cz + r_in * math.sin(a)))
    for k in range(seg):
        k2 = (k + 1) % seg
        m.face([b + 2 * k, b + 2 * k2, b + 2 * k2 + 1, b + 2 * k + 1], role)
    m.end(mark, closed=False)


def disc_front(m, cx, cz, y, r, role, seg=16):
    b = len(m.V)
    for k in range(seg):
        a = 2 * math.pi * k / seg
        m.V.append((cx + r * math.cos(a), y, cz + r * math.sin(a)))
    uv = [(0.5 + 0.5 * math.cos(2 * math.pi * k / seg), 0.5 + 0.5 * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    m.face([b + k for k in range(seg)], role, uv)


# 조작판(책상) 좌표 -> 모델 좌표 변환: 조작판 앞면 중심이 원점, x 오른쪽, z 조작판 위쪽, -y 플레이어 쪽
DESK_M = H.mul(H.trans(0, PF[0], PF[1]), H.rot_x(-R(TILT)))


def desk_point(x, y, z):
    v = np.array(DESK_M) @ np.array([x, y, z, 1.0])
    return tuple(v[:3])


# ================================================================ 본체
m = H.Mesh()
# 콘솔 측면 단면 (y, z) 을 X 방향으로 밀어낸 덩어리
bot = (PF[0] - DESK_H / 2 * CU[0], PF[1] - DESK_H / 2 * CU[1])
top = (PF[0] + DESK_H / 2 * CU[0], PF[1] + DESK_H / 2 * CU[1])
prof = [(0.0, 0.0), (-0.6, 0.0), (-0.6, 0.87), bot, top, (0.0, top[1])]
m.extrude_profile(prof, -W / 2, W / 2, "side", cap="cheek", closed=True)
quad_front(m, -W / 2, W / 2, 0.0, 0.87, -0.6005, "basefront")
s0 = len(m.V); quad_front(m, -W / 2, W / 2, -DESK_H / 2, DESK_H / 2, -0.0006, "desk"); m.xform(DESK_M, s0)
# 발판 홈
m.box(-W / 2 + 0.02, W / 2 - 0.02, -0.62, -0.6, 0.0, 0.07, "dark", {"back": None})

# 위쪽 화면 패널
m.box(-W / 2 - 0.025, W / 2 + 0.025, UF, 0.0, UPZ - UPH / 2 - 0.025, UPZ + UPH / 2 + 0.025, "side", {"front": "upper", "back": None})
frame_boxes(m, -0.69, -0.07, UPZ - 0.22, UPZ + 0.22, 0.05, UF - 0.03, UF, "trim")
ycyl(m, 0.38, UPZ, UF, 0.03, 0.26, "bezel", None, seg=16)
ring_front(m, 0.38, UPZ, UF - 0.03, 0.26, 0.22, "bezel", seg=16)
# 배관 (천장까지)
for px in (-0.62, -0.52):
    m.cyl(px, -0.07, UPZ + UPH / 2 + 0.025, 2.40, 0.03, "pipe", cap=None, seg=6)
m.box(0.42, 0.70, -0.13, -0.02, UPZ + UPH / 2 + 0.025, 2.40, "side", {"top": None, "bottom": None})

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
    """조작판 위 부품: 조작판 좌표로 만들고, 조작판 기울기대로 세워 붙인다."""
    q = H.Mesh(); mesh_fn(q)
    return add(name, q, (sx, 0.0, sz), atlas, mat, rot_x=-TILT, loc=desk_point(sx, 0.0, sz))


# ---- 화면 (임시 공용 화면 텍스처. UI가 들어갈 자리)
q = H.Mesh(); quad_front(q, -0.64, -0.12, UPZ - 0.17, UPZ + 0.17, UF - 0.002, "scr")
add("Screen_Coord", q, (-0.38, UF - 0.002, UPZ), SCR, SCR_MAT)
q = H.Mesh(); disc_front(q, 0.38, UPZ, UF - 0.004, 0.22, "scr", seg=16)
add("Screen_Radar", q, (0.38, UF - 0.004, UPZ), SCR, SCR_MAT)
desk_part("Screen_NavInput", lambda q: quad_front(q, -0.63, -0.27, 0.135, 0.205, -0.002, "scr"), -0.45, 0.17, SCR, SCR_MAT)

# ---- 항로 입력 키패드 (4 x 3)
NAVKEYS = [("NavKey_1", "1"), ("NavKey_2", "2"), ("NavKey_3", "3"), ("NavKey_4", "4"), ("NavKey_5", "5"), ("NavKey_6", "6"),
           ("NavKey_7", "7"), ("NavKey_8", "8"), ("NavKey_9", "9"), ("NavKey_0", "0"), ("NavKey_Clear", "C"), ("NavKey_Enter", "E")]
for i, (nm, k) in enumerate(NAVKEYS):
    sx = -0.58 + (i % 4) * 0.087; sz = 0.06 - (i // 4) * 0.09
    desk_part(nm, lambda q, sx=sx, sz=sz, k=k: q.box(sx - 0.033, sx + 0.033, -0.026, 0.0, sz - 0.033, sz + 0.033, "keyside2",
                                                      {"front": "key_" + k, "back": None}), sx, sz)

# ---- 동서남북 이동 버튼
for nm, k, sx, sz in (("Button_N", "N", 0.12, 0.12), ("Button_S", "S", 0.12, -0.12),
                      ("Button_W", "W", 0.0, 0.0), ("Button_E", "E2", 0.24, 0.0)):
    desk_part(nm, lambda q, sx=sx, sz=sz, k=k: q.box(sx - 0.047, sx + 0.047, -0.045, 0.0, sz - 0.047, sz + 0.047, "keyside",
                                                      {"front": "key_" + k, "back": None}), sx, sz)

# ---- 이동 상태 표시등
desk_part("Light_Status", lambda q: ycyl(q, 0.58, 0.07, 0.0, 0.035, 0.042, "lamp_g", "lamp_g", seg=8, r1=0.034), 0.58, 0.07)

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
    body.location = (0.0, -1.6, 0.0)
    body.rotation_euler = (0, 0, R(180))
for o in objs:
    o.select_set(False)
