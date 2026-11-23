"""Actual local ONNX inference; synthetic independent retrieval probes, not pytest doubles."""
import json,time
from pathlib import Path
from app.core.config import settings
from app.retrieval.semantic import encode,status
from app.retrieval.engine import compute_cosine_similarity

settings.SEMANTIC_ENABLED=True
documents=['Damaged goods may be returned within seven days of delivery. An invoice is required.','Karim bought two hundred taka of rice on credit.','The shop opens at nine in the morning and closes at night.']
queries=['নষ্ট পণ্য কত দিনের মধ্যে ফেরত দেওয়া যাবে?','When can I bring back broken items?']
started=time.monotonic();passages,identity=encode(documents)
report={'scope':'Actual CPU multilingual E5 ONNX inference on English passages and independent Bangla/English paraphrases','passed':False,'model':identity,'checks':[]}
try:
    assert passages and len(passages[0])==384,str(status())
    for query in queries:
        vectors,_=encode([query],query=True);assert vectors
        scores=[compute_cosine_similarity(vectors[0],p) for p in passages]
        report['checks'].append({'query':query,'scores':scores,'top_document':scores.index(max(scores))})
        assert scores.index(max(scores))==0,'Return policy should outrank rice credit and opening hours'
    report['passed']=True
except Exception as error:report['failure']=str(error)
finally:
    report['elapsed_ms']=int((time.monotonic()-started)*1000)
    Path('docs/evidence/real-workflow/JR-03/semantic-inference.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'elapsed_ms':report['elapsed_ms'],'status':status(),'failure':report.get('failure')}))
    if not report['passed']:raise SystemExit(1)
