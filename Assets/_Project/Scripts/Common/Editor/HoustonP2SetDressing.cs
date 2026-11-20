using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// HOUSTON: P2_ControlRoom 블록아웃을 복사한 테스트 씬(Scenes/Test/Test_Jiun)에 P2 프리팹을 자동 배치한다.
// 메인 씬(P2_ControlRoom)은 건드리지 않는다. 다시 실행하면 배치만 새로 만든다.
public static class HoustonP2SetDressing
{
    const string Src = "Assets/_Project/Scenes/P2_ControlRoom.unity";
    const string Dst = "Assets/_Project/Scenes/Test/Test_Jiun.unity";
    const string PrefabDir = "Assets/_Project/Prefabs/P2/";
    const string RootName = "P2_SetDressing";

    struct E
    {
        public string n; public Vector3 p; public float yaw, sx;
        public E(string n, float x, float y, float z, float yaw, float sx) { this.n = n; p = new Vector3(x, y, z); this.yaw = yaw; this.sx = sx; }
    }

    static readonly E[] Items = {
        new E("P2_Desk_02", -1.961f, 0.1f, -2.001f, 45.0f, 0.8f),
        new E("P2_CRTMonitor_01", -2.477f, 0.99f, -1.739f, 45.0f, 1.0f),
        new E("P2_Keyboard_01", -2.152f, 0.99f, -1.414f, 45.0f, 1.0f),
        new E("P2_CRTMonitor_01", -2.088f, 0.99f, -2.128f, 45.0f, 1.0f),
        new E("P2_Keyboard_01", -1.763f, 0.99f, -1.803f, 45.0f, 1.0f),
        new E("P2_CRTMonitor_01", -1.699f, 0.99f, -2.517f, 45.0f, 1.0f),
        new E("P2_Keyboard_01", -1.374f, 0.99f, -2.192f, 45.0f, 1.0f),
        new E("P2_PCTower_01", -1.628f, 0.1f, -2.545f, 45.0f, 1.0f),
        new E("P2_OfficeChair_01", -1.218f, 0.1f, -1.258f, 225f, 1.0f),
        new E("P2_ServerRack_01", -1.34f, 0.1f, -3.18f, 45.0f, 1.0f),
        new E("P2_ServerRack_01", -3.15f, 0.1f, -1.38f, 45.0f, 1.0f),
        new E("P2_RecordFolder_01", -2.187f, 0.99f, -1.35f, 57f, 1.0f),
        new E("P2_StickyNote_01", -1.452f, 0.99f, -1.916f, 37f, 1.0f),
        new E("P2_IDBadge_01", -1.183f, 0.99f, -2.284f, 70f, 1.0f),
        new E("P2_Mug_01", -2.505f, 0.99f, -1.386f, 45.0f, 1.0f),
        new E("P2_PaperStack_01", -1.374f, 0.99f, -2.517f, 45.0f, 1.0f),
        new E("P2_MedPod_01", -1.99f, 0.1f, 1.56f, 135.0f, 1.0f),
        new E("P2_MedicalRecord_01", -2.308f, 0.76f, 1.242f, 145f, 1.0f),
        new E("P2_HealthMonitor_01", -0.99f, 0.1f, 2.7f, 165.0f, 1.0f),
        new E("P2_IVStand_01", -0.929f, 0.1f, 1.701f, 135.0f, 1.0f),
        new E("P2_OxygenTank_01", -2.287f, 0.1f, 2.14f, 135.0f, 1.0f),
        new E("P2_Respirator_01", -1.778f, 0.1f, 0.57f, 135.0f, 1.0f),
        new E("P2_Curtain_01", -3.08f, 0.1f, 0.76f, 45.0f, 1.0f),
        new E("P2_WarningPoster_01", -2.336f, 1.55f, 2.189f, 135.0f, 1.0f),
        new E("P2_MedShelf_01", 0.3f, 0.1f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBottle_01", 0.6f, 0.975f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBottle_01", 0.48f, 0.975f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBottle_02", 0.35f, 0.975f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBottle_02", 0.22f, 0.975f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBox_01", 0.05f, 0.975f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBox_01", 0.5f, 0.575f, 3.45f, 180.0f, 1.0f),
        new E("P2_MedBox_01", 0.2f, 0.575f, 3.45f, 195f, 1.0f),
        new E("P2_Photo_01", 0.1f, 1.375f, 3.47f, 170f, 1.0f),
        new E("P2_Memo_01", 0.5f, 1.375f, 3.45f, 186f, 1.0f),
        new E("P2_Bookcase_02", 1.64f, 0.1f, 2.73f, 225.0f, 1.0f),
        new E("P2_Bookcase_02", 2.54f, 0.1f, 1.83f, 225.0f, 1.0f),
        new E("P2_Desk_02", 1.6f, 0.1f, -1.71f, 225.0f, 0.95f),
        new E("P2_Desk_02", 1.31f, 0.1f, -3.0f, 315.0f, 0.65f),
        new E("P2_CRTMonitor_01", 1.7f, 0.99f, -1.47f, 231.0f, 1.0f),
        new E("P2_Keyboard_01", 1.35f, 0.99f, -1.753f, 231.0f, 1.0f),
        new E("P2_DeskPhone_01", 1.034f, 0.99f, -1.286f, 225.0f, 1.0f),
        new E("P2_DeskLamp_01", 2.201f, 0.99f, -2.028f, 225.0f, 1.0f),
        new E("P2_OfficeChair_01", 0.58f, 0.1f, -2.37f, 51.0f, 1.0f),
        new E("P2_Blueprint_01", 1.239f, 0.99f, -2.929f, 319f, 1.0f),
        new E("P2_BlueprintRoll_01", 1.628f, 0.99f, -3.177f, 315.0f, 1.0f),
        new E("P2_CrewManifest_01", 0.815f, 0.992f, -3.141f, 303f, 1.0f),
        new E("P2_StickyNote_02", 1.359f, 0.992f, -2.456f, 325f, 1.0f),
        new E("P2_Desk_01", 10.892f, 0.1f, 1.802f, 225.0f, 1.0f),
        new E("P2_CRTMonitor_01", 11.387f, 0.99f, 1.59f, 225.0f, 1.0f),
        new E("P2_Keyboard_01", 11.069f, 0.99f, 1.272f, 225.0f, 1.0f),
        new E("P2_CRTMonitor_01", 10.68f, 0.99f, 2.297f, 225.0f, 1.0f),
        new E("P2_Keyboard_01", 10.362f, 0.99f, 1.979f, 225.0f, 1.0f),
        new E("P2_OfficeChair_01", 10.185f, 0.1f, 1.095f, 45f, 1.0f),
        new E("P2_StickyNote_03", 10.503f, 0.99f, 1.625f, 210f, 1.0f),
        new E("P2_PaperSheet_01", 11.069f, 0.99f, 1.13f, 245f, 1.0f),
        new E("P2_Desk_02", 9.44f, 0.1f, 3.02f, 180.0f, 1.0f),
        new E("P2_CRTMonitor_01", 9.14f, 0.99f, 3.22f, 180.0f, 1.0f),
        new E("P2_PCTower_01", 8.59f, 0.1f, 3.22f, 180.0f, 1.0f),
        new E("P2_Manual_01", 9.94f, 0.99f, 2.87f, 188f, 1.0f),
        new E("P2_Photo_02", 9.59f, 0.99f, 2.72f, 166f, 1.0f),
        new E("P2_Mug_01", 10.29f, 0.99f, 3.12f, 180.0f, 1.0f),
        new E("P2_Desk_02", 11.89f, 0.1f, 0.49f, 270.0f, 1.0f),
        new E("P2_CRTMonitor_01", 12.09f, 0.99f, 0.49f, 270.0f, 1.0f),
        new E("P2_Keyboard_01", 11.64f, 0.99f, 0.49f, 270.0f, 1.0f),
        new E("P2_DeskLamp_01", 12.04f, 0.99f, -0.26f, 270.0f, 1.0f),
        new E("P2_Binder_01", 12.19f, 0.99f, 1.19f, 270.0f, 1.0f),
        new E("P2_ServerRack_01", 6.87f, 0.1f, 1.8f, 135.0f, 1.0f),
        new E("P2_FileCabinet_02", 8.44f, 0.1f, -2.87f, 0.0f, 1.0f),
        new E("P2_FileCabinet_02", 9.04f, 0.1f, -2.87f, 0.0f, 1.0f),
        new E("P2_OxygenTank_01", 9.7f, 0.1f, 0.77f, 0.0f, 1.0f),
        new E("P2_CableBundle_01", 4.7f, 0.1f, -1.36f, 0.0f, 1.0f),
        new E("P2_FileCabinet_01", 12.0f, 0.1f, -1.7f, 270.0f, 1.0f)
    };

    [MenuItem("HOUSTON/P2 테스트 씬/소품 배치하기 (Test_Jiun)")]
    static void Build()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(Dst) == null && !AssetDatabase.CopyAsset(Src, Dst))
        {
            EditorUtility.DisplayDialog("HOUSTON", Src + " 를 복사하지 못했어요.", "확인");
            return;
        }
        var scene = EditorSceneManager.OpenScene(Dst, OpenSceneMode.Single);
        var old = GameObject.Find(RootName);
        if (old != null) Object.DestroyImmediate(old);
        var root = new GameObject(RootName);

        int made = 0; var missing = new List<string>();
        foreach (var e in Items)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabDir + e.n + ".prefab");
            if (prefab == null) { if (!missing.Contains(e.n)) missing.Add(e.n); continue; }
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
            go.transform.SetParent(root.transform, false);
            go.transform.position = e.p;
            go.transform.rotation = Quaternion.Euler(0f, e.yaw, 0f);
            if (!Mathf.Approximately(e.sx, 1f)) go.transform.localScale = new Vector3(e.sx, 1f, 1f);
            made++;
        }
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        string msg = $"소품 {made}개를 배치했어요.\n씬: {Dst}";
        if (missing.Count > 0) msg += "\n\n프리팹이 없어서 건너뜀: " + string.Join(", ", missing);
        EditorUtility.DisplayDialog("HOUSTON", msg, "확인");
    }

    [MenuItem("HOUSTON/P2 테스트 씬/블록아웃 가구 보이기·숨기기")]
    static void ToggleBlockout()
    {
        int n = 0; bool? target = null;
        foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            if (r.GetComponentInParent<Transform>().root.name == RootName) continue;
            string nm = r.gameObject.name;
            if (!(nm.StartsWith("Cube") || nm == "e")) continue;
            var b = r.bounds;
            if (b.size.y >= 2.5f || b.min.y >= 2.6f || b.size.x > 10f || b.size.z > 10f) continue;  // walls, ceiling, floor
            if (target == null) target = !r.enabled;
            Undo.RecordObject(r, "Toggle blockout");
            r.enabled = target.Value; n++;
        }
        EditorSceneManager.MarkSceneDirty(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
        Debug.Log($"[HOUSTON] 블록아웃 가구 {n}개 {(target == true ? "보이기" : "숨기기")}");
    }
}
