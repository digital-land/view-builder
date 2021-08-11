from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    String,
    Date,
    UniqueConstraint,
)

Base = declarative_base()


class Slug(Base):
    __tablename__ = "slug"
    dl_type = None
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    slug = Column(String, index=True, unique=True)

    category = relationship("Category", back_populates="slug")
    geography = relationship("Geography", back_populates="slug")
    document = relationship("Document", back_populates="slug")
    policy = relationship("Policy", back_populates="slug")

    def __repr__(self):
        return "Slug({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class PolicyCategory(Base):
    __tablename__ = "policy_category"
    dl_type = "join"
    policy_id = Column(Integer, ForeignKey("policy.id"), primary_key=True, index=True)
    category_id = Column(
        Integer, ForeignKey("category.id"), primary_key=True, index=True
    )
    category = relationship("Category", back_populates="policies")
    policy = relationship("Policy", back_populates="categories")


class DocumentCategory(Base):
    __tablename__ = "document_category"
    dl_type = "join"
    document_id = Column(
        Integer, ForeignKey("document.id"), primary_key=True, index=True
    )
    category_id = Column(
        Integer, ForeignKey("category.id"), primary_key=True, index=True
    )
    document = relationship("Document", back_populates="categories")
    category = relationship("Category", back_populates="documents")


class Category(Base):
    __tablename__ = "category"
    dl_type = "schema"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"), index=True)
    category = Column(String, index=True)
    type = Column(String, index=True)
    reference = Column(String)
    name = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    __table_args__ = (UniqueConstraint("category", "type"),)

    slug = relationship("Slug", back_populates="category")
    documents = relationship("DocumentCategory", back_populates="category")
    policies = relationship("PolicyCategory", back_populates="category")
    geographies = relationship("GeographyCategory", back_populates="category")

    def __repr__(self):
        return "Category({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Organisation(Base):
    __tablename__ = "organisation"
    dl_type = "schema"
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    organisation = Column(String, index=True, unique=True)
    reference = Column(String)
    name = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    geographies = relationship("OrganisationGeography", back_populates="organisation")
    policies = relationship("PolicyOrganisation", back_populates="organisation")
    documents = relationship("DocumentOrganisation", back_populates="organisation")

    def __repr__(self):
        return "Organisation({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Metric(Base):
    __tablename__ = "metric"
    dl_type = None
    id = Column(Integer, primary_key=True)
    field = Column(String)
    value = Column(String)

    geography = relationship("GeographyMetric", back_populates="metric")


class Geography(Base):
    __tablename__ = "geography"
    dl_type = "schema"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    geography = Column(String, index=True)
    geometry = Column(String)
    point = Column(String)
    name = Column(String)
    notes = Column(String)
    documentation_url = Column(String)
    type = Column(String, index=True)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="geography")
    organisations = relationship("OrganisationGeography", back_populates="geography")
    policies = relationship("PolicyGeography", back_populates="geography")
    documents = relationship("DocumentGeography", back_populates="geography")
    metrics = relationship("GeographyMetric", back_populates="geography")
    categories = relationship("GeographyCategory", back_populates="geography")

    def __repr__(self):
        return "Geography({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class OrganisationGeography(Base):
    __tablename__ = "organisation_geography"
    dl_type = "join"
    organisation_id = Column(
        Integer, ForeignKey("organisation.id"), primary_key=True, index=True
    )
    geography_id = Column(
        Integer, ForeignKey("geography.id"), primary_key=True, index=True
    )
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="organisations")
    organisation = relationship("Organisation", back_populates="geographies")


class GeographyCategory(Base):
    __tablename__ = "geography_category"
    dl_type = "join"
    category_id = Column(
        Integer, ForeignKey("category.id"), primary_key=True, index=True
    )
    geography_id = Column(
        Integer, ForeignKey("geography.id"), primary_key=True, index=True
    )
    geography = relationship("Geography", back_populates="categories")
    category = relationship("Category", back_populates="geographies")


class GeographyMetric(Base):
    __tablename__ = "geography_metric"
    dl_type = "join"
    metric_id = Column(Integer, ForeignKey("metric.id"), primary_key=True, index=True)
    geography_id = Column(
        Integer, ForeignKey("geography.id"), primary_key=True, index=True
    )
    geography = relationship("Geography", back_populates="metrics")
    metric = relationship("Metric", back_populates="geography")


class PolicyDocument(Base):
    __tablename__ = "policy_document"
    dl_type = "join"
    policy_id = Column(Integer, ForeignKey("policy.id"), primary_key=True, index=True)
    document_id = Column(
        Integer, ForeignKey("document.id"), primary_key=True, index=True
    )
    document = relationship("Document", back_populates="policies")
    policy = relationship("Policy", back_populates="documents")


class Policy(Base):
    __tablename__ = "policy"
    dl_type = "schema"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    policy = Column(String, index=True, unique=True)
    reference = Column(String)
    name = Column(String)
    description = Column(String)
    notes = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="policy")
    documents = relationship("PolicyDocument", back_populates="policy")
    categories = relationship("PolicyCategory", back_populates="policy")
    geographies = relationship("PolicyGeography", back_populates="policy")
    organisations = relationship("PolicyOrganisation", back_populates="policy")

    def __repr__(self):
        return "Policy({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class PolicyGeography(Base):
    __tablename__ = "policy_geography"
    dl_type = "join"
    policy_id = Column(Integer, ForeignKey("policy.id"), primary_key=True, index=True)
    geography_id = Column(
        Integer, ForeignKey("geography.id"), primary_key=True, index=True
    )
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="policies")
    policy = relationship("Policy", back_populates="geographies")


class PolicyOrganisation(Base):
    __tablename__ = "policy_organisation"
    dl_type = "join"
    policy_id = Column(Integer, ForeignKey("policy.id"), primary_key=True, index=True)
    organisation_id = Column(
        Integer, ForeignKey("organisation.id"), primary_key=True, index=True
    )
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    organisation = relationship("Organisation", back_populates="policies")
    policy = relationship("Policy", back_populates="organisations")


class Document(Base):
    __tablename__ = "document"
    dl_type = "schema"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    prefix = Column(String)
    document = Column(String, index=True)
    reference = Column(String)
    name = Column(String)
    description = Column(String)
    notes = Column(String)
    document_url = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="document")
    categories = relationship("DocumentCategory", back_populates="document")
    policies = relationship("PolicyDocument", back_populates="document")
    geographies = relationship("DocumentGeography", back_populates="document")
    organisations = relationship("DocumentOrganisation", back_populates="document")

    def __repr__(self):
        return "Document({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class DocumentGeography(Base):
    __tablename__ = "document_geography"
    dl_type = "join"
    document_id = Column(
        Integer, ForeignKey("document.id"), primary_key=True, index=True
    )
    geography_id = Column(
        Integer, ForeignKey("geography.id"), primary_key=True, index=True
    )
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="documents")
    document = relationship("Document", back_populates="geographies")


class DocumentOrganisation(Base):
    __tablename__ = "document_organisation"
    dl_type = "join"
    document_id = Column(
        Integer, ForeignKey("document.id"), primary_key=True, index=True
    )
    organisation_id = Column(
        Integer, ForeignKey("organisation.id"), primary_key=True, index=True
    )
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    organisation = relationship("Organisation", back_populates="documents")
    document = relationship("Document", back_populates="organisations")
