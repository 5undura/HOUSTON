using UnityEngine;
using UnityEngine.Events;

namespace Houston.P1
{
    [DisallowMultipleComponent]
    public sealed class P1WorldButton : MonoBehaviour
    {
        [SerializeField] private bool logPress = true;
        [SerializeField] private UnityEvent onPressed = new UnityEvent();

        public void Press()
        {
            if (!isActiveAndEnabled)
                return;

            if (logPress)
                Debug.Log($"[HOUSTON P1] Pressed: {gameObject.name}", this);

            onPressed?.Invoke();
        }
    }
}
