import boto3

# Créer un client S3 (utilise le profil par défaut)
s3 = boto3.client('s3')

# Lister les buckets
response = s3.list_buckets()

print("Liste des buckets S3 :")
for bucket in response['Buckets']:
    print(f" - {bucket['Name']}")
