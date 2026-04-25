# RAG

import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.tools.retriever import create_retriever_tool
from pinecone import Pinecone, ServerlessSpec

INDEX_NAME = "supply-chain-rag-index"
DATA_PATH = "./data/docs"
DIMENSION = 768
RAG_TOOL = None

def initialize_rag_system(data_path=DATA_PATH) -> PineconeVectorStore:
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )

    index = pc.Index(INDEX_NAME)
    stats = index.describe_index_stats()
    
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    # this (should ?) prevent any duplications from occurring

    vectorstore = None
    if stats['total_vector_count'] == 0:
        loader = DirectoryLoader(data_path, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(documents)
        
        vectorstore = PineconeVectorStore.from_documents(
            splits, 
            embeddings, 
            index_name=INDEX_NAME
        )
    else:
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=INDEX_NAME,
            embedding=embeddings
        )

    return vectorstore


def create_retriever_tool_for_agent(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    return create_retriever_tool(
        retriever,
        name = "search_knowledge_base",
        description=(
            "Search the internal knowledge base for information about "
            "supplier return policies, markdown authorization rules, "
            "disposal procedures, and product catalog details for specific SKUs. "
            "Use this when the user asks about what to do with dead or slow-moving stock, "
            "supplier options, or product-specific handling notes."
        ),
        
    )

@st.cache_resource
def get_rag_tool():
    return create_retriever_tool_for_agent(initialize_rag_system(DATA_PATH))