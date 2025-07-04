import asyncio
import io
import boto3
import time
import pdf2image

from PIL import Image
from pathlib import Path
from botocore.client import Config
from langchain_core.documents import Document
from typing import Optional, cast

from langchain.text_splitter import RecursiveCharacterTextSplitter


def upload_pdf_to_s3(
    bucket_name: str,
    local_file_path: str,
    file_name: str
):
    s3_client = boto3.client(
        "s3",
        region_name="eu-west-1"
    )

    s3_client.upload_file(
        local_file_path,
        bucket_name,
        'documents/' + file_name
    )

    print(f"✅ Fichier uploadé sur s3://{bucket_name}/{'documents/' + file_name}")


async def _get_chunks_from_file(
    file_path
):
    textract_client_config = Config(
        retries={"max_attempts": 10}
    )
    textract_client = boto3.client(
        "textract",
        region_name="eu-west-1",
        config=textract_client_config
    )

    bucket_name = "bluegen-dev-blueaxel-documents"
    file_name = Path(file_path).name

    start = time.time()
    upload_pdf_to_s3(
        bucket_name=bucket_name,
        local_file_path=file_path,
        file_name=file_name
    )
    print(f"✅ Upload time: {time.time() - start:.2f} seconds.")

    start = time.time()
    r = textract_client.start_document_text_detection(
        DocumentLocation={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": 'documents/' + file_name
            }
        }
    )

    job_id = r["JobId"]
    print(f"Textract job started with ID: {job_id}")

    while True:
        result = textract_client.get_document_text_detection(
            JobId=job_id
        )
        status = result["JobStatus"]

        if status == "SUCCEEDED":
            break
        elif status == "FAILED":
            raise Exception("Le job a échoué")

        await asyncio.sleep(2)
    print(f"✅ Read time: {time.time() - start:.2f} seconds.")

    start = time.time()
    lines = [
        block["Text"]
        for block in result.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]
    page_text = "\n".join(lines)
    print(f"✅ Join time: {time.time() - start:.2f} seconds.")

    return page_text

# 26.16
# 24.65
# 22.65
# 42.45
# 200.87


async def run():
    start = time.time()
    global_doc = await _get_chunks_from_file("OCR/test/CRD S.pdf")

    print(global_doc[:100])

    print(f"Total processing time: {time.time() - start:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(run())
