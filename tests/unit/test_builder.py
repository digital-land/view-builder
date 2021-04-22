import view_builder.builder
import pytest
from view_builder.builder import ViewBuilder
from unittest.mock import call


@pytest.fixture
def mock_session(mocker):
    mock_session = mocker.patch.object(view_builder.builder, "Session", autospec=True)
    # To ensure mock session replaces Session in 'with' block usage
    mock_session.return_value.__enter__.return_value = mock_session
    return mock_session


@pytest.mark.usefixtures("mock_session")
def test_view_builder(mock_session):
    test_items = [[{"obj1": "value1"}], [{"obj2": "value2"}]]
    test_builder = ViewBuilder(engine=None, item_mapper=lambda x, y: y)
    test_builder.build_model("test_dataset", test_items)
    mock_session.add.assert_has_calls([call(test_items[0][0]), call(test_items[1][0])])
