
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import zipfile
import io
import os

st.set_page_config(page_title="Conversor de Faturas", layout="wide")

st.title("📄 Conversor de Faturas - Excel/XML")
uploaded_file = st.file_uploader("Faça o upload de um arquivo Excel (.xlsx) ou ZIP contendo Excel/XML:", type=["xlsx", "zip"])

formato = st.radio("Escolha o formato de saída:", ["Excel (.xlsx)", "XML (.xml)"])

def processar_excel(df):
    # Remover duplicatas por UnidadeConsumidora + Data
    df = df.drop_duplicates(subset=["UnidadeConsumidora", "Data"])

    # Corrigir nome: se nome < 10, substituir por nome conhecido via CNPJ ou "NOME DESCONHECIDO"
    cnpj_col = next((col for col in df.columns if "cnpj" in col.lower()), None)
    if cnpj_col:
        cnpj_para_nome = {}
        for _, row in df.iterrows():
            nome = str(row["NomeTitular"]).strip()
            cnpj = str(row[cnpj_col]).strip()
            if len(nome) >= 10:
                cnpj_para_nome[cnpj] = nome

        def substituir_nome(row):
            nome = str(row["NomeTitular"]).strip()
            cnpj = str(row[cnpj_col]).strip()
            if len(nome) < 10:
                return cnpj_para_nome.get(cnpj, "NOME DESCONHECIDO")
            return nome

        df["NomeTitular"] = df.apply(substituir_nome, axis=1)
    return df

def gerar_xml(df):
    root = ET.Element("Faturas")
    for _, row in df.iterrows():
        fatura = ET.SubElement(root, "Fatura")
        for col in df.columns:
            valor = str(row[col])
            ET.SubElement(fatura, col).text = valor
    xml_bytes = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_bytes

if uploaded_file:
    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file) as z:
            nomes_arquivos = z.namelist()
            arquivos_excel = [n for n in nomes_arquivos if n.endswith(".xlsx")]
            if arquivos_excel:
                with z.open(arquivos_excel[0]) as f:
                    df = pd.read_excel(f)
            else:
                st.error("Nenhum arquivo .xlsx encontrado no .zip enviado.")
                st.stop()
    else:
        df = pd.read_excel(uploaded_file)

    df = processar_excel(df)

    st.success("Arquivo processado com sucesso!")

    if formato == "Excel (.xlsx)":
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 Baixar Excel", buffer.getvalue(), file_name="faturas_convertidas.xlsx")
    else:
        xml_bytes = gerar_xml(df)
        st.download_button("📥 Baixar XML", xml_bytes, file_name="faturas_convertidas.xml")
