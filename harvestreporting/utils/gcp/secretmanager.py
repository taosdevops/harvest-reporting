from google.cloud import secretmanager


def get_from_secret_manager(project_id:str, secret_name:str):
    """Gets a secret from GCP Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(json.dumps(request).encode("UTF-8"))
    secret_string = response.payload.data.decode("UTF-8")
    return secret_string