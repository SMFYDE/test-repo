"""
"""


import asyncio
import io
import boto3
import time
import pdf2image

from PIL import Image
from pathlib import Path
from botocore.client import Config
from typing import Optional, cast

from langchain_core.documents import Document


async def _analyze_one_page(
    textract_client,
    image: Image.Image,
    page_number: int
) -> tuple[int, str]:
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")

    # response = textract_client.detect_document_text(
    #     Document={"Bytes": image_bytes.getvalue()}
    # )

    response = textract_client.start_document_text_detection(
        Document={
            "Bytes": image_bytes.getvalue()
        }
    )
    job_id = response["JobId"]

    lines = [
        block["Text"]
        for block in response.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]
    page_text = "\n".join(lines)

    return page_number, page_text


async def _get_chunks_from_file(file_path):
    """
    Extract text from a PDF file using AWS Textract and convert it into chunks.

    Args:
        file (ProcessedState): The file information containing the path and metadata.

    Returns:
        list[Document]: A list of Document objects containing the extracted text and metadata,
    """

    textract_client_config = Config(
        retries={
            "max_attempts": 10,
        }
    )
    textract_client = boto3.client(
        "textract", region_name="eu-west-1", config=textract_client_config
    )

    start = time.time()

    pdf_path = Path(file_path)

    images = pdf2image.convert_from_path(
        str(pdf_path),
    )

    document_text: list[Optional[str]] = [None] * len(images)

    # semaphore = asyncio.Semaphore(4)
    # tasks = [_analyze_one_page(textract_client, image, i) for i, image in enumerate(images, start=1)]
    # states = await asyncio.gather(*tasks)

    for i, image in enumerate(images, start=1):
        page_n, page_text = await _analyze_one_page(textract_client, image, i)
        document_text[page_n - 1] = page_text
        if page_n % 10 == 0:
            print(f"Processed {page_n} pages...")

    global_text = "\n\n".join(cast(list[str], document_text))
    global_doc = Document(
        page_content=global_text, metadata={"source": str(pdf_path)}
    )

    print()
    print(f"---> _get_chunks_from_file: {time.time() - start:.2f} seconds.")
    print()

    return global_doc


async def run():
    states = await _get_chunks_from_file("OCR/test/test.pdf")

    for state in states:
        global_doc = state
        print(f"Document source: {global_doc}")


if __name__ == "__main__":
    asyncio.run(run())
