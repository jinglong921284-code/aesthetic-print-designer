# Privacy and data handling

Last updated: 2026-09-23

This notice covers the Aesthetic Print Designer skills-only package maintained by Lialynn in [this repository](https://github.com/jinglong921284-code/aesthetic-print-designer). It describes the distributed instructions and scripts. It does not replace the policies of the agent host, model provider, GitHub, or optional services you choose to use.

## Data used during a workflow

Depending on your request, the workflow can read references, artwork, prompts, design briefs, colour-role definitions, authorized colour-library files, and technical specifications that you supply or make accessible to the host. Outputs can include image derivatives, colour tables, PDFs, validation reports, and local workflow records. Records may contain file paths, checksums, Print IDs, versions, timestamps, and, if supplied for a handoff, recipient or document identifiers.

The package does not include a publisher-operated backend, account system, analytics SDK, or telemetry endpoint. Its local image, colour, and PDF tools do not send inputs or outputs to the maintainer. Installing this package does not itself give the maintainer access to your conversations, artwork, or local files.

## Host processing and optional services

The host agent and its model or image tools may process your prompts, attachments, and tool results under that provider's terms and your account settings. “Local tool” does not mean the entire agent conversation stays on your device. Dependencies downloaded during setup are obtained through the package manager you use.

Optional image-generation, Lovart, Feishu/Lark, browser, document, or transfer tools have their own data handling and authentication. They are not supplied as MCP servers by this package. In particular, the optional Feishu readback script can invoke an installed, authenticated `lark-cli` to fetch a specified document and save audit results. External reads use the configured service; writes, uploads, messages, supplier contact, and transfers require a confirmed target and authorization under the workflow instructions. Local specification work does not require a Feishu account.

Do not supply credentials in prompts, artwork, or support issues. Configure optional services through the host or the service's authentication mechanism. Only provide artwork and colour-library data you are authorized to use.

## Storage, retention, and deletion

Local outputs remain in the selected workspace or output directory. Explicitly requested tracked closure also writes `.print-closure/` records in its project. The package has no automatic retention or deletion schedule for these files. You can remove the files and records you no longer need using your normal file-management tools; backups and synchronized copies are governed by their storage services.

Host conversations, attachments, optional-service documents, and service logs are retained according to the relevant provider and account settings. Deleting a local output does not delete those other copies. Use each service's controls or support process for access or deletion requests concerning data it holds.

## Support information

If you open a GitHub issue, the maintainer receives the information you choose to post. Issues in this public repository are visible to others. Use sanitized examples and remove client artwork, personal information, credentials, proprietary palettes, and confidential commercial details. Support information is used to understand and respond to the request; issue history is retained on GitHub unless edited or removed through GitHub's available controls. The package does not automatically publish workflow data as support information.

For questions about this notice or maintainer-controlled support content, use the route in [SUPPORT.md](SUPPORT.md). Start with a non-sensitive request if a private follow-up is needed; no private contact address is currently published here. The maintainer cannot delete records held independently by your agent host, GitHub, or another service.

## Changes

Updates to this notice are recorded in repository history. Recheck it when updating the package or enabling an optional integration.
