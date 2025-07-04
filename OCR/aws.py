""""
AWS textract service for OCR operations.
"""

import io
import time
import boto3
import pdf2image

from botocore.client import Config

from langchain_aws import BedrockEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
dpi = 200
fmt = 'png'
# print(f"config: dpi: {dpi} | fmt: {fmt}")
start = time.time()
pdf_path = "OCR/test/test.pdf"
images = pdf2image.convert_from_path(
    pdf_path,
    dpi=dpi,
)

# print(f"---> pdf2image.convert_from_path: {time.time() - start:.2f} seconds")

# ------------------------------------------------------------------------------------------------------------------------
start = time.time()


def get_document_text(image):
    for i, image in enumerate(images):
        print(f"--- Page {i+1}/{len(images)} ---")

        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")

        response = textract.detect_document_text(
            Document={
                'Bytes': image_bytes.getvalue()
            }
        )

        print(f"Response: {response}")
        print('\n')
        for BoundingBox in response['Blocks']:
            print(f"{BoundingBox}")
        print('\n')

        lines = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                lines.append(block['Text'])

    return '\n'.join(lines)


text = get_document_text(images)

global_doc = Document(
    page_content=text,
    metadata={'source': str(pdf_path)}
)
print(f"---> pdf2image.convert_from_path: {time.time() - start:.2f} seconds")
print(f"{text}")

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


