using UnityEngine;

// HOUSTON: 환풍기 날개처럼 계속 도는 물체. 플레이 중에만 돈다.
public class HoustonSpin : MonoBehaviour
{
    public Vector3 axis = Vector3.up;   // 로컬 축
    public float degreesPerSecond = 200f;

    void Update()
    {
        transform.Rotate(axis, degreesPerSecond * Time.deltaTime, Space.Self);
    }
}
