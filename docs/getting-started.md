# Getting started: install the skill and run your first colour match

For **v1.3.0**, primarily with Codex running on your computer. Other clients require their own supported skill installation workflow. Allow about ten minutes for the exercise once your environment is ready; installing Python or downloading dependencies may take longer.

[Download Skill ZIP](https://github.com/jinglong921284-code/aesthetic-print-designer/releases/download/v1.3.0/aesthetic-print-designer-v1.3.0-2026-09-28.zip) · [Worked example](first-run-example.md) · [Back to README](../README.md)

## 1. Download and check the folder

Download and extract the ZIP. The extracted folder should contain:

```text
aesthetic-print-designer/
├── SKILL.md
├── agents/
├── assets/
│   └── colour-libraries/
├── references/
├── scripts/
├── requirements.txt
└── requirements-visual.txt
```

Keep the complete folder, including its license files. Copying only `SKILL.md` leaves out required resources. The whole GitHub repository is not the installable skill folder. Public downloads do not require GitHub sign-in; if you reach a login page, use the download link above.

## 2. Install in Codex

After downloading, send this request to your local Codex chat and provide the actual path to the extracted folder:

```text
Install the complete aesthetic-print-designer folder at the path I provide
as a personal skill for this local Codex environment.
First check for an existing skill with the same name. If one exists, report
its location and differences before replacing it.
Use the currently supported user-level skills directory. Preserve all assets,
references, scripts and license files.
After installation, check that SKILL.md and
assets/colour-libraries/pantone-tcx-rgb.json exist.
Only install and verify the files; do not start a design or colour task yet.
```

For manual installation, the current official user-level directory is `~/.agents/skills/`. The resulting layout should be:

```text
~/.agents/skills/aesthetic-print-designer/SKILL.md
```

- **macOS:** In Finder, press `Command-Shift-G` and enter `~/.agents/skills/`. If the directory does not exist, ask Codex to create it using the request above, or run `mkdir -p ~/.agents/skills` in Terminal. Copy the complete extracted skill folder into it.
- **Native Windows:** Enter `%USERPROFILE%` in the File Explorer address bar. Create or open `.agents`, then `skills`, and copy the complete skill folder there.
- **WSL or remote execution:** Install in the home directory of the environment where Codex actually runs. The Windows host directory is not automatically the WSL or remote directory.
- If a folder with the same name exists, back it up and confirm the version before replacing it. Do not merge two versions. Check for same-name skills in other locations to avoid selecting the wrong copy.

Codex detects skill changes automatically. If the skill does not appear, restart Codex and open a new chat. Directory and refresh guidance was checked against the [official OpenAI Skills documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) on 2026-09-29. These are local folder installation instructions; they do not imply that this skill is listed in the plugin directory.

## 3. Verify that Codex can read the skill

Send this in a new chat:

```text
Use aesthetic-print-designer.
Read the installed SKILL.md, report its actual file location and supported tasks,
and check that the bundled TCX JSON and CSV files exist.
Only inspect the installation; do not generate images or files yet.
```

**Success looks like:** an actual file location, confirmation that both TCX files exist, and a description of reference analysis, print directions, repeat checks, colour matching and specification sheets. A generic offer to help with design does not verify installation.

## 4. Prepare the tool environment

You can start reference analysis before setting up local tools. This colour exercise requires Python 3.10+, NumPy and Pillow. Send this request to Codex:

```text
Check the runtime for aesthetic-print-designer's colour tools.
Use an existing compatible environment if available. Otherwise, create .venv
inside the skill folder, install requirements.txt, and use that environment's
Python for subsequent tool commands.
Do not change global Python or install optional PDF dependencies.
If Python 3.10+ is missing or system permissions are required, explain what is needed.
```

To set up manually, open a terminal in the installed `aesthetic-print-designer` folder. Check the Python version before continuing.

**macOS / Linux** — `python3 --version` must report 3.10 or newer:

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/run_print_tool.py pantone-quick --hex '#F3ECE0' --top 1
```

**Windows PowerShell** — `py -3 --version` must report 3.10 or newer:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_print_tool.py pantone-quick --hex '#F3ECE0' --top 1
```

If the version is older, prepare a compatible Python installation first. These commands call the environment's Python directly, so no activation script is needed. For PDF export later, follow the [optional dependency instructions](../README.md#local-runtime).

## 5. First exercise: match three colours

Copy this into a Codex chat that has identified the skill:

```text
Use aesthetic-print-designer's pantone-quick tool to run a real match against
the bundled TCX library.
Ground: #F3ECE0; main motif: #3F6F9F; accent: #DF7327.
Return the nearest candidate for each colour, including source HEX, TCX code,
colour name and computed Delta E 2000. State the library and matching method.
Show the result in chat only. Keep the status as a screen-computed candidate
with physical review pending.
If execution fails, report the error rather than inventing codes or colour differences.
```

With the default v1.3.0 library, expect:

| Role | Input HEX | TCX candidate | Name | Delta E 2000 |
|---|---|---|---|---|
| Ground | `#F3ECE0` | `11-0103` | Egret | 0.0000 |
| Main motif | `#3F6F9F` | `18-4141` | Campanula | 2.4062 |
| Accent | `#DF7327` | `16-1255` | Russet Orange | 1.4313 |

These are [actual tool results](examples/first-colour-match.json), not a physical colour guarantee. A zero digital difference means the RGB values agree with this dataset. Another library may return different candidates.

**Completion criteria:** the skill was read, the tool ran, three candidates were returned, the library and method were identified, and physical review remains pending.

## 6. Continue with your own design task

Attach a reference image you have permission to use, then send:

```text
Use aesthetic-print-designer to analyse the attached reference.
Product: [your product]; theme: [your theme]; intended use: [your use case].
Analyse the motifs, composition, mark-making and palette relationships.
Propose three distinct original print directions. Explain which principles
can be reinterpreted and which identifying elements should be avoided.
Do not generate images yet; wait for me to choose a direction.
```

This is a next-step prompt, not a completed image-generation case study. Image generation requires a suitable tool in your client; without it, the skill can provide directions and prompts. Existing artwork can go straight to the [specification-sheet example](../README.md#3-generate-an-english-print-specification-sheet). The artwork displayed in the README is reference-only and is not practice material.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Skill not found | Ensure the path ends directly in `aesthetic-print-designer/SKILL.md`, without an extra nested folder. Restart and check for duplicate versions. |
| TCX files missing | Confirm you downloaded the complete v1.3.0 ZIP and copied all supporting files. |
| NumPy or Pillow missing | Install requirements.txt with the same Python interpreter that runs the tool. |
| Results differ from the table | Check the loaded skill path and library SHA-256. Look for a `PANTONE_TCX_DB` or explicit library override. |
| Images cannot be generated | Check the client's image-generation tools. Reference analysis and the colour exercise can be completed separately. |
| ReportLab missing | This is needed for PDF export only. Install requirements-visual.txt in the same environment. |
| Managed computer blocks installation or downloads | Record the restriction and contact your administrator. A permission failure is not a successful skill run. |

## First-user trial record

Have a first-time user complete this. Keep maintainer tests separate from independent user trials.

```text
Date:
Operating system and Codex version:
Skill version and actual installation location:
Installation time / first-task time:
Was the skill detected?
Were Python and dependencies ready?
Were all three candidates returned?
Blocked step, original error and resolution:
Least clear instruction:
Was another person's help needed?
Final outcome: completed / not completed
```

Current evidence: the maintainer ran the colour command. First-time installation on another computer, Windows execution and an independent designer trial remain unverified. Ten minutes is an exercise target, not a measured installation-time promise. Share feedback through [GitHub Issues](https://github.com/jinglong921284-code/aesthetic-print-designer/issues), removing personal paths, client artwork and account details first.
