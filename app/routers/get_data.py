from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

router= APIRouter()
def build_knowledge_base():
    # 1. Charger tous les PDFs du dossier "data_agri"
    print("Chargement des documents...")
    loader = DirectoryLoader('./data', glob="./*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    
    # 2. Découpage intelligent
    # chunk_overlap permet de ne pas couper une phrase explicative importante entre deux morceaux
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(docs)
    
    # 3. Création des vecteurs
    print(f"Indexation de {len(chunks)} segments de texte...")
    embeddings = MistralAIEmbeddings(api_key=os.getenv("MISTRAL_API_KEY"))
    vector_db = FAISS.from_documents(chunks, embeddings)
    
    # 4. Sauvegarde
    vector_db.save_local("faiss_rice_index")
    print("Base de connaissances prête !")

if __name__ == "__main__":
    build_knowledge_base()
