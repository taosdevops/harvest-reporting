from unittest.mock import MagicMock, patch

import pytest

import reporting.notifications


def test_assert_pubsub_publish_called_with_params():
    reporting.notifications.pubsub_v1.PublisherClient = MagicMock()
    reporting.notifications.pubsub_v1.PublisherClient.return_value.topic_path.return_value = "topic_path"
    reporting.notifications.publish_to_pubsub(project_id="project_id", topic_id="topic_id", payload={"payload": "oui"}, attributes={"attributes": "yes"})
    reporting.notifications.pubsub_v1.PublisherClient.return_value.publish.assert_called_with('topic_path', b'{"payload": "oui"}', attributes='yes')


def test_assert_bad_pubsub_publish_raises_RuntimeError():
    reporting.notifications.pubsub_v1.PublisherClient = MagicMock()
    reporting.notifications.pubsub_v1.PublisherClient.return_value.topic_path.return_value = "topic_path"
    reporting.notifications.pubsub_v1.PublisherClient.return_value.publish.side_effect = Exception
    with pytest.raises(RuntimeError):
        reporting.notifications.publish_to_pubsub(project_id="project_id", topic_id="topic_id", payload={"payload": "oui"}, attributes={"attributes": "yes"})
