#!/usr/bin/env python3
"""Servidor da UI do cérebro (lab/). Zero dependências — só stdlib.

Uso:   python3 lab/ui/server.py [porta]      (padrão: 8765)
Abre:  http://localhost:8765

Lê lab/ e updates/ ao vivo a cada request — nada de build, nada de cache.
Única escrita permitida: marcar/desmarcar checkbox em
knowledge/wiki/pendencias-globais.md (convenção da própria página:
"quem concluir um item, marca aqui com data").
"""
import json
import os
import re
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

UI_DIR = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(UI_DIR)
REPO = os.path.dirname(LAB)
UPDATES = os.path.join(REPO, 'updates')
PENDENCIAS = os.path.join(LAB, 'knowledge', 'wiki', 'pendencias-globais.md')


def safe_path(rel):
    """Resolve caminho relativo ao repo, restrito a lab/ e updates/."""
    full = os.path.realpath(os.path.join(REPO, rel))
    for base in (LAB, UPDATES):
        if full == base or full.startswith(base + os.sep):
            return full
    raise PermissionError(rel)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def first_heading(text, fallback):
    for line in text.splitlines():
        if line.startswith('#'):
            return line.lstrip('#').strip()
    return fallback


def list_md(dirpath):
    if not os.path.isdir(dirpath):
        return []
    return sorted(f for f in os.listdir(dirpath) if f.endswith('.md'))


def parse_tsv(path):
    if not os.path.exists(path):
        return [], []
    lines = [l for l in read(path).splitlines() if l.strip()]
    if not lines:
        return [], []
    header = lines[0].split('\t')
    rows = [dict(zip(header, l.split('\t'))) for l in lines[1:]]
    return header, rows


def md_collection(dirpath, prefix):
    out = []
    for f in list_md(dirpath):
        content = read(os.path.join(dirpath, f))
        out.append({'file': f, 'path': f'{prefix}/{f}',
                    'title': first_heading(content, f), 'content': content})
    return out


def api_overview():
    _, agents = parse_tsv(os.path.join(LAB, 'agents', 'catalog.tsv'))
    by_status, by_domain = {}, {}
    for a in agents:
        s, d = a.get('status', '?'), a.get('domain', '?')
        by_status[s] = by_status.get(s, 0) + 1
        by_domain[d] = by_domain.get(d, 0) + 1

    pend = read(PENDENCIAS) if os.path.exists(PENDENCIAS) else ''
    open_items = len(re.findall(r'^\s*- \[ \]', pend, re.M))
    done_items = len(re.findall(r'^\s*- \[x\]', pend, re.M))

    upd_files = sorted(list_md(UPDATES), reverse=True)
    recent = [{'file': f, 'title': first_heading(read(os.path.join(UPDATES, f)), f)}
              for f in upd_files[:8]]

    inbox_dir = os.path.join(LAB, 'inbox')
    inbox = [f for f in os.listdir(inbox_dir)
             if not f.startswith('.') and f != 'README.md'] if os.path.isdir(inbox_dir) else []

    _, score = parse_tsv(os.path.join(LAB, 'scoreboard.tsv'))
    skills = [f for f in list_md(os.path.join(LAB, 'skills'))]
    archive_dir = os.path.join(LAB, 'archive')
    archived = [f for f in os.listdir(archive_dir)
                if not f.startswith('.')] if os.path.isdir(archive_dir) else []

    return {
        'agents': {'total': len(agents), 'by_status': by_status, 'by_domain': by_domain},
        'pendencias': {'open': open_items, 'done': done_items},
        'updates_total': len(upd_files),
        'updates_recent': recent,
        'inbox': inbox,
        'scoreboard_rows': len(score),
        'skills_total': len(skills),
        'archive_total': len(archived),
    }


def toggle_pendencia(req):
    lines = read(PENDENCIAS).splitlines()
    i = req.get('line', -1)
    if not (isinstance(i, int) and 0 <= i < len(lines)) or lines[i] != req.get('expect'):
        return 409, {'error': 'o arquivo mudou desde o carregamento — recarregue a página'}
    line, today = lines[i], date.today().isoformat()
    if '- [ ]' in line:
        line = line.replace('- [ ]', '- [x]', 1) + f' *(feito {today} via UI)*'
    elif '- [x]' in line:
        line = re.sub(r'\s*\*\(feito \d{4}-\d{2}-\d{2} via UI\)\*\s*$', '', line)
        line = line.replace('- [x]', '- [ ]', 1)
    else:
        return 400, {'error': 'a linha não é um checkbox'}
    lines[i] = line
    with open(PENDENCIAS, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return 200, {'ok': True, 'line': line}


def api_biblioteca():
    """A biblioteca: catálogo de onde mora a verdade de cada sistema + vocabulário
    + os espelhos de engenharia já sincronizados."""
    pdir = os.path.join(LAB, 'knowledge', 'projects')

    def safe(p):
        return read(p) if os.path.exists(p) else ''

    mirrors = []
    for f in sorted(list_md(pdir)):
        if f.startswith('_'):
            continue
        content = read(os.path.join(pdir, f))
        first = content.splitlines()[0] if content else ''
        mirrors.append({'slug': f[:-3], 'header': first, 'content': content})
    return {
        'fontes': safe(os.path.join(pdir, '_fontes.md')),
        'index': safe(os.path.join(pdir, '_index.md')),
        'vocab': safe(os.path.join(LAB, 'knowledge', 'vocabulario-pedro.md')),
        'mirrors': mirrors,
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        try:
            if url.path in ('/', '/index.html'):
                with open(os.path.join(UI_DIR, 'index.html'), 'rb') as f:
                    self._send(200, f.read(), 'text/html; charset=utf-8')
            elif url.path == '/api/overview':
                self._send(200, api_overview())
            elif url.path == '/api/updates':
                files = sorted(list_md(UPDATES), reverse=True)
                self._send(200, [{'file': f, 'title': first_heading(read(os.path.join(UPDATES, f)), f),
                                  'content': read(os.path.join(UPDATES, f))} for f in files])
            elif url.path == '/api/wiki':
                self._send(200, md_collection(os.path.join(LAB, 'knowledge', 'wiki'),
                                              'lab/knowledge/wiki'))
            elif url.path == '/api/skills':
                self._send(200, md_collection(os.path.join(LAB, 'skills'), 'lab/skills'))
            elif url.path == '/api/agents':
                header, rows = parse_tsv(os.path.join(LAB, 'agents', 'catalog.tsv'))
                self._send(200, {'header': header, 'rows': rows})
            elif url.path == '/api/scoreboard':
                header, rows = parse_tsv(os.path.join(LAB, 'scoreboard.tsv'))
                self._send(200, {'header': header, 'rows': rows})
            elif url.path == '/api/biblioteca':
                self._send(200, api_biblioteca())
            elif url.path == '/api/changelog':
                self._send(200, {'content': read(os.path.join(LAB, 'changelog.md'))})
            elif url.path == '/api/file':
                rel = q.get('path', [''])[0]
                self._send(200, {'path': rel, 'content': read(safe_path(rel))})
            else:
                self._send(404, {'error': 'rota desconhecida'})
        except PermissionError:
            self._send(403, {'error': 'caminho fora de lab/ e updates/'})
        except FileNotFoundError:
            self._send(404, {'error': 'arquivo não encontrado'})
        except Exception as e:  # noqa: BLE001 — UI local, erro vira JSON
            self._send(500, {'error': str(e)})

    def do_POST(self):
        if urlparse(self.path).path != '/api/toggle':
            return self._send(404, {'error': 'rota desconhecida'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            req = json.loads(self.rfile.read(length))
            code, body = toggle_pendencia(req)
            self._send(code, body)
        except Exception as e:  # noqa: BLE001
            self._send(500, {'error': str(e)})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(('', port), Handler)
    print(f'Cérebro UI: http://localhost:{port}  (lab/ e updates/ lidos ao vivo; Ctrl-C para sair)')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
