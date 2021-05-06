from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Table,
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
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    slug = Column(String, unique=True)

    category = relationship("Category", back_populates="slug")
    geography = relationship("Geography", back_populates="slug")
    document = relationship("Document", back_populates="slug")
    policy = relationship("Policy", back_populates="slug")

    def __repr__(self):
        return "Slug({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


policy_category = Table(
    "policy_category",
    Base.metadata,
    Column("policy", Integer, ForeignKey("policy.id")),
    Column("category", Integer, ForeignKey("category.id")),
)

document_category = Table(
    "document_category",
    Base.metadata,
    Column("category", Integer, ForeignKey("category.id")),
    Column("document", Integer, ForeignKey("document.id")),
)


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    category = Column(String)
    type = Column(String)
    reference = Column(String)
    name = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    __table_args__ = (UniqueConstraint("category", "type"),)

    slug = relationship("Slug", back_populates="category")
    documents = relationship(
        "Document", secondary=document_category, back_populates="categories"
    )
    policies = relationship(
        "Policy", secondary=policy_category, back_populates="categories"
    )

    def __repr__(self):
        return "Category({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Organisation(Base):
    __tablename__ = "organisation"
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    organisation = Column(String, unique=True)
    reference = Column(String)
    name = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    # TODO: add relationships
    geographies = relationship("OrganisationGeography", back_populates="organisation")
    policies = relationship("PolicyOrganisation", back_populates="organisation")
    documents = relationship("DocumentOrganisation", back_populates="organisation")

    def __repr__(self):
        return "Organisation({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Geography(Base):
    __tablename__ = "geography"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    geography = Column(String, unique=True)
    geometry = Column(String)
    name = Column(String)
    type = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="geography")
    organisations = relationship("OrganisationGeography", back_populates="geography")
    policies = relationship("PolicyGeography", back_populates="geography")
    documents = relationship("DocumentGeography", back_populates="geography")

    def __repr__(self):
        return "Geography({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class OrganisationGeography(Base):
    __tablename__ = "organisation_geography"
    organisation_id = Column(Integer, ForeignKey("organisation.id"), primary_key=True)
    geography_id = Column(Integer, ForeignKey("geography.id"), primary_key=True)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="organisations")
    organisation = relationship("Organisation", back_populates="geographies")


policy_document = Table(
    "policy_document",
    Base.metadata,
    Column("policy", Integer, ForeignKey("policy.id")),
    Column("document", Integer, ForeignKey("document.id")),
)


class Policy(Base):
    __tablename__ = "policy"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    policy = Column(String, unique=True)
    reference = Column(String)
    name = Column(String)
    description = Column(String)
    notes = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="policy")
    documents = relationship(
        "Document", secondary=policy_document, back_populates="policies"
    )
    categories = relationship(
        "Category", secondary=policy_category, back_populates="policies"
    )
    geographies = relationship("PolicyGeography", back_populates="policy")
    organisations = relationship("PolicyOrganisation", back_populates="policy")

    def __repr__(self):
        return "Policy({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class PolicyGeography(Base):
    __tablename__ = "policy_geography"
    policy_id = Column(Integer, ForeignKey("policy.id"), primary_key=True)
    geography_id = Column(Integer, ForeignKey("geography.id"), primary_key=True)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="policies")
    policy = relationship("Policy", back_populates="geographies")


class PolicyOrganisation(Base):
    __tablename__ = "policy_organisation"
    policy_id = Column(Integer, ForeignKey("policy.id"), primary_key=True)
    organisation_id = Column(Integer, ForeignKey("organisation.id"), primary_key=True)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    organisation = relationship("Organisation", back_populates="policies")
    policy = relationship("Policy", back_populates="organisations")


class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    prefix = Column(String)
    document = Column(String)
    reference = Column(String)
    name = Column(String)
    description = Column(String)
    notes = Column(String)
    document_url = Column(String)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="document")
    categories = relationship(
        "Category", secondary=document_category, back_populates="documents"
    )
    policies = relationship(
        "Policy", secondary=policy_document, back_populates="documents"
    )
    geographies = relationship("DocumentGeography", back_populates="document")
    organisations = relationship("DocumentOrganisation", back_populates="document")

    def __repr__(self):
        return "Document({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class DocumentGeography(Base):
    __tablename__ = "document_geography"
    document_id = Column(Integer, ForeignKey("document.id"), primary_key=True)
    geography_id = Column(Integer, ForeignKey("geography.id"), primary_key=True)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="documents")
    document = relationship("Document", back_populates="geographies")


class DocumentOrganisation(Base):
    __tablename__ = "document_organisation"
    document_id = Column(Integer, ForeignKey("document.id"), primary_key=True)
    organisation_id = Column(Integer, ForeignKey("organisation.id"), primary_key=True)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    organisation = relationship("Organisation", back_populates="documents")
    document = relationship("Document", back_populates="organisations")
