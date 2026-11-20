using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.RenderGraphModule;
using UnityEngine.Rendering.RenderGraphModule.Util;
using UnityEngine.Rendering.Universal;

// HOUSTON: PSX 화면 효과 렌더러 기능. PC_Renderer에 등록돼 있고,
// 씬의 Volume에 "HOUSTON/PSX 화면 효과"가 켜져 있을 때만 동작한다.
public class PSXRendererFeature : ScriptableRendererFeature
{
    public Shader shader;
    [Tooltip("씬 뷰에도 효과 보이기")]
    public bool showInSceneView = true;

    Material m_Material;
    PSXPass m_Pass;

    public override void Create()
    {
        m_Pass = new PSXPass { renderPassEvent = RenderPassEvent.AfterRenderingPostProcessing };
    }

    public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
    {
        var type = renderingData.cameraData.cameraType;
        if (type != CameraType.Game && !(showInSceneView && type == CameraType.SceneView)) return;

        var v = VolumeManager.instance.stack.GetComponent<PSXVolume>();
        if (v == null || !v.IsActive()) return;

        if (shader == null) shader = Shader.Find("HOUSTON/PSX Screen");
        if (shader == null) return;
        if (m_Material == null) m_Material = CoreUtils.CreateEngineMaterial(shader);

        m_Pass.Setup(m_Material, v);
        m_Pass.ConfigureInput(ScriptableRenderPassInput.Depth);
        m_Pass.requiresIntermediateTexture = true;
        renderer.EnqueuePass(m_Pass);
    }

    protected override void Dispose(bool disposing)
    {
        CoreUtils.Destroy(m_Material);
        m_Material = null;
    }

    class PSXPass : ScriptableRenderPass
    {
        static readonly int ResId = Shader.PropertyToID("_PSX_Res");
        static readonly int ParamsId = Shader.PropertyToID("_PSX_Params");
        static readonly int FogColorId = Shader.PropertyToID("_PSX_FogColor");
        static readonly int FogId = Shader.PropertyToID("_PSX_Fog");

        Material m_Material;
        PSXVolume m_Volume;

        class PassData
        {
            public Material material;
            public TextureHandle source;
        }

        public PSXPass() { profilingSampler = new ProfilingSampler("HOUSTON PSX"); }

        public void Setup(Material material, PSXVolume v)
        {
            m_Material = material;
            m_Volume = v;
        }

        public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
        {
            var res = frameData.Get<UniversalResourceData>();
            var cam = frameData.Get<UniversalCameraData>();
            if (res.isActiveTargetBackBuffer || m_Material == null) return;

            var v = m_Volume;
            var td = cam.cameraTargetDescriptor;
            float h = v.verticalResolution.value;
            float w = Mathf.Round(h * td.width / Mathf.Max(1f, td.height));
            m_Material.SetVector(ResId, new Vector4(w, h, 1f / w, 1f / h));
            m_Material.SetVector(ParamsId, new Vector4((1 << v.colorBits.value) - 1, v.dither.value,
                v.fog.value ? 1f : 0f, v.pixelate.value ? 1f : 0f));
            m_Material.SetColor(FogColorId, v.fogColor.value);
            m_Material.SetVector(FogId, new Vector4(v.fogStart.value, v.fogEnd.value, v.fogMax.value, 0f));

            var desc = renderGraph.GetTextureDesc(res.activeColorTexture);
            desc.name = "_PSXSource";
            desc.clearBuffer = false;
            var copy = renderGraph.CreateTexture(desc);
            renderGraph.AddBlitPass(res.activeColorTexture, copy, Vector2.one, Vector2.zero, passName: "HOUSTON PSX Copy");

            using (var builder = renderGraph.AddRasterRenderPass<PassData>("HOUSTON PSX", out var data, profilingSampler))
            {
                data.material = m_Material;
                data.source = copy;
                builder.UseTexture(copy);
                if (res.cameraDepthTexture.IsValid()) builder.UseTexture(res.cameraDepthTexture);
                builder.SetRenderAttachment(res.activeColorTexture, 0, AccessFlags.Write);
                builder.SetRenderFunc(static (PassData d, RasterGraphContext ctx) =>
                {
                    Blitter.BlitTexture(ctx.cmd, d.source, new Vector4(1f, 1f, 0f, 0f), d.material, 0);
                });
            }
        }
    }
}
