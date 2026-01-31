# Guia de instalação e execução — BeSaveMD

Este guia descreve como instalar e rodar o BeSaveMD no seu ambiente (Windows, Linux ou macOS).

---

## Pré-requisitos

- **Python 3.8 ou superior**  
  Verifique: `python --version` ou `python3 --version`
- **pip** (geralmente já vem com o Python)  
  Verifique: `pip --version`

---

## Instalação passo a passo

### 1. Clonar o repositório

```bash
git clone https://github.com/WilqueMessias/BeSaveMD.git
cd BeSaveMD
```

### 2. (Recomendado) Criar ambiente virtual

**Windows (PowerShell ou CMD):**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Com o ambiente ativado, o prompt deve mostrar algo como `(venv)` no início.

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Dependências principais:

- `flask` — servidor web
- `markdown` — conversão MD → HTML
- `xhtml2pdf` — conversão HTML → PDF
- `PyMuPDF` (fitz) — leitura e análise de PDF

### 4. Rodar o servidor web

```bash
python app.py
```

Saída esperada (ou similar):

```
--- STARTING APP ---
 * Running on http://127.0.0.1:5050
```

Acesse no navegador: **http://localhost:5050**

### 5. (Opcional) Usar linha de comando

Sem iniciar o servidor, você pode converter arquivos pelo terminal:

**Markdown → PDF:**

```bash
python convert_md_to_pdf.py documento.md
# ou com nome de saída explícito:
python convert_md_to_pdf.py documento.md saida.pdf
```

**PDF → Markdown:**

```bash
python pdf_engine.py documento.pdf
# ou com nome de saída explícito:
python pdf_engine.py documento.pdf saida.md
```

---

## Windows: atalho

Na pasta do projeto, execute:

```bash
start_app.bat
```

Isso inicia o servidor Flask na porta 5050. Abra o navegador em http://localhost:5050.

---

## Porta e host

Por padrão o Flask roda em `http://127.0.0.1:5050`. Para mudar a porta ou expor para a rede:

Edite no final de `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=False, port=5050, host='0.0.0.0')  # 0.0.0.0 = aceitar conexões de outras máquinas
```

Ou defina variáveis de ambiente antes de rodar:

```bash
# Linux/macOS
export FLASK_RUN_PORT=8080
export FLASK_RUN_HOST=0.0.0.0
python app.py
```

(No código atual, `port=5050` está fixo em `app.run`; para usar variáveis de ambiente seria preciso alterar o script.)

---

## Possíveis problemas

### "No module named 'flask'" (ou markdown, xhtml2pdf, fitz)

- Certifique-se de ter ativado o ambiente virtual (`venv\Scripts\activate` no Windows, `source venv/bin/activate` no Linux/macOS).
- Rode novamente: `pip install -r requirements.txt`

### "Address already in use"

- A porta 5050 está em uso. Feche o outro processo que a usa ou mude a porta em `app.py` (ex.: `port=5051`).

### Erro ao converter PDF → MD

- Alguns PDFs são só imagem (escaneados) ou têm layout muito atípico; a reconstrução em Markdown é heurística e pode falhar ou ficar imperfeita. Para PDFs “normais” (texto selecionável), o resultado costuma ser bom.

### Upload muito grande

- O limite é 10 MB. Arquivos maiores retornam erro 413. O valor está em `app.py` em `MAX_CONTENT_LENGTH`.

---

## Resumo

| Ação | Comando |
|------|---------|
| Instalar dependências | `pip install -r requirements.txt` |
| Subir servidor web | `python app.py` |
| Acessar interface | http://localhost:5050 |
| CLI: MD → PDF | `python convert_md_to_pdf.py arquivo.md [saida.pdf]` |
| CLI: PDF → MD | `python pdf_engine.py arquivo.pdf [saida.md]` |
