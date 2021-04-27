from datetime import date
from view_builder.model.table import (
    Slug,
    Category,
    Organisation,
    Geography,
    OrganisationGeography,
    Policy,
    PolicyGeography,
    PolicyOrganisation,
)


class DatasetModelFactory:
    def __init__(self):
        self._dataset_models = {}

    def register_dataset_model(self, model_class):
        self._dataset_models[model_class.dataset_name] = model_class

    def get_dataset_model(self, name, session, data: dict):
        model_class = self._dataset_models.get(name)
        if not model_class:
            raise ValueError("No matching dataset model found")
        return model_class(session, data)


factory = DatasetModelFactory()


class DatasetModel:
    def __init__(self, session, data: dict):
        self.data = data
        self.session = session

        if not data.get("slug", None):
            raise ValueError("Data missing slug field")

        if not data.get("entry-date", None):
            raise ValueError("Entry missing entry-date")

        self.data["entry_date"] = date.fromisoformat(self.data.pop("entry-date"))
        if "start-date" in self.data:
            self.data["start_date"] = date.fromisoformat(self.data.pop("start-date"))
        if "end-date" in self.data:
            self.data["end_date"] = date.fromisoformat(self.data.pop("end-date"))

        if self.data["entry_date"] > date.today():
            raise ValueError("entry-date cannot be in the future")

    def get_organisation(self, organisation):
        # Add custom exception handling if necessary
        return (
            self.session.query(Organisation)
            .filter(Organisation.organisation == organisation)
            .one()
        )

    def get_category(self, category):
        # Add custom exception handling if necessary
        return self.session.query(Category).filter(Category.category == category).one()

    def get_geography(self, geography):
        # Add custom exception handling if necessary
        return (
            self.session.query(Geography).filter(Geography.geography == geography).one()
        )


class DeveloperAgreementTypeModel(DatasetModel):

    dataset_name = "developer-agreement-type"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)
        self.slug = {
            key: data[key] for key in Slug.__table__.columns.keys() if key in self.data
        }
        self.category = {
            key: data[key]
            for key in Category.__table__.columns.keys()
            if key in self.data
        }
        if "category" not in self.category and self.dataset_name in self.data:
            self.category["category"] = self.data[self.dataset_name]
        # Add check for presence of key field ?

    def to_orm(self):
        slug = Slug(**self.slug)
        category = Category(**self.category, slug=slug)
        return [category]


factory.register_dataset_model(DeveloperAgreementTypeModel)


class DevelopmentPolicyCategoryModel(DatasetModel):

    dataset_name = "development-policy-category"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)
        self.slug = {
            key: data[key] for key in Slug.__table__.columns.keys() if key in self.data
        }
        self.category = {
            key: data[key]
            for key in Category.__table__.columns.keys()
            if key in self.data
        }
        if "category" not in self.category and self.dataset_name in self.data:
            self.category["category"] = self.data[self.dataset_name]
        # Add check for presence of key field ?

    def to_orm(self):
        slug = Slug(**self.slug)
        category = Category(**self.category, slug=slug)
        return [category]


factory.register_dataset_model(DevelopmentPolicyCategoryModel)


class LocalAuthorityDistrictModel(DatasetModel):

    dataset_name = "local-authority-district"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)
        self.slug = {
            key: data[key] for key in Slug.__table__.columns.keys() if key in self.data
        }
        self.geography = {
            key: data[key]
            for key in Geography.__table__.columns.keys()
            if key in self.data
        }

    def to_orm(self):
        slug = Slug(**self.slug)
        geography = Geography(**self.geography, slug=slug)
        organisation = self.get_organisation(self.data["organisation"])

        relationship = OrganisationGeography(
            organisation=organisation, geography=geography
        )
        return [geography, relationship]


factory.register_dataset_model(LocalAuthorityDistrictModel)


class DevelopmentPolicyModel(DatasetModel):

    dataset_name = "development-policy"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)
        self.slug = {
            key: data[key] for key in Slug.__table__.columns.keys() if key in self.data
        }
        self.policy = {
            key: data[key]
            for key in Policy.__table__.columns.keys()
            if key in self.data
        }

        if "policy" not in self.policy and self.dataset_name in self.data:
            self.policy["policy"] = self.data[self.dataset_name]

        self.categories = self.data["development-policy-categories"].split(";")
        self.organisations = self.data["organisation"].split(";")
        self.geographies = self.data["geographies"].split(";")

    def to_orm(self):
        orms = []
        slug = Slug(**self.slug)
        policy = Policy(**self.policy, slug=slug)
        policy.categories = []

        for category in self.categories:
            category_orm = self.get_category(category)
            policy.categories.append(category_orm)

        orms.append(policy)

        for org in self.organisations:
            organisation = self.get_organisation(org)
            relationship = PolicyOrganisation(organisation=organisation, policy=policy)
            orms.append(relationship)

        for geography in self.geographies:
            geography_orm = self.get_geography("local-authority-district:" + geography)
            relationship = PolicyGeography(geography=geography_orm, policy=policy)
            orms.append(relationship)

        return orms


factory.register_dataset_model(DevelopmentPolicyModel)
