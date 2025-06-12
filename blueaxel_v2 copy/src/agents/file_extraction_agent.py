"""
This agent is responsible for extracting information from files.
It uses a language model to analyze the file content and extract relevant information based on predefined rules.
"""

import boto3

from typing import Any
from textwrap import dedent

from langchain_aws import BedrockEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.pydantic import PydanticOutputParser

from bluegen.bluegen_bedrock.bedrock import BlueGenChatBedrock
from agents.blueaxel_v2.src.core.file_preprocessing_pipeline import ProcessedState


class FileExtractionAgent:
    def __init__(
        self,
        query: str
    ) -> None:
        self.query = query

        boto3_client = boto3.client(
            'bedrock-runtime',
            region_name='us-west-2'
        )
        self.model = BlueGenChatBedrock(
            client=boto3_client,
            model_id='anthropic.claude-3-5-sonnet-20241022-v2:0',
            region_name='us-west-2',
        )

        self.embedding = BedrockEmbeddings(
            client=boto3_client,
            model_id='amazon.titan-embed-text-v2:0',
            region_name='us-west-2',
        )

    async def _prompt_build_template(self) -> str:
        return dedent("""
        # SYSTEM INSTRUCTIONS
        You must analyze the document and extract the relevant information from it.
        You must answer the question based on the document.
        You will be guided by the system instructions during the retrieval process.

        ## PARSING INFORMATION
            - Do not rename or change the titles found in the context.
            - Do not change the order of the questions.
            - Do not change the order of the answers.
            - If the answer is a date, use the European format 'DD-MM-YYYY'.
            - If the answer is a duration, write it in digits and specify
            the unit (days, months, or frequency).
            - If the answer refers to a time interval, write it in digits
            and specify the frequency (e.g., every 2 weeks, 45 days, every year).
            - If the answer is a code, write it in digits.
            - If the answer is a name, write it in capital letters.
            - If the answer is a location, write it in capital letters.
            - If the answer is a price, write it in digits and specify the currency.
            - If the answer is a percentage, write it in digits.

        ## ANSWERING INSTRUCTIONS
            - You must answer the question by providing a ```JSON``` object.
            - Keys in the JSON must follow the `snake_case` format.
            - Do not include any text outside of the JSON.
            - Do not invent information; base your answer strictly on the context.
            - If the answer is not in the context, respond with 'Unknown'.
            - If a value cannot be found in the context, do not guess. Write 'Unknown'.
            - DO NOT use square brackets for the main structure. Always use curly braces.

        ## DOCUMENT INPUT COMPONENTS
        --------------------------------- CONTEXT --------------------------------------
        This is the document context you must take into account:
        {context}

        ------------------------ MAIN EXTRACTION OBJECTIVE -----------------------------
        This is the question:
        {question}

        --------------------------- HELPER QUESTIONS -----------------------------------
        These are the helper questions that may assist in answering the main question:
        {helper_questions}

        --------------------------- OUTPUT FORMAT TEMPLATE -----------------------------
        This is how the answer should be formatted:
        {format_instruction}
        """)

    # @retry(
    #     retry=retry_if_exception_type(ClientError),
    #     stop=stop_after_attempt(5),  # Max 5 retries
    #     wait=wait_exponential(multiplier=2, min=1, max=10),  # Exponential backoff
    # )
    async def extract_specific_information_from_document(
        self,
        output_pattern,
        state: ProcessedState
    ) -> Any:
        print()

        prompt = await self._prompt_build_template()
        parser = PydanticOutputParser(pydantic_object=output_pattern)

        print("step 1: Prompt template built")

        template = ChatPromptTemplate(
            [
                ("system", prompt),
                ("user", "{question}"),
            ],
        )

        print("step 2: Template created")

        # TODO recuperer les dates des documents pour trouver le dernier

        # TODO checker la taille du document
        # Si trop long, faire un split et faire une recherche par chunk
        # Sinon, envoyer le document entier

        def extract_keywords(question_block: str) -> str:
            """
            Extract keywords from the question block.

            Args:
                question_block (str): The block of text containing the question.

            Returns:
                str: A string of keywords extracted from the question block.
            """
            lines = question_block.split("\n")
            keywords = []
            for line in lines:
                if line.strip().startswith("- "):
                    # Clean first part of the line
                    cleaned = (
                        line.replace("What are", "")
                            .replace("What is", "")
                            .replace("Is there", "")
                            .strip(" -")
                    )
                    # Cut off end of line if it contains a separator
                    for sep in ["?", "("]:
                        if sep in cleaned:
                            cleaned = cleaned.split(sep)[0]
                    keywords.append(cleaned.strip().lower())
            return "\n".join(keywords)

        extracted_keywords = extract_keywords(self.query)
        # print(f"Extracted keywords: {extracted_keywords}")

        # ! Est ce que k n'est pas sensé etre le nombre de questions posées ?
        docs = await state["vector_store"].asimilarity_search_with_score(
            query=extracted_keywords,
            k=20,
        )
        if not docs:
            raise ValueError("No documents found in vector store.")

        print()
        print(f"Found {len(docs)} documents in vector store.")
        for doc in docs:
            print(f"Document score: {doc[1]}")
            print(f"Document content: {doc[0].page_content}...")
            print()

        print("step 3: Documents retrieved from vector store")

        input_dict = {
            "context": [f"{doc[0].page_content}" for doc in docs],
            "question": self.query,
            "format_instruction": parser.get_format_instructions(),
            "helper_questions": "",
        }

        print("step 4: Input dictionary created")

        chain = template | self.model | parser

        print("step 5: Chain created")
        # print(f"Input dictionary for extraction: {input_dict}")

        document_type_answer = await chain.ainvoke(input_dict)

        return document_type_answer
