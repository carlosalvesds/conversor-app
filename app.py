
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import fitz  # PyMuPDF
import zipfile

st.set_page_config(page_title="Conversor PDF/ZIP ➡️ Excel/XML", layout="wide")
st.title("📄 Conversor de Faturas (PDF ou ZIP ➡️ Excel/XML)")

uploaded_file = st.file_uploader("Faça o upload de um arquivo PDF ou ZIP contendo faturas:", type=["pdf", "zip"])
formato = st.radio("Escolha o formato de saída:", ["Excel (.xlsx)", "XML (.xml)"])

def extrair_dados_pdf(pdf_bytes):
    texto_completo = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for pagina in doc:
            texto_completo += pagina.get_text()

    # Simulação da extração – ajustar conforme estrutura real dos PDFs
    dados = []
    nfe, data, total, uc, protocolo, nome = "", "", "", "", "", ""
    linhas = texto_completo.splitlines()
    for linha in linhas:
        if "NFe" in linha or "Chave" in linha:
            nfe = linha.strip()
        elif "Data" in linha:
            data = linha.strip().split()[-1]
        elif "Valor Total" in linha:
            total = linha.strip().split()[-1].replace("R$", "").replace(",", ".")
        elif "Unidade Consumidora" in linha:
            uc = linha.strip().split()[-1]
        elif "Protocolo" in linha:
            protocolo = linha.strip().split()[-1]
        elif "Nome" in linha and len(linha.split()) > 2:
            nome = linha.strip()

    dados.append({
        "NumeroNota": nfe,
        "Data": data,
        "TotalPagar": total,
        "UnidadeConsumidora": uc,
        "Protocolo": protocolo,
        "NomeTitular": nome,
    })

    return pd.DataFrame(dados)

def gerar_xml(df):
    root = ET.Element("Faturas")
    for _, row in df.iterrows():
        fatura = ET.SubElement(root, "Fatura")
        for col in df.columns:
            valor = str(row[col])
            ET.SubElement(fatura, col).text = valor
    return ET.tostring(root, encoding="utf-8", method="xml")

def processar_entrada(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extrair_dados_pdf(uploaded_file.read())
    elif uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file, "r") as z:
            pdf_files = [f for f in z.namelist() if f.endswith(".pdf")]
            if not pdf_files:
                st.warning("Nenhum arquivo PDF encontrado no ZIP.")
                return pd.DataFrame()
            frames = []
            for file_name in pdf_files:
                with z.open(file_name) as pdf:
                    frames.append(extrair_dados_pdf(pdf.read()))
            return pd.concat(frames, ignore_index=True)
    else:
        st.warning("Formato de arquivo não suportado.")
        return pd.DataFrame()

if uploaded_file:
    try:
        df = processar_entrada(uploaded_file)
        if df.empty:
            st.error("Nenhum dado foi extraído.")
        else:
            st.success("Arquivo processado com sucesso!")

            if formato == "Excel (.xlsx)":
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False)
                st.download_button("📥 Baixar Excel", buffer.getvalue(), file_name="faturas_convertidas.xlsx")
            else:
                xml_bytes = gerar_xml(df)
                st.download_button("📥 Baixar XML", xml_bytes, file_name="faturas_convertidas.xml")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
