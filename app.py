
import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Função para limpar nomes
def limpar_nome(nome):
    if isinstance(nome, str):
        nome_limpo = re.sub(r'\b(COMERCIAL|NORMAL|CONVENCIONAL|CNPJ)\b', '', nome, flags=re.IGNORECASE)
        nome_limpo = nome_limpo.replace('\n', ' ').strip()
        nome_limpo = re.sub(r'\s{2,}', ' ', nome_limpo)
        return nome_limpo
    return nome

# Interface Streamlit
st.title("Processador de Faturas (.xlsx)")

uploaded_file = st.file_uploader("Envie o arquivo .xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Limpeza e processamento
    df["NomeTitular"] = df["NomeTitular"].apply(limpar_nome)
    df = df.drop_duplicates()
    df["TotalPagar"] = df["TotalPagar"].astype(str).str.replace(",", ".").astype(float)

    st.success("Arquivo processado com sucesso!")
    st.dataframe(df.head())

    # Baixar como Excel
    output_excel = BytesIO()
    df.to_excel(output_excel, index=False, engine='openpyxl')
    output_excel.seek(0)
    st.download_button(
        label="📥 Baixar Excel Corrigido (.xlsx)",
        data=output_excel,
        file_name="faturas_corrigidas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Baixar como XML simples
    import xml.etree.ElementTree as ET

    def df_para_xml(dataframe):
        root = ET.Element("Faturas")
        for _, row in dataframe.iterrows():
            fatura = ET.SubElement(root, "Fatura")
            for col in dataframe.columns:
                child = ET.SubElement(fatura, col)
                child.text = str(row[col])
        return ET.tostring(root, encoding="utf-8", method="xml")

    output_xml = df_para_xml(df)
    st.download_button(
        label="📥 Baixar como XML",
        data=output_xml,
        file_name="faturas_corrigidas.xml",
        mime="application/xml"
    )
