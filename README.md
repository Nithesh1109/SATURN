# 🪐 SATURN

**SATURN is a Windows-first AI computer agent that plans, executes, verifies, and safely recovers from desktop tasks.**

The current development branch is `copilot/continue-development-saturn`. It contains the SATURN agent core, cloud AI provider, Windows/desktop tools, screenshot perception, cloud vision adapter, safety validation, verification, safe-mode real-test harness, and automated tests.

## Current status

- **Development version:** v1.0 development
- **Platform:** Windows-first
- **AI:** cloud-first, provider-neutral interface
- **Text model:** NVIDIA NIM / Meta Llama 3.1 8B Instruct by default
- **Vision model:** NVIDIA NIM / Meta Llama 3.2 90B Vision Instruct by default
- **Computer control:** Windows + PyAutoGUI through registered tools
- **Safety:** centralized validation, confirmation gates, safe-mode real-test policy
- **Testing:** deterministic automated tests plus explicit opt-in real cloud smoke tests

The architecture remains the source of truth in `ARCHITECTURE.md`.

## Repository structure

```text
SATURN/
├── src/saturn/
│   ├── agent/       # planning, execution, orchestration, sessions
│   ├── ai/          # provider contracts, cloud/local adapters, router
│   ├── core/        # runtime, local API, HTTP server
│   ├── memory/      # local memory foundation
│   ├── runtime/     # safe mode, real-test and cloud smoke-test entry points
│   ├── security/    # permission contracts
│   ├── tools/       # Windows and desktop tools + validation
│   └── vision/      # screenshot perception, cloud vision, targets, verification
├── tests/           # deterministic automated tests
├── ARCHITECTURE.md
├── .env.example     # safe configuration template; contains no secrets
└── pyproject.toml
```

## Development setup

Create and activate a virtual environment, then install SATURN in editable mode:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

All normal tests are offline and must not require an API key or perform unrestricted desktop actions.

## Cloud AI configuration

SATURN deliberately does **not** store an API key in the repository.

1. Create an NVIDIA API key from the NVIDIA API Catalog.
2. In your PowerShell session, set:

```powershell
$env:NVIDIA_API_KEY="nvapi-..."
```

3. Optional model overrides:

```powershell
$env:SATURN_CLOUD_MODEL="meta/llama-3.1-8b-instruct"
$env:SATURN_VISION_MODEL="meta/llama-3.2-90b-vision-instruct"
```

The NVIDIA hosted API exposes the configured text and vision models through its OpenAI-compatible HTTP interface.

## Real cloud AI smoke test

Before allowing SATURN to control the desktop with a real model, validate the external AI boundaries first:

```powershell
python -m saturn.runtime.ai_smoke
```

This performs a **text-only cloud test** and never executes a desktop action.

To additionally test the vision model with an existing screenshot:

```powershell
python -m saturn.runtime.ai_smoke --vision-image .\saturn_real_test.png
```

Only send screenshots you are comfortable sharing with the configured cloud provider.

## Local Core API

The Core API binds to `127.0.0.1` by default. If `SATURN_API_TOKEN` is configured, POST endpoints require:

```text
Authorization: Bearer <token>
```

`GET /health` remains available for local health checks.

## Safety boundary

Do not skip the validator or safe-mode policy to make a real test pass. AI-generated actions are untrusted input. Real desktop testing should proceed in this order:

```text
Cloud text smoke
      ↓
Cloud vision smoke
      ↓
Screenshot + perception
      ↓
Target validation
      ↓
One harmless desktop action
      ↓
Verification
      ↓
Bounded multi-step task
```

Dangerous operations such as shutdown, lock, deletion, or unrestricted filesystem changes are not part of the first real smoke test.

## License

License to be finalized before the first public release.
