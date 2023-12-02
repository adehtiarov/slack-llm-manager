import json

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain import PromptTemplate, LLMChain, OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

def get_documents():
    with open("bugs-platform-history-processed.json", "r") as f:
        data = json.load(f)
    docs = []
    for i in range(0, len(data), 3):
        docs.append(str(data[i:i+3])) # Group threads into 3s, as sometimes users reply outside of the thread
    return [Document(page_content=doc) for doc in docs]

chat = OpenAI(temperature=0)
print(str(chat))

chain = load_summarize_chain(chat, chain_type="map_reduce")
print(str(chain))

docs = get_documents()
reduced_docs = [] 
invocations = 3
for i in range(0, len(docs), 3):
    interim = chain.run(docs[i:i+3])
    reduced_docs.append(Document(page_content=interim))
    invocations -= 1
    if invocations == 0:
        break

print(chain.run(reduced_docs))
