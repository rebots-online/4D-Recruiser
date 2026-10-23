"""Regenerate/check architecture views; documentation tooling, not product code."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re

OUT = Path(__file__).resolve().parent
MASTER = OUT.parents[1] / 'ARCHITECTURE.md'
DEPS = {
    'C01': [], 'G01': ['C01'], 'I01': ['C01', 'G01'],
    'S01': ['C01', 'G01'], 'T01': ['C01'], 'D01': ['C01'],
    'A01': ['C01'], 'R01': ['C01', 'G01', 'T01'],
    'J01': ['C01', 'I01', 'S01', 'A01'], 'W01': ['C01'],
    'P01': ['C01', 'S01'], 'U01': ['C01', 'W01'],
    'H01': ['C01', 'D01'],
    'B01': ['C01', 'G01', 'I01', 'S01', 'T01', 'D01', 'A01',
            'R01', 'J01', 'W01', 'P01', 'U01', 'H01'],
}


def main(refresh):
    source = MASTER.read_text(encoding='utf-8')
    rows = []
    for line in source.splitlines():
        if not re.match(r'^\| E\d{3} \|', line):
            continue
        cells = [v.strip() for v in line.strip('|').split('|')]
        assert len(cells) == 6, cells
        eid, loc, decl, behavior, engaged, ad = cells
        owner, suffix = loc.split(' / ', 1)
        rows.append(dict(id=eid, owner=owner, pathSuffix=suffix,
                         declaration=decl.replace('`', ''), behavior=behavior,
                         engagedBy=engaged.split(','), authorizedBy=ad))
    assert [r['id'] for r in rows] == [f'E{i:03}' for i in range(1, 88)]
    for row in rows:
        assert row['owner'] in DEPS
        assert re.fullmatch(r'AD(?:0[1-9]|10)', row['authorizedBy'])
        assert all(v.strip() in DEPS or v.strip() in ['all', 'CLI']
                   for v in row['engagedBy'])
    modules = [dict(id=k, uses=v, declarations=[r for r in rows if r['owner'] == k])
               for k, v in DEPS.items()]
    tree = ['@startjson', '{"solution":"4D-Recruiser v2.0",'
            '"status":"architecture; TC12 UI freeze outstanding","modules":[']
    tree += [json.dumps(m, ensure_ascii=False, separators=(',', ':'))
             + (',' if i < len(modules)-1 else '') for i, m in enumerate(modules)]
    tree += [']}', '@endjson']
    graph = ['flowchart LR', 'ROOT["4D-Recruiser solution AST"]']
    for module in modules:
        owner = module['id']
        graph.append(f'subgraph {owner}["{owner} owned declarations"]')
        for row in module['declarations']:
            names = re.findall(r'(?:^|; )([A-Za-z_][A-Za-z0-9_]*(?:<T>)?)(?=[{=( :]|$)',
                               row['declaration']) or [row['declaration'].split('{')[0]]
            label = html.escape(row['id'] + ' ' + ', '.join(names), quote=True)
            graph.append(f'{row["id"]}["{label}"]')
        graph.extend(['end', f'ROOT --> {owner}'])
    for owner, uses in DEPS.items():
        if uses:
            graph.append(owner + ' -. uses .-> ' + ' & '.join(uses))
    views = '```plantuml\n' + '\n'.join(tree) + '\n```\n\n```mermaid\n'
    views += '\n'.join(graph) + '\n```\n'
    refreshed = re.sub(r'<!-- AST_VIEWS_BEGIN -->[\s\S]*?<!-- AST_VIEWS_END -->',
                       '<!-- AST_VIEWS_BEGIN -->\n' + views + '<!-- AST_VIEWS_END -->', source)
    if refresh:
        MASTER.write_text(refreshed, encoding='utf-8')
        source = refreshed
    assert source == refreshed, 'Diagram drift: run --refresh and render again'
    assert len(source.splitlines()) < 500
    assert len(re.findall(r'^```', source, re.M)) % 2 == 0
    assert json.loads('\n'.join(tree[1:-1]))['modules'] == modules
    assert set(re.findall(r'^(E\d{3})\[', '\n'.join(graph), re.M)) == {r['id'] for r in rows}
    (OUT / 'solution-ast.puml').write_text('\n'.join(tree) + '\n', encoding='utf-8')
    for i, block in enumerate(re.findall(r'```mermaid\n(.*?)\n```', source, re.S)):
        name = 'workflow.mmd' if i == 0 else 'solution-ast.mmd'
        (OUT / name).write_text(block + '\n', encoding='utf-8')
    report = dict(master='DOCS/ARCHITECTURE.md', sha256=hashlib.sha256(MASTER.read_bytes()).hexdigest(),
                  entityGroups=len(rows), modules=len(modules), lines=len(source.splitlines()),
                  tablePlantUmlMermaidParity='PASS', balancedFences='PASS',
                  ownerAndDecisionReferences='PASS', productRuntime='NOT RUN',
                  architectureExit='NOT ATTESTED: TC12 UI source export and clearance absent')
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    main(parser.parse_args().refresh)
