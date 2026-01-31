# BeSaveMD

<p align="center">
  <strong>Conversão bidirecional Markdown ↔ PDF</strong><br>
  Para qualquer documento: currículos, artigos, relatórios e mais.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.0+-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/API--first-REST-00A67E?logo=api" alt="API-first">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

<p align="center">
  <a href="#-sobre">Sobre</a> •
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#-tecnologias">Tecnologias</a> •
  <a href="#-instalação">Instalação</a> •
  <a href="#-uso">Uso</a> •
  <a href="#-api">API</a> •
  <a href="#-estrutura-do-projeto">Estrutura</a> •
  <a href="#-documentação">Documentação</a> •
  <a href="#-autor">Autor</a>
</p>

---

## Sobre

**BeSaveMD** é um sistema de conversão **MD ↔ PDF** pensado para uso em qualquer tipo de documento: currículos, artigos, relatórios, documentação técnica, etc. Você pode usar pela **interface web** (drag & drop), pela **linha de comando** ou pela **API REST**, com o mesmo contrato para web, Android e iOS (API-first).

- **MD → PDF**: Markdown vira HTML e depois PDF (xhtml2pdf), com CSS para A4 e opções como tech badges e seção “About Me” estilizada.
- **PDF → MD**: PDF é analisado com PyMuPDF; heurísticas de tamanho de fonte, negrito/itálico e listas geram Markdown.

---

## Funcionalidades

| Recurso | Descrição |
|--------|------------|
| **Conversão MD → PDF** | Upload de `.md` → download de PDF com tipografia e margens A4 |
| **Conversão PDF → MD** | Upload de `.pdf` → download de Markdown reconstruído (headers, listas, formatação) |
| **Interface web** | Uma página com abas, drag & drop e feedback visual |
| **CLI** | Scripts para terminal: `convert_md_to_pdf.py` e `pdf_engine.py` |
| **API REST** | Endpoints `/api/convert` e `/api/convert-to-md` para integração (web, mobile, scripts) |
| **Validação** | Extensão e tamanho (até 10 MB) validados no backend |
| **API-first** | Um contrato, várias frentes (site, Android, iOS) |

---

## Tecnologias

- **Backend**: [Python](https://www.python.org/) 3.8+, [Flask](https://flask.palletsprojects.com/)
- **Conversão MD→HTML**: [Markdown](https://python-markdown.github.io/) (extensões `extra`, `codehilite`)
- **Conversão HTML→PDF**: [xhtml2pdf](https://xhtml2pdf.readthedocs.io/) (pisa)
- **Conversão PDF→MD**: [PyMuPDF](https://pymupdf.readthedocs.io/) (fitz)
- **Frontend**: HTML, CSS, JavaScript (vanilla), drag & drop

---

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- `pip`

### Passos

```bash
# Clone o repositório
git clone https://github.com/WilqueMessias/BeSaveMD.git
cd BeSaveMD

# Crie um ambiente virtual (recomendado)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

---

## Uso

### Interface web

```bash
python app.py
```

Acesse **http://localhost:5050**. Use as abas **MD para PDF** e **PDF para MD**, arraste o arquivo ou clique para selecionar.

### Linha de comando

**Markdown → PDF**

```bash
python convert_md_to_pdf.py documento.md [saida.pdf]
# Saída opcional; padrão: mesmo nome com .pdf
```

**PDF → Markdown**

```bash
python pdf_engine.py documento.pdf [saida.md]
# Saída opcional; padrão: mesmo nome com .md
```

### Windows (atalho)

```bash
start_app.bat
```

Inicia o servidor Flask na porta 5050.

---

## API

O backend é **API-first**: os mesmos endpoints servem a interface web e clientes externos (apps, scripts).

| Endpoint | Método | Descrição | Request | Response (sucesso) | Erro |
|----------|--------|-----------|---------|--------------------|------|
| `/api/convert` | POST | MD → PDF | `multipart/form-data`, campo `file` (`.md`) | 200 + PDF (binary) | 400/500 + JSON `{"error": "..."}` |
| `/api/convert-to-md` | POST | PDF → MD | `multipart/form-data`, campo `file` (`.pdf`) | 200 + MD (binary) | 400/500 + JSON `{"error": "..."}` |

- **Limite de upload**: 10 MB  
- **Base URL**: onde o backend estiver (ex.: `https://seu-dominio.com`)  
- **Exemplo (curl)**:

```bash
# MD → PDF
curl -X POST -F "file=@documento.md" http://localhost:5050/api/convert -o saida.pdf

# PDF → MD
curl -X POST -F "file=@documento.pdf" http://localhost:5050/api/convert-to-md -o saida.md
```

Documentação detalhada da API: [docs/API.md](docs/API.md).

---

## Estrutura do projeto

```
BeSaveMD/
├── app.py                 # Servidor Flask: rotas web + API
├── convert_md_to_pdf.py    # CLI: Markdown → PDF
├── pdf_engine.py          # Motor PDF → Markdown (PyMuPDF)
├── requirements.txt      # Dependências Python
├── start_app.bat          # Atalho para iniciar o servidor (Windows)
├── templates/
│   └── index.html         # Interface web (abas, drag & drop)
├── .cursor/rules/         # Regras do projeto (API-first, convenções)
├── docs/                  # Documentação
│   ├── API.md             # Documentação completa da API
│   ├── INSTALACAO.md      # Guia de instalação e execução
│   └── ARQUITETURA.md     # Arquitetura e decisões
└── README.md              # Este arquivo
```

---

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/API.md](docs/API.md) | Contrato da API, exemplos de request/response, códigos de erro |
| [docs/INSTALACAO.md](docs/INSTALACAO.md) | Instalação passo a passo, ambientes virtuais, troubleshooting |
| [docs/ARQUITETURA.md](docs/ARQUITETURA.md) | Visão geral da arquitetura, fluxos MD↔PDF, API-first |

---

## Autor

**Wilque Messias**

- GitHub: [@WilqueMessias](https://github.com/WilqueMessias)
- Repositório: [BeSaveMD](https://github.com/WilqueMessias/BeSaveMD)

Projeto desenvolvido como ferramenta de conversão de documentos e demonstração de API-first (web + CLI + API).

---

## Licença

Uso livre para estudo e adaptação. Documentos pessoais não são versionados (veja `.gitignore`).
