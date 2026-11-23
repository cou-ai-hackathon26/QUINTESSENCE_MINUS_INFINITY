"""One final offline regression pass, captured against the actual working tree."""
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence/readiness/AJ-03'
OUT.mkdir(parents=True, exist_ok=True)
ENV = os.environ.copy()
ENV['PYTHONPATH'] = str(ROOT / 'apps/api')
ENV['PYTHONIOENCODING'] = 'utf-8'
ENV.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=ROOT.as_posix())
GIT = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]


def run(item):
    name, command = item
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (OUT / (name + '.log')).write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
    row = {'check': name, 'command': command, 'exit_code': result.returncode, 'seconds': round(time.monotonic()-started, 2)}
    print(json.dumps(row), flush=True)
    if result.returncode: print((result.stdout + result.stderr)[-4000:], flush=True)
    return row


if __name__ == '__main__':
    npm = ['cmd', '/c', 'pnpm.cmd'] if os.name == 'nt' else ['pnpm']
    head = subprocess.check_output(GIT + ['rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    diff = subprocess.check_output(GIT + ['diff', '--', '.', ':!docs/DATABASE_SETUP.md'], cwd=ROOT)
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(run, [
            ('backend', [sys.executable, '-m', 'pytest', 'apps/api/tests/', '-q', '-p', 'no:cacheprovider']),
            ('frontend', npm + ['test:web']),
        ]))
    rows.append(run(('build', npm + ['build'])))
    rows.append(run(('secrets', ['node', 'scripts/scan-secrets.js'])))
    report = {'at_utc': datetime.now(timezone.utc).isoformat(), 'base_head': head,
              'tracked_diff_sha256_excluding_owner_database_notes': hashlib.sha256(diff).hexdigest(),
              'cwd': str(ROOT), 'mode': 'offline_no_provider_calls', 'checks': rows,
              'passed': all(row['exit_code'] == 0 for row in rows)}
    (OUT / 'final-checks.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    sys.exit(0 if report['passed'] else 1)
