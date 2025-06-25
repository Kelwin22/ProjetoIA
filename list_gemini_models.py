import google.generativeai as genai
import os
from dotenv import load_dotenv

# Obtém o caminho absoluto do diretório atual
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Carrega as variáveis de ambiente do arquivo .env no diretório atual
env_path = os.path.join(diretorio_atual, '.env')
load_dotenv(dotenv_path=env_path)

# LÊ A CHAVE DIRETAMENTE DO AMBIENTE CARREGADO PELO dotenv
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configura o SDK do Google Gemini com a chave de API
# Garante que a chave seja passada para a configuração
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("ERRO: GOOGLE_API_KEY não encontrada no arquivo .env ou não carregada.")
    exit()

# Lista os modelos e filtra os que suportam 'generateContent'
print("Modelos disponíveis para generateContent:")
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Erro ao listar modelos: {e}")