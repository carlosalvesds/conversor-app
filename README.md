# Extrator de Notas Fiscais (Streamlit)

Este aplicativo Streamlit permite extrair dados específicos de arquivos PDF de notas fiscais de energia elétrica.

## ✅ Funcionalidades

- Upload de múltiplos arquivos `.pdf` ou um `.zip` contendo vários PDFs
- Extração automática de:
  - Nota Fiscal
  - Série
  - CNPJ
  - Valor (R$)
  - Data de Emissão
  - Nome do Destinatário
  - Protocolo de Autorização
  - Unidade Consumidora
  - Chave de Acesso
- Geração automática de um arquivo Excel formatado com os dados

## 🚀 Como executar localmente

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/extrator-notas-fiscais.git
cd extrator-notas-fiscais
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Rode o app:

```bash
streamlit run extrator_notas_fiscais.py
```

## 🌐 Deploy na Web

Você pode implantar este projeto gratuitamente usando [Streamlit Cloud](https://streamlit.io/cloud).

---

Desenvolvido com ❤️ usando Python + Streamlit.