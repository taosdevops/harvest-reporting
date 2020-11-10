import json
import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

import yaml
from dacite import from_dict

import harvestreporting.utils.gcp.secretmanager
import harvestreporting.utils.gcp.cloudstorage

LOGGER = logging.getLogger(__name__)

def get_env_var_or_fetch_from_secret_manager(name:str):
    """Gets an environment variable if available, else gets a secret value from GCP Secret Manager."""
    environment_variable = os.getenv(name)
    if environment_variable:
        return environment_variable
    elif not environment_variable:
        try:
            secret_name = f"harvest-reports-{name.lower().replace('_', '-')}" # eg env var name is BEARER_TOKEN, secret name is 'harvest-reports-bearer-token'
            return harvestreporting.utils.gcp.secretmanager.get_from_secret_manager(project_id=GCP_PROJECT, secret_name=secret_name)
        except:
            # Implemented so that tests can still run
            LOGGER.debug(f"Failed to authenticate with GCP Secret Manager. You're either testing or an environment variable doesn't have the right value: {os.environ}")
            return "NOT_SET"


# Environment Variables
## Required, these must be set or they will return "NOT_SET" which may cause errors
HARVEST_ACCOUNT_ID = os.getenv("HARVEST_ACCOUNT_ID", "NOT_SET")
ORIGIN_EMAIL_ADDRESS = os.getenv("ORIGIN_EMAIL_ADDRESS", "NOT_SET")
BUCKET = os.getenv("BUCKET", "NOT_SET")
GCP_PROJECT = os.getenv("GCP_PROJECT", "NOT_SET")
## Required or fetched from Secret Manager
### If the name is changed, be sure to update the associated secret's name in GCP Secret Manager!
BEARER_TOKEN = get_env_var_or_fetch_from_secret_manager("BEARER_TOKEN")
SENDGRID_API_KEY = get_env_var_or_fetch_from_secret_manager("SENDGRID_API_KEY")
## Optional, these have a default value
CONFIG_PATH = os.getenv("CONFIG_PATH", "config/clients.yaml") # default to "config/clients.yaml"
LOG_LEVEL = os.getenv("LOG_LEVEL", "info") # default to "info"


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
        f = harvestreporting.utils.gcp.cloudstorage.load(bucket, project, fname)
    else:
        LOGGER.info(f"Fetching config from file system: file|{fname}")
        with open(fname, "r") as f_obj:
            f = f_obj.read()

    return from_dict(
        data_class=ReporterConfig, data=yaml.load(f, Loader=yaml.Loader)
    )
