from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
import os
import time
from shared import buscar_contratos # Importação de shared para modelos de dados, etc.
from pinecone_utils import buscar_documentos # Importação para a busca semântica

router = APIRouter()

# Configura o SDK do Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Define o modelo de chat do Gemini, com um fallback se a variável de ambiente não for encontrada
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "models/gemini-1.5-flash") # Ajustado para o modelo validado

# Configura o SDK do Gemini com a chave API
genai.configure(api_key=GOOGLE_API_KEY)
# Inicializa o modelo de chat do Gemini
gemini_model = genai.GenerativeModel(GEMINI_CHAT_MODEL)

class QuestionRequest(BaseModel):
    question: str
    max_results: int = 50

class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Responde a perguntas sobre contratos usando o LLM com base nos resultados da busca semântica."""
    start_time = time.time()
    
    try:
        # Validação básica da pergunta
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia")
            
        print(f"[LLM] Recebida pergunta: '{request.question}' (max_results={request.max_results})")
        
        # 1. Busca direta no Pinecone usando a função buscar_documentos
        # IMPORTANTE: Contornando a função buscar_contratos para evitar incompatibilidade de formatos
        # A importação de buscar_documentos já está no topo, mas deixei o comentário para contexto.
        
        print(f"[LLM] Realizando busca semântica direta...")
        try:
            # Busca direta nos documentos (agora async)
            documentos = await buscar_documentos(request.question, request.max_results)
            
            # Verifica se há resultados
            if not documentos or len(documentos) == 0:
                print(f"[LLM] Nenhum documento relevante encontrado.")
                raise HTTPException(status_code=404, detail="Nenhum documento relevante encontrado.")
            
            print(f"[LLM] Encontrados {len(documentos)} documentos relevantes.")
        except Exception as e:
            print(f"[LLM] Erro na busca semântica: {type(e).__name__} - {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar a consulta de busca: {str(e)}")
        
        # 3. Prepara contexto para o LLM diretamente dos documentos encontrados
        context = "\n\n".join(
            f"[Documento {i+1} - {doc['arquivo']}]\n{doc['texto']}"
            for i, doc in enumerate(documentos)
        )

        # 4. Geração da resposta com o LLM
        print(f"[LLM] Gerando resposta com o modelo {GEMINI_CHAT_MODEL}...")

        answer = "Não foi possível obter uma resposta do modelo." # Valor padrão
        try:
            # Prepara a parte 'system' como a primeira parte do prompt do usuário
            system_instruction = (
                "Você é um assistente especializado em contratos imobiliários com acesso a uma base de documentos. "
                "Suas respostas devem ser:\n"
                "1. DETALHADAS - Forneça informações completas e abrangentes sobre o que foi perguntado.\n"
                "2. ESPECÍFICAS - Quando a pergunta for sobre pessoas, entidades ou cláusulas, inclua TODOS os detalhes disponíveis nos documentos.\n"
                "3. ESTRUTURADAS - Organize a resposta de forma clara, usando listas ou seções quando apropriado.\n"
                "4. BASEADAS EM EVIDÊNCIAS - Cite explicitamente de qual documento/contrato a informação foi extraída.\n"
                ". Cite explicitamente codigos de barras, caso as informações sejam de boletos de cobrança."
            )

            # Monta o prompt completo para o Gemini, incluindo o contexto dos documentos e a pergunta
            full_prompt = f"{system_instruction}\n\nDocumentos:\n{context}\n\nPergunta: {request.question}"

            # Chama a API do Gemini
            resposta_final = await gemini_model.generate_content(
                contents=[
                    {"role": "user", "parts": [{"text": full_prompt}]}
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5
                )
            )

            # --- Início do tratamento robusto da resposta do Gemini ---
            if resposta_final.text:
                answer = resposta_final.text
            elif resposta_final.parts: # Se .text não funcionar, tente iterar pelas partes
                answer = "".join([part.text for part in resposta_final.parts if hasattr(part, 'text')])
                if not answer: # Se ainda assim não houver texto nas partes
                    print("[LLM] Aviso: Resposta do Gemini contém partes, mas sem texto válido.")
            else:
                # Caso a resposta não tenha texto nem partes de texto
                print("[LLM] Aviso: Resposta do Gemini não contém texto. Verificando bloqueios...")
                if resposta_final.prompt_feedback and resposta_final.prompt_feedback.block_reason:
                    block_reason = resposta_final.prompt_feedback.block_reason.name
                    answer = f"A resposta não pôde ser gerada devido a filtros de segurança do modelo. Motivo: {block_reason}"
                    print(f"[LLM] Resposta BLOQUEADA por motivo: {block_reason}")
                else:
                    answer = "Não foi possível gerar uma resposta detalhada do modelo. Resposta vazia ou inesperada."
                    print("[LLM] Aviso: Resposta do Gemini vazia ou em formato inesperado.")
            # --- Fim do tratamento robusto da resposta do Gemini ---

        except Exception as e:
            # Registra o erro de forma mais detalhada para depuração
            print(f"[LLM] Erro na geração da resposta com Gemini (Tipo da Exceção: {type(e).__name__}): {e}")
            # Em caso de erro na geração, ainda tentamos retornar uma mensagem de erro genérica.
            answer = "Ocorreu um erro interno ao gerar a resposta com o modelo."
            raise HTTPException(status_code=500, detail=answer) # Retorna a mensagem de erro específica

        # 5. Prepara e retorna a resposta diretamente dos documentos
        response = {
            "answer": answer,
            "sources": [{
                "filename": doc["arquivo"],
                "text": doc["texto"]
            } for doc in documentos]
        }
        
        elapsed_time = time.time() - start_time
        print(f"[LLM] Resposta gerada em {elapsed_time:.2f} segundos.")
        
        return response
        
    except HTTPException as e:
        # Repassa exceções HTTP
        raise
    except Exception as e:
        print(f"[LLM] Erro inesperado ao processar pergunta (Tipo da Exceção: {type(e).__name__}): {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")
