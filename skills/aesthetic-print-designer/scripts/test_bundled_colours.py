#!/usr/bin/env python3
"""Check shipped reference consistency and portable default matching."""
from pathlib import Path
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'assets/colour-libraries'

def main():
    rgb = json.loads((LIB / 'pantone-tcx-rgb.json').read_text())
    full = json.loads((LIB / 'pantone-tcx-full.json').read_text())
    with (LIB / 'pantone-tcx.csv').open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rgb) == len(full) == len(rows) == 2800
    assert len({r['tcx'] for r in rgb}) == 2800
    for a, b, c in zip(rgb, full, rows):
        assert {k:a[k] for k in ('name','tcx','hex')} == b
        assert all(str(a[k]) == (c[k].strip("'\"") if k == 'name' else c[k]) for k in a), (a, c)
        assert [a[k] for k in ('r','g','b')] == [int(a['hex'][i:i+2],16) for i in (1,3,5)]
    auxiliary = json.loads((LIB / 'pantone-colours-com.json').read_text())
    assert len(auxiliary) == len({r['code'] for r in auxiliary}) == 907
    assert all(re.fullmatch(r'#[0-9a-fA-F]{6}', r['hex']) for r in auxiliary)
    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        env = os.environ.copy()
        env.pop('PANTONE_TCX_DB', None)
        env['PRINT_DESIGNER_PYTHON'] = sys.executable
        entry = ROOT / 'scripts/run_print_tool.py'
        quick = subprocess.run([sys.executable, str(entry), 'pantone-quick', '--hex', '#F3ECE0', '--top', '1'],cwd=temp,env=env,capture_output=True,text=True)
        assert quick.returncode == 0, quick.stdout + quick.stderr
        assert json.loads(quick.stdout)['data']['queries'][0]['matches'][0]['tcx'] == '11-0103'
        image = temp / 'fixture.png'
        Image.new('RGB', (64,64), (243,236,224)).save(image)
        roles = temp / 'roles.json'
        roles.write_text(json.dumps({'roles':[{'id':1,'role':'ground','element':'synthetic flat field','sample_points':[[32,32]]}]}))
        args = [sys.executable,str(entry),'colour-spec','--image',str(image),'--roles',str(roles),'--out-dir',str(temp/'out')]
        spec = subprocess.run(args,cwd=temp,env=env,capture_output=True,text=True)
        assert spec.returncode == 0, spec.stdout + spec.stderr
        report = json.loads(spec.stdout)['data']
        assert report['roles'][0]['pantone_tcx'] == '11-0103'
        assert report['pantone_library_sha256'] == hashlib.sha256((LIB/'pantone-tcx.csv').read_bytes()).hexdigest()
        assert report['physical_review']['status'] == 'pending'
        invalid = subprocess.run(args+['--pantone-csv',str(temp/'missing.csv')],cwd=temp,env=env,capture_output=True,text=True)
        assert invalid.returncode != 0
    print('bundled colour consistency and portable default tests passed')

if __name__ == '__main__':
    main()
