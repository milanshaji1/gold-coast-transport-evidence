"""Rebuild a committed checkout from the exact release archive without upstream access."""
import hashlib,json,os,subprocess,sys,tarfile,tempfile,time
from datetime import datetime,timezone
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
release_info=json.loads((root/'evidence/release.json').read_text())
release=root/'release/transport-inputs-8c293a52745057c4.tar.gz'
if sha(release)!='62661bb1f4116e86be3249173d263aded3a21d110a592fd0f47a2d1ed6e65a55':
    raise ValueError('release archive hash mismatch')
with tempfile.TemporaryDirectory(prefix='transport-clean-rebuild-') as td:
    temp=Path(td); target=temp/'checkout'; target.mkdir()
    code=temp/'code.tar'
    with code.open('wb') as stream:
        subprocess.run(['git','archive','HEAD'],cwd=root,check=True,stdout=stream)
    for archive in (code,release):
        with tarfile.open(archive) as tf: tf.extractall(target,filter='data')
    env=dict(os.environ,PYTHONPATH=str(target/'src'))
    commands=[['-m','transport.acquire',(target/'evidence/snapshot-path.txt').read_text().strip()],
              ['-m','transport.pipeline','freeze'],['-m','transport.pipeline','evaluate'],
              ['-m','transport.map_layers'],['-m','transport.roads'],['-m','transport.exports']]
    executions=[]
    for args in commands:
        started=time.monotonic()
        result=subprocess.run([sys.executable,*args],cwd=target,env=env,text=True,capture_output=True,timeout=120)
        executions.append({'command':'python '+' '.join(args),'exit_code':result.returncode,'seconds':round(time.monotonic()-started,3)})
        if result.returncode: raise RuntimeError(result.stdout+'\n'+result.stderr)
    same=sha(target/'evidence/results.json')==sha(root/'evidence/results.json')
    if not same: raise ValueError('rebuilt result differs from historical result')
    compared={p.name:sha(p)==sha(target/'site/data'/p.name) for p in (root/'site/data').iterdir() if p.is_file()}
    if not all(compared.values()): raise ValueError(f'public exports differ: {compared}')
    report={'status':'passed','recorded_utc':datetime.now(timezone.utc).isoformat(),
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
            'snapshot_id':'8c293a52745057c4','release_sha256':sha(release),
            'result_sha256':sha(target/'evidence/results.json'),'same_as_recorded':same,
            'site_exports_identical':compared,'commands':executions,
            'scope':'Fresh code extraction and frozen data archive, existing pinned runtime reused; no upstream network calls. Post-review integrity checks enabled. Original single-pass acquisition consistency is not retrospectively proven.'}
    (root/'evidence/reproducibility.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
