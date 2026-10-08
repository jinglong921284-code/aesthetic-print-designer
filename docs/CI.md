# Automated program checks

The **Package tests** GitHub Actions workflow runs on `push` and `pull_request`
with Ubuntu and Python 3.11. It builds the documented plugin ZIP from the checked-out
commit, extracts it into a temporary directory, checks the package layout and runs
all ten existing `test_*.py` entrypoints from that extraction. Any failed command
fails the job. Bundled-colour tests read the shipped TCX reference files, verify
consistency and matching, and keep physical review pending; these are third-party
digital references, not an officially licensed Pantone library or certification.

Local equivalent (Python 3.10+ with pip; run from the repository root):

```sh
python -m pip install -r skills/aesthetic-print-designer/requirements-visual.txt 'pypdf>=6,<7'
python .github/scripts/validate_package.py
```

The archive uses committed `HEAD` files. Commit intended package changes before
using this command to validate them. Dependencies follow the project's declared
ranges; pypdf is used only to inspect PDFs in regression tests.

The eight AI-session scenarios in [SUBMISSION_TESTS.md](SUBMISSION_TESTS.md) remain
manual. CI does not call a model, use personal account credentials or API keys,
perform image generation, exercise the desktop plugin UI, certify physical colour,
or demonstrate Windows installation or an independent user's first-use experience.

Only official checkout/setup-python Actions are used, pinned to verified full
commit SHAs. The automatic GitHub token has `contents: read` permission and checkout
does not persist credentials. No repository secrets, deployments or releases are
configured. See GitHub's [Python guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
and [secure use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
