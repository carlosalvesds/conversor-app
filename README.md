
# 📊 Streamlit Faturas App

Uma aplicação web feita com [Streamlit](https://streamlit.io/) para processar faturas em Excel, limpar os dados, remover duplicatas e permitir o download no formato `.xlsx` ou `.xml`.

---

## 🚀 Funcionalidades

- Upload de arquivos `.xlsx` com colunas como `NomeTitular`, `TotalPagar`, etc.
- Limpeza automática dos nomes dos titulares (remove palavras como COMERCIAL, CNPJ, etc).
- Conversão de valores para número (`TotalPagar`).
- Remoção de linhas duplicadas.
- Download do resultado em `.xlsx` ou `.xml`, conforme escolha do usuário.

---

## 🛠️ Como rodar localmente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/streamlit-faturas.git
cd streamlit-faturas
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

3. Rode o app:
```bash
streamlit run app.py
```

---

## ☁️ Implantação no Streamlit Cloud

1. Crie um repositório com `app.py` e `requirements.txt`
2. Acesse [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecte ao GitHub e selecione o repositório
4. Escolha `app.py` como arquivo principal e clique em **Deploy**

---

## 📂 Exemplo de estrutura do repositório

```
streamlit-faturas/
│
├── app.py
├── requirements.txt
└── README.md
```

---

Desenvolvido com ❤️ usando Python + Streamlit.
