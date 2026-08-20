# SATURN v1.0 Architecture

## 1. Product Definition

SATURN is a general-purpose desktop AI agent that accepts voice or text requests, reasons using local or cloud AI, executes computer actions through controlled tools, verifies outcomes, recovers from failures, and communicates naturally.

## 2. Core Principles

- Agentic execution
- Hybrid local/cloud intelligence
- Risk-based permissions
- Tool-mediated computer control
- Verification after actions
- Adaptive recovery and replanning
- Local-first memory
- On-demand screen vision
- Extensible plugins
- Environment-aware operation
- Voice and text interfaces

## 3. High-Level Architecture

```text
                         SATURN
                            |
             +--------------+--------------+
             |                             |
        SATURN CORE                 CONTROL CENTER
      background runtime                  UI
             |                             |
             +--------------+--------------+
                            |
                  Local authenticated API
                            |
       +--------------------+--------------------+
       |                    |                    |
      AI                   AGENT               MEMORY
       |                    |                    |
   +---+---+          TASK ORCHESTRATOR       SQLite
   |       |                    |             retrieval
 Local   Cloud              TOOL SYSTEM
                             |
          +------------------+------------------+
          |         |         |        |         |
       Windows   Browser    Files   Plugins   Developer
```

## 4. SATURN Core

The Core is a background runtime independent of the UI. It manages requests, conversations, AI routing, tasks, tools, memory, permissions, notifications, plugins, logging, errors, and verification.

## 5. Control Center

A separate UI process for chat, task visibility, memory, tools, activity, permissions, plugins, system information, and settings. Closing the UI must not terminate the Core.

## 6. Local API

Core and UI communicate through a localhost-only authenticated API. The interface is designed so future clients can connect without coupling them to internal implementation details.

## 7. Input

SATURN accepts voice, keyboard shortcuts, text, and UI interactions.

Voice pipeline: microphone -> wake word -> speech-to-text -> Core.

## 8. AI System

All model providers are hidden behind a common AI interface. SATURN v1 supports a local model path and a cloud model path. The rest of the system must not depend directly on a specific provider.

## 9. AI Router

The router selects local or cloud intelligence using task complexity, privacy, model availability, connectivity, latency, and cost considerations.

## 10. Agent

SATURN uses hybrid planning and replanning. It creates a high-level plan, executes one step, observes the result, verifies it, and either continues or replans when conditions change.

## 11. Task Orchestrator

Tasks have explicit lifecycle states and support dependencies, priority, cancellation, retries, timeouts, and parallel execution where safe.
The current v1 implementation executes plans step-by-step with lifecycle transitions (PENDING, PLANNING, EXECUTING, VERIFYING, COMPLETED, FAILED, CANCELLED), verification after each step, bounded retries, and bounded replanning loops.

## 12. Tool System

AI never receives unrestricted operating-system execution. It emits structured tool calls. The permission engine evaluates them, the tool executor performs them, and verification reports the outcome.

## 13. Initial Tool Categories

- Windows applications and windows
- Keyboard and mouse
- Screenshots
- Clipboard
- Audio and display controls
- Processes and power
- Browser navigation and interaction
- File operations
- Developer tools
- Communication tools
- Future external-device integrations

## 14. Vision

Screen vision is on-demand. SATURN activates screenshot/vision analysis only when visual understanding is required, then returns to normal operation.

## 15. Memory

Memory is divided conceptually into short-term task context, long-term useful information, and knowledge/document retrieval. v1 stores local structured data in SQLite. Large-file architecture is intentionally deferred.

## 16. Security

Actions are classified by risk. Low-risk actions can execute automatically. Medium-risk actions may require contextual confirmation. High-risk and critical actions require explicit confirmation. Critical actions always require confirmation.

## 17. Secrets Vault

Passwords, API keys, tokens, and other secrets are kept in a dedicated encrypted vault rather than ordinary memory. Tools request access through the vault and permission system.

## 18. Plugins

SATURN supports installable plugins containing tools, configuration, permissions, dependencies, versions, and metadata. SATURN may generate a candidate plugin, but it must pass security/testing checks and receive user approval before installation.

## 19. Operational Learning

SATURN can store successful actions, failures, recovery strategies, user corrections, and useful workflows. v1 does not autonomously modify model weights. Model training is a deliberate future development process.

## 20. Verification

Tools should verify their effects whenever feasible. SATURN must not claim success when it has evidence that an action failed or when required verification has not completed.

## 21. Error Recovery

Failures are analyzed for safe recovery. SATURN may retry or adapt when a safe recovery exists; otherwise it asks the user. Successful recovery strategies may become operational memory.

## 22. Personality

SATURN is intelligent, sarcastic, funny, and competent. Personality must never override safety, accuracy, permissions, or explicit user instructions.

## 23. Notifications

Notifications are context-aware: low-priority items remain in the task queue, attention items use Windows notifications, important items may also use voice, and dangerous actions require visible confirmation.

## 24. Environment Detection

SATURN must work across different user machines without hard-coded personal paths. It detects OS, CPU, GPU, RAM, storage, audio devices, browsers, applications, permissions, network state, and local AI availability.

## 25. Distribution

Development dependencies may include Python, Git, and build tooling. End users should eventually receive SATURN as a packaged Windows application with first-run environment detection and configuration.

## 26. Updates

SATURN supports update checking and downloads, controlled installation for normal releases, prioritized security fixes, release notes, and rollback where practical.

## 27. Development Strategy

Build in milestones: foundation -> Core/UI API -> AI -> agent -> first tools -> voice -> security -> memory -> plugins -> packaging.

Architecture changes must be deliberate and documented before implementation branches diverge.
