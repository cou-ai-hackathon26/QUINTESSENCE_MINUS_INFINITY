"""Real, local multilingual ONNX encoder. Never download or hash text into fake vectors."""
import json,hashlib
import threading
from pathlib import Path
from app.core.config import settings

_lock=threading.Lock()
_model=None
_identity=None
_error=None


def status():
    manifest=Path(settings.SEMANTIC_MODEL_PATH)/'manifest.json'
    return {'enabled':settings.SEMANTIC_ENABLED,'prepared':manifest.is_file(),'available':_model is not None and _error is None,'model':_identity,'error':_error}


def encode(texts,query=False):
    global _model,_identity,_error
    if not texts or not settings.SEMANTIC_ENABLED:return None,None
    with _lock:
        try:
            if _model is None:
                from fastembed import TextEmbedding
                from fastembed.common.model_description import ModelSource,PoolingType
                folder=Path(settings.SEMANTIC_MODEL_PATH)
                manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
                if hashlib.sha256((folder/manifest['model_file']).read_bytes()).hexdigest()!=manifest['model_sha256']:raise ValueError('Model artifact checksum mismatch')
                name=manifest['model']
                if name not in {row['model'] for row in TextEmbedding.list_supported_models()}:
                    TextEmbedding.add_custom_model(model=name,pooling=PoolingType.MEAN,normalization=True,sources=ModelSource(hf=name),dim=384,model_file=manifest['model_file'],license='mit')
                _model=TextEmbedding(model_name=name,specific_model_path=str(folder.resolve()),local_files_only=True,threads=2,providers=['CPUExecutionProvider'])
                _identity=name+'@'+manifest['revision']+':'+manifest['model_sha256']
            prefix='query: ' if query else 'passage: '
            vectors=[value.tolist() for value in _model.embed([prefix+text for text in texts],batch_size=8)]
            _error=None
            return vectors,_identity
        except Exception:
            _error='local_semantic_model_unavailable'
            return None,None
