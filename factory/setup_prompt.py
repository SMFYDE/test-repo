config = {
    'kbis': {
        'question_template': """
            The kbis is an official document in France that certifies the legal existence of a business or company. It is issued by the clerk of the commercial court and is the company's only official "identity card".
            It contains useful information that you must extract:
            - What is the gestion number of the document ?
            - What is the name of the commercial court ?
            - What is the RCS immatriculation number ?
            - What is the name of the company ?
            - What is the address of the company ?
        """
    },
    'insee_file': {
        'question_template': """
            The INSEE Producer File, also known as the SIRENE register status notice, is a document that provides an 'identity sheet' for each company, association or public body registered in the SIRENE register. This sheet contains information about the company.
            According to the INSEE Producer File,
            - What is the SIREN number of the company ?
            - What is the name of the company ?
            - What is the company's start date of activity?
            - What is the SIRET number ?
        """,
    },
    'cart_or_card': {
        'question_template': """
            - What is the name of the company (producer)?
        """,
    },
    'DCC': {
        'question_template': """
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
    },
    'others': {
        'question_template': """
            - What is the name of the company (producer)?
        """,
    },
}


def extract_keywords(question_block: str) -> str:
    lines = question_block.split("\n")
    keywords = []
    for line in lines:
        if line.strip().startswith("- "):
            # Nettoyage du début
            cleaned = (
                line.replace("What are", "")
                    .replace("What is", "")
                    .replace("Is there", "")
                    .strip(" -")
            )
            # On coupe à la première occurrence de '?' ou '(' ou ':'
            for sep in ["?", "("]:
                if sep in cleaned:
                    cleaned = cleaned.split(sep)[0]
            keywords.append(cleaned.strip().lower())
    return "\n".join(keywords)


extracted_keywords = extract_keywords(config['DCC']['question_template'])
print(f"Extracted keywords:\n{extracted_keywords}")
