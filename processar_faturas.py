
import pandas as pd
import re

# Caminho de entrada e saída
entrada = "faturas.xlsx"
saida = "faturas_corrigidas_sem_duplicatas.xlsx"

# Carregar planilha
df = pd.read_excel(entrada)

# Função para limpar os nomes
def limpar_nome(nome):
    if isinstance(nome, str):
        nome_limpo = re.sub(r'\b(COMERCIAL|NORMAL|CONVENCIONAL|CNPJ)\b', '', nome, flags=re.IGNORECASE)
        nome_limpo = nome_limpo.replace('\n', ' ').strip()
        nome_limpo = re.sub(r'\s{2,}', ' ', nome_limpo)
        return nome_limpo
    return nome

# Aplicar limpeza
df["NomeTitular"] = df["NomeTitular"].apply(limpar_nome)

# Remover duplicatas
df = df.drop_duplicates()

# Converter valores para float
df["TotalPagar"] = df["TotalPagar"].str.replace(",", ".").astype(float)

# Salvar nova planilha
df.to_excel(saida, index=False)
print(f"Arquivo salvo como: {saida}")
