#!/usr/bin/env python3
"""First pass at building the catalog from the ranked candidate list.

Human curation then edits data/catalog.json directly (the committed source of truth).
This script only bootstraps it and is kept for reproducibility.

Usage: python3 scripts/curate.py && mv data/catalog.generated.json data/catalog.json
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")

TODAY = "2026-10-08"
ACTIVE_SINCE = "2025-01-01"   # last push must be after this (unless the repo is huge)

# ordered rules: (category, section, pattern, min_stars) - first match wins
RULES: list[tuple[str, str, str, int]] = [
    # -- runtimes / sandboxes / durable execution
    ("runtimes", "Sandboxed execution runtimes",
     r"e2b|daytona|firecracker|microvm|microsandbox|code interpreter|sandbox|gvisor", 400),
    ("runtimes", "Durable execution & workflow engines",
     r"durable execution|workflow engine|temporal|inngest|restate|dbos|trigger\.dev|windmill|prefect|dagster", 800),
    ("runtimes", "Managed agent runtimes & deployment",
     r"agent (runtime|platform|infrastructure)|deploy (ai )?agents|agent server|agent hosting|kagent|agent operator", 400),
    # -- gateways / serving
    ("gateways", "LLM gateways, routers & proxies",
     r"\bgateway\b|llm router|routing|\blitellm\b|portkey|openrouter|ai gateway|bifrost|tensorzero|proxy for openai", 500),
    ("gateways", "Inference servers & local runners",
     r"inference (server|engine)|vllm|ollama|llama\.cpp|text-generation-inference|serving engine|local llm|sglang|lmdeploy|exllama", 1500),
    ("gateways", "Cost, caching & optimisation",
     r"prompt cach|cost (optimis|optimiz|control)|token (counting|budget)|semantic cach|quantiz", 500),
    # -- protocols / interop
    ("protocols", "Agent-to-agent, tool & payment protocols",
     r"agent2agent|a2a protocol|agent protocol|model context protocol|\bmcp\b|agent (communication|interop)|agntcy|x402|agent payments", 300),
    ("protocols", "MCP servers, clients & registries",
     r"mcp (server|client|registry|gateway|proxy|toolkit)|mcp-server|awesome-mcp|fastmcp|mcp-use", 300),
    # -- memory / rag
    ("memory", "Agent memory & state",
     r"agent memory|long[- ]term memory|memory layer|memgpt|letta|\bmem0\b|\bzep\b|graphiti|cognee|langmem|memory bank|memory for (llm|ai)", 300),
    ("memory", "RAG frameworks & pipelines",
     r"\brag\b|retrieval[- ]augmented|retriev|chunking|rerank|document (qa|parsing|loader)", 600),
    ("memory", "Vector, graph & search backends",
     r"vector (database|db|store|search)|embedding (database|store)|similarity search|knowledge graph|graph database|faiss|hnsw|pgvector", 800),
    # -- tooling
    ("tooling", "Tool calling & function calling",
     r"function calling|tool calling|tool[- ]use|tools for (llms|llm|agents)|tool (library|router|registry)", 400),
    ("tooling", "Integrations & API-to-tool bridges",
     r"integrations? (for|with) (llms|ai|agents)|api to tool|composio|toolhouse|openapi (to|for) (llm|agent)|connectors? for (llms|ai agents)", 500),
    ("tooling", "Agent skills & reusable capabilities",
     r"agent skills|skills for (claude|agents)|capabilit(y|ies) library|plugins for (llms|agents)", 300),
]

RULES += [
    # -- coding
    ("coding", "Terminal & CLI coding agents",
     r"coding agent|code agent|cli agent|terminal agent|command[- ]line (coding|ai)|swe agent|software engineering agent|aider|cline|roo code|opencode|codex cli|gemini cli|qwen code", 800),
    ("coding", "IDE & editor agents",
     r"(ide|editor|vscode|jetbrains|vim|neovim) (extension|plugin|agent)|autocomplete for code|copilot for|code completion|pair programm", 600),
    ("coding", "Autonomous issue-to-PR agents",
     r"issue to pr|pull request (agent|review|automation)|code review (agent|bot|ai)|autonomous (bug|fix)|swe[- ]bench", 400),
    ("coding", "Code search, context & repo understanding",
     r"code (search|index|graph|understanding|retrieval)|repository (understanding|mapping)|context for (coding|code)", 400),
    ("coding", "Spec-driven development & agent rule files",
     r"spec[- ]driven|agents\.md|claude\.md|rules for (ai|coding) agents", 200),
    # -- browser / computer use
    ("browser", "Browser-use agents & frameworks",
     r"browser (automation|agent|use)|web agent|autonomous browsing|headless browser for (agents|ai)|playwright (agent|mcp)", 500),
    ("browser", "Computer-use & GUI agents",
     r"computer use|gui agent|screen (understanding|control)|omniparser|ui-tars|osworld|ui automation (with|for) (llm|vlm|agents)", 300),
    ("browser", "Browser infrastructure for agents",
     r"browser (infrastructure|as a service|cloud|pool)|stealth browser|browserbase|browserless|anti[- ]bot", 400),
    # -- voice
    ("voice", "Voice agent frameworks",
     r"voice (agent|ai|bot)|realtime (voice|audio)|speech to speech|conversational (ai|voice)|telephony|pipecat|livekit agents|voice webrtc", 400),
    ("voice", "Speech models & APIs",
     r"speech recognition|text to speech|\btts\b|\bstt\b|asr|voice cloning|audio (model|api)|transcription|whisper", 1200),
    # -- multi-agent
    ("multi-agent", "Multi-agent frameworks",
     r"multi[- ]agent|multiagent|agent swarm|crew of agents|group chat|agent society|collaborative agents", 400),
    ("multi-agent", "Role-play, simulation & generative societies",
     r"role[- ]play|simulation (of|for) agents|generative agents|social simulation|agent village|agent society", 300),
    ("multi-agent", "Graph, plan & orchestration layers",
     r"orchestrat|state machine for agents|graph for agents|planner|task decomposition|dag for (llm|agents)|agent workflow", 600),
    # -- frameworks
    ("frameworks", "General-purpose agent frameworks",
     r"agent framework|framework for (building )?(ai |llm |autonomous )?agents|build (ai|llm|autonomous) agents|agent (sdk|toolkit)|llm application framework", 700),
    ("frameworks", "Typed, minimal & production SDKs",
     r"minimal (agent|framework)|typed (agent|llm)|structured output|type[- ]safe (llm|agent)|pydantic", 500),
    ("frameworks", "Low-code, visual & self-hosted builders",
     r"low[- ]code|no[- ]code|visual (builder|editor|workflow)|drag and drop (ai|agent)|self[- ]hosted (ai|llm) platform|flowise|dify|n8n|langflow", 800),
    ("frameworks", "Prompting, planning & agent design",
     r"prompt (engineering|optimis|optimiz|management)|dspy|chain of thought|reasoning framework|planning for agents|agent design pattern", 700),
    # -- ux
    ("ux", "Chat UIs & agent frontends",
     r"chat (ui|interface|frontend)|web ui for (llm|ai)|copilotkit|assistant-ui|open webui|librechat|chainlit|chatbot ui", 700),
    ("ux", "Generative UI & agent-driven interfaces",
     r"generative ui|agent (ui|ux)|ag-ui|ui components for (ai|agents)|streaming ui", 200),
]

RULES += [
    # -- observability / eval
    ("observability", "Tracing, monitoring & observability",
     r"observability|tracing|telemetry|monitoring for (llm|ai|agents)|langfuse|langsmith|arize|weave|helicone|langwatch|opik|logfire", 300),
    ("observability", "Evaluation frameworks & test suites",
     r"eval(uation)? (framework|suite|harness)|llm evals|testing (framework )?for (llm|agents|prompts)|deepeval|promptfoo|ragas|inspect_ai", 300),
    ("observability", "Benchmarks & leaderboards",
     r"benchmark|leaderboard|swe[- ]bench|gaia|webarena|agentbench|terminal[- ]bench|mle[- ]bench|tau[- ]bench|bfcl", 300),
    ("observability", "Datasets & RL environments for agents",
     r"dataset for (agents|llm)|rl environment|training environment|agent trajectory|reinforcement learning (for|with) (agents|llms)|gym for agents", 200),
    # -- safety
    ("safety", "Guardrails & output validation",
     r"guardrail|content (filter|moderation)|output validation|safety (layer|check)|nemo guardrails|llamafirewall", 300),
    ("safety", "Prompt injection, red teaming & agent security",
     r"prompt injection|jailbreak|red[- ]team|adversarial|agent security|ai security|vulnerabilit|exploit (llm|agent)", 200),
    ("safety", "Identity, permissions & governance",
     r"agent (identity|auth|permission)|oauth for (ai|agents)|policy engine for (ai|agents)|ai governance|audit log for (ai|agents)", 200),
    # -- robotics
    ("robotics", "Robot learning & VLA models",
     r"robot|embodied|vision[- ]language[- ]action|\bvla\b|manipulation|locomotion|lerobot|openvla|gr00t|habitat|mujoco|sim2real", 400),
    # -- applied
    ("applied", "Research & knowledge-work agents",
     r"deep research|research agent|literature review|paper (search|qa)|knowledge work|report generation|scientific (agent|discovery)", 500),
    ("applied", "Data, analytics & BI agents",
     r"data (analysis|analyst|science) agent|text to sql|sql agent|analytics agent|notebook agent", 500),
    ("applied", "Customer, sales & back-office agents",
     r"customer support (agent|ai)|sales (agent|ai)|outreach|sdr|crm (agent|ai)|email agent|inbox|scheduling agent", 400),
    ("applied", "Personal assistants & computer automation",
     r"personal assistant|desktop (agent|automation)|os agent|computer automation|self[- ]operating computer|autogpt", 800),
    ("applied", "Game, simulation & world agents",
     r"game (agent|ai|playing)|minecraft|world model|agent in games|poker|strateg", 400),
    # -- learning
    ("learning", "Courses, books & structured guides",
     r"course|book|tutorial|curriculum|learn (to build|about)|handbook|guide to (building|agents)|from scratch", 300),
    ("learning", "Reference implementations & examples",
     r"examples|reference implementation|starter (template|kit)|template for (agents|ai)|cookbook|recipes", 800),
    ("learning", "Papers, surveys & explainers",
     r"survey|arxiv|paper list|reading list|research (collection|papers)|literature", 500),
    ("learning", "Awesome lists & indexes",
     r"^awesome|awesome list|curated list|collection of (resources|links)", 1500),
]
CATEGORY_META = {
    "learning": ("📚", "Learn, Courses & Reference"),
    "concepts": ("🧠", "Concepts, Papers & Context Engineering"),
    "frameworks": ("🏗️", "Frameworks & SDKs"),
    "coding": ("🖥️", "Coding Agents & Software Engineering"),
    "browser": ("🌐", "Browser, Web & Computer-Use Agents"),
    "voice": ("🗣️", "Voice & Realtime Agents"),
    "multi-agent": ("🤝", "Multi-Agent Orchestration"),
    "tooling": ("🔌", "Tooling, Function Calling & MCP"),
    "memory": ("🧩", "Memory, RAG & Knowledge"),
    "observability": ("🧪", "Evaluation, Benchmarks & Observability"),
    "safety": ("🛡️", "Safety, Security & Guardrails"),
    "runtimes": ("⚙️", "Runtimes, Sandboxes & Deployment"),
    "gateways": ("🚀", "Gateways, Routing & Model Serving"),
    "protocols": ("🧭", "Protocols & Interoperability"),
    "ux": ("🎨", "Agent UX, Frontends & Templates"),
    "applied": ("🏢", "Applied & Vertical Agents"),
    "robotics": ("🤖", "Embodied & Robotics Agents"),
    "commercial": ("💼", "Commercial Platforms & Products"),
}


def slugify(name: str) -> str:
    s = re.sub(r"[^\w\s.-]", "", name.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


def clean_desc(text: str) -> str:
    d = re.sub(r"\s+", " ", text or "").strip()
    d = re.sub(r"^[\-\*\s]+", "", d)
    d = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", d)
    d = d.replace("|", "/").replace("\u2014", "-")
    d = re.sub(r"(?i)^(a|an|the)\s+", "", d)
    d = d.rstrip(" .")
    if len(d) > 240:
        d = d[:237].rsplit(" ", 1)[0] + "..."
    return d


def main() -> int:
    with open(os.path.join(DATA, "candidates.json")) as fh:
        cand = json.load(fh)
    seed_path = os.path.join(DATA, "seed.json")
    seeds = json.load(open(seed_path)) if os.path.exists(seed_path) else {"entries": []}

    seed_repos = {e["repo"].lower() for e in seeds.get("entries", []) if e.get("repo")}
    seed_urls = {e.get("url", "").rstrip("/").lower() for e in seeds.get("entries", []) if e.get("url")}
    used_ids = {e["id"] for e in seeds.get("entries", [])}

    buckets: dict[tuple[str, str], list[dict]] = {}
    skipped = {"archived": 0, "stale": 0, "low_stars": 0, "no_rule": 0, "seeded": 0}
    for r in cand["repos"]:
        if r["archived"]:
            skipped["archived"] += 1
            continue
        if r["pushed_at"] < ACTIVE_SINCE and r["stars"] < 8000:
            skipped["stale"] += 1
            continue
        if r["full_name"].lower() in seed_repos or r["url"].rstrip("/").lower() in seed_urls:
            skipped["seeded"] += 1
            continue
        hay = f'{r["name"]} {r["description"]} {" ".join(r["topics"])}'
        for cid, sec, pat, min_stars in RULES:
            if re.search(pat, hay, re.I):
                if r["stars"] < min_stars:
                    skipped["low_stars"] += 1
                    break
                buckets.setdefault((cid, sec), []).append(r)
                break
        else:
            skipped["no_rule"] += 1

    cats: dict[str, dict] = {}
    for (cid, sec), items in buckets.items():
        items.sort(key=lambda r: -r["stars"])
        cats.setdefault(cid, {}).setdefault(sec, []).extend(items[:60])

    generated = []
    for cid, secs in cats.items():
        emoji, title = CATEGORY_META.get(cid, ("📦", cid.title()))
        sections = []
        for sec, items in secs.items():
            entries = []
            for r in items:
                eid = slugify(r["name"])
                base, i = eid, 2
                while eid in used_ids:
                    eid, i = f"{base}-{i}", i + 1
                used_ids.add(eid)
                entries.append({
                    "id": eid,
                    "name": r["name"],
                    "repo": r["full_name"],
                    "url": r["url"],
                    "description": clean_desc(r["description"]) or "See repository for details",
                    "kind": "oss",
                    "tags": r["topics"][:2],
                    "added": TODAY,
                })
            sections.append({"title": sec, "entries": entries})
        generated.append({"id": cid, "title": title, "emoji": emoji,
                          "description": "", "sections": sections})

    total = sum(len(s["entries"]) for g in generated for s in g["sections"])
    print("generated:", {g["id"]: sum(len(s["entries"]) for s in g["sections"]) for g in generated})
    print("total generated entries:", total, "| skipped:", skipped)
    with open(os.path.join(DATA, "catalog.generated.json"), "w") as fh:
        json.dump({"meta": {"title": "Awesome AI Agents", "repo": "kyliesparks/Awesome-ai-agents",
                            "updated": TODAY, "homepage": "https://github.com/kyliesparks/Awesome-ai-agents"},
                   "categories": generated}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())