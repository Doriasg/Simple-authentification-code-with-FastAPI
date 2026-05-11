import os
from fastapi import APIRouter, HTTPException
from mistralai.client import Mistral
from app.schemas import PromptRequest
from app.schemas import DiseaseData
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS

router = APIRouter()

# Charger la base de documents au démarrage
embeddings = MistralAIEmbeddings(api_key=os.getenv("MISTRAL_API_KEY"))
vector_db = FAISS.load_local("faiss_rice_index", embeddings, allow_dangerous_deserialization=True)

# Initialisation du client Mistral
def get_mistral_client():
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    api_key = MISTRAL_API_KEY
    return Mistral(api_key=api_key)

router = APIRouter()

@router.post('/chatbot')
def chatbot(prompt_request: PromptRequest):
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    
    try:
        # --- PHASE RAG : Recherche de contexte ---
        # On cherche les 3 passages les plus pertinents dans vos documents
        docs = vector_db.similarity_search(prompt_request.prompt, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        # --- PHASE GENERATION : Réponse avec contexte ---
        system_prompt = (
            "Tu es un expert en riziculture au Bénin. Et tu maitrise les pathologies du riz. Utilise exclusivement les extraits "
            f"scientifiques suivants pour répondre :\n\n{context}\n\n"
            "Si la réponse n'est pas dans le texte, dis-le poliment. Ne fais aucune supposition. Sois précis et concis"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_request.prompt}
        ]

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages
        )
        
        return {"answer": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post('/recommandations')
def recommandations(disease_data: DiseaseData):
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    disease_name = disease_data.disease_name
    try:
        # --- PHASE RAG : Recherche de contexte ---
        # On cherche les 3 passages les plus pertinents dans vos documents
        docs = vector_db.similarity_search(disease_name, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])

        # --- PHASE GENERATION : Réponse avec contexte ---
        system_prompt = (
            "Tu es un expert en riziculture au Bénin. Et tu maitrise les pathologies du riz. Utilise exclusivement les extraits "
            f"scientifiques suivants pour répondre :\n\n{context}\n\n"
            "Si la réponse n'est pas dans le texte, dis-le poliment. Alors, formule des recommandations pour éradiquer contre cette maladie du riz sachant qu'une plante"
            " du champ est atteinte: {disease_name}. S'il y a des fongicides à recommander, mentionne-les."
            "Sois précis et concis dans tes réponses"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": disease_name}
        ]

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages
        )
        
        return {"answer": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))