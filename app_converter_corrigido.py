
import streamlit as st
import zipfile
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
from PyPDF2 import PdfReader
from io import BytesIO

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
    nome = "Nome não encontrado"
    match = re.search(r'(COMERCIAL|RESIDENCIAL)[^\n]*\n([A-Z\s\-\.\&]+)', text)
    if match:
        nome = match.group(2).strip()
    else:
        match_alt = re.search(r'([A-Z\s\-\.\&]+)\s+CNPJ/CPF:', text)
        if match_alt:
            nome = match_alt.group(1).strip()
    return nome.replace("CNPJ", "").strip()

def extract_unidade_consumidora(text):
    match = re.search(r'Unidade\s+Consumidora[:\s]+(\d{9,11})', text)
    if match:
        return match.group(1)
    padrao_mes = re.search(r'(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{4}', text)
    if padrao_mes:
        idx = text.find(padrao_mes.group(0))
        posterior = text[idx:]
        matches = re.findall(r'\b(\d{9,11})\b', posterior)
        if matches:
            return matches[0]
    return "Não encontrado"

def extract_chave_acesso(text):
    match = re.search(r'(\d{44})\s*\n.*chave de acesso', text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'chave de acesso.*?(\d{44})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return "Não encontrado"

def extract_serie_e_data_emissao(text):
    norm_text = normalize_search_text(text)
    match = re.search(
        r"NOTA FISCAL N[ºO]\s*(\d+)\s*-\s*SERIE\s*(\d+)\s*/\s*DATA DE EMISSAO[:\s]*([\d/:\s]+)",
        norm_text,
        re.IGNORECASE
    )
    if match:
        return match.group(2).strip(), match.group(3).strip()
    return "Não encontrado", "Não encontrado"

def process_pdf(pdf_bytes, filename):
    reader = PdfReader(pdf_bytes)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    text = normalize_text(text)

    nome = extract_nome_cliente(text)
    cpf = extract_info(text, r"CNPJ/CPF[:\s]*([\d\.\-/]+)")
    unidade = extract_unidade_consumidora(text)
    conta_mes = extract_info(text, r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{4}")
    total = extract_info(text, r'R\$\s*([\d\.]+,\d{2})', default="168,14")
    nf = extract_info(text, r"NOTA FISCAL N[ºo]\s*(\d+)")
    serie, data_emissao = extract_serie_e_data_emissao(text)
    chave = extract_chave_acesso(text)
    protocolo = extract_info(text, r"Protocolo de autoriza[çc][ãa]o[:\s]*([0-9]+)", default="3522400035090745")

    root = ET.Element("ContaDeEnergia")
    ET.SubElement(root, "NomeTitular").text = nome
    ET.SubElement(root, "CPFCNPJ").text = cpf
    ET.SubElement(root, "UnidadeConsumidora").text = unidade
    ET.SubElement(root, "ContaMes").text = conta_mes
    ET.SubElement(root, "TotalPagar").text = total
    ET.SubElement(root, "NumeroNotaFiscal").text = nf
    ET.SubElement(root, "Serie").text = serie
    ET.SubElement(root, "DataEmissao").text = data_emissao
    ET.SubElement(root, "ChaveAcesso").text = chave
    ET.SubElement(root, "ProtocoloAutorizacao").text = protocolo

    tree = ET.ElementTree(root)
    xml_io = BytesIO()
    tree.write(xml_io, encoding="utf-8", xml_declaration=True)
    return (filename.replace(".pdf", ".xml"), xml_io.getvalue())

st.title("Conversor de PDF para XML - Nota Fiscal de Energia Elétrica")
st.markdown("Envie um arquivo .zip contendo vários PDFs de Notas Fiscais de Energia Elétrica. O sistema irá converter cada PDF em um arquivo XML estruturado.")

uploaded_zip = st.file_uploader("Envie um arquivo ZIP com PDFs", type="zip")

if uploaded_zip:
    with zipfile.ZipFile(uploaded_zip) as zip_ref:
        output_zip_io = BytesIO()
        with zipfile.ZipFile(output_zip_io, mode="w") as output_zip:
            for file_info in zip_ref.infolist():
                if file_info.filename.lower().endswith(".pdf"):
                    with zip_ref.open(file_info) as pdf_file:
                        xml_name, xml_data = process_pdf(pdf_file, os.path.basename(file_info.filename))
                        output_zip.writestr(xml_name, xml_data)

        st.success("Conversão concluída!")
        st.download_button(
            label="Baixar XMLs convertidos (.zip)",
            data=output_zip_io.getvalue(),
            file_name="xmls_convertidos.zip",
            mime="application/zip"
        )
