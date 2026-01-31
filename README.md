# BeSaveMD

Sistema de conversão bidirecional **Markdown ↔ PDF** para qualquer documento (currículos, artigos, relatórios, etc.).

- **MD → PDF**: Markdown vira HTML e depois PDF (xhtml2pdf). Inclui opcionalmente tech badges e seção "About Me" estilizada.
- **PDF → MD**: PDF analisado com PyMuPDF; heurísticas de fonte e layout geram Markdown.

## Como rodar

### Dependências

```bash
pip install flask markdown xhtml2pdf PyMuPDF
```

Ou use um `requirements.txt` (crie com as dependências acima).

### Servidor web (Flask)

```bash
python app.py
```

Acesse `http://localhost:5050`. Interface: abas "MD para PDF" e "PDF para MD", drag & drop.

### Linha de comando

**MD → PDF:**

```bash
python convert_md_to_pdf.py documento.md [documento.pdf]
```

**PDF → MD:**

```bash
python pdf_engine.py documento.pdf [documento.md]
```

## API (web, Android, iOS)

Backend é **API-first**. Mesmo contrato para todos os clientes:

| Endpoint            | Método | Request                          | Response (sucesso) | Erro        |
|---------------------|--------|----------------------------------|--------------------|-------------|
| `/api/convert`       | POST   | `multipart/form-data`, campo `file` (.md)  | 200 + PDF binary   | 400/500 JSON `{"error": "..."}` |
| `/api/convert-to-md`| POST   | `multipart/form-data`, campo `file` (.pdf) | 200 + MD binary    | 400/500 JSON `{"error": "..."}` |

- Limite de upload: 10 MB.
- Base URL: onde o backend estiver (ex.: `https://seu-dominio.com`).

## Estrutura

| Arquivo / pasta      | Função |
|----------------------|--------|
| `app.py`             | Flask: rotas web e `/api/convert`, `/api/convert-to-md` |
| `pdf_engine.py`      | Conversão PDF → Markdown (PyMuPDF) |
| `convert_md_to_pdf.py` | Script CLI MD → PDF |
| `templates/index.html` | Interface web |

## Subir para o repositório (BeSaveMD)

Repositório: [github.com/WilqueMessias/BeSaveMD](https://github.com/WilqueMessias/BeSaveMD)

```bash
# Adicionar remote (se ainda não tiver)
git remote add besavemd https://github.com/WilqueMessias/BeSaveMD.git

# Ou trocar a origem para BeSaveMD
git remote set-url origin https://github.com/WilqueMessias/BeSaveMD.git

# Commit das alterações (README, .gitignore, regras, CLI com argparse)
git add .gitignore README.md requirements.txt .cursor app.py convert_md_to_pdf.py pdf_engine.py templates
git status   # conferir — documentos pessoais não devem aparecer
git commit -m "BeSaveMD: conversor MD↔PDF para qualquer documento, API-first"

# Enviar para o repositório
git push -u origin main
```

Documentos pessoais ficam fora do repositório (`.gitignore`); só o sistema é versionado.

## Licença

Use e adapte como quiser. Documentos pessoais não vão no repositório (veja `.gitignore`).
