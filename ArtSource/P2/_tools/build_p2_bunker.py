"""HOUSTON P2 bunker props (2026-11-25 구조 개편). Run inside Blender (needs houston_lib.py next to it).
스타일: 모양은 스페이스 에이지(둥근 화면, 곡선), 재질은 폴아웃 벙커(크림·민트 법랑, 벗겨짐, 리벳, 녹).
정면 = Blender -Y (= Unity 로컬 +Z). 벽에 붙는 물건은 뒷면 y=0, 앞으로 -y 방향."""
import bpy, os, sys, math, importlib
import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(TOOLS), "_build")
sys.path.insert(0, TOOLS)
import houston_lib as H
importlib.reload(H)

MOD = os.path.join(OUT, "Models", "P2"); TEX = os.path.join(OUT, "Textures", "P2")
TEXC = os.path.join(OUT, "Textures", "Common"); PRE = os.path.join(OUT, "_preview_bunker")
for d in (MOD, TEX, TEXC, PRE):
    os.makedirs(d, exist_ok=True)

win = bpy.context.window_manager.windows[0]
sc = bpy.data.scenes.get("HOUSTON_bunker") or bpy.data.scenes.new("HOUSTON_bunker")
win.scene = sc
for o in list(sc.objects):
    bpy.data.objects.remove(o, do_unlink=True)

R = math.radians
GROUPS = {}
REPORT = []

# palette (폴아웃 벙커 법랑 + 녹)
CREAM = (196, 184, 148); MINT = (118, 162, 142); OLIVE = (92, 100, 78); METAL = (104, 106, 102)
DARK = (44, 46, 46); BLACK = (24, 24, 26); RUST = (122, 72, 44); BRASS = (176, 140, 70)
GREEN = (90, 210, 110); AMBER = (220, 150, 40); RED = (184, 50, 42); LABEL = (206, 200, 178)
CLOTH = (92, 98, 84); BLANKET = (110, 74, 58)


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


def chips(A, name, n=10, seed=1, color=RUST):
    """법랑 벗겨짐: 작은 녹 점·얼룩"""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        fx, fy = rng.random(), rng.random()
        w, h = 0.02 + rng.random() * 0.06, 0.02 + rng.random() * 0.05
        A.rect(name, fx, fy, min(1, fx + w), min(1, fy + h), color, amp=8, seed=int(rng.integers(0, 99)))


def rivets(A, name, fy, n, color=BRASS, fx0=0.05, fx1=0.95):
    for i in range(n):
        A.dot(name, fx0 + (fx1 - fx0) * i / max(1, n - 1), fy, color)


def knob(m, x, y, z, r, d, role, seg=8):
    """앞(-Y)으로 튀어나온 원통 손잡이"""
    s = len(m.V)
    m.cyl(0, 0, 0, d, r, role, cap=role, seg=seg)
    m.xform(H.mul(H.trans(x, y, z), H.rot_x(R(90))), s)


# ---------------------------------------------------------------- shared screen (기존과 같은 공용 화면)
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


# ================================================================ 1. 벽걸이 대형 CRT
def wall_crt(N="P2_WallCRT_01", W=0.95, Hh=1.30):
    A = H.Atlas(128)
    A.cell("housing", 0, 0, 64, 64).cell("frame", 64, 0, 128, 32).cell("plate", 64, 32, 128, 48)
    A.cell("brass", 64, 48, 80, 64).cell("knob", 80, 48, 96, 64).cell("dark", 96, 48, 128, 64)
    A.cell("vent", 0, 64, 64, 96).cell("cable", 64, 64, 96, 96)
    A.default_sw = "plastic"
    A.fill("housing", MINT, amp=6, grime=0.35, seed=11).bevel("housing", 14, 18); chips(A, "housing", 14, 3)
    A.fill("frame", CREAM, amp=6, grime=0.3, seed=12).bevel("frame", 16, 20); chips(A, "frame", 10, 4)
    rivets(A, "frame", 0.15, 8); rivets(A, "frame", 0.85, 8)
    A.fill("plate", LABEL, amp=4, grime=0.15, seed=13).frame("plate", 0, 0, 1, 1, DARK)
    A.text("plate", 0.06, 0.25, "MONITOR", (40, 40, 40))
    A.fill("brass", BRASS, amp=8, grime=0.1, seed=14)
    A.fill("knob", BLACK, amp=4, grime=0, seed=15).dot("knob", 0.5, 0.2, LABEL)
    A.fill("dark", DARK, amp=4, grime=0.2, seed=16)
    A.fill("vent", OLIVE, amp=5, grime=0.3, seed=17).hlines("vent", 0.15, 0.85, 3, -22, 0.1, 0.9)
    A.fill("cable", BLACK, amp=4, grime=0, seed=18)
    img, mat = mat_from(A, N)
    D = 0.30                             # 몸통 깊이 (2026-11-26: 베젤 얇게, 크기는 인자)
    BT, BB, BS = 0.07, 0.15, 0.07        # 위·아래·옆 테두리 두께
    m = H.Mesh()
    m.box(-W, W, -D, 0, 0.0, Hh, "housing", {"back": None, "front": "dark"})
    F0, F1 = -D - 0.06, -D
    m.box(-W, W, F0, F1, Hh - BT, Hh, "frame")                # 위
    m.box(-W, W, F0, F1, 0.0, BB, "frame")                    # 아래 (라벨·노브)
    m.box(-W, -W + BS, F0, F1, BB, Hh - BT, "frame")          # 왼
    m.box(W - BS, W, F0, F1, BB, Hh - BT, "frame")            # 오
    for sx in (-1, 1):                                        # 모서리 작은 사선 블록 (둥근 화면 느낌)
        for (z0, z1) in ((BB, BB + 0.06), (Hh - BT - 0.06, Hh - BT)):
            x0 = W - BS - 0.06 if sx > 0 else -W + BS
            m.box(x0, x0 + 0.06, F0 + 0.01, F1, z0, z1, "frame")
    quad_front(m, -0.22, 0.22, 0.03, 0.12, F0 - 0.001, "plate")
    for x in (-W + 0.20, -W + 0.33, W - 0.33, W - 0.20):
        knob(m, x, F0, 0.075, 0.03, 0.04, "knob")
    m.box(-W + 0.35, W - 0.35, -D + 0.02, -0.04, Hh, Hh + 0.05, "vent")
    s = len(m.V); m.cyl(0, 0, 0, 0.45, 0.03, "cable", seg=6); m.xform(H.trans(W - 0.2, -0.12, Hh - 0.1), s)
    for x in (-W + 0.035, W - 0.035):
        for z in (0.04, Hh - 0.035):
            m.box(x - 0.015, x + 0.015, F0 - 0.012, F0, z - 0.015, z + 0.015, "brass")
    body = H.build_object(bpy, sc, N, m, A, mat)
    so, sm = screen_obj("Screen", -W + BS, W - BS, BB, Hh - BT, -D - 0.02, body)
    finish(N, [body, so], [m, sm])


# ================================================================ 2·3. 콘솔 (가운데 / 날개) — 같은 아틀라스
CON = H.Atlas(128)
CON.cell("console", 0, 0, 64, 64).cell("top", 64, 0, 128, 32).cell("keys", 64, 32, 128, 64)
CON.cell("toggles", 0, 64, 64, 96).cell("gauge", 64, 64, 96, 96).cell("base", 96, 64, 128, 96)
CON.cell("brass", 0, 96, 32, 128).cell("knob", 32, 96, 64, 128).cell("lever", 64, 96, 96, 128).cell("plate", 96, 96, 128, 112)
CON.default_sw = "plastic"
CON.fill("console", CREAM, amp=6, grime=0.35, seed=21).bevel("console", 14, 18); chips(CON, "console", 16, 5)
CON.hlines("console", 0.55, 0.6, 2, -18)
CON.fill("top", OLIVE, amp=5, grime=0.2, seed=22).frame("top", 0, 0, 1, 1, DARK); rivets(CON, "top", 0.1, 6)
CON.fill("keys", DARK, amp=4, grime=0.1, seed=23)
for r_ in range(4):
    for c_ in range(8):
        CON.rect("keys", 0.06 + c_ * 0.115, 0.12 + r_ * 0.2, 0.06 + c_ * 0.115 + 0.085, 0.12 + r_ * 0.2 + 0.14, LABEL if (r_ + c_) % 5 else AMBER, amp=3)
CON.fill("toggles", MINT, amp=5, grime=0.25, seed=24).frame("toggles", 0, 0, 1, 1, DARK)
for i in range(6):
    CON.rect("toggles", 0.08 + i * 0.15, 0.2, 0.08 + i * 0.15 + 0.06, 0.45, METAL, amp=2)
    CON.dot("toggles", 0.11 + i * 0.15, 0.65, [GREEN, AMBER, RED][i % 3])
CON.fill("gauge", LABEL, amp=3, grime=0, seed=25).circle("gauge", 0.5, 0.5, 0.42, (235, 228, 205)).circle("gauge", 0.5, 0.5, 0.42, DARK, ring=0.05)
CON.rect("gauge", 0.48, 0.2, 0.52, 0.5, RED, amp=0)
CON.fill("base", DARK, amp=4, grime=0.4, seed=26)
CON.fill("brass", BRASS, amp=8, grime=0.1, seed=27)
CON.fill("knob", RED, amp=6, grime=0, seed=28)
CON.fill("lever", METAL, amp=6, grime=0.1, seed=29)
CON.fill("plate", LABEL, amp=3, grime=0.1, seed=30).text("plate", 0.08, 0.25, "COMM", (40, 40, 40))
CON_IMG, CON_MAT = mat_from(CON, "P2_Console_01")


def console_body(m, half, depth=0.78, h0=0.74, h1=0.92):
    """바닥 박스 + 앞으로 기울어진 윗판. 정면(-Y)이 앉는 쪽."""
    y0, y1 = -depth / 2, depth / 2
    m.box(-half, half, y0 + 0.08, y1, 0.0, 0.10, "base")                 # 들어간 발판
    m.box(-half, half, y0, y1, 0.10, h0, "console")
    m.extrude_profile([(y0 - 0.04, h0), (y1, h1), (y1, h0)], -half, half, "top", cap="console", closed=True)
    return y0, y1, h0, h1


def tilt_place(m, start, y0, y1, h0, h1, along, lift=0.005):
    """윗판 위로 붙이기: along=0(앞)~1(뒤)"""
    ang = math.atan2(h1 - h0, (y1 - (y0 - 0.04)))
    y = (y0 - 0.04) + (y1 - (y0 - 0.04)) * along
    z = h0 + (h1 - h0) * along
    m.xform(H.mul(H.trans(0, y, z + lift), H.rot_x(ang)), start)


def console_main():
    N = "P2_ConsoleMain_01"
    m = H.Mesh()
    y0, y1, h0, h1 = console_body(m, 0.68)
    # 뒤쪽 받침대 (작은 화면용)
    m.box(-0.45, 0.45, y1 - 0.16, y1, h1 - 0.02, h1 + 0.42, "console")
    m.box(-0.12, 0.12, y1 - 0.17, y1 - 0.16, h1 + 0.03, h1 + 0.08, "plate")
    # 레버 (오른쪽)
    s = len(m.V); m.cyl(0.55, -0.05, h0 + 0.05, h0 + 0.40, 0.018, "lever", seg=6)
    m.box(0.52, 0.58, -0.08, -0.02, h0 + 0.40, h0 + 0.46, "knob")
    m.box(0.50, 0.60, -0.10, 0.0, h0 + 0.03, h0 + 0.08, "brass")
    # 토글 줄 (왼쪽, 본체에 포함)
    s = len(m.V); m.box(-0.62, -0.36, -0.08, 0.08, 0.0, 0.02, "toggles", {"top": "toggles"}); tilt_place(m, s, y0, y1, h0, h1, 0.4)
    body = H.build_object(bpy, sc, N, m, CON, CON_MAT)
    # 입력 패널 (퍼즐용 별도 오브젝트)
    km = H.Mesh(); s = len(km.V)
    km.box(-0.30, 0.30, -0.11, 0.11, 0.0, 0.025, "keys", {"top": "keys"})
    tilt_place(km, s, y0, y1, h0, h1, 0.35)
    ko = H.build_object(bpy, sc, "InputPanel", km, CON, CON_MAT, parent=body)
    so, sm = screen_obj("Screen", -0.40, 0.40, h1 + 0.06, h1 + 0.40, y1 - 0.161, body)
    finish(N, [body, ko, so], [m, km, sm])


def console_seg():
    N = "P2_ConsoleSeg_01"
    m = H.Mesh()
    y0, y1, h0, h1 = console_body(m, 0.55)
    s = len(m.V); m.box(-0.45, 0.45, -0.09, 0.09, 0.0, 0.02, "toggles", {"top": "toggles"}); tilt_place(m, s, y0, y1, h0, h1, 0.3)
    for i, x in enumerate((-0.25, 0.0, 0.25)):
        s = len(m.V); m.box(x - 0.09, x + 0.09, -0.09, 0.09, 0.0, 0.012, "gauge", {"top": "gauge"}); tilt_place(m, s, y0, y1, h0, h1, 0.78)
    body = H.build_object(bpy, sc, N, m, CON, CON_MAT)
    finish(N, [body], [m])


# ================================================================ 4. 회전 의자 (지휘석: 원형 받침 + 두꺼운 등받이 + 팔걸이 조작부)
def swivel_chair():
    N = "P2_SwivelChair_01"
    A = H.Atlas(64).cell("frame", 0, 0, 32, 32).cell("cushion", 32, 0, 64, 32).cell("dark", 0, 32, 32, 48)
    A.cell("pad", 32, 32, 64, 48).cell("brass", 0, 48, 32, 64).cell("metal", 32, 48, 64, 64)
    A.fill("frame", CREAM, amp=6, grime=0.35, seed=41).bevel("frame", 12, 16); chips(A, "frame", 8, 6)
    A.fill("cushion", (96, 60, 48), amp=8, grime=0.4, seed=42, sw="fabric").hlines("cushion", 0.1, 0.9, 4, -14)
    A.rect("cushion", 0.62, 0.5, 0.86, 0.7, (150, 122, 84), amp=4)          # 해진 곳
    A.fill("dark", DARK, amp=4, grime=0.3, seed=43)
    A.fill("pad", OLIVE, amp=4, grime=0.2, seed=44).dot("pad", 0.2, 0.5, GREEN).dot("pad", 0.45, 0.5, AMBER).dot("pad", 0.7, 0.5, RED)
    A.fill("brass", BRASS, amp=8, grime=0.1, seed=45)
    A.fill("metal", METAL, amp=6, grime=0.2, seed=46)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.cyl(0, 0, 0.0, 0.06, 0.32, "dark", cap="dark", seg=10)                # 원형 받침
    m.cyl(0, 0, 0.06, 0.38, 0.06, "metal", seg=6)                          # 기둥
    m.cyl(0, 0, 0.36, 0.40, 0.14, "brass", cap="brass", seg=8)
    m.box(-0.27, 0.27, -0.25, 0.25, 0.40, 0.46, "frame")                   # 좌판 틀
    m.box(-0.25, 0.25, -0.24, 0.22, 0.46, 0.56, "cushion")                 # 방석
    s = len(m.V)                                                            # 등받이 (뒤로 약간 젖힘)
    m.box(-0.27, 0.27, 0.20, 0.30, 0.0, 0.70, "frame")
    m.box(-0.24, 0.24, 0.16, 0.20, 0.06, 0.66, "cushion")
    m.box(-0.16, 0.16, 0.17, 0.30, 0.70, 0.86, "frame")                    # 머리 받침
    m.box(-0.14, 0.14, 0.15, 0.17, 0.72, 0.84, "cushion")
    m.xform(H.mul(H.trans(0, 0.0, 0.46), H.rot_x(R(-10))), s)
    for sx in (-1, 1):                                                      # 팔걸이 + 조작 패드
        x0 = 0.27 if sx > 0 else -0.37
        m.box(x0, x0 + 0.10, -0.06, 0.04, 0.46, 0.66, "frame")
        m.box(x0, x0 + 0.10, -0.26, 0.20, 0.66, 0.72, "frame")
        m.box(x0 + 0.01, x0 + 0.09, -0.24, -0.08, 0.72, 0.735, "pad")
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 5. 볼트 문 (영원히 닫힘)
def vault_door():
    N = "P2_VaultDoor_01"
    A = H.Atlas(128)
    A.cell("frame", 0, 0, 64, 64).cell("door", 64, 0, 128, 64).cell("cog", 0, 64, 32, 96).cell("hub", 32, 64, 64, 96)
    A.cell("weld", 64, 64, 96, 96).cell("hinge", 96, 64, 128, 96).cell("hazard", 0, 96, 64, 112).cell("brass", 64, 96, 96, 128)
    A.default_sw = "metal"
    A.fill("frame", OLIVE, amp=6, grime=0.45, seed=51).bevel("frame", 14, 18); chips(A, "frame", 18, 7)
    A.fill("door", (150, 146, 120), amp=6, grime=0.4, seed=52)
    A.circle("door", 0.5, 0.5, 0.46, (150, 146, 120)).circle("door", 0.5, 0.5, 0.46, DARK, ring=0.05); A.circle("door", 0.5, 0.5, 0.30, (138, 134, 110)).circle("door", 0.5, 0.5, 0.30, DARK, ring=0.05)
    chips(A, "door", 22, 8)
    A.fill("cog", (120, 118, 100), amp=6, grime=0.3, seed=53)
    A.fill("hub", BRASS, amp=8, grime=0.2, seed=54)
    A.fill("weld", (96, 82, 70), amp=10, grime=0.2, seed=55)
    for i in range(6):
        A.rect("weld", 0.05 + i * 0.15, 0.3, 0.05 + i * 0.15 + 0.09, 0.7, (170, 120, 70), amp=10)   # 용접 비드
    A.fill("hinge", DARK, amp=5, grime=0.3, seed=56).hlines("hinge", 0, 1, 4, -16)
    A.hazard("hazard", 0, 0, 1, 1, w=6)
    A.fill("brass", BRASS, amp=8, grime=0.1, seed=57)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    FW, FH = 1.35, 2.90                     # 2026-11-26: 복도 벽 한 칸을 통째로 대신하는 판 (벽 안으로 들어간 문)
    m.box(-FW, FW, -0.10, 0.0, 0.0, FH, "frame", {"back": None})
    for x0 in (-FW, FW - 0.10):                                            # 옆 벽두께 (움푹 들어간 느낌)
        m.box(x0, x0 + 0.10, -0.40, -0.10, 0.0, FH, "frame")
    m.box(-FW, FW, -0.40, -0.10, 2.50, FH, "frame")                        # 위 인방
    m.box(-FW + 0.10, FW - 0.10, -0.12, -0.10, 0.0, 0.12, "hazard")        # 바닥 경고띠
    cz, rr = 1.30, 1.08
    def disc(r, y_front, y_back, side, cap, seg):
        s = len(m.V); m.cyl(0, 0, 0, y_back - y_front, r, side, cap=cap, seg=seg)
        m.xform(H.mul(H.trans(0, y_front, cz), H.rot_x(R(-90))), s)
    disc(rr + 0.08, -0.16, -0.10, "frame", "frame", 16)        # 문틀 링
    disc(rr, -0.40, -0.16, "cog", "door", 16)                  # 문짝
    for k in range(12):                                         # 톱니
        a = 2 * math.pi * k / 12
        s = len(m.V); m.box(-0.07, 0.07, -0.32, -0.16, cz + rr - 0.02, cz + rr + 0.12, "cog")
        m.xform(H.mul(H.trans(0, 0, cz), H.rot_y(a), H.trans(0, 0, -cz)), s)
    disc(0.16, -0.50, -0.40, "hub", "hub", 10)                 # 허브
    s = len(m.V); m.cyl(0, 0, 0, 0.04, 0.42, "brass", seg=12)  # 핸들 휠 림
    m.xform(H.mul(H.trans(0, -0.60, cz), H.rot_x(R(-90))), s)
    for k in range(3):
        s = len(m.V); m.box(-0.42, 0.42, -0.62, -0.56, -0.02, 0.02, "brass")
        m.xform(H.mul(H.trans(0, 0, cz), H.rot_y(k * math.pi / 3)), s)
    s = len(m.V); m.cyl(0, 0, 0, -0.10, 0.04, "brass", seg=6); m.xform(H.mul(H.trans(0, -0.50, cz), H.rot_x(R(-90))), s)
    # 안쪽에서 덧댄 용접 철판 2개 (못 열게 막음)
    m.box(-1.15, 1.15, -0.50, -0.42, 0.80, 0.98, "weld")
    m.box(-1.15, 1.15, -0.50, -0.42, 1.62, 1.80, "weld")
    for x in (-1.10, 1.10):
        for z in (0.89, 1.71):
            m.box(x - 0.05, x + 0.05, -0.52, -0.50, z - 0.05, z + 0.05, "brass")
    # 경첩 (오른쪽 큰 원통)
    m.cyl(1.05, -0.22, 0.45, 2.15, 0.12, "hinge", cap="hinge", seg=8)
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 6. 해치 문틀 (복도 ↔ 방)
def hatch_frame():
    N = "P2_HatchFrame_01"
    A = H.Atlas(64).cell("frame", 0, 0, 32, 32).cell("hazard", 32, 0, 64, 16).cell("brass", 32, 16, 48, 32).cell("pipe", 0, 32, 32, 64)
    A.fill("frame", MINT, amp=6, grime=0.4, seed=61).bevel("frame", 12, 16); chips(A, "frame", 10, 9)
    A.hazard("hazard", 0, 0, 1, 1, w=4)
    A.fill("brass", BRASS, amp=8, grime=0.1, seed=62)
    A.fill("pipe", METAL, amp=6, grime=0.3, seed=63)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    OW, OH, T, D = 1.35, 2.84, 0.24, 0.20      # 바깥 반폭(=복도 2.7m), 높이, 두께, 반깊이
    m.box(-OW, -OW + T, -D, D, 0.0, OH, "frame")
    m.box(OW - T, OW, -D, D, 0.0, OH, "frame")
    m.box(-OW, OW, -D, D, OH - T - 0.05, OH, "frame")
    m.box(-OW + T, OW - T, -D, D, 0.0, 0.06, "hazard")           # 문턱
    for sx in (-1, 1):                                             # 위 모서리 사선 (해치 느낌)
        x0 = OW - T - 0.30 if sx > 0 else -OW + T
        m.box(x0, x0 + 0.30, -D, D, OH - T - 0.35, OH - T - 0.05, "frame")
    for z in (0.5, 1.4, 2.3):
        for x in (-OW + T / 2, OW - T / 2):
            m.box(x - 0.03, x + 0.03, -D - 0.015, -D, z - 0.03, z + 0.03, "brass")
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 7. 간이 침대
def bunk():
    N = "P2_Bunk_01"
    A = H.Atlas(64).cell("metal", 0, 0, 32, 32).cell("mattress", 32, 0, 64, 32).cell("blanket", 0, 32, 32, 64).cell("pillow", 32, 32, 64, 64)
    A.fill("metal", OLIVE, amp=6, grime=0.4, seed=71); chips(A, "metal", 6, 10)
    A.fill("mattress", (150, 146, 120), amp=6, grime=0.5, seed=72, sw="fabric").hlines("mattress", 0, 1, 5, -10)
    A.rect("mattress", 0.5, 0.4, 0.8, 0.7, (120, 104, 70), amp=6)   # 얼룩
    A.fill("blanket", BLANKET, amp=8, grime=0.3, seed=73, sw="fabric").hlines("blanket", 0.2, 0.3, 2, 18)
    A.fill("pillow", (170, 166, 146), amp=5, grime=0.4, seed=74, sw="fabric")
    img, mat = mat_from(A, N)
    m = H.Mesh()
    L, Wd = 0.98, 0.42
    for x in (-L + 0.03, L - 0.03):
        for y in (-Wd + 0.03, Wd - 0.03):
            m.box(x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0.0, 0.38, "metal")
    m.box(-L, L, -Wd, Wd, 0.30, 0.36, "metal")
    m.box(-L + 0.02, L - 0.02, -Wd + 0.02, Wd - 0.02, 0.36, 0.48, "mattress")
    m.box(-L + 0.10, L - 0.55, -Wd + 0.01, Wd - 0.01, 0.48, 0.53, "blanket", {"front": "blanket"})
    m.box(-L + 0.12, 0.0, -Wd - 0.01, -Wd + 0.06, 0.20, 0.53, "blanket")   # 앞으로 늘어진 담요
    m.box(L - 0.45, L - 0.08, -Wd + 0.08, Wd - 0.08, 0.48, 0.60, "pillow")
    m.box(L - 0.03, L + 0.03, -Wd, Wd, 0.30, 0.80, "metal")                 # 머리판
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 8. 식량 선반
def food_shelf():
    N = "P2_FoodShelf_01"
    A = H.Atlas(128)
    A.cell("shelf", 0, 0, 64, 32).cell("can_a", 64, 0, 96, 32).cell("can_b", 96, 0, 128, 32)
    A.cell("crate", 0, 32, 64, 64).cell("jug", 64, 32, 96, 64).cell("box", 96, 32, 128, 64)
    A.fill("shelf", METAL, amp=6, grime=0.4, seed=81); chips(A, "shelf", 10, 11)
    A.fill("can_a", (150, 150, 140), amp=5, grime=0.2, seed=82).rect("can_a", 0, 0.3, 1, 0.75, (170, 60, 40), amp=4)
    A.text("can_a", 0.1, 0.4, "BEANS", LABEL)
    A.fill("can_b", (150, 150, 140), amp=5, grime=0.2, seed=83).rect("can_b", 0, 0.3, 1, 0.75, (60, 110, 70), amp=4)
    A.fill("crate", (120, 96, 60), amp=8, grime=0.3, seed=84, sw="wood").frame("crate", 0, 0, 1, 1, (70, 54, 34))
    A.text("crate", 0.1, 0.35, "RATION", (40, 32, 20))
    A.fill("jug", (150, 170, 176), amp=5, grime=0.1, seed=85)
    A.fill("box", (170, 150, 110), amp=6, grime=0.3, seed=86).text("box", 0.1, 0.4, "MRE", (60, 40, 20))
    img, mat = mat_from(A, N)
    m = H.Mesh()
    Wd, Dp, Hh = 0.55, 0.42, 1.85
    for x in (-Wd + 0.02, Wd - 0.02):
        for y in (-Dp + 0.02, -0.02):
            m.box(x - 0.02, x + 0.02, y - 0.02, y + 0.02, 0.0, Hh, "shelf")
    levels = (0.08, 0.55, 1.0, 1.45, 1.82)
    for z in levels:
        m.box(-Wd, Wd, -Dp, 0.0, z, z + 0.03, "shelf")
    rng = np.random.default_rng(5)
    for li, z in enumerate(levels[:4]):
        zb = z + 0.03
        if li == 0:
            m.box(-0.50, -0.02, -0.38, -0.04, zb, zb + 0.30, "crate")
            m.cyl(0.25, -0.20, zb, zb + 0.34, 0.14, "jug", cap="jug", seg=8)
        else:
            x = -0.48
            while x < 0.45:
                if rng.random() < 0.25:
                    x += 0.12; continue              # 빈칸 (줄어드는 식량)
                if rng.random() < 0.3:
                    m.box(x, x + 0.22, -0.34, -0.10, zb, zb + 0.16, "box"); x += 0.26
                else:
                    m.cyl(x + 0.05, -0.22, zb, zb + 0.12, 0.045, "can_a" if rng.random() < 0.6 else "can_b", cap="shelf", seg=6); x += 0.11
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 9. 물탱크
def water_tank():
    N = "P2_WaterTank_01"
    A = H.Atlas(64).cell("tank", 0, 0, 32, 32).cell("metal", 32, 0, 64, 32).cell("gauge", 0, 32, 32, 64).cell("brass", 32, 32, 64, 64)
    A.fill("tank", MINT, amp=6, grime=0.45, seed=91, sw="metal"); chips(A, "tank", 12, 12)
    A.rect("tank", 0.1, 0.35, 0.9, 0.5, LABEL, amp=3); A.text("tank", 0.15, 0.38, "H2O", (40, 40, 40))
    A.fill("metal", DARK, amp=5, grime=0.3, seed=92)
    A.fill("gauge", LABEL, amp=3, grime=0, seed=93).circle("gauge", 0.5, 0.5, 0.42, (235, 228, 205)).circle("gauge", 0.5, 0.5, 0.42, DARK, ring=0.05)
    A.rect("gauge", 0.48, 0.5, 0.52, 0.82, RED, amp=0)    # 바늘이 아래 (물 부족)
    A.fill("brass", BRASS, amp=8, grime=0.15, seed=94)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    for x in (-0.3, 0.3):
        for y in (-0.3, 0.3):
            m.box(x - 0.03, x + 0.03, y - 0.03, y + 0.03, 0.0, 0.35, "metal")
    m.cyl(0, 0, 0.32, 1.75, 0.45, "tank", cap="metal", seg=12)
    m.cyl(0, 0, 1.75, 1.85, 0.30, "metal", cap="metal", seg=12)
    for z in (0.6, 1.5):
        m.cyl(0, 0, z, z + 0.05, 0.47, "metal", seg=12)            # 띠
    m.box(-0.10, 0.10, -0.47, -0.44, 1.20, 1.40, "gauge", {"front": "gauge"})
    m.box(-0.03, 0.03, -0.62, -0.42, 0.45, 0.51, "brass")          # 꼭지 관
    m.box(-0.03, 0.03, -0.62, -0.56, 0.36, 0.51, "brass")
    m.box(-0.05, 0.05, -0.62, -0.52, 0.52, 0.56, "brass")          # 손잡이
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 10~15. 생활 가구·가전
def fridge():
    N = "P2_Fridge_01"
    A = H.Atlas(64).cell("body", 0, 0, 32, 64).cell("dark", 32, 0, 64, 16).cell("brass", 32, 16, 48, 32).cell("grille", 32, 32, 64, 64)
    A.fill("body", (186, 184, 166), amp=6, grime=0.45, seed=101).bevel("body", 14, 18); chips(A, "body", 14, 21)
    A.hlines("body", 0.34, 0.36, 2, -30)                                    # 위아래 칸 경계
    A.fill("dark", DARK, amp=4, grime=0.2, seed=102)
    A.fill("brass", (200, 200, 190), amp=6, grime=0.1, seed=103)
    A.fill("grille", DARK, amp=4, grime=0.3, seed=104).hlines("grille", 0.1, 0.9, 3, 18)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.36, 0.36, -0.62, 0.0, 0.06, 1.62, "body")
    m.box(-0.34, 0.34, -0.60, -0.02, 0.0, 0.06, "grille")
    s = len(m.V); m.cyl(0, 0, 0, 0.72, 0.31, "body", cap="body", seg=8)   # 둥근 윗면 (50년대 냉장고)
    m.xform(H.mul(H.trans(-0.36, -0.31, 1.62), H.rot_y(R(90))), s)
    for z0, z1 in ((0.75, 1.05), (1.25, 1.45)):
        m.box(0.24, 0.30, -0.68, -0.62, z0, z1, "brass")                       # 손잡이
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


def stove_counter():
    N = "P2_StoveCounter_01"
    A = H.Atlas(64).cell("counter", 0, 0, 32, 32).cell("top", 32, 0, 64, 32).cell("burner", 0, 32, 16, 48)
    A.cell("pot", 16, 32, 32, 48).cell("knob", 32, 32, 48, 48).cell("dark", 48, 32, 64, 48).cell("kettle", 0, 48, 32, 64)
    A.fill("counter", MINT, amp=6, grime=0.4, seed=111).bevel("counter", 12, 16); chips(A, "counter", 10, 22)
    A.vlines("counter", 0.49, 0.51, 2, -30)
    A.fill("top", METAL, amp=6, grime=0.3, seed=112)
    A.fill("burner", BLACK, amp=2, grime=0).circle("burner", 0.5, 0.5, 0.4, (150, 60, 30), ring=0.12)
    A.fill("pot", (120, 120, 116), amp=6, grime=0.3, seed=113)
    A.fill("knob", BLACK, amp=3, grime=0, seed=114)
    A.fill("dark", DARK, amp=4, grime=0.3, seed=115)
    A.fill("kettle", (170, 70, 50), amp=6, grime=0.3, seed=116)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.60, 0.60, -0.55, 0.0, 0.0, 0.86, "counter", {"top": "top"})
    m.box(-0.58, 0.58, -0.53, -0.02, 0.0, 0.08, "dark")
    for x in (-0.30, 0.0):                                                   # 핫플레이트 2구
        m.box(x - 0.12, x + 0.12, -0.40, -0.16, 0.86, 0.88, "burner", {"top": "burner"})
    for x in (-0.30, 0.0):
        m.box(x - 0.025, x + 0.025, -0.575, -0.55, 0.74, 0.79, "knob")
    m.cyl(-0.30, -0.28, 0.88, 1.00, 0.10, "pot", cap="pot", seg=8)          # 냄비
    m.cyl(0.32, -0.30, 0.86, 1.02, 0.08, "kettle", cap="kettle", seg=8, r1=0.05)  # 주전자
    m.box(0.36, 0.44, -0.32, -0.28, 0.96, 0.99, "kettle")
    m.box(-0.60, 0.60, -0.08, 0.0, 1.30, 1.34, "top")                       # 벽 선반
    for x in (-0.4, -0.25, 0.3, 0.45):
        m.cyl(x, -0.04, 1.34, 1.44, 0.04, "pot", cap="pot", seg=6)
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


def table():
    N = "P2_Table_01"
    A = H.Atlas(32).cell("top", 0, 0, 16, 16).cell("leg", 16, 0, 32, 16).cell("cloth", 0, 16, 32, 32)
    A.fill("top", (150, 120, 80), amp=6, grime=0.3, seed=121, sw="wood")
    A.fill("leg", METAL, amp=5, grime=0.2, seed=122)
    A.fill("cloth", (170, 166, 140), amp=4, grime=0.4, seed=123)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.45, 0.45, -0.35, 0.35, 0.72, 0.76, "top")
    for x in (-0.40, 0.40):
        for y in (-0.30, 0.30):
            m.box(x - 0.025, x + 0.025, y - 0.025, y + 0.025, 0.0, 0.72, "leg")
    m.box(-0.15, 0.20, -0.20, 0.10, 0.76, 0.765, "cloth")                   # 접시 받침 천
    m.cyl(0.0, -0.05, 0.765, 0.78, 0.09, "leg", cap="leg", seg=8)           # 빈 접시
    m.cyl(0.25, 0.15, 0.76, 0.86, 0.04, "leg", cap="leg", seg=6)            # 컵
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


def stool():
    N = "P2_Stool_01"
    A = H.Atlas(32).cell("seat", 0, 0, 16, 16).cell("leg", 16, 0, 32, 16)
    A.fill("seat", (120, 70, 50), amp=6, grime=0.35, seed=131, sw="fabric")
    A.fill("leg", METAL, amp=5, grime=0.2, seed=132)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.cyl(0, 0, 0.42, 0.48, 0.18, "seat", cap="seat", seg=8)
    for k in range(3):
        a = 2 * math.pi * k / 3
        s = len(m.V); m.box(-0.02, 0.02, -0.02, 0.02, 0.0, 0.43, "leg")
        m.xform(H.mul(H.trans(0.14 * math.cos(a), 0.14 * math.sin(a), 0), H.rot_z(a)), s)
    m.cyl(0, 0, 0.18, 0.20, 0.13, "leg", seg=8, caps=(False, False))
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


def radio():
    N = "P2_Radio_01"
    A = H.Atlas(32).cell("case", 0, 0, 16, 16).cell("grille", 16, 0, 32, 16).cell("dial", 0, 16, 16, 32).cell("knob", 16, 16, 32, 32)
    A.fill("case", (120, 84, 54), amp=6, grime=0.3, seed=141, sw="wood")
    A.fill("grille", (190, 170, 130), amp=4, grime=0.2, seed=142).hlines("grille", 0.1, 0.9, 2, -30)
    A.fill("dial", (220, 190, 120), amp=3, grime=0, seed=143).rect("dial", 0.48, 0.1, 0.54, 0.9, RED, amp=0)
    A.fill("knob", BLACK, amp=3, grime=0, seed=144)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.18, 0.18, -0.09, 0.09, 0.0, 0.22, "case")
    quad_front(m, -0.15, 0.02, 0.04, 0.19, -0.091, "grille")
    quad_front(m, 0.05, 0.16, 0.12, 0.19, -0.091, "dial")
    for x in (0.07, 0.13):
        knob(m, x, -0.09, 0.07, 0.02, 0.02, "knob", seg=6)
    m.box(0.12, 0.14, -0.01, 0.01, 0.22, 0.50, "knob")                      # 안테나
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


def footlocker():
    N = "P2_FootLocker_01"
    A = H.Atlas(32).cell("box", 0, 0, 16, 16).cell("trim", 16, 0, 32, 16).cell("plate", 0, 16, 32, 24)
    A.fill("box", OLIVE, amp=6, grime=0.4, seed=151); chips(A, "box", 6, 23)
    A.fill("trim", METAL, amp=5, grime=0.2, seed=152)
    A.fill("plate", LABEL, amp=3, grime=0.2, seed=153)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    m.box(-0.40, 0.40, -0.22, 0.22, 0.0, 0.40, "box")
    m.box(-0.41, 0.41, -0.23, 0.23, 0.36, 0.42, "trim")
    m.box(-0.04, 0.04, -0.235, -0.22, 0.28, 0.36, "trim")                   # 걸쇠
    quad_front(m, -0.20, 0.10, 0.12, 0.22, -0.221, "plate")
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


# ================================================================ 16. 기록 보관 선반 (단서 종이 받침대)
def _archive(N, variant):
    A = H.Atlas(128)
    A.cell("frame", 0, 0, 32, 64).cell("cab", 32, 0, 64, 32).cell("ledge", 32, 32, 64, 64)
    A.cell("box", 64, 0, 96, 32).cell("box2", 96, 0, 128, 32).cell("binder", 64, 32, 96, 64).cell("binder2", 96, 32, 128, 64)
    A.cell("paper", 0, 64, 32, 96).cell("plate", 32, 64, 64, 80).cell("brass", 64, 64, 80, 80)
    A.fill("frame", OLIVE, amp=6, grime=0.4, seed=161); chips(A, "frame", 8, 31)
    A.fill("cab", MINT, amp=6, grime=0.4, seed=162).bevel("cab", 12, 16); chips(A, "cab", 10, 32)
    A.vlines("cab", 0.49, 0.51, 2, -30); A.rect("cab", 0.40, 0.45, 0.46, 0.55, BRASS, amp=2); A.rect("cab", 0.54, 0.45, 0.60, 0.55, BRASS, amp=2)
    A.fill("ledge", METAL, amp=6, grime=0.3, seed=163)
    A.fill("box", (150, 130, 96), amp=6, grime=0.3, seed=164).rect("box", 0.3, 0.35, 0.7, 0.6, LABEL, amp=2)
    A.fill("box2", (120, 110, 90), amp=6, grime=0.35, seed=165).rect("box2", 0.25, 0.3, 0.75, 0.55, LABEL, amp=2)
    A.fill("binder", (60, 80, 100), amp=5, grime=0.2, seed=166).rect("binder", 0.3, 0.15, 0.7, 0.35, LABEL, amp=2)
    A.fill("binder2", (120, 50, 40), amp=5, grime=0.2, seed=167).rect("binder2", 0.3, 0.15, 0.7, 0.35, LABEL, amp=2)
    A.fill("paper", (200, 194, 172), amp=3, grime=0.3, seed=168).hlines("paper", 0.2, 0.8, 3, -24, 0.15, 0.85)
    A.fill("plate", LABEL, amp=3, grime=0.2, seed=169).text("plate", 0.06, 0.25, "RECORDS", (40, 40, 40))
    A.fill("brass", BRASS, amp=8, grime=0.1, seed=170)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    Wd, Dp = 0.60, 0.42
    for x in (-Wd, Wd - 0.04):                                               # 옆 기둥
        m.box(x, x + 0.04, -Dp, 0.0, 0.0, 2.10, "frame")
    m.box(-Wd, Wd, -0.03, 0.0, 0.9, 2.10, "frame")                             # 뒷판
    m.box(-Wd + 0.04, Wd - 0.04, -Dp + 0.02, 0.0, 0.0, 0.88, "cab")           # 아래 수납장
    m.box(-Wd, Wd, -Dp - 0.14, 0.0, 0.88, 0.92, "ledge")                       # 종이 펼치는 선반판 (앞으로 튀어나옴)
    m.box(-0.15, 0.15, -Dp - 0.145, -Dp - 0.14, 0.82, 0.88, "plate")
    rng = np.random.default_rng(7 + variant)
    for z in (1.30, 1.70, 2.06):
        m.box(-Wd + 0.04, Wd - 0.04, -Dp + 0.04, -0.03, z, z + 0.03, "ledge")
    for zi, z in enumerate((0.92, 1.33, 1.73)):
        if zi == 0:
            continue                                                          # 선반판 위는 단서 종이 자리로 비워 둠
        x = -Wd + 0.07
        while x < Wd - 0.12:
            r = rng.random()
            if variant == 2 and r < 0.35:
                x += 0.15; continue                                           # 빈칸
            if r < 0.45:
                w = 0.30; m.box(x, x + w, -0.34, -0.05, z, z + 0.24, "box" if rng.random() < 0.6 else "box2"); x += w + 0.02
            else:
                n = int(rng.integers(2, 5))
                for _ in range(n):
                    if x > Wd - 0.12: break
                    m.box(x, x + 0.06, -0.30, -0.05, z, z + 0.30, "binder" if rng.random() < 0.6 else "binder2"); x += 0.065
                x += 0.04
    if variant == 2:                                                          # 쓰러진 바인더·바닥 상자
        s = len(m.V); m.box(0.0, 0.30, -0.30, -0.05, 0.0, 0.06, "binder2"); m.xform(H.trans(-0.2, 0, 1.73 + 0.03), s)
        m.box(-0.35, 0.05, -0.80, -0.48, 0.0, 0.26, "box2")
    m.box(-0.35, 0.10, -0.38, -0.08, 2.09, 2.11, "paper")                     # 맨 위 종이 더미
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


def archive_shelf():
    _archive("P2_ArchiveShelf_01", 1)


def archive_shelf2():
    _archive("P2_ArchiveShelf_02", 2)


# ================================================================ 17. 큰 CRT 2종 + 하나로 이어진 반원 콘솔 (2026-11-26)
def wall_crt_side():
    wall_crt("P2_WallCRT_02", 1.00, 1.60)      # 좌우 벽용 2.0 × 1.6


def wall_crt_main():
    wall_crt("P2_WallCRT_03", 1.40, 1.60)      # 가운데 벽용 2.8 × 1.6


def console_arc():
    """원점 = 의자 자리. 세 칸(±45°)이 이음매 없이 이어진 다각형 호. 정면(앉는 쪽)은 원점을 향함."""
    N = "P2_ConsoleArc_01"
    RF, RB = 0.95, 1.75                       # 앞·뒤 반지름 (평면 거리)
    H0, H1, KICK = 0.74, 0.92, 0.10
    m = H.Mesh()
    half = R(22.5)
    def col(a, r):                            # 다각형 모서리 점 (면이 평평하도록 r/cos)
        rr = r / math.cos(half)
        return (rr * math.cos(a), rr * math.sin(a))
    angs = [R(45), R(90), R(135)]             # 오른쪽(+X 쪽)·가운데(+Y)·왼쪽
    def prism(r0, r1, z0, z1a, z1b, role, top_role, ends):
        """r0(앞)~r1(뒤) 다각형 고리 띠. 윗면은 앞 z1a → 뒤 z1b 경사."""
        b = len(m.V)
        edges = [angs[0] - half, angs[0] + half, angs[1] + half, angs[2] + half]
        for a in edges:
            fx, fy = col(a, r0); bx, by = col(a, r1)
            m.V += [(fx, fy, z0), (fx, fy, z1a), (bx, by, z0), (bx, by, z1b)]
        for i in range(3):
            q = b + i * 4; w = q + 4
            m.face([q + 1, w + 1, w, q], role)                 # 앞 (원점 쪽을 향함)
            m.face([q + 3, w + 3, w + 1, q + 1], top_role)     # 윗면 (위를 향함)
            m.face([w + 3, q + 3, q + 2, w + 2], role)         # 뒤 (바깥을 향함)
        if ends:
            for q, flip in ((b, True), (b + 12, False)):
                f = [q, q + 1, q + 3, q + 2]
                m.face(list(reversed(f)) if flip else f, role)
    prism(RF + 0.08, RB, 0.0, KICK, KICK, "base", "base", True)        # 들어간 발판
    prism(RF, RB, KICK, H0, H1, "console", "top", True)                # 본체 + 경사 윗판
    def on_top(a, along, start):
        """방금 만든 디테일(세그먼트 로컬: x=옆, y=0, z=0 기준)을 각도 a 칸의 윗판 위로"""
        ang = math.atan2(H1 - H0, RB - RF)
        y = RF + (RB - RF) * along; z = H0 + (H1 - H0) * along + 0.004
        m.xform(H.mul(H.rot_z(a - R(90)), H.trans(0, y, z), H.rot_x(ang)), start)
    # 옆 칸: 토글 줄 + 계기판 3개
    for a in (angs[0], angs[2]):
        s = len(m.V); m.box(-0.30, 0.30, -0.08, 0.08, 0.0, 0.02, "toggles", {"top": "toggles"}); on_top(a, 0.28, s)
        for x in (-0.22, 0.0, 0.22):
            s = len(m.V); m.box(x - 0.08, x + 0.08, -0.08, 0.08, 0.0, 0.012, "gauge", {"top": "gauge"}); on_top(a, 0.75, s)
    # 가운데 칸: 낮은 받침대(작은 화면) + 레버
    a = angs[1]
    s = len(m.V); m.box(-0.40, 0.40, RB - 0.16, RB, H1 - 0.02, H1 + 0.30, "console")
    m.box(-0.12, 0.12, RB - 0.17, RB - 0.16, H1 + 0.01, H1 + 0.05, "plate")
    m.cyl(0.50, RF + 0.25, H0, H0 + 0.36, 0.018, "lever", seg=6)
    m.box(0.47, 0.53, RF + 0.22, RF + 0.28, H0 + 0.36, H0 + 0.42, "knob")
    m.box(0.45, 0.55, RF + 0.20, RF + 0.30, H0 + 0.02, H0 + 0.07, "brass")
    s2 = len(m.V); m.box(-0.62, -0.38, -0.08, 0.08, 0.0, 0.02, "toggles", {"top": "toggles"}); on_top(a, 0.35, s2)
    body = H.build_object(bpy, sc, N, m, CON, CON_MAT)
    km = H.Mesh(); s = len(km.V)
    km.box(-0.28, 0.28, -0.11, 0.11, 0.0, 0.025, "keys", {"top": "keys"})
    ang = math.atan2(H1 - H0, RB - RF)
    km.xform(H.mul(H.trans(0, RF + (RB - RF) * 0.35, H0 + (H1 - H0) * 0.35 + 0.004), H.rot_x(ang)), s)
    ko = H.build_object(bpy, sc, "InputPanel", km, CON, CON_MAT, parent=body)
    so, sm = screen_obj("Screen", -0.36, 0.36, H1 + 0.03, H1 + 0.27, RB - 0.161, body)
    finish(N, [body, ko, so], [m, km, sm])


# ================================================================ 18. 천장 환풍기 + 테이프 릴 메인프레임 (2026-11-26)
def ceiling_fan():
    """원점 = 천장면 가운데(위쪽 z=0), 아래(-z)로 내려옴. 날개는 자식 'Blades'(가운데 피벗, 돌릴 수 있게)."""
    N = "P2_CeilingFan_01"
    A = H.Atlas(64).cell("housing", 0, 0, 32, 32).cell("grille", 32, 0, 64, 32).cell("dark", 0, 32, 32, 48).cell("blade", 32, 32, 64, 48).cell("brass", 0, 48, 16, 64)
    A.fill("housing", METAL, amp=6, grime=0.45, seed=181).bevel("housing", 12, 16); chips(A, "housing", 8, 41)
    A.fill("grille", DARK, amp=4, grime=0.3, seed=182).hlines("grille", 0.05, 0.95, 3, 26)
    A.fill("dark", BLACK, amp=2, grime=0, seed=183)
    A.fill("blade", (110, 112, 104), amp=6, grime=0.4, seed=184)
    A.fill("brass", BRASS, amp=6, grime=0.1, seed=185)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    S, T = 0.45, 0.10
    m.box(-S, S, -S, S, -T, 0.0, "housing", {"top": None, "bottom": "dark"})       # 바닥면은 안쪽 어둠
    for (x0, x1, y0, y1) in ((-S - 0.05, S + 0.05, -S - 0.05, -S), (-S - 0.05, S + 0.05, S, S + 0.05),
                             (-S - 0.05, -S, -S, S), (S, S + 0.05, -S, S)):
        m.box(x0, x1, y0, y1, -T - 0.03, 0.0, "housing")                          # 테두리
    for i in range(7):                                                            # 앞 창살
        y = -S + 0.06 + i * (2 * S - 0.12) / 6
        m.box(-S, S, y - 0.012, y + 0.012, -T - 0.035, -T - 0.01, "grille")
    for x in (-S, S):
        for y in (-S, S):
            m.box(x - 0.02, x + 0.02, y - 0.02, y + 0.02, -T - 0.045, -T - 0.03, "brass")
    body = H.build_object(bpy, sc, N, m, A, mat)
    bm = H.Mesh()
    bm.cyl(0, 0, -0.06, -0.02, 0.06, "brass", cap="brass", seg=8)
    for k_ in range(4):
        s_ = len(bm.V); bm.box(0.05, 0.38, -0.06, 0.06, -0.05, -0.035, "blade")
        bm.xform(H.mul(H.rot_z(k_ * math.pi / 2), H.rot_x(R(12))), s_)
    bo = H.build_object(bpy, sc, "Blades", bm, A, mat, parent=body, pivot=(0, 0, -0.04))
    finish(N, [body, bo], [m, bm])


def mainframe():
    """테이프 릴 메인프레임 (폴아웃 풍). 뒷면 y=0, 앞으로 -y."""
    N = "P2_Mainframe_01"
    A = H.Atlas(128)
    A.cell("cab", 0, 0, 64, 64).cell("window", 64, 0, 96, 32).cell("reel", 96, 0, 128, 32).cell("panel", 64, 32, 128, 64)
    A.cell("dark", 0, 64, 32, 96).cell("plate", 32, 64, 96, 80).cell("vent", 96, 64, 128, 96)
    A.fill("cab", CREAM, amp=6, grime=0.4, seed=191).bevel("cab", 14, 18); chips(A, "cab", 16, 42)
    A.fill("window", (30, 36, 36), amp=3, grime=0.1, seed=192)
    A.fill("reel", (160, 160, 150), amp=4, grime=0.1, seed=193).circle("reel", 0.5, 0.5, 0.45, (60, 52, 40)).circle("reel", 0.5, 0.5, 0.18, (170, 170, 160)).circle("reel", 0.5, 0.5, 0.06, BLACK)
    A.fill("panel", MINT, amp=5, grime=0.3, seed=194).frame("panel", 0, 0, 1, 1, DARK)
    rng = np.random.default_rng(3)
    for r_ in range(4):
        for c_ in range(10):
            if rng.random() < 0.7:
                A.dot("panel", 0.06 + c_ * 0.095, 0.15 + r_ * 0.2, [GREEN, AMBER, RED, (200, 200, 190)][int(rng.integers(0, 4))])
    A.fill("dark", DARK, amp=4, grime=0.3, seed=195)
    A.fill("plate", LABEL, amp=3, grime=0.2, seed=196).text("plate", 0.04, 0.25, "DATA CORE", (40, 40, 40))
    A.fill("vent", OLIVE, amp=5, grime=0.3, seed=197).hlines("vent", 0.1, 0.9, 3, -22, 0.1, 0.9)
    img, mat = mat_from(A, N)
    m = H.Mesh()
    W, Dp, Hh = 0.42, 0.62, 2.0
    m.box(-W, W, -Dp, 0.0, 0.08, Hh, "cab", {"back": None})
    m.box(-W + 0.02, W - 0.02, -Dp + 0.02, -0.02, 0.0, 0.08, "dark")
    m.box(-W + 0.04, W - 0.04, -Dp - 0.01, -Dp, 1.05, 1.80, "window", {"front": "window"})      # 릴 창
    for x in (-0.18, 0.18):                                                                         # 릴 2개 (창 안)
        s_ = len(m.V); m.cyl(0, 0, 0, 0.012, 0.15, "reel", cap="reel", seg=10)
        m.xform(H.mul(H.trans(x, -Dp - 0.012, 1.45), H.rot_x(R(90))), s_)
    m.box(-W + 0.04, W - 0.04, -Dp - 0.01, -Dp, 0.55, 0.95, "panel", {"front": "panel"})         # 불빛 패널
    m.box(-0.30, 0.30, -Dp - 0.012, -Dp, 1.86, 1.94, "plate", {"front": "plate"})
    m.box(-W + 0.04, W - 0.04, -Dp - 0.01, -Dp, 0.15, 0.45, "vent", {"front": "vent"})
    for x in (-W + 0.03, W - 0.03):                                                                 # 손잡이 레일
        m.box(x - 0.015, x + 0.015, -Dp - 0.04, -Dp, 1.0, 1.85, "dark")
    body = H.build_object(bpy, sc, N, m, A, mat)
    finish(N, [body], [m])


ERR = {}
ONLY = globals().get('ONLY')
for fn in (wall_crt, console_main, console_seg, swivel_chair, vault_door, hatch_frame, bunk, food_shelf, water_tank,
           fridge, stove_counter, table, stool, radio, footlocker, archive_shelf, archive_shelf2,
           wall_crt_side, wall_crt_main, console_arc, ceiling_fan, mainframe):
    if ONLY and fn.__name__ not in ONLY:
        continue
    try:
        fn()
    except Exception:
        import traceback
        ERR[fn.__name__] = traceback.format_exc()[-1500:]

if not ERR:
    try:
        H.render_preview(bpy, win, sc, GROUPS, PRE, res=320)
    except Exception:
        import traceback
        ERR["preview"] = traceback.format_exc()[-1500:]
