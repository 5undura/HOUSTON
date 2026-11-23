using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

// HOUSTON P2 camera feel: owns EffectPivot local transform, Camera FOV,
// and dedicated URP blur/vignette Volumes. Movement and mouse pitch remain elsewhere.
public class P2CameraEffects : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private P2FirstPersonController movement;
    [SerializeField] private P2InfectionStatus infection;
    [SerializeField] private Transform effectPivot;
    [SerializeField] private Camera playerCamera;
    [Tooltip("Optional dedicated Global Volume containing only Depth Of Field.")]
    [SerializeField] private Volume blurVolume;
    [Tooltip("Dedicated Global Volume containing only Vignette.")]
    [SerializeField] private Volume vignetteVolume;

    [Header("Accessibility / Effect Toggles")]
    public bool enablePhysicalMotion = true;
    public bool enableBlur = true;
    public bool enableFovPulse = true;
    public bool enableStumble = true;
    public bool enableVignette = true;
    public bool enableDistanceBlur = true;
    public bool enableDistanceDarkening = true;

    [Header("Base Motion - Always Active")]
    [Range(0f, 0.02f)] public float idleBreathingHeight = 0.005f;
    [Range(0f, 1.5f)] public float idleSwayDegrees = 0.25f;
    [Range(0f, 0.02f)] public float idleWanderMeters = 0.004f;
    [Range(0f, 0.08f)] public float walkingBobHeight = 0.026f;
    [Range(0.5f, 3f)] public float walkingCyclesPerSecond = 1.65f;
    [Range(0f, 2f)] public float walkingRollDegrees = 0.65f;

    [Header("Infection Effect Strength")]
    [Range(0f, 1f)] public float blurWeightLimit = 0.98f;
    [Range(0f, 12f)] public float maxExtraFov = 7f;
    [Range(0f, 6f)] public float maxDisturbanceDegrees = 3.6f;
    [Range(0f, 1.5f)] public float infectedIdleSwayDegrees = 0.5f;
    [Range(0f, 0.7f)] public float maxStumbleSlowdown = 0.45f;

    [Header("Infection Response - Shared Strength Curve")]
    [Tooltip("Higher values make symptoms grow slowly at first and much faster near 100% infection.")]
    [Range(1f, 3f)] public float infectionResponseExponent = 1.6f;
    [Tooltip("Hard cap for all infection-related movement slowdown, including stumble episodes.")]
    [Range(0f, 0.25f)] public float maxInfectionSpeedReduction = 0.25f;

    [Header("Breathing FOV - Breaths Per Minute")]
    public bool enableFovBreathing = true;
    [Range(1f, 60f)] public float healthyBreathsPerMinute = 14f;
    [Range(1f, 60f)] public float infectedBreathsPerMinute = 27f;
    [Tooltip("Healthy breathing: nearly invisible FOV expansion in degrees.")]
    [Range(0f, 2f)] public float healthyBreathFovDegrees = 0.10f;
    [Tooltip("At 50% infection, the breath FOV change remains subtle.")]
    [Range(0f, 2f)] public float midBreathFovDegrees = 0.20f;
    [Tooltip("At 100% infection, breathing becomes visibly stronger.")]
    [Range(0f, 3f)] public float infectedBreathFovDegrees = 1.0f;

    [Header("Irregular Event Intervals (X = Min, Y = Max seconds)")]
    public Vector2 blurIntervalHealthy = new Vector2(6f, 10f);
    public Vector2 blurIntervalInfected = new Vector2(2.8f, 4.8f);
    public Vector2 nauseaIntervalHealthy = new Vector2(28f, 45f);
    public Vector2 nauseaIntervalInfected = new Vector2(9f, 16f);
    public Vector2 stumbleInterval = new Vector2(11f, 20f);

    [Header("Stress Blur - Brief Focus Loss")]
    [Tooltip("Stress blur events only happen at or above this normalized infection level (0-1).")]
    [Range(0f, 1f)] public float stressBlurMinInfection = 0.2f;
    [Tooltip("Random wait between stress blur events at lower infection (seconds).")]
    public Vector2 stressBlurIntervalLow = new Vector2(13f, 20f);
    [Tooltip("Random wait between stress blur events at full infection (seconds).")]
    public Vector2 stressBlurIntervalHigh = new Vector2(5f, 9f);
    [Tooltip("Duration of each short focus loss (seconds).")]
    public Vector2 stressBlurDurationRange = new Vector2(1.0f, 1.6f);
    [Range(0f, 1f)] public float stressBlurLowIntensity = 0.75f;
    [Range(0f, 1f)] public float stressBlurHighIntensity = 1f;
    [Min(0.1f)] public float blurRiseSpeed = 9f;
    [Min(0.1f)] public float blurRecoverySpeed = 2.8f;

    [Header("Runtime Depth Of Field - Strength of Visible Blur")]
    [Tooltip("Ensure the assigned Blur Volume really produces noticeable blur, not only weight changes.")]
    public bool autoConfigureDepthOfField = true;
    [Min(0f)] public float gaussianBlurStart = 0.1f;
    [Min(0f)] public float gaussianBlurEnd = 0.8f;
    [Range(0.5f, 1.5f)] public float gaussianBlurMaxRadius = 1.0f;

    [Header("Persistent Distance Blur - Camera Distance in Meters")]
    [Tooltip("Far blurring begins beyond this distance at 0% infection.")]
    [Min(0f)] public float healthyDistanceBlurStart = 5f;
    [Tooltip("Far blurring reaches maximum strength beyond this distance at 0% infection.")]
    [Min(0.1f)] public float healthyDistanceBlurEnd = 16f;
    [Min(0f)] public float infectedDistanceBlurStart = 2.5f;
    [Min(0.1f)] public float infectedDistanceBlurEnd = 8f;
    [Range(0.5f, 1.5f)] public float healthyDistanceBlurRadius = 1.05f;
    [Range(0.5f, 1.5f)] public float infectedDistanceBlurRadius = 1.5f;
    [Range(0f, 1f)] public float healthyDistanceBlurWeight = 0.88f;
    [Range(0f, 1f)] public float infectedDistanceBlurWeight = 0.96f;

    [Header("Persistent Distance Darkness - Scene-wide Linear Fog")]
    [Tooltip("This changes RenderSettings fog for the entire active Scene, not only P2.")]
    public Color healthyFogColor = new Color(0.115f, 0.13f, 0.16f, 1f);
    [Tooltip("Only subtly darker than the healthy color.")]
    public Color infectedFogColor = new Color(0.105f, 0.12f, 0.148f, 1f);
    [Min(0f)] public float healthyFogStartDistance = 8f;
    [Min(0.1f)] public float healthyFogEndDistance = 32f;
    [Min(0f)] public float infectedFogStartDistance = 7f;
    [Min(0.1f)] public float infectedFogEndDistance = 28f;
    [Min(0.1f)] public float distanceFogSmoothSpeed = 3f;

    [Header("Dynamic Vignette: Infection Baseline and Irregular Variation")]
    [Range(0f, 0.6f)] public float baseVignetteIntensity = 0.28f;
    [Tooltip("Minimum vignette strength at zero infection, including older scenes that saved a low Base Vignette Intensity in Inspector.")]
    [Range(0f, 0.6f)] public float minimumHealthyVignetteIntensity = 0.26f;
    [Range(0f, 0.8f)] public float maxInfectedVignetteIntensity = 0.48f;
    [Range(0f, 0.15f)] public float vignetteBreathingAmount = 0.06f;
    [Tooltip("Extra irregular fluctuation at 100% infection.")]
    [Range(0f, 0.15f)] public float infectedVignetteVariation = 0.04f;
    [Range(0f, 0.2f)] public float vignetteEventBoost = 0.065f;
    [Min(0.1f)] public float vignetteSmoothSpeed = 5.5f;

    private Vector3 baseLocalPosition;
    private Quaternion baseLocalRotation;
    private float baseFov;
    private bool initialized;
    private float movementBlend;
    private float walkingCyclePhase;
    private float breathingPhase;
    private float previousStress = -1f;
    private Vignette runtimeVignette;
    private DepthOfField runtimeDepthOfField;

    // Fog is a Scene setting. Keep the original values for safe teardown.
    private bool hasSavedFog;
    private bool fogIsApplied;
    private bool originalFogEnabled;
    private FogMode originalFogMode;
    private Color originalFogColor;
    private float originalFogStartDistance;
    private float originalFogEndDistance;

    private float nextBlurTime;
    private float nextNauseaTime;
    private float nextStumbleTime;
    private float blurStart = -999f;
    private float nauseaStart = -999f;
    private float stumbleStart = -999f;
    private float blurDuration = 1f;
    private float nauseaDuration = 1f;
    private float stumbleDuration = 1f;
    private float blurPulse;
    private float nauseaPulse;
    private float stumblePulse;

    // This extra pulse is independent of the existing blinking/nausea/stumble events.
    private float nextStressBlurTime;
    private float stressBlurStart = -999f;
    private float stressBlurDuration = 1f;
    private float stressBlurPeak = 1f;
    private float stressBlurPulse;
    private bool wasStressEligible;

    private void Awake()
    {
        if (movement == null) movement = GetComponent<P2FirstPersonController>();
        if (infection == null) infection = GetComponent<P2InfectionStatus>();
        if (movement == null || infection == null || effectPivot == null || playerCamera == null)
        {
            Debug.LogError("P2CameraEffects: Assign Movement, Infection, EffectPivot and PlayerCamera.", this);
            enabled = false;
            return;
        }

        baseLocalPosition = effectPivot.localPosition;
        baseLocalRotation = effectPivot.localRotation;
        baseFov = playerCamera.fieldOfView;

        SaveOriginalFog();
        ConfigureBlurVolume();

        if (vignetteVolume != null)
        {
            // .profile creates a runtime copy; do not change the shared profile asset.
            VolumeProfile runtimeProfile = vignetteVolume.profile;
            if (runtimeProfile != null && runtimeProfile.TryGet<Vignette>(out runtimeVignette))
            {
                vignetteVolume.weight = 1f;
                runtimeVignette.active = true;
                runtimeVignette.intensity.overrideState = true;
                runtimeVignette.intensity.value = Mathf.Max(
                    baseVignetteIntensity, minimumHealthyVignetteIntensity);
            }
            else
            {
                Debug.LogWarning("P2CameraEffects: Vignette Volume needs a Vignette override.", this);
            }
        }

        initialized = true;
    }

    private void Start()
    {
        if (!initialized) return;
        float now = Time.time;
        ScheduleBlur(now);
        ScheduleNausea(now);
        ScheduleStumble(now);
        ScheduleStressBlur(now);
        previousStress = InfectionStress(Mathf.Clamp01(infection.Normalized));
    }

    private void Update()
    {
        if (!initialized) return;

        float now = Time.time;
        float inf = Mathf.Clamp01(infection.Normalized);
        float stress = InfectionStress(inf);

        // When the infection rises quickly via the test UI, let stronger effects
        // become noticeable shortly rather than waiting for old healthy timers.
        if (previousStress >= 0f && stress > previousStress + 0.08f)
        {
            nextBlurTime = Mathf.Min(nextBlurTime, now + Random.Range(1.5f, 2.8f));
            nextNauseaTime = Mathf.Min(nextNauseaTime, now + Random.Range(2.5f, 4.5f));
            nextStumbleTime = Mathf.Min(nextStumbleTime, now + Random.Range(3f, 5f));
        }
        previousStress = stress;

        if (now >= nextBlurTime)
        {
            blurStart = now;
            blurDuration = Random.Range(1.05f, 2.1f) * Mathf.Lerp(0.85f, 1.45f, stress);
            ScheduleBlur(now);
        }
        if (now >= nextNauseaTime)
        {
            nauseaStart = now;
            nauseaDuration = Random.Range(1.7f, 2.7f) * Mathf.Lerp(0.80f, 1.75f, stress);
            ScheduleNausea(now);
        }
        if (now >= nextStumbleTime)
        {
            if (enableStumble && inf >= 0.65f)
            {
                stumbleStart = now;
                stumbleDuration = Random.Range(1.3f, 2.1f) * Mathf.Lerp(1f, 1.65f, stress);
            }
            ScheduleStumble(now); // also reschedule below 65, avoiding sudden events
        }

        blurPulse = Pulse(now, blurStart, blurDuration);
        nauseaPulse = Pulse(now, nauseaStart, nauseaDuration) * Mathf.Lerp(0.10f, 1f, stress);
        stumblePulse = enableStumble
            ? Pulse(now, stumbleStart, stumbleDuration) * Mathf.InverseLerp(0.65f, 1f, inf)
            : 0f;

        // Crossing the stress threshold triggers a reasonably quick first event,
        // so raising infection during testing doesn't require a long wait.
        bool stressEligible = inf >= stressBlurMinInfection;
        if (stressEligible && !wasStressEligible)
            nextStressBlurTime = now + Random.Range(1.5f, 3.2f);
        wasStressEligible = stressEligible;

        if (now >= nextStressBlurTime)
        {
            if (enableBlur && stressEligible)
            {
                stressBlurStart = now;
                stressBlurDuration = RandomInterval(stressBlurDurationRange)
                                   * Mathf.Lerp(0.8f, 1.85f, stress);
                stressBlurPeak = Random.Range(0.9f, 1f);
            }
            ScheduleStressBlur(now);
        }
        stressBlurPulse = enableBlur && stressEligible
            ? Pulse(now, stressBlurStart, stressBlurDuration)
            : 0f;

        // Continuous 0..25% slowdown; temporary stumble dips share the same cap.
        // Thus infection never reduces regular movement by more than 25%.
        float speedReductionCap = Mathf.Clamp(maxInfectionSpeedReduction, 0f, 0.25f);
        float continuousSlowdown = speedReductionCap * stress;
        float stumbleExtra = (speedReductionCap - continuousSlowdown)
                           * Mathf.Clamp01(maxStumbleSlowdown * stumblePulse);
        movement.StatusSpeedMultiplier = 1f - (continuousSlowdown + stumbleExtra);

        if (blurVolume != null)
        {
            float target = 0f;
            if (enableBlur)
            {
                float regularBlur = blurPulse * Mathf.Lerp(0.20f, 1f, stress);
                float infectionBlur = 0.05f * stress;
                float oldBlur = Mathf.Clamp01(regularBlur + 0.85f * nauseaPulse
                              + 0.95f * stumblePulse + infectionBlur);

                // The new stress effect temporarily dominates the DOF volume.
                // Higher infection makes the same short episode blur more strongly.
                float infectionStrength = Mathf.InverseLerp(
                    stressBlurMinInfection, 1f, inf);
                float stressStrength = Mathf.Lerp(
                    stressBlurLowIntensity, stressBlurHighIntensity, infectionStrength);
                // At lower infection, even a high serialized Inspector value
                // is toned down; strength grows nonlinearly as infection rises.
                float stressBlur = stressBlurPulse * stressBlurPeak * stressStrength
                                 * Mathf.Lerp(0.28f, 1f, stress);

                // Even with no transient event, distant objects remain out of focus.
                // Symptoms bring the blur forward and increase its radius.
                float distanceBaseline = enableDistanceBlur
                    ? Mathf.Lerp(healthyDistanceBlurWeight,
                        infectedDistanceBlurWeight, stress)
                    : 0f;
                target = Mathf.Clamp01(Mathf.Max(oldBlur, stressBlur, distanceBaseline))
                         * blurWeightLimit;

                UpdateDistanceDepthOfField(stress);
            }
            float speed = target > blurVolume.weight ? blurRiseSpeed : blurRecoverySpeed;
            blurVolume.weight = Mathf.MoveTowards(
                blurVolume.weight, target, Time.deltaTime * speed);
        }

        UpdateDistanceFog(stress);
        UpdateVignette(now, inf);
    }

    private void LateUpdate()
    {
        if (!initialized) return;

        float t = Time.time;
        float inf = Mathf.Clamp01(infection.Normalized);
        float stress = InfectionStress(inf);

        // One shared rhythm for subtle physical breathing and the FOV inhale/exhale.
        float breathsPerMinute = Mathf.Lerp(
            healthyBreathsPerMinute, infectedBreathsPerMinute, inf);
        breathingPhase += Time.deltaTime * breathsPerMinute / 60f * Mathf.PI * 2f;
        if (breathingPhase >= Mathf.PI * 2f)
            breathingPhase %= Mathf.PI * 2f;

        float actualMoveSpeed = movement.moveSpeed * movement.StatusSpeedMultiplier;
        float walk = Mathf.Clamp01(movement.PlanarSpeed / Mathf.Max(actualMoveSpeed, 0.01f));
        movementBlend = Mathf.MoveTowards(
            movementBlend, movement.IsInteracting ? 0f : walk, Time.deltaTime * 5f);

        Vector3 offset = Vector3.zero;
        Vector3 rotation = Vector3.zero;
        if (enablePhysicalMotion)
        {
            // Subtle breathing continues even if infection does not change.
            float breathWave = -Mathf.Cos(breathingPhase);
            offset.y += breathWave * idleBreathingHeight
                      * Mathf.Lerp(1f, 1.4f, stress);

            // Slow irregular sway in all directions (not a fixed repeating pattern).
            float idleX = SignedNoise(t * 0.43f, 13.31f);
            float idleY = SignedNoise(39.28f, t * 0.38f);
            float idleZ = SignedNoise(t * 0.35f, 72.19f);
            float idleDegrees = idleSwayDegrees + stress * infectedIdleSwayDegrees;
            rotation.x += idleX * idleDegrees;
            rotation.y += idleY * idleDegrees * 0.5f;
            rotation.z += idleZ * idleDegrees * 0.75f;
            offset.x += idleX * idleWanderMeters;
            offset.y += idleY * idleWanderMeters * 0.45f;

            // Visible footsteps, blended in/out with real movement speed.
            // Tie the actual footstep rhythm to measured horizontal speed,
            // not elapsed wall-clock time. At 75% speed, footsteps happen
            // at ~75% of the original rate, with continuous phase and no jumps.
            float speedRatio = Mathf.Clamp01(
                movement.PlanarSpeed / Mathf.Max(movement.moveSpeed, 0.01f));
            walkingCyclePhase += Time.deltaTime * walkingCyclesPerSecond
                                 * Mathf.PI * 2f * speedRatio;
            if (walkingCyclePhase >= Mathf.PI * 2f)
                walkingCyclePhase %= Mathf.PI * 2f;
            float cycle = walkingCyclePhase;
            offset.y += Mathf.Sin(cycle * 2f) * walkingBobHeight
                      * movementBlend * Mathf.Lerp(1f, 1.2f, stress);
            offset.x += Mathf.Cos(cycle) * walkingBobHeight * 0.45f
                      * movementBlend * Mathf.Lerp(1f, 1.2f, stress);
            rotation.z += Mathf.Sin(cycle) * walkingRollDegrees * movementBlend;
            rotation.x += Mathf.Cos(cycle * 2f) * 0.13f * movementBlend;

            // Infection episodes: lower-frequency drift rather than rapid camera jitter.
            float episode = (nauseaPulse + stumblePulse * 1.45f
                          + stressBlurPulse * 0.25f)
                          * Mathf.Lerp(0.25f, 1f, stress);
            float nx = SignedNoise(t * 1.45f, 8.44f);
            float ny = SignedNoise(22.13f, t * 1.16f);
            float nz = SignedNoise(t * 1.28f, 91.6f);
            rotation.x += nx * maxDisturbanceDegrees * episode;
            rotation.y += ny * maxDisturbanceDegrees * episode * 0.5f;
            rotation.z += nz * maxDisturbanceDegrees * episode;
            offset.x += nx * 0.028f * episode;
            offset.y += ny * 0.020f * episode;
        }

        float smooth = 1f - Mathf.Exp(-10f * Time.deltaTime);
        effectPivot.localPosition = Vector3.Lerp(
            effectPivot.localPosition, baseLocalPosition + offset, smooth);
        effectPivot.localRotation = Quaternion.Slerp(
            effectPivot.localRotation,
            baseLocalRotation * Quaternion.Euler(rotation), smooth);

        float targetFov = baseFov;

        if (enableFovBreathing)
        {
            // Shared phase above keeps body motion and FOV breathing in sync.
            // 0..50%: practically invisible; 50..100%: faster growth in amplitude.
            float breathDegrees = inf <= 0.5f
                ? Mathf.Lerp(healthyBreathFovDegrees, midBreathFovDegrees, inf * 2f)
                : Mathf.Lerp(midBreathFovDegrees, infectedBreathFovDegrees,
                    Mathf.Pow((inf - 0.5f) * 2f, 1.7f));
            float inhale = 0.5f - 0.5f * Mathf.Cos(breathingPhase);
            targetFov += breathDegrees * inhale;  // Inhale expands, exhale returns.
        }

        if (enableFovPulse)
        {
            // Sudden stress episodes widen FOV further, with much bigger
            // changes at high infection. Episode durations also scale in Update().
            float episodicFov = Mathf.Clamp01(
                nauseaPulse * 0.70f + stumblePulse * 0.95f
                + stressBlurPulse * 0.40f);
            targetFov += maxExtraFov * episodicFov * Mathf.Lerp(0.15f, 1f, stress);
        }
        float fovSmooth = 1f - Mathf.Exp(-5.5f * Time.deltaTime);
        playerCamera.fieldOfView = Mathf.Lerp(playerCamera.fieldOfView, targetFov, fovSmooth);
    }

    private void UpdateVignette(float now, float inf)
    {
        if (runtimeVignette == null) return;

        float stress = InfectionStress(inf);
        float intensity = 0f;
        if (enableVignette)
        {
            // Infection sets the overall level, not an always-rising animation.
            float healthyBaseline = Mathf.Max(
                baseVignetteIntensity, minimumHealthyVignetteIntensity);
            float infectedBaseline = Mathf.Max(
                healthyBaseline, maxInfectedVignetteIntensity);
            float baseline = Mathf.Lerp(
                healthyBaseline,
                infectedBaseline,
                stress);

            // Layered Perlin noise is irregular but remains smooth across frames.
            float slowDrift = SignedNoise(now * 0.33f, 123.5f);
            float mediumDrift = SignedNoise(now * 0.83f, 77.1f);
            float fastDrift = SignedNoise(now * 1.46f, 28.9f);
            float irregular = 0.45f * slowDrift
                            + 0.35f * mediumDrift
                            + 0.20f * fastDrift;

            float fluctuationAmount = vignetteBreathingAmount
                                    + infectedVignetteVariation * stress;
            float episodic = Mathf.Clamp01(nauseaPulse + stumblePulse
                                            + stressBlurPulse * 0.45f);

            intensity = baseline
                + irregular * fluctuationAmount
                + vignetteEventBoost * episodic * Mathf.Lerp(0.25f, 1f, stress);
        }

        float k = 1f - Mathf.Exp(-vignetteSmoothSpeed * Time.deltaTime);
        runtimeVignette.intensity.value = Mathf.Lerp(
            runtimeVignette.intensity.value, Mathf.Clamp01(intensity), k);
    }

    private void ConfigureBlurVolume()
    {
        if (blurVolume == null)
        {
            Debug.LogWarning(
                "P2CameraEffects: Blur Volume is unassigned. Stress blur cannot appear.", this);
            return;
        }

        blurVolume.weight = 0f;
        VolumeProfile runtimeProfile = blurVolume.profile; // Runtime copy; never edit shared asset.
        if (runtimeProfile == null || !runtimeProfile.TryGet<DepthOfField>(out var dof))
        {
            Debug.LogWarning(
                "P2CameraEffects: Blur Volume must have a Depth Of Field override in its profile.", this);
            return;
        }

        runtimeDepthOfField = dof;
        if (!autoConfigureDepthOfField) return;

        // Gaussian only blurs the far field. At rest, the distance settings below
        // keep nearby objects clear and distant objects noticeably out of focus.
        dof.active = true;
        dof.mode.overrideState = true;
        dof.mode.value = DepthOfFieldMode.Gaussian;
        dof.gaussianStart.overrideState = true;
        dof.gaussianStart.value = Mathf.Max(0f, gaussianBlurStart);
        dof.gaussianEnd.overrideState = true;
        dof.gaussianEnd.value = Mathf.Max(gaussianBlurStart + 0.1f, gaussianBlurEnd);
        dof.gaussianMaxRadius.overrideState = true;
        dof.gaussianMaxRadius.value = gaussianBlurMaxRadius;

        UpdateDistanceDepthOfField(InfectionStress(Mathf.Clamp01(infection.Normalized)));
    }

    private void UpdateDistanceDepthOfField(float stress)
    {
        if (!autoConfigureDepthOfField || runtimeDepthOfField == null) return;

        if (!enableDistanceBlur)
        {
            // Original short-focus stress blur behavior when distance blur is off.
            runtimeDepthOfField.gaussianStart.value = Mathf.Max(0f, gaussianBlurStart);
            runtimeDepthOfField.gaussianEnd.value = Mathf.Max(
                gaussianBlurStart + 0.1f, gaussianBlurEnd);
            runtimeDepthOfField.gaussianMaxRadius.value = gaussianBlurMaxRadius;
            return;
        }

        // Larger infection means a shorter distance to noticeable far-field blur.
        float start = Mathf.Lerp(
            healthyDistanceBlurStart, infectedDistanceBlurStart, stress);
        float end = Mathf.Lerp(
            healthyDistanceBlurEnd, infectedDistanceBlurEnd, stress);
        end = Mathf.Max(start + 0.1f, end);
        float radius = Mathf.Lerp(
            healthyDistanceBlurRadius, infectedDistanceBlurRadius, stress);

        // Existing intermittent stress episodes briefly drag focus all the way
        // toward the camera, without permanently blurring nearby objects.
        float focusLoss = Mathf.Clamp01(Mathf.Max(
            stressBlurPulse * Mathf.Lerp(0.4f, 1f, stress),
            blurPulse * Mathf.Lerp(0.05f, 0.65f, stress),
            nauseaPulse * Mathf.Lerp(0.1f, 0.8f, stress),
            stumblePulse * 0.9f));

        start = Mathf.Lerp(start, Mathf.Max(0f, gaussianBlurStart), focusLoss);
        end = Mathf.Lerp(end, Mathf.Max(gaussianBlurStart + 0.1f, gaussianBlurEnd), focusLoss);
        runtimeDepthOfField.gaussianStart.value = Mathf.Max(0f, start);
        runtimeDepthOfField.gaussianEnd.value = Mathf.Max(start + 0.1f, end);
        runtimeDepthOfField.gaussianMaxRadius.value = Mathf.Clamp(
            radius + focusLoss * 0.10f, 0.5f, 1.5f);
    }

    private void SaveOriginalFog()
    {
        if (hasSavedFog) return;
        originalFogEnabled = RenderSettings.fog;
        originalFogMode = RenderSettings.fogMode;
        originalFogColor = RenderSettings.fogColor;
        originalFogStartDistance = RenderSettings.fogStartDistance;
        originalFogEndDistance = RenderSettings.fogEndDistance;
        hasSavedFog = true;
    }

    private void UpdateDistanceFog(float stress)
    {
        // Linear fog darkens distant scenery while leaving nearby scenery intact.
        if (!enableDistanceDarkening)
        {
            RestoreOriginalFog();
            return;
        }
        if (!hasSavedFog) SaveOriginalFog();
        RenderSettings.fog = true;
        RenderSettings.fogMode = FogMode.Linear;

        float targetStart = Mathf.Lerp(
            healthyFogStartDistance, infectedFogStartDistance, stress);
        float targetEnd = Mathf.Lerp(
            healthyFogEndDistance, infectedFogEndDistance, stress);
        targetEnd = Mathf.Max(targetStart + 0.1f, targetEnd);
        Color targetColor = Color.Lerp(healthyFogColor, infectedFogColor, stress);

        // Snap to the baseline the first frame, otherwise previously disabled
        // fog could temporarily darken the entire room during initialization.
        if (!fogIsApplied)
        {
            RenderSettings.fogStartDistance = targetStart;
            RenderSettings.fogEndDistance = targetEnd;
            RenderSettings.fogColor = targetColor;
            fogIsApplied = true;
            return;
        }

        float amount = 1f - Mathf.Exp(-distanceFogSmoothSpeed * Time.deltaTime);
        RenderSettings.fogStartDistance = Mathf.Lerp(
            RenderSettings.fogStartDistance, targetStart, amount);
        RenderSettings.fogEndDistance = Mathf.Max(
            RenderSettings.fogStartDistance + 0.1f,
            Mathf.Lerp(RenderSettings.fogEndDistance, targetEnd, amount));
        RenderSettings.fogColor = Color.Lerp(
            RenderSettings.fogColor, targetColor, amount);
    }

    private void RestoreOriginalFog()
    {
        if (!hasSavedFog) return;
        RenderSettings.fog = originalFogEnabled;
        RenderSettings.fogMode = originalFogMode;
        RenderSettings.fogStartDistance = originalFogStartDistance;
        RenderSettings.fogEndDistance = originalFogEndDistance;
        RenderSettings.fogColor = originalFogColor;
        fogIsApplied = false;
    }

    private void ScheduleStressBlur(float now)
    {
        float inf = Mathf.Clamp01(infection.Normalized);
        float factor = Mathf.Pow(Mathf.InverseLerp(
            stressBlurMinInfection, 1f, inf), 1.25f);
        Vector2 waitRange = Vector2.Lerp(
            stressBlurIntervalLow, stressBlurIntervalHigh, factor);
        nextStressBlurTime = now + RandomInterval(waitRange);
    }

    private void ScheduleBlur(float now)
    {
        float inf = Mathf.Clamp01(infection.Normalized);
        Vector2 range = Vector2.Lerp(
            blurIntervalHealthy, blurIntervalInfected, InfectionStress(inf));
        nextBlurTime = now + RandomInterval(range);
    }

    private void ScheduleNausea(float now)
    {
        float inf = Mathf.Clamp01(infection.Normalized);
        Vector2 range = Vector2.Lerp(
            nauseaIntervalHealthy, nauseaIntervalInfected, InfectionStress(inf));
        nextNauseaTime = now + RandomInterval(range);
    }

    private void ScheduleStumble(float now)
    {
        float stress = InfectionStress(Mathf.Clamp01(infection.Normalized));
        float delayFactor = Mathf.Lerp(1.4f, 0.7f, stress);
        nextStumbleTime = now + RandomInterval(stumbleInterval) * delayFactor;
    }

    private float InfectionStress(float normalizedInfection)
    {
        return Mathf.Pow(Mathf.Clamp01(normalizedInfection),
            Mathf.Max(1f, infectionResponseExponent));
    }

    private static float RandomInterval(Vector2 range)
    {
        float min = Mathf.Max(0.1f, Mathf.Min(range.x, range.y));
        float max = Mathf.Max(min, Mathf.Max(range.x, range.y));
        return Random.Range(min, max);
    }

    private static float SignedNoise(float x, float y)
    {
        return Mathf.PerlinNoise(x, y) * 2f - 1f;
    }

    private static float Pulse(float now, float start, float duration)
    {
        float elapsed = now - start;
        if (elapsed < 0f || elapsed >= duration) return 0f;
        float inAmount = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(elapsed / (duration * 0.22f)));
        float outAmount = 1f - Mathf.SmoothStep(0f, 1f,
            Mathf.Clamp01((elapsed - duration * 0.56f) / (duration * 0.44f)));
        return inAmount * outAmount;
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
        if (runtimeVignette != null) runtimeVignette.intensity.value = 0f;
        RestoreOriginalFog();
    }
}
