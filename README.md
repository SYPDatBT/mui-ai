# EMINEL Gateway (E-GW) Onboarding Workspace

A self-contained, portable knowledge workspace for onboarding the **EMINEL Gateway (E-GW)** project — an initiative to replace the legacy Maxell gateway with the mui gateway (Aqara M300) and migrate the server side to the EMINEL-Smart / ESTA platform, with Hokkaido Gas (Kitagas) as the end customer. The work is carried out by SYP (a Vietnamese vendor of mui Lab).

This repository is **not** the project source code. It is the onboarding and working-state workspace: study documents, Q&A with the customer, cross-session memory for AI agents, reusable AI skills, and dated deliverables. The idea is that the entire working state lives in this one folder — move it to another machine, point it at the project repositories, and continue working exactly where you left off.

## What's inside

| Path | Description |
|---|---|
| `CLAUDE.md` | AI bootstrap file — the first file any AI agent must read. Defines the workspace layout, operating rules, communication conventions, and security constraints. |
| `AGENTS.md` | Short entry point for any AI agent (Claude, Copilot, Cursor, …) pointing to the required reading order. |
| `requirements/` | The study documentation set. `README.md` is the design/review framework for the documents; `onboarding_guide.md` is the main learning guide (v1.1, 10 chapters + 7 appendices, ~4,000 lines) with images in `assets/`; `self_study_plan.md` is the four-track self-study plan. |
| `submit_folder/qa/` | All Q&A files, wherever the questions are headed (customer via mui PM, or mui itself) — e.g. `qa_kitagas.md`, the bilingual (Vietnamese–Japanese) question list for the customer. New files go here and carry the date in the filename: `qa_<topic>_<YYYYMMDD>.md`. |
| `memory/` | Cross-session memory for AI agents: `00_INDEX.md` (operating rules ⛔ + current progress + file map — always read first) and dated `NN_session_*.md` files recording what was done and what is still in flight. |
| `skillAI/` | Reusable AI skills: `notion-connect`, `slack-connect`, `update-memory`, and `3-step-review` (a three-pass document review process plus new-machine setup procedure). Read each skill's `SKILL.md` before use. |
| `submit_folder/` | Dated deliverable snapshots (e.g. the legacy batch migration assessment reports). Never edited retroactively. |

## How it works

1. **AI-first workflow** — every session starts with an AI agent reading `CLAUDE.md` → `memory/00_INDEX.md` → the latest starred session file. Progress questions are answered from recorded state, never guessed.
2. **Evidence-based documentation** — every important claim in the guides must cite a source file and line number in the project repositories, with observation clearly separated from speculation.
3. **Persistent memory** — at the end of each working day, the `update-memory` skill captures session state so the next session (possibly on another machine) can resume seamlessly.
4. **Three-pass review** — document changes go through the `3-step-review` skill (accuracy of citations, correctness, readability for a newcomer) before being considered done.

## Related repositories (not included here)

The actual project sources live **outside** this workspace (by default in `../sources/`) and are managed separately:

- `eminel_gw_project` — project documentation (the primary reference)
- `legacy_eminel_docs` — design and code of the legacy system
- `syp-eminelstandard-backend` / `syp-eminelstandard-web-admin` — EMINEL-Smart code (branch `gw-syp-dev`)
- `syp-eminelstandard-app-syp-dev` — Flutter app (ESTA) snapshot

On a new machine, clone/place those repositories yourself and point the workspace at their location. Line-number citations in the onboarding guide correspond to the commit recorded at the top of the guide.

## Conventions

- Working language is Vietnamese; Japanese terminology is kept as-is (with a short explanation on first use). Customer-facing content is written in Japanese keigo and must not contain internal IDs, repository paths, or internal status markers.
- No tokens or API keys (Notion, Slack, …) are ever written into this workspace, including memory and logs.
