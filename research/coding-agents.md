# Coding / Software-Engineering Agents & Their Benchmarks (state of the art, Oct 2026)

_Research date: 2026-10-08. All star counts from GitHub API (`/repos/OWNER/REPO`) on 2026-10-08. All
"latest release" values from `/releases/latest` on 2026-10-08 unless a different date is stated.
Download counts = npm `last-week` (2026-09-28 → 2026-10-04) or PyPI latest upload date._

## Key findings (2026)

- **The CLI agent market consolidated around 4 harnesses**: Terminal-Bench 4.0's leaderboard is topped
  *only* by Claude Code (Opus 5.5, 64.85 %) and OpenAI Codex (GPT-6 Astra / GPT-6.1 Sol, 58.18 %) —
  every other entry is 1–2 models behind — source: https://www.tbench.ai/ (fetched 2026-10-08).
- **Google replaced Gemini CLI**: `Gemini CLI was replaced by Antigravity CLI on June 18th, 2026` for
  unpaid + Google One users — https://geminicli.com/docs/ (fetched 2026-10-08). Gemini CLI is still
  shipped/updated (v0.63.0, 2026-10-06) for paid tiers.
- **Windsurf is gone as a brand**: windsurf.com now serves *Devin Desktop* ("Devin Desktop is the new
  name for Windsurf … building on the IDE foundation of Windsurf") under Cognition, positioned as a
  command centre for fleets of local+cloud agents — https://windsurf.com/ (fetched 2026-10-08).
- **Continue was acquired by Cursor**: continue.dev's only content is "Continue has joined Cursor";
  the Apache-2.0 codebase remains public — https://continue.dev/ (fetched 2026-10-08).
- **Tabnine is now a Tricentis product**: tabnine.com serves "Agentic Quality Engineering Platform –
  Tricentis"; `codota/TabNine` (10,769 stars) is archived — https://www.tabnine.com/ (fetched 2026-10-08).
- **Roo Code shut down its OSS IDE agent**: `RooCodeInc/Roo-Code` (24,284 stars) archived 2026-05-15;
  roocode.com now sells *Roomote*, a cloud coding agent — https://github.com/RooCodeInc/Roo-Code,
  https://roocode.com/ (fetched 2026-10-08).
- **Kilo now sits inside Anaconda's "AI Dev Factory"**: kilo.ai headlines "Anaconda launches new
  capabilities across the AI Dev Factory starting with Kilo Desktop" and the site sells a VS Code /
  JetBrains / CLI / Cloud / Slack / Mobile agent — https://kilo.ai/ (fetched 2026-10-08).
- **Codegen exited the agent business**: "Codegen has joined ClickUp"; codegen.com is now a
  skills/agents directory — https://codegen.com/ (fetched 2026-10-08).
- **Ona (ex-Gitpod) is "Part of OpenAI Platform"** — https://ona.com/ (fetched 2026-10-08).
- **AWS is retiring Amazon Q Developer IDE plugins (end of support 2027-04-30) and points users to
  Kiro** — https://aws.amazon.com/q/developer/ (fetched 2026-10-08). Google is sunsetting Firebase
  Studio on 2027-03-22, pointing to AI Studio / Antigravity — https://firebase.google.com/studio.
- **SWE-bench Verified is frozen for frontier labs**: since 2025-11-18 only academic/research
  submissions are accepted; the leaderboard still tops out at **79.20 %** (Sonar Foundation Agent +
  Claude 4.5 Opus, 2025-12-05 / live-SWE-agent + Claude 4.5 Opus, 2025-12-15), newest entry
  2026-02-26 — https://raw.githubusercontent.com/SWE-bench/experiments/main/README.md and the
  embedded `leaderboard-data` JSON at https://www.swebench.com/ (fetched 2026-10-08).
- **Terminal-Bench is now semantic-versioned and continuous (TB 4.0, 2026-08-29)**; saturated tasks
  are deleted instead of "TB 5" being built — https://www.tbench.ai/news/terminal-bench-4-0
  (fetched 2026-10-08).
- **Aider's polyglot leaderboard is stale** (top = gpt-5 (high), 88.0 %, run 2025-08-23, $29.08) and
  its repo has had no release since v0.86.0 (2025-08-09; last push 2026-05-22) —
  https://aider.chat/docs/leaderboards/ (fetched 2026-10-08).
- **LiveCodeBench stopped publishing 2026 data**: the leaderboard loads `v5.json`, whose newest
  performance row is dated 2025-01-05; repo last push 2025-07-16 —
  https://livecodebench.github.io/leaderboard.html, https://livecodebench.github.io/v5.json.
- **New benchmark layer in 2026**: DeepSWE (v1.1, updated 2026-09-22, top 74 %), ProgramBench
  (2026-09-28, top 4.5 % resolved), SWE-bench Pro (top 61.50 %), Senior SWE-Bench (top 34.7 %),
  Real-SWE (Sep 2026, top 46.25 %), OSWorld 2.0/2.1, SWE-rebench-v2, METR's "many SWE-bench-passing
  PRs would not be merged" note (2026-03-10) — sources in §4.
- **AGENTS.md won the context-file war**: agents.md claims "used by over 60k open-source projects"
  and lists Codex, Jules, Factory, Aider, goose, opencode, Zed, Warp, VS Code, Devin, UiPath, Junie,
  Amp, Cursor, RooCode, Gemini CLI, Kilo Code, Semgrep, GitHub Copilot, Ona, Windsurf/Devin Desktop,
  Augment; **Claude Code now reads a repo's `AGENTS.md` in place of `CLAUDE.md`** —
  https://agents.md/, https://code.claude.com/docs/en/memory (fetched 2026-10-08).
- **Agent Skills (SKILL.md) became an open standard** (published as such on 2025-12-18) with
  `anthropics/skills` at **180,133 stars** and a third-party directory at skills.sh; the 2026
  "skills" repo wave is enormous (e.g. `affaan-m/ECC` 275,261 stars, `addyosmani/agent-skills`
  103,203 stars) — https://agentskills.io/, https://www.anthropic.com/news/skills, https://skills.sh/.
- **Sandbox layer is normalised on microVMs**: E2B (e2b 2.53.1, 2026-10-06), Modal 1.6.1
  (2026-10-03) + "VM Sandboxes", Fly.io **Sprites**, microsandbox 0.7.7, Firecracker 1.17.0;
  Terminal-Bench itself recommends "running on Modal or Daytona" — https://www.tbench.ai/tasks.
- **Harbor** (`harbor-framework/harbor`, 5,916 stars, v0.24.0 2026-10-05) replaced the old
  `terminal-bench` CLI as the sandboxed agent-evaluation runner (`harbor run -d terminal-bench/terminal-bench`).