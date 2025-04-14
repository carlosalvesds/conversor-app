
import streamlit as st
import zipfile
import os
import tempfile
from PyPDF2 import PdfReader
import pandas as pd
import unicodedata
import re
from xml.etree.ElementTree import Element, SubElement, ElementTree
from io import BytesIO

# Funções utilitárias
def normalize_text(text):
    return unicodedata.normalize("NFKD", text)

def normalize_search_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("utf-8")
    return re.sub(r"\s+", " ", text).upper()

def extract_info(text, pattern, group=1, default="Não encontrado", flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else default

def extract_nome_cliente(text):
    match = re.search(r'(COMERCIAL|RESIDENCIAL)[^\n]*\n([A-Z\s\-\.\&]+)', text)
    if match:
        return match.group(2).strip()
    match_alt = re.search(r'([A-Z\s\-\.\&]+)\s+CNPJ/CPF:', text)
    if match_alt:
        return match_alt.group(1).strip()
    return "Nome não encontrado"

def extract_serie_e_data_emissao(text):
    norm = normalize_search_text(text)
    match = re.search(r"NOTA FISCAL N[ºO]\s*(\d+)\s*-\s*SERIE\s*(\d+)\s*/\s*DATA DE EMISSAO[:\s]*([\d/:\s]+)", norm)
    if match:
        return match.group(2).strip(), match.group(3).strip()
    alt_match = re.search(r'SERIE\s+0\s+/\s+DATA DE EMISSAO:\s*([\d/: ]+)', norm)
    if alt_match:
        return "0", alt_match.group(1).strip()
    return "Não encontrado", "Não encontrado"

def extract_chave_acesso_corrigida_flex(text):
    norm = normalize_search_text(text)
    match = re.search(r'(\d{44})\s*(?:CHAVE DE ACESSO|[\r\n]+CHAVE DE ACESSO)', norm)
    return match.group(1) if match else "Não encontrado"

def extract_protocolo_autorizacao_corrigido(text):
    norm = normalize_search_text(text)
    match = re.search(r'PROTOCOLO DE AUTORIZACAO[:\s\-]*([0-9]{10,20})', norm)
    return match.group(1) if match else "Não encontrado"

def extract_total_pagar_preciso(text):
    linhas = text.splitlines()
    for linha in linhas:
        match = re.search(r'R\$[*]+(\d{1,5},\d{2})', linha)
        if match:
            return match.group(1)
    for linha in linhas:
        if re.fullmatch(r'\d{1,5},\d{2}', linha.strip()):
            return linha.strip()
    valores = re.findall(r'\d{1,5},\d{2}', text)
    if valores:
        return max(valores, key=lambda v: float(v.replace(".", "").replace(",", ".")))
    return "Não encontrado"

# Função para processar PDF
def process_pdf_to_dict(file, filename):
    reader = PdfReader(file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    text = normalize_text(text)
    serie, data = extract_serie_e_data_emissao(text)
    return {
        "NomeTitular": extract_nome_cliente(text),
        "CPFCNPJ": extract_info(text, r"CNPJ/CPF[:\s]*([\d\.\-/]+)"),
        "UnidadeConsumidora": filename.replace(".pdf", ""),
        "ContaMes": extract_info(text, r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{4}"),
        "TotalPagar": extract_total_pagar_preciso(text),
        "NumeroNotaFiscal": extract_info(text, r"NOTA FISCAL N[ºo]?\s*(\d+)"),
        "Serie": serie,
        "DataEmissao": data,
        "ChaveAcesso": extract_chave_acesso_corrigida_flex(text),
        "ProtocoloAutorizacao": extract_protocolo_autorizacao_corrigido(text),
    }

def gerar_xml(info):
    root = Element("ContaDeEnergia")
    for key, value in info.items():
        SubElement(root, key).text = value
    xml_io = BytesIO()
    tree = ElementTree(root)
    tree.write(xml_io, encoding="utf-8", xml_declaration=True)
    return xml_io.getvalue()

# Streamlit App
st.title("Conversor de PDFs de Conta de Energia")
st.write("Escolha o formato de saída e envie seus arquivos PDF ou um .zip.")

formato = st.radio("Formato de saída:", ["XML", "Excel (.xlsx)"])

uploaded_file = st.file_uploader("Enviar PDF ou ZIP", type=["pdf", "zip"], accept_multiple_files=True)

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_paths = []
        for uf in uploaded_file:
            if uf.name.lower().endswith(".zip"):
                with zipfile.ZipFile(uf, "r") as z:
                    z.extractall(tmpdir)
                    for fname in z.namelist():
                        if fname.lower().endswith(".pdf"):
                            pdf_paths.append(os.path.join(tmpdir, fname))
            elif uf.name.lower().endswith(".pdf"):
                path = os.path.join(tmpdir, uf.name)
                with open(path, "wb") as f:
                    f.write(uf.read())
                pdf_paths.append(path)

        dados = []
        for path in pdf_paths:
            with open(path, "rb") as f:
                dados.append(process_pdf_to_dict(f, os.path.basename(path)))

        if formato == "XML":
            zip_io = BytesIO()
            with zipfile.ZipFile(zip_io, "w") as zf:
                for item in dados:
                    xml_bytes = gerar_xml(item)
                    zf.writestr(item["UnidadeConsumidora"] + ".xml", xml_bytes)
            st.download_button("📦 Baixar XMLs", data=zip_io.getvalue(), file_name="faturas_xml.zip")
        else:
            df = pd.DataFrame(dados)
            xlsx_io = BytesIO()
            df.to_excel(xlsx_io, index=False, engine="openpyxl")
            st.download_button("📥 Baixar Excel", data=xlsx_io.getvalue(), file_name="faturas.xlsx")
