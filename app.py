
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import fitz  # PyMuPDF

st.set_page_config(page_title="Conversor PDF para Excel/XML", layout="wide")

st.title("📄 Conversor de Faturas (PDF ➡️ Excel/XML)")
uploaded_file = st.file_uploader("Faça o upload de um arquivo PDF contendo a fatura:", type=["pdf"])

formato = st.radio("Escolha o formato de saída:", ["Excel (.xlsx)", "XML (.xml)"])

def extrair_dados_pdf(pdf_bytes):
    texto_completo = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for pagina in doc:
            texto_completo += pagina.get_text()

    # Simulação da extração – ajustar conforme estrutura real dos PDFs
    dados = []
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
        "NumeroNota": nfe if 'nfe' in locals() else '',
        "Data": data if 'data' in locals() else '',
        "TotalPagar": total if 'total' in locals() else '',
        "UnidadeConsumidora": uc if 'uc' in locals() else '',
        "Protocolo": protocolo if 'protocolo' in locals() else '',
        "NomeTitular": nome if 'nome' in locals() else '',
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

if uploaded_file:
    try:
        df = extrair_dados_pdf(uploaded_file.read())
        st.success("PDF processado com sucesso!")

        if formato == "Excel (.xlsx)":
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            st.download_button("📥 Baixar Excel", buffer.getvalue(), file_name="fatura_convertida.xlsx")
        else:
            xml_bytes = gerar_xml(df)
            st.download_button("📥 Baixar XML", xml_bytes, file_name="fatura_convertida.xml")
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
