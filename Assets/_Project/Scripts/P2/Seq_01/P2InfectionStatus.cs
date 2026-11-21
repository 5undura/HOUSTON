using System;
using UnityEngine;

// Single source of truth for player infection. UI and VFX only read this value.
public class P2InfectionStatus : MonoBehaviour
{
    [SerializeField, Range(0f, 100f)] private float infection = 0f;

    public float Level => infection;
    public float Normalized => infection / 100f;
    public event Action<float> InfectionChanged;

    public void SetInfection(float value)
    {
        float next = Mathf.Clamp(value, 0f, 100f);
        if (Mathf.Approximately(next, infection)) return;
        infection = next;
        InfectionChanged?.Invoke(infection);
    }

    public void AddInfection(float amount)
    {
        SetInfection(infection + amount);
    }

    private void OnValidate()
    {
        infection = Mathf.Clamp(infection, 0f, 100f);
    }
}
