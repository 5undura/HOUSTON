"""HOUSTON P2 clue / paper props. Run inside Blender. Content is placeholder until puzzles are fixed."""
import bpy, os, sys, math, importlib
import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(TOOLS), "_build")
sys.path.insert(0, TOOLS)
import houston_lib as H
importlib.reload(H)

H.FONT.update({'Q': "010101101110011", 'Z': "111001010100111", 'J': "001001001101010", '?': "110001010000010",
               '#': "101111101111101", '=': "000111000111000"})

MOD = os.path.join(OUT, "Models", "P2"); TEX = os.path.join(OUT, "Textures", "P2"); PRE = os.path.join(OUT, "_preview_clues")
for d in (MOD, TEX, PRE):
    os.makedirs(d, exist_ok=True)

win = bpy.context.window_manager.windows[0]
sc = bpy.data.scenes.get("HOUSTON_clues") or bpy.data.scenes.new("HOUSTON_clues")
win.scene = sc
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)

GROUPS, REPORT = {}, []
INK = (40, 46, 90); PEN = (30, 30, 34); GREY = (120, 118, 112); REDINK = (170, 40, 36)
PAPER = (214, 210, 198)


# ------------------------------------------------------------ extra painters
def px_of(A, name, fx, fy):
    x0, y0, x1, y1 = A.cells[name]
    return x0 + int(round(fx * (x1 - x0 - 1))), y0 + int(round(fy * (y1 - y0 - 1)))


def line(A, name, fx0, fy0, fx1, fy1, color):
    x0, y0 = px_of(A, name, fx0, fy0); x1, y1 = px_of(A, name, fx1, fy1)
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        A.A[y, x, :3] = color


def poly(A, name, pts, color, closed=True):
    for a, b in zip(pts, pts[1:] + (pts[:1] if closed else [])):
        line(A, name, a[0], a[1], b[0], b[1], color)


def textbars(A, name, fx0, fy0, fx1, fy1, step, color, seed=0, h=1):
    rng = np.random.default_rng(seed)
    X0, Y0 = px_of(A, name, fx0, fy0); X1, Y1 = px_of(A, name, fx1, fy1)
    for y in range(Y0, Y1, step):
        x = X0; end = X1 - int(rng.integers(0, max(1, (X1 - X0) // 3)))
        while x < end:
            w = int(rng.integers(2, 7))
            A.A[y:y + h, x:min(x + w, end), :3] = color
            x += w + int(rng.integers(1, 3))


def scribble(A, name, fx0, fy0, fx1, fy1, step, color, seed=0):
    rng = np.random.default_rng(seed)
    X0, Y0 = px_of(A, name, fx0, fy0); X1, Y1 = px_of(A, name, fx1, fy1)
    for y in range(Y0, Y1, step):
        x = X0; end = X1 - int(rng.integers(0, max(1, (X1 - X0) // 2)))
        while x < end:
            w = int(rng.integers(3, 8))
            for k in range(w):
                if x + k >= end:
                    break
                yy = y + int(rng.integers(-1, 2)) if rng.random() < 0.5 else y
                A.A[yy, x + k, :3] = color
            x += w + 2


def paper(A, name, color=PAPER, seed=1, grime=0.2):
    A.fill(name, color, amp=4, grad=6, speck=0.03, grime=grime, seed=seed)


def stamp(A, name, fx, fy, text, color=REDINK):
    x0, y0, x1, y1 = A.cells[name]
    w = (len(text) * 4 + 3) / (x1 - x0); h = 9 / (y1 - y0)
    A.frame(name, fx, fy, fx + w, fy + h, color)
    A.text(name, fx + 2 / (x1 - x0), fy + 2 / (y1 - y0), text, color)


def portrait_atlas():
    A = (H.Atlas(128).cell("sheet", 0, 0, 90, 128).cell("edge", 96, 0, 128, 32)
         .cell("back", 96, 32, 128, 64).cell("misc", 96, 64, 128, 96).cell("misc2", 96, 96, 128, 128))
    A.default_sw = "paper"
    return A


def landscape_atlas():
    A = (H.Atlas(128).cell("sheet", 0, 0, 128, 90).cell("edge", 0, 96, 32, 128)
         .cell("back", 32, 96, 64, 128).cell("misc", 64, 96, 128, 128))
    A.default_sw = "paper"
    return A


def base_cells(A):
    A.fill("edge", (206, 202, 190), amp=3, grad=0, speck=0, grime=0, seed=2).hlines("edge", 0, 1, 2, -14)
    A.fill("back", (200, 196, 184), amp=4, grad=6, speck=0.02, grime=0.15, seed=3)


def mat_from(A, name):
    img = A.to_image(bpy, "T_" + name, os.path.join(TEX, "T_" + name + ".png"))
    return H.make_material(bpy, "M_" + name, img)


def finish(name, objs, meshes):
    H.export_fbx(bpy, win, sc, objs, os.path.join(MOD, name + ".fbx"))
    GROUPS[name] = objs
    REPORT.append({"name": name, "tris": sum(m.tris() for m in meshes), "dims": [round(x, 3) for x in objs[0].dimensions]})


def flat(m, w, d, th, top="sheet", z0=0.0):
    m.box(-w / 2, w / 2, -d / 2, d / 2, z0, z0 + th, "edge", {"top": top, "bottom": "back"})


# ============================================================ large papers
def crew_manifest():
    N = "P2_CrewManifest_01"
    A = portrait_atlas(); base_cells(A); paper(A, "sheet", seed=11)
    A.text("sheet", 0.07, 0.04, "CREW MANIFEST", PEN)
    A.hlines("sheet", 0.1, 0.11, 1, -90, 0.06, 0.94)
    A.text("sheet", 0.07, 0.13, "VESSEL EX-07", GREY)
    A.frame("sheet", 0.06, 0.22, 0.94, 0.78, (90, 88, 84))
    for i in range(6):
        y = 0.25 + i * 0.087
        A.text("sheet", 0.1, y, "0%d" % (i + 1), PEN)
        textbars(A, "sheet", 0.26, y + 0.01, 0.7, y + 0.04, 3, (70, 70, 70), seed=20 + i)
        A.rect("sheet", 0.8, y + 0.005, 0.88, y + 0.045, [(60, 140, 70), (60, 140, 70), (190, 140, 40), REDINK, REDINK, REDINK][i], amp=0)
        if i < 5:
            A.hlines("sheet", y + 0.075, y + 0.08, 1, -40, 0.06, 0.94)
    A.text("sheet", 0.07, 0.83, "ONBOARD: 0", REDINK)
    stamp(A, "sheet", 0.5, 0.88, "VOID")
    A.fill("misc", PAPER, seed=12); A.fill("misc2", PAPER, seed=13)
    mat = mat_from(A, N)
    m = H.Mesh(); flat(m, 0.21, 0.297, 0.001)
    o = H.build_object(bpy, sc, N, m, A, mat); finish(N, [o], [m])


def medical_record():
    N = "P2_MedicalRecord_01"
    A = portrait_atlas(); A.swmap.update(misc="wood", misc2="metal"); base_cells(A); paper(A, "sheet", seed=31)
    A.text("sheet", 0.07, 0.07, "PATIENT REC", PEN)
    A.text("sheet", 0.07, 0.14, "ID EX-07-03", GREY)
    A.frame("sheet", 0.06, 0.22, 0.94, 0.48, (90, 88, 84))
    A.hlines("sheet", 0.28, 0.46, 4, -30, 0.08, 0.92)
    pts = [(0.08, 0.3), (0.2, 0.32), (0.3, 0.31), (0.38, 0.36), (0.46, 0.35), (0.56, 0.4), (0.66, 0.39), (0.76, 0.44), (0.92, 0.46)]
    poly(A, "sheet", pts, REDINK, closed=False)
    for i in range(5):
        y = 0.53 + i * 0.06
        A.frame("sheet", 0.07, y, 0.13, y + 0.04, PEN)
        textbars(A, "sheet", 0.18, y + 0.012, 0.9, y + 0.03, 3, (80, 80, 80), seed=40 + i)
    line(A, "sheet", 0.08, 0.545, 0.12, 0.565, INK); line(A, "sheet", 0.08, 0.605, 0.12, 0.625, INK)
    A.text("sheet", 0.07, 0.86, "O2 LOW", INK)
    scribble(A, "sheet", 0.45, 0.86, 0.92, 0.95, 4, INK, seed=45)
    A.fill("misc", (118, 92, 66), amp=6, grad=8, speck=0.04, grime=0.2, seed=32)
    A.fill("misc2", (150, 152, 150), amp=6, grad=20, speck=0, grime=0, seed=33).bevel("misc2")
    mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.115, 0.115, -0.16, 0.16, 0, 0.005, "misc")
    flat(m, 0.21, 0.297, 0.001, z0=0.005)
    m.box(-0.05, 0.05, 0.13, 0.165, 0.006, 0.016, "misc2")
    m.cyl(0, 0.165, 0.008, 0.014, 0.012, "misc2", cap="misc2", seg=6)
    o = H.build_object(bpy, sc, N, m, A, mat); finish(N, [o], [m])


def warning_poster():
    N = "P2_WarningPoster_01"
    A = portrait_atlas(); base_cells(A); paper(A, "sheet", (212, 208, 194), seed=51, grime=0.35)
    A.rect("sheet", 0, 0, 1, 0.2, (204, 168, 44))
    A.text("sheet", 0.19, 0.06, "WARNING", (24, 24, 24), scale=2, spacing=1)
    tri = [(0.5, 0.25), (0.75, 0.5), (0.25, 0.5)]
    poly(A, "sheet", tri, (24, 24, 24))
    poly(A, "sheet", [(0.5, 0.27), (0.72, 0.49), (0.28, 0.49)], (24, 24, 24))
    A.rect("sheet", 0.48, 0.32, 0.53, 0.42, (24, 24, 24), amp=0).rect("sheet", 0.48, 0.44, 0.53, 0.47, (24, 24, 24), amp=0)
    A.text("sheet", 0.12, 0.55, "QUARANTINE", REDINK)
    textbars(A, "sheet", 0.08, 0.63, 0.92, 0.84, 3, (60, 60, 60), seed=52)
    A.hazard("sheet", 0, 0.9, 1, 1, w=4)
    A.fill("misc", PAPER, seed=53); A.fill("misc2", PAPER, seed=54)
    mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.1485, 0.1485, -0.001, 0.0, -0.21, 0.21, "edge", {"front": "sheet", "back": "back"})
    o = H.build_object(bpy, sc, N, m, A, mat); finish(N, [o], [m])


def manual():
    N = "P2_Manual_01"
    A = portrait_atlas(); A.swmap.update(sheet="fabric", back="fabric", misc="fabric", misc2="fabric")
    A.fill("edge", (210, 204, 186), amp=3, grad=0, speck=0, grime=0, seed=61).hlines("edge", 0, 1, 2, -18)
    A.fill("back", (44, 54, 84), amp=5, grime=0.25, seed=62)
    A.fill("sheet", (44, 54, 84), amp=5, grad=10, speck=0.05, grime=0.3, seed=63).bevel("sheet", 14, 16)
    A.text("sheet", 0.12, 0.1, "SYS MANUAL", (220, 220, 210))
    A.text("sheet", 0.12, 0.18, "CIRCUIT", (150, 170, 200))
    A.text("sheet", 0.12, 0.24, "REPAIR", (150, 170, 200))
    for i, c in enumerate(((180, 50, 42), (200, 168, 44), (60, 100, 180), (70, 150, 80))):
        A.rect("sheet", 0.12, 0.42 + i * 0.07, 0.88, 0.46 + i * 0.07, c, amp=3)
    A.rect("sheet", 0.12, 0.78, 0.6, 0.88, (200, 198, 186)).text("sheet", 0.15, 0.8, "B2-07", PEN)
    A.fill("misc", (30, 36, 60), amp=4, grime=0.2, seed=64).vlines("misc", 0.1, 0.9, 6, 30)
    A.fill("misc2", (30, 36, 60), seed=65)
    mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.105, 0.105, -0.1485, 0.1485, 0, 0.022, "edge", {"top": "sheet", "bottom": "back", "left": "misc"})
    o = H.build_object(bpy, sc, N, m, A, mat); finish(N, [o], [m])


def record_folder():
    N = "P2_RecordFolder_01"
    A = portrait_atlas()
    A.fill("edge", (206, 202, 190), amp=3, grad=0, speck=0, grime=0, seed=71).hlines("edge", 0, 1, 2, -14)
    A.fill("back", (186, 160, 104), amp=5, grime=0.3, seed=72)
    A.fill("sheet", (190, 164, 106), amp=5, grad=8, speck=0.05, grime=0.35, seed=73)
    A.rect("sheet", 0.15, 0.12, 0.85, 0.3, (214, 210, 198))
    A.text("sheet", 0.2, 0.15, "EX LOG", PEN)
    textbars(A, "sheet", 0.2, 0.23, 0.8, 0.28, 3, GREY, seed=74)
    stamp(A, "sheet", 0.12, 0.62, "CLASSIFIED")
    A.fill("misc", (180, 154, 98), amp=4, grime=0.1, seed=75)
    A.fill("misc2", PAPER, seed=76)
    mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.1175, 0.1175, -0.1525, 0.1525, 0, 0.004, "edge", {"top": "back", "bottom": "back"})
    m.box(-0.105, 0.125, -0.145, 0.145, 0.004, 0.007, "edge", {"top": "misc2"})
    m.box(-0.1175, 0.1175, -0.1525, 0.1525, 0.007, 0.009, "edge", {"top": "sheet", "bottom": "back"})
    m.box(0.02, 0.1, 0.1525, 0.168, 0.007, 0.009, "misc")
    o = H.build_object(bpy, sc, N, m, A, mat); finish(N, [o], [m])


def blueprint():
    N = "P2_Blueprint_01"
    A = landscape_atlas()
    BL = (38, 66, 122); LN = (200, 214, 230)
    A.fill("sheet", BL, amp=5, grad=8, speck=0.02, grime=0.25, seed=81)
    A.vlines("sheet", 0, 1, 8, 16); A.hlines("sheet", 0, 1, 8, 16)
    hull = [(0.1, 0.45), (0.2, 0.28), (0.7, 0.28), (0.88, 0.4), (0.93, 0.5), (0.88, 0.6), (0.7, 0.72), (0.2, 0.72), (0.1, 0.55)]
    poly(A, "sheet", hull, LN)
    for ey in ((0.33, 0.42), (0.58, 0.67)):
        poly(A, "sheet", [(0.04, ey[0]), (0.1, ey[0]), (0.1, ey[1]), (0.04, ey[1])], LN)
    for x in (0.35, 0.5, 0.65):
        line(A, "sheet", x, 0.29, x, 0.71, LN)
    line(A, "sheet", 0.2, 0.5, 0.65, 0.5, (120, 150, 190))
    A.circle("sheet", 0.8, 0.5, 0.035, LN, ring=0.012)
    A.circle("sheet", 0.575, 0.38, 0.09, (210, 70, 60), ring=0.012)
    A.text("sheet", 0.04, 0.05, "EX-07", LN)
    A.text("sheet", 0.04, 0.13, "DECK A", (150, 180, 220))
    line(A, "sheet", 0.1, 0.8, 0.93, 0.8, LN)
    for x in (0.1, 0.35, 0.5, 0.65, 0.93):
        line(A, "sheet", x, 0.77, x, 0.83, LN)
    A.frame("sheet", 0.66, 0.85, 0.98, 0.98, LN)
    textbars(A, "sheet", 0.68, 0.88, 0.96, 0.96, 3, LN, seed=82)
    A.fill("edge", BL, amp=4, grime=0, seed=83)
    for r, c in ((0.48, (220, 228, 236)), (0.38, BL), (0.3, (220, 228, 236)), (0.2, BL), (0.12, (220, 228, 236))):
        A.circle("edge", 0.5, 0.5, r, c)
    A.fill("back", (206, 210, 216), amp=4, grime=0.15, seed=84)
    A.fill("misc", BL, amp=5, grad=10, speck=0.02, grime=0.2, seed=85).vlines("misc", 0, 1, 8, 20)
    textbars(A, "misc", 0.1, 0.2, 0.9, 0.8, 4, LN, seed=86)
    mat = mat_from(A, N)
    m = H.Mesh(); m.box(-0.297, 0.297, -0.21, 0.21, 0, 0.001, "back", {"top": "sheet"})
    o = H.build_object(bpy, sc, N, m, A, mat); finish(N, [o], [m])
    # rolled version shares the material
    R = H.Mesh(); st = len(R.V)
    R.cyl(0, 0, -0.3, 0.3, 0.03, "misc", cap="edge", seg=8)
    R.xform(H.mul(H.trans(0, 0, 0.03), H.rot_y(math.radians(90))), st)
    ro = H.build_object(bpy, sc, "P2_BlueprintRoll_01", R, A, mat); finish("P2_BlueprintRoll_01", [ro], [R])


# ============================================================ small papers (shared atlas)
def small_papers():
    A = H.Atlas(128).grid(["sticky_y", "sticky_p", "sticky_b", "memo", "photo1", "photo2", "badge", "clip",
                           "edge_w", "back_w"], 4)
    A.default_sw = "paper"; A.swmap.update(badge="plastic", clip="metal")
    for nm, c, sd, txt in (("sticky_y", (214, 196, 92), 91, "4-7-2"), ("sticky_p", (212, 146, 152), 92, "EX07?"), ("sticky_b", (132, 172, 204), 93, "!!")):
        A.fill(nm, c, amp=4, grad=10, speck=0.02, grime=0.1, seed=sd).shade(nm, 0, 0, 1, 0.15, -14)
        A.text(nm, 0.15, 0.25, txt, INK)
        scribble(A, nm, 0.12, 0.55, 0.88, 0.9, 4, INK, seed=sd + 10)
    A.fill("memo", (216, 214, 202), amp=3, grad=4, speck=0.02, grime=0.15, seed=94)
    A.hlines("memo", 0.15, 1, 4, -30).vlines("memo", 0.15, 0.17, 1, -40)
    for k in range(3):
        A.shade("memo", 0.15, 0.0, 0.17, 1, 0)
    A.A[:, :, :] = A.A
    x0, y0, x1, y1 = A.cells["memo"]; A.A[y0:y1, x0 + 5, :3] = (190, 90, 90)
    scribble(A, "memo", 0.22, 0.13, 0.92, 0.92, 4, INK, seed=95)
    for nm, sd in (("photo1", 96), ("photo2", 97)):
        A.fill(nm, (222, 220, 212), amp=3, grad=0, speck=0, grime=0.15, seed=sd)
        A.rect(nm, 0.1, 0.08, 0.9, 0.72, (120, 130, 140), amp=4)
        A.rect(nm, 0.1, 0.08, 0.9, 0.3, (150, 160, 170), amp=4)
        A.rect(nm, 0.1, 0.55, 0.9, 0.72, (72, 70, 62), amp=4)
        scribble(A, nm, 0.15, 0.8, 0.8, 0.9, 3, INK, seed=sd + 5)
    for fx in (0.3, 0.55):
        A.rect("photo1", fx, 0.36, fx + 0.12, 0.6, (40, 40, 44), amp=0)
        A.rect("photo1", fx + 0.02, 0.28, fx + 0.1, 0.36, (40, 40, 44), amp=0)
    A.rect("photo2", 0.6, 0.12, 0.68, 0.55, (220, 220, 214), amp=0)
    A.rect("photo2", 0.62, 0.08, 0.66, 0.12, (220, 220, 214), amp=0)
    A.rect("photo2", 0.3, 0.2, 0.33, 0.55, (50, 50, 54), amp=0)
    for k in range(4):
        A.rect("photo2", 0.33, 0.24 + k * 0.08, 0.6, 0.25 + k * 0.08, (50, 50, 54), amp=0)
    A.fill("badge", (214, 214, 208), amp=3, grad=0, speck=0, grime=0.1, seed=98)
    A.rect("badge", 0, 0, 1, 0.22, (60, 130, 130))
    A.text("badge", 0.12, 0.05, "EX-07", (230, 236, 230))
    A.rect("badge", 0.1, 0.3, 0.45, 0.68, (110, 112, 116))
    A.rect("badge", 0.2, 0.36, 0.35, 0.5, (60, 60, 64)).rect("badge", 0.15, 0.5, 0.4, 0.68, (60, 60, 64))
    textbars(A, "badge", 0.52, 0.32, 0.92, 0.66, 3, (60, 60, 60), seed=99)
    for i in range(10):
        A.rect("badge", 0.12 + i * 0.075, 0.76, 0.12 + i * 0.075 + (0.04 if i % 3 else 0.02), 0.92, (30, 30, 30), amp=0)
    A.fill("clip", (150, 152, 150), amp=5, grad=20, speck=0, grime=0, seed=100)
    A.fill("edge_w", (210, 206, 194), amp=3, grad=0, speck=0, grime=0, seed=101)
    A.fill("back_w", (204, 200, 188), amp=3, grad=4, speck=0.02, grime=0.1, seed=102)
    A.cells["edge"] = A.cells["edge_w"]; A.cells["back"] = A.cells["back_w"]
    img = A.to_image(bpy, "T_P2_Papers_01", os.path.join(TEX, "T_P2_Papers_01.png"))
    mat = H.make_material(bpy, "M_P2_Papers_01", img)
    items = [("P2_StickyNote_01", 0.076, 0.076, 0.0008, "sticky_y"), ("P2_StickyNote_02", 0.076, 0.076, 0.0008, "sticky_p"),
             ("P2_StickyNote_03", 0.076, 0.076, 0.0008, "sticky_b"), ("P2_Memo_01", 0.105, 0.148, 0.0008, "memo"),
             ("P2_Photo_01", 0.088, 0.107, 0.001, "photo1"), ("P2_Photo_02", 0.088, 0.107, 0.001, "photo2"),
             ("P2_IDBadge_01", 0.054, 0.086, 0.001, "badge")]
    for nm, w, d, th, top in items:
        m = H.Mesh(); flat(m, w, d, th, top=top)
        if nm == "P2_IDBadge_01":
            m.box(-0.008, 0.008, 0.04, 0.052, 0.0, 0.003, "clip")
        o = H.build_object(bpy, sc, nm, m, A, mat); finish(nm, [o], [m])


ERR = {}
for fn in (crew_manifest, medical_record, warning_poster, manual, record_folder, blueprint, small_papers):
    try:
        fn()
    except Exception:
        import traceback
        ERR[fn.__name__] = traceback.format_exc()[-900:]

H.render_preview(bpy, win, sc, GROUPS, PRE, rot=(50, 0, -25))
