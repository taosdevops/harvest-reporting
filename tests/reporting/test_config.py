import os
import unittest
import unittest.mock

from google.cloud.secretmanager import SecretManagerServiceClient
from google.cloud.secretmanager_v1.types import (AccessSecretVersionResponse,
                                                 SecretPayload)

import reporting.config


class TestEnvironmentConfiguration(unittest.TestCase):
    # def test_initializing_secrets_client(self):
    #     env_config = reporting.config.EnvironmentConfiguration()
    #     assert type(env_config.secrets_client) == SecretManagerServiceClient

    def test_get_bearer_token(self) -> str:
        os.environ[reporting.config.BEARER_TOKEN] = "dummy_token"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.bearer_token == "dummy_token"

        del os.environ[reporting.config.BEARER_TOKEN]

        os.environ["GCP_PROJECT"] = "dummy_project"
        os.environ["BEARER_TOKEN_SECRET"] = "dummy_secret"
        os.environ["BEARER_TOKEN_VERSION"] = "dummy_version"

        env_config_2 = reporting.config.EnvironmentConfiguration()

        client = unittest.mock.MagicMock()
        client.secret_version_path.return_value = "dummy_secret_path"
        client.access_secret_version.return_value = AccessSecretVersionResponse(
            name="dummy_secret", payload=SecretPayload(data=b"dummy_token")
        )

        env_config_2.secrets_client = client

        assert env_config_2.bearer_token == "dummy_token"
        env_config_2.secrets_client.secret_version_path.assert_called_once()
        env_config_2.secrets_client.secret_version_path.assert_called_with(
            "dummy_project", "dummy_secret", "dummy_version"
        )
        env_config_2.secrets_client.access_secret_version.assert_called_once()
        env_config_2.secrets_client.access_secret_version.assert_called_with(
            "dummy_secret_path"
        )

        del os.environ["GCP_PROJECT"]
        del os.environ["BEARER_TOKEN_SECRET"]
        del os.environ["BEARER_TOKEN_VERSION"]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        with self.assertRaises(reporting.config.MissingEnvironmentVariable):
            token = env_config_missing.bearer_token

    def test_get_sendgrid_api_key(self) -> str:
        os.environ[reporting.config.SENDGRID_API_KEY] = "dummy_sg_key"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.sendgrid_api_key == "dummy_sg_key"

        del os.environ[reporting.config.SENDGRID_API_KEY]

        os.environ[reporting.config.GCP_PROJECT] = "dummy_sg_project"
        os.environ[reporting.config.SENDGRID_API_KEY_SECRET] = "dummy_sg_secret"
        os.environ[
            reporting.config.SENDGRID_API_KEY_SECRET_VERSION
        ] = "dummy_sg_version"

        env_config_2 = reporting.config.EnvironmentConfiguration()

        client = unittest.mock.MagicMock()
        client.secret_version_path.return_value = "dummy_sg_secret_path"
        client.access_secret_version.return_value = AccessSecretVersionResponse(
            name="dummy_sg_secret", payload=SecretPayload(data=b"dummy_sg_token")
        )

        env_config_2.secrets_client = client

        assert env_config_2.sendgrid_api_key == "dummy_sg_token"
        env_config_2.secrets_client.secret_version_path.assert_called_once()
        env_config_2.secrets_client.secret_version_path.assert_called_with(
            "dummy_sg_project", "dummy_sg_secret", "dummy_sg_version"
        )
        env_config_2.secrets_client.access_secret_version.assert_called_once()
        env_config_2.secrets_client.access_secret_version.assert_called_with(
            "dummy_sg_secret_path"
        )

        del os.environ[reporting.config.GCP_PROJECT]
        del os.environ[reporting.config.SENDGRID_API_KEY_SECRET]
        del os.environ[reporting.config.SENDGRID_API_KEY_SECRET_VERSION]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        with self.assertRaises(reporting.config.MissingEnvironmentVariable):
            token = env_config_missing.sendgrid_api_key

    def test_get_harvest_account(self) -> str:
        os.environ[reporting.config.HARVEST_ACCOUNT_ID] = "dummy_harvest_account"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.harvest_account == "dummy_harvest_account"

        del os.environ[reporting.config.HARVEST_ACCOUNT_ID]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        with self.assertRaises(reporting.config.MissingEnvironmentVariable):
            token = env_config_missing.harvest_account

    def test_get_log_level(self) -> str:
        os.environ[reporting.config.LOG_LEVEL] = "test"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.log_level == "test"

        del os.environ[reporting.config.LOG_LEVEL]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        assert env_config_missing.log_level == "info"

    def test_get_project(self) -> str:
        os.environ[reporting.config.GCP_PROJECT] = "test-project"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.project_id == "test-project"

        del os.environ[reporting.config.GCP_PROJECT]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        with self.assertRaises(reporting.config.MissingEnvironmentVariable):
            token = env_config_missing.project_id

    def test_get_bucket(self) -> str:
        os.environ[reporting.config.BUCKET] = "test-bucket"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.bucket == "test-bucket"

        del os.environ[reporting.config.BUCKET]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        assert env_config_missing.bucket == None

    def test_get_config_path(self) -> str:
        os.environ[reporting.config.CONFIG_PATH] = "test-config.yaml"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.config_path == "test-config.yaml"

        del os.environ[reporting.config.CONFIG_PATH]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        assert env_config_missing.config_path == "config/clients.yaml"

    def test_get_origin_email_address(self) -> str:
        os.environ[reporting.config.ORIGIN_EMAIL_ADDRESS] = "test@example.com"

        env_config = reporting.config.EnvironmentConfiguration()

        assert env_config.origin_email_address == "test@example.com"

        del os.environ[reporting.config.ORIGIN_EMAIL_ADDRESS]

        env_config_missing = reporting.config.EnvironmentConfiguration()

        with self.assertRaises(reporting.config.MissingEnvironmentVariable):
            token = env_config_missing.origin_email_address
