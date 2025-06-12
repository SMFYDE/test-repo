"""
This module orchestrates the BlueAxel workflow using a state graph.
"""

import json

from chainlit.types import AskFileResponse
from chainlit import Message as cl_Message

from langgraph.graph import StateGraph, END, START

from agents.blueaxel_v2.src.core.utils import get_traduction_from_key
from agents.blueaxel_v2.src.core.file_preprocessing_pipeline import FilePreprocessingPipeline, ProcessedState
from agents.blueaxel_v2.src.agents.file_extraction_agent import FileExtractionAgent
from agents.blueaxel_v2.src.agents.file_classification_agent import FileClassificationAgent
from agents.blueaxel_v2.src.factory.structured_prompt_builder import StructuredPromptBuilder


class BlueAxelGraph:
    def __init__(
        self,
        user_full_name: str,
        debug: bool = False
    ):
        self.user_full_name = user_full_name
        self.debug = debug

    def build_graph(self) -> None:
        self.workflow = StateGraph(ProcessedState)

        self.workflow.add_node('preprocessing', self._preprocessing)
        self.workflow.add_node('classification', self._classify_file_type)
        self.workflow.add_node('extraction', self._extraction)

        self.workflow.add_edge(START, 'preprocessing')
        self.workflow.add_edge('preprocessing', 'classification')
        self.workflow.add_edge('classification', 'extraction')
        self.workflow.add_edge('extraction', END)

        self.app = self.workflow.compile()

        png = self.app.get_graph().draw_mermaid_png()
        with open(
            'bluegen/agents/blueaxel_v2/docs/blueaxel_workflow.png',
            'wb'
        ) as f:
            f.write(png)

    def print_logs(self, filename, logs):
        """
        Print the logs from the state graph (adapted for dict-based logs).
        """
        print(f"\nWorkflow completed with file: {filename}")
        for step, log in logs.items():
            print(f"\n {'✔️' if log['log_status'] == 'success' else '❌'} {log['log_status']}: {log['log_name']} ({step})")
            for log_info in log['log_infos']:
                print(f" - {log_info}")
            print()
        print()

    async def run(
        self,
        file: AskFileResponse
    ) -> None:
        """
        Run the BlueAxel workflow.
        """
        print('Running BlueAxel workflow...')

        return await self.app.ainvoke({
            'file_name': file.name,
            'file_path': file.path,
            'file_type': file.type,
            'file_size': file.size,
        })

    async def _preprocessing(
        self,
        state: dict
    ) -> ProcessedState:
        """
        Preprocess the file by extracting text and metadata.

        Args:
            state (dict): The current state of the workflow containing file information.

        Returns:
            ProcessedState: The updated state after preprocessing the file.
        """
        print('Preprocessing files...')
        status_msg = cl_Message(
            content="🔁 *Préprocessing en cours...*",
            author=self.user_full_name
        )
        await status_msg.send()

        file_preprocessing_pipeline = FilePreprocessingPipeline(
            self.user_full_name,
            debug=self.debug
        )
        state = await file_preprocessing_pipeline.preprocess_one_file(state)
        if state['file_name'] is None:
            status_msg.content = "❌ *Le fichier n'a pas pu être prétraité.*"
            await status_msg.update()
            raise ValueError("File preprocessing failed. Please check the file content.")

        state['logs']['preprocessing'] = {
            'log_name': 'NODE: preprocessing',
            'log_status': 'success',
            'log_infos': [
                f"File {state['file_name']} preprocessed successfully",
                f"File size: {state['file_size']} bytes",
                f"file.type: {state['file_type']}",
                f"Extracted {len(state['chunks'])} chunks from the file",
                f"Vector store created: {state['vector_store']}",
            ]
        }
        status_msg.content = "✅ *Préprocessing terminé*"
        await status_msg.update()
        return state

    async def _classify_file_type(
        self,
        state: ProcessedState
    ) -> ProcessedState:
        """
        Classify the file type based on its content.

        Args:
            state (ProcessedState): The current state of the workflow containing file information.

        Returns:
            ProcessedState: The updated state after classifying the file type.
        """
        print('Classifying file type...')
        status_msg = cl_Message(
            content="🔁 *Classification en cours...*",
            author=self.user_full_name
        )
        await status_msg.send()

        file_classification_agent = FileClassificationAgent()
        file_category_by_model = await file_classification_agent.get_document_type(state)
        if file_category_by_model == 'unknown':
            status_msg.content = f"❌ *Le fichier {state['file_name']} n'a pas pu être classé.*"
            await status_msg.update()
            raise ValueError(f"File category is 'unknown' for file: {state['file_name']}. Please check the file content.")

        state['file_category'] = file_category_by_model
        state['logs']['classification'] = {
            'log_name': 'NODE: classification',
            'log_status': 'success',
            'log_infos': [
                f'File {state['file_name']} classified successfully',
                f'File category: {state['file_category']}',
            ]
        }
        status_msg.content = f"✅ *Classification terminé: {get_traduction_from_key(state['file_category'])}*"
        await status_msg.update()
        return state

    async def _extraction(
        self,
        state: ProcessedState
    ) -> ProcessedState:
        """
        Extract specific information from the file content.

        Args:
            state (ProcessedState): The current state of the workflow containing file information.

        Returns:
            ProcessedState: The updated state after extracting information.
        """
        print('Extracting information from the file...')
        status_msg = cl_Message(
            content="🔁 *Extraction en cours...*",
            author=self.user_full_name
        )
        await status_msg.send()

        # Call factory to get the right prompts for the file type found by the classification agent
        factory = StructuredPromptBuilder()
        output_pattern_class, prompt = factory.get_question_prompt_from_category(
            category=state['file_category']
        )
        if not output_pattern_class:
            status_msg.content = f"❌ *Aucun prompt de parsing trouvé pour la catégorie : {state['file_category']}*"
            await status_msg.update()
            raise ValueError(f"No output pattern class found for category: {state['file_category']}")

        # This agent will use the prompt to extract information from the file
        extraction_model_agent = FileExtractionAgent(query=prompt)
        extracted_info = await extraction_model_agent.extract_specific_information_from_document(
            output_pattern_class,
            state
        )
        if not extracted_info:
            status_msg.content = f"❌ *Le fichier {state['file_name']} n'a pas pu être extrait.*"
            await status_msg.update()
            raise ValueError(f"Extraction failed for file: {state['file_name']}. Please check the file content.")
        extracted_info = extracted_info.model_dump()  # Convert the extracted information to a dictionary if it's a dataclass (come from Pydantic)

        state['logs']['extraction'] = {
            'log_name': 'NODE: extraction',
            'log_status': 'success',
            'log_infos': [
                f"File {state['file_name']} processed successfully",
                f"File prompt:\n{prompt}",
                f"Answer:\n{json.dumps(extracted_info, indent=2, ensure_ascii=False)}",
                f"{json.dumps(extracted_info, indent=2, ensure_ascii=False)}"
            ]
        }
        status_msg.content = "✅ *Extraction terminée*"
        await status_msg.update()
        return state
