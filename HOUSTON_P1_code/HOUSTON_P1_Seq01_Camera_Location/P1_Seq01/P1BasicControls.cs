using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace Houston.P1
{
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Camera))]
    public sealed class P1BasicControls : MonoBehaviour
    {
        [Header("Panel views (Transform rotation only)")]
        [SerializeField] private Transform navigationView;  // 1
        [SerializeField] private Transform externalCameraView;  // 2
        [SerializeField] private Transform systemPcView;  // 3
        [SerializeField] private Transform repairView;  // 4

        [Header("3D button picking")]
        [SerializeField, Min(0.1f)] private float clickDistance = 8f;
        [SerializeField] private LayerMask clickLayers = Physics.DefaultRaycastLayers;

        private Camera playerCamera;
        private readonly List<RaycastResult> uiHits = new List<RaycastResult>();

        private void Awake()
        {
            playerCamera = GetComponent<Camera>();

            // Start facing the external-camera panel, if it is assigned.
            if (externalCameraView != null)
                transform.rotation = externalCameraView.rotation;

#if !ENABLE_INPUT_SYSTEM && !ENABLE_LEGACY_INPUT_MANAGER
            Debug.LogWarning("[HOUSTON P1] No Unity input backend is active.", this);
#endif
        }

        private void Update()
        {
            // The same number keys also type coordinates into the navigation PC.
            int viewKey = IsTypingInInputField() ? 0 : ReadViewKey();
            if (viewKey != 0)
            {
                LookAtPanel(viewKey);
                return; // Don't click a different panel in the same frame.
            }

            if (!ReadClick(out Vector2 pointerPosition) || IsOverUi(pointerPosition))
                return;

            Ray ray = playerCamera.ScreenPointToRay(pointerPosition);
            if (!Physics.Raycast(ray, out RaycastHit hit, clickDistance, clickLayers,
                    QueryTriggerInteraction.Ignore))
                return;

            // The collider can be on the button itself or on a child of it.
            P1WorldButton button = hit.collider.GetComponentInParent<P1WorldButton>();
            if (button != null)
                button.Press();
        }

        private static bool IsTypingInInputField()
        {
            EventSystem events = EventSystem.current;
            GameObject selected = events != null ? events.currentSelectedGameObject : null;
            TMP_InputField field = selected != null ? selected.GetComponentInParent<TMP_InputField>() : null;
            return field != null && field.isFocused;
        }

        private bool IsOverUi(Vector2 pointerPosition)
        {
            EventSystem events = EventSystem.current;
            if (events == null)
                return false;

            var pointer = new PointerEventData(events) { position = pointerPosition };
            events.RaycastAll(pointer, uiHits);
            // Only UI in front of the world should consume world clicks.
            // Decoration (including the camera's RawImage) should have Raycast Target off.
            bool overUi = uiHits.Count > 0 && uiHits[0].module is GraphicRaycaster;
            uiHits.Clear();
            return overUi;
        }

        private void LookAtPanel(int viewKey)
        {
            Transform view;
            switch (viewKey)
            {
                case 1: view = navigationView; break;
                case 2: view = externalCameraView; break;
                case 3: view = systemPcView; break;
                case 4: view = repairView; break;
                default: return;
            }

            if (view == null)
            {
                Debug.LogWarning($"[HOUSTON P1] View {viewKey} is not assigned.", this);
                return;
            }

            // The player stays in the same place; only the viewing angle changes.
            transform.rotation = view.rotation;
        }

        private static int ReadViewKey()
        {
#if ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;
            if (keyboard != null)
            {
                if (keyboard.digit1Key.wasPressedThisFrame) return 1;
                if (keyboard.digit2Key.wasPressedThisFrame) return 2;
                if (keyboard.digit3Key.wasPressedThisFrame) return 3;
                if (keyboard.digit4Key.wasPressedThisFrame) return 4;
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKeyDown(KeyCode.Alpha1)) return 1;
            if (Input.GetKeyDown(KeyCode.Alpha2)) return 2;
            if (Input.GetKeyDown(KeyCode.Alpha3)) return 3;
            if (Input.GetKeyDown(KeyCode.Alpha4)) return 4;
#endif
            return 0;
        }

        private static bool ReadClick(out Vector2 pointerPosition)
        {
            pointerPosition = default;
#if ENABLE_INPUT_SYSTEM
            Mouse mouse = Mouse.current;
            if (mouse != null && mouse.leftButton.wasPressedThisFrame)
            {
                pointerPosition = mouse.position.ReadValue();
                return true;
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetMouseButtonDown(0))
            {
                pointerPosition = Input.mousePosition;
                return true;
            }
#endif
            return false;
        }
    }
}
