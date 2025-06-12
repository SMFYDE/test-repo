# class InvoicesPVModulesAndBuildingIntegrationResponseFormatter(BaseModel):
#     # - What is the invoice number (Facture n°)?
#     invoice_number: str = Field(
#         description="The invoice number associated with the InvoicesPVModulesAndBuildingIntegration response."
#     )

#     # - What is the delivery note number (Bon de livraison n°)?
#     delivery_note_number: str = Field(
#         description="The delivery note number associated with the InvoicesPVModulesAndBuildingIntegration response."
#     )


# class InvoicesPVModulesAndBuildingIntegrationComplementaryResponseFormatter(BaseModel):
#     # - What is the reference code of the photovoltaic modules?
#     reference_code_of_photovoltaic_modules: str = Field(
#         description="The reference code of the photovoltaic modules associated with the InvoicesPVModulesAndBuildingIntegration response."
#     )

#     # - How many photovoltaic modules are listed?
#     number_of_photovoltaic_modules: str = Field(
#         description="The number of photovoltaic modules associated with the InvoicesPVModulesAndBuildingIntegration response."
#     )


# class InvoicesAndDeliveryNotesForAdditionalComponentsResponseFormatter(BaseModel):
#     # - What is the invoice number (Facture n°)?
#     invoice_number: str = Field(
#         description="The invoice number associated with the InvoicesAndDeliveryNotesForAdditionalComponents response."
#     )

#     # - What is the delivery note number (Bon de livraison n°)?
#     delivery_note_number: str = Field(
#         description="The delivery note number associated with the InvoicesAndDeliveryNotesForAdditionalComponents response."
#     )


# class InvoicesAndDeliveryNotesForAdditionalComponentsComplementaryResponseFormatter(BaseModel):
#     # - What is the reference code of the additional components?
#     reference_code_of_additional_components: str = Field(
#         description="The reference code of the additional components associated with the InvoicesAndDeliveryNotesForAdditionalComponents response."
#     )

#     # - How many additional components are listed?
#     number_of_additional_components: str = Field(
#         description="The number of additional components associated with the InvoicesAndDeliveryNotesForAdditionalComponents response."
#     )


class_definitions = {
    "InvoicesPVModulesAndBuildingIntegrationResponseFormatter": {
        "snake_name": "invoices_PV_modules_and_building_integration",
        "invoice_number": "The invoice number associated with the InvoicesPVModulesAndBuildingIntegration response.",
        "delivery_note_number": "The delivery note number associated with the InvoicesPVModulesAndBuildingIntegration response."
    },
    "InvoicesPVModulesAndBuildingIntegrationComplementaryResponseFormatter": {
        "reference_code_of_photovoltaic_modules": "The reference code of the photovoltaic modules associated with the InvoicesPVModulesAndBuildingIntegration response.",
        "number_of_photovoltaic_modules": "The number of photovoltaic modules associated with the InvoicesPVModulesAndBuildingIntegration response."
    },

    "InvoicesAndDeliveryNotesForAdditionalComponentsResponseFormatter": {
        "invoice_number": "The invoice number associated with the InvoicesAndDeliveryNotesForAdditionalComponents response.",
        "delivery_note_number": "The delivery note number associated with the InvoicesAndDeliveryNotesForAdditionalComponents response."
    },
    "InvoicesAndDeliveryNotesForAdditionalComponentsComplementaryResponseFormatter": {
        "reference_code_of_additional_components": "The reference code of the additional components associated with the InvoicesAndDeliveryNotesForAdditionalComponents response.",
        "number_of_additional_components": "The number of additional components associated with the InvoicesAndDeliveryNotesForAdditionalComponents response."
    }
}


def Field(value):
    return value + " (formatted)"


class Base:
    pass


def make_class(name: str, fields: dict):
    attrs = {k: Field(v) for k, v in fields.items()}
    if ()
    return type(name, (Base,), attrs)


for class_name, fields in class_definitions.items():
    globals()[class_name] = make_class(class_name, fields)

print(InvoicesPVModulesAndBuildingIntegrationResponseFormatter.invoice_number)
print(InvoicesPVModulesAndBuildingIntegrationResponseFormatter.delivery_note_number)
