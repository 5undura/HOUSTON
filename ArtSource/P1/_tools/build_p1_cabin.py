"""HOUSTON P1 - 캐빈 내부 (P1_Cabin_01): 팔각형 벽, 바닥, 천장, 천장 조명, 경고등 8개.
P2 팀의 houston_lib.py 를 그대로 사용한다. 면은 안쪽만 보인다 (카메라는 항상 캐빈 안).
Unity 배치: 블록아웃과 같은 자리 Position (0, 0, 0), Rotation (0, 0, 0).
"""
import bpy, os, sys, math, importlib, json
import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
P1DIR = os.path.dirname(TOOLS)
ART = os.path.dirname(P1DIR)
sys.path.insert(0, os.path.join(ART, "P2", "_tools"))
import houston_lib as H
importlib.reload(H)

OUT = os.path.join(P1DIR, "_build")
MOD = os.path.join(OUT, "Models", "P1"); TEX = os.path.join(OUT, "Textures", "P1")
for d in (MOD, TEX):
    os.makedirs(d, exist_ok=True)

win = bpy.context.window_manager.windows[0]
sc = win.scene
N = "P1_Cabin_01"
S, C, HH = 1.6, 0.6, 2.4
R2 = math.sqrt(0.5)

WALLC = (100, 70, 54); RUST_D = (62, 42, 32); DARK = (42, 34, 30); BOLT = (176, 150, 120)

A = H.Atlas(128)
A.cell("wall", 0, 0, 32, 64).cell("corner", 32, 0, 64, 64).cell("floor", 64, 0, 96, 32).cell("ceil", 96, 0, 128, 32)
A.cell("ceilight", 64, 32, 96, 48).cell("lamp", 96, 32, 104, 40).cell("lamphouse", 104, 32, 112, 40)
A.cell("pipe", 112, 32, 120, 40).cell("dark", 120, 32, 128, 40)


def rust(name, seed=0, amount=0.3, col=(150, 82, 36)):
    x0, y0, x1, y1 = A.cells[name]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    n = H._hash(xx // 3, yy // 3, seed) * 0.6 + H._hash(xx // 7 + 3, yy // 7 + 1, seed + 5) * 0.4
    m = n > (1 - amount)
    v = A.A[y0:y1, x0:x1, :3]
    v[m] = v[m] * 0.6 + np.array(col, float) * 0.4
    m2 = n < amount * 0.35
    v[m2] = v[m2] * 0.72


def wallpaint(nm, seed):
    A.fill(nm, WALLC, amp=10, grad=14, speck=0.06, grime=0.45, seed=seed)
    rust(nm, seed=seed + 1, amount=0.3)
    A.bevel(nm, 16, 22)
    A.shade(nm, 0.0, 0.0, 0.07, 1.0, -22).shade(nm, 0.93, 0.0, 1.0, 1.0, -22)
    for fy in (0.30, 0.62):
        A.shade(nm, 0.0, fy, 1.0, fy + 0.012, -34)
        for fx in (0.12, 0.37, 0.62, 0.87):
            A.dot(nm, fx, fy - 0.025, BOLT, 1)
    A.rect(nm, 0.0, 0.875, 1.0, 1.0, (66, 52, 44), amp=5)
    A.hazard(nm, 0.0, 0.85, 1.0, 0.875, w=2)


wallpaint("wall", 201)
wallpaint("corner", 205)
A.shade("corner", 0.3, 0.0, 0.7, 0.85, -26)                      # 배관 뒤 그늘

A.fill("floor", (80, 72, 66), amp=6, grad=6, speck=0.05, grime=0.4, seed=210)
for i in range(2, 32, 4):
    for j in range(2, 32, 4):
        A.dot("floor", i / 32, j / 32, (112, 102, 94), 1)
A.frame("floor", 0, 0, 1, 1, (40, 34, 30))
for b in ((0.06, 0.06), (0.9, 0.06), (0.06, 0.9), (0.9, 0.9)):
    A.dot("floor", b[0], b[1], BOLT, 1)
rust("floor", seed=211, amount=0.2, col=(120, 70, 40))

A.fill("ceil", (92, 80, 72), amp=6, grad=8, speck=0.04, grime=0.3, seed=220)
A.frame("ceil", 0, 0, 1, 1, (48, 40, 36))
A.hlines("ceil", 0.4, 0.6, 2, -30, 0.2, 0.8)
rust("ceil", seed=221, amount=0.2)

A.fill("ceilight", (232, 222, 192), amp=4, grad=14, speck=0, grime=0, seed=230)
A.frame("ceilight", 0, 0, 1, 1, (70, 62, 56))
A.vlines("ceilight", 0.33, 0.34, 1, -60, 0.0, 1.0).vlines("ceilight", 0.66, 0.67, 1, -60, 0.0, 1.0)
A.fill("lamp", (210, 46, 36), amp=6, grad=20, speck=0, grime=0, seed=231); A.dot("lamp", 0.3, 0.3, (255, 220, 210), 2)
A.fill("lamphouse", (54, 48, 44), amp=4, grad=8, speck=0, grime=0, seed=232)
A.fill("pipe", (70, 58, 52), amp=6, grad=0, speck=0.03, grime=0, seed=233); A.hlines("pipe", 0, 1, 3, -18)
A.fill("dark", DARK, amp=5, grad=4, speck=0.02, grime=0.2, seed=234)

img = A.to_image(bpy, "T_" + N, os.path.join(TEX, "T_" + N + ".png"))
MAT = H.make_material(bpy, "M_" + N, img)

FULL = [(0, 0), (1, 0), (1, 1), (0, 1)]


def quad(m, pts, role):
    b = len(m.V); m.V += [tuple(p) for p in pts]
    m.face([b, b + 1, b + 2, b + 3], role, FULL)


def wall(m, cx, cy, nx, ny, w, role, cols=1):
    rx, ry = -ny, nx                      # 안에서 봤을 때 오른쪽
    for k in range(cols):
        a = -w / 2 + w * k / cols; b2 = a + w / cols
        p0 = (cx + rx * a, cy + ry * a); p1 = (cx + rx * b2, cy + ry * b2)
        quad(m, [(p0[0], p0[1], 0), (p1[0], p1[1], 0), (p1[0], p1[1], HH), (p0[0], p0[1], HH)], role)


m = H.Mesh()
# 벽 4장 (각 2칸) + 모서리 벽 4장
for cx, cy, nx, ny in ((0, -S, 0, 1), (0, S, 0, -1), (-S, 0, 1, 0), (S, 0, -1, 0)):
    wall(m, cx, cy, nx, ny, 2 * (S - C), "wall", cols=2)
CORNERS = []
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = sx * (S - C / 2), sy * (S - C / 2)
        nx, ny = -sx * R2, -sy * R2
        wall(m, cx, cy, nx, ny, C * math.sqrt(2), "corner")
        CORNERS.append((cx, cy, nx, ny))
        # 모서리 세로 배관 2개
        for o in (-0.16, 0.16):
            px = cx + nx * 0.07 + (-ny) * o; py = cy + ny * 0.07 + nx * o
            m.cyl(px, py, 0.0, HH, 0.04, "pipe", cap=None, seg=6)
# 바닥 / 천장 (0.8 m 판)
T = 0.8
for i in range(4):
    for j in range(4):
        x0, y0 = -S + i * T, -S + j * T; x1, y1 = x0 + T, y0 + T
        quad(m, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], "floor")
        quad(m, [(x0, y1, HH), (x1, y1, HH), (x1, y0, HH), (x0, y0, HH)], "ceil")
# 천장 조명
m.box(-0.35, 0.35, -0.2, 0.2, HH - 0.06, HH, "dark", {"bottom": "ceilight", "top": None})

body = H.build_object(bpy, sc, N, m, A, MAT)
objs, meshes = [body], [m]

# 경고등 8개 (블록아웃 WarningLight_01~08 과 같은 자리)
REFC = [(-1.116, -1.4275), (-1.4275, -1.116), (-1.4275, 1.116), (-1.116, 1.4275),
        (1.116, 1.4275), (1.4275, 1.116), (1.4275, -1.116), (1.116, -1.4275)]
WALLD = -(2 * S - C) * R2                 # 모서리 벽 평면: p . n = WALLD
for i, (x, y) in enumerate(REFC):
    nx, ny = (R2 if x < 0 else -R2), (R2 if y < 0 else -R2)
    d = x * nx + y * ny - WALLD
    bx, by = x - nx * d, y - ny * d
    q = H.Mesh()
    q.box(-0.06, 0.06, -0.07, 0.0, -0.045, 0.045, "lamphouse", {"front": "lamp", "back": None})
    o = H.build_object(bpy, sc, "WarningLight_%02d" % (i + 1), q, A, MAT, parent=body, pivot=(0, 0, 0))
    o.location = (bx, by, 2.1)
    o.rotation_euler = (0, 0, math.atan2(nx, -ny))
    objs.append(o); meshes.append(q)

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
report = {"name": N, "tris": sum(mm.tris() for mm in meshes), "objects": len(objs),
          "dims": [round(v, 3) for v in body.dimensions], "parts": [o.name for o in objs[1:]]}
with open(os.path.join(OUT, N + "_report.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
print(json.dumps(report))
for o in objs:
    o.select_set(False)
