using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

// HOUSTON: Test_Jiun 씬에 PSX 화면 효과 + 조명 테스트 세팅을 자동으로 만든다.
// - PC/Mobile 렌더러에 PSX 렌더러 기능 등록 (Volume에서 켜야만 동작하므로 다른 씬엔 영향 없음)
// - 해·하늘 끄기, 어두운 주변광
// - 벽마다 주황 벽등, 모니터 앞 녹색 빛, 스탠드 아래 따뜻한 스팟
// - PSX Volume (저해상도·디더링·안개·색보정)
// 다시 실행하면 조명만 새로 만들고, Volume 프로필 수치는 유지한다.
public static class HoustonP2LightingTest
{
    const string ScenePath = "Assets/_Project/Scenes/Test/Test_Jiun.unity";
    const string Dir = "Assets/_Project/Scenes/Test/Test_Jiun_Lighting";
    const string ProfilePath = Dir + "/VP_Test_Jiun_PSX.asset";
    const string LampMatPath = Dir + "/M_Test_WallLamp.mat";
    const string ShaderPath = "Assets/_Project/Shaders/Common/PSX_Screen.shader";
    static readonly string[] RendererPaths = { "Assets/Settings/PC_Renderer.asset", "Assets/Settings/Mobile_Renderer.asset" };
    const string RootName = "P2_LightingTest";
    const string DressingRoot = "P2_SetDressing";

    // ── 조명 수치 (여기만 바꿔서 다시 실행하면 됨) ──
    static readonly Color WallColor = new Color(1f, 0.42f, 0.12f);
    const float WallIntensity = 1.6f, WallRange = 3.2f, WallHeight = 2.1f;
    static readonly Color ScreenColor = new Color(0.45f, 1f, 0.5f);
    const float ScreenIntensity = 0.7f, ScreenRange = 2.0f;
    static readonly Color LampColor = new Color(1f, 0.78f, 0.5f);
    const float LampIntensity = 2.5f, LampRange = 2.2f;
    static readonly Color Ambient = new Color(0.03f, 0.03f, 0.038f);

    [MenuItem("HOUSTON/P2 테스트 씬/PSX·조명 세팅하기 (Test_Jiun)")]
    static void Build()
    {
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(ScenePath) == null)
        {
            EditorUtility.DisplayDialog("HOUSTON", ScenePath + " 가 없어요. 먼저 '소품 배치하기'를 실행해 주세요.", "확인");
            return;
        }

        int added = RegisterFeature();
        if (!AssetDatabase.IsValidFolder(Dir)) AssetDatabase.CreateFolder("Assets/_Project/Scenes/Test", "Test_Jiun_Lighting");
        var profile = EnsureProfile();
        var lampMat = EnsureLampMaterial();

        var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        var old = GameObject.Find(RootName);
        if (old != null) Object.DestroyImmediate(old);
        var root = new GameObject(RootName);

        // 1) 환경: 지하라서 해·하늘 없음
        var sun = GameObject.Find("Directional Light");
        if (sun != null) sun.SetActive(false);
        RenderSettings.skybox = null;
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientLight = Ambient;
        RenderSettings.reflectionIntensity = 0.15f;
        RenderSettings.fog = false; // 안개는 PSX Volume에서 처리

        var cam = Camera.main;
        if (cam != null)
        {
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            cam.nearClipPlane = 0.05f;
            cam.transform.position = new Vector3(1.9f, 1.6f, 1.2f);
            cam.transform.LookAt(new Vector3(-1.5f, 1.0f, -1.6f));
            var camData = cam.GetUniversalAdditionalCameraData();
            if (camData != null) camData.renderPostProcessing = true;
        }

        // 2) PSX Volume
        var vgo = new GameObject("PSX Volume");
        vgo.transform.SetParent(root.transform, false);
        var vol = vgo.AddComponent<Volume>();
        vol.isGlobal = true;
        vol.priority = 10;
        vol.sharedProfile = profile;

        // 3) 주황 벽등
        var wallRoot = Child(root, "Wall Lights");
        int walls = 0;
        var cands = new List<(Renderer r, Vector3 n, float thick)>();
        foreach (var r in Object.FindObjectsByType<MeshRenderer>(FindObjectsInactive.Exclude, FindObjectsSortMode.None))
        {
            string top = r.transform.root.name;
            if (top == DressingRoot || top == RootName) continue;
            if (r.bounds.size.y < 2.5f) continue;
            var s = r.transform.lossyScale;
            bool thinX = Mathf.Abs(s.x) < Mathf.Abs(s.z);
            float len = Mathf.Abs(thinX ? s.z : s.x), thick = Mathf.Abs(thinX ? s.x : s.z);
            if (len < 1.5f || thick > 0.6f) continue;
            var n = thinX ? r.transform.right : r.transform.forward;
            n.y = 0f; n.Normalize();
            cands.Add((r, n, thick));
        }
        foreach (var g in cands.GroupBy(c => c.r.transform.parent))
        {
            var center = Vector3.zero;
            foreach (var c in g) center += c.r.bounds.center;
            center /= g.Count();
            foreach (var c in g)
            {
                var b = c.r.bounds;
                var n = c.n;
                if (Vector3.Dot(center - b.center, n) < 0f) n = -n;
                float y = Mathf.Min(b.min.y + WallHeight, b.max.y - 0.25f);
                var surface = new Vector3(b.center.x, y, b.center.z) + n * (c.thick * 0.5f);

                var lamp = GameObject.CreatePrimitive(PrimitiveType.Cube);
                lamp.name = "WallLamp_" + walls.ToString("00");
                Object.DestroyImmediate(lamp.GetComponent<Collider>());
                lamp.transform.SetParent(wallRoot.transform, false);
                lamp.transform.position = surface + n * 0.03f;
                lamp.transform.rotation = Quaternion.LookRotation(n);
                lamp.transform.localScale = new Vector3(0.35f, 0.07f, 0.06f);
                var mr = lamp.GetComponent<MeshRenderer>();
                mr.sharedMaterial = lampMat;
                mr.shadowCastingMode = ShadowCastingMode.Off;

                var l = AddLight(wallRoot, "WallLight_" + walls.ToString("00"), LightType.Point, WallColor, WallIntensity, WallRange);
                l.transform.position = surface + n * 0.25f;
                walls++;
            }
        }

        // 4) 모니터 빛 · 스탠드 빛
        var screenRoot = Child(root, "Screen Lights");
        var lampRoot = Child(root, "Desk Lamp Lights");
        int screens = 0, lamps = 0;
        var dressing = GameObject.Find(DressingRoot);
        if (dressing != null)
        {
            foreach (Transform t in dressing.transform)
            {
                string nm = t.name;
                bool crt = nm.StartsWith("P2_CRTMonitor"), health = nm.StartsWith("P2_HealthMonitor"), desk = nm.StartsWith("P2_DeskLamp");
                if (!crt && !health && !desk) continue;
                if (!TryBounds(t, out var b)) continue;

                if (desk)
                {
                    var l = AddLight(lampRoot, "LampLight_" + lamps.ToString("00"), LightType.Spot, LampColor, LampIntensity, LampRange);
                    l.transform.position = new Vector3(b.center.x, b.max.y - 0.05f, b.center.z);
                    l.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
                    l.spotAngle = 85f;
                    l.innerSpotAngle = 40f;
                    l.shadows = LightShadows.Hard;
                    l.shadowStrength = 0.8f;
                    lamps++;
                }
                else
                {
                    var f = t.forward; f.y = 0f; f.Normalize();
                    float depth = Mathf.Abs(Vector3.Dot(b.extents, new Vector3(Mathf.Abs(f.x), 0f, Mathf.Abs(f.z))));
                    var pos = b.center + f * (depth + 0.2f);
                    if (health) pos.y = b.center.y + b.extents.y * 0.4f;
                    var l = AddLight(screenRoot, "ScreenLight_" + screens.ToString("00"), LightType.Point, ScreenColor, ScreenIntensity, ScreenRange);
                    l.transform.position = pos;
                    screens++;
                }
            }
        }

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        string msg = $"벽등 {walls}개, 모니터 빛 {screens}개, 스탠드 빛 {lamps}개를 만들었어요.";
        if (added > 0) msg += $"\n렌더러 {added}개에 PSX 효과를 등록했어요.";
        msg += "\n\n효과 수치: " + ProfilePath + " (인스펙터에서 조절)";
        if (dressing == null) msg += "\n\n" + DressingRoot + " 가 없어서 모니터·스탠드 빛은 건너뜀";
        EditorUtility.DisplayDialog("HOUSTON", msg, "확인");
    }

    [MenuItem("HOUSTON/P2 테스트 씬/PSX 효과 켜기·끄기")]
    static void Toggle()
    {
        var p = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
        if (p == null || !p.TryGet(out PSXVolume v))
        {
            EditorUtility.DisplayDialog("HOUSTON", "먼저 'PSX·조명 세팅하기'를 실행해 주세요.", "확인");
            return;
        }
        Undo.RecordObject(v, "Toggle PSX");
        v.on.Override(!v.on.value);
        EditorUtility.SetDirty(v);
        AssetDatabase.SaveAssets();
        SceneView.RepaintAll();
        Debug.Log("[HOUSTON] PSX 효과 " + (v.on.value ? "켜짐" : "꺼짐"));
    }

    static int RegisterFeature()
    {
        var shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
        int added = 0;
        foreach (var path in RendererPaths)
        {
            var data = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>(path);
            if (data == null) continue;
            var existing = data.rendererFeatures.OfType<PSXRendererFeature>().FirstOrDefault();
            if (existing != null)
            {
                if (existing.shader == null) { existing.shader = shader; EditorUtility.SetDirty(existing); }
                continue;
            }
            var f = ScriptableObject.CreateInstance<PSXRendererFeature>();
            f.name = "HOUSTON PSX";
            f.shader = shader;
            AssetDatabase.AddObjectToAsset(f, data);
            AssetDatabase.TryGetGUIDAndLocalFileIdentifier(f, out string _, out long localId);
            var so = new SerializedObject(data);
            var list = so.FindProperty("m_RendererFeatures");
            var map = so.FindProperty("m_RendererFeatureMap");
            list.arraySize++;
            list.GetArrayElementAtIndex(list.arraySize - 1).objectReferenceValue = f;
            map.arraySize++;
            map.GetArrayElementAtIndex(map.arraySize - 1).longValue = localId;
            so.ApplyModifiedProperties();
            data.SetDirty();
            EditorUtility.SetDirty(data);
            added++;
        }
        AssetDatabase.SaveAssets();
        return added;
    }

    static VolumeProfile EnsureProfile()
    {
        var p = AssetDatabase.LoadAssetAtPath<VolumeProfile>(ProfilePath);
        if (p != null) return p; // 이미 있으면 수치 유지

        p = ScriptableObject.CreateInstance<VolumeProfile>();
        AssetDatabase.CreateAsset(p, ProfilePath);

        var psx = Add<PSXVolume>(p);
        psx.on.Override(true);
        psx.pixelate.Override(true);
        psx.verticalResolution.Override(240);
        psx.colorBits.Override(5);
        psx.dither.Override(1f);
        psx.fog.Override(true);
        psx.fogColor.Override(new Color(0.012f, 0.010f, 0.009f));
        psx.fogStart.Override(2.5f);
        psx.fogEnd.Override(11f);
        psx.fogMax.Override(1f);

        var tm = Add<Tonemapping>(p);
        tm.mode.Override(TonemappingMode.Neutral);

        var ca = Add<ColorAdjustments>(p);
        ca.postExposure.Override(0.3f);
        ca.contrast.Override(8f);
        ca.saturation.Override(-12f);

        var bloom = Add<Bloom>(p);
        bloom.threshold.Override(0.9f);
        bloom.intensity.Override(0.4f);

        var vig = Add<Vignette>(p);
        vig.intensity.Override(0.3f);
        vig.smoothness.Override(0.4f);

        EditorUtility.SetDirty(p);
        AssetDatabase.SaveAssets();
        return p;
    }

    static T Add<T>(VolumeProfile p) where T : VolumeComponent
    {
        var c = p.Add<T>(false);
        c.name = typeof(T).Name;
        AssetDatabase.AddObjectToAsset(c, p);
        return c;
    }

    static Material EnsureLampMaterial()
    {
        var m = AssetDatabase.LoadAssetAtPath<Material>(LampMatPath);
        if (m != null) return m;
        m = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        m.SetColor("_BaseColor", new Color(0.3f, 0.12f, 0.04f));
        m.SetColor("_EmissionColor", WallColor * 2.5f);
        m.EnableKeyword("_EMISSION");
        m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.None;
        AssetDatabase.CreateAsset(m, LampMatPath);
        return m;
    }

    static GameObject Child(GameObject parent, string name)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent.transform, false);
        return go;
    }

    static Light AddLight(GameObject parent, string name, LightType type, Color color, float intensity, float range)
    {
        var go = Child(parent, name);
        var l = go.AddComponent<Light>();
        l.type = type;
        l.color = color;
        l.intensity = intensity;
        l.range = range;
        l.shadows = LightShadows.None;
        l.lightmapBakeType = LightmapBakeType.Realtime;
        return l;
    }

    static bool TryBounds(Transform t, out Bounds b)
    {
        b = default;
        bool any = false;
        foreach (var r in t.GetComponentsInChildren<Renderer>())
        {
            if (!any) { b = r.bounds; any = true; }
            else b.Encapsulate(r.bounds);
        }
        return any;
    }
}
