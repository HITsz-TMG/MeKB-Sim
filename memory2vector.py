import faiss
import numpy as np
import json
from langchain.embeddings import HuggingFaceEmbeddings
import requests
import time
m3e_embedding_model = HuggingFaceEmbeddings(model_name='moka-ai/m3e-base')

def normalize_L2(x):
    return x / np.sqrt((x ** 2).sum(-1, keepdims=True))

with open('The_big_bang_theory.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

topic_list = []
for item in data:
    topic_list.append(item['topic'])


start = time.time()
topic_vectors = m3e_embedding_model.embed_documents(topic_list)
topics_normalized = normalize_L2(np.array(topic_vectors).astype('float32'))
end = time.time()
print(end-start)


d = topics_normalized.shape[1]  
index = faiss.IndexFlatIP(d)  
# print(d)

index.add(topics_normalized)
faiss.write_index(index, 'index.faiss')

