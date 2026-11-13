"""HOUSTON PSX prop toolkit (Blender 4.x/5.x).
Atlas painter (numpy) + simple mesh builder + export/preview helpers.
Conventions: 1 unit = 1 m, front faces -Y, pivot bottom-center unless noted.
"""
import os, math
import numpy as np

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 15.0) - 0.5

FONT = {
 'A': "010101111101101", 'B': "110101110101110", 'C': "011100100100011", 'D': "110101101101110",
 'E': "111100110100111", 'F': "111100110100100", 'G': "011100101101011", 'H': "101101111101101",
 'I': "111010010010111", 'K': "101101110101101", 'L': "100100100100111", 'M': "101111111101101",
 'N': "110101101101101", 'O': "111101101101111", 'P': "110101110100100", 'R': "110101110101101",
 'S': "011100010001110", 'T': "111010010010010", 'U': "101101101101111", 'V': "101101101101010",
 'X': "101101010101101", 'Y': "101101010010010", 'W': "101101111111101",
 '0': "010101101101010", '1': "010110010010111", '2': "110001010100111", '3': "110001010001110",
 '4': "101101111001001", '5': "111100110001110", '6': "011100111101111", '7': "111001010010010",
 '8': "111101111101111", '9': "111101111001110", '-': "000000111000000", '.': "000000000000010",
 ' ': "000000000000000", '+': "000010111010000", '!': "010010010000010", '%': "101001010100101",
 '/': "001001010100100", ':': "000010000010000",
}


def _hash(xx, yy, seed=0):
    h = (xx.astype(np.uint64) * np.uint64(73856093)) ^ (yy.astype(np.uint64) * np.uint64(19349663)) ^ np.uint64(seed * 83492791 + 1)
    h = (h ^ (h >> np.uint64(13))) * np.uint64(1274126177)
    h = h & np.uint64(0xFFFFFFFF)
    return ((h >> np.uint64(8)) & np.uint64(0xFFFF)).astype(float) / 65535.0


class Atlas:
    def __init__(self, size):
        self.W = size
        self.A = np.zeros((size, size, 4), float)
        self.A[..., 3] = 255
        self.cells = {}

    # ---- layout
    def cell(self, name, x0, y0, x1, y1):
        self.cells[name] = (x0, y0, x1, y1)
        return self

    def grid(self, names, n):
        s = self.W // n
        for i, nm in enumerate(names):
            if nm:
                x, y = (i % n) * s, (i // n) * s
                self.cells[nm] = (x, y, x + s, y + s)
        return self

    def _px(self, name, fx0, fy0, fx1, fy1):
        x0, y0, x1, y1 = self.cells[name]
        w, h = x1 - x0, y1 - y0
        return (x0 + int(round(fx0 * w)), y0 + int(round(fy0 * h)),
                x0 + max(int(round(fx0 * w)) + 1, int(round(fx1 * w))),
                y0 + max(int(round(fy0 * h)) + 1, int(round(fy1 * h))))

    # ---- painting (fractions are inside the cell, y=0 top)
    def fill(self, name, color, amp=10, grad=12, speck=0.05, grime=0.3, seed=0, region=(0, 0, 1, 1)):
        x0, y0, x1, y1 = self._px(name, *region)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        t = (yy - y0) / max(1, (y1 - y0) - 1)
        d = BAYER[yy % 4, xx % 4] * amp + (0.5 - t) * grad
        r = _hash(xx, yy, seed)
        r2 = _hash(xx + 7, yy + 3, seed + 1)
        d = d + np.where(r < speck * 0.5, 16, 0) - np.where((r >= speck * 0.5) & (r < speck), 18, 0)
        d = d - grime * np.clip((t - 0.55) / 0.45, 0, 1) * 40 * (0.6 + 0.4 * r2)
        self.A[y0:y1, x0:x1, :3] = np.clip(np.array(color, float) + d[..., None], 0, 255)
        return self

    def bevel(self, name, hi=20, lo=24, region=(0, 0, 1, 1)):
        x0, y0, x1, y1 = self._px(name, *region)
        A = self.A
        A[y0, x0:x1, :3] += hi
        A[y0:y1, x0, :3] += hi * 0.5
        A[y1 - 1, x0:x1, :3] -= lo
        A[y0:y1, x1 - 1, :3] -= lo * 0.5
        np.clip(A, 0, 255, out=A)
        return self

    def rect(self, name, fx0, fy0, fx1, fy1, color, amp=6, seed=3):
        x0, y0, x1, y1 = self._px(name, fx0, fy0, fx1, fy1)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        d = BAYER[yy % 4, xx % 4] * amp
        self.A[y0:y1, x0:x1, :3] = np.clip(np.array(color, float) + d[..., None], 0, 255)
        return self

    def shade(self, name, fx0, fy0, fx1, fy1, delta):
        x0, y0, x1, y1 = self._px(name, fx0, fy0, fx1, fy1)
        self.A[y0:y1, x0:x1, :3] = np.clip(self.A[y0:y1, x0:x1, :3] + delta, 0, 255)
        return self

    def frame(self, name, fx0, fy0, fx1, fy1, color):
        x0, y0, x1, y1 = self._px(name, fx0, fy0, fx1, fy1)
        c = np.array(color, float)
        self.A[y0, x0:x1, :3] = c; self.A[y1 - 1, x0:x1, :3] = c
        self.A[y0:y1, x0, :3] = c; self.A[y0:y1, x1 - 1, :3] = c
        return self

    def hlines(self, name, fy0, fy1, step, delta, fx0=0, fx1=1):
        x0, y0, x1, y1 = self._px(name, fx0, fy0, fx1, fy1)
        for y in range(y0, y1, step):
            self.A[y, x0:x1, :3] = np.clip(self.A[y, x0:x1, :3] + delta, 0, 255)
        return self

    def vlines(self, name, fx0, fx1, step, delta, fy0=0, fy1=1):
        x0, y0, x1, y1 = self._px(name, fx0, fy0, fx1, fy1)
        for x in range(x0, x1, step):
            self.A[y0:y1, x, :3] = np.clip(self.A[y0:y1, x, :3] + delta, 0, 255)
        return self

    def hazard(self, name, fx0, fy0, fx1, fy1, w=3, c1=(196, 160, 44), c2=(34, 32, 30)):
        x0, y0, x1, y1 = self._px(name, fx0, fy0, fx1, fy1)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        m = ((xx + yy) // w) % 2 == 0
        col = np.where(m[..., None], np.array(c1, float), np.array(c2, float))
        col = col + (BAYER[yy % 4, xx % 4] * 8)[..., None]
        self.A[y0:y1, x0:x1, :3] = np.clip(col, 0, 255)
        return self

    def dot(self, name, fx, fy, color, size=1):
        x0, y0, x1, y1 = self.cells[name]
        x = x0 + int(fx * (x1 - x0)); y = y0 + int(fy * (y1 - y0))
        self.A[y:y + size, x:x + size, :3] = np.array(color, float)
        return self

    def text(self, name, fx, fy, s, color, scale=1, spacing=1):
        x0, y0, x1, y1 = self.cells[name]
        x = x0 + int(fx * (x1 - x0)); y = y0 + int(fy * (y1 - y0))
        c = np.array(color, float)
        for ch in s.upper():
            g = FONT.get(ch, FONT[' '])
            for i, b in enumerate(g):
                if b == '1':
                    gx, gy = x + (i % 3) * scale, y + (i // 3) * scale
                    if gx < self.W and gy < self.W:
                        self.A[gy:gy + scale, gx:gx + scale, :3] = c
            x += (3 + spacing) * scale
        return self

    def cross(self, name, fcx, fcy, fsize, color):
        h = fsize / 2; t = fsize / 6
        self.rect(name, fcx - h, fcy - t, fcx + h, fcy + t, color, amp=4)
        self.rect(name, fcx - t, fcy - h, fcx + t, fcy + h, color, amp=4)
        return self

    def circle(self, name, fcx, fcy, fr, color, ring=None):
        x0, y0, x1, y1 = self.cells[name]
        w = x1 - x0
        cx, cy, r = x0 + fcx * w, y0 + fcy * (y1 - y0), fr * w
        yy, xx = np.mgrid[y0:y1, x0:x1]
        dd = np.sqrt((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2)
        m = dd <= r
        if ring is not None:
            m = m & (dd >= r - ring)
        self.A[y0:y1, x0:x1, :3][m] = np.array(color, float)
        return self

    def alpha(self, name, a, region=(0, 0, 1, 1)):
        x0, y0, x1, y1 = self._px(name, *region)
        self.A[y0:y1, x0:x1, 3] = a
        return self

    # ---- output
    def to_image(self, bpy, name, path):
        img = bpy.data.images.get(name)
        if img is not None:
            bpy.data.images.remove(img)
        img = bpy.data.images.new(name, self.W, self.W, alpha=True)
        px = (self.A[::-1] / 255.0).astype(np.float32).ravel()
        img.pixels.foreach_set(px)
        img.filepath_raw = path
        img.file_format = 'PNG'
        img.save()
        return img


def _newell(pts):
    n = np.zeros(3)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n += np.array([(a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])])
    return n


class Mesh:
    def __init__(self):
        self.V, self.F, self.R, self.U = [], [], [], []

    def begin(self):
        return (len(self.V), len(self.F))

    def end(self, mark, closed=True, double=False):
        v0, f0 = mark
        if closed:
            c = np.mean(np.array(self.V[v0:]), axis=0)
            for i in range(f0, len(self.F)):
                pts = np.array([self.V[j] for j in self.F[i]])
                if np.dot(_newell(pts), pts.mean(0) - c) < 0:
                    self.F[i] = tuple(reversed(self.F[i]))
                    if self.U[i] is not None:
                        self.U[i] = list(reversed(self.U[i]))
        if double:
            for i in range(f0, len(self.F)):
                self.F.append(tuple(reversed(self.F[i])))
                self.R.append(self.R[i])
                self.U.append(None if self.U[i] is None else list(reversed(self.U[i])))
        return self

    def face(self, idx, role, uv=None):
        self.F.append(tuple(idx)); self.R.append(role); self.U.append(uv)

    def box(self, x0, x1, y0, y1, z0, z1, role, over=None):
        over = over or {}
        m = self.begin(); b = len(self.V)
        self.V += [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
                   (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
        q = {'front': (0, 1, 2, 3), 'back': (5, 4, 7, 6), 'left': (4, 0, 3, 7), 'right': (1, 5, 6, 2),
             'top': (3, 2, 6, 7), 'bottom': (4, 5, 1, 0)}
        for k, f in q.items():
            if k in over and over[k] is None:
                continue
            self.face([b + i for i in f], over.get(k, role))
        return self.end(m)

    def cyl(self, cx, cy, z0, z1, r0, side, cap=None, seg=8, r1=None, caps=(True, True), rot=0.0):
        r1 = r0 if r1 is None else r1
        m = self.begin(); b = len(self.V)
        for k in range(seg):
            a = rot + 2 * math.pi * k / seg
            self.V.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0))
        for k in range(seg):
            a = rot + 2 * math.pi * k / seg
            self.V.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1))
        for k in range(seg):
            k2 = (k + 1) % seg
            self.face([b + k, b + k2, b + seg + k2, b + seg + k], side,
                      [(k / seg, 0), ((k + 1) / seg, 0), ((k + 1) / seg, 1), (k / seg, 1)])
        if cap is not None:
            if caps[0] and r0 > 1e-6:
                self.face([b + k for k in range(seg)], cap)
            if caps[1] and r1 > 1e-6:
                self.face([b + seg + k for k in range(seg)], cap)
        return self.end(m)

    def xform(self, M, start):
        M = np.array(M, float)
        for i in range(start, len(self.V)):
            v = M @ np.array([*self.V[i], 1.0])
            self.V[i] = tuple(v[:3])
        return self

    def extrude_profile(self, prof, x0, x1, role, cap=None, closed=False, double=False):
        """prof: list of (y,z) points (open polyline unless closed). Extruded along X."""
        m = self.begin(); b = len(self.V); n = len(prof)
        for (y, z) in prof: self.V.append((x0, y, z))
        for (y, z) in prof: self.V.append((x1, y, z))
        segs = n if closed else n - 1
        for k in range(segs):
            k2 = (k + 1) % n
            self.face([b + k, b + n + k, b + n + k2, b + k2], role,
                      [(0, k / segs), (1, k / segs), (1, (k + 1) / segs), (0, (k + 1) / segs)])
        if cap is not None:
            self.face([b + k for k in range(n)], cap)
            self.face([b + n + k for k in reversed(range(n))], cap)
        return self.end(m, closed=closed and not double, double=double)

    def tris(self):
        return sum(len(f) - 2 for f in self.F)


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def trans(x, y, z):
    return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]


def mul(*Ms):
    R = np.eye(4)
    for M in Ms:
        R = R @ np.array(M, float)
    return R


# ------------------------------------------------------------ Blender side
def make_material(bpy, name, img, alpha=False, emissive=False):
    m = bpy.data.materials.get(name)
    if m is not None:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.interpolation = 'Closest'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 1.0
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.1
    if alpha:
        nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
        for attr, val in (('surface_render_method', 'BLENDED'), ('blend_method', 'BLEND')):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    if emissive:
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.0
    return m


def build_object(bpy, scene, name, mesh, atlas, mat, location=(0, 0, 0), parent=None, pivot=(0, 0, 0)):
    o = bpy.data.objects.get(name)
    if o is not None:
        bpy.data.objects.remove(o, do_unlink=True)
    me = bpy.data.meshes.get(name)
    if me is not None:
        bpy.data.meshes.remove(me)
    px, py, pz = pivot
    V = [(v[0] - px, v[1] - py, v[2] - pz) for v in mesh.V]
    me = bpy.data.meshes.new(name)
    me.from_pydata(V, [], [list(f) for f in mesh.F])
    me.update()
    uvl = me.uv_layers.new(name='UVMap')
    W = atlas.W
    uvs = []
    for f, role, uvf in zip(mesh.F, mesh.R, mesh.U):
        x0, y0, x1, y1 = atlas.cells[role]
        pts = np.array([mesh.V[i] for i in f])
        if uvf is None:
            n = np.abs(_newell(pts))
            d = int(np.argmax(n))
            ua, va = {0: (1, 2), 1: (0, 2), 2: (0, 1)}[d]
            us, vs = pts[:, ua], pts[:, va]
            uu = (us - us.min()) / max(1e-9, us.max() - us.min())
            vv = (vs - vs.min()) / max(1e-9, vs.max() - vs.min())
            uvf = list(zip(uu, vv))
        for (uu, vv) in uvf:
            u = (x0 + 0.5 + uu * (x1 - x0 - 1)) / W
            v = 1 - (y1 - 0.5 - vv * (y1 - y0 - 1)) / W
            uvs += [u, v]
    uvl.data.foreach_set('uv', uvs)
    for p in me.polygons:
        p.use_smooth = False
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.location = pivot
    if parent is not None:
        o.parent = parent
    return o


def export_fbx(bpy, win, scene, objs, path):
    with bpy.context.temp_override(window=win, scene=scene):
        for x in scene.objects:
            x.select_set(x in objs)
        with bpy.context.temp_override(window=win, scene=scene, active_object=objs[0], selected_objects=objs):
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'},
                                     global_scale=1.0, apply_scale_options='FBX_SCALE_ALL',
                                     axis_forward='-Z', axis_up='Y', bake_space_transform=True,
                                     mesh_smooth_type='FACE', path_mode='STRIP', embed_textures=False)


def render_preview(bpy, win, scene, groups, outdir, res=256, rot=(70, 0, -35)):
    from mathutils import Vector, Euler
    cam = bpy.data.objects.get('PrevCam')
    if cam is None:
        cam = bpy.data.objects.new('PrevCam', bpy.data.cameras.new('PrevCam'))
    if cam.name not in scene.collection.objects:
        scene.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_euler = Euler([math.radians(a) for a in rot])
    r = scene.render; r.engine = 'BLENDER_WORKBENCH'; r.resolution_x = r.resolution_y = res
    r.resolution_percentage = 100; r.image_settings.file_format = 'PNG'
    sh = scene.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
    if scene.world is None:
        scene.world = bpy.data.worlds.new('PrevWorld')
    scene.world.color = (0.08, 0.08, 0.09)
    allobj = [o for g in groups.values() for o in g]
    for name, g in groups.items():
        for o in scene.objects:
            if o.type == 'MESH':
                o.hide_render = o not in g
        dg = bpy.context.evaluated_depsgraph_get()
        co = []
        for o in g:
            for v in o.bound_box:
                co += list(o.matrix_world @ Vector(v))
        loc, _ = cam.camera_fit_coords(dg, co)
        zc = sum(co[2::3]) / (len(co) // 3)
        cam.location = loc + (loc - Vector((0, 0, zc))) * 0.12
        r.filepath = os.path.join(outdir, name + '.png')
        with bpy.context.temp_override(window=win, scene=scene):
            bpy.ops.render.render(write_still=True)
    for o in scene.objects:
        o.hide_render = False
