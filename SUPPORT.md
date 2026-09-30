# Support

Maintainer: **Lialynn** — [jinglong921284-code](https://github.com/jinglong921284-code).

For bugs, installation problems, workflow questions, or suggestions, [open a GitHub issue](https://github.com/jinglong921284-code/aesthetic-print-designer/issues/new). Search [existing issues](https://github.com/jinglong921284-code/aesthetic-print-designer/issues) first. GitHub requires an account to post. Support is provided on a best-effort basis; there is no guaranteed response time or service-level agreement.

## A useful bug report

Include:

- The plugin version and repository commit, if known.
- Agent host and operating system; Python version and relevant dependency versions for local-tool failures.
- The requested workflow, exact steps, expected result, and actual result.
- A short error message and minimal synthetic or sanitized input sufficient to reproduce it.
- Whether the problem involves local work or an optional integration.

Public issues must not contain API keys, access tokens, client artwork, personal information, proprietary colour libraries, confidential specifications, or unredacted local paths. Screenshots and logs can expose these too. For a sensitive report, post only a non-sensitive request for a private contact route and wait for the maintainer to arrange one; no private reporting address is currently published.

## Common setup checks

- Install the single skill folder for the standalone skill workflow, or use the whole plugin package described in the [submission guide](docs/SUBMISSION.md). The existing v1.2.0 skill ZIP is not the new plugin bundle.
- Local image tools require Python 3.10+ with the skill's `requirements.txt`; the PDF preset also requires `requirements-visual.txt`. Follow [Local runtime](README.md#local-runtime).
- Image generation needs a separate available image tool. Without one, the workflow can return prompts and export requirements.
- No Pantone database is bundled. Without authorized colour data, retain source HEX values and leave named-colour matching pending.
- Optional Feishu/Lark work needs the user's configured tools, credentials, permissions, and target. Core local work remains available without it.

Reports and previews support design decisions. They do not certify intellectual-property clearance, physical colour, fabric performance, supplier receipt, or production approval.

## Licensing and privacy

For commercial-use, exclusive-license, or rights-buyout enquiries, use the existing [commercial licensing process](COMMERCIAL-LICENSING.md). The [LICENSE](LICENSE) remains unchanged; installing a plugin does not grant additional commercial or artwork rights.

For data-handling questions, see [PRIVACY.md](PRIVACY.md) and use the issue route above with a non-sensitive description.
