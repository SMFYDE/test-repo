import asyncio
import time
import boto3
from pathlib import Path
from botocore.client import Config


def upload_pdf_to_s3(
    bucket_name: str,
    local_file_path: str,
    file_name: str
):
    s3_key = f"documents/{file_name}"

    s3_client = boto3.client(
        "s3",
        region_name="eu-west-1"
    )
    s3_client.upload_file(
        local_file_path,
        bucket_name,
        s3_key
    )

    print(f"✅ Upload: s3://{bucket_name}/{s3_key}")
    return s3_key


def wait_for_textract_job(textract_client, job_id):
    while True:
        result = textract_client.get_document_text_detection(
            JobId=job_id
        )
        status = result["JobStatus"]

        if status == "SUCCEEDED":
            return
        elif status == "FAILED":
            raise Exception("Le job Textract a échoué")

        time.sleep(2)


def get_all_lines(textract_client, job_id):
    lines = []
    next_token = None

    while True:
        kwargs = {"JobId": job_id}
        if next_token:
            kwargs["NextToken"] = next_token

        result = textract_client.get_document_text_detection(**kwargs)

        for block in result["Blocks"]:
            if block["BlockType"] == "LINE":
                lines.append(block["Text"])

        next_token = result.get("NextToken")
        if not next_token:
            break

    return "\n".join(lines)


async def _get_chunks_from_file(file_path: str):
    bucket_name = "bluegen-dev-blueaxel-documents"
    file_name = Path(file_path).name

    s3_key = upload_pdf_to_s3(
        bucket_name,
        file_path,
        file_name
    )

    textract_client = boto3.client(
        "textract",
        region_name="eu-west-1",
        config=Config(retries={"max_attempts": 10})
    )

    response = textract_client.start_document_text_detection(
        DocumentLocation={
            "S3Object": {
                "Bucket": bucket_name,
                "Name": s3_key
            }
        }
    )
    job_id = response["JobId"]
    print(f"🚀 Job lancé : {job_id}")

    await asyncio.to_thread(wait_for_textract_job, textract_client, job_id)
    text = await asyncio.to_thread(get_all_lines, textract_client, job_id)

    return text

# 44.42
# 20.32
# 46.16
# 62.16
# 27.82

# ! Mais du coup c'est complètement instable
# ! Qu'est ce qu'on fait du coup ?


async def run():
    start = time.time()
    text = await _get_chunks_from_file("OCR/test/CRD S.pdf")
    print(text[:500])
    print(f"✅ Total processing time: {time.time() - start:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(run())
