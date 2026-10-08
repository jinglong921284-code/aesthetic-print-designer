# Local alignment and verification — 2026-10-08

## Scope and source

Local-only validation on the user's Mac, macOS 27.0.1 arm64, Python 3.11.15; at test time, no push, commit, merge, review submission or release had been performed. No browser was used. GitHub connector, Git and public web documentation were read.

- Latest fetched main: `a67a8b55efcb40433488c9ce1f72e5a34580569b`.
- PR #1 head: `347936910b3dd80e2fd0c298a3472e661dbfd0a7`; open, draft, not merged at check time.
- Public v1.3.0 tag: `4bab1ae5bbe7a1601db739e8d9e6249d5d7e22b0`.
- Local branch: `local/pr-1-alignment`, based on current main with PR metadata/docs brought forward. This preserves current colour tools, bundled data, and onboarding rather than reverting to the older PR tree.
- New packaging version 1.3.1 is local metadata only. It is not a published release.

Repository has no AGENTS.md or .agents/skills instructions. Checked local .agents and .codex skill locations and relevant memory background; current repository files govern. An existing personal .codex skill differs from the public version and was left untouched. No user files or existing installation were overwritten.

## Passed checks

| Check | Result / evidence |
|---|---|
| Actual published ZIP download/extraction | Pass: one top-level aesthetic-print-designer folder; full skill copied into an isolated `.agents/skills` layout under the validation workspace, not the real user skill directory. |
| Installation file checks | Pass: SKILL.md, TCX JSON/CSV and supporting resources retained. Initial check covered copying/readability; subsequent isolated Codex CLI installation and skills/list discovery passed (see follow-up matrix). |
| Fresh Python environment | Pass: existing Python 3.11.15 used to create a new venv; NumPy 2.4.6, Pillow 12.3.0, ReportLab 4.5.1 and test-only pypdf 6.19.0 installed. |
| First colour command from extracted/copied release | Pass: 2,800-entry bundled TCX data, SHA-256 `5e5ac131379a2a934e4291de2f11393e9c7ebcb490b079677ca427292423b7a5`; Egret 11-0103 / 0.0000, Campanula 18-4141 / 2.4062, Russet Orange 16-1255 / 1.4313. Status screen_computed_candidate; physical review pending. |
| Release ZIP regressions | Pass: all 10 test_*.py entry points exit 0. |
| Extracted local plugin regressions | Pass: all 10 test_*.py entry points exit 0. |
| P2 program smoke | Pass: matching edges 100%, offset and 3×3 output. Maintainer viewed both: intact circles, no pixel-edge seam, deliberately regular repeated islands/grid rhythm. Initial report was pending_visual_review. Follow-up installed-package inspection recorded visual_revise for the conspicuous synthetic grid/island rhythm; expected exit code 4. No design/production pass recorded. |
| P3 program smoke | Pass: all three roles preserved in order; fictional TEST-0001/2/3 returned at ΔE00=0. Annotation viewed, IDs 1–3 retained. These codes are fictional, not Pantone. Legacy Pantone-labelled fields require this explanation; physical review pending. |
| P4 program smoke | Pass: PDF created; pypdf assertions below verify two pages and preserved rows/status/notice. Follow-up native CoreGraphics rendering and inspection of both installed-package PDF pages passed: no visible clipping, sequential IDs, three source HEX rows, Draft, pending fields and notice retained. |
| Fixture preservation | Pass: SHA-256 before/after identical for every input. |
| Manifest/listing | Pass: JSON parses, identity agrees, explicit final-submission length/category/URL checks; no app or screenshots configured. Full portable JSON Schema validation was not rerun. |
| Local document links and whitespace | Checked after final edits; see local check log. |

## Failures, restrictions and not-run items

- Initial Git clone failed due to an unavailable configured localhost proxy; retry without proxy required network escalation and succeeded. Initial pip dependency install failed under sandbox/proxy settings; approved isolated-environment network retry succeeded. These are resolved setup attempts, not failing regressions. System Python 3.9.6 is below the documented 3.10 minimum; no global Python change was made.
- Bundled dependency-loader tool was unavailable for this delegated execution. The existing public Python 3.11 executable was used explicitly instead; no host-specific path was added to the distributed skill.
- Follow-up after user-controlled isolated login: P1–P5 and N1–N3 executed in eight fresh CLI conversations, all **Pass** for the specified agent behavior. See [exact matrix and evidence](LOCAL_TEST_MATRIX-2026-10-08.md). No credentials were copied; no API key or purchased quota was used. Program results were not substituted for these actual agent runs.
- Initial PDF visual inspection restriction was resolved: the existing macOS Swift/CoreGraphics/ImageIO frameworks rendered both pages locally. Both pages were viewed; no extra rendering software or cloud service was installed.
- Windows, WSL, remote host and independent first-user/designer trial: **Not run**. No measured ten-minute installation claim, physical colour certification or fabric/production approval.
- Directory scan, plugin-creator validator, logo/identity/portal checks and signed-out live main privacy/support links: **Not run**. The latter documents are local and cannot be claimed live before merge.

## Evidence and reproduction

The adjacent local `evidence/` directory (outside this repository) contains actual release ZIP, isolated copied installation, extracted local plugin, individual command logs, `results.json`, `fixture-hashes.json`, `manifest-checks.json`, synthetic outputs and final ZIP/hash inventory. These machine logs include local paths and should be sanitized before public posting. `verify.py` in the parent workspace records exact commands; do not rerun in the same fixture directory without choosing a new evidence destination.

Follow-up used bundled `codex-cli 0.162.0-alpha.2` without global configuration changes. CLI state, local marketplace and cache are inside `evidence/`. The initial discovery phase initiated no model turn or login. Subsequently the user personally authorized official login and eight fresh conversations ran using existing ChatGPT/Codex entitlement; no external write, API key or separately billed API call was used. First skill enumeration exposed metadata from the user-level `.agents/skills` catalog; 30 outside skill entries were subsequently disabled in isolated configuration and discovery rerun. Only the tested print plugin and generated built-in system skills remained enabled. This is a controlled maintainer installation, not an independent-user trial.

Official packaging and listing references were rechecked via web retrieval on 2026-10-08: [portable package guide](https://developers.openai.com/plugins/build/plugins) and [submission error reference](https://developers.openai.com/plugins/deploy/submission-errors). The older documentation-check date in the submission guide remains historical; this check does not assert portal acceptance.

## Authenticated agent results

All eight specified scenarios were run using default model gpt-6.1-sol in eight unique fresh CLI threads on 2026-10-08 (Asia/Shanghai). Each used workspace-write sandbox, distinct fixtures/output directory, no shared daemon and ephemeral session storage. The test prompts and sanitized result summaries are under [validation/2026-10-08/results.json](validation/2026-10-08/results.json). All input SHA-256 values remained unchanged. P1, N2 and N3 created no files. P2 accurately recorded artwork visual_revise (expected tool exit 4), not production approval. P3 retained all fictional roles/codes and relabelled output fields. P4 actually viewed both rendered PDF pages. P5 remained a Draft with unknown production fields. N1 refused unsupported physical certification/approval and saved a bounded colour-evidence report.

Independent maintainer artifact checks confirmed PDF page count/key text, P3 1–3/code/HEX order, P5 exact-byte source copy and P2's separate edge/visual status. These are controlled Mac agent checks, not Windows or independent first-user results. No global configuration was modified; the fresh official login cache stays only in isolated local state and is excluded from every deliverable archive.

One initial runner invocation omitted the CLI argument separator after --image and exited before creating a model thread. It was corrected; eight actual thread.started/turn.completed streams were then recorded. This setup attempt is not a ninth agent case or product failure.
