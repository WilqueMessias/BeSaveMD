# pdf_styles.py
# Centraliza os estilos CSS usados na geração de PDFs.

CSS_STYLE = """
<style>
    @page {
        size: A4;
        margin: 1.5cm;
    }
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 10pt;
        line-height: 1.6;
        color: #1a1a1a;
    }
    h1 {
        font-size: 28pt;
        font-weight: bold;
        color: #000;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    h2 {
        font-size: 14pt;
        color: #000;
        border-bottom: 1px solid #ddd;
        padding-bottom: 4px;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h3 {
        font-size: 11pt;
        color: #333;
        margin-top: 12px;
        margin-bottom: 4px;
        font-weight: bold;
    }
    .about-section {
        background-color: #f9f9f9;
        padding: 10px 15px;
        border-left: 4px solid #333;
        margin-bottom: 20px;
        font-style: italic;
    }
    p {
        margin: 6px 0;
    }
    a {
        text-decoration: none;
        color: #000;
        border-bottom: 1px solid #ccc;
    }
    ul {
        margin: 5px 0;
        padding-left: 20px;
    }
    li {
        margin-bottom: 4px;
    }
    img {
        height: 14px;
        vertical-align: middle;
    }
    div[align="center"] {
        text-align: center;
        margin-bottom: 30px;
    }
</style>
"""