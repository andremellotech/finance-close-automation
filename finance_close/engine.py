"""Regras puras de qualidade e conciliação; dinheiro sempre em centavos."""
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from .configuration import FIELDS, normalize_catalog
from .guidance import explain


def parse_cents(value):
    if isinstance(value, bool) or value is None:
        raise ValueError("Valor monetário inválido")
    text = str(value).strip()
    if not re.fullmatch(r"-?\d+(?:\.\d{1,2})?", text):
        raise ValueError("Use um número com ponto decimal e até duas casas")
    return int(Decimal(text) * 100)


def money(cents):
    return f"{'-' if cents < 0 else ''}{abs(cents) // 100}.{abs(cents) % 100:02d}"


def process(rows, controls, period, catalog, source_files=None):
    catalog = normalize_catalog(catalog)
    if not re.fullmatch(r"\d{4}-\d{2}", period):
        raise ValueError("Competência deve ser AAAA-MM")
    date.fromisoformat(period + "-01")
    entries = []
    for original in sorted(rows, key=lambda r: (r["arquivo"], r["linha"])):
        entry = {**original, "erros": list(original.get('_input_errors', [])), "status": "APROVADO", "valor_centavos": None}
        for field in FIELDS:
            value = original.get(field, "")
            if isinstance(value, (datetime, date)) and field == "data_competencia":
                value = value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
            entry[field] = str(value).strip() if value is not None else ""
            if not entry[field] and field in catalog['obrigatorios']:
                entry["erros"].append("CAMPO_VAZIO:" + field)
        try:
            raw_date = entry["data_competencia"]
            parsed = date.fromisoformat(raw_date)
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
                raise ValueError()
            if parsed.strftime("%Y-%m") != period:
                entry["erros"].append("FORA_COMPETENCIA")
        except ValueError:
            entry["erros"].append("DATA_INVALIDA")
        if entry["centro_custo"] and entry["centro_custo"] not in catalog["centros"]:
            entry["erros"].append("CENTRO_DESCONHECIDO")
        if entry["categoria"] not in catalog["categorias"]:
            entry["erros"].append("CATEGORIA_DESCONHECIDA")
        try:
            if original.get('_valor_formato_invalido'):
                raise ValueError('Formato monetário diferente do perfil')
            entry["valor_centavos"] = parse_cents(original.get("valor_brl"))
            value = entry["valor_centavos"]
            sign = catalog['categorias'].get(entry['categoria'], {}).get('sinal')
            if (sign == 'nao_negativo' and value < 0) or (sign == 'nao_positivo' and value > 0):
                entry["erros"].append("SINAL_INCOMPATIVEL")
        except ValueError:
            entry["erros"].append("VALOR_INVALIDO")
        if original.get("_formula"):
            entry["erros"].append("FORMULA_NAO_ACEITA")
        for field in original.get("_excel_errors", []):
            entry["erros"].append("ERRO_CELULA_EXCEL:" + field)
        if entry["erros"]:
            entry["status"] = "PENDENTE"
        entries.append(entry)

    by_id = defaultdict(list)
    for entry in entries:
        if entry["registro_id"]:
            by_id[entry["registro_id"]].append(entry)
    for group in by_id.values():
        if len(group) < 2:
            continue
        def identity(e):
            return tuple(e[k] if k != "valor_brl" else (e["valor_centavos"] if e["valor_centavos"] is not None else e[k]) for k in FIELDS)
        if len({identity(e) for e in group}) > 1:
            for entry in group:
                entry["status"] = "CONFLITO"
                entry["erros"].append("CONFLITO_ID")
        else:
            for entry in group[1:]:
                entry["erros"].append("DUPLICATA_EXATA")
                if entry["status"] == "APROVADO":
                    entry["status"] = "DUPLICADO"

    files = set(source_files if source_files is not None else (e["arquivo"] for e in entries))
    reconciliations = []
    for filename in sorted(files | set(controls)):
        received = [e for e in entries if e["arquivo"] == filename]
        unknown = sum(e["valor_centavos"] is None for e in received)
        observed = sum(e["valor_centavos"] or 0 for e in received)
        expected = controls.get(filename)
        expected_count = expected_total = None
        if expected is not None:
            raw_count = str(expected["linhas_esperadas"]).strip()
            if not re.fullmatch(r"\d+", raw_count):
                raise ValueError("Controle com quantidade inválida: " + filename)
            expected_count = int(raw_count)
            expected_total = parse_cents(expected["total_esperado_brl"])
        if filename not in files:
            status = "ARQUIVO_AUSENTE"
        elif expected is None:
            status = "SEM_CONTROLE"
        elif not received:
            status = "VAZIO"
        elif unknown:
            status = "INCOMPLETO"
        elif len(received) != expected_count or observed != expected_total:
            status = "DIVERGENTE"
        else:
            status = "CONCILIADO"
        reconciliations.append(dict(arquivo=filename, linhas_recebidas=len(received), linhas_esperadas=expected_count, total_recebido_centavos=observed, total_esperado_centavos=expected_total, valores_nao_quantificaveis=unknown, diferenca_centavos=None if unknown or expected_total is None or filename not in files else observed - expected_total, status=status))

    for entry in entries:
        entry['orientacoes'] = explain(entry['erros'])
    counts = Counter(e["status"] for e in entries)
    approved = [e for e in entries if e["status"] == "APROVADO"]
    total_approved = sum(e["valor_centavos"] for e in approved)
    total_excluded = sum(e["valor_centavos"] or 0 for e in entries if e["status"] != "APROVADO")
    summary = dict(arquivos=len(files), recebidas=len(entries), aprovadas=counts["APROVADO"], pendentes=counts["PENDENTE"], duplicadas=counts["DUPLICADO"], conflitos=counts["CONFLITO"], excluidas=len(entries) - len(approved), valores_nao_quantificaveis=sum(e["valor_centavos"] is None for e in entries), total_recebido_centavos=total_approved + total_excluded, total_aprovado_centavos=total_approved, total_excluido_centavos=total_excluded, receitas_centavos=sum(e["valor_centavos"] for e in approved if catalog['categorias'][e['categoria']]['natureza'] == 'receita'), gastos_centavos=-sum(e["valor_centavos"] for e in approved if catalog['categorias'][e['categoria']]['natureza'] == 'gasto'))
    released = bool(entries) and not summary["excluidas"] and all(c["status"] == "CONCILIADO" for c in reconciliations)
    return dict(competencia=period, liberado=released, resumo=summary, linhas=entries, conciliacao=reconciliations, fontes=source_files or {}, catalogo=catalog)
