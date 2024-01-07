import uuid
import pytest
from entities import RequestQuery, ResponseQuery
from main import correct_request


@pytest.fixture
def waiting_response():
    return ResponseQuery(
        id=uuid.uuid4(),
        operation_type="operation",
        file="path/to/file",
    )


class TestQuery:
    def test_correct_request_matching_query(self, waiting_response):
        request_query = RequestQuery(
            id=waiting_response.id,
            operation_type=waiting_response.operation_type,
            file=waiting_response.file,
            output_path="path/to",
            params={"param": "value"},
        )
        assert correct_request(request_query, waiting_response) == True

    def test_incorrect_id(self, waiting_response):
        request_query = RequestQuery(
            id=uuid.uuid4(),
            operation_type=waiting_response.operation_type,
            file=waiting_response.file,
            output_path="path/to",
            params={"param": "value"},
        )
        with pytest.raises(ValueError):
            correct_request(request_query, waiting_response)

    def test_incorrect_operation_type(self, waiting_response):
        request_query = RequestQuery(
            id=waiting_response.id,
            operation_type="different_operation",
            file=waiting_response.file,
            output_path="path/to",
            params={"param": "value"},
        )
        with pytest.raises(ValueError):
            correct_request(request_query, waiting_response)

    def test_incorrect_output_path(self, waiting_response):
        request_query = RequestQuery(
            id=waiting_response.id,
            operation_type=waiting_response.operation_type,
            file=waiting_response.file,
            output_path="different/path",
            params={"param": "value"},
        )
        with pytest.raises(ValueError):
            correct_request(request_query, waiting_response)
