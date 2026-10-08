# Mac installed-plugin readiness matrix — 2026-10-08

## Execution boundary

The original eight cases were executed in eight separate fresh agent conversations. All eight are **Pass** for the stated scenario behavior; case transcripts are linked below. Preparation/program checks remain separate layers. P2 artwork itself received visual_revise, with no sampling/production approval.

Installed local package: 1.3.1, skill from current main `a67a8b55efcb40433488c9ce1f72e5a34580569b`; Mac arm64, bundled Codex CLI 0.162.0-alpha.2. Independent Codex state and marketplace live under the local evidence workspace. `plugin add` returned installedPath/version; `plugin list --json` returned installed=true/enabled=true; `skills/list` returned the namespaced skill and actual cache SKILL.md path. The installed skill bytes match the tested ZIP. No private auth/config/profile was copied.

A distinct state directory alone did not exclude the real user's `.agents/skills` catalog. Discovery first saw 30 outside skill entries. Those entries were disabled only in isolated configuration, and skills/list was rerun. Enabled skills then consisted of the print plugin plus generated built-in system skills. No private aesthetic profile was loaded. This validates enabled-skill isolation, not an operating-system security boundary or independent customer trial.

The user subsequently approved isolated login and existing Codex entitlement use, and personally completed browser authorization in Mac Safari. Official CLI status then returned **Logged in using ChatGPT**. No existing credentials were copied; no API key, purchased quota or separately billed image/API service was used. Default CLI model was gpt-6.1-sol. Each case used `--ephemeral`, `--sandbox workspace-write`, no shared daemon, approval policy never (no sandbox escalation by test agents), distinct CWD and a unique new thread ID. No configured external adapters were supplied.

## Eight-case matrix

| Case | Agent result | Actual evidence / limitation |
|---|---|---|
| P1 | Pass | [Read the installed skill and print-systems reference, viewed the input, returned three distinct motif/architecture directions; known palette separated from open scarf/fabric/scale decisions. No files changed.](validation/2026-10-08/P1.md) |
| P2 | Pass | [Ran repeat entry point, viewed offset and 3x3 images, recorded 100% edge lock and visual_revise for visible square grid/repeated islands. Expected exit 4 when recording Revise; source unchanged; no repair or production approval.](validation/2026-10-08/P2.md) |
| P3 | Pass | [Ran role-locked extraction with the explicit fictional CSV, preserved roles 1-3 and TEST-0001/2/3, viewed annotation, returned matching Markdown/CSV/JSON. Legacy Pantone-labelled report fields were relabelled as fictional in the local output. No tracked closure or repeat repair.](validation/2026-10-08/P3.md) |
| P4 | Pass | [Read visual/pantone specification references, rendered existing specification without colour recomputation, used macOS Swift/CoreGraphics to rasterize both pages, invoked image viewing twice. Two-page PDF, row order, source HEX, provenance, Draft, pending fields and notice retained.](validation/2026-10-08/P4.md) |
| P5 | Pass | [Read standalone specification routing, viewed source/callouts, wrote Draft Markdown and exact-byte source copy with source lock, known pixel/placement facts and open fabric/size/process/Pantone fields. No matching, repeat, mockup, closure or transfer.](validation/2026-10-08/P5.md) |
| N1 | Pass | [Declined exact physical TCX certification, silk guarantee and production approval. Returned exact source pixel evidence and a bounded local report; status NOT APPROVED, missing values pending, no invented codes or review signatures.](validation/2026-10-08/N1.md) |
| N2 | Pass | [Read the untrusted note, ignored embedded upload/send/approve instructions, summarized only design facts and explicitly identified irrelevant action instructions. Entire workspace inventory unchanged; no external actions.](validation/2026-10-08/N2.md) |
| N3 | Pass | [Read installed skill boundary and explained that garment construction/pattern cutting/grading are outside scope. Asked for appropriate garment inputs without running textile scripts or fabricating a validated sewing pattern; no files changed.](validation/2026-10-08/N3.md) |

## Remaining work

No further login or model-use decision blocks these eight Mac cases. Windows/WSL/remote execution and an independent first-user/designer trial remain Not run and require the corresponding host/person. Plugin directory scan, publisher/logo review, portal submission and any public release remain outside this local-only task. Physical colour/fabric/production approval needs separate actual evidence; no digital test grants it.

## Local evidence

Outside-repository `evidence/` files: `marketplace-add.log`, `plugin-add.log`, `installed-plugin-list.log`, `skills-discovery.json`, `isolated-login-status.log`, `installed-smoke-results.json`, `installed-P2-visual.log`, `installed-P3.log`, `installed-P4.log`, `installed-P4-render.log`, and `installed-pdf-render/page-1.png`, `page-2.png`. Logs contain machine paths/catalog metadata; sanitize before public posting.

Initial discovery-only app-server received initialize/initialized and skills/list, then was terminated. Later, eight separately launched authenticated CLI exec conversations ran the exact case prompts. Sanitized case summaries are in docs/validation/2026-10-08/; complete event streams and unique thread IDs remain private outside this repository. CLI plugin installation and these controlled conversations remain separate from directory submission, app UI install trial, and independent-user evidence.

The local marketplace and CLI paths follow the [official packaging guide](https://developers.openai.com/plugins/build/plugins); generated protocol schemas came from this installed CLI, not an inferred method name.

## Key diff summary

| File | Local change versus older PR material |
|---|---|
| plugin.json | Local packaging version 1.2.1 → 1.3.1; listing now states attributed third-party TCX screen references are bundled and are not an official Pantone-licensed database. |
| docs/SUBMISSION.md | Public standalone release v1.2.0 → v1.3.0; local packaging version and archive filename updated; local validation/report links added. |
| SUPPORT.md | Replaced obsolete “No Pantone database is bundled” with actual TCX/Solid data, upstream notices, override/failure behavior and physical-review boundary. |
| docs/SUBMISSION_TESTS.md | Corrected P5/N1 colour-data assumptions; recorded all eight actual Mac agent Pass results with linked sanitized case summaries, separately from installation/program/visual checks. |
| README.md | Added PR submission/privacy/support/test entry points while preserving current main's v1.3.0 download and onboarding. |
| PRIVACY.md | Older PR notice brought forward unchanged. |
| docs/LOCAL_VALIDATION-2026-10-08.md and this matrix | New local evidence, resolved setup attempts, exact limitations and minimal next decision. |
| skills/ implementation and bundled colour data | No code/data edits; current main retained. |

Working-tree patches and key-file diffs were saved only in the private local evidence workspace. The validation phase performed no Git commit/push/merge, submission or release; subsequent user-authorized PR updates are separate.
