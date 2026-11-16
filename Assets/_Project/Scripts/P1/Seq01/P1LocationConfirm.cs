using System;
using TMPro;
using UnityEngine;
using UnityEngine.Events;

namespace Houston.P1
{
    [DisallowMultipleComponent]
    public sealed class P1LocationConfirm : MonoBehaviour
    {
        [Header("Navigation panel")]
        [SerializeField] private TMP_InputField sectorInput;
        [SerializeField] private TMP_Text positionText;
        [SerializeField] private TMP_Text feedbackText;

        [Header("Mission data")]
        [SerializeField] private string expectedSector = "C-2";
        [SerializeField] private bool requirePhotoBeforeConfirm = true;
        [SerializeField] private P1ExternalCamera externalCamera;
        [SerializeField] private UnityEvent onLocationConfirmed = new UnityEvent();

        public bool HasConfirmedPosition { get; private set; }
        public string ConfirmedSector { get; private set; } = string.Empty;

        private void Awake()
        {
            if (positionText != null)
                positionText.text = "CURRENT SECTOR: --";
            ShowFeedback("ENTER SECTOR FROM CONTROL");
        }

        private void OnEnable()
        {
            if (sectorInput != null)
                sectorInput.onSubmit.AddListener(ConfirmEnteredSector);
        }

        private void OnDisable()
        {
            if (sectorInput != null)
                sectorInput.onSubmit.RemoveListener(ConfirmEnteredSector);
        }

        // Connect the navigation CONFIRM button to this no-argument method.
        public void Submit()
        {
            if (sectorInput == null)
            {
                ShowFeedback("COORDINATE INPUT NOT CONNECTED");
                Debug.LogWarning("[HOUSTON P1] Assign the sector input field.", this);
                return;
            }
            ConfirmEnteredSector(sectorInput.text);
        }

        private void ConfirmEnteredSector(string input)
        {
            if (HasConfirmedPosition)
                return;

            string expected = NormalizeSector(expectedSector);
            if (expected.Length == 0 || (requirePhotoBeforeConfirm && externalCamera == null))
            {
                ShowFeedback("NAV CONFIG INCOMPLETE");
                Debug.LogWarning("[HOUSTON P1] Set Expected Sector and assign External Camera if required.", this);
                return;
            }

            if (requirePhotoBeforeConfirm && !externalCamera.HasTakenPhoto)
            {
                ShowFeedback("TAKE AN OBSERVATION PHOTO FIRST");
                return;
            }

            string entered = NormalizeSector(input);
            if (entered.Length == 0)
            {
                ShowFeedback("ENTER A SECTOR CODE");
                return;
            }

            if (!string.Equals(entered, expected, StringComparison.Ordinal))
            {
                ShowFeedback("SECTOR NOT VERIFIED - CHECK WITH CONTROL");
                return;
            }

            ConfirmedSector = expected;
            HasConfirmedPosition = true;
            if (positionText != null)
                positionText.text = $"CURRENT SECTOR: {ConfirmedSector}";
            ShowFeedback("LOCATION CONFIRMED");
            sectorInput.SetTextWithoutNotify(ConfirmedSector);
            sectorInput.interactable = false;
            onLocationConfirmed?.Invoke();
            // Confirming a location never moves the ship or unlocks flight controls.
        }

        private static string NormalizeSector(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
                return string.Empty;

            return value.Trim().ToUpperInvariant()
                .Replace('\u2010', '-').Replace('\u2011', '-')
                .Replace('\u2013', '-').Replace('\u2212', '-')
                .Replace(" ", string.Empty);
        }

        private void ShowFeedback(string message)
        {
            if (feedbackText != null)
                feedbackText.text = message;
        }
    }
}
