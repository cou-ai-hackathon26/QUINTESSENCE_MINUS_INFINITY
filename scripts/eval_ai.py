"""Compatibility entry point. No fake image/audio bytes or invented evaluation metrics."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
args=['scripts/verify-groq-live.py'] if '--live' in sys.argv else ['-m','pytest','apps/api/tests/test_groq_provider.py','apps/api/tests/test_evidence_retry.py','-q','-p','no:cacheprovider']
print('Actual provider verification' if '--live' in sys.argv else 'Offline provider contract tests; not a model-quality benchmark',flush=True)
raise SystemExit(subprocess.call([sys.executable,*args],cwd=root))
