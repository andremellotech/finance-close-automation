"""Gera entradas fictícias determinísticas e as executa pelo motor real."""
import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import pandas as pd
from .engine import FIELDS, process, money
from .io import load_rows, load_controls
from .export import write_outputs
from .report import render_report
from .configuration import normalize_catalog
from .configuration import normalize_profile
from .audit import ensure_execution

CATALOG = {"centros": {"ANA": "Analytics", "ENG": "Engenharia", "OPS": "Operações"}, "categorias": {"REV": "Receita", "DIR": "Custos diretos", "PES": "Pessoal", "TEC": "Tecnologia", "COM": "Comercial", "ADM": "Administrativo"}}
AMOUNTS = {"ANA": [200000, -50000, -60000, -15000, -8000, -7000], "ENG": [180000, -60000, -55000, -12000, -9000, -4000], "OPS": [220000, -75000, -70000, -14000, -11000, -5000]}
FILENAMES = {"ANA": "analytics.csv", "ENG": "engenharia.xlsx", "OPS": "operacoes.csv"}


def generate_demo(root):
    root = Path(root)
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config/catalogo.json").write_text(json.dumps(normalize_catalog(CATALOG), ensure_ascii=False, indent=2), encoding="utf-8")
    base = {}
    for area, values in AMOUNTS.items():
        base[area] = [dict(zip(FIELDS, [f"{area}-{index:03}", "2025-09-15", area, category, f"{label} — exemplo fictício", f"{amount:.2f}"])) for index, ((category, label), amount) in enumerate(zip(CATALOG["categorias"].items(), values), 1)]
    with (root / "config/controle.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["arquivo", "linhas_esperadas", "total_esperado_brl"])
        for area in base:
            writer.writerow([FILENAMES[area], 6, f"{sum(AMOUNTS[area]):.2f}"])
    results = {}
    for key in ("com-pendencias", "validado"):
        data = deepcopy(base)
        if key == "com-pendencias":
            data["ANA"][2]["centro_custo"] = "XYZ"
            data["ANA"].append({**base["ANA"][0], "registro_id": "", "valor_brl": "125.50"})
            data["ANA"].append(deepcopy(base["ANA"][0]))
            data["ENG"][3]["valor_brl"] = "valor inválido"
            data["ENG"].append({**base["ENG"][0], "valor_brl": "180100.00"})
            data["OPS"][4]["data_competencia"] = "2025-08-15"
        directory = root / "sample-input" / key
        directory.mkdir(parents=True, exist_ok=True)
        for area, records in data.items():
            file = directory / FILENAMES[area]
            if file.suffix == ".csv":
                with file.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter=";")
                    writer.writeheader()
                    writer.writerows(records)
            else:
                frame = pd.DataFrame(records, columns=FIELDS)
                frame["data_competencia"] = [datetime.fromisoformat(value) for value in frame["data_competencia"]]
                frame["valor_brl"] = [float(value) if value != "valor inválido" else value for value in frame["valor_brl"]]
                with pd.ExcelWriter(file, engine="xlsxwriter", datetime_format="yyyy-mm-dd", engine_kwargs={"options": {"strings_to_formulas": False}}) as writer:
                    writer.book.set_properties({"author": "André Mello", "title": "Entradas fictícias", "created": datetime(2025, 9, 30)})
                    frame.to_excel(writer, sheet_name="Lancamentos", index=False)
                    sheet = writer.sheets["Lancamentos"]
                    sheet.set_column("A:A", 18)
                    sheet.set_column("B:B", 22)
                    sheet.set_column("C:D", 17)
                    sheet.set_column("E:E", 43)
                    sheet.set_column("F:F", 20)
                    sheet.freeze_panes(1, 0)
                    sheet.autofilter(0, 0, len(frame), 5)
        rows, sources = load_rows(directory)
        result = process(rows, load_controls(root / "config/controle.csv"), "2025-09", CATALOG, sources)
        result['demonstrativo'] = True
        result['perfil_entrada'] = normalize_profile()
        result = ensure_execution(result)
        write_outputs(result, root / "examples" / key, overwrite=True)
        results[key] = result
    render_report(results, root / "index.html")
    return results
