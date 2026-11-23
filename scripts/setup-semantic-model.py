"""Explicit bounded download of official multilingual E5 weights; never run on user requests."""
import hashlib,json,shutil
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download

model='intfloat/multilingual-e5-small'
target=Path('apps/api/data/models/multilingual-e5-small')
target.mkdir(parents=True,exist_ok=True)
revision=HfApi().model_info(model).sha
model_file='onnx/model_qint8_avx512_vnni.onnx'
files=['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json',model_file]
for filename in files:
    source=hf_hub_download(model,filename,revision=revision,cache_dir='tmp/hf-semantic-cache')
    destination=target/filename;destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,destination)
    print(json.dumps({'file':filename,'bytes':destination.stat().st_size}),flush=True)
manifest={'model':model,'revision':revision,'model_file':model_file,'model_sha256':hashlib.sha256((target/model_file).read_bytes()).hexdigest(),'dimension':384,'prefixes':{'query':'query: ','passage':'passage: '},'runtime':'fastembed 0.9.1 / ONNX Runtime CPU; quantized official artifact'}
(target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
Path('docs/evidence/real-workflow/JR-03').mkdir(parents=True,exist_ok=True)
Path('docs/evidence/real-workflow/JR-03/semantic-model.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'downloaded':True,'revision':revision,'dimension':384}))
