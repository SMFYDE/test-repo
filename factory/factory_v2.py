"""
Factory class for dynamically receiving prompts and generating classes based on the provided configuration.
"""

config = {
    'kbis': {
        'question_template': """
            The Kbis is an official document in France that certifies the legal existence of a business or company. It is issued by the clerk of the commercial court and is the company's only official "identity card".

            - In this document, what is the gestion number of the document ?
        """
    },
    'insee_file': {
        'question_template': """
            The INSEE Producer File, also known as the SIRENE register status notice, is a document that provides an 'identity sheet' for each company, association or public body registered in the SIRENE register. This sheet contains information about the SIREN number (unique company identifier).

            - what is the SIREN number of the company ?
        """,
    }
}


class PromptRegistry:
    def __init__(
        self
    ) -> None:
        self.factory_config = config

    def get_question_prompt_from_category(
        self,
        category: str
    ) -> str:
        """
        Get the question prompt for the specified category.

        Args:
            category (str): The name of the category to retrieve the prompt for.

        Returns:
            str: The question prompt string.
        """
        if category not in self.factory_config:
            raise ValueError(f"Category '{category}' not found in factory configuration.")
        if 'question_template' not in self.factory_config[category]:
            raise ValueError(f"Question template not found for category '{category}'.")

        return self.factory_config[category]['question_template'].strip()


my_prompt_registry = PromptRegistry()

print(my_prompt_registry.get_question_prompt_from_category(category="kbis"))
print(my_prompt_registry.get_question_prompt_from_category(category="insee_file"))
