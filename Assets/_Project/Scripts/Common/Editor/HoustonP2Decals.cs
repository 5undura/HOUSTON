using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

// HOUSTON: 경고 데칼 7종을 개별 프리팹으로 나누고, 테스트 씬(Test_Jiun)의 벽·장비에 붙인다.
// P2_Decals_01.fbx 안의 7개 메시는 모두 원점에 겹쳐 있음 (정면 = 로컬 +Z, 두께 0).
public static class HoustonP2Decals
{
    const string ModelPath = "Assets/_Project/Models/P2/P2_Decals_01.fbx";
    const string PrefabDir = "Assets/_Project/Prefabs/P2/";
    const string RootName = "P2_Decals";
    const string DressingRoot = "P2_SetDressing";
    const float Gap = 0.004f; // 표면에서 띄우는 거리 (Z-fighting 방지)

    // ── 1) 프리팹 나누기 ──
    [MenuItem("HOUSTON/프리팹 만들기/P2 데칼 7종 나누기")]
    static void Split()
    {
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(ModelPath);
        if (model == null) { EditorUtility.DisplayDialog("HOUSTON", ModelPath + " 가 없어요.", "확인"); return; }
        int made = 0, skipped = 0;
        foreach (var mf in model.GetComponentsInChildren<MeshFilter>(true))
        {
            string path = PrefabDir + mf.name + ".prefab";
            if (AssetDatabase.LoadAssetAtPath<GameObject>(path) != null) { skipped++; continue; }
            var go = new GameObject(mf.name);
            go.AddComponent<MeshFilter>().sharedMesh = mf.sharedMesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterials = mf.GetComponent<MeshRenderer>().sharedMaterials;
            mr.shadowCastingMode = ShadowCastingMode.Off;
            PrefabUtility.SaveAsPrefabAsset(go, path);
            Object.DestroyImmediate(go);
            made++;
        }
        AssetDatabase.SaveAssets();
        Debug.Log($"[HOUSTON] 데칼 프리팹 {made}개 생성, 이미 있던 {skipped}개는 그대로 둠");
    }

    // ── 2) 테스트 씬 배치 ──
    // Wall: (x, z)에 가장 가까운 블록아웃 벽의 안쪽 면에 붙임 / Front: 배치된 소품(이름, n번째)의 정면에 붙임
    struct D
    {
        public string decal, prop; public int index; public float x, z, y, side;
        public static D Wall(string d, float x, float z, float y) => new D { decal = d, x = x, z = z, y = y };
        public static D Front(string d, string prop, int index, float y, float side = 0f) => new D { decal = d, prop = prop, index = index, y = y, side = side };
    }

    static readonly D[] Items = {
        // 복도: 비상구, 출입 제한, 바닥 쪽 경고 줄무늬
        D.Wall("P2_Decal_Exit_01", 3.9f, 1.34f, 2.05f),
        D.Wall("P2_Decal_AuthOnly_01", 5.5f, -1.5f, 1.6f),
        D.Wall("P2_Decal_HazardStripe_01", 4.1f, -1.5f, 0.3f),
        // 왼쪽 방 의료 구역 벽 (산소통 근처, 경고 포스터 양옆)
        D.Wall("P2_Decal_Danger_01", -1.53f, 3.09f, 1.5f),
        D.Wall("P2_Decal_O2_01", -2.86f, 1.88f, 1.1f),
        // 장비 라벨
        D.Front("P2_Decal_Label_01", "P2_ServerRack_01", 0, 1.85f),
        D.Front("P2_Decal_Barcode_01", "P2_ServerRack_01", 1, 1.85f, 0.12f),
        D.Front("P2_Decal_Barcode_01", "P2_FileCabinet_02", 0, 0.95f, 0.15f),
    };

    [MenuItem("HOUSTON/P2 테스트 씬/데칼 배치하기 (Test_Jiun)")]
    static void Place()
    {
        var scene = EditorSceneManager.GetActiveScene();
        var old = GameObject.Find(RootName);
        if (old != null) Undo.DestroyObjectImmediate(old);
        var root = new GameObject(RootName);
        Undo.RegisterCreatedObjectUndo(root, "HOUSTON 데칼 배치");

        var walls = FindWalls();
        var dressing = GameObject.Find(DressingRoot);
        int made = 0; var fails = new List<string>();
        foreach (var d in Items)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabDir + d.decal + ".prefab");
            if (prefab == null) { fails.Add(d.decal + " (프리팹 없음 → '데칼 7종 나누기' 먼저)"); continue; }
            bool ok = d.prop == null ? OnWall(d, walls, out var pos, out var n) : OnFront(d, dressing, out pos, out n);
            if (!ok) { fails.Add(d.decal + (d.prop == null ? " (근처 벽 없음)" : $" ({d.prop} #{d.index} 없음)")); continue; }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            go.transform.SetParent(root.transform, false);
            go.transform.SetPositionAndRotation(pos + n * Gap, Quaternion.LookRotation(n));
            made++;
        }
        EditorSceneManager.MarkSceneDirty(scene);
        string msg = $"[HOUSTON] 데칼 {made}개 배치 (씬 저장은 Cmd+S)";
        if (fails.Count > 0) msg += " / 건너뜀: " + string.Join(", ", fails);
        Debug.Log(msg);
    }

    struct Wall { public Bounds b; public Vector3 n, t; public float len, thick; }

    // HoustonP2LightingTest의 벽 찾기와 같은 기준: 높이 2.5m 이상, 길이 1.5m 이상, 두께 0.6m 이하
    static List<Wall> FindWalls()
    {
        var list = new List<(Renderer r, Vector3 n, float len, float thick)>();
        foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Exclude))
        {
            string top = r.transform.root.name;
            if (top == DressingRoot || top == RootName || top == "P2_LightingTest") continue;
            if (r.bounds.size.y < 2.5f) continue;
            var s = r.transform.lossyScale;
            bool thinX = Mathf.Abs(s.x) < Mathf.Abs(s.z);
            float len = Mathf.Abs(thinX ? s.z : s.x), thick = Mathf.Abs(thinX ? s.x : s.z);
            if (len < 1.5f || thick > 0.6f) continue;
            var n = thinX ? r.transform.right : r.transform.forward;
            n.y = 0f; n.Normalize();
            list.Add((r, n, len, thick));
        }
        var walls = new List<Wall>();
        foreach (var g in list.GroupBy(c => c.r.transform.parent))
        {
            var center = Vector3.zero;
            foreach (var c in g) center += c.r.bounds.center;
            center /= g.Count();
            foreach (var c in g)
            {
                var n = c.n;
                if (Vector3.Dot(center - c.r.bounds.center, n) < 0f) n = -n; // 방 안쪽을 향하게
                walls.Add(new Wall { b = c.r.bounds, n = n, t = Vector3.Cross(Vector3.up, n), len = c.len, thick = c.thick });
            }
        }
        return walls;
    }

    static bool OnWall(D d, List<Wall> walls, out Vector3 pos, out Vector3 n)
    {
        pos = n = default;
        var p = new Vector3(d.x, 0f, d.z);
        float best = 1.0f; // 1m 안에 벽이 없으면 실패
        foreach (var w in walls)
        {
            var c = new Vector3(w.b.center.x, 0f, w.b.center.z);
            float along = Mathf.Clamp(Vector3.Dot(p - c, w.t), -w.len * 0.5f + 0.3f, w.len * 0.5f - 0.3f);
            var onLine = c + w.t * along;
            float dist = Vector3.Distance(p, onLine);
            if (dist >= best) continue;
            best = dist;
            pos = onLine + w.n * (w.thick * 0.5f);
            pos.y = d.y;
            n = w.n;
        }
        return best < 1.0f;
    }

    static bool OnFront(D d, GameObject dressing, out Vector3 pos, out Vector3 n)
    {
        pos = n = default;
        if (dressing == null) return false;
        var t = dressing.transform.Cast<Transform>().Where(c => c.name.StartsWith(d.prop)).Skip(d.index).FirstOrDefault();
        if (t == null) return false;
        // 소품 로컬 공간에서 정면(+Z) 면 찾기
        float maxZ = float.MinValue, minX = float.MaxValue, maxX = float.MinValue;
        var toLocal = t.worldToLocalMatrix;
        foreach (var r in t.GetComponentsInChildren<MeshRenderer>())
        {
            var lb = r.localBounds; var m = toLocal * r.transform.localToWorldMatrix;
            for (int i = 0; i < 8; i++)
            {
                var corner = lb.center + Vector3.Scale(lb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                var lc = m.MultiplyPoint3x4(corner);
                maxZ = Mathf.Max(maxZ, lc.z); minX = Mathf.Min(minX, lc.x); maxX = Mathf.Max(maxX, lc.x);
            }
        }
        if (maxZ == float.MinValue) return false;
        var local = new Vector3((minX + maxX) * 0.5f + d.side, 0f, maxZ);
        pos = t.TransformPoint(local);
        pos.y = d.y;
        n = t.forward; n.y = 0f; n.Normalize();
        return true;
    }
}
