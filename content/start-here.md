## Just getting started? Start here

You don't need 500 links. Depending on what you're trying to build, this is the shortest path:

| If you want to… | Start with | Then read |
|---|---|---|
| **Understand the field** | Anthropic's *Building effective agents* and OpenAI's *A practical guide to building agents* | the surveys in [Concepts & Context Engineering](#-concepts--context-engineering) |
| **Build your first agent** | A batteries-included SDK: OpenAI Agents SDK, Claude Agent SDK or Google ADK | [Frameworks & SDKs](#-frameworks--sdks) |
| **Give an agent tools** | The Model Context Protocol, then an MCP server library or gateway | [Tooling, Function Calling & MCP](#-tooling-function-calling--mcp) |
| **Make it reliable** | Tracing first (Langfuse/Opik/Phoenix), then an eval suite | [Evaluation, Benchmarking & Observability](#-evaluation-benchmarking--observability) |
| **Make it safe to run** | A sandbox runtime and a guardrail layer | [Runtimes, Sandboxes & Deployment](#-runtimes-sandboxes--deployment) + [Safety, Security & Guardrails](#-safety-security--guardrails) |
| **Automate coding** | A terminal agent (Claude Code, Codex CLI, Gemini CLI) + an AGENTS.md file | [Coding Agents & Software Engineering](#-coding-agents--software-engineering) |
| **Automate the browser** | browser-use, Playwright MCP or a hosted browser-agent platform | [Browser, Web & Computer-Use Agents](#-browser-web--computer-use-agents) |
| **Ship to production** | A managed runtime, then a gateway for routing and cost control | [Runtimes, Sandboxes & Deployment](#-runtimes-sandboxes--deployment) + [Gateways, Routing & Model Serving](#-gateways-routing--model-serving) |
| **Talk to a customer** | A voice stack (LiveKit Agents, Pipecat, Vapi) or a support platform | [Voice & Realtime Agents](#-voice--realtime-agents) |

**Anti-patterns the ecosystem learned the hard way (2024 → 2026):**

- Don't start with a multi-agent framework. Start with one agent, one tool, one loop, and a
  trace. Add agents when a single context window genuinely can't hold the job.
- Don't build your own memory store before you've measured retrieval quality. Most "agent
  forgets things" bugs are retrieval bugs, not memory bugs.
- Don't skip evals until launch. Agent behaviour drifts when *any* dependency changes: model,
  prompt, tool schema, retrieval index. Pin and re-run.
- Don't hand a production agent a shell without a sandbox and an egress policy.