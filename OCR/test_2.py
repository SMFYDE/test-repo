""""
AWS textract service for OCR operations.
"""

import io
from pathlib import Path
import time
import boto3
import pdf2image
import concurrent

from botocore.client import Config

from langchain.schema import Document
from langchain_aws import BedrockEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


# BlueAxel
# ---> pdf2image.convert_from_path: 8.52 seconds.
# ---> _get_chunks_from_file: 29.51 seconds.
# ---> _split_document_into_chunks: 0.00 seconds.

# Ici
# ---> pdf2image.convert_from_path: 1.41 seconds.
# ---> _get_chunks_from_file: 22.59 seconds.
# ---> _split_document_into_chunks: 0.02 seconds.

# Embedding client configuration
embedding_client_config = Config(
    retries={
        'max_attempts': 40,
        'mode': 'adaptive'
    },
    connect_timeout=40,
    max_pool_connections=100
)
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    config=embedding_client_config
)
embedding = BedrockEmbeddings(
    client=bedrock_client,
    model_id='amazon.titan-embed-text-v2:0',
    region_name='us-east-1',
)

# Textract client configuration
config = Config(retries=dict(max_attempts=10))
textract = boto3.client("textract", region_name="eu-west-1", config=config)

# ------------------------------------------------------------------------------------------------------------------------
start = time.time()
pdf_path = "OCR/test/24. Fiche CARD-i Saint-Clar-de-Rivière.pdf"
images = pdf2image.convert_from_path(
    pdf_path,
)

end = time.time()
print(f"---> pdf2image.convert_from_path: {end - start:.2f} seconds")

# ------------------------------------------------------------------------------------------------------------------------
start = time.time()


def _analyze_page(textract_client, image, page_number):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')

    response = textract_client.detect_document_text(
        Document={'Bytes': image_bytes.getvalue()}
    )

    lines = [
        block['Text']
        for block in response.get('Blocks', [])
        if block['BlockType'] == 'LINE'
    ]
    page_text = '\n'.join(lines)

    return page_number, page_text


start = time.time()

document_text = [None] * len(images)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(_analyze_page, textract, image, i)
        for i, image in enumerate(images, start=1)
    ]
    for future in concurrent.futures.as_completed(futures):
        page_number, page_text = future.result()
        document_text[page_number - 1] = page_text
        if page_number % 10 == 0:
            print(f'Processed {page_number} pages...')

global_text = '\n\n'.join(document_text)
global_doc = Document(
    page_content=global_text,
    metadata={'source': str(pdf_path)}
)
end = time.time()
print(f"---> _get_chunks_from_file: {end - start:.2f} seconds.")

# ------------------------------------------------------------------------------------------------------------------------
start = time.time()
text_splitter = RecursiveCharacterTextSplitter(
    separators=['\n\n', '\n', '.', ' ', ''],
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
chunks = text_splitter.split_documents([global_doc])
end = time.time()
print(f"---> _split_document_into_chunks: {end - start:.2f} seconds")

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1}/{len(chunks)} ---")
    print(chunk.page_content[:100])

# 1.09 + 7.90
