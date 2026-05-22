## Wumpus World 개발 기록

현재까지 Wumpus World의 기본 환경 구성과 GUI 기반 탐색 시스템을 구현하였습니다.

또한 Direction 기반 Action 구조와 DFS(Depth-First Search) 기반 자동 탐색 알고리즘을 적용하여, 에이전트가 스스로 환경을 탐험할 수 있도록 구현하였습니다.

프로젝트 개발 과정 및 단계별 구현 내용은 Velog에 정리하였습니다.

👉 https://velog.io/@ccy8497/Wumpus-World-Project

---

## 현재 구현 완료 기능

- Wumpus World 맵 생성
- Tkinter GUI 기반 화면 출력
- Wumpus / Pit / Gold 오브젝트 배치
- Direction 기반 Action 시스템
- DFS 기반 자동 탐색
- Percept 기반 위험 추론
- DFS Backtracking 구현
- 탐험 정보 시각화

---

## 향후 구현 예정 기능

- Shoot 기능
- Grab 기능
- Climb 기능
- Gold 획득 후 탈출 로직
- Wumpus 제거 기능
- 최종 게임 종료 조건 구현
