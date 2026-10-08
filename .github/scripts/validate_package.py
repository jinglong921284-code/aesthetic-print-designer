#!/usr/bin/env python3
"""Build the documented ZIP from HEAD and run every program test in its extraction."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[2]
ROOT_NAME = 'aesthetic-print-designer'
CONTENTS = ['plugin.json', 'README.md', 'LICENSE', 'NOTICE.md',
            'COMMERCIAL-LICENSING.md', 'PRIVACY.md', 'SUPPORT.md', 'docs', 'skills']


def main():
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PRINT_DESIGNER_PYTHON'] = sys.executable
    env.pop('PANTONE_TCX_DB', None)
    with tempfile.TemporaryDirectory(prefix='print-package-') as temporary:
        work = Path(temporary)
        archive = work / 'plugin.zip'
        subprocess.run(['git', 'archive', '--format=zip', f'--prefix={ROOT_NAME}/',
                        '-o', str(archive), 'HEAD', *CONTENTS], cwd=REPO, check=True)
        with zipfile.ZipFile(archive) as package:
            for name in package.namelist():
                path = Path(name)
                assert not path.is_absolute() and '..' not in path.parts, name
                assert path.parts[0] == ROOT_NAME, name
                assert not {'.git', '.env', '__pycache__'}.intersection(path.parts), name
                assert path.suffix not in {'.pyc', '.pyo', '.jsonl'}, name
            package.extractall(work)
        root = work / ROOT_NAME
        for name in CONTENTS:
            assert (root / name).exists(), name
        manifest = json.loads((root / 'plugin.json').read_text())
        assert manifest['version'], 'missing plugin version'
        scripts = root / 'skills' / ROOT_NAME / 'scripts'
        tests = sorted(scripts.glob('test_*.py'))
        assert len(tests) >= 10, 'expected existing program regression entrypoints'
        for test in tests:
            print(f'RUN {test.name}', flush=True)
            subprocess.run([sys.executable, str(test)], cwd=work, env=env, check=True)
        print(f'PASS: package {manifest["version"]}; {len(tests)} program test entrypoints')


if __name__ == '__main__':
    main()
