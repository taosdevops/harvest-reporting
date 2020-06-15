import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import logging

from google.cloud.secretmanager import SecretManagerServiceClient


LOGGER = logging.getLogger(__name__)


class MissingEnvironmentVariable(BaseException):
    def __init__(self, env_var):
        self.env_var = env_var
        super().__init__(f"Missing environment variable {env_var}")


# TODO: This needs to be a singleton. There's no point in fetching the secrets every time this class is instantiated.
class EnvironmentConfiguration(object):
    def __init__(self):
        self.secrets_client = SecretManagerServiceClient()
        self.log_level = self._get_log_level()
        self.bearer_token = self._get_bearer_token()
        self.harvest_account = self._get_harvest_account()
        self.origin_email_address = self._get_origin_email_address()
        self.sendgrid_api_key = self._get_sendgrid_api_key()
        self.bucket = self._get_bucket()
        self.config_path = self._get_config_path()
        self.project_id = self._get_project_id()
        self.function_region = self._get_function_region()
        self.function_name = self._get_function_name()

    def _get_bearer_token(self) -> str:
        if os.getenv("BEARER_TOKEN"):
            return os.getenv("BEARER_TOKEN")
        else:
            self.secrets_client = SecretManagerServiceClient()

            # Use the project ID function since self.project_id hasn't been
            # instantiated yet
            bearer_token_secret = os.getenv("BEARER_TOKEN_SECRET")

            if not bearer_token_secret:
                raise MissingEnvironmentVariable("BEARER_TOKEN_SECRET")

            bearer_token_version = os.getenv("BEARER_TOKEN_VERSION", "latest")

            version = self.secrets_client.secret_version_path(
                self._get_project_id(), bearer_token_secret, bearer_token_version
            )

            secret = self.secrets_client.access_secret_version(version)

            LOGGER.info(f"Fetched bearer token secret version {version}")

            return secret.payload.data.decode("UTF-8")

    def _get_harvest_account(self) -> str:
        harvest_account = os.getenv("HARVEST_ACCOUNT_ID")
        if not harvest_account:
            raise MissingEnvironmentVariable("HARVEST_ACCOUNT_ID")

        return harvest_account

    def _get_origin_email_address(self) -> str:
        email = os.getenv("ORIGIN_EMAIL_ADDRESS")
        if not email:
            raise MissingEnvironmentVariable("ORIGIN_EMAIL_ADDRESS")

        return email

    def _get_sendgrid_api_key(self) -> str:
        if os.getenv("SENDGRID_API_TOKEN"):
            return os.getenv("SENDGRID_API_TOKEN")
        else:
            # Use the project ID function since self.project_id hasn't been
            # instantiated yet
            sendgrid_api_key_secret = os.getenv("SENDGRID_API_KEY_SECRET")

            if not sendgrid_api_key_secret:
                raise MissingEnvironmentVariable("SENDGRID_API_KEY_SECRET")

            sendgrid_api_key_version = os.getenv("SENDGRID_API_KEY_VERSION", "latest")

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
        return os.getenv("BUCKET")

    def _get_config_path(self) -> str:
        return os.getenv("CONFIG_PATH", "config/clients.yaml")

    def _get_project_id(self) -> str:
        project_id = os.getenv("GCP_PROJECT")
        if not project_id:
            raise MissingEnvironmentVariable("GCP_PROJECT")
        return project_id

    def _get_function_region(self) -> str:
        region = os.getenv("FUNCTION_REGION")
        if not region and not self.bearer_token and not self.log_stdout:
            raise MissingEnvironmentVariable("FUNCTION_REGION")
        return region

    def _get_function_name(self) -> str:
        name = os.getenv("FUNCTION_NAME")
        if not name and not self.bearer_token and not self.log_stdout:
            raise MissingEnvironmentVariable("FUNCTION_NAME")
        return name

    def _get_log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "false")


@dataclass
class VerificationConfig(object):
    email: Optional[List[str]] = field(default_factory=list)
    slack: Optional[str] = ""
    teams: Optional[str] = ""


@dataclass
class RecipientsConfig(object):
    templateId: Optional[str] = ""
    sendVerificationConfig: Optional[VerificationConfig] = None


@dataclass
class Recipients(object):
    config: Optional[RecipientsConfig] = None
    emails: Optional[List[str]] = field(default_factory=list)
    slack: Optional[List[str]] = field(default_factory=list)
    teams: Optional[List[str]] = field(default_factory=list)


@dataclass
class Customer(object):

    name: str
    hours: Optional[int] = ""
    recipients: Optional[Recipients] = None

@dataclass
class ReporterConfig(object):
    customers: List[Customer]
    recipients: Recipients
    exceptions: Recipients
    customer_filter: Optional[List[str]] = field(default_factory=list)
