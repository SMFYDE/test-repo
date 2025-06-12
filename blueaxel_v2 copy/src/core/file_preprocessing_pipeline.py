"""
File Preprocessing Pipeline for BlueAxel V2
"""


import boto3
import botocore

from typing import Any, Callable, List, Dict, Optional, TypedDict
from pathlib import Path

from chainlit import AskFileMessage
from chainlit import Message as cl_Message
from chainlit.types import AskFileResponse

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_aws import BedrockEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from agents.certifluid.utils.utils_processing_image import pdf_to_image_files


class ProcessedState(TypedDict):
    file_name: str  # The name of the file
    file_path: str  # The path to the file
    file_type: str  # The MIME type of the file, e.g., "application/pdf"
    file_size: int  # The size of the file in bytes
    file_category: str  # The category of the file, e.g., "kbis", "insee_file", etc.
    vector_store: FAISS  # The vector store created from the file's content
    chunks: Optional[dict[str, Any]]  # Additional extracted information from the file, e.g., text chunks
    logs: Dict  # Logs generated during processing


class FilePreprocessingPipeline:
    def __init__(
        self,
        full_name: str,
        debug: bool = True
    ) -> None:
        """
        Goal of this class is to catch and preprocess documents.
        Then create a vector store from the documents using the specified embedding model.

        Args:
            full_name (str): The full name of the user for identification in messages.
        """
        self.debug = debug
        self.full_name = full_name

        client_config = botocore.config.Config(
            retries={
                'max_attempts': 40,  # number of retries
                'mode': 'adaptive'  # Backoff exponentiel adaptatif
            },
            connect_timeout=40,
            max_pool_connections=100
        )
        bedrock_client = boto3.client(
            'bedrock-runtime', region_name='us-east-1', config=client_config
        )
        self.embedding = BedrockEmbeddings(
            client=bedrock_client,
            model_id='amazon.titan-embed-text-v2:0',
            region_name='us-east-1',
        )

    async def _request_user_for_analysis_files(
        self
    ) -> List[AskFileResponse]:
        """
        Request the user to upload files for analysis.

        Returns:
            List[AskFileResponse]: A list of files uploaded by the user.
        """
        files = AskFileMessage(
            content="Rajouter des fichiers PDF pour l'analyse.",
            accept=['application/pdf'],
            author=self.full_name,
            max_files=12,
            max_size_mb=100,
            timeout=480000,
        )
        files = await files.send()
        if not files:
            raise ValueError('No files were provided')

        status_msg = cl_Message(
            content='I have the files, I will now analyze them.',
            author=self.full_name,
        )
        await status_msg.send()
        return files

    async def preprocess_one_file(
        self,
        file: ProcessedState
    ) -> ProcessedState:
        """
        Preprocess a single file by extracting text and creating a vector store.

        Args:
            file (AskFileResponse): File information object.

        Returns:
            ProcessedState: A processed state with vector store.
        """
        chunks = await self._get_chunks_from_file(file)

        # build vector store from chunks
        vector_store = FAISS.from_documents(
            chunks,
            self.embedding
        )

        print()
        print()
        print("TENTATIVE ICI")
        print()
        print()

        # ? Techniquement ca fonctionne mais j'ai des erreurs de text c'est bizarre

        import pytesseract
        print(pytesseract)

        # ! a enlever pour deployer
        pytesseract.pytesseract.tesseract_cmd = r"C:/Users/ydefontaine/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"

        pdf_paths = ["bluegen/agents/blueaxel_v2/data_tests/24. Fiche CARD-i Saint-Clar-de-Rivière.pdf"]
        image_files = await pdf_to_image_files(pdf_paths)
        print(f"Processed images: {image_files}")

        texts = []

        # call an OCR function on each image
        for image_path in image_files:
            print(f"Processing image: {image_path}")
            try:
                text = pytesseract.image_to_string(image_path)
                texts.append(text)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

        print()
        for i, text in enumerate(texts):
            print(f"Text from image {i + 1}:")
            print(text)
            print("-" * 40)
        print()
        print()
        print()


        # ### PREPROCESSING TEXT ### #
        # This is a test, no idea if it will work or be useful
        # How will I retrieve the data if I remove the data here?

        # for chunk in chunks:
        #     chunk.page_content = chunk.page_content.lower()
        #     chunk.page_content = re.sub(
        #         r"[^\w\s.,:;/-]",
        #         '',
        #         chunk.page_content
        #     )  # remove special characters except for .,;:/- which are useful in text
        #     chunk.page_content = re.sub(
        #         r"page \d+/\d+",
        #         '',
        #         chunk.page_content
        #     )  # text like "page 1/3" is not useful
        #     chunk.page_content = re.sub(
        #         r"\d{6,}",
        #         '<NUM>',
        #         chunk.page_content
        #     )  # long number (RCS, SIREN, etc.)
        #     chunk.page_content = re.sub(
        #         r"\d{2}/\d{2}/\d{4}",
        #         '<DATE>',
        #         chunk.page_content
        #     )  # Dates
        #     chunk.page_content = re.sub(
        #         r"\d{2}:\d{2}:\d{2}",
        #         '<HOURS>',
        #         chunk.page_content
        #     )  # Hours

        ############################

        return ProcessedState(
            file_name=file['file_name'],
            file_path=file['file_path'],
            file_type=file['file_type'],
            file_size=file['file_size'],
            vector_store=vector_store,
            chunks=chunks,
            logs={},
        )

    def _split_documents_into_chunks(
        self,
        documents: Document
    ) -> Document:
        """
        Split documents into smaller chunks for preprocessing.

        Args:
            documents (Iterable[Document]): The documents to process.

        Returns:
            List[Document]: A list of processed document chunks.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ' ', ''],
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # If a single document is provided, convert it to a list
        if isinstance(documents, Document):
            documents = [documents]

        processed_documents = text_splitter.split_documents(documents)
        return processed_documents

    def _get_file_type_loader(
        self,
        file: ProcessedState
    ) -> Optional[Callable[[], Any]]:
        """
        Get the appropriate document loader based on the file type.

        Args:
            file (AskFileResponse): File information object.

        Returns:
            Optional[Callable[[], Any]]: A loader function for the file type, or None if unsupported.
        """
        # TODO Faire un OCR pour les pdf scannés
        file_path = Path(file['file_path'])
        if file['file_type'] == 'application/pdf':
            return PyPDFLoader(str(file_path))
        return None

    async def _get_chunks_from_file(
        self,
        file: ProcessedState
    ) -> Dict[str, Any]:
        """
        Extract text content, type and name from various file types and handle tabular data.

        Args:
            file (Dict[str, Any]): A dictionary containing file information.

        Returns:
            Dict[str, Any]: A dictionary containing extracted text documents.
        """
        chunks = None
        loader: Any | None = self._get_file_type_loader(file)
        if loader is not None:
            documents = loader.load()
            chunks = self._split_documents_into_chunks(documents)
        return chunks
