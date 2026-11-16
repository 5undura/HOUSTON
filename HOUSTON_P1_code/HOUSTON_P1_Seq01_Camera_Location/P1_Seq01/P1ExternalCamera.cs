using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace Houston.P1
{
    [DisallowMultipleComponent]
    public sealed class P1ExternalCamera : MonoBehaviour
    {
        private enum Direction { Up, Right, Down, Left }

        [Header("Observation textures (2D images)")]
        [SerializeField] private Texture2D upPhoto;
        [SerializeField] private Texture2D rightPhoto;
        [SerializeField] private Texture2D downPhoto;
        [SerializeField] private Texture2D leftPhoto;
        [SerializeField] private Direction startingDirection = Direction.Up;

        [Header("Camera monitor")]
        [SerializeField] private RawImage photoDisplay;
        [SerializeField] private TMP_Text directionText;
        [SerializeField] private TMP_Text feedbackText;

        private Direction targetDirection;
        private Direction savedDirection;
        private Texture2D savedPhoto;

        // A deleted photo does not erase mission progress. It can be retaken.
        public bool HasTakenPhoto { get; private set; }

        private void Awake()
        {
            targetDirection = startingDirection;
            if (photoDisplay != null)
                photoDisplay.raycastTarget = false;
            RefreshMonitor();
            ShowFeedback("NO PHOTO - PRESS CAPTURE");
        }

        public void AimUp() => SetAim(Direction.Up);
        public void AimRight() => SetAim(Direction.Right);
        public void AimDown() => SetAim(Direction.Down);
        public void AimLeft() => SetAim(Direction.Left);

        public void CapturePhoto()
        {
            Texture2D photo = TextureFor(targetDirection);
            if (photo == null)
            {
                ShowFeedback("NO IMAGE FOR THIS DIRECTION");
                Debug.LogWarning($"[HOUSTON P1] Assign a texture for {targetDirection}.", this);
                return;
            }

            savedPhoto = photo;
            savedDirection = targetDirection;
            HasTakenPhoto = true;
            RefreshMonitor();
            ShowFeedback($"PHOTO SAVED: {DirectionLabel(savedDirection)}");
        }

        public void DeletePhoto()
        {
            if (savedPhoto == null)
            {
                ShowFeedback("NO PHOTO TO DELETE");
                return;
            }

            savedPhoto = null;
            RefreshMonitor();
            ShowFeedback("PHOTO DELETED");
        }

        private void SetAim(Direction direction)
        {
            targetDirection = direction;
            RefreshMonitor();
            ShowFeedback(savedPhoto == null ? "PRESS CAPTURE" : "CAPTURE TO REPLACE PHOTO");
        }

        private Texture2D TextureFor(Direction direction)
        {
            switch (direction)
            {
                case Direction.Up: return upPhoto;
                case Direction.Right: return rightPhoto;
                case Direction.Down: return downPhoto;
                case Direction.Left: return leftPhoto;
                default: return null;
            }
        }

        private void RefreshMonitor()
        {
            if (photoDisplay != null)
            {
                photoDisplay.texture = savedPhoto;
                photoDisplay.enabled = savedPhoto != null;
            }

            if (directionText != null)
            {
                string saved = savedPhoto != null ? DirectionLabel(savedDirection) : "--";
                directionText.text = $"AIM: {DirectionLabel(targetDirection)}\nPHOTO: {saved}";
            }
        }

        private static string DirectionLabel(Direction direction) => direction.ToString().ToUpperInvariant();

        private void ShowFeedback(string message)
        {
            if (feedbackText != null)
                feedbackText.text = message;
        }
    }
}
