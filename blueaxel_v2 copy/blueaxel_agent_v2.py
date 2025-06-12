"""
BlueAxelV2 Agent for BlueGen
This agent is designed to handle file uploads and process them using a state graph.
He can analyze PDF files uploaded by the user and classify them based on their content.
Then, it can provide insights or summaries based on the analysis.
"""

import json

from textwrap import dedent
from typing import Any, List
from operator import itemgetter

import chainlit as cl
from chainlit import AskFileMessage
from chainlit import Message as cl_Message
from chainlit.types import AskFileResponse

from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableSerializable,
)

from core.model import model_provider_type
from agents.agent import Agent

from agents.blueaxel_v2.src.core.utils import get_traduction_from_key
from agents.blueaxel_v2.src.graph.file_graph_orchestration import BlueAxelGraph

# A l'ajout d'un nouveau fichier il faut
# créer la class de sortie correspondante
# ajouter les prompts dans la config

# Au lieu de prendre PRM il a prix l'IBAN
# Comptage ?
# Connexion de la puissance d'injection ?


class BlueAxelV2(Agent):
    def __init__(
        self,
        name: str,
        full_name: str,
        model: model_provider_type
    ):
        super().__init__(name=name, full_name=full_name, model=model)

    def convert_json_to_markdown_table(self, answer_json) -> None:
        """
        Convert a JSON string to a markdown table format using French translations from traductor.json.

        Args:
            answer_json (str): The JSON string containing the data to be formatted.

        Returns:
            str: A markdown table representation of the data.
        """
        data = json.loads(answer_json)

        markdown_table = "| Champs | Valeur |\n|-------|-------|\n"
        for key, value in data.items():
            french_key = get_traduction_from_key(key)
            markdown_table += f"| {french_key} | {value} |\n"
        return markdown_table

    async def init_chat(
        self,
        resume: bool = False
    ) -> None:
        print()

        # producteur -> entreprise
        # installation -> etablissement

        # Initialize the state graph
        self.state_graph = BlueAxelGraph(
            self.full_name,
            debug=False
        )
        self.state_graph.build_graph()

        async def _request_user_for_analysis_files(
            self
        ) -> List[AskFileResponse]:
            """
            Request the user to upload files for analysis.

            Returns:
                List[AskFileResponse]: A list of files uploaded by the user.
            """
            status_msg = cl_Message(
                content=dedent("""
                    # 👋 Bienvenue sur l'agent BlueAxel !

                    Je peux analyser les fichiers PDF suivants :

                    - 📄 **Fichier Kbis**
                    - 🏢 **Fichier INSEE** (producteur ou installation)
                    - 🔌 **Contrat de raccordement** (CARD ou CART)
                    - 📝 **Demande complète de contrat** (DCC)

                    ---
                """)
            )

            files = await AskFileMessage(
                content=status_msg.content,
                accept=["application/pdf"],
                author=self.full_name,
                max_files=12,
                max_size_mb=100,
                timeout=480000,
            ).send()
            if not files:
                status_msg.content = "❌ *Il y a une erreur avec le fichier envoyé.*"
                await status_msg.update()
                raise ValueError("No files were provided")

            return files

        files = await _request_user_for_analysis_files(self)

        # Process each file using the state graph
        for file in files:
            print(f"Processing file: {file.name} ({file.size} bytes)")
            stats = await self.state_graph.run(file)
            self.state_graph.print_logs(stats['file_name'], stats['logs'])

            status_msg = cl_Message(
                content=self.convert_json_to_markdown_table(stats['logs']['extraction']['log_infos'][3])
            )
            await status_msg.send()

    async def update_settings(
        self,
        settings: dict[Any, Any]
    ) -> None:
        pass

    def setup_runnable(
            self
    ) -> RunnableSerializable[Any, Any]:
        def get_prompt() -> ChatPromptTemplate:

            system_prompt = """You are a personal assistant called BlueGen from the Socotec company. Here is some information about the Socotec company:
            Socotec specializes in Testing, Inspection, and Certification (TIC), and is dedicated to risk management and asset integrity in construction and infrastructure. 
            The company operates in 26 countries with 200,000 clients.

            You are the general agent of the BlueGen application and can assist with all daily work tasks. The application also includes two other agents: the Ask-PDF agent and the ResoTech agent.

            - You must not generate content that may be harmful to someone physically or emotionally, even if a user requests or tries to rationalize that harmful content.
            - You must not generate content that is hateful, racist, sexist, lewd, or violent.

            """

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        system_prompt,
                    ),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", "{question}"),
                ]
            )
            return prompt

        memory: ConversationBufferMemory = cl.user_session.get("memory")

        prompt = get_prompt()

        runnable = (
            RunnablePassthrough.assign(
                history=RunnableLambda(memory.load_memory_variables)
                | itemgetter("history")
            )
            | prompt
            | self.model
            | StrOutputParser()
        )

        return runnable

    async def get_message(
        self,
        user_message: cl.Message,
        ai_response: cl.Message
    ) -> None:
        pass
        # status_msg = cl_Message(content="", author=ai_response.author)
        # status_msg.content = "💭 *Thinking... of thinking*"
        # await status_msg.send()
