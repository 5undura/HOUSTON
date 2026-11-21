using UnityEngine;
using UnityEngine.InputSystem;

// P2 movement & mouse look only. Camera effects belong to P2CameraEffects.
[RequireComponent(typeof(CharacterController))]
public class P2FirstPersonController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private Transform viewRoot;

    [Header("Movement")]
    [Min(0f)] public float moveSpeed = 2.2f;
    [Min(0f)] public float acceleration = 8f;
    [Min(0f)] public float deceleration = 12f;
    public float gravity = -9.81f;

    [Header("Mouse Look")]
    [Min(0f)] public float mouseSensitivity = 0.12f;
    [Range(0f, 89f)] public float maxLookAngle = 80f;

    private CharacterController characterController;
    private Vector3 planarVelocity;
    private float verticalVelocity;
    private float cameraPitch;
    private bool isInteracting;

    // Status systems (infection, etc.) can alter movement without modifying this script.
    public float StatusSpeedMultiplier { get; set; } = 1f;
    public float PlanarSpeed { get; private set; }
    public bool IsWalking => PlanarSpeed > 0.12f;
    public bool IsInteracting => isInteracting;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        if (viewRoot == null)
            Debug.LogError("P2FirstPersonController: Assign ViewRoot in Inspector.", this);
    }

    private void Start()
    {
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }

    private void Update()
    {
        UpdateCursor();

        bool canMove = !isInteracting && Cursor.lockState == CursorLockMode.Locked;
        Vector2 input = canMove ? ReadMovementInput() : Vector2.zero;

        MovePlayer(input);
        if (canMove)
            LookAround();
    }

    private Vector2 ReadMovementInput()
    {
        if (Keyboard.current == null) return Vector2.zero;

        Vector2 input = Vector2.zero;
        if (Keyboard.current.wKey.isPressed) input.y += 1f;
        if (Keyboard.current.sKey.isPressed) input.y -= 1f;
        if (Keyboard.current.aKey.isPressed) input.x -= 1f;
        if (Keyboard.current.dKey.isPressed) input.x += 1f;
        return input.normalized;
    }

    private void MovePlayer(Vector2 input)
    {
        Vector3 direction = transform.TransformDirection(new Vector3(input.x, 0f, input.y));
        float effectiveSpeed = moveSpeed * Mathf.Clamp(StatusSpeedMultiplier, 0.1f, 1.5f);
        Vector3 desiredVelocity = direction * effectiveSpeed;
        float rate = input.sqrMagnitude > 0f ? acceleration : deceleration;

        planarVelocity = Vector3.MoveTowards(
            planarVelocity, desiredVelocity, rate * Time.deltaTime);

        if (characterController.isGrounded && verticalVelocity < 0f)
            verticalVelocity = -2f; // keeps ground contact stable

        verticalVelocity += gravity * Time.deltaTime;
        Vector3 displacement = (planarVelocity + Vector3.up * verticalVelocity) * Time.deltaTime;
        CollisionFlags flags = characterController.Move(displacement);

        if ((flags & CollisionFlags.Below) != 0 && verticalVelocity < 0f)
            verticalVelocity = -2f;
        if ((flags & CollisionFlags.Above) != 0 && verticalVelocity > 0f)
            verticalVelocity = 0f;

        Vector3 measured = characterController.velocity;
        PlanarSpeed = new Vector2(measured.x, measured.z).magnitude;
    }

    private void LookAround()
    {
        if (Mouse.current == null || viewRoot == null) return;
        Vector2 delta = Mouse.current.delta.ReadValue();

        transform.Rotate(0f, delta.x * mouseSensitivity, 0f);
        cameraPitch = Mathf.Clamp(
            cameraPitch - delta.y * mouseSensitivity,
            -maxLookAngle, maxLookAngle);
        viewRoot.localRotation = Quaternion.Euler(cameraPitch, 0f, 0f);
    }

    private void UpdateCursor()
    {
        if (isInteracting) return;
        if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
        if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame &&
            Cursor.lockState != CursorLockMode.Locked)
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }
    }

    // Later, call SetInteractionMode(true) on entering a monitor/puzzle UI;
    // call SetInteractionMode(false) on exiting it.
    public void SetInteractionMode(bool active)
    {
        isInteracting = active;
        Cursor.lockState = active ? CursorLockMode.None : CursorLockMode.Locked;
        Cursor.visible = active;
    }

    private void OnDisable()
    {
        StatusSpeedMultiplier = 1f;
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }
}
