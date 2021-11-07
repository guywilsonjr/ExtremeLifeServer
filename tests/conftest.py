import pytest
from pytest_mock import MockerFixture
from components.dbaccess import db

@pytest.fixture
def mock_uuid(mocker: MockerFixture) -> str:
    _mock_uuid = "mocked_channel_name"
    class mock_uuid:
        hex = _mock_uuid
    mocker.patch("uuid.UUID").return_value = mock_uuid
    return _mock_uuid


@pytest.fixture
def setup_db(mocker: MockerFixture):
    return db.setup_db("configs/db_config")