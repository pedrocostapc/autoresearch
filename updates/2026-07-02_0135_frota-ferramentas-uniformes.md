# Frota — painel de ferramentas uniforme + documentado

As 4 máquinas da frota (M1, M3, Ryzen5, 3060ti) agora rodam o MESMO painel de extração (2026-07-02).
Documentei o painel completo em `lab/knowledge/wiki/frota-de-maquinas.md` §2b: o que cada ferramenta faz
(pymupdf, pdfplumber, pypdfium2, markitdown, pdftotext, camelot, docling + OCR: Apple Vision/easyocr/
tesseract/paddleocr), a regra de leitura, e como instalar.

Consertos de hoje: (1) M1 rodava venv pobre (ocr-venv, 3 engines) → apontado pro frota-venv (completo).
(2) pdftotext faltava nos Macs → instalado via MICROMAMBA (Homebrew precisa sudo, trava por SSH; micromamba
não precisa). Melhoria pendente anotada: a decisão de OCR do worker é frágil ("any engine >40 chars" —
uma engine ruidosa engana e pula OCR num PDF vetorial); o certo é consenso.
