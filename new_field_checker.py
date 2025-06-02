from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import faiss
import numpy as np
import re

# ------------ Configuration ------------
STANDARD_FIELDS_PATH = 'standard_fields.txt'
SIMILARITY_THRESHOLD = 0.6

# ------------ User Input Model ------------
class HtmlRequest(BaseModel):
    html: str

# ------------ Dummy Embedding Function (Replace with Actual) ------------
def get_danske_embedding(text: str) -> np.ndarray:
    np.random.seed(hash(text) % 2**32)
    return np.random.rand(384).astype('float32')  # Must return float32 numpy array

# ------------ Field Utilities ------------
def extract_standard_fields(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(.*?)\nClass:.*?\n(<div.*?</div>)', re.DOTALL)
    fields = pattern.findall(content)

    standard_fields = []
    for field_name, html in fields:
        standard_fields.append((field_name.strip(), html.strip()))
    return standard_fields

def extract_div_blocks(html_content):
    div_blocks = []
    stack = []
    current_div = ''
    inside_div = False

    lines = html_content.split('\n')
    for line in lines:
        stripped = line.strip()
        if '<div' in stripped:
            if not inside_div:
                current_div = ''
                stack = []
                inside_div = True
            stack.append('div')
        if inside_div:
            current_div += line + '\n'
        if '</div>' in stripped:
            if stack:
                stack.pop()
            if not stack:
                div_blocks.append(current_div.strip())
                inside_div = False
    return div_blocks

def build_faiss_index(standard_fields):
    dim = len(get_danske_embedding("test"))
    index = faiss.IndexFlatL2(dim)
    embeddings = []
    names = []
    html_map = []

    for name, html in standard_fields:
        emb = get_danske_embedding(name)
        embeddings.append(emb)
        names.append(name)
        html_map.append(html)

    embedding_matrix = np.vstack(embeddings).astype('float32')
    index.add(embedding_matrix)

    return index, html_map, names, embedding_matrix

def replace_fields(ai_html, index, html_map, threshold=SIMILARITY_THRESHOLD):
    div_blocks = extract_div_blocks(ai_html)
    replaced_html = ai_html

    for block in div_blocks:
        match = re.search(r'<label.*?>(.*?)</label>', block)
        label = match.group(1).strip() if match else block[:50]
        query_emb = get_danske_embedding(label).astype('float32').reshape(1, -1)

        D, I = index.search(query_emb, 1)
        distance = D[0][0]
        best_idx = I[0][0]

        similarity = 1 / (1 + distance)

        if similarity >= threshold:
            std_html = html_map[best_idx]
            replaced_html = replaced_html.replace(block, std_html)

    return replaced_html

# ------------ FastAPI Server ------------
app = FastAPI()

# Global objects (initialized on startup)
standard_fields = []
faiss_index = None
html_map = []

@app.on_event("startup")
def startup_event():
    global standard_fields, faiss_index, html_map
    standard_fields = extract_standard_fields(STANDARD_FIELDS_PATH)
    faiss_index, html_map, _, _ = build_faiss_index(standard_fields)
    print("FAISS index loaded with", len(standard_fields), "standard fields.")

@app.post("/standardize-form/")
def standardize_form(data: HtmlRequest):
    modified_html = replace_fields(data.html, faiss_index, html_map)
    return {"modified_html": modified_html}
