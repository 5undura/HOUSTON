// HOUSTON: PS1 느낌 화면 효과 (PSXRendererFeature가 사용)
// 1) 저해상도 픽셀화  2) 거리 안개  3) 색 단계 줄이기 + 4x4 디더링
Shader "HOUSTON/PSX Screen"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off ZTest Always Cull Off Blend Off

        Pass
        {
            Name "PSX"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            float4 _PSX_Res;      // xy: 가상 해상도, zw: 1/해상도
            float4 _PSX_Params;   // x: 색 단계 수-1, y: 디더 세기, z: 안개 켜기, w: 픽셀화 켜기
            float4 _PSX_FogColor;
            float4 _PSX_Fog;      // x: 시작 거리, y: 끝 거리, z: 최대 농도

            static const float kBayer[16] = {
                 0,  8,  2, 10,
                12,  4, 14,  6,
                 3, 11,  1,  9,
                15,  7, 13,  5 };

            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = input.texcoord;
                float2 pix = floor(uv * _PSX_Res.xy);
                float2 suv = _PSX_Params.w > 0.5 ? (pix + 0.5) * _PSX_Res.zw : uv;
                if (_PSX_Params.w < 0.5) pix = floor(uv * _ScreenParams.xy);

                float3 c = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_PointClamp, suv).rgb;

                if (_PSX_Params.z > 0.5)
                {
                    float d = LinearEyeDepth(SampleSceneDepth(suv), _ZBufferParams);
                    float f = saturate((d - _PSX_Fog.x) / max(_PSX_Fog.y - _PSX_Fog.x, 0.001)) * _PSX_Fog.z;
                    c = lerp(c, _PSX_FogColor.rgb, f);
                }

                // 색 단계는 화면에 보이는 감마 공간에서 자른다 (PS1 = 채널당 5비트)
                c = LinearToSRGB(saturate(c));
                uint2 p = (uint2)pix % 4;
                float b = (kBayer[p.y * 4 + p.x] + 0.5) / 16.0 - 0.5;
                float levels = _PSX_Params.x;
                c = saturate(floor(c * levels + 0.5 + b * _PSX_Params.y) / levels);
                return half4(SRGBToLinear(c), 1);
            }
            ENDHLSL
        }
    }
}
