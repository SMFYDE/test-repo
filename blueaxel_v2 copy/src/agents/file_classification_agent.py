"""
This agent is responsible for classifying files based on their content and type.
It uses a language model to analyze the file and determine its classification, such as whether it is a KBIS, INSEE, SIRET, or other types of documents.
"""

import boto3

from typing import Literal, Optional
from pydantic import BaseModel, Field
from textwrap import dedent

from langchain_core.output_parsers import JsonOutputParser

from bluegen_bedrock.bedrock import BlueGenChatBedrock
from agents.blueaxel_v2.src.core.file_preprocessing_pipeline import ProcessedState


class DocumentTypeResponseFormatter(BaseModel):
    """
    A class to format the response for Document Type requests.

    Attributes:
        document_type (str): The type of the document.
    """
    document_type: Literal[
        'kbis',
        'insee_file',
        'invoices_mentioning_the_reference_of_the_photovoltaic_modules_and_if_applicable_the_building_integration_system',
        'invoices_for_the_purchase_of_other_components_and_the_corresponding_delivery_notes',
        'simplified_carbon_assessment',
        'professional_qualification_or_certification_for_the_installation_company',
        'cart_or_card',
        'general_terms_and_conditions_of_the_purchase_or_remuneration_contract',
        'DCC',
        'others',
    ] = Field(
        default='others',
        description="The type of the document associated with the response."
    )


class DocumentFeatures(BaseModel):
    mentions_rcs: bool
    mentions_tribunal: bool
    mentions_siren: bool
    mentions_ape: bool
    mentions_producteur: bool
    mentions_raccordement: bool
    mentions_reseau: bool
    mentions_cart_or_card: bool
    mentions_contrat_signature: bool

    document_type_hint: Optional[str]
    commentaire: Optional[str]
    percent: Optional[str]


class FileClassificationAgent:
    def __init__(
        self
    ) -> None:
        # TODO je pense qu'il y a un probleme avec cette valeur, elle est trop petite
        self.TOKENS_LIMIT = 100000  # Limit for the number of tokens in the document content

        boto3_client = boto3.client(
            'bedrock-runtime',
            region_name='us-west-2'
        )
        self.model = BlueGenChatBedrock(
            client=boto3_client,
            # model_id='anthropic.claude-3-5-sonnet-20241022-v2:0',
            model_id='us.anthropic.claude-3-7-sonnet-20250219-v1:0',
            # model_id='anthropic.claude-sonnet-4-20250514-v1:0',
            region_name='us-west-2',
        )

    def _prompt_build_template(
        self,
        file_name: str,
        context: str,
        response_formatter: str,
    ) -> str:
        """
        Build the prompt template for the document type detection agent.

        Args:
            file_name (str): The name of the file being analyzed.

        Returns:
            str: The formatted prompt template for the agent.
        """
        return f"""
            # PARSING INFORMATION
            You are an agent that detects the type of document based on the content.
            Here is the list of document types that you have to detect as your task:
            - Kbis of producer, which is a legal document that provides information about a business's registration in the French Trade and Companies Register.
            - INSEE File, which contains the INSEE number of the producer, a unique identifier for businesses in France.
            - Invoices mentioning the reference of the photovoltaic modules and, if applicable, the building integration system, along with the corresponding delivery notes. These documents provide proof of purchase and technical details for the modules.
            - Invoices for the purchase of other components and the corresponding delivery notes, which confirm the acquisition of additional equipment necessary for the project.
            - Simplified carbon assessment, which evaluates the estimated carbon impact of the project. This document is required if specified in the call for tenders or the applicable tariff decree.
            - Professional qualification or certification for the installation company, which demonstrates that the company is qualified to carry out photovoltaic installations. This is required if specified in the regulations.
            - CART (Contract for Access to Public Transmission Networks) or CARD (Contract for Access to Public Distribution Networks), which defines the terms of access to the French electricity grid for the installation.
            - General terms and conditions of the purchase or remuneration contract, which outline the standard terms governing the sale or remuneration of the electricity produced by the photovoltaic installation.
            - Specific terms and conditions of the purchase or remuneration contract, including amendment requests and contract amendments, which detail project-specific provisions, changes, and updates to the contract.

            # ANSWERING INSTRUCTIONS
                - You must answer the question by providing a JSON object.
                - Do not include any additional text in addition to the JSON.
                - Do not invent any information, base your answer on the context.
                - If the answer is not in the context, say 'Unknown'.
                - DO NOT use square brackets for the main structure. Always use curly braces.

            # CONTEXT
            <context>
                {context}
            </context>

            # QUESTION
            <question>
            The file name is: {file_name}.
                The document of interest contains a certain type of information, which will help determine whether it is a:
                - Kbis of producer
                - INSEE Producer File
                - SIRET of Installation
                - Invoices mentioning the reference of the photovoltaic modules and, if applicable, the building integration system
                - Invoices for the purchase of other components and the corresponding delivery notes
                - Simplified carbon assessment
                - Professional qualification or certification for the installation company
                - CART (Contract for Access to Public Transmission Networks) or CARD (Contract for Access to Public Distribution Networks)
                - General terms and conditions of the purchase or remuneration contract
                - Specific terms and conditions of the purchase or remuneration contract, including amendment requests and contract amendments

                According to your analysis, what is the type of document?
            </question>

            # ANSWER
            Answer to the question asked by the user in a JSON object format:
            <response_formatter>
                {response_formatter}
            </response_formatter>
        """

    async def get_document_type(
        self,
        state: ProcessedState
    ) -> str:
        """
        Classify the file type based on its content.

        Args:
            state (ProcessedState): The current state of the workflow containing file information.

        Returns:
            str: The classified document type.
        """
        # Limit the length of the chunks to TOKENS_LIMIT
        def _truncate_content(chunks: list[str], limit: int) -> str:
            result = []
            current_length = 0
            for info in chunks:
                available_space = limit - current_length
                if available_space <= 0:
                    break
                chunk = info.page_content[:available_space]
                result.append(chunk)
                current_length += len(chunk)
            return "".join(result)

        # envoyer les questions au model
        parser = JsonOutputParser(pydantic_object=DocumentFeatures)

        # Questions posées au LLM
        questions_prompt = f"""
            # PARSING INFORMATION
            You are going to analyze a document in order to determine its characteristics. For each of the following questions, please answer YES or NO:

            # CONTEXT
            <context>
                Document title: {state['file_name']}
                Document content: {_truncate_content(state['chunks'], self.TOKENS_LIMIT)}
            </context>

            # QUESTION
            <question>
                Does the document contain a RCS number?
                Does it mention a commercial court registry or a tribunal?
                Does it contain a SIREN or SIRET number?
                Does it include an APE or NAF code?
                Does it mention a producer or a third-party applicant?
                Does it refer to grid connection or connection power?
                Does it mention 'card' or 'cart'?
                Are there mentions of network operators (e.g., Enedis, RTE)?
                Is this document a signed contract or a pre-contractual version?
                Based on the content, can you suggest a document type from the following: KBIS, INSEE file, contract request (CDD), or grid connection contract (CART or CARD)?
                Indicate your level of confidence between 0% (no idea) and 100% (almost certain), based solely on the elements present in the document.
            </question>

            # ANSWER
            Answer to the question asked by the user in a JSON object format:
            <response_formatter>
                {parser.get_format_instructions()}
            </response_formatter>
        """

        response = await self.model.ainvoke(dedent(questions_prompt).strip())
        answer = parser.parse(response.content)
        print()
        print(f'{answer['mentions_rcs']} - mentions_rcs')
        print(f'{answer['mentions_tribunal']} - mentions_tribunal')
        print(f'{answer['mentions_siren']} - mentions_siren')
        print(f'{answer['mentions_ape']} - mentions_ape')
        print(f'{answer['mentions_producteur']} - mentions_producteur')
        print(f'{answer['mentions_raccordement']} - mentions_raccordement')
        print(f'{answer['mentions_reseau']} - mentions_reseau')
        print(f'{answer['mentions_contrat_signature']} - mentions_contrat_signature')
        print(f'{answer['mentions_cart_or_card']} - mentions_cart_or_card')
        print()
        print(f'document_type_hint: {answer['document_type_hint']} with confidence {answer['percent']}')
        print(f'commentaire: {answer['commentaire']}')
        print()

        # TODO Faire un modele ML simple (Random Forest, Liear Regression etc.)
        # TODO Refaire un appel au modele
        # TODO Similarité textuelle (sans ML)
        # TODO Melange de tout ?
        # Algorithme de classification (exemple simple)
        # if answer['document_type_hint'] == 'KBIS':
        #     answer = 'kbis'
        # elif answer['document_type_hint'] == 'INSEE file':
        #     answer = 'insee_file'
        # elif answer['document_type_hint'] == 'contract request (CDD)':
        #     answer = 'DCC'
        # elif answer['document_type_hint'] == 'grid connection contract (CART or CARD)':
        #     answer = 'cart_or_card'
        # else:
        #     answer = 'others'
        # if answer['mentions_rcs'] and answer['mentions_tribunal']:
        #     answer = "kbis"
        # elif answer['mentions_siren'] and answer['mentions_ape']:
        #     answer = "insee_file"
        # elif answer['mentions_producteur'] and not answer['mentions_contrat_signature']:
        #     answer = "DCC"
        # elif answer['mentions_raccordement'] and answer['mentions_reseau']:
        #     answer = "cart_or_card"
        # else:
        #     answer = "Impossible de determiner le type de document"

        def classify_document(features: DocumentFeatures) -> str:
            scores = {
                "kbis": 0,
                "insee_file": 0,
                "cart_or_card": 0,
                "DCC": 0
            }

            # --- KBIS ---
            if features['mentions_rcs'] or features['mentions_tribunal']:
                scores["kbis"] += 2
            if not features['mentions_siren']:
                scores["kbis"] += 1
            if not features['mentions_producteur'] and not features['mentions_raccordement']:
                scores["kbis"] += 1

            # --- Fiche INSEE ---
            if features['mentions_siren'] or features['mentions_ape']:
                scores["insee_file"] += 2
            if not features['mentions_rcs']:
                scores["insee_file"] += 1

            # --- Contrat de raccordement (CARD/CART) ---
            if (
                features['mentions_raccordement']
                or features['mentions_producteur']
                or features['mentions_reseau']
                or features['mentions_contrat_signature']
            ):
                scores["cart_or_card"] += 2
            if features['mentions_cart_or_card']:
                scores["cart_or_card"] += 1

            # --- Demande de contrat (CDD) ---
            if (
                features['mentions_producteur']
                or features['mentions_raccordement']
                or features['mentions_reseau']
            ):
                scores["DCC"] += 2
            if features['mentions_contrat_signature']:
                scores["DCC"] += 1
            if not features['mentions_ape']:
                scores["DCC"] += 1
            if not features['mentions_cart_or_card']:
                scores["DCC"] += 3

            # --- Choix final ---
            print(f'Scores: {scores}')
            predicted_type = max(scores, key=scores.get)
            return predicted_type

        answer = classify_document(answer)

        # examiner les reponses du model pour determiner le type de document
        print(f'Algo predict: {answer}')
        print()

        return answer

        query = f"""
            Document title: {state['file_name']}
            Document type: {state['file_type']}
            Document content: {_truncate_content(state['chunks'], self.TOKENS_LIMIT)}
        """

        parser = JsonOutputParser(
            pydantic_object=DocumentTypeResponseFormatter,
        )

        prompt = self._prompt_build_template(
            file_name=state['file_name'],
            context=dedent(query).strip(),
            response_formatter=parser.get_format_instructions(),
        )

        # print(f'Prompt for document type classification: {prompt}')
        # print(f'Prompt len: {len(prompt)}')

        response = await self.model.ainvoke(prompt)
        answer = parser.parse(response.content)
        if 'document_type' not in answer:
            raise ValueError('Document type not found in model response.')
        return answer['document_type']
