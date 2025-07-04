import boto3

client = boto3.client('bedrock', region_name='eu-west-1')

response = client.list_foundation_models(
    byOutputModality='TEXT'
)

print("Modèles disponibles EN ON-DEMAND :\n")

for model in response['modelSummaries']:
    if 'ON_DEMAND' in model.get('inferenceTypesSupported', []):
        print(f"✅ Nom : {model['modelName']}")
        print(f"ID  : {model['modelId']}")
        print(f"Provider : {model['providerName']}")
        print(f"Supporte : {model['inferenceTypesSupported']}")
        print('-' * 40)

print("\nModèles uniquement PROVISIONNÉS :\n")

for model in response['modelSummaries']:
    if 'ON_DEMAND' not in model.get('inferenceTypesSupported', []):
        print(f"❌ Nom : {model['modelName']}")
        print(f"ID  : {model['modelId']}")
        print(f"Provider : {model['providerName']}")
        print(f"Supporte : {model['inferenceTypesSupported']}")
        print('-' * 40)
