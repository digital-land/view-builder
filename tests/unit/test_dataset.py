from view_builder.model.dataset import (
    DatasetModel,
    DatasetModelFactory,
    DeveloperAgreementTypeModel,
    GeographyDatasetModel,
    DevelopmentPolicyModel,
    DevelopmentPlanDocumentModel,
    DocumentModel,
    BrownfieldLandModel,
)
from view_builder.model.table import (
    Entity,
    Organisation,
    Geography,
    GeographyMetric,
    GeographyCategory,
    OrganisationGeography,
    Category,
    Policy,
    PolicyOrganisation,
    PolicyGeography,
    PolicyDocument,
    PolicyCategory,
    Document,
    DocumentGeography,
    DocumentOrganisation,
    DocumentCategory,
)
import datetime
import pytest


class DummyModel:
    dataset_name = "dummy-dataset"

    def __init__(self, *args):
        pass


dummy_organisation = Organisation(
    entity=1, organisation="government-organisation:CCC", name="some organisation"
)
dummy_geography = Geography(
    entity=1, geography="government-geography:A000000", name="some geography"
)
dummy_category = Category(entity=1, category="A category", name="some category")
dummy_policy = Policy(entity=1, policy="A policy", name="some policy")
dummy_entity = Entity(entity=1)


@pytest.fixture
def mock_get_organisation(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_organisation",
        lambda self, org: dummy_organisation,
    )
    return mock_db


@pytest.fixture
def mock_get_geography(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_geography",
        lambda self, geography: dummy_geography,
    )
    return mock_db


@pytest.fixture
def mock_get_category(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_category",
        lambda self, category, type: dummy_category,
    )
    return mock_db


@pytest.fixture
def mock_get_policy(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_policy",
        lambda self, policy: dummy_policy,
    )
    return mock_db


@pytest.fixture
def mock_get_entity(mocker):
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_entity",
        lambda self, entity: dummy_entity,
    )
    return mock_db


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
        "entity": 1,
    }
    DatasetModel(None, test_data)


def test_dataset_model_no_entity():
    test_data = {"entry-date": "2020-10-04", "start-date": "2020-10-05"}

    with pytest.raises(ValueError, match="^Data missing entity field$"):
        DatasetModel(None, test_data)


def test_dataset_model_no_entry_date():
    test_data = {"start-date": "2020-10-05", "entity": 1}

    with pytest.raises(ValueError, match="^Entry missing entry-date$"):
        DatasetModel(None, test_data)


def test_dataset_model_future_entry_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    test_data = {
        "entry-date": tomorrow.isoformat(),
        "start-date": "2020-10-05",
        "entity": 1,
    }

    with pytest.raises(ValueError, match="^entry-date cannot be in the future$"):
        DatasetModel(None, test_data)


# Test to cover CategoryDatasetModel
def test_development_agreement_type_model():
    test_data = {
        "developer-agreement-type": "AAA",
        "name": "BBB",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "entity": 1,
        "extra_field": "CCC",
    }

    developer_agreement_type_orm = DeveloperAgreementTypeModel(None, test_data)
    orm_obj_list = developer_agreement_type_orm.to_orm()

    assert len(orm_obj_list) == 1
    orm_obj = orm_obj_list[0]

    assert orm_obj.name == test_data["name"]
    assert orm_obj.start_date == test_data["start_date"]
    assert orm_obj.entity == test_data["entity"]


def test_geography_dataset_model(mocker):
    test_data = {
        "name": "BBB",
        "geography": "local-authority-district:AAA",
        "geometry": "MULTIPOLYGON (((-1.111111 2.222222, 3.333333333 4.444444444)))",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisation": "government-organisation:CCC",
        "entity": 1,
        "extra_field": "ZZZ",
    }
    test_organisation = Organisation(
        entity=1, organisation="government-organisation:CCC", name="some organisation"
    )
    mocker.patch(
        "view_builder.model.dataset.GeographyDatasetModel.get_organisation",
        lambda self, org: test_organisation,
    )
    geography_model = GeographyDatasetModel(None, test_data)
    orm_obj_list = geography_model.to_orm()

    assert len(orm_obj_list) == 2
    first_orm_obj = orm_obj_list[0]

    assert isinstance(first_orm_obj, Geography)
    assert first_orm_obj.geography == test_data["geography"]
    assert first_orm_obj.geometry == test_data["geometry"]
    assert first_orm_obj.entity == test_data["entity"]

    second_orm_obj = orm_obj_list[1]
    assert isinstance(second_orm_obj, OrganisationGeography)
    assert second_orm_obj.geography == first_orm_obj
    assert second_orm_obj.organisation == test_organisation


@pytest.mark.usefixtures("mock_get_organisation")
@pytest.mark.usefixtures("mock_get_geography")
@pytest.mark.usefixtures("mock_get_category")
def test_development_policy_model(
    mock_get_organisation, mock_get_geography, mock_get_category
):
    test_data = {
        "development-policy": "AAA",
        "name": "BBB",
        "development-policy-categories": "A;B",
        "geographies": "A000000;B1111111",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisation": "government-organisation:CCC",
        "entity": 1,
        "notes": "ZZZ",
        "description": "a description",
    }

    development_policy_orm = DevelopmentPolicyModel(None, test_data)
    orm_obj_list = development_policy_orm.to_orm()

    assert len(orm_obj_list) == 6

    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Policy)
    assert first_orm_obj.policy == test_data["development-policy"]
    assert first_orm_obj.name == test_data["name"]
    assert first_orm_obj.notes == test_data["notes"]
    assert first_orm_obj.description == test_data["description"]
    assert first_orm_obj.entity == test_data["entity"]

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyCategory)
                and x.category == dummy_category
                and x.policy == first_orm_obj
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyOrganisation)
                and x.policy == first_orm_obj
                and x.organisation == dummy_organisation
            ]
        )
        == 1
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyGeography)
                and x.policy == first_orm_obj
                and x.geography == dummy_geography
            ]
        )
        == 2
    )


@pytest.mark.usefixtures("mock_get_organisation")
@pytest.mark.usefixtures("mock_get_geography")
@pytest.mark.usefixtures("mock_get_category")
@pytest.mark.usefixtures("mock_get_policy")
def test_development_plan_document_model(
    mock_get_organisation, mock_get_geography, mock_get_category, mock_get_policy
):
    test_data = {
        "development-plan-document": "AAA",
        "name": "BBB",
        "development-plan-types": "A;B",
        "development-policies": "pol-a;pol-b",
        "geographies": "A000000;B1111111",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisations": "government-organisation:CCC",
        "document-url": "www.example.com",
        "entity": 1,
        "notes": "ZZZ",
        "description": "a description",
    }

    development_plan_doc_orm = DevelopmentPlanDocumentModel(None, test_data)
    orm_obj_list = development_plan_doc_orm.to_orm()

    assert len(orm_obj_list) == 8

    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Document)
    assert first_orm_obj.document == test_data["development-plan-document"]
    assert first_orm_obj.name == test_data["name"]
    assert first_orm_obj.notes == test_data["notes"]
    assert first_orm_obj.description == test_data["description"]
    assert first_orm_obj.entity == test_data["entity"]
    assert first_orm_obj.document_url == test_data["document-url"]

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentCategory)
                and x.document == first_orm_obj
                and x.category == dummy_category
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyDocument)
                and x.document == first_orm_obj
                and x.policy == dummy_policy
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentOrganisation)
                and x.document == first_orm_obj
                and x.organisation == dummy_organisation
            ]
        )
        == 1
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentGeography)
                and x.document == first_orm_obj
                and x.geography == dummy_geography
            ]
        )
        == 2
    )


@pytest.fixture
def mock_get_geography_entity(mocker):
    ret = dummy_entity
    ret.geography = [dummy_geography]
    mock_db = mocker.patch(
        "view_builder.model.dataset.DatasetModel.get_entity",
        lambda self, entity: ret,
    )
    return mock_db


@pytest.mark.usefixtures("mock_get_organisation")
@pytest.mark.usefixtures("mock_get_geography_entity")
@pytest.mark.usefixtures("mock_get_category")
@pytest.mark.usefixtures("mock_get_policy")
def test_document_model(
    mock_get_organisation, mock_get_geography_entity, mock_get_category, mock_get_policy
):
    test_data = {
        "document": "AAA",
        "name": "BBB",
        "document-types": "A;B",
        "development-policies": "pol-a;pol-b",
        "geographies": "1;2",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisations": "local-authority-eng:CCC",
        "document-url": "www.example.com",
        "entity": 3,
        "notes": "ZZZ",
        "description": "a description",
    }

    doc_orm = DocumentModel(None, test_data)
    orm_obj_list = doc_orm.to_orm()

    assert len(orm_obj_list) == 8

    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Document)
    assert first_orm_obj.document == test_data["document"]
    assert first_orm_obj.name == test_data["name"]
    assert first_orm_obj.notes == test_data["notes"]
    assert first_orm_obj.description == test_data["description"]
    assert first_orm_obj.entity == test_data["entity"]
    assert first_orm_obj.document_url == test_data["document-url"]

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentCategory)
                and x.document == first_orm_obj
                and x.category == dummy_category
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, PolicyDocument)
                and x.document == first_orm_obj
                and x.policy == dummy_policy
            ]
        )
        == 2
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentOrganisation)
                and x.document == first_orm_obj
                and x.organisation == dummy_organisation
            ]
        )
        == 1
    )

    assert (
        len(
            [
                x
                for x in orm_obj_list
                if isinstance(x, DocumentGeography)
                and x.document == first_orm_obj
                and x.geography == dummy_geography
            ]
        )
        == 2
    )


@pytest.mark.usefixtures("mock_get_organisation")
def test_brownfield_land_model(mocker, mock_get_organisation):
    test_data = {
        "name": "BBB",
        "site": "a site",
        "point": "POINT (((-1.111111 2.222222)))",
        "planning-permission-type": "Full planning Permission",
        "planning-permission-status": "not permissioned",
        "ownership-status": "owned by a public authority",
        "deliverable": "yes",
        "hazardous-substances": "yes",
        "maximum-net-dwellings": "4",
        "minimum-net-dwellings": "5",
        "planning-permission-date": "2016-07-13",
        "planning-permission-history": "www.example.com",
        "hectares": "7",
        "site-address": "an address",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "organisation": "government-organisation:CCC",
        "entity": 1,
        "extra_field": "ZZZ",
    }

    test_categories = set()
    test_metrics = set()
    for field in BrownfieldLandModel.category_fields:
        test_categories.add(test_data[field].replace(" ", "-").lower())

    for field in BrownfieldLandModel.site_category_fields:
        test_categories.add(field)

    for metric in BrownfieldLandModel.metric_fields:
        print(test_data[metric])
        test_metrics.add(str(test_data[metric]))

    mocker.patch(
        "view_builder.model.dataset.BrownfieldLandModel.get_category",
        lambda self, category, type: Category(
            entity=1, category=category, name=category
        ),
    )

    brownfield_orm = BrownfieldLandModel(None, test_data)
    orm_obj_list = brownfield_orm.to_orm()
    first_orm_obj = orm_obj_list[0]
    assert isinstance(first_orm_obj, Geography)

    for orm_obj in orm_obj_list:
        if isinstance(orm_obj, GeographyCategory):
            assert orm_obj.category.category in test_categories
            test_categories.remove(orm_obj.category.category)

    for orm_obj in orm_obj_list:
        if isinstance(orm_obj, GeographyMetric):
            assert orm_obj.metric.value in test_metrics
            test_metrics.remove(orm_obj.metric.value)
