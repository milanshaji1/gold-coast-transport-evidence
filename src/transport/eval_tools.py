"""Post-freeze tool-contract evaluation, not an LLM benchmark."""
import asyncio,hashlib,json,time
from datetime import datetime,timezone
from uuid import uuid4
from pathlib import Path
from transport.client import call_tools
from transport.acquire import dump

def response_error(response):
    return response.get('is_error', response.get('isError', False))

FROZEN_RUNTIME=('src/transport/client.py','src/transport/tools.py','src/transport/server.py','src/transport/retrieval.py',
                'data/corpus/documents.json','evidence/ai/final-tool-cases.json')
AMENDED_FILES=('evidence/ai/system-freeze.json','evidence/ai/final-tool-results.json',
               'evidence/ai/final-tool-results-original-scoring.json','evidence/results.json',
               'src/transport/eval_tools.py','requirements.lock')


def verify_tool_freeze(root):
    frozen=json.loads((root/'evidence/ai/system-freeze.json').read_text())
    for name in FROZEN_RUNTIME:
        if name not in frozen or not (root/name).is_file() or hashlib.sha256((root/name).read_bytes()).hexdigest()!=frozen[name]:
            raise ValueError(f'tool freeze mismatch: {name}')
    amendment=root/'evidence/ai/scorer-amendment.json'
    if not amendment.exists(): raise ValueError('tool freeze scorer amendment missing')
    amended=json.loads(amendment.read_text())['files']
    for name in AMENDED_FILES:
        if name not in amended or not (root/name).is_file() or hashlib.sha256((root/name).read_bytes()).hexdigest()!=amended[name]:
            raise ValueError(f'tool freeze amendment mismatch: {name}')
    return hashlib.sha256((root/'evidence/ai/system-freeze.json').read_bytes()).hexdigest()


async def evaluate(root):
    freeze_sha=verify_tool_freeze(root)
    cases=json.loads((root/'evidence/ai/final-tool-cases.json').read_text())
    outputs=[]
    for offset in range(0,len(cases),6):
        batch=cases[offset:offset+6]
        response=await call_tools([c['request'] for c in batch])
        for c,actual in zip(batch,response['calls']):
            r=actual['response']; structured=r.get('structured_content', r.get('structuredContent'))
            # MCP SDK wraps some structured dict returns under result.
            if structured is None:
                content=r.get('content',[])
                try: structured=json.loads(next(b['text'] for b in content if b.get('type')=='text'))
                except (ValueError,StopIteration): structured={}
            if 'result' in structured: structured=structured['result']
            expected=c['expected']
            if expected.get('error'): passed=response_error(r) is True
            else:
                passed=not response_error(r)
                for key,value in expected.items():
                    if key=='document_id': passed=passed and value in [d['id'] for d in structured.get('documents',[])]
                    elif key=='empty_documents': passed=passed and structured.get('documents')==[]
                    elif key=='quality_crashes': passed=passed and structured.get('quality',{}).get('analysis_crashes')==value
                    else: passed=passed and structured.get(key)==value
            outputs.append({'id':c['id'],'category':c['category'],'passed':bool(passed),'request':c['request'],'expected':expected,'response':r})
    report={'evaluation_kind':'regression replay of already-seen cases; not a new held-out evaluation',
            'system_freeze_sha256':freeze_sha,'recorded_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Tool contracts over real MCP transport. No live LLM, agent-selection or generated-answer reliability claim.',
            'cases':len(outputs),'passed':sum(c['passed'] for c in outputs),'results':outputs}
    # Append a unique replay record; neither historical score file is a write target.
    directory=root/'evidence/ai/regressions'; directory.mkdir(exist_ok=True)
    path=directory/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8]+'.json')
    with path.open('x') as stream: json.dump(report,stream,indent=2,sort_keys=True,allow_nan=False)
    print(f'Regression artifact: {path}')
    print({k:v for k,v in report.items() if k!='results'})
    return report

if __name__=='__main__': asyncio.run(evaluate(Path(__file__).resolve().parents[2]))
