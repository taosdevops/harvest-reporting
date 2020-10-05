import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

import yaml
from dacite import from_dict
from google.cloud import storage as storage
from google.cloud.secretmanager import SecretManagerServiceClient

LOGGER = logging.getLogger(__name__)
HARVEST_ACCOUNT_ID = "HARVEST_ACCOUNT_ID"
BEARER_TOKEN = "BEARER_TOKEN"
BEARER_TOKEN_SECRET = "BEARER_TOKEN_SECRET"
BEARER_TOKEN_SECRET_VERSION = "BEARER_TOKEN_VERSION"
ORIGIN_EMAIL_ADDRESS = "ORIGIN_EMAIL_ADDRESS"
SENDGRID_API_KEY = "SENDGRID_API_KEY"
SENDGRID_API_KEY_SECRET = "SENDGRID_API_KEY_SECRET"
SENDGRID_API_KEY_SECRET_VERSION = "SENDGRID_API_KEY_SECRET_VERSION"
BUCKET = "BUCKET"
CONFIG_PATH = "CONFIG_PATH"
GCP_PROJECT = "GCP_PROJECT"
LOG_LEVEL = "LOG_LEVEL"


class MissingEnvironmentVariable(BaseException):
    def __init__(self, env_var):
        self.env_var = env_var
        super().__init__(f"Missing environment variable {env_var}")


class EnvironmentConfiguration(object):
    """Class used to fetch all environment variables used to configure the
    reporter. All values are lazy-loaded.
    """
    def __init__(self):
        self._secrets_client = None
        self._log_level = None
        self._bearer_token = None
        self._harvest_account = None
        self._origin_email_address = None
        self._sendgrid_api_key = None
        self._bucket = None
        self._config_path = None
        self._project_id = None

    @property
    def secrets_client(self):
        """Creates a new secrets client to be used when fetching secrets from
        GCP's secrets manager.

        Returns:
            SecretManagerServiceClient: A secret manager client from Google's
            Python SDK
        """
        if self._secrets_client == None:
            self._secrets_client = SecretManagerServiceClient()
        return self._secrets_client

    @secrets_client.setter
    def secrets_client(self, client):
        """Allows for manually setting a secrets client
        """
        self._secrets_client = client

    @property
    def log_level(self):
        """Fetch the configured log level. Defaults to `info`.

        Returns:
            str: String containing configured log level
        """
        if self._log_level == None:
            self._log_level = self._get_log_level()
        return self._log_level

    @property
    def bearer_token(self):
        """Fetch the configured Harvest API bearer token.

        Requires either a `BEARER_TOKEN` environment variable to be set or the
        `BEARER_TOKEN_SECRET` environment variable to be set. If the
        `BEARER_TOKEN_SECRET` environment variable is set, the
        `BEARER_TOKEN_SECRET_VERSION` can also be set to pull a specific secret
        version.

        Raises:
            MissingEnvironmentVariable: Raised if no valid bearer token
            configuration is present

        Returns: str: The bearer token
        """
        if self._bearer_token == None:
            self._bearer_token = self._get_bearer_token()
        return self._bearer_token

    @property
    def harvest_account(self):
        """Fetch the Harvest account to query.

        Raises:
            MissingEnvironmentVariable: if the "HARVEST_ACCOUNT_ID" environment
            variable is missing

        Returns: str: Account ID string
        """
        if self._harvest_account == None:
            self._harvest_account = self._get_harvest_account()
        return self._harvest_account

    @property
    def origin_email_address(self):
        """Fetch email address to use for `From` email header.

        Raises:
            MissingEnvironmentVariable: if `ORIGIN_EMAIL_ADDRESS` environment
            variable is missing

        Returns: str: Email address from which to send mail
        """
        if self._origin_email_address == None:
            self._origin_email_address = self._get_origin_email_address()
        return self._origin_email_address

    @property
    def sendgrid_api_key(self):
        """Fetches the Sendgrid API key.

        The Sendgrid API key can either be passed in directly using the
        `SENDGRID_API_KEY` environment variable or can be stored in Google's Secret
        Manger using the `SENDGRID_API_KEY_SECRET` and
        `SENDGRID_API_KEY_SECRET_VERSION` environment variables.

        Raises:
            MissingEnvironmentVariable: if one of the required environment
            variables is missing

        Returns:
            str: Sendgrid API key
        """
        if self._sendgrid_api_key == None:
            self._sendgrid_api_key = self._get_sendgrid_api_key()
        return self._sendgrid_api_key

    @property
    def bucket(self) -> str:
        """Fetches bucket from environment if one is specified.

        Returns:
            str: bucket name if specified
            None: if no bucket name specified
        """
        if self._bucket == None:
            self._bucket = self._get_bucket()
        return self._bucket

    @property
    def config_path(self) -> str:
        """Path on file system or in bucket of config file

        Raises:
            MissingEnvironmentVariable: If no `CONFIG_PATH` environment varialbe
            specified.

        Returns:
            str: Path to config
        """
        if self._config_path == None:
            self._config_path = self._get_config_path()
        return self._config_path

    @property
    def project_id(self) -> str:
        """Fetches the GCP project ID.

        Raises:
            MissingEnvironmentVariable: if GCP_PROJECT env var is missing

        Returns:
            str: GCP project ID
        """
        if self._project_id == None:
            self._project_id = self._get_project_id()
        return self._project_id

    def _get_bearer_token(self) -> str:
        """Helper function containing logic to fetch Harvest API bearer token
        using environment variables.

        Raises:
            MissingEnvironmentVariable: if needed env vars are not present

        Returns:
            str: Harvest API bearer toekn
        """
        if os.getenv(BEARER_TOKEN):
            return os.getenv(BEARER_TOKEN)
        else:
            # Use the project ID function since self.project_id hasn't been
            # instantiated yet
            bearer_token_secret = os.getenv(BEARER_TOKEN_SECRET)

            if not bearer_token_secret:
                raise MissingEnvironmentVariable(BEARER_TOKEN_SECRET)

            bearer_token_version = os.getenv(BEARER_TOKEN_SECRET_VERSION, "latest")

            version = self.secrets_client.secret_version_path(
                self._get_project_id(), bearer_token_secret, bearer_token_version
            )

            secret = self.secrets_client.access_secret_version(version)

            LOGGER.info(f"Fetched bearer token secret version {version}")

            return secret.payload.data.decode("UTF-8")

    def _get_harvest_account(self) -> str:
        """Helper function containing logic to fetch Harvest account ID
        using environment variables.

        Raises:
            MissingEnvironmentVariable: if HARVEST_ACCOUNT_ID env var is not present

        Returns:
            str: Harvest API bearer token
        """
        harvest_account = os.getenv(HARVEST_ACCOUNT_ID)
        if not harvest_account:
            raise MissingEnvironmentVariable(HARVEST_ACCOUNT_ID)

        return harvest_account

    def _get_origin_email_address(self) -> str:
        """Helper function containing logic to fetch email address to send
        email from using environment variables.

        Raises:
            MissingEnvironmentVariable: if ORIGIN_EMAIL_ADDRESS env var is not present

        Returns:
            str: Email address to send mail from
        """
        email = os.getenv(ORIGIN_EMAIL_ADDRESS)
        if not email:
            raise MissingEnvironmentVariable(ORIGIN_EMAIL_ADDRESS)

        return email

    def _get_sendgrid_api_key(self) -> str:
        """Helper function containing logic to fetch Sendgrid API key
        using environment variables.

        Required environment variables are SENDGRID_API_KEY _or_
        SENDGRID_API_KEY_SECRET with SENDGRID_API_KEY_VERSION.

        Raises:
            MissingEnvironmentVariable: if required env vars are not present

        Returns:
            str: Sendgrid API key
        """
        if os.getenv(SENDGRID_API_KEY):
            return os.getenv(SENDGRID_API_KEY)
        else:
            # Use the project ID function since self.project_id hasn't been
            # instantiated yet
            sendgrid_api_key_secret = os.getenv(SENDGRID_API_KEY_SECRET)

            if not sendgrid_api_key_secret:
                raise MissingEnvironmentVariable(SENDGRID_API_KEY_SECRET)

            sendgrid_api_key_version = os.getenv(
                SENDGRID_API_KEY_SECRET_VERSION, "latest"
            )

            version = self.secrets_client.secret_version_path(
                self._get_project_id(),
                sendgrid_api_key_secret,
                sendgrid_api_key_version,
            )

            LOGGER.debug(f"fetching secret {version}")

            secret = self.secrets_client.access_secret_version(version)

            LOGGER.info(f"Fetched secret version {version}")

            return secret.payload.data.decode("UTF-8")

    def _get_bucket(self) -> str:
        """Helper function containing logic to fetch GCS bucket
        using environment variables.

        Raises:
            MissingEnvironmentVariable: if BUCKET env var is not present

        Returns:
            str: GCS bucket name
        """
        return os.getenv(BUCKET)

    def _get_config_path(self) -> str:
        """Helper function containing logic to fetch config path
        using environment variables.

        Raises:
            MissingEnvironmentVariable: if CONFIG_PATH env var is not present

        Returns:
            str: Path to config in bucket
        """
        return os.getenv(CONFIG_PATH, "config/clients.yaml")

    def _get_project_id(self) -> str:
        """Helper function containing logic to fetch GCP project ID
        using environment variables.

        Raises:
            MissingEnvironmentVariable: if GCP_PROJECT env var is not present

        Returns:
            str: GCP project ID
        """
        project_id = os.getenv(GCP_PROJECT)
        if not project_id:
            raise MissingEnvironmentVariable(GCP_PROJECT)
        return project_id

    def _get_log_level(self) -> str:
        """Helper function containing logic to fetch log level
        using environment variables.

        Raises:
            MissingEnvironmentVariable: if LOG_LEVEL env var is not present

        Returns:
            str: log level, defaults to `info`
        """
        return os.getenv(LOG_LEVEL, "info")


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
