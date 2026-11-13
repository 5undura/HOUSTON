"""HOUSTON P2 medical + sci-fi props. Run inside Blender (needs houston_lib.py next to it)."""
import bpy, os, sys, math, importlib
import numpy as np

TOOLS = "/Users/hajiun/Downloads/poly_assets/HOUSTON_P2/_tools"
OUT = "/Users/hajiun/Downloads/poly_assets/HOUSTON_P2"
sys.path.insert(0, TOOLS)
import houston_lib as H
importlib.reload(H)

MOD = os.path.join(OUT, "Models", "P2"); TEX = os.path.join(OUT, "Textures", "P2")
TEXC = os.path.join(OUT, "Textures", "COM"); PRE = os.path.join(OUT, "_preview_props")
for d in (MOD, TEX, TEXC, PRE):
    os.makedirs(d, exist_ok=True)

win = bpy.context.window_manager.windows[0]
sc = bpy.data.scenes.get("HOUSTON_props") or bpy.data.scenes.new("HOUSTON_props")
win.scene = sc
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)

R = math.radians
GROUPS = {}
REPORT = []

# palette
OFFW = (162, 164, 156); PANEL = (128, 130, 124); METAL = (104, 106, 102); DARK = (46, 48, 48)
BLACK = (28, 28, 30); TEAL = (80, 200, 186); GREEN = (90, 210, 110); AMBER = (220, 150, 40); RED = (184, 50, 42)
CLOTH = (112, 124, 126); LABEL = (190, 188, 176)


def tube(m, a, b, r, role, seg=6):
    a = np.array(a, float); b = np.array(b, float); d = b - a; L = np.linalg.norm(d); z = d / L
    start = len(m.V)
    m.cyl(0, 0, 0, L, r, role, cap=None, seg=seg)
    up = np.array([0, 0, 1.0]); v = np.cross(up, z); c = float(np.dot(up, z))
    if np.linalg.norm(v) < 1e-8:
        Rm = np.eye(3) if c > 0 else np.diag([1, -1, -1])
    else:
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        Rm = np.eye(3) + vx + vx @ vx * (1 / (1 + c))
    M = np.eye(4); M[:3, :3] = Rm; M[:3, 3] = a
    m.xform(M, start)


def quad_front(m, x0, x1, z0, z1, y, role):
    b = len(m.V)
    m.V += [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    m.face([b, b + 1, b + 2, b + 3], role, [(0, 0), (1, 0), (1, 1), (0, 1)])


def mat_from(atlas, name, folder=TEX, alpha=False):
    img = atlas.to_image(bpy, "T_" + name, os.path.join(folder, "T_" + name + ".png"))
    return img, H.make_material(bpy, "M_" + name, img, alpha=alpha)


def finish(name, objs, meshes):
    H.export_fbx(bpy, win, sc, objs, os.path.join(MOD, name + ".fbx"))
    GROUPS[name] = objs
    REPORT.append({"name": name, "tris": sum(mm.tris() for mm in meshes),
                   "dims": [round(x, 2) for x in objs[0].dimensions], "parts": [o.name for o in objs]})


# ---------------------------------------------------------------- shared screen
scr = H.Atlas(32).cell("scr", 0, 0, 32, 32)
scr.fill("scr", (10, 40, 22), amp=6, grad=0, speck=0, grime=0)
scr.hlines("scr", 0, 1, 2, -8)
for i, L in enumerate((14, 20, 9, 16, 5)):
    scr.rect("scr", 0.12, 0.14 + i * 0.1, 0.12 + L / 32, 0.14 + i * 0.1 + 1 / 32, (90, 230, 130), amp=0)
scr_img = scr.to_image(bpy, "T_COM_Screen_01", os.path.join(TEXC, "T_COM_Screen_01.png"))
SCR_MAT = H.make_material(bpy, "M_COM_Screen_01", scr_img, emissive=True)


def screen_obj(name, x0, x1, z0, z1, y, parent):
    m = H.Mesh(); quad_front(m, x0, x1, z0, z1, y, "scr")
    o = H.build_object(bpy, sc, name, m, scr, SCR_MAT, parent=parent, pivot=((x0 + x1) / 2, y, (z0 + z1) / 2))
    return o, m


# ================================================================ 1. MedPod
def med_pod():
    N = "P2_MedPod_01"
    A = H.Atlas(128).grid(["body", "front", "base", "cloth", "console", "trim", "glass", "pillow", "hose", "dark"], 4)
    A.fill("body", OFFW, grime=0.35, seed=1).bevel("body").vlines("body", 0.5, 0.51, 1, -22)
    A.dot("body", 0.08, 0.08, (90, 90, 88)).dot("body", 0.9, 0.08, (90, 90, 88))
    A.fill("front", OFFW, grime=0.4, seed=2).bevel("front")
    A.frame("front", 0.04, 0.08, 0.96, 0.78, (120, 120, 114))
    A.text("front", 0.1, 0.16, "MED-04", (64, 66, 64))
    A.hlines("front", 0.42, 0.7, 2, -26, 0.55, 0.92)
    A.hazard("front", 0, 0.82, 1, 1, w=3)
    A.fill("base", DARK, amp=6, grime=0.2, seed=3).bevel("base", 10, 14)
    A.fill("cloth", CLOTH, amp=8, grad=6, speck=0.02, grime=0.1, seed=4).vlines("cloth", 0.1, 1, 7, -12)
    A.fill("pillow", (152, 158, 156), amp=6, grad=10, speck=0.02, grime=0.05, seed=5).bevel("pillow", 10, 18)
    A.fill("console", (40, 42, 44), amp=5, grime=0.1, seed=6).bevel("console", 14, 10)
    A.text("console", 0.1, 0.08, "VITAL", TEAL)
    for i, c in enumerate((GREEN, GREEN, AMBER, RED)):
        A.dot("console", 0.12 + i * 0.18, 0.34, c, 2)
    for r in range(2):
        for k in range(3):
            A.rect("console", 0.12 + k * 0.27, 0.55 + r * 0.2, 0.3 + k * 0.27, 0.68 + r * 0.2, (96, 98, 96))
    A.fill("trim", METAL, amp=8, grime=0.2, seed=7).bevel("trim")
    A.fill("glass", (110, 150, 150), amp=4, grad=6, speck=0, grime=0, seed=8).alpha("glass", 70)
    for k in range(3):
        A.shade("glass", 0.15 + k * 0.08, 0, 0.18 + k * 0.08, 1, 40)
    A.fill("hose", (56, 58, 60), amp=4, grime=0, seed=9).hlines("hose", 0, 1, 2, -14)
    A.fill("dark", DARK, amp=5, grime=0.2, seed=10)
    img, mat = mat_from(A, N)
    lid_mat = H.make_material(bpy, "M_" + N + "_Lid", img, alpha=True)

    m = H.Mesh()
    m.box(-1.05, 1.05, -0.45, 0.45, 0.0, 0.1, "base")
    m.box(-1.0, 1.0, -0.42, 0.42, 0.1, 0.55, "body", {"front": "front", "back": "front", "top": "dark"})
    m.box(-0.85, 0.88, -0.36, 0.36, 0.55, 0.66, "cloth")
    m.box(-0.83, -0.58, -0.28, 0.28, 0.66, 0.74, "pillow")
    m.box(-1.05, -0.85, -0.44, 0.44, 0.55, 1.15, "body", {"front": "console", "top": "trim"})
    m.box(0.88, 1.05, -0.44, 0.44, 0.55, 0.8, "body", {"top": "trim"})
    m.box(-0.85, 0.88, -0.44, -0.37, 0.55, 0.70, "trim")
    m.box(-0.85, 0.88, 0.37, 0.44, 0.55, 0.70, "trim")
    m.box(0.9, 1.03, -0.22, 0.22, 0.8, 0.9, "console")
    for x in (-1.0, -0.92):
        tube(m, (x, 0.47, 0.02), (x, 0.47, 1.0), 0.028, "hose")
    tube(m, (-1.0, 0.47, 1.0), (-0.98, 0.42, 1.08), 0.028, "hose")
    tube(m, (-0.92, 0.47, 1.0), (-0.92, 0.42, 1.08), 0.028, "hose")
    body = H.build_object(bpy, sc, N, m, A, mat)
    s, sm = screen_obj(N + "_Screen", -1.03, -0.87, 0.86, 1.06, -0.4405, body)

    # lid (hinge at back edge)
    prof = [(0.43 * math.cos(R(a)), 0.70 + 0.40 * math.sin(R(a))) for a in range(180, -1, -36)]
    L = H.Mesh()
    L.extrude_profile(prof, -0.84, 0.87, "glass", cap="glass", double=True)
    prof2 = [(0.445 * math.cos(R(a)), 0.70 + 0.415 * math.sin(R(a))) for a in range(180, -1, -36)]
    for x in (-0.86, -0.02, 0.85):
        L.extrude_profile(prof2, x, x + 0.04, "trim", cap="trim", double=True)
    lid = H.build_object(bpy, sc, N + "_Lid", L, A, lid_mat, parent=body, pivot=(0, 0.43, 0.70))
    finish(N, [body, s, lid], [m, sm, L])


# ================================================================ 2. Health monitor
def health_monitor():
    N = "P2_HealthMonitor_01"
    A = H.Atlas(128).grid(["plastic", "bezel", "metal", "dark", "wheel", "lamp"], 4)
    A.fill("plastic", (150, 152, 146), grime=0.3, seed=11).bevel("plastic")
    A.fill("bezel", (66, 68, 66), amp=6, grime=0.15, seed=12).bevel("bezel", 18, 14)
    A.rect("bezel", 0.1, 0.1, 0.78, 0.78, (24, 26, 26))
    for r in range(4):
        A.rect("bezel", 0.83, 0.14 + r * 0.15, 0.94, 0.24 + r * 0.15, (110, 112, 108))
    A.dot("bezel", 0.86, 0.75, GREEN, 2)
    A.text("bezel", 0.08, 0.84, "HEALTH", TEAL)
    A.fill("metal", (124, 126, 124), amp=6, grad=0, grime=0.1, seed=13).vlines("metal", 0, 1, 5, 14)
    A.fill("dark", DARK, amp=5, grime=0.25, seed=14).bevel("dark", 10, 12)
    A.fill("wheel", BLACK, amp=4, grime=0, seed=15)
    A.fill("lamp", RED, amp=6, grad=24, speck=0, grime=0, seed=16)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    for k in range(5):
        st = len(m.V)
        m.box(0.0, 0.26, -0.022, 0.022, 0.04, 0.075, "dark")
        m.xform(H.rot_z(R(72 * k + 90)), st)
        a = R(72 * k + 90)
        m.cyl(0.25 * math.cos(a), 0.25 * math.sin(a), 0, 0.045, 0.03, "wheel", cap="wheel", seg=6)
    m.cyl(0, 0, 0.03, 0.11, 0.055, "dark", cap="dark", seg=8)
    m.cyl(0, 0, 0.11, 1.26, 0.018, "metal", cap="metal", seg=6)
    m.box(-0.05, 0.05, -0.03, 0.05, 1.18, 1.28, "dark")
    m.box(-0.22, 0.22, -0.10, 0.06, 1.25, 1.58, "plastic", {"front": "bezel"})
    m.box(-0.10, 0.06, -0.02, 0.02, 1.58, 1.62, "dark")
    m.cyl(0.15, -0.02, 1.58, 1.64, 0.025, "lamp", cap="lamp", seg=6)
    body = H.build_object(bpy, sc, N, m, A, mat)
    s, sm = screen_obj(N + "_Screen", -0.176, 0.123, 1.329, 1.546, -0.1015, body)
    finish(N, [body, s], [m, sm])


# ================================================================ 3. Oxygen tank
def oxygen_tank():
    N = "P2_OxygenTank_01"
    A = H.Atlas(64).grid(["tank", "brass", "dark", "gauge"], 2)
    A.fill("tank", (58, 94, 72), amp=8, grad=8, speck=0.08, grime=0.4, seed=21)
    A.rect("tank", 0, 0.08, 1, 0.36, LABEL)
    A.text("tank", 0.06, 0.12, "O2", (40, 70, 52), scale=1)
    A.hlines("tank", 0.28, 0.34, 2, -60, 0.06, 0.6)
    A.text("tank", 0.56, 0.12, "O2", (40, 70, 52))
    A.fill("brass", (150, 126, 72), amp=8, grad=20, speck=0.05, grime=0.1, seed=22)
    A.fill("dark", (40, 40, 42), amp=5, grime=0, seed=23).text("dark", 0.2, 0.4, "O2", (180, 50, 42))
    A.fill("gauge", (200, 198, 186), amp=4, grad=0, speck=0, grime=0, seed=24)
    A.circle("gauge", 0.5, 0.5, 0.48, (40, 40, 40), ring=0.06)
    A.rect("gauge", 0.48, 0.2, 0.53, 0.52, RED, amp=0)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.cyl(0, 0, 0, 0.04, 0.122, "dark", cap="dark", seg=10)
    m.cyl(0, 0, 0.04, 1.05, 0.115, "tank", cap="dark", seg=10)
    m.cyl(0, 0, 1.05, 1.14, 0.115, "tank", r1=0.07, cap="dark", seg=10, caps=(False, True))
    m.cyl(0, 0, 1.14, 1.20, 0.035, "brass", cap="brass", seg=8)
    m.box(-0.03, 0.03, -0.03, 0.03, 1.20, 1.27, "brass")
    m.box(0.03, 0.075, -0.012, 0.012, 1.215, 1.245, "brass")
    st = len(m.V)
    m.cyl(0, 0, 0, 0.02, 0.032, "brass", cap="gauge", seg=8)
    m.xform(H.mul(H.trans(0, -0.03, 1.235), H.rot_x(R(90))), st)
    body = H.build_object(bpy, sc, N, m, A, mat)
    V = H.Mesh()
    V.cyl(0, 0, 1.27, 1.30, 0.008, "brass", cap="brass", seg=6)
    V.cyl(0, 0, 1.30, 1.325, 0.048, "dark", cap="dark", seg=8)
    V.box(-0.05, 0.05, -0.006, 0.006, 1.30, 1.325, "dark")
    valve = H.build_object(bpy, sc, N + "_Valve", V, A, mat, parent=body, pivot=(0, 0, 1.27))
    finish(N, [body, valve], [m, V])


# ================================================================ 4. Respirator cart
def respirator():
    N = "P2_Respirator_01"
    A = H.Atlas(128).grid(["metal", "shelf", "unit", "panel", "hose", "mask", "wheel", "dark"], 4)
    A.fill("metal", METAL, amp=8, grime=0.25, seed=31).bevel("metal")
    A.fill("shelf", (118, 120, 116), amp=8, grime=0.3, seed=32).bevel("shelf").frame("shelf", 0.05, 0.05, 0.95, 0.95, (90, 92, 88))
    A.fill("unit", (166, 166, 158), grime=0.35, seed=33).bevel("unit").hlines("unit", 0.2, 0.7, 2, -24, 0.15, 0.85)
    A.fill("panel", (52, 54, 56), amp=5, grime=0.15, seed=34).bevel("panel", 16, 12)
    A.rect("panel", 0.06, 0.12, 0.46, 0.46, (20, 22, 22))
    for k in range(3):
        A.circle("panel", 0.6 + k * 0.14, 0.28, 0.055, (150, 150, 144)).dot("panel", 0.6 + k * 0.14, 0.24, BLACK)
    A.dot("panel", 0.6, 0.48, GREEN, 2).dot("panel", 0.7, 0.48, AMBER, 2)
    A.text("panel", 0.08, 0.6, "RESP-2", TEAL)
    A.hazard("panel", 0, 0.86, 1, 1, w=2)
    A.circle("panel", 0.82, 0.7, 0.08, (30, 30, 30))
    A.fill("hose", (64, 68, 72), amp=4, grime=0, seed=35).hlines("hose", 0, 1, 2, -16)
    A.fill("mask", (150, 168, 166), amp=6, grad=16, speck=0, grime=0, seed=36)
    A.fill("wheel", BLACK, amp=4, grime=0, seed=37)
    A.fill("dark", DARK, amp=5, grime=0.2, seed=38).text("dark", 0.1, 0.3, "FILTER", (150, 150, 140))
    img, mat = mat_from(A, N)
    m = H.Mesh()
    for x in (-0.28, 0.25):
        for y in (-0.2, 0.17):
            m.box(x, x + 0.03, y, y + 0.03, 0.06, 0.75, "metal")
            m.cyl(x + 0.015, y + 0.015, 0, 0.06, 0.03, "wheel", cap="wheel", seg=6)
    m.box(-0.3, 0.3, -0.22, 0.22, 0.25, 0.28, "shelf")
    m.box(-0.3, 0.3, -0.22, 0.22, 0.72, 0.75, "shelf")
    m.box(-0.29, 0.29, 0.19, 0.22, 0.75, 1.0, "metal", {"back": None})
    m.box(-0.2, 0.02, -0.16, 0.12, 0.28, 0.40, "dark")
    m.box(-0.24, 0.22, -0.18, 0.16, 0.75, 1.05, "unit", {"front": "panel"})
    pts = [(0.15, -0.18, 0.838), (0.2, -0.32, 0.78), (0.27, -0.36, 0.92), (0.24, -0.27, 1.06), (0.12, -0.1, 1.12)]
    for a, b in zip(pts[:-1], pts[1:]):
        tube(m, a, b, 0.022, "hose")
    m.cyl(0.05, -0.04, 1.05, 1.11, 0.06, "mask", r1=0.03, cap="mask", seg=8)
    body = H.build_object(bpy, sc, N, m, A, mat)
    s, sm = screen_obj(N + "_Screen", -0.212, -0.024, 0.888, 0.99, -0.1805, body)
    finish(N, [body, s], [m, sm])


# ================================================================ 5. Med shelf + bottles
def med_shelf():
    N = "P2_MedShelf_01"
    A = H.Atlas(128).grid(["frame", "shelf", "back", "sign"], 4)
    A.fill("frame", (118, 122, 118), amp=8, grime=0.3, seed=41).bevel("frame")
    A.fill("shelf", (132, 134, 130), amp=8, grime=0.2, seed=42).bevel("shelf")
    A.rect("shelf", 0.1, 0.2, 0.35, 0.8, LABEL).rect("shelf", 0.6, 0.2, 0.85, 0.8, LABEL)
    A.fill("back", (84, 88, 86), amp=6, grime=0.35, seed=43).vlines("back", 0.0, 1, 8, -14)
    A.fill("sign", (196, 194, 184), amp=4, grime=0.15, seed=44).bevel("sign", 8, 20)
    A.cross("sign", 0.25, 0.5, 0.36, RED)
    A.text("sign", 0.5, 0.38, "MED", (60, 60, 60))
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.45, -0.43, -0.175, 0.175, 0, 1.8, "frame")
    m.box(0.43, 0.45, -0.175, 0.175, 0, 1.8, "frame")
    m.box(-0.43, 0.43, 0.155, 0.175, 0.05, 1.8, "back")
    for z in (0.05, 0.45, 0.85, 1.25):
        m.box(-0.43, 0.43, -0.175, 0.155, z, z + 0.025, "shelf")
    m.box(-0.45, 0.45, -0.175, 0.175, 1.8, 1.83, "frame")
    m.box(-0.43, 0.43, -0.175, -0.16, 0, 0.05, "frame")
    m.box(-0.2, 0.2, -0.19, -0.175, 1.83, 1.97, "frame", {"front": "sign"})
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])

    B = H.Atlas(64).grid(["amber", "cap", "vial", "box"], 2)
    B.fill("amber", (150, 92, 36), amp=6, grad=18, speck=0, grime=0.1, seed=45)
    B.rect("amber", 0, 0.3, 1, 0.7, LABEL).hlines("amber", 0.4, 0.65, 3, -70, 0.1, 0.7)
    B.fill("cap", (200, 200, 196), amp=4, grime=0, seed=46).hlines("cap", 0, 1, 3, -16)
    B.fill("vial", (150, 180, 184), amp=4, grad=20, speck=0, grime=0, seed=47)
    B.rect("vial", 0, 0.5, 1, 1, (90, 130, 170))
    B.fill("box", (196, 196, 190), amp=4, grime=0.1, seed=48).rect("box", 0, 0.1, 1, 0.3, (60, 90, 150))
    B.text("box", 0.2, 0.45, "RX", (60, 90, 150))
    bimg = B.to_image(bpy, "T_P2_MedBottle_01", os.path.join(TEX, "T_P2_MedBottle_01.png"))
    bmat = H.make_material(bpy, "M_P2_MedBottle_01", bimg)
    for nm, fn in (("P2_MedBottle_01", lambda b: (b.cyl(0, 0, 0, 0.075, 0.025, "amber", cap="cap", seg=8),
                                                   b.cyl(0, 0, 0.075, 0.095, 0.027, "cap", cap="cap", seg=8))),
                   ("P2_MedBottle_02", lambda b: (b.cyl(0, 0, 0, 0.06, 0.015, "vial", cap="vial", seg=6),
                                                   b.cyl(0, 0, 0.06, 0.072, 0.016, "cap", cap="cap", seg=6))),
                   ("P2_MedBox_01", lambda b: b.box(-0.045, 0.045, -0.02, 0.02, 0, 0.06, "box"))):
        b = H.Mesh(); fn(b)
        o = H.build_object(bpy, sc, nm, b, B, bmat)
        finish(nm, [o], [b])


# ================================================================ 6. IV stand
def iv_stand():
    N = "P2_IVStand_01"
    A = H.Atlas(64).grid(["metal", "dark", "bag", "wheel"], 2)
    A.fill("metal", (140, 142, 140), amp=6, grad=0, grime=0.1, seed=51).vlines("metal", 0, 1, 4, 14)
    A.fill("dark", DARK, amp=5, grime=0.2, seed=52)
    A.fill("bag", (186, 196, 188), amp=4, grad=10, speck=0, grime=0, seed=53)
    A.rect("bag", 0, 0.55, 1, 1, (150, 176, 166))
    A.rect("bag", 0.15, 0.15, 0.85, 0.45, LABEL).hlines("bag", 0.2, 0.42, 3, -70, 0.2, 0.8)
    A.fill("wheel", BLACK, amp=4, grime=0, seed=54)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    for k in range(5):
        st = len(m.V); a = R(72 * k + 90)
        m.box(0.0, 0.24, -0.015, 0.015, 0.035, 0.06, "dark"); m.xform(H.rot_z(a), st)
        m.cyl(0.235 * math.cos(a), 0.235 * math.sin(a), 0, 0.04, 0.025, "wheel", cap="wheel", seg=6)
    m.cyl(0, 0, 0.03, 0.09, 0.04, "dark", cap="dark", seg=6)
    m.cyl(0, 0, 0.09, 1.9, 0.012, "metal", cap="metal", seg=6)
    m.box(-0.13, 0.13, -0.008, 0.008, 1.86, 1.88, "metal")
    for x in (-0.12, 0.12):
        m.box(x - 0.006, x + 0.006, -0.006, 0.006, 1.80, 1.86, "metal")
    m.box(0.07, 0.17, -0.02, 0.02, 1.52, 1.80, "bag")
    m.box(0.117, 0.123, -0.004, 0.004, 1.0, 1.52, "dark")
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 7. Curtain
def curtain():
    N = "P2_Curtain_01"
    A = H.Atlas(64).grid(["cloth_a", "cloth_b", "rail", "hook"], 2)
    A.fill("cloth_a", (112, 128, 118), amp=6, grad=8, speck=0.03, grime=0.45, seed=61).hlines("cloth_a", 0.9, 0.94, 2, -20)
    A.fill("cloth_b", (88, 102, 94), amp=6, grad=8, speck=0.03, grime=0.45, seed=62).hlines("cloth_b", 0.9, 0.94, 2, -20)
    A.fill("rail", (120, 122, 120), amp=6, grime=0, seed=63).bevel("rail")
    A.fill("hook", (90, 92, 90), amp=4, grime=0, seed=64)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.8, 0.8, -0.02, 0.02, 2.2, 2.24, "rail")
    for x in (-0.6, 0.6):
        m.box(x - 0.015, x + 0.015, -0.015, 0.015, 2.24, 2.32, "rail")
    n = 12; xs = np.linspace(-0.78, 0.78, n + 1)
    mk = m.begin()
    for i in range(n):
        y0 = 0.04 if i % 2 == 0 else -0.04; y1 = -y0
        b = len(m.V)
        m.V += [(xs[i], y0, 0.12), (xs[i + 1], y1, 0.12), (xs[i + 1], y1, 2.18), (xs[i], y0, 2.18)]
        m.face([b, b + 1, b + 2, b + 3], "cloth_a" if i % 2 == 0 else "cloth_b",
               [(i / n, 0), ((i + 1) / n, 0), ((i + 1) / n, 1), (i / n, 1)])
    m.end(mk, closed=False, double=True)
    for x in xs[::2]:
        m.box(x - 0.01, x + 0.01, -0.01, 0.01, 2.17, 2.21, "hook")
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 8. Cable bundle
def cables():
    N = "P2_CableBundle_01"
    A = H.Atlas(64).grid(["k", "r", "y", "g", "clip"], 4)
    for nm, c, sd in (("k", (34, 34, 36), 71), ("r", (130, 42, 38), 72), ("y", (176, 146, 44), 73), ("g", (84, 86, 88), 74)):
        A.fill(nm, c, amp=4, grad=14, speck=0.02, grime=0, seed=sd)
    A.fill("clip", (120, 122, 118), amp=4, grime=0, seed=75)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    lanes = [("k", 0.0, 0.035, 0.03), ("g", 0.03, 0.06, 0.022), ("r", -0.03, 0.05, 0.018), ("y", 0.0, 0.085, 0.015)]
    for role, y, z, r in lanes:
        tube(m, (-1.0, y, z), (1.0, y, z), r, role, seg=6)
    sag = [(-0.6, -0.05, 0.05), (-0.35, -0.07, -0.0 + 0.02), (-0.1, -0.06, 0.03), (0.15, -0.05, 0.06)]
    for a, b in zip(sag[:-1], sag[1:]):
        tube(m, a, b, 0.012, "r", seg=6)
    for x in (-0.8, -0.2, 0.4, 0.95):
        m.box(x - 0.02, x + 0.02, -0.06, 0.07, 0.0, 0.12, "clip", {"bottom": None})
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 9. Decals
def decals():
    N = "P2_Decals_01"
    A = H.Atlas(128)
    A.cell("hazard", 0, 0, 128, 16).cell("danger", 0, 16, 64, 56).cell("o2", 64, 16, 96, 48)
    A.cell("barcode", 96, 16, 128, 32).cell("auth", 0, 56, 64, 72).cell("label", 64, 56, 112, 72)
    A.cell("exit", 0, 72, 64, 88)
    A.hazard("hazard", 0, 0, 1, 1, w=6).shade("hazard", 0, 0, 1, 1, -10)
    A.fill("danger", (200, 168, 44), amp=6, grad=6, speck=0.03, grime=0.2, seed=81).frame("danger", 0.03, 0.05, 0.97, 0.95, BLACK)
    A.rect("danger", 0.08, 0.15, 0.3, 0.85, BLACK).text("danger", 0.16, 0.3, "!", (200, 168, 44), scale=2)
    A.text("danger", 0.36, 0.25, "DANGER", BLACK).text("danger", 0.36, 0.55, "HIGH O2", BLACK)
    A.fill("o2", (50, 110, 70), amp=6, grime=0.2, seed=82).frame("o2", 0.05, 0.05, 0.95, 0.95, (220, 220, 210))
    A.text("o2", 0.22, 0.32, "O2", (230, 230, 220), scale=2)
    A.fill("barcode", (210, 208, 200), amp=4, grime=0, seed=83)
    for i, w in enumerate([1, 2, 1, 1, 3, 1, 2, 1, 1, 2, 1, 3]):
        x0 = 0.06 + i * 0.075
        A.rect("barcode", x0, 0.15, x0 + 0.025 * w, 0.7, BLACK, amp=0)
    A.fill("auth", (150, 44, 38), amp=6, grime=0.15, seed=84).text("auth", 0.08, 0.3, "AUTH ONLY", (230, 220, 210))
    A.fill("label", (206, 204, 194), amp=4, grime=0.1, seed=85).frame("label", 0, 0, 1, 1, (60, 60, 60))
    A.text("label", 0.12, 0.3, "B2-07", (40, 40, 40))
    A.fill("exit", (40, 120, 70), amp=6, grime=0.1, seed=86).text("exit", 0.1, 0.3, "EXIT", (230, 240, 230))
    A.rect("exit", 0.58, 0.45, 0.8, 0.56, (230, 240, 230), amp=0)
    for k in range(4):
        A.rect("exit", 0.8 + k * 0.016, 0.3 + k * 0.06, 0.816 + k * 0.016, 0.71 - k * 0.06, (230, 240, 230), amp=0)
    img, mat = mat_from(A, N)
    sizes = {"HazardStripe": ("hazard", 1.0, 0.125), "Danger": ("danger", 0.4, 0.25), "O2": ("o2", 0.2, 0.2),
             "Barcode": ("barcode", 0.12, 0.06), "AuthOnly": ("auth", 0.4, 0.1), "Label": ("label", 0.24, 0.08),
             "Exit": ("exit", 0.4, 0.1)}
    objs, meshes = [], []
    for i, (k, (cell, w, h)) in enumerate(sizes.items()):
        q = H.Mesh(); x = i * 0.0
        quad_front(q, -w / 2, w / 2, -h / 2, h / 2, -0.001, cell)
        o = H.build_object(bpy, sc, "P2_Decal_" + k + "_01", q, A, mat)
        objs.append(o); meshes.append(q)
    H.export_fbx(bpy, win, sc, objs, os.path.join(MOD, N + ".fbx"))
    for o, q in zip(objs, meshes):
        GROUPS[o.name] = [o]
    REPORT.append({"name": N, "tris": sum(q.tris() for q in meshes), "parts": [o.name for o in objs]})


# ================================================================ 10. Server rack
def server_rack():
    N = "P2_ServerRack_01"
    A = H.Atlas(128).cell("front", 0, 0, 40, 128).cell("side", 40, 0, 80, 128).cell("top", 80, 0, 112, 32).cell("dark", 80, 32, 112, 64)
    A.fill("side", (60, 62, 64), amp=6, grime=0.3, seed=91).bevel("side", 12, 14)
    A.hlines("side", 0.1, 0.3, 2, -14, 0.15, 0.85).hlines("side", 0.7, 0.9, 2, -14, 0.15, 0.85)
    A.fill("front", (54, 56, 58), amp=5, grime=0.25, seed=92).frame("front", 0, 0, 1, 1, (30, 30, 32))
    rng = np.random.default_rng(7)
    y = 8
    while y < 120:
        hgt = int(rng.choice([3, 3, 6]))
        A.rect("front", 0.08, y / 128, 0.92, (y + hgt - 1) / 128, (74, 76, 78) if rng.random() > 0.3 else (40, 42, 44), amp=4)
        if rng.random() > 0.25:
            for k in range(int(rng.integers(1, 4))):
                A.dot("front", 0.7 + k * 0.07, (y + 1) / 128, [GREEN, GREEN, AMBER, TEAL][int(rng.integers(0, 4))])
        if hgt == 6:
            A.hlines("front", (y + 1) / 128, (y + 5) / 128, 2, -18, 0.12, 0.55)
        y += hgt + 1
    A.text("front", 0.12, 0.012, "SRV07", (190, 190, 180))
    A.fill("top", (50, 52, 54), amp=5, grime=0, seed=93).vlines("top", 0.1, 0.9, 3, -16, 0.2, 0.8)
    A.fill("dark", (36, 36, 38), amp=4, grime=0, seed=94)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.3, 0.3, -0.4, 0.4, 0.0, 0.05, "dark")
    m.box(-0.3, 0.3, -0.4, 0.4, 0.05, 2.0, "side", {"front": "front", "top": "top"})
    for x in (-0.27, 0.25):
        m.box(x, x + 0.02, -0.42, -0.4, 0.9, 1.15, "dark")
    m.box(-0.12, 0.12, 0.15, 0.32, 2.0, 2.12, "dark", {"bottom": None})
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


ERR = {}
for fn in (med_pod, health_monitor, oxygen_tank, respirator, med_shelf, iv_stand, curtain, cables, decals, server_rack):
    try:
        fn()
    except Exception:
        import traceback
        ERR[fn.__name__] = traceback.format_exc()[-900:]

H.render_preview(bpy, win, sc, GROUPS, PRE)
