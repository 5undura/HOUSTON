using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

// HOUSTON: PSX 화면 효과 설정. Volume 프로필에 "HOUSTON/PSX 화면 효과"로 추가해서 쓴다.
// 이 컴포넌트가 켜진 Volume이 없으면 효과는 아무 일도 하지 않는다.
[Serializable, VolumeComponentMenu("HOUSTON/PSX 화면 효과")]
[SupportedOnRenderPipeline(typeof(UniversalRenderPipelineAsset))]
public sealed class PSXVolume : VolumeComponent
{
    [Tooltip("효과 켜기")]
    public BoolParameter on = new BoolParameter(false);

    [Header("저해상도")]
    public BoolParameter pixelate = new BoolParameter(true);
    [Tooltip("세로 픽셀 수. PS1은 240")]
    public ClampedIntParameter verticalResolution = new ClampedIntParameter(240, 120, 720);

    [Header("색 단계 · 디더링")]
    [Tooltip("채널당 비트 수. PS1은 5 (32단계)")]
    public ClampedIntParameter colorBits = new ClampedIntParameter(5, 2, 8);
    public ClampedFloatParameter dither = new ClampedFloatParameter(1f, 0f, 1f);

    [Header("안개")]
    public BoolParameter fog = new BoolParameter(true);
    public ColorParameter fogColor = new ColorParameter(new Color(0.012f, 0.010f, 0.009f), false, false, true);
    public MinFloatParameter fogStart = new MinFloatParameter(2.5f, 0f);
    public MinFloatParameter fogEnd = new MinFloatParameter(11f, 0f);
    public ClampedFloatParameter fogMax = new ClampedFloatParameter(1f, 0f, 1f);

    public bool IsActive() => active && on.value;
}
