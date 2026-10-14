"""Interface de execução local e geração da demonstração."""
import argparse
import sys
import json
from pathlib import Path
from .engine import process
from .io import load_rows, load_controls, load_catalog
from .export import write_outputs
from .configuration import load_profile
from .audit import ensure_execution

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Automação demonstrativa de fechamento financeiro mensal")
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--input', required=True)
    common.add_argument('--controls', required=True)
    common.add_argument('--period', required=True)
    common.add_argument('--catalog', default=str(ROOT / 'config/catalogo.json'))
    common.add_argument('--profile', help='Perfil JSON de nomes de colunas e formatos de entrada')
    run = sub.add_parser('run', parents=[common], help='Consolidar CSV/XLSX e conferir controles')
    run.add_argument("--output", required=True)
    check = sub.add_parser('check', parents=[common], help='Conferir preparação e dados sem exportar arquivos')
    check.add_argument('--json', action='store_true', help='Imprimir diagnóstico estruturado')
    setup = sub.add_parser('setup', help='Assistente interativo para criar configuração')
    setup.add_argument('--output', required=True)
    compare = sub.add_parser('compare', help='Comparar dois resultados JSON sem alterar as execuções')
    compare.add_argument('--before', required=True)
    compare.add_argument('--after', required=True)
    compare.add_argument('--output', required=True)
    sub.add_parser("demo", help="Gerar os dois exemplos e a demonstração estática")
    args = parser.parse_args(argv)
    try:
        if args.command == 'compare':
            from .comparison import compare_results, write_comparison
            before = json.loads(Path(args.before).read_text(encoding='utf-8'))
            after = json.loads(Path(args.after).read_text(encoding='utf-8'))
            target = write_comparison(compare_results(before, after), args.output)
            print(f'Comparação gerada em {target}. O sucesso deste comando não aprova o lote financeiro.')
            return 0
        if args.command == 'setup':
            from .assistant import setup_project
            target = setup_project(args.output)
            print(f'Configuração criada em {target}. Preencha o controle independente antes de executar check.')
            return 0
        if args.command == 'check':
            from .diagnostics import diagnose, describe_diagnosis
            report = diagnose(args.input, args.controls, args.period, args.catalog, args.profile)
            print(json.dumps(report, ensure_ascii=False) if args.json else describe_diagnosis(report))
            return report['status']
        if args.command == "demo":
            from .demo import generate_demo
            generate_demo(ROOT)
            print("Demonstração e exemplos gerados em index.html e examples/.")
            return 0
        source, output = Path(args.input).resolve(), Path(args.output).resolve()
        if output == source or source in output.parents:
            raise ValueError("A saída deve ficar fora da pasta de entrada")
        profile = load_profile(args.profile)
        rows, sources = load_rows(source, profile)
        result = process(rows, load_controls(args.controls), args.period, load_catalog(args.catalog), sources)
        result['perfil_entrada'] = profile
        result = ensure_execution(result)
        write_outputs(result, output)
        print(f"{'VALIDADO' if result['liberado'] else 'COM PENDÊNCIAS'} | {result['resumo']['aprovadas']}/{result['resumo']['recebidas']} linhas aprovadas | Execução: {result['execucao']['id']} | Saída: {output}")
        return 0 if result["liberado"] else 2
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
