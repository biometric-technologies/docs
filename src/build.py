#!/usr/bin/env python3
"""Build docs.iriscan.net: Markdown pages + OpenAPI reference -> static HTML."""
import html, json, os, re, shutil, sys
import markdown, yaml

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, '..', 'site')

ORDER = ['index', 'sdk', 'converter', 'cloud-api', 'edge', 'mosip']
GROUPS = [('Get started', ['index']), ('Open source', ['sdk', 'converter']),
          ('Services', ['cloud-api', 'edge']), ('Integrations', ['mosip'])]

LOGO = '<svg viewBox="37.65 43.294 511.585 511.598" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M536.34 219.06c-21.16 64.09-66.99 116.98-126.25 147.41-1.93-39.3-12.98-78.7-33.99-115.1-21.01-36.38-49.62-65.68-82.65-86.98-56-36.11-124.74-49.37-190.87-35.61C181.54 40.09 314.45 15.9 421.32 77.6c24.26 14 45.35 31.37 63.03 51.2 23.61 26.48 41.15 57.31 51.99 90.26z" fill="#5cc8ff"/><path d="M176.78 366.45c-3.29 66.55 19.62 132.7 64.57 183.09-25.98-5.39-51.55-14.96-75.79-28.96C58.7 458.9 13.21 331.71 50.51 218.98c5.39-16.31 12.52-32.31 21.45-47.76 8.92-15.46 19.2-29.62 30.62-42.44 66.13-13.75 134.87-.5 190.87 35.61-33.06 21.3-61.66 50.57-82.67 86.98-21.02 36.4-32.07 75.81-34 115.08z" fill="#1c77c3"/><path d="M514.93 426.97c-37.9 65.68-100.54 108.15-169.36 122.51-33.97 7.09-69.46 7.32-104.22.06-44.95-50.39-67.86-116.54-64.57-183.09 34.99 17.97 74.64 28.1 116.66 28.1s81.67-10.13 116.64-28.08c59.27-30.43 105.1-83.32 126.25-147.41 22 66.76 16.51 142.25-21.4 207.91z" fill="#0a328f"/></svg>'

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&family=Open+Sans:wght@400;600&family=Raleway:wght@400&family=JetBrains+Mono:wght@400;500&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'">'
         '<noscript><link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&family=Open+Sans:wght@400;600&family=Raleway:wght@400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"></noscript>')
STRIP = '<script>if(/\\.html$/.test(location.pathname))history.replaceState(null,"",location.pathname.replace(/(index)?\\.html$/,"")+location.search+location.hash)</script>'

def clean_links(h):
    h = re.sub(r'href="index\.html(#[^"]*)?"', lambda m: 'href="/' + (m.group(1) or '') + '"', h)
    return re.sub(r'href="([a-z0-9-]+)\.html(#[^"]*)?"', lambda m: f'href="/{m.group(1)}{m.group(2) or ""}"', h)


def parse(path):
    raw = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n', raw, re.S)
    meta = yaml.safe_load(m.group(1))
    return meta, raw[m.end():]


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


# ---------- OpenAPI rendering ----------
EXAMPLES = {
    'addPerson': ('POST', '/persons', {'name': 'Jane Doe', 'leftEye': '<base64 image>', 'rightEye': '<base64 image>',
                                      'metadata': {'employeeId': 'E-1042'}}),
    'editPerson': ('PUT', '/persons/6041f3a2c1e8', {'name': 'Jane A. Doe', 'metadata': {'employeeId': 'E-1042', 'site': 'Tallinn'}}),
    'deletePerson': ('DELETE', '/persons/6041f3a2c1e8', None),
    'queryPersons': ('GET', '/persons/query?term=doe&page=0&pageSize=20&sort=name,asc', None),
    'findPersons': ('POST', '/persons/find', {'eye': '<base64 image>'}),
    'verifyPersons': ('POST', '/persons/6041f3a2c1e8/verify', {'eye': '<base64 image>'}),
}
PERSON_EX = {'id': '6041f3a2c1e8', 'tenantId': '5f9b1c7e2a44', 'iris': {
    'leftEye': {'raw': '<base64>', 'code': '<base64 iris code>', 'mask': '<base64 mask>', 'blackPercentage': 0.12},
    'rightEye': {'raw': '<base64>', 'code': '<base64 iris code>', 'mask': '<base64 mask>', 'blackPercentage': 0.09}},
    'metadata': {'employeeId': 'E-1042'}}
RESP_EX = {'Person': PERSON_EX,
           'PersonPage': {'numberOfElements': 1, 'totalElements': 1, 'totalPages': 1, 'content': [PERSON_EX]}}


FIELD_DESC = {
    'name': 'Display name of the person', 'leftEye': 'Left eye image, base64 (PNG or JPEG)',
    'rightEye': 'Right eye image, base64 (PNG or JPEG)', 'metadata': 'Any JSON object stored with the person, returned as is',
    'eye': 'Probe eye image, base64 (PNG or JPEG)', 'raw': 'Normalised iris texture, base64', 'code': 'Binary iris code, base64',
    'mask': 'Mask of unusable bits for the code, base64', 'blackPercentage': 'Share of the iris hidden by eyelids, lashes or reflections (0–1)',
    'iris': 'Templates for both eyes', 'leftEye ': '', 'numberOfElements': 'Persons on this page', 'totalElements': 'Persons matching the query',
    'totalPages': 'Number of pages', 'content': 'Persons on this page', 'timestamp': 'Time of the error', 'status': 'HTTP status name',
    'message': 'Human-readable error', 'errors': 'Validation messages, one per field', 'id': 'Person ID', 'tenantId': 'Tenant ID',
}


def schema_rows(spec, schema, prefix=''):
    rows = []
    if '$ref' in schema:
        schema = spec['components']['schemas'][schema['$ref'].split('/')[-1]]
    for name, p in (schema.get('properties') or {}).items():
        if '$ref' in p:
            t = p['$ref'].split('/')[-1]
            typ = f'<a href="#schema-{slug(t)}">{t}</a>'
        elif p.get('type') == 'array':
            it = p.get('items', {})
            typ = 'array of ' + (f'<a href="#schema-{slug(it["$ref"].split("/")[-1])}">{it["$ref"].split("/")[-1]}</a>' if '$ref' in it else it.get('type', ''))
        else:
            typ = p.get('type', 'object') + (f' ({p["format"]})' if p.get('format') else '')
            if p.get('format') == 'binary':
                typ = 'string (base64 image)'
        rows.append((prefix + name, typ, FIELD_DESC.get(name) or p.get('description', '')))
    return rows


def table(rows, head=('Field', 'Type', 'Description')):
    if not rows:
        return ''
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' if i else f'<td><code>{c}</code></td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def render_openapi(path):
    spec = yaml.safe_load(open(path, encoding='utf-8'))
    out = []
    for p, item in spec['paths'].items():
        for method, op in item.items():
            oid = op.get('operationId', '')
            out.append(f'<div class="op" id="{slug(oid)}">')
            out.append(f'<h3><span class="badge m-{method}">{method.upper()}</span>{html.escape(p)}</h3>')
            out.append(f'<p class="sum">{html.escape(op.get("summary", ""))}</p>')
            params = [(x['name'], f'{x["in"]}, ' + x.get('schema', {}).get('type', '') + (', required' if x.get('required') else ''),
                       html.escape(x.get('description') or x.get('schema', {}).get('description', ''))) for x in op.get('parameters', [])]
            if params:
                out.append('<h4>Parameters</h4>' + table(params, ('Name', 'Where', 'Description')))
            rb = op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
            if rb:
                out.append('<h4>Request body</h4>' + table(schema_rows(spec, rb)))
            ex = EXAMPLES.get(oid)
            if ex:
                m, url, body = ex
                cmd = f'curl -X {m} "https://api.iriscan.net{url}" \\\n  -H "Api-Key: $IRISCAN_API_KEY"'
                if body is not None:
                    cmd += ' \\\n  -H "Content-Type: application/json" \\\n  -d \'' + json.dumps(body, indent=2) + "'"
                out.append('<h4>Example</h4><pre><code>' + html.escape(cmd) + '</code></pre>')
            resp = op.get('responses', {})
            ok = resp.get('200', {}).get('content', {}).get('application/json', {}).get('schema', {})
            ref = ok.get('$ref', '').split('/')[-1]
            if ref in RESP_EX:
                out.append('<h4>Response 200</h4><pre><code>' + html.escape(json.dumps(RESP_EX[ref], indent=2)) + '</code></pre>')
            codes = ''.join(f'<span><b>{c}</b>{html.escape(r.get("description", ""))}</span>' for c, r in sorted(resp.items()))
            out.append(f'<h4>Responses</h4><p class="resp">{codes}</p></div>')
    out.append('<h2 id="schemas">Schemas</h2>')
    for name, s in spec['components']['schemas'].items():
        out.append(f'<h3 id="schema-{slug(name)}">{name}</h3>' + table(schema_rows(spec, s)))
    return '\n'.join(out)


# ---------- page shell ----------
def sidebar(pages, cur, toc):
    out = []
    for g, ids in GROUPS:
        out.append(f'<div class="grp"><b>{g}</b>')
        for i in ids:
            cls = ' class="on"' if i == cur else ''
            out.append(f'<a href="{i}.html"{cls}>{pages[i]["nav"]}</a>')
            if i == cur:
                out += [f'<a class="sub" href="#{a}">{html.escape(t)}</a>' for a, t in toc]
        out.append('</div>')
    out.append('<div class="grp"><b>Links</b><a href="https://www.iriscan.com/">iriscan.com</a>'
               '<a href="https://github.com/biometric-technologies">GitHub</a>'
               '<a href="https://www.iriscan.com/biometric-data-interchange#demo">Converter demo</a></div>')
    return '\n'.join(out)


def shell(meta, body, nav, prev, nxt, canonical):
    CSS = open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()
    pager = '<div class="pager">'
    pager += f'<a href="{prev[0]}.html"><small>Previous</small>{prev[1]}</a>' if prev else '<span></span>'
    pager += f'<a class="next" href="{nxt[0]}.html"><small>Next</small>{nxt[1]}</a>' if nxt else '<span></span>'
    pager += '</div>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
{STRIP}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(meta["title"])} · Iriscan Docs</title>
<meta name="description" content="{html.escape(meta.get("desc", ""))}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.png">
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header class="top">
<a class="brand" href="index.html">{LOGO}<span>IRISCAN</span><small>Docs</small></a>
<nav><a href="sdk.html">SDK</a><a href="converter.html">Converter</a><a href="cloud-api.html">Cloud API</a><a href="https://github.com/biometric-technologies">GitHub</a><a href="https://www.iriscan.com/get-started">Contact</a></nav>
<button class="menu-btn" type="button" onclick="document.body.classList.toggle('nav-open')">Menu</button>
</header>
<div class="layout">
<aside class="side" onclick="if(event.target.tagName==='A')document.body.classList.remove('nav-open')">
{nav}
</aside>
<main class="doc">
{body}
{pager}
<footer class="foot">© 2019–2026 Biometric Technologies OÜ · Tallinn, Estonia · <a href="mailto:info@iriscan.net">info@iriscan.net</a></footer>
</main>
</div>
</body>
</html>
'''


def build():
    if os.path.exists(OUT):
        for f in os.listdir(OUT):
            if f in ('.git', 'CNAME', '.nojekyll'):
                continue
            p = os.path.join(OUT, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    pages = {}
    for pid in ORDER:
        meta, md = parse(os.path.join(SRC, 'pages', pid + '.md'))
        pages[pid] = dict(meta, md=md)
    for n, pid in enumerate(ORDER):
        meta = pages[pid]
        md = meta['md']
        conv = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'attr_list', 'md_in_html'],
                                 extension_configs={'toc': {'slugify': lambda v, s: slug(v)}})
        body = conv.convert(md.replace('{{REFERENCE}}', '<!--REF-->'))
        if '<!--REF-->' in body:
            body = re.sub(r'(<p>)?<!--REF-->(</p>)?', lambda m: render_openapi(os.path.join(SRC, 'tenant-api.yaml')), body)
        toc = [(t['id'], t['name']) for t in conv.toc_tokens[0]['children']] if conv.toc_tokens else []
        if pid == 'cloud-api':
            toc.append(('schemas', 'Schemas'))
        prev = (ORDER[n - 1], pages[ORDER[n - 1]]['nav']) if n else None
        nxt = (ORDER[n + 1], pages[ORDER[n + 1]]['nav']) if n + 1 < len(ORDER) else None
        canonical = 'https://docs.iriscan.net/' + ('' if pid == 'index' else pid)
        open(os.path.join(OUT, pid + '.html'), 'w', encoding='utf-8').write(
            clean_links(shell(meta, body, sidebar(pages, pid, toc), prev, nxt, canonical)))
    shutil.copy(os.path.join(SRC, 'style.css'), OUT)
    shutil.copy(os.path.join(SRC, 'tenant-api.yaml'), os.path.join(OUT, 'openapi.yaml'))
    if os.path.exists(os.path.join(SRC, 'favicon.png')):
        shutil.copy(os.path.join(SRC, 'favicon.png'), OUT)
    open(os.path.join(OUT, '404.html'), 'w').write(open(os.path.join(OUT, 'index.html')).read())
    print('built', len(ORDER), 'pages ->', OUT)


if __name__ == '__main__':
    build()
