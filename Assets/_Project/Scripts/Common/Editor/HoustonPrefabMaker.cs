using System;
using System.IO;
using UnityEditor;
using UnityEngine;

// HOUSTON: Models/<구역> 안의 모든 FBX를 Prefabs/<구역> 프리팹(Prefab Variant)으로 만든다.
// 이미 있는 프리팹은 건드리지 않는다. 루트에 전체 크기에 맞춘 BoxCollider를 하나 붙인다.
public static class HoustonPrefabMaker
{
    const string ModelRoot = "Assets/_Project/Models";
    const string PrefabRoot = "Assets/_Project/Prefabs";

    [MenuItem("HOUSTON/프리팹 만들기/P2")] static void MakeP2() => Make("P2");
    [MenuItem("HOUSTON/프리팹 만들기/P1")] static void MakeP1() => Make("P1");
    [MenuItem("HOUSTON/프리팹 만들기/Common")] static void MakeCommon() => Make("Common");

    static void Make(string zone)
    {
        string src = $"{ModelRoot}/{zone}";
        string dst = $"{PrefabRoot}/{zone}";
        if (!AssetDatabase.IsValidFolder(src))
        {
            EditorUtility.DisplayDialog("HOUSTON", $"{src} 폴더가 없어요.", "확인");
            return;
        }
        if (!AssetDatabase.IsValidFolder(dst)) AssetDatabase.CreateFolder(PrefabRoot, zone);

        int made = 0, skipped = 0;
        foreach (string guid in AssetDatabase.FindAssets("t:Model", new[] { src }))
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (!path.EndsWith(".fbx", StringComparison.OrdinalIgnoreCase)) continue;
            string name = Path.GetFileNameWithoutExtension(path);
            string outPath = $"{dst}/{name}.prefab";
            if (AssetDatabase.LoadAssetAtPath<GameObject>(outPath) != null) { skipped++; continue; }

            var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(model);
            inst.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            AddBoxCollider(inst);
            PrefabUtility.SaveAsPrefabAsset(inst, outPath);
            UnityEngine.Object.DestroyImmediate(inst);
            made++;
        }
        AssetDatabase.SaveAssets();
        EditorUtility.DisplayDialog("HOUSTON", $"{zone}: 새 프리팹 {made}개 생성, 이미 있던 {skipped}개는 그대로 둠", "확인");
    }

    static void AddBoxCollider(GameObject go)
    {
        var renderers = go.GetComponentsInChildren<Renderer>();
        if (renderers.Length == 0 || go.GetComponent<Collider>() != null) return;
        Bounds b = renderers[0].bounds;
        foreach (var r in renderers) b.Encapsulate(r.bounds);
        var c = go.AddComponent<BoxCollider>();
        c.center = go.transform.InverseTransformPoint(b.center);
        Vector3 s = go.transform.lossyScale;
        c.size = new Vector3(b.size.x / s.x, b.size.y / s.y, b.size.z / s.z);
    }
}
