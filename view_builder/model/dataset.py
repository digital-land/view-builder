import logging
from datetime import date
from sqlalchemy.orm.exc import NoResultFound
from view_builder.model.table import (
    Entity,
    Category,
    Organisation,
    Geography,
    GeographyCategory,
    GeographyMetric,
    OrganisationGeography,
    Policy,
    PolicyGeography,
    PolicyOrganisation,
    PolicyCategory,
    PolicyDocument,
    Document,
    DocumentGeography,
    DocumentOrganisation,
    DocumentCategory,
    Metric,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("dataset")


class RelationshipError(Exception):
    pass


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
    dataset_name = None
    typology = None

    def __init__(self, session, data: dict):
        self.data = data
        self.session = session

        if not data.get("entity", None):
            raise ValueError("Data missing entity field")

        if not data.get("entry-date", None):
            raise ValueError("Entry missing entry-date")

        self.data["entry_date"] = date.fromisoformat(self.data.pop("entry-date"))
        if "start-date" in self.data:
            self.data["start_date"] = date.fromisoformat(self.data.pop("start-date"))
        if "end-date" in self.data:
            self.data["end_date"] = date.fromisoformat(self.data.pop("end-date"))

        if self.data["entry_date"] > date.today():
            raise ValueError("entry-date cannot be in the future")

        self.entity = {
            key: data[key]
            for key in Entity.__table__.columns.keys()
            if key in self.data
        }

        self.entity["dataset"] = self.dataset_name
        self.entity["typology"] = self.typology

    def to_orm(self, allow_broken_relationships=False):
        raise NotImplementedError()

    def get_organisation(self, organisation):
        return (
            self.session.query(Organisation)
            .filter(Organisation.organisation == organisation)
            .one()
        )

    def get_category(self, category, type):
        return (
            self.session.query(Category)
            .filter(Category.category == category, Category.type == type)
            .one()
        )

    def get_geography(self, geography):
        return (
            self.session.query(Geography).filter(Geography.geography == geography).one()
        )

    def get_entity(self, entity):
        return self.session.query(Entity).filter(Entity.entity == entity).one()

    def get_policy(self, policy):
        return self.session.query(Policy).filter(Policy.policy == policy).one()

    def find_relation(self, get_relation_func, from_item, to_item, allow_broken):
        try:
            orm = get_relation_func(to_item)
        except NoResultFound:
            message = "Relationship could not be formed between {} and {}".format(
                from_item.entity, to_item
            )
            if allow_broken:
                logger.debug(message)
                orm = None
            else:
                raise RelationshipError(message)

        return orm


class CategoryDatasetModel(DatasetModel):

    dataset_name = None
    typology = "category"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)

        self.category = {
            key: data[key]
            for key in Category.__table__.columns.keys()
            if key in self.data
        }
        if "category" not in self.category and self.dataset_name in self.data:
            self.category["category"] = self.data[self.dataset_name]

        self.category["type"] = self.dataset_name

    def to_orm(self, allow_broken_relationships=False):
        entity = Entity(**self.entity)
        category = Category(**self.category, entity_rel=entity)
        return [category]


class GeographyDatasetModel(DatasetModel):

    dataset_name = None
    typology = "geography"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)

        self.geography = {
            key: data[key]
            for key in Geography.__table__.columns.keys()
            if key in self.data
        }
        self.geography["type"] = self.dataset_name

    def to_orm(self, allow_broken_relationships=False):
        orms = []
        entity = Entity(**self.entity)
        geography = Geography(**self.geography, entity_rel=entity)
        orms.append(geography)

        if "organisation" in self.data and self.data["organisation"]:
            organisation = self.find_relation(
                self.get_organisation,
                geography,
                self.data["organisation"],
                allow_broken_relationships,
            )

            if organisation:
                relationship = OrganisationGeography(
                    organisation=organisation, geography=geography
                )
                orms.append(relationship)

        return orms


class DeveloperAgreementTypeModel(CategoryDatasetModel):

    dataset_name = "developer-agreement-type"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(DeveloperAgreementTypeModel)


class DevelopmentPolicyCategoryModel(CategoryDatasetModel):

    dataset_name = "development-policy-category"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(DevelopmentPolicyCategoryModel)


class DevelopmentPlanTypeModel(CategoryDatasetModel):

    dataset_name = "development-plan-type"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(DevelopmentPlanTypeModel)


class DocumentTypeModel(CategoryDatasetModel):

    dataset_name = "document-type"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(DocumentTypeModel)


class OwnershipStatusModel(CategoryDatasetModel):

    dataset_name = "ownership-status"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(OwnershipStatusModel)


class SiteCategoryModel(CategoryDatasetModel):

    dataset_name = "site-category"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(SiteCategoryModel)


class PlanningPermissionStatusModel(CategoryDatasetModel):

    dataset_name = "planning-permission-status"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(PlanningPermissionStatusModel)


class PlanningPermissionTypeModel(CategoryDatasetModel):

    dataset_name = "planning-permission-type"

    def __init__(self, session, data: dict):
        CategoryDatasetModel.__init__(self, session, data)


factory.register_dataset_model(PlanningPermissionTypeModel)


class LocalAuthorityDistrictModel(GeographyDatasetModel):

    dataset_name = "local-authority-district"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(LocalAuthorityDistrictModel)


class ConservationAreaModel(GeographyDatasetModel):

    dataset_name = "conservation-area"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(ConservationAreaModel)


class DevelopmentPolicyModel(DatasetModel):

    dataset_name = "development-policy"
    typology = "policy"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)

        self.policy = {
            key: data[key]
            for key in Policy.__table__.columns.keys()
            if key in self.data
        }

        if "policy" not in self.policy and self.dataset_name in self.data:
            self.policy["policy"] = self.data[self.dataset_name]

        self.categories = (
            self.data["development-policy-categories"].split(";")
            if "development-policy-categories" in self.data
            else []
        )
        self.organisations = (
            self.data["organisation"].split(";") if "organisation" in self.data else []
        )
        self.geographies = (
            self.data["geographies"].split(";") if "geographies" in self.data else []
        )

    def to_orm(self, allow_broken_relationships=False):
        orms = []
        entity = Entity(**self.entity)
        policy = Policy(**self.policy, entity_rel=entity)

        orms.append(policy)

        def category_callback(category):
            return self.get_category(
                category=category, type="development-policy-category"
            )

        for category in self.categories:
            category_orm = self.find_relation(
                category_callback, policy, category, allow_broken_relationships
            )
            if category_orm:
                relationship = PolicyCategory(category=category_orm, policy=policy)
                orms.append(relationship)

        for org in self.organisations:
            org_orm = self.find_relation(
                self.get_organisation, policy, org, allow_broken_relationships
            )
            if org_orm:
                relationship = PolicyOrganisation(organisation=org_orm, policy=policy)
                orms.append(relationship)

        for geography in self.geographies:
            geography_orm = self.find_relation(
                self.get_geography,
                policy,
                "local-authority-district:" + geography,
                allow_broken_relationships,
            )
            if geography_orm:
                relationship = PolicyGeography(geography=geography_orm, policy=policy)
                orms.append(relationship)

        return orms


factory.register_dataset_model(DevelopmentPolicyModel)


class DevelopmentPlanDocumentModel(DatasetModel):

    dataset_name = "development-plan-document"
    typology = "document"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)

        self.document = {
            key: data[key]
            for key in Document.__table__.columns.keys()
            if key in self.data
        }

        if "document" not in self.document and self.dataset_name in self.data:
            self.document["document"] = self.data[self.dataset_name]

        if "document_url" not in self.document and "document-url" in self.data:
            self.document["document_url"] = self.data["document-url"]

        self.categories = (
            self.data["development-plan-types"].split(";")
            if "development-plan-types" in self.data
            else []
        )
        self.policies = (
            self.data["development-policies"].split(";")
            if "development-policies" in self.data
            else []
        )
        self.organisations = (
            self.data["organisations"].split(";")
            if "organisations" in self.data
            else []
        )
        self.geographies = (
            self.data["geographies"].split(";") if "geographies" in self.data else []
        )

    def to_orm(self, allow_broken_relationships=False):
        orms = []
        entity = Entity(**self.entity)
        document = Document(**self.document, entity_rel=entity)

        orms.append(document)

        def category_callback(category):
            return self.get_category(category=category, type="development-plan-type")

        for category in self.categories:
            category_orm = self.find_relation(
                category_callback, document, category, allow_broken_relationships
            )
            if category_orm:
                relationship = DocumentCategory(
                    document=document, category=category_orm
                )
                orms.append(relationship)

        for policy in self.policies:
            policy_orm = self.find_relation(
                self.get_policy, document, policy, allow_broken_relationships
            )
            if policy_orm:
                relationship = PolicyDocument(policy=policy_orm, document=document)
                orms.append(relationship)

        for org in self.organisations:
            org_orm = self.find_relation(
                self.get_organisation, document, org, allow_broken_relationships
            )
            if org_orm:
                relationship = DocumentOrganisation(
                    organisation=org_orm, document=document
                )
                orms.append(relationship)

        for geography in self.geographies:
            geography_orm = self.find_relation(
                self.get_geography,
                document,
                "local-authority-district:" + geography,
                allow_broken_relationships,
            )
            if geography_orm:
                relationship = DocumentGeography(
                    geography=geography_orm, document=document
                )
                orms.append(relationship)

        return orms


factory.register_dataset_model(DevelopmentPlanDocumentModel)


class DocumentModel(DatasetModel):

    dataset_name = "document"
    typology = "document"

    def __init__(self, session, data: dict):
        DatasetModel.__init__(self, session, data)

        self.document = {
            key: data[key]
            for key in Document.__table__.columns.keys()
            if key in self.data
        }

        if "document_url" not in self.document and "document-url" in self.data:
            self.document["document_url"] = self.data["document-url"]

        self.categories = (
            self.data["document-types"].split(";")
            if "document-types" in self.data
            else []
        )
        self.policies = (
            self.data["development-policies"].split(";")
            if "development-policies" in self.data
            else []
        )
        self.organisations = (
            self.data["organisations"].split(";")
            if "organisations" in self.data
            else []
        )
        self.geographies = (
            self.data["geographies"].split(";") if "geographies" in self.data else []
        )

    def to_orm(self, allow_broken_relationships=False):
        orms = []
        entity = Entity(**self.entity)
        document = Document(**self.document, entity_rel=entity)

        orms.append(document)

        def category_callback(category):
            return self.get_category(category=category, type="document-type")

        for category in self.categories:
            category_orm = self.find_relation(
                category_callback, document, category, allow_broken_relationships
            )
            if category_orm:
                relationship = DocumentCategory(
                    document=document, category=category_orm
                )
                orms.append(relationship)

        for policy in self.policies:
            policy_orm = self.find_relation(
                self.get_policy, document, policy, allow_broken_relationships
            )
            if policy_orm:
                relationship = PolicyDocument(policy=policy_orm, document=document)
                orms.append(relationship)

        for org in self.organisations:
            org_orm = self.find_relation(
                self.get_organisation, document, org, allow_broken_relationships
            )
            if org_orm:
                relationship = DocumentOrganisation(
                    organisation=org_orm, document=document
                )
                orms.append(relationship)

        # Geographies in Document are referenced by entity, not by code
        for geography in self.geographies:
            geography_entity = self.find_relation(
                self.get_entity,
                document,
                geography,
                allow_broken_relationships,
            )

            if geography_entity and geography_entity.geography:
                relationship = DocumentGeography(
                    geography=geography_entity.geography[0], document=document
                )
                orms.append(relationship)

        return orms


factory.register_dataset_model(DocumentModel)


class BrownfieldLandModel(GeographyDatasetModel):
    dataset_name = "brownfield-land"
    site_category_fields = ["deliverable", "hazardous-substances"]
    category_fields = [
        "ownership-status",
        "planning-permission-type",
        "planning-permission-status",
    ]
    metric_fields = [
        "maximum-net-dwellings",
        "minimum-net-dwellings",
        "planning-permission-date",
        "planning-permission-history",
        "hectares",
        "site-address",
    ]

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)
        self.geography["geography"] = data["site"]

        if "documentation_url" not in self.geography and "site-plan-url" in self.data:
            self.geography["documentation_url"] = self.data["site-plan-url"]

        self.categories = []

        for category_field in self.category_fields:
            if category_field in self.data:
                self.categories.extend(
                    (category_field, category.replace(" ", "-").lower())
                    for category in self.data[category_field].split(";")
                )

        self.categories.extend(
            ("site-category", site_category)
            for site_category in self.site_category_fields
            if site_category in self.data
        )

        self.metrics = (
            (metric_field, self.data[metric_field])
            for metric_field in self.metric_fields
            if metric_field in self.data and self.data[metric_field]
        )

        # TODO site-address

    def to_orm(self, allow_broken_relationships=False):
        orms = super().to_orm(allow_broken_relationships)
        geography = orms[0]

        for (category_type, category) in self.categories:
            category_orm = self.find_relation(
                lambda cat: self.get_category(category=cat, type=category_type),
                geography,
                category,
                allow_broken_relationships,
            )
            if category_orm:
                relationship = GeographyCategory(
                    geography=geography, category=category_orm
                )
                orms.append(relationship)

        for (metric, value) in self.metrics:
            metric_orm = Metric(field=metric, value=value)
            relationship = GeographyMetric(geography=geography, metric=metric_orm)
            orms.append(relationship)

        return orms


factory.register_dataset_model(BrownfieldLandModel)


class HeritageCoastModel(GeographyDatasetModel):
    dataset_name = "heritage-coast"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(HeritageCoastModel)


class AreaOfOutstandingNaturalBeautyModel(GeographyDatasetModel):
    dataset_name = "area-of-outstanding-natural-beauty"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(AreaOfOutstandingNaturalBeautyModel)


class AncientWoodlandModel(GeographyDatasetModel):
    dataset_name = "ancient-woodland"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(AncientWoodlandModel)


class ParishModel(GeographyDatasetModel):
    dataset_name = "parish"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(ParishModel)


class BattlefieldModel(GeographyDatasetModel):
    dataset_name = "battlefield"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(BattlefieldModel)


class HeritageAtRiskModel(GeographyDatasetModel):
    dataset_name = "heritage-at-risk"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(HeritageAtRiskModel)


class BuildingPreservationNoticeModel(GeographyDatasetModel):
    dataset_name = "building-preservation-notice"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(BuildingPreservationNoticeModel)


class ParkAndGardenModel(GeographyDatasetModel):
    dataset_name = "park-and-garden"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(ParkAndGardenModel)


class HeritateAtRiskModel(GeographyDatasetModel):
    dataset_name = "heritate-at-risk"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(HeritateAtRiskModel)


class ScheduledMonumentModel(GeographyDatasetModel):
    dataset_name = "scheduled-monument"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(ScheduledMonumentModel)


class WorldHeritageSiteModel(GeographyDatasetModel):
    dataset_name = "world-heritage-site"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(WorldHeritageSiteModel)


class ProtectedWreckSiteModel(GeographyDatasetModel):
    dataset_name = "protected-wreck-site"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(ProtectedWreckSiteModel)


class BuildingPreservationNoticeModel(GeographyDatasetModel):
    dataset_name = "building-preservation-notice"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(BuildingPreservationNoticeModel)


class CertificateOfImmunityModel(GeographyDatasetModel):
    dataset_name = "certificate-of-immunity"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(CertificateOfImmunityModel)


class ListedBuildingModel(GeographyDatasetModel):
    dataset_name = "listed-building"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(ListedBuildingModel)


class SpecialAreaOfConservationModel(GeographyDatasetModel):
    dataset_name = "special-area-of-conservation"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(SpecialAreaOfConservationModel)


class GreenBeltModel(GeographyDatasetModel):
    dataset_name = "green-belt"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(GreenBeltModel)


class RamsarModel(GeographyDatasetModel):
    dataset_name = "ramsar"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(RamsarModel)


class SiteOfSpecialScientificInterestModel(GeographyDatasetModel):
    dataset_name = "site-of-special-scientific-interest"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(SiteOfSpecialScientificInterestModel)


class OpenSpaceModel(GeographyDatasetModel):
    dataset_name = "open-space"

    def __init__(self, session, data: dict):
        GeographyDatasetModel.__init__(self, session, data)


factory.register_dataset_model(OpenSpaceModel)
