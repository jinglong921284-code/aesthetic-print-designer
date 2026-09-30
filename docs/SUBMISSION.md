# OpenAI skills-only plugin submission

Prepared against the official documentation checked on **2026-09-23**:

- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Submit plugins](https://developers.openai.com/plugins/deploy/submission)
- [Submission errors and final listing limits](https://developers.openai.com/plugins/deploy/submission-errors)
- [Agent Plugins 1.0.0 manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), referenced by the OpenAI packaging guide

This is submission preparation, not evidence of directory acceptance or publication.

## Package and listing

The canonical entry point is root [`plugin.json`](../plugin.json), using the portable Agent Plugins schema. OpenAI listing fields live under `extensions.com.openai.interface`. The host discovers `skills/aesthetic-print-designer/` from the root `skills/` directory. No redundant compatibility manifest, MCP configuration, app connection, or hook is required for this package.

Manifest version **1.2.1** identifies this new packaging revision; it does not assert that a v1.2.1 GitHub release or directory listing already exists. The existing public skill release remains v1.2.0 until a new release is deliberately published.

The manifest contains the display name, concise subtitle, long description, Creativity category, three capabilities, and three starter prompts. It uses **Lialynn**, the name in the existing copyright notice. The publisher must verify that this matches the identity selected in the submission portal; if it differs, update both `author.name` and `developerName` together and align the public notices before submission.

After this change is merged, use these public pages in the portal:

| Field | URL |
|---|---|
| Website | https://github.com/jinglong921284-code/aesthetic-print-designer |
| Privacy | https://github.com/jinglong921284-code/aesthetic-print-designer/blob/main/PRIVACY.md |
| Support | https://github.com/jinglong921284-code/aesthetic-print-designer/blob/main/SUPPORT.md |

These `main` links will not expose new documents until merge. Reopen them while signed out before submission. No `termsOfServiceURL` is invented: current software-use terms remain [LICENSE](../LICENSE) and [COMMERCIAL-LICENSING.md](../COMMERCIAL-LICENSING.md). The publisher should decide whether separate public plugin terms are needed. The error reference currently treats listing URLs as optional for skills-only ZIP uploads, while the general submission guide asks publishers to prepare them; resolve any portal-specific requirement before submitting.

No logo, icon, or screenshot is declared. There was no reusable brand icon in the checked source tree. The publisher still needs a suitable logo for the listing. Reference-only release artwork must not be repurposed as a logo. Skills-only uploads must not declare interface screenshots.

## Build the review ZIP

From a clean checkout of the commit being submitted, run:

```bash
git archive --format=zip --prefix=aesthetic-print-designer/ \
  -o ../aesthetic-print-designer-1.2.1-plugin.zip HEAD \
  plugin.json README.md LICENSE NOTICE.md COMMERCIAL-LICENSING.md \
  PRIVACY.md SUPPORT.md docs skills
```

This creates one top-level plugin directory with its root manifest, skill, referenced scripts/templates, and notices. It excludes `.git`, local environments, generated artwork, client files, and the reference-only release sample. Use the committed tree; uncommitted changes are not included. The old standalone skill ZIP has a different layout and cannot substitute for this archive.

## Review and test

Use [SUBMISSION_TESTS.md](SUBMISSION_TESTS.md) for five positive and three negative cases, reproducible fixtures, expected outputs, and a result log. Run them with the final ZIP installed in a clean supported host, without private skills or colour databases. A schema check or bundled Python regression does not establish that these agent-level scenarios passed.

The portable JSON schema checks portable fields, but deliberately leaves extension contents open. Check OpenAI interface values against the linked submission error reference as well. The local plugin-creator validator may support only `.codex-plugin/plugin.json` and older interface fields; its result alone is not authoritative for the portable manifest or final directory submission.

## Publisher checklist

- Confirm the publisher identity and notices; obtain the required Platform submission access and identity verification.
- Review the privacy/support statements, the noncommercial license, and any separate terms needed for the listing. Add a private support route only if one actually exists and the publisher chooses to publish it.
- Supply the missing logo and verify asset rights; do not use the restricted reference sample.
- Install and exercise the final package; complete the eight-case result log with real transcripts and artifacts, including visual inspection where required.
- In the [submission portal](https://platform.openai.com/plugins), choose **Skills only**, upload the ZIP, and review the imported listing, starter prompts, skill scan, and any normalized fields.
- Choose supported countries/regions, complete policy attestations and release notes, resolve scan issues, and submit for review. Publish only after approval and the publisher's release decision.

Suggested release note: “Adds a portable skills-only plugin manifest, privacy and support documentation, and reproducible submission test cases around the existing textile-print workflow. Core skill behavior and licensing remain unchanged.”
