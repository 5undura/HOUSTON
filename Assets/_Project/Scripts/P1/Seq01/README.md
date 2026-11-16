# HOUSTON P1 - SEQ 01 외부 카메라와 위치 확인

사진 촬영 → 잔해 특징을 P2에게 말로 설명 → P2가 알려준 구역 코드 입력 → 현재 위치 확인까지 구현합니다. 현재 위치 확인과 우주선 이동은 별개입니다.

## 1. 가져오기

1. ZIP을 풉니다. `.cs` 파일을 Unity 프로젝트에서 팀이 정한 `Assets` 아래 스크립트 폴더에 넣습니다. UI는 uGUI와 TextMesh Pro를 사용합니다.
2. 플레이어 카메라에 `P1BasicControls`를 붙입니다. 카메라 바깥에 빈 오브젝트 네 개를 만들고, 각각의 로컬 Z축이 바라볼 패널 쪽을 향하도록 회전시킵니다. `Navigation View`, `External Camera View`, `System Pc View`, `Repair View`에 차례로 연결합니다. 카메라는 마우스 커서가 움직이는 상태에서 테스트합니다.

## 2. 외부 카메라 조작판

1. 조작판 부모 오브젝트에 `P1ExternalCamera`를 붙입니다.
2. `Up Photo`, `Right Photo`, `Down Photo`, `Left Photo`에 이미지 에셋을 넣습니다. 임시 테스트에는 서로 다른 PNG 네 장이면 됩니다. 정답 단서가 보이는 잔해 이미지는 한 방향에 넣고 나머지는 다른 장면으로 구분합니다. 이미지는 ZIP에 포함되지 않습니다.
3. 모니터 앞에 World Space Canvas를 두거나 먼저 화면 Canvas로 테스트합니다. 캔버스에 Raw Image를 만들고 `Photo Display`에 연결합니다. 조준 방향과 결과 텍스트가 필요하면 `Direction Text`, `Feedback Text`에 각각 `TextMeshPro - Text (UI)`를 연결합니다. 사진이 없을 때는 Raw Image만 숨겨지므로 모니터 배경은 별도 오브젝트로 둡니다.
4. 각각의 3D 버튼에 `BoxCollider`(`Is Trigger` 끔)와 `P1WorldButton`을 추가합니다. `On Pressed`에서 `+`를 누르고 `P1ExternalCamera`가 붙은 오브젝트를 연결한 뒤 해당 함수를 선택합니다. 2D UI 버튼을 쓴다면 `Button > On Click()`에 같은 함수를 연결합니다.

| 버튼 | 연결할 함수 |
|---|---|
| 위 / 오른쪽 / 아래 / 왼쪽 | `AimUp()` / `AimRight()` / `AimDown()` / `AimLeft()` |
| 촬영 | `CapturePhoto()` |
| 삭제 | `DeletePhoto()` |

방향만 바꿔서는 새 사진이 나오지 않습니다. 촬영을 눌러야 해당 방향의 이미지가 저장되고 모니터에 표시됩니다. 사진은 한 장만 보관하고 새 촬영이 이전 사진을 덮어씁니다. 삭제는 화면만 비웁니다. 이미 사진을 찍었다는 기록까지 지우지는 않습니다.

## 3. 항법 패널에서 위치 확인

1. 항법 패널에 `P1LocationConfirm`을 붙입니다. Canvas에 `TMP_InputField`와 `TextMeshPro - Text (UI)` 두 개를 만들어 `Sector Input`, `Position Text`, `Feedback Text`에 각각 연결합니다. 입력칸은 `Content Type: Standard`, `Line Type: Single Line`을 권장합니다. 하이픈(`-`)이 필요하므로 숫자 전용이나 영숫자 전용으로 설정하지 않습니다.
2. `External Camera`에는 `P1ExternalCamera` 컴포넌트를 연결합니다. 기본값은 첫 사진을 찍어야 위치를 확인할 수 있습니다. 위치 입력만 따로 테스트하려면 `Require Photo Before Confirm`을 잠시 끌 수 있습니다.
3. `Expected Sector`를 P2 데이터베이스가 안내하는 코드와 똑같이 맞춥니다. `C-2`는 테스트용 예시입니다. 입력 칸의 플레이스홀더에는 정답 코드를 표시하지 않습니다.
4. 확인 버튼의 `On Pressed`(3D) 또는 `On Click()`(UI)에 `P1LocationConfirm.Submit()`을 연결합니다. 입력칸에 포커스를 두고 Enter를 눌러도 확인됩니다. Enter는 코드가 자동으로 연결하므로 입력 칸의 `On Submit`에 추가 등록하지 않습니다.
5. 성공 시 한 번 호출되는 `On Location Confirmed`는 다음 단계 연결용입니다. 아직은 비워둬도 됩니다. 여기서 우주선 이동 버튼을 바로 활성화하지 않습니다. 그 기능은 회로 수리 성공 후에 연결합니다.

## 4. UI와 3D 버튼이 함께 있는 씬에서

- 씬에 EventSystem 하나와 프로젝트 입력 설정에 맞는 UI 입력 모듈을 둡니다. 새 Input System이면 `Input System UI Input Module`, 기존 입력이면 `Standalone Input Module`을 사용합니다. World Space Canvas의 Event Camera에는 플레이어 카메라를 연결하고 `Graphic Raycaster`를 확인합니다.
- 사진, 배경, 라벨처럼 클릭이 필요 없는 그래픽은 `Raycast Target`을 끕니다. 입력 칸과 UI 버튼은 켜 둡니다. UI가 앞에 있으면 같은 클릭으로 뒤의 3D 버튼도 눌리지 않습니다.
- 위치 입력 칸에 포커스가 있을 때 상단 숫자 `1`~`4`는 입력에만 사용됩니다. 입력 칸 밖을 클릭하면 다시 패널 시점 전환에 쓸 수 있습니다.

## 5. 테스트 순서

1. 외부 카메라에서 다른 방향을 선택합니다. 화면에는 저장된 사진이 없거나, 이전에 찍은 사진만 계속 보여야 합니다.
2. 촬영 → 선택한 방향 사진 표시 → 삭제 → 화면에서 사진 사라짐 → 다시 촬영을 확인합니다.
3. 항법 패널로 전환하고 입력 칸에 `B-3`을 입력합니다. `3`을 눌러도 시스템 PC로 시점이 전환되지 않아야 하며, 확인하면 오답 안내가 표시됩니다. `C-2`를 입력할 때 `2` 역시 외부 카메라 패널로 시점을 바꾸면 안 됩니다.
4. P2가 불러준 코드 `C-2`를 입력하고 확인합니다. `LOCATION CONFIRMED`와 `CURRENT SECTOR: C-2`가 표시되고 입력이 잠겨야 합니다. 예시 코드 외에 팀 실제 코드를 쓰면 테스트 값도 바꿉니다.

아직 포함하지 않은 기능은 실제 3D 외부 카메라 촬영, P2 데이터베이스와 음성 통신, 우주선 이동, 회로 수리, 진행 저장입니다. 확인 성공 전에는 게임을 중단하지 않고 다른 구역 코드를 다시 입력할 수 있습니다.
