# Changelog

## v1.2.0 - 2026-09-21

- Added **Print Specification Sheet / 印花规格单** as an explicit output mode with direct trigger phrases and a standalone one-pass selected-print workflow.
- Added a reusable, standardized print-specification template covering source control, Print ID, type, size, repeat or placement, colour count and candidates, fabric, process, resolution, colour mode, version, status, technical notes, and open items.
- Separated design-stage specification work from the second-stage Production Handoff route so a request for a sheet does not start supplier, sampling, transfer, or approval work.
- Updated the public README and skill UI prompt to make the print-specification capability discoverable.
- Refined the README positioning to an end-to-end fashion textile print workflow with production-oriented print specification sheets.
- Added `Ready for Sampling` as the design-stage completion status after current-version design, merchandising, and pattern-room confirmation, while retaining separate physical-review and production-approval statuses.
- Added colour-focused and full-technical scopes within Print Specification Sheet mode, independently of Markdown, DOCX, and PDF presentation formats.
- Added a portable English two-page visual PDF preset, structured input template, optional renderer dependencies, and validation tests.
- Preserved existing-specification values when translating or reformatting, kept representative colours separate from production separations, and made artwork-use notices explicit and configurable.
- The installable skill ZIP contains only reusable templates, instructions, code, and fictional test fixtures; no client artwork, specification, or sample output is included in that ZIP. The separately published reference-only visual sample is not part of the installable package.

## v1.1.0 - 2026-09-02

- Changed new releases from MIT to the Polyform Noncommercial License 1.0.0.
- Added a public GitHub Issues route for commercial-use licenses, exclusive licensing, and rights-buyout enquiries.
- Preserved the original MIT terms for the already-published v1.0.0 and v1.0.1 tags.
- Added packaging checks so standalone release ZIPs include the license, notices, and commercial-licensing terms.
- Made no functional changes to design, repeat validation, colour specification, closure, or handoff behavior.

## v1.0.1 - 2026-09-02

- Included the MIT `LICENSE` and `NOTICE.md` inside the standalone skill folder so release ZIPs retain their legal notices when downloaded independently.
- Kept all creative, validation, colour-specification, closure, and handoff behavior unchanged from v1.0.0.

## v1.0.0 - 2026-09-02

- Removed personal aesthetic defaults, real-project examples, private paths, and the fixed 19mm silk assumption.
- Added a host-neutral Python selector, dependency manifest, and clean runtime guidance.
- Removed automatic Pantone database fallback; users must provide authorized JSON or CSV data.
- Replaced all colour-library test records with clearly fictional `TEST-*` codes and `Fixture *` names.
- Added strict colour-library validation and safe unfilled colour-role placeholders.
- Made local document mode the default closure path; Feishu/Lark is an explicit optional adapter.
- Preserved Feishu numbered-artwork-to-five-column row/cell consistency auditing.
- Separated creative selection from local persistence, cloud writes, uploads, email, supplier contact, and file transfer authorization.
- Routed placement, border, engineered, and panel selections away from repeat-only repair gates.
- Generalized production handoff to a versioned local package plus an authorized transfer manifest.
- Marked annotation styling and quality thresholds as configurable workflow defaults rather than industry standards.
- Added public-package privacy checks and cross-environment regression coverage.
