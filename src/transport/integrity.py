"""Content guards; post-holdout amendments never rewrite the historical freeze."""
import hashlib,json
from datetime import datetime,timezone
from transport.acquire import dump

ANALYSIS_FILES=tuple('src/transport/'+n+'.py' for n in ('acquire','ingest','pipeline','spatial','analysis','evaluate','integrity'))+('requirements.lock','evidence/freeze.json')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def analysis_identity(root,raw):
    return {name:sha(root/name) for name in ANALYSIS_FILES}|{'raw_manifest':sha(raw/'manifest.json')}


def write_analysis_integrity(root,raw,phase):
    path=root/'evidence/analysis-integrity.json'
    if path.exists(): raise FileExistsError('analysis integrity is immutable; document a separate amendment')
    dump(path,{'phase':phase,'recorded_utc':datetime.now(timezone.utc).isoformat(),'files':analysis_identity(root,raw)})


def verify_analysis_integrity(root,raw):
    path=root/'evidence/analysis-integrity.json'
    if not path.exists(): raise ValueError('analysis integrity freeze missing')
    record=json.loads(path.read_text())
    if record['files']!=analysis_identity(root,raw): raise ValueError('analysis implementation or source manifest changed after integrity freeze')
