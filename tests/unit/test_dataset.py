from view_builder.model.dataset import DatasetORM, DeveloperAgreementTypeORM
import datetime
import pytest


def test_dataset_orm_no_slug():
    test_data = {
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05"
    }

    with pytest.raises(ValueError, match="^Data missing slug field$"):
        DatasetORM(test_data)


def test_dataset_orm_no_entry_date():
    test_data = {
        "start-date": "2020-10-05",
        "slug": "dataset/AAA"
    }

    with pytest.raises(ValueError, match="^Entry missing entry-date$"):
        DatasetORM(test_data)


def test_dataset_orm_future_entry_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    test_data = {
        "entry-date": tomorrow.isoformat(),
        "start-date": "2020-10-05",
        "slug": "dataset/AAA"
    }

    with pytest.raises(ValueError, match="^entry-date cannot be in the future$"):
        DatasetORM(test_data)


def test_development_agreement_type_orm():
    test_data = {
        "developer-agreement-type": "AAA",
        "name": "BBB",
        "entry-date": "2020-10-04",
        "start-date": "2020-10-05",
        "slug": "developer-agreement-type/AAA",
        "extra_field": "CCC"
    }

    developer_agreement_type_orm = DeveloperAgreementTypeORM(test_data)
    orm_obj = developer_agreement_type_orm.to_orm()
    assert(orm_obj.reference == test_data["developer-agreement-type"])
    assert(orm_obj.name == test_data["name"])
    assert(orm_obj.slug.slug == test_data["slug"])
