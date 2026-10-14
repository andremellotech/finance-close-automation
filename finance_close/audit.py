"""Identificação local de execução e das configurações efetivamente utilizadas."""
from datetime import datetime, timezone
import hashlib
import json
import platform
from uuid import uuid4
from . import __version__


def fingerprint(value):
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(content).hexdigest()


def ensure_execution(result):
    if 'execucao' in result:
        return result
    controls = {c['arquivo']: {'linhas_esperadas': c['linhas_esperadas'], 'total_esperado_centavos': c['total_esperado_centavos']} for c in result['conciliacao'] if c['linhas_esperadas'] is not None}
    profile = result.get('perfil_entrada')
    execution = {
        'id': str(uuid4()),
        'gerado_em_utc': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'versao_aplicacao': __version__, 'versao_python': platform.python_version(),
        'configuracoes': {'catalogo_sha256': fingerprint(result['catalogo']), 'perfil_sha256': fingerprint(profile) if profile is not None else None, 'controle_sha256': fingerprint(controls)},
    }
    return {**result, 'schema_versao': 1, 'execucao': execution}
