import os,sys
import pathlib
import re

from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

DOCS_FOLDER='parsed_data'

name_filter = "**/*.md"
separator = "\n### "
chunk_size_limit = 3000
max_chunk_overlap = 0

main_path = pathlib.Path(DOCS_FOLDER)
document_files = list(main_path.glob(name_filter))

documents = [
    Document(
        page_content=open(file, "r").read(),
        metadata={"source": str(file).replace('parsed_data/','').replace('.md','')}
    )
    for file in document_files
]

text_splitter = CharacterTextSplitter(separator=separator, chunk_size=chunk_size_limit, chunk_overlap=max_chunk_overlap)
split_docs = text_splitter.split_documents(documents)


import tiktoken
# create a GPT-4 encoder instance
enc = tiktoken.encoding_for_model("gpt-4")

total_word_count = sum(len(doc.page_content.split()) for doc in split_docs)
total_token_count = sum(len(enc.encode(doc.page_content)) for doc in split_docs)

print(f"\nTotal word count: {total_word_count}")
print(f"\nEstimated tokens: {total_token_count}")
print(f"\nEstimated cost of embedding: ${total_token_count * 0.0004 / 1000}")

answer = input("Continue? [y/n] ")
if answer.upper() in ["Y", "YES"]:
    pass
elif answer.upper() in ["N", "NO"]:
    sys.exit(0)

print('\ngenerating vector store...')

from dotenv import load_dotenv
load_dotenv()

import os
from getpass import getpass

embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(split_docs, embeddings)

vector_store.save_local('vector_store')

print('vector store generated.\n')

