import os
from database.mongodb import database
from fastapi import File, HTTPException, UploadFile
from llama_cpp import Optional
from rag.loadData import initialize_splitter, load_split_pdf_file
from services.bl import create_chat, create_issue, get_chats, get_issues, resolve_issue
from services.user import get_current_active_user
from rag.vectorDb import create_vector_db, load_local_db
from rag.load_llm import load_lamma_cpp
from common.function import read_file, load_yml_file, VECTOR_DB_MODEL_NAME

TEXT_SPLITTER = initialize_splitter(chunk_size = 1000, chunk_overlap = 100)

async def upload_file(file: UploadFile = File(...), collection_name : Optional[str] = "test_collection"):
  try:
      contents = file.file.read()
      fileName = file.filename.replace(' ', '_');
      if os.path.exists(f"rag-data/{fileName}"): 
        return {"fileExists": True }
      with open(f"rag-data/{fileName}", "wb") as f:
        f.write(contents)
  except Exception:
      return {"fileError": True}
  finally:
      file.file.close()

  try:
    await database().get_collection("Docs").insert_one({"collection_id": collection_name, "name": fileName})
    if fileName.endswith(".pdf"):
        data = load_split_pdf_file(f"rag-data/{fileName}", TEXT_SPLITTER)
        
    else:
        raise HTTPException(status_code=400, detail="Only pdf files are supported")
    
    db = create_vector_db(data, VECTOR_DB_MODEL_NAME, collection_name)
  except Exception:
    if os.path.exists(f"rag-data/{fileName}"): 
      os.remove(f"rag-data/{fileName}")
      database().get_collection("Docs").delete_one({"collection_id": collection_name})
    return {"success": False, "message": f"Error in creating vector db, {fileName}"}

  return {"success": True,
     "message": f"Successfully uploaded {fileName}", 
          "num_splits" : len(data)}


def get_collections(collection_name : Optional[str] = "test_collection"):
    try:
        collection_list = read_file("rag-data/COLLECTIONS.txt")
        collection_list = collection_list.split("\n")[:-1]
    except Exception:
        raise HTTPException("No collections found upload some documents first")

    if collection_name not in collection_list:
        raise HTTPException("There is no collection with name {collection_name}") 
    collection = load_local_db(collection_name)
    return collection


# Using the retriaval qa prompt template from the langchain library - https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/chains/retrieval_qa/prompt.py
def create_prompt(query, relevant_docs):
    relevant_text = ""
    relevant_docs = relevant_docs["documents"][0]
    for docs in (relevant_docs[0: 950] if len(relevant_docs) > 950 else relevant_docs):
      relevant_text += ("\n" + str(docs))
    
    prompt = f"""Use the following pieces of context to answer the question at the end. If you don"t know the answer, just say that you don"t know, don"t try to make up an answer. Do not repeat Helpfull Answer in the result.
      {relevant_text}
      Question: {query}?
      Helpful Answer:"""
    return prompt


async def get_existing_docs():
  list = []
  try:
    collection_list = read_file("rag-data/COLLECTIONS.txt")
    collection_list = collection_list.split("\n")[:-1]
    for i in collection_list:
        doc = await database().get_collection("Docs").find_one({"collection_id": i})
        list.append({"collection_id": i, "name": doc["name"]})
  except Exception:
      return []
  finally:
    return list



