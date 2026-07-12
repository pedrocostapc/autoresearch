#!/usr/bin/env bash
# lab-sync.sh <slug>
#
# Copia o CLAUDE.md (ou AGENTS.md) do repositório atual para o espelho do
# cérebro em ~/Dev/autoresearch/lab/knowledge/projects/<slug>.md, com um
# cabeçalho de data + commit. Zero IA, zero token — é só cópia. Rode de dentro
# do repo do projeto.
#
# Uso:   bash ~/Dev/autoresearch/lab/bin/lab-sync.sh <slug>
#   ex.: bash ~/Dev/autoresearch/lab/bin/lab-sync.sh ai-connect
set -euo pipefail

SLUG="${1:?uso: lab-sync.sh <slug>   (ex.: ai-connect, supersec, newrisenos, risencore, pedro-obras)}"
BRAIN="$HOME/Dev/autoresearch/lab/knowledge/projects"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if   [ -f "$ROOT/CLAUDE.md" ];  then SRC="$ROOT/CLAUDE.md"
elif [ -f "$ROOT/AGENTS.md" ];  then SRC="$ROOT/AGENTS.md"
else
  echo "erro: não achei CLAUDE.md nem AGENTS.md na raiz ($ROOT)." >&2
  echo "Escreva o doc de contexto do projeto primeiro, depois rode o sync." >&2
  exit 1
fi

mkdir -p "$BRAIN"
COMMIT="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo 'sem-git')"
BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '?')"
DATE="$(date '+%Y-%m-%d %H:%M')"

{
  echo "<!-- ESPELHO automático — NÃO editar aqui. Fonte: $SRC"
  echo "     sync: $DATE | branch: $BRANCH | commit: $COMMIT -->"
  echo
  cat "$SRC"
} > "$BRAIN/$SLUG.md"

echo "✓ sincronizado: $SRC  →  $BRAIN/$SLUG.md  ($DATE, commit $COMMIT)"
