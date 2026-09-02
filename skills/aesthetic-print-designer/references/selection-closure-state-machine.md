# Explicit-Selection Closure State Machine

Use this procedure for a selected **repeat architecture** only after the user authorizes tracked local closure in an approved project directory. Read `references/selection-closure-routing.md` first. The program stores state under `<project-dir>/.print-closure/<Print-ID>/closure-state.json` and refuses to skip gates. Placement, border, engineered, and panel designs use their architecture-specific evidence route instead.

## State order

Local mode, which is the default:

`source_lock → garment_mockup → colour_spec → initial_repeat_validation → repeat_repair when required → final_repeat_validation → closure_audit → closed`

Explicit Feishu mode adds `feishu_sync` before `closure_audit`.

`还可以`, `不错`, and `方向可以` are candidate signals. `选中`, `保留`, `确认`, and `这张定了` approve a creative direction, but initialization also requires authorization for local closure files. They never authorize an external document write or message by themselves.

## Init preflight

Before `init`, resolve all four required identifiers:

1. **Project directory:** use the existing, user-approved project directory already in scope. Do not create a guessed project path because of a typo or ambiguous conversation context.
2. **Print ID:** reuse the approved project/series Print ID. If none exists, ask once for the ID or naming rule; do not invent a production identifier.
3. **Design name:** reuse the approved name attached to the selected direction. If it is unnamed, ask for the name in the same bundled question as the missing Print ID.
4. **Exact source file:** use the original selected file or the exact attachment bytes. If only a rendered conversation preview or screenshot is accessible, request the original instead of re-encoding it and treating that derivative as the source.

Record the user's exact explicit selection phrase and local-closure authorization. If several required fields are absent, ask one concise bundled question. Category, garment template, and fabric may remain unset at init because the state machine exposes truthful resolution stages for them; the four identifiers above may not. Choose Feishu mode only when the exact document and update are authorized.

## Commands

Start closure and lock the source without overwriting it:

```bash
python3 scripts/run_print_tool.py closure init \
  --project-dir <project> --print-id <ID> --name <name> \
  --source <selected-file> --approval-phrase <exact-user-phrase> \
  --category <category> --garment-template <template> \
  --document-mode local
```

For an explicitly authorized Feishu target, use `--document-mode feishu --feishu-doc <doc-url>`. If category, template, fabric, or a Feishu-mode document was unavailable at initialization, fill it later:

```bash
python3 scripts/run_print_tool.py closure set-context \
  --project-dir <project> --print-id <ID> \
  --category <category> --garment-template <template> \
  --fabric <confirmed-fabric> --feishu-doc <authorized-doc-url>
```

Record evidence only when the reported stage is the next action:

```bash
python3 scripts/run_print_tool.py closure record-file \
  --project-dir <project> --print-id <ID> \
  --stage garment_mockup --file <mockup>

python3 scripts/run_print_tool.py closure record-file \
  --project-dir <project> --print-id <ID> \
  --stage colour_spec --file <annotation> --file <colour-table> \
  --colour-report <colour-role-spec.json>
```

Build the colour evidence from explicitly locked roles, never from unconstrained clustering:

```bash
python3 scripts/run_print_tool.py colour-spec \
  --image <locked-selected-source> --roles <role-definition.json> \
  --pantone-csv <authorized-pantone-tcx.csv> --out-dir <colour-spec-dir> \
  --fabric <confirmed-fabric>
```

Omit `--fabric` when it is not confirmed; the report records it as pending. Copy `assets/colour-role-template.json` and fill every required element and sample or HEX before use. Keep small-area accents when the design relationship requires them. The program retains every locked role, creates the numbered annotation, calculates CIEDE2000 against the named user-provided library, and keeps physical colour and actual-fabric review pending.

Run the existing repeat validator, then record its JSON report:

```bash
python3 scripts/run_repeat_tool.py validate <tile> --out-dir <validation-dir>
python3 scripts/run_print_tool.py closure record-validation \
  --project-dir <project> --print-id <ID> --report <validation.json>
```

If the report does not equal `digital_seamless_repeat_passed`, the next action becomes `repeat_repair`. Record the bounded repair, rerun validation, and record the new report:

```bash
python3 scripts/run_print_tool.py seam-guard prepare \
  --tile <failed-tile> --out-dir <guard-dir>

# Edit only the generated white central cross, then protect the result:
python3 scripts/run_print_tool.py seam-guard apply \
  --manifest <seam-guard-manifest.json> --edited <edited-half-offset> \
  --output <guarded-half-offset>

python3 scripts/run_print_tool.py closure record-file \
  --project-dir <project> --print-id <ID> \
  --stage repeat_repair --file <guarded-half-offset> \
  --guard-report <seam-guard-report.json>
```

In Feishu mode only, after the separately authorized targeted edit, let the state machine fetch the affected Print ID section as the user. It records the sync only when the live readback contains the Print ID, `digital_seamless_repeat_passed`, and the final tile SHA-256:

```bash
python3 scripts/run_print_tool.py closure record-feishu \
  --project-dir <project> --print-id <ID> --doc-url <doc-url>
```

Use `--readback-file <lark-fetch-output.json>` only for an offline replay or test.

Close only after the checksum audit passes:

```bash
python3 scripts/run_print_tool.py closure audit \
  --project-dir <project> --print-id <ID>
```

In local mode, the final audit verifies local evidence and checksums and ends with `local_design_closure_completed`; external synchronization remains outside that closure. In Feishu mode, it additionally runs `document_consistency_audit.py` against the stored full Print-ID section and ends with `feishu_design_closure_completed`. It blocks on stale failure terms, missing final status/SHA, fewer than three Print-ID images, a missing colour annotation, a missing/duplicated/reordered mapping row, a row whose element/HEX/TCX/name does not match the same locked role, nonsequential colour roles, or a partial `<excerpt>` readback. Global value presence is not sufficient.

At any point, inspect the truthful state and next action:

```bash
python3 scripts/run_print_tool.py closure status \
  --project-dir <project> --print-id <ID>
```

## Gate behavior

- Preserve the selected source in `source_locked` and reject a different source under the same Print ID.
- Store SHA-256 for every evidence file and fail the final audit when a file is missing or changed.
- Require a role-locked colour report matching the selected-source checksum. Reject dropped roles, missing Pantone candidates, nonsequential callouts, or a falsely completed physical review.
- Reuse an initial validation as the final validation only when edge lock and visual review both pass.
- Require a repair stage after either data failure or visual revise.
- Require the seam guard report for every repair; protected pixels outside the central cross must remain an exact 100% match.
- In Feishu mode, require a successful user-identity readback. A write response alone is not evidence of synchronization.
- In Feishu mode, fetch the heading outline first, then the complete Print-ID section; reject partial keyword excerpts and require `document_consistency_passed`.
- In local mode, mark Feishu sync `not_required` and do not invoke `lark-cli`.
- Mark the final state `local_design_closure_completed` or `feishu_design_closure_completed`; never convert either into sampling or production approval.
