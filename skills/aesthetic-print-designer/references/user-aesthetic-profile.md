# User Print Aesthetic Profile

Use this reference only when the user explicitly requests `印花审美画像`, `印花审美更新`, `print aesthetic profile`, or `update my print aesthetic profile`. An ordinary print brief, a supplied reference image, a visual-collection link, or a request to design a print does not activate this mode.

## Activation and persistence boundary

Treat analysis permission and write permission as separate decisions.

- `印花审美画像` starts a read-only analysis by default. Return the candidate profile in the conversation unless the user also asks to save it and identifies or approves the target.
- `印花审美更新` authorizes updating an existing, user-selected canonical profile after its current version and manifest are read. If the target is missing or ambiguous, stop before writing and ask for the target.
- Never create, replace, move, or append to a profile merely because images or a reference folder are available.
- Never modify, rename, delete, reorganize, or annotate source images, saved visual-collection baselines, or local collections.
- When persistence is authorized, copy `assets/user-aesthetic-profile-template.md` to the approved target and fill only evidence-supported fields. Do not overwrite the asset.

## Source and canonical layers

Keep source evidence separate from synthesis:

1. **Attachment source:** images or files supplied in the current conversation.
2. **Local collection source:** a user-selected directory such as a configurable `print research` folder.
3. **Saved visual-collection source:** a user-approved board baseline, export, or snapshot, including Pinterest when supplied. It is a source layer, not the final profile.
4. **Other approved source:** another path, board export, document, or snapshot explicitly placed in scope by the user.
5. **Canonical profile:** the versioned synthesis across in-scope sources. This is the only summary layer that may later be treated as the personal-aesthetic input to a print brief.

Do not silently promote a source layer into the canonical profile. Preserve source-specific conflicts and dates instead of smoothing them into one timeless preference.

## Configurable source registry

Resolve the source registry before analysis. For each source, record:

- stable `source_id` and source type;
- user-facing label;
- user-approved root path, attachment identity, or snapshot identity;
- whether the source is in scope for this run;
- whether it is read-only;
- snapshot or retrieval date when applicable;
- access or evidence limitations.

Do not embed personal absolute paths in the reusable template. In a persisted profile, store a configurable root label plus paths relative to that root. Keep the resolved absolute path only in the current execution context when it is needed to read local files.

## Evidence manifest

Build a deterministic manifest before interpreting the images. For every file or attachment, record:

- `source_id`;
- relative path under the declared source root, or a stable attachment/snapshot identifier;
- SHA-256 of the exact bytes;
- byte size;
- modification time when the source exposes one, otherwise `not_available`;
- media type;
- manifest status: `new`, `modified`, `deleted`, `unchanged`, or `current` on the first snapshot.

Sort entries by `source_id` and relative path before calculating the manifest-set SHA-256. Use SHA-256, not modification time, as the content-identity authority.

For an update, compare the current manifest with the last canonical manifest:

- new path with no previous entry -> `new`;
- same relative path with a different SHA-256 -> `modified`;
- previous relative path absent from the current manifest -> `deleted`;
- same relative path and SHA-256 -> `unchanged`;
- different relative path with the same SHA-256 and byte size -> note `probable rename/move`; do not infer deletion plus new taste evidence.

Deleted files remain in the append-only history and are excluded from the current synthesis unless the user explicitly preserves their earlier influence. A changed modification time with the same SHA-256 is not a content modification.

## Per-image or per-source analysis

Analyze each current or changed visual separately before synthesis. Keep these fields distinct:

1. **Observations:** directly visible colour relationships, motif grammar, composition, scale hierarchy, density, negative space, edge/mark character, texture, directionality, and material cues. Do not infer fibre, process, origin, brand, or production feasibility from appearance alone.
2. **Inferences:** bounded interpretations of mood, taste preference, likely use, or recurring aesthetic tension. Attach a confidence level and the supporting observation IDs.
3. **Keep:** transferable principles that may inform original work.
4. **Avoid:** generic, off-tone, overused, misleading, or copy-prone properties.
5. **Protected identifiers:** logos, characters, artist signatures, brand codes, distinctive layouts, recognizable artwork, or other elements that must not be reproduced.
6. **Evidence limitations:** crop, compression, unknown provenance, screenshot status, incomplete board coverage, duplicate/near-duplicate content, or other uncertainty.

Do not copy a recognizable composition or convert repeated exposure to one brand or artist into permission to reproduce its signature.

## Candidate synthesis

Synthesize only after the per-source evidence is complete enough for the requested scope. The candidate profile should contain:

- palette relationships rather than unsupported universal colour rules;
- motif and symbol preferences;
- composition, scale, density, and negative-space tendencies;
- mark, edge, texture, and material-character preferences;
- emotional tone and aesthetic tensions;
- stable anchors, variable preferences, rejection signals, and unresolved conflicts;
- source coverage and confidence for every major conclusion;
- protected or identifying elements excluded from downstream design.

The first synthesis is always `candidate`. It is not an `approved personal aesthetic profile`, may not override an explicit brief, and may not be silently used as a production benchmark.

## Confirmation and approval

Promote a candidate version to `approved` only after the user explicitly confirms that version or its named conclusions. Record the exact confirmation wording, date, approved scope, approver, and manifest-set SHA-256.

Partial confirmation approves only the named fields. Keep all other fields `candidate`, `disputed`, or `insufficient_evidence`. Ordinary feedback such as `还可以`, `不错`, or `差不多` does not approve the canonical profile.

## Versioning and updates

- Give every canonical summary an immutable `profile_version` and `summary_version`.
- A new synthesis supersedes rather than rewrites the prior current summary.
- Preserve the previous manifest-set SHA-256, current manifest-set SHA-256, added/modified/deleted counts, changed conclusions, retained conclusions, confidence changes, and user decision.
- Keep the change log append-only. Never edit or delete an earlier entry to make the history appear consistent.
- A newly updated summary returns to `candidate` unless the user explicitly approves that version. Unchanged conclusions may cite their prior approval, but new or materially changed conclusions cannot inherit approval automatically.

## Read-only and persisted outputs

For a read-only run, return:

1. source scope and manifest summary;
2. new/modified/deleted evidence;
3. per-image observations and inferences;
4. candidate canonical summary;
5. rights and confidence warnings;
6. the exact decision required for approval or persistence.

For an authorized persisted run, additionally record the canonical path, profile and summary versions, complete manifest, approval state, and append-only change-log entry. Read the saved file back and verify the version, status, manifest-set SHA-256, source counts, approval record, and newest change-log entry before reporting success.

## Privacy and publication boundary

Persist only the minimum personal paths, preference evidence, and confirmation wording needed for the approved profile purpose. Prefer configurable root labels, relative paths, stable IDs, and short decision evidence over unnecessary personal metadata. A filled profile is user data, not part of this reusable skill: never include it in a public package, example archive, test fixture, or release. De-identify any excerpt before sharing it outside the approved scope.
