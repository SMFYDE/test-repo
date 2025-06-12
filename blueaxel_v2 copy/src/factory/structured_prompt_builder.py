"""
Factory class for dynamically receiving prompts and generating classes based on the provided configuration.
"""

from textwrap import dedent

from typing import Optional
from pydantic import BaseModel

# TODO Copier coller tous les prompts dans la config cet aprem

config = {
    'kbis': """
            The kbis is an official document in France that certifies the legal existence of a business or company. It is issued by the clerk of the commercial court and is the company's only official "identity card".
            From this document, you must extract the following information:

            - What is the gestion number of the document ?
            - What is the name of the commercial court ?
            - What is the RCS immatriculation number ?
            - What is the name of the company ?
            - What is the address of the company ?
    """,
    'insee_file': """
            The INSEE Producer File, also known as the SIRENE register status notice, is a document that provides an 'identity sheet' for each company, association or public body registered in the SIRENE register. This sheet contains information about the company.
            From this document, you must extract the following information:

            - What is the SIREN number of the company ?
            - What is the name of the company ?
            - What is the company's start date of activity?
            - What is the SIRET number ?
    """,
    'cart_or_card': """
            The CART or CARD is a document that contains information about the photovoltaic installation contract. It includes details about the producer, the installation, and the technical specifications of the photovoltaic system.
            From this document, you must extract the following information:

            - What is the CARD-i contract number ?
            - What is the name of the project ?
            - What is the PRM (Production Reference Meter) ?
            - What is the SIRET number of the establishment ?
            - What is the address of the site ?
            - What is the connection power for injection ?
            - What are the counting methods ?
    """,
    'DCC': """
            The DCC (Complete Contract Request), including any amendments, is a key document in the photovoltaic installation contract process. It typically includes technical and administrative details about the producer and the installation.
            From this document, you must extract the following information:

            - What is the name of the company (producer)?
            - What is the SIREN number of the producer?
            - What is the address of the producer?

            - What is the name of the installation?
            - What is the SIRET number of the installation? (It must be the same as the producer’s SIREN)
            - What is the address of the installation?

            - What is the maximum installed production capacity (in kVA)? (Must match the on-site inspection)
            - What is the injection type of the production?
            - What is the power curtailment device? (Verify with on-site inspection)

            - What is the maximum active power drawn (in kW)? (Not a control point, but should be compared with the on-site inspection)

            - What are the photovoltaic inverters (or production units)? (Include details and power, to be compared with max installed capacity)
            - What is the installed peak power (in kWc)? (To be compared with on-site inspection)

            - What are the geodetic coordinates of the four extreme points?
            - Point 1: coordinates
            - Point 2: coordinates
            - Point 3: coordinates
            - Point 4: coordinates

            - Is there a "prime tuile"? (Yes or No)
            - What is the Q power?
    """,
    'others': """
            - What is the name of the company (producer)?
    """,
}


class KbisExtractionOutputPattern(BaseModel):
    gestion_number: Optional[str]

    greffe_name: Optional[str]
    rcs_immatriculation_number: Optional[str]
    company_name: Optional[str]
    company_address: Optional[str]


class InseeFileExtractionOutputPattern(BaseModel):
    company_siren_number: Optional[str]

    company_name: Optional[str]
    company_activity_start_date: Optional[str]
    company_siret_number: Optional[str]

    company_address: Optional[str]


class CartOrCardExtractionOutputPattern(BaseModel):
    cardi_contract_number: Optional[str]

    project_name: Optional[str]
    prm: Optional[str]
    company_siret_number: Optional[str]
    company_address: Optional[str]
    injection_power_connection: Optional[str]
    count: Optional[str]


class InverterDetail(BaseModel):
    quantity: int = 1
    model: str
    nominal_power_kva: Optional[int] = None
    max_power_kva: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.model} (Nominal: {self.nominal_power_kva} kVA, Max: {self.max_power_kva} kVA, Qty: {self.quantity})"


class DCCExtractionOutputPattern(BaseModel):
    company_name: Optional[str]

    producer_siren_number: Optional[str]
    producer_address: Optional[str]

    installation_name: Optional[str]
    installation_siret_number: Optional[str]
    installation_address: Optional[str]

    max_production_capacity_kva: Optional[str]
    injection_type: Optional[str]
    curtailment_device: Optional[str]
    max_active_power_kw: Optional[str]

    inverters_details: Optional[list[InverterDetail]]

    installed_peak_power_kwc: Optional[str]

    geodetic_point_1: Optional[str]
    geodetic_point_2: Optional[str]
    geodetic_point_3: Optional[str]
    geodetic_point_4: Optional[str]

    prime_tuile: Optional[str]
    q_power: Optional[str]


class StructuredPromptBuilder:
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

        print(f"Retrieving question prompt for category: {category}")

        prompt = dedent(
            self.factory_config[category]
        ).strip()

        class_category_link = {
            'kbis': KbisExtractionOutputPattern,
            'insee_file': InseeFileExtractionOutputPattern,
            'cart_or_card': CartOrCardExtractionOutputPattern,
            'DCC': DCCExtractionOutputPattern,
        }

        return class_category_link[category], prompt


# my_prompt_registry = PromptRegistry()

# print(my_prompt_registry.get_question_prompt_from_category(category="kbis"))
# print(my_prompt_registry.get_question_prompt_from_category(category="insee_file"))
