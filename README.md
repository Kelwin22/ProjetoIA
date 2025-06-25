# Contratus AI - Sistema de Consulta Semântica de Contratos

## 🔍 Visão Geral do Projeto

O **Contratus AI** é um sistema moderno para processamento e consulta inteligente de contratos imobiliários. Ele utiliza o poder dos Large Language Models (LLMs) e bancos de dados vetoriais para permitir busca semântica e responder a perguntas em linguagem natural diretamente do conteúdo de seus documentos.

### 🎯 Problema Resolvido

Em um cenário com múltiplos contratos complexos, encontrar informações específicas (como valores de aluguel, prazos de rescisão, nomes de partes) pode ser demorado e propenso a erros. O Contratus AI automatiza e agiliza essa busca, transformando seus contratos em uma base de conhecimento interativa.

## 🧠 Conceitos Fundamentais

Este projeto implementa a arquitetura de **Geração Aumentada por Recuperação (RAG - Retrieval-Augmented Generation)**:

### RAG (Retrieval-Augmented Generation)
É uma técnica que capacita um LLM a acessar e utilizar informações de uma base de conhecimento externa (neste caso, seus contratos PDF) para gerar respostas mais precisas, atualizadas e com citação de fontes, indo além do seu conhecimento de treinamento.

### Embeddings
São representações numéricas (vetores) de textos. Textos com significados semelhantes são transformados em vetores "próximos" em um espaço multidimensional. O modelo utilizado é o **Google Gemini (models/embedding-001)**, com dimensão 768.

### Banco de Dados Vetorial (Pinecone)
Uma base de dados otimizada para armazenar e realizar buscas de similaridade em alta velocidade entre vetores de embeddings. A métrica de similaridade utilizada é a **Cosseno**.

### Large Language Model (LLM)
O "cérebro" do sistema que compreende as perguntas e formula as respostas. O modelo utilizado é o **Google Gemini (models/gemini-1.5-flash)**.

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python** com **FastAPI** e **Uvicorn**
- **Pinecone** (cliente Python)
- **google-generativeai** (para Gemini)
- **langchain-community** (para processamento de PDFs)
- **python-dotenv**

### Frontend
- **SvelteKit**
- **Tailwind CSS**
- **DaisyUI**

## 📁 Estrutura do Projeto

```
├── .env                  # Variáveis de ambiente (chaves API, etc.)
├── api_pinecone.py       # API principal com FastAPI (busca semântica, LLM)
├── api_upload.py         # API para upload de contratos
├── llm_router.py         # Roteador para perguntas ao LLM
├── pinecone_utils.py     # Utilitários para interação com o Pinecone
├── processar_contrato.py # Script para processamento de PDFs
├── README.md             # Este arquivo
├── requirements.txt      # Dependências Python
├── shared.py             # Funções e modelos compartilhados
├── contratos/            # Diretório para armazenar os contratos PDF
└── frontend/             # Aplicação SvelteKit (interface do usuário)
```

## 🚀 Como Rodar o Projeto

### Pré-requisitos

Certifique-se de ter os seguintes softwares instalados:

- **Git**: Para clonar o repositório → [Baixar Git](https://git-scm.com/)
- **Python 3.11.9**: Versão recomendada → [Baixar Python](https://www.python.org/downloads/)
  - ⚠️ **IMPORTANTE**: Durante a instalação, marque "Add Python 3.11 to PATH"
- **Node.js LTS e npm**: Para o frontend → [Baixar Node.js](https://nodejs.org/)
  - ⚠️ **IMPORTANTE**: Certifique-se de que "Add to PATH" esteja selecionado

> **Nota para Windows/PowerShell**: Pode ser necessário ajustar a política de execução:
> ```powershell
> Set-ExecutionPolicy RemoteSigned
> ```

### 1. Configuração do Projeto

#### Clonar o Repositório
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd Contratus-AI-RAG
```

#### Configurar Variáveis de Ambiente
Crie um arquivo `.env` na pasta raiz com o seguinte conteúdo:

```env
# Configurações do Pinecone
PINECONE_API_KEY=SEU_VALOR_DA_PINECONE_API_KEY_AQUI
PINECONE_HOST=SEU_VALOR_DO_PINECONE_HOST_AQUI
PINECONE_INDEX_NAME=brito-ai

# Configurações do Google Gemini
GOOGLE_API_KEY=SUA_CHAVE_DO_GEMINI_AQUI
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_CHAT_MODEL=models/gemini-1.5-flash
```

#### Como obter as chaves:
- **Pinecone**: Acesse [pinecone.io](https://pinecone.io) → API Keys
- **Google Gemini**: Acesse [Google AI Studio](https://aistudio.google.com) → Get API Key

#### Criar o Índice no Pinecone
No painel do Pinecone, crie um índice com as configurações:
- **Name**: `brito-ai`
- **Dimension**: `768` 
- **Metric**: `Cosine`
- **Pod Type**: Starter (para contas gratuitas)

### 2. Instalação de Dependências

#### Dependências Python
```bash
py -3.11 -m pip install -r requirements.txt
py -3.11 -m pip install google-generativeai
```

#### Dependências Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Processar os Contratos

1. Coloque seus arquivos PDF na pasta `contratos/`
2. Execute o processamento:
```bash
py -3.11 processar_contrato.py
```

### 4. Rodando a Aplicação

Você precisará de **3 terminais** abertos simultaneamente:

#### Terminal 1: API Principal (Porta 8000)
```bash
py -3.11 -m uvicorn api_pinecone:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2: API de Upload (Porta 8001) - Opcional
```bash
py -3.11 -m uvicorn api_upload:app --host 127.0.0.1 --port 8001 --reload
```

#### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

### 5. Usando a Aplicação

1. Acesse a URL fornecida pelo Terminal 3 (geralmente `http://localhost:5173`)
2. Ative o "Modo Pergunta" na interface
3. Digite sua pergunta em linguagem natural:
   - *"Qual o valor do aluguel do contrato do Bruno Mendes Oliveira?"*
   - *"Quais são os termos de rescisão para o contrato da Ana Carolina Silva?"*
4. Clique em "Buscar"

O sistema buscará nos seus contratos e o Google Gemini gerará uma resposta detalhada com citações das fontes.

## 🔧 Solução de Problemas

### Erros Comuns

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError` | Execute `py -3.11 -m pip install -r requirements.txt` |
| `PINECONE_API_KEY não encontrada` | Verifique se o arquivo `.env` está na pasta raiz |
| `Reason: Forbidden / Wrong API key` | Confirme suas credenciais do Pinecone no `.env` |
| `Vector dimension 768 does not match 1536` | Recrie o índice Pinecone com dimensão 768 |
| `npm não reconhecido` | Instale o Node.js LTS e reinicie o terminal |

## 📝 Licença

Este projeto está sob a licença [MIT](LICENSE).

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

---

**Desenvolvido com ❤️ usando RAG + Google Gemini + Pinecone**
