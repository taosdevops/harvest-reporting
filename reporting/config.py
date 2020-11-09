import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

import yaml
from dacite import from_dict
from google.cloud import secretmanager, storage

LOGGER = logging.getLogger(__name__)

# Environment Variables
## Required, these must be set or they will return None
HARVEST_ACCOUNT_ID = os.getenv("HARVEST_ACCOUNT_ID")
ORIGIN_EMAIL_ADDRESS = os.getenv("ORIGIN_EMAIL_ADDRESS")
BUCKET = os.getenv("BUCKET")
GCP_PROJECT = os.getenv("GCP_PROJECT")
## Optional, these have a default value if they're not set
CONFIG_PATH = os.getenv("CONFIG_PATH", "config/clients.yaml") # default to "config/clients.yaml"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info") # default to "info"


def get_env_var_or_fetch_from_secret_manager(name:str):
    """Gets an environment variable if available, else gets a secret value from GCP Secret Manager."""
    environment_variable = os.getenv(name)
    if environment_variable:
        return environment_variable
    elif not environment_variable:
        secret_name = f"harvest-reports-{name.lower().replace('_', '-')}" # eg env var name is BEARER_TOKEN, secret name is 'harvest-reports-bearer-token'
        return get_from_secret_manager(project_id=GCP_PROJECT, secret_name=secret_name)


def get_from_secret_manager(project_id:str, secret_name:str):
    """Gets a secret from GCP Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request.encode("UTF-8"))
    secret_string = response.payload.data.decode("UTF-8")
    return secret_string


# Environment Variables
## Required or fetched from Secret Manager
### If the name is changed, be sure to update the associated secret's name in GCP Secret Manager!
BEARER_TOKEN = get_env_var_or_fetch_from_secret_manager("BEARER_TOKEN")
SENDGRID_API_KEY = get_env_var_or_fetch_from_secret_manager("SENDGRID_API_KEY")


@dataclass
class VerificationConfig(object):
    email: Optional[List[str]] = field(default_factory=list)
    slack: Optional[str] = ""
    teams: Optional[str] = ""


@dataclass
class RecipientsConfig(object):
    templateId: Optional[str] = ""
    sendVerificationConfig: Optional[VerificationConfig] = VerificationConfig()


@dataclass
class Recipients(object):
    config: Optional[RecipientsConfig] = RecipientsConfig()
    emails: Optional[List[str]] = field(default_factory=list)
    slack: Optional[List[str]] = field(default_factory=list)
    teams: Optional[List[str]] = field(default_factory=list)


@dataclass
class Customer(object):

    name: str
    hours: Optional[int] = 80
    recipients: Optional[Recipients] = Recipients()


@dataclass
class ReporterConfig(object):
    customers: List[Customer]
    recipients: Recipients
    exceptions: Recipients
    customer_filter: Optional[List[str]] = field(default_factory=list)

def load(fname: str, bucket: str = None, project: str = None) -> ReporterConfig:
    """Function to load config from file system or a GCS bucket.

    Args:
        fname (str): File to load
        bucket (str, optional): Name of bucket to pull from. Defaults to None.
        project (str, optional): GCP project the bucket lives in. Defaults to None.

    Returns:
        ReporterConfig: Loaded configuration
    """
    if bucket:
        LOGGER.info(f"Fetching config from Cloud Storage: bucket|{bucket}, project|{project}, file|{fname}")
        f = load_from_gcs(bucket, project, fname)
    else:
        LOGGER.info(f"Fetching config from file system: file|{fname}")
        with open(fname, "r") as f_obj:
            f = f_obj.read()

    return from_dict(
        data_class=ReporterConfig, data=yaml.load(f, Loader=yaml.Loader)
    )


def load_from_gcs(bucket: str, project: str, fname: str) -> str:
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
