from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_function():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # embeddings= BedrockEmbeddings(credentials_profile_name="bedrock-admin", region_name="us-east-1")
    return embeddings


