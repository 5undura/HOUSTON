using UnityEngine;
using UnityEngine.InputSystem;

// Temporary debug overlay, independent of the final UI system.
public class P2InfectionDebugUI : MonoBehaviour
{
    [SerializeField] private P2InfectionStatus infection;
    [SerializeField] private bool enableTestKeys = true;
    [SerializeField, Min(1f)] private float testStep = 10f;

    private void Awake()
    {
        if (infection == null)
            infection = GetComponent<P2InfectionStatus>();
    }

    private void Update()
    {
        if (!enableTestKeys || infection == null || Keyboard.current == null) return;
        if (Keyboard.current.upArrowKey.wasPressedThisFrame)
            infection.AddInfection(testStep);
        if (Keyboard.current.downArrowKey.wasPressedThisFrame)
            infection.AddInfection(-testStep);
    }

    private void OnGUI()
    {
        if (infection == null) return;
        float x = 16f;
        float y = 16f;
        GUI.Box(new Rect(x, y, 254f, 84f), "P2 INFECTION (TEST)");
        GUI.Label(new Rect(x + 14f, y + 25f, 210f, 22f),
            $"Infection: {infection.Level:0} / 100");
        GUI.Box(new Rect(x + 14f, y + 51f, 224f, 13f), "");
        GUI.Box(new Rect(x + 14f, y + 51f, 224f * infection.Normalized, 13f), "");
        if (enableTestKeys)
            GUI.Label(new Rect(x + 14f, y + 65f, 220f, 18f), "Up Arrow +10   Down Arrow -10");
    }
}
