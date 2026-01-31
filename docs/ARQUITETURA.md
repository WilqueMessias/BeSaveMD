# Arquitetura — BeSaveMD

Este documento descreve a arquitetura do BeSaveMD: fluxos de conversão, organização do código e decisão API-first.

---

## Visão geral

O BeSaveMD é um sistema de conversão **bidirecional** entre Markdown e PDF:

1. **MD → PDF**: Markdown é convertido em HTML (biblioteca Markdown) e depois em PDF (xhtml2pdf). Inclui pré-processamento opcional (tech badges, seção “About Me”).
2. **PDF → MD**: O PDF é analisado com PyMuPDF (fitz); heurísticas de tamanho de fonte, negrito/itálico e posição dos blocos geram Markdown.

O backend é **API-first**: a mesma lógica de conversão é usada pela interface web, pela API REST e (indiretamente) pelos scripts de linha de comando. Assim, web, Android e iOS podem compartilhar o mesmo contrato.

---

## Fluxo MD → PDF

```
[Arquivo .md]
      ↓
  Leitura (UTF-8)
      ↓
  Pré-processamento (opcional: tech_badge_preprocessor, seção About Me)
      ↓
  markdown.markdown() → HTML
      ↓
  Injeção de CSS (A4, tipografia)
      ↓
  xhtml2pdf (pisa) → PDF em memória
      ↓
[Resposta: PDF binary ou erro JSON]
```

- **Entrada**: texto Markdown (string ou arquivo).
- **Saída**: bytes do PDF (envio como arquivo ou stream).
- **Onde está**: `app.py` (`_md_to_pdf_bytes`), `convert_md_to_pdf.py` (CLI que lê arquivo e chama lógica equivalente).

---

## Fluxo PDF → MD

```
[Arquivo .pdf]
      ↓
  Leitura (bytes) → arquivo temporário (PyMuPDF exige path)
      ↓
  PDFReconstructor (pdf_engine.py):
    - analyze_fonts() → identifica “body” por tamanho de fonte mais frequente
    - Por página: blocos ordenados (Y, X), merge de blocos próximos
    - Por bloco: header level por ratio de tamanho, listas por caractere/posição, negrito/itálico por nome da fonte
      ↓
  Saída: string Markdown
      ↓
[Resposta: MD (text) ou erro JSON]
```

- **Entrada**: bytes do PDF (ou path para arquivo temporário).
- **Saída**: string Markdown.
- **Onde está**: `pdf_engine.py` (classe `PDFReconstructor`, método `convert()`), `app.py` (`_pdf_to_md_bytes` que usa arquivo temporário e `os.unlink`).

A conversão é **heurística**: funciona bem para PDFs com texto selecionável e estrutura “normal”; PDFs só imagem ou layout muito atípico podem dar resultado imperfeito.

---

## Organização do código

| Componente | Arquivo(s) | Responsabilidade |
|------------|------------|-------------------|
| Servidor web + API | `app.py` | Rotas `/`, `/convert`, `/convert-to-md`, `/api/convert`, `/api/convert-to-md`; validação de extensão e tamanho; chamada às funções de conversão. |
| Lógica MD → PDF | `app.py` (`_md_to_pdf_bytes`, `tech_badge_preprocessor`, CSS) | Pré-processamento, Markdown→HTML, HTML→PDF. |
| Lógica PDF → MD | `pdf_engine.py` | Análise de fontes, blocos, headers, listas, formatação → Markdown. |
| CLI MD → PDF | `convert_md_to_pdf.py` | Argumentos (entrada/saída), leitura do .md, geração do PDF (usa próprio CSS ou poderia importar de app). |
| CLI PDF → MD | `pdf_engine.py` (`__main__`) | Argumentos (entrada/saída), chamada a `PDFReconstructor`. |
| Interface web | `templates/index.html` | Abas “MD para PDF” / “PDF para MD”, drag & drop, form que envia para `/convert` ou `/convert-to-md`. |

A lógica de conversão fica **no backend**; a interface web e os clientes da API apenas enviam arquivos e exibem o resultado (ou erro). Nenhuma regra de negócio de conversão fica no frontend.

---

## API-first

- **Contrato único**: Os endpoints `/api/convert` e `/api/convert-to-md` têm request (multipart `file`) e response (binary ou JSON `{"error": "..."}`) definidos e documentados em [API.md](API.md).
- **Um backend, vários clientes**: O mesmo backend atende:
  - Interface web (form POST para `/convert` e `/convert-to-md`).
  - Clientes externos (Android, iOS, scripts) via `/api/convert` e `/api/convert-to-md`.
- **CLI**: Os scripts `convert_md_to_pdf.py` e `pdf_engine.py` usam a mesma lógica (ou equivalente) que o servidor, mas rodam localmente sem HTTP; não duplicam regras, apenas expõem a mesma capacidade via terminal.

Ao adicionar funcionalidade nova (ex.: novo formato ou opção de layout), o fluxo recomendado é: definir contrato → implementar no backend (funções reutilizáveis) → expor na API e, se fizer sentido, na web e no CLI.

---

## Segurança e limites

- **Upload**: Extensão validada no backend (apenas `.md` em `/api/convert` e `.convert`, apenas `.pdf` em `/api/convert-to-md` e `/convert-to-md`). Tamanho máximo 10 MB (`MAX_CONTENT_LENGTH`).
- **Arquivos temporários**: PDF→MD usa `tempfile.NamedTemporaryFile` e `os.unlink` após uso, evitando `temp_{filename}` e riscos de path traversal ou conflito de nomes.
- **Erros**: Em rotas de API, erros retornam JSON `{"error": "..."}`; em rotas web, retornam texto. Não se expõe stack trace ao cliente.

---

## Dependências principais

- **Flask**: servidor HTTP e rotas.
- **Markdown**: conversão MD → HTML (extensões `extra`, `codehilite`).
- **xhtml2pdf (pisa)**: HTML → PDF.
- **PyMuPDF (fitz)**: leitura e análise de PDF (fontes, blocos, texto).

Todas estão listadas em `requirements.txt`.
