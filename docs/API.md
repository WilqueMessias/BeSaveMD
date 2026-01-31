# Documentação da API — BeSaveMD

A API do BeSaveMD é **REST**, com dois endpoints para conversão de documentos. O mesmo contrato serve a interface web e clientes externos (Android, iOS, scripts).

---

## Base URL

Onde o backend estiver rodando, por exemplo:

- Local: `http://localhost:5050`
- Produção: `https://seu-dominio.com`

---

## Autenticação

Atualmente a API **não exige autenticação**. Em produção, considere adicionar API key ou JWT conforme sua necessidade.

---

## Limites

| Item | Valor |
|------|--------|
| Tamanho máximo do arquivo | 10 MB |
| Encoding | UTF-8 (MD e PDF) |
| Formato do body | `multipart/form-data` |

---

## Endpoints

### 1. MD → PDF

Converte um arquivo Markdown (`.md`) em PDF.

**Endpoint:** `POST /api/convert`

**Request**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `file` | arquivo | sim | Arquivo `.md` (Markdown) |

**Exemplo (curl)**

```bash
curl -X POST \
  -F "file=@documento.md" \
  http://localhost:5050/api/convert \
  -o saida.pdf
```

**Exemplo (JavaScript / fetch)**

```javascript
const formData = new FormData();
formData.append('file', arquivoMd); // File object

const response = await fetch('http://localhost:5050/api/convert', {
  method: 'POST',
  body: formData
});

if (response.ok) {
  const blob = await response.blob();
  // download ou uso do PDF
} else {
  const json = await response.json();
  console.error(json.error);
}
```

**Response (sucesso)**

| Código | Conteúdo | Headers |
|--------|----------|---------|
| 200 | PDF em binário | `Content-Type: application/pdf`, `Content-Disposition: attachment; filename="nome.pdf"` |

O nome do arquivo de saída segue o nome do arquivo enviado, trocando a extensão por `.pdf`.

**Response (erro)**

| Código | Conteúdo | Situação |
|--------|----------|----------|
| 400 | `{"error": "No file part"}` | Campo `file` não enviado |
| 400 | `{"error": "No selected file"}` | Arquivo vazio ou sem nome |
| 400 | `{"error": "Arquivo deve ser .md"}` | Extensão diferente de `.md` |
| 413 | (resposta do servidor) | Arquivo maior que 10 MB |
| 500 | `{"error": "mensagem"}` | Erro interno (ex.: falha ao gerar PDF) |

---

### 2. PDF → MD

Converte um arquivo PDF em Markdown.

**Endpoint:** `POST /api/convert-to-md`

**Request**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `file` | arquivo | sim | Arquivo `.pdf` |

**Exemplo (curl)**

```bash
curl -X POST \
  -F "file=@documento.pdf" \
  http://localhost:5050/api/convert-to-md \
  -o saida.md
```

**Exemplo (Python / requests)**

```python
import requests

url = "http://localhost:5050/api/convert-to-md"
with open("documento.pdf", "rb") as f:
    files = {"file": ("documento.pdf", f, "application/pdf")}
    r = requests.post(url, files=files)

if r.ok:
    with open("saida.md", "wb") as out:
        out.write(r.content)
else:
    print(r.json().get("error"))
```

**Response (sucesso)**

| Código | Conteúdo | Headers |
|--------|----------|---------|
| 200 | Conteúdo Markdown (texto) | `Content-Type: text/markdown`, `Content-Disposition: attachment; filename="nome.md"` |

O nome do arquivo de saída segue o nome do PDF enviado, trocando a extensão por `.md`.

**Response (erro)**

| Código | Conteúdo | Situação |
|--------|----------|----------|
| 400 | `{"error": "No file part"}` | Campo `file` não enviado |
| 400 | `{"error": "No selected file"}` | Arquivo vazio ou sem nome |
| 400 | `{"error": "Arquivo deve ser .pdf"}` | Extensão diferente de `.pdf` |
| 413 | (resposta do servidor) | Arquivo maior que 10 MB |
| 500 | `{"error": "mensagem"}` | Erro interno (ex.: PDF corrompido ou não suportado) |

---

## Resumo do contrato

| Endpoint | Método | Campo | Extensão | Sucesso (200) | Erro (4xx/5xx) |
|----------|--------|-------|----------|---------------|----------------|
| `/api/convert` | POST | `file` | `.md` | PDF binary | JSON `{"error": "..."}` |
| `/api/convert-to-md` | POST | `file` | `.pdf` | MD (text) | JSON `{"error": "..."}` |

Clientes (web, Android, iOS) devem usar exatamente esse contrato para manter a interface consistente entre plataformas.
