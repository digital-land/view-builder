from view_builder.model.dataset import (
    DatasetModel,
    DatasetModelFactory,
    DeveloperAgreementTypeModel,
    LocalAuthorityDistrictModel,
)
from view_builder.model.table import Organisation, Geography, OrganisationGeography
import datetime
import pytest


class DummyModel:
    dataset_name = "dummy-dataset"

    def __init__(self, *args):
        pass


def test_dataset_model_factory_register_and_get():
    test_factory = DatasetModelFactory()
    test_factory.register_dataset_model(DummyModel)
    output = test_factory.get_dataset_model("dummy-dataset", None, {"check": True})

    assert isinstance(output, DummyModel)


def test_dataset_model_factory_no_class():
    test_factory = DatasetModelFactory()
    with pytest.raises(ValueError, match="^No matching dataset model found$"):
        test_factory.get_dataset_model("test_class", None, {"check": True})


def test_dataset_model_date_mapping():
    test_data = {
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "slug": "dataset/AAA",
    }
    DatasetModel(None, test_data)


def test_dataset_model_no_slug():
    test_data = {"entry-date": "2020-10-04", "start-date": "2020-10-05"}

    with pytest.raises(ValueError, match="^Data missing slug field$"):
        DatasetModel(None, test_data)


def test_dataset_model_no_entry_date():
    test_data = {"start-date": "2020-10-05", "slug": "dataset/AAA"}

    with pytest.raises(ValueError, match="^Entry missing entry-date$"):
        DatasetModel(None, test_data)


def test_dataset_model_future_entry_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    test_data = {
        "entry-date": tomorrow.isoformat(),
        "start-date": "2020-10-05",
        "slug": "dataset/AAA",
    }

    with pytest.raises(ValueError, match="^entry-date cannot be in the future$"):
        DatasetModel(None, test_data)


def test_development_agreement_type_model():
    test_data = {
        "developer-agreement-type": "AAA",
        "name": "BBB",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "slug": "developer-agreement-type/AAA",
        "extra_field": "CCC",
    }

    developer_agreement_type_orm = DeveloperAgreementTypeModel(None, test_data)
    orm_obj_list = developer_agreement_type_orm.to_orm()

    assert len(orm_obj_list) == 1
    orm_obj = orm_obj_list[0]

    assert orm_obj.reference == test_data["developer-agreement-type"]
    assert orm_obj.name == test_data["name"]
    assert orm_obj.start_date == test_data["start_date"]
    assert orm_obj.slug.slug == test_data["slug"]


def test_local_authority_district_model(mocker):
    test_data = {
        "name": "BBB",
        "geography": "local-authority-district:AAA",
        "geometry": "MULTIPOLYGON (((-1.111111 2.222222, 3.333333333 4.444444444)))",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisation": "government-organisation:CCC",
        "slug": "local-authority-district/AAA",
        "extra_field": "ZZZ",
    }
    test_organisation = Organisation(
        id=1, organisation="government-organisation:CCC", name="some organisation"
    )
    mocker.patch(
        "view_builder.model.dataset.LocalAuthorityDistrictModel.get_organisation",
        lambda self, org: test_organisation,
    )
    local_authority_district_orm = LocalAuthorityDistrictModel(None, test_data)
    orm_obj_list = local_authority_district_orm.to_orm()

    assert len(orm_obj_list) == 2
    first_orm_obj = orm_obj_list[0]

    assert isinstance(first_orm_obj, Geography)
    first_orm_obj.geography == test_data["geography"]
    first_orm_obj.geometry == test_data["geometry"]
    first_orm_obj.slug.slug == test_data["slug"]

    second_orm_obj = orm_obj_list[1]
    assert isinstance(second_orm_obj, OrganisationGeography)
    assert second_orm_obj.geography == first_orm_obj
    assert second_orm_obj.organisation == test_organisation
