"""
"""

from typing import ClassVar, Optional
from pydantic import BaseModel


class KbisPattern(BaseModel):
    name: ClassVar[str] = 'kbis'

    document_date: Optional[str]
    gestion_number: Optional[str]

    greffe_name: Optional[str]
    rcs_immatriculation_number: Optional[str]
    company_name: Optional[str]
    company_address: Optional[str]


class InseeFilePattern(BaseModel):
    document_date: Optional[str]
    company_siren_number: Optional[str]

    company_name: Optional[str]
    company_activity_start_date: Optional[str]
    company_siret_number: Optional[str]

    company_address: Optional[str]


class CartOrCardPattern(BaseModel):
    document_date: Optional[str]
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


class DCCPattern(BaseModel):
    document_date: Optional[str]
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


class InvoicesPhotovoltaicModulesPattern(BaseModel):
    document_date: Optional[str]

    facture_number: Optional[str]
    delivery_note_number: Optional[str]

    # Modules
    module_reference: Optional[str]
    module_count: Optional[int]


class InvoicesOtherComponentsPattern(BaseModel):
    document_date: Optional[str]

    facture_number: Optional[str]
    delivery_note_number: Optional[str]

    # Onduleurs
    inverter_reference: Optional[str]
    inverter_count: Optional[int]


class GeneralConditionsContractPattern(BaseModel):
    document_date: Optional[str]
    has_general_conditions_contract: Optional[bool]
    # TODO qu'est ce que je dois récuperer comme info ?


class ParticularConditionsContractPattern(BaseModel):
    document_date: Optional[str]
    has_particular_conditions_contract: Optional[bool]
    # TODO qu'est ce que je dois récuperer comme info ?


class NonCumulationAttestationPattern(BaseModel):
    document_date: Optional[str]
    # TODO qu'est ce que je dois récuperer comme info ?
