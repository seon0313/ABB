# ABB - Ai Building Bot
*망치질하다가 접질렸봇*
서울로봇고 2025 3-1 1팀 졸업작품

- [Project_ABB Programe](https://github.com/seon0313/Project_ABB_Program)
- [ABB Server](https://github.com/seon0313/ABB_Server)
- [ABB RealTime API](https://github.com/seon0313/ABB_RealTime_AI)

## 목차

## 팀원

|직급|이름|역할|
|---|---|---|
|조장|[추윤선](https://github.com/seon0313)|시스템 개발|
|팀원|[김윤석](https://github.com/yoon7270)|모듈 코딩 및 프로그램 UI|
|팀원|한행모|모듈 코딩|
|팀원|김재원|디자인 및 설계|
|팀원|[조현수](https://github.com/johyunsu2mb)|디자인 및 설계|

## 개발환경

- OS: Arch Linux (Hyprland), ~~Windows 11~~
- Python: 3.13.3

> ABB는 Windows 시스템에서 동작하지 않습니다. 구동시 WSL2 또는 Linux, Unix, maxOS 환경에서 구동해주세요.

## 프로그램

ABB는 추윤선의 독자 개발 시스템을 구동합니다.


|파일명|설명|
|---|---|
|`robot.py`|로봇의 메인 클래스|
|`log.py`|프로그램의 Log 기록 프로그램|
|`RealTime.py`|[ABB RealTime API](https://github.com/seon0313/ABB_RealTime_AI)|
|`server.py`|Websocket 서버. `robot.py`의 통제를 받는다. 외부 프로그램과 소통을 위한 기능|
|`system.py`|`Event`, `EventListener`, `RobotSystem`등 로봇 시스템 관련 코드|
|`controller.py`|로봇의 움직임 제어 프로그램|

아래는 ABB의 시스템 작동 구조도 입니다.

```
Robot
│  └── Event, RobotSystem
│
├── Server
│
├── RealTime
│
├── Controller
│
└── Background
```

위 하위 클래스들은 `Event`와 `EventListener`를 이용하여 서로 소통합니다.

각 하위 노드들은 별개의 Thread에서 동작합니다.

`RobotSystem`클래스에서 로봇의 Event, Log시스템, 변수를 저장하고 관리합니다.

## 가이드

`onclick_install.py`를 실행하여 실행에 필요한 모듈을 한번에 설치할 수 있습니다.

프로그램을 실행후 필수 모듈을 설치해 주세요.

`Unity` 프로그램을 설치하지 않았을 시 `/Debug`에서 `app.py`를 실행하여 서버에 접속할수 있는 웹프로그램을 실행할수 있습니다. 인터넷 브라우저에서 접속후 사용하세요. `port = 9181`
(필수 기능만 사용가능)