from google.cloud import storage


def load(bucket: str, project: str, fname: str) -> str:
    """Returns file contents from provided bucket and file names

    Args:
        bucket (str): Bucket to fetch file from
        project (str): Project in which bucket lives
        fname (str): File path in bucket to download

    Returns:
        str: Full file downloaded from GCS
    """
    client = storage.Client(project=project)
    bucket = client.bucket(bucket)
    blob = bucket.blob(fname)
    response = blob.download_as_string()

    return response