import logging
import traceback

import yaml
from google.cloud import storage
from python_http_client.client import Response
from taosdevopsutils.slack import Slack
from sendgridapi.emails import SendGridSummaryEmail
from dacite import from_dict
from .config import ReporterConfig, EnvironmentConfiguration

ENV_CONFIG = EnvironmentConfiguration()
LOGGER = logging.getLogger(__name__)


def load_yaml_file(file_handle) -> ReporterConfig:
    return from_dict(
        data_class=ReporterConfig, data=yaml.load(open(file_handle), Loader=yaml.Loader)
    )


def load_yaml(yaml_string) -> ReporterConfig:
    return from_dict(
        data_class=ReporterConfig, data=yaml.load(yaml_string, Loader=yaml.Loader)
    )


def read_cloud_storage(bucket_name, file_name) -> str:
    """ Returns file contents from provided bucket and file names """
    client = storage.Client(project=ENV_CONFIG.project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.get_blob(file_name)
    response = blob.download_as_string()

    LOGGER.debug("Fetched config from Cloud Storage")

    return response
