using UnityEngine;
using UnityEngine.Rendering;

// Owns only the EffectPivot local transform, Camera FOV, and optional blur Volume weight.
// ViewRoot (mouse pitch) and P2_Player (yaw/movement) are controlled elsewhere.
public class P2CameraEffects : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private P2FirstPersonController movement;
    [SerializeField] private P2InfectionStatus infection;
    [SerializeField] private Transform effectPivot;
    [SerializeField] private Camera playerCamera;
    [Tooltip("Optional: dedicated URP Global Volume with Depth Of Field override.")]
    [SerializeField] private Volume blurVolume;

    [Header("Optional Accessibility Toggles")]
    public bool enablePhysicalMotion = true;
    public bool enableBlur = true;
    public bool enableFovPulse = true;
    public bool enableStumble = true;

    [Header("Subtle Base Motion")]
    [Range(0f, 0.01f)] public float idleBreathingHeight = 0.0018f;
    [Range(0f, 0.06f)] public float walkingBobHeight = 0.013f;
    [Range(0.5f, 3f)] public float walkingCyclesPerSecond = 1.6f;
    [Range(0f, 1f)] public float walkingRollDegrees = 0.22f;

    [Header("Infection Visual Limits")]
    [Range(0f, 1f)] public float blurWeightLimit = 0.72f;
    [Range(0f, 8f)] public float maxExtraFov = 4.5f;
    [Range(0f, 5f)] public float maxDisturbanceDegrees = 2.5f;
    [Range(0f, 0.6f)] public float maxStumbleSlowdown = 0.40f;

    private Vector3 baseLocalPosition;
    private Quaternion baseLocalRotation;
    private float baseFov;
    private bool initialized;
    private float movementBlend;

    private float nextBlurTime;
    private float nextNauseaTime;
    private float nextStumbleTime;
    private float blurStart = -999f;
    private float blurDuration = 1f;
    private float nauseaStart = -999f;
    private float nauseaDuration = 1f;
    private float stumbleStart = -999f;
    private float stumbleDuration = 1f;
    private float blurPulse;
    private float nauseaPulse;
    private float stumblePulse;

    private void Awake()
    {
        if (movement == null) movement = GetComponent<P2FirstPersonController>();
        if (infection == null) infection = GetComponent<P2InfectionStatus>();

        if (movement == null || infection == null || effectPivot == null || playerCamera == null)
        {
            Debug.LogError("P2CameraEffects: Missing Movement, Infection, EffectPivot, or Camera reference.", this);
            enabled = false;
            return;
        }

        baseLocalPosition = effectPivot.localPosition;
        baseLocalRotation = effectPivot.localRotation;
        baseFov = playerCamera.fieldOfView;
        if (blurVolume != null) blurVolume.weight = 0f;
        initialized = true;
    }

    private void Start()
    {
        float now = Time.time;
        ScheduleBlur(now);
        ScheduleNausea(now);
        ScheduleStumble(now);
    }

    private void Update()
    {
        float now = Time.time;
        float inf = infection.Normalized;

        // Separate irregular timers, rather than a single repeating sine wave.
        if (now >= nextBlurTime)
        {
            blurStart = now;
            blurDuration = Random.Range(0.55f, 1.2f);
            ScheduleBlur(now);
        }
        if (now >= nextNauseaTime)
        {
            nauseaStart = now;
            nauseaDuration = Random.Range(1.2f, 2.0f);
            ScheduleNausea(now);
        }
        if (inf >= 0.65f && enableStumble && now >= nextStumbleTime)
        {
            stumbleStart = now;
            stumbleDuration = Random.Range(1.0f, 1.6f);
            ScheduleStumble(now);
        }

        blurPulse = Pulse(now, blurStart, blurDuration);
        nauseaPulse = Pulse(now, nauseaStart, nauseaDuration) * (0.08f + 0.92f * inf);
        stumblePulse = (enableStumble ? Pulse(now, stumbleStart, stumbleDuration) : 0f)
                      * Mathf.InverseLerp(0.65f, 1f, inf);

        // Movement effect remains independent from camera effect toggles.
        movement.StatusSpeedMultiplier = 1f - maxStumbleSlowdown * stumblePulse;

        if (blurVolume != null)
        {
            float targetBlur = 0f;
            if (enableBlur)
            {
                float blurEvent = blurPulse * (0.20f + 0.80f * inf);
                targetBlur = Mathf.Clamp01(blurEvent + 0.48f * nauseaPulse + 0.65f * stumblePulse)
                             * blurWeightLimit;
            }
            blurVolume.weight = Mathf.MoveTowards(
                blurVolume.weight, targetBlur, Time.deltaTime * 3f);
        }
    }

    private void LateUpdate()
    {
        float t = Time.time;
        float inf = infection.Normalized;
        float walk = Mathf.Clamp01(movement.PlanarSpeed / Mathf.Max(movement.moveSpeed, 0.01f));
        movementBlend = Mathf.MoveTowards(movementBlend, movement.IsInteracting ? 0f : walk,
            Time.deltaTime * 4f);

        Vector3 localOffset = Vector3.zero;
        Vector3 rotation = Vector3.zero;

        if (enablePhysicalMotion)
        {
            // Quiet breathing when stationary; walking introduces a gentle step rhythm.
            localOffset.y += Mathf.Sin(t * 1.6f) * idleBreathingHeight;
            float cycle = t * walkingCyclesPerSecond * Mathf.PI * 2f;
            localOffset.y += Mathf.Sin(cycle * 2f) * walkingBobHeight * movementBlend;
            localOffset.x += Mathf.Cos(cycle) * walkingBobHeight * 0.40f * movementBlend;
            rotation.z += Mathf.Sin(cycle) * walkingRollDegrees * movementBlend;

            float disturbance = nauseaPulse + stumblePulse * 1.5f;
            float wanderX = Mathf.PerlinNoise(t * 1.9f, 14.5f) * 2f - 1f;
            float wanderY = Mathf.PerlinNoise(19.2f, t * 1.7f) * 2f - 1f;
            float wanderZ = Mathf.PerlinNoise(t * 1.3f, 3.7f) * 2f - 1f;

            rotation.x += wanderX * maxDisturbanceDegrees * disturbance;
            rotation.y += wanderY * maxDisturbanceDegrees * disturbance * 0.45f;
            rotation.z += wanderZ * maxDisturbanceDegrees * disturbance;
            localOffset.x += wanderX * 0.015f * disturbance;
            localOffset.y += wanderY * 0.011f * disturbance;
        }

        effectPivot.localPosition = Vector3.Lerp(
            effectPivot.localPosition, baseLocalPosition + localOffset,
            Mathf.Clamp01(Time.deltaTime * 12f));
        effectPivot.localRotation = Quaternion.Slerp(
            effectPivot.localRotation,
            baseLocalRotation * Quaternion.Euler(rotation),
            Mathf.Clamp01(Time.deltaTime * 12f));

        float targetFov = baseFov;
        if (enableFovPulse)
        {
            targetFov += maxExtraFov * Mathf.Clamp01(
                nauseaPulse * 0.40f + stumblePulse * 0.95f);
        }
        playerCamera.fieldOfView = Mathf.Lerp(
            playerCamera.fieldOfView, targetFov,
            Mathf.Clamp01(Time.deltaTime * 8f));
    }

    private void ScheduleBlur(float now)
    {
        float inf = infection.Normalized;
        nextBlurTime = now + Random.Range(Mathf.Lerp(7f, 3.2f, inf),
                                          Mathf.Lerp(12f, 6f, inf));
    }

    private void ScheduleNausea(float now)
    {
        float inf = infection.Normalized;
        nextNauseaTime = now + Random.Range(Mathf.Lerp(35f, 17f, inf),
                                            Mathf.Lerp(60f, 30f, inf));
    }

    private void ScheduleStumble(float now)
    {
        nextStumbleTime = now + Random.Range(14f, 27f);
    }

    // Smooth attack and release: no instantaneous jerk at event boundaries.
    private static float Pulse(float now, float start, float duration)
    {
        float elapsed = now - start;
        if (elapsed < 0f || elapsed >= duration) return 0f;
        float attack = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(elapsed / (duration * 0.25f)));
        float release = 1f - Mathf.SmoothStep(0f, 1f,
            Mathf.Clamp01((elapsed - duration * 0.55f) / (duration * 0.45f)));
        return attack * release;
    }

    private void OnDisable()
    {
        if (!initialized) return;
        if (movement != null) movement.StatusSpeedMultiplier = 1f;
        if (effectPivot != null)
        {
            effectPivot.localPosition = baseLocalPosition;
            effectPivot.localRotation = baseLocalRotation;
        }
        if (playerCamera != null) playerCamera.fieldOfView = baseFov;
        if (blurVolume != null) blurVolume.weight = 0f;
    }
}