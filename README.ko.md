# Sinopia

> *Sinopia*(시노피아) — 르네상스 프레스코화에서 젖은 회반죽이 굳어 수정이 불가능해지기 전, 거친 초벌 벽면에 붉은 흙으로 그리는 구조 밑그림.

**잘 모르는 분야에서 AI에게 "이거 만들까?"라고 편하게 물으면, AI도 질문의 눈높이에 맞춰 답합니다** — 입문자용 원론, 완곡한 조언, 그리고 말하지 않은 조건을 그럴듯한 추측으로 채운 계획이 돌아옵니다.

**Claude Code**, **Antigravity**, **Codex CLI**를 위한 착수 전 검토 스킬입니다. Sinopia는 일상어로 짧은 상담을 진행해 의도를 확인한 뒤, 사실관계·제약·미확정 변수·실패 모드를 정제된 시니어 브리프로 정리하고, 격리된 새 컨텍스트의 전문가가 **오직 그 정제된 브리프만 보고** 검토하도록 분리합니다. 코드를 짜거나 에셋을 뽑고 비용을 쓰기 전에 결론 우선의 `Go / Conditional Go / Pilot-First / No-Go` 브리핑을 받아볼 수 있습니다.

`/sinopia` · `/snp` · 평문 파일 2개 · 의존성 0 · 엄격한 읽기 전용 · [English README](./README.md)

---

## 언제 쓰면 좋은가

- **되돌리기 비싼 작업에 들어가기 직전** — BGM·아트 대량 생성, 영상 포맷 설계, 새 아키텍처 도입, 유료 연동처럼 전제가 틀리면 수 시간이나 크레딧이 날아가는 작업 전.
- **내 주력 분야가 아닌 영역을 디렉팅할 때** — 오디오·비주얼 디렉팅, 계약·약관, 외주 브리프, 가격 정책, 낯선 기술 스택처럼 일상어 발주가 AI의 입문자 기본값으로 흐르기 쉬운 작업.
- **본작업 전에 깔끔한 `Go / Pilot-First / No-Go` 관문이 필요할 때** — 파일 수정이나 커밋 없이 판단 근거와 통과 게이트만 먼저 확인하고 싶을 때.

단순 버그 수정, 범위가 명확한 코드 편집, 사실 조회, 자유 발산 브레인스토밍에는 직접 실행하는 편이 빠릅니다.

---

## 빠른 시작

**Claude Code**, **Antigravity (`agy`)**, **Codex CLI** 중 하나가 필요합니다. 스킬 실행 자체에는 Python·Node 등 별도 런타임 의존성이 전혀 없습니다.

### 1. 설치

저장소를 클론하고 [`skill/sinopia/`](./skill/sinopia/)의 평문 파일 2개를 직접 확인한 뒤 로컬 설치 스크립트를 실행합니다.

```bash
git clone https://github.com/Excelsus4/sinopia.git && cd sinopia

# macOS / Linux / Git Bash
bash tools/install.sh --dry-run
bash tools/install.sh --target claude                # claude | agy | codex | all | auto
bash tools/install.sh --target agy --agy-mode plugin # agy 기본값 (또는 --agy-mode skill)
```

```powershell
# Windows PowerShell 5.1+ / PowerShell 7
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all
```

<details>
<summary>수동 복사 설치 (인스톨러 미사용)</summary>

`cp -r` 실행 시 `sinopia/sinopia`로 중첩되지 않도록 기존 폴더가 있다면 먼저 지우고 복사합니다.

```bash
# Claude Code (+ /sinopia, /snp 슬래시 커맨드)
mkdir -p ~/.claude/skills ~/.claude/commands
rm -rf ~/.claude/skills/sinopia
cp -r skill/sinopia ~/.claude/skills/sinopia
cp commands/*.md ~/.claude/commands/

# Antigravity (agy) — skill 모드 (네이티브 plugin 모드는 tools/install.* 사용)
mkdir -p ~/.gemini/config/skills
rm -rf ~/.gemini/config/skills/sinopia
cp -r skill/sinopia ~/.gemini/config/skills/sinopia

# Codex CLI
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/sinopia
cp -r skill/sinopia ~/.codex/skills/sinopia
```

</details>

### 2. 작업 공간에서 실행

검토하고 싶은 프로젝트 워크스페이스(또는 일반 세션)에서 명시적으로 호출합니다.

```text
/sinopia 모바일 MVP 출시 전에 오프라인 동기화까지 넣는 게 맞을까?
/snp 외주로 사운드 팩을 발주하려는데, 계약 전에 놓치기 쉬운 함정부터 검토해줘
```

Sinopia는 프로젝트 문서에 이미 적힌 내용은 건너뛰고 필요한 질문만 일상어로 확인한 뒤, 이해한 내용을 요약해 확인을 받고 격리 전문가 검토를 거쳐 깔끔하게 판정 브리핑으로 마무리합니다.

---

## 왜 같은 대화창 재정식화보다 정제된 격리 브리프가 나은가

같은 대화 안에서 *"먼저 전문가처럼 정리한 뒤 검토해줘"*라고 요청해도, 앞에 남은 구어체 원문과 분위기 때문에 모델의 어텐션이 계속 기존 프레임에 묶입니다. Sinopia는 접수와 심의 사이에 컨텍스트 경계를 둡니다.

| 방식 | 검토자가 보는 입력 | 흔한 한계 |
|---|---|---|
| **직접 질문** (*"출시 전에 오프라인 동기화 넣을까?"*) | 구어체 질문 + 빠진 제약 조건 | 교과서식 장단점 나열, 팀 규모·충돌 처리 기준·일정을 임의로 추정 |
| **같은 대화창 재정식화** (`/plan` 또는 동일 스레드 RaR) | 정리된 문장 **+** 앞선 구어체 대화 전체 | 초기 프레임과 완곡한 브레인스토밍 톤에 계속 끌려감 |
| **Sinopia** (Stage 1 -> Stage 2 -> Stage 3) | **정제된 시니어 브리프만** (확인된 사실, 안티골, 명시적 미확정 변수, 근거 있는 실패 모드) | 추측 없이 실패 메커니즘 방어, 미확정 변수의 `If-Then` 분기, 검증 게이트에 집중 |

---

## 동작 흐름

1. **Stage 1 — 일상어 상담 및 미러백 확인 (메인 컨텍스트):**
   - 워크스페이스 문서를 먼저 조용히 읽어 이미 문서화된 내용은 다시 묻지 않습니다.
   - 결론을 바꾸는 핵심 변수만 일상어로 확인하며, *전달 선호*("쉽게 설명해줘")와 *실제 설계 제약*("최종 사용자가 초보자")을 분리해 처리합니다.
   - 이해한 내용을 3~6줄로 요약해 확인을 받은 뒤에야 Stage 2로 넘깁니다. (사용자가 처음부터 확인 생략을 명시한 경우 미확인 추론은 모두 `Explicit Unknowns`로 넘깁니다.)
   - 확정된 의도를 건조하고 명확한 시니어 브리프로 정제합니다.
2. **Stage 2 — 블라인드 시니어 검토 (격리된 새 컨텍스트):**
   - 대화 이력이나 `fork` 상속이 없는 새 읽기 전용 서브에이전트를 띄워 **정제된 브리프와 검토 규칙만** 전달합니다. (격리 실행이 실패하면 메인 대화에서 몰래 대체 실행하지 않고 즉시 알린 뒤 중단합니다.)
   - 미확정 변수는 임의로 가정하지 않고 `If-Then` 조건 분기로 처리하며, 실측 지표나 시장 취향이 필요한 지점은 `[External Validation Required]`로 표시합니다.
3. **Stage 3 — 원의도 대조 브리핑 및 하드 스톱 (메인 컨텍스트):**
   - Stage 2 결과를 사용자의 원래 의도·제약·안티골과 양방향으로 대조해 번역 누락이나 톤 완화를 점검합니다.
   - 사용자의 언어와 원하는 밀도에 맞춰 결론 우선 브리핑을 전달하고, 파일 수정·계획 문서 생성·커밋 없이 깔끔하게 멈춥니다.

---

## 결과 브리핑 형식

브리핑은 판정과 의도 정합성 체크로 시작해 핵심 함정 방어선, 권장 설계 또는 최소 파일럿과 통과 게이트, 외부 검증 경계 순으로 정리됩니다.

```text
판정: Go | Conditional Go | Pilot-First | No-Go — 1~2줄 핵심 이유
의도·격리 체크: Stage 1/2 과정에서 원래 목표·제약과 어긋난 가정이 없는지 확인

1. 만들기 전에 막아야 할 핵심 함정
   - <실패 모드>: 깨지는 메커니즘 + 구체적 방어 규칙

2. 권장 실행 설계 및 착수 전 QA 게이트
   - 권장 접근 방식 또는 최소 파일럿
   - 측정 가능한 통과/실패 게이트 3~5개
   - 조건 분기 (미확정 변수가 남은 경우에만 IF -> THEN)

3. 외부 검증이 필요한 경계
   - 순수 추론으로 확정할 수 없고 실측·가격·소규모 파일럿이 필요한 항목
```

브리핑을 본 뒤 본작업 착수, 소규모 파일럿 실행, 조건 재정의 후 재검토, 발산 탐색 전환, 중단 중 원하는 다음 단계를 직접 결정하면 됩니다.

---

## 적용 범위

Sinopia는 **평문 파일 2개**([`SKILL.md`](./skill/sinopia/SKILL.md), [`references/prompt_templates.md`](./skill/sinopia/references/prompt_templates.md))만으로 동작하는 의존성 0의 착수 전 검토 스킬입니다. 워크스페이스 파일을 수정하거나 계획 문서를 임의로 만들지 않으며, 커밋도 하지 않습니다. 실제 사용자 테스트, 시장 리서치, 빌드 후 QA를 대체하지 않고 그 앞단의 설계 판단을 돕습니다.

---

## 로컬 검증 (개발용)

테스트 스위트는 Python 3.9+ 표준 라이브러리(`unittest`)만 사용합니다.

```bash
python3 -m unittest tools/test_tools.py -v
bash tools/install.sh --target all --dry-run
```

Windows PowerShell:

```powershell
python -m unittest tools/test_tools.py -v
powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all -DryRun
```

---

## 동반 도구 및 라이선스

| 도구 | 단계 | 역할 |
|---|---|---|
| **Sinopia** *(현재 저장소)* | 착수 전 | 일상어 상담 + 정제된 브리프의 격리 시니어 검토 |
| **[Sfumato](https://github.com/Excelsus4/sfumato)** | 아이디어 발산 | LLM 획일화를 깨는 크로스도메인 탐색 |
| **[Sprezzatura](https://github.com/Excelsus4/sprezzatura)** | 사후 QA | 로컬 테스트를 통과하는 환경·경계 결함 읽기 전용 감사 |

[MIT 라이선스](./LICENSE)로 배포됩니다.
