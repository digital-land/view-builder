from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Table, ForeignKey, Column, Integer, String, Date

Base = declarative_base()


class Slug(Base):
    __tablename__ = "slug"
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    slug = Column(String, unique=True)

    category = relationship("Category", back_populates="slug")
    geography = relationship("Geography", back_populates="slug")
    document = relationship("Document", back_populates="slug")

    def __repr__(self):
        return "Slug({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    category = Column(String, unique=True)
    reference = Column(String)
    name = Column(String)
    start_date = Column(Date)
    entry_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="category")
    policy = relationship("Policy", back_populates="category")
    document = relationship("Document", back_populates="category")

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
    start_date = Column(Date)
    end_date = Column(Date)

    # TODO: add relationships
    document = relationship("Document", back_populates="organisation")
    geographies = relationship("OrganisationGeography", back_populates="organisation")

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
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="geography")
    document = relationship("Document", back_populates="geography")
    organisation = relationship("OrganisationGeography", back_populates="geography")

    def __repr__(self):
        return "Geography({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class OrganisationGeography(Base):
    __tablename__ = "organisation_geography"
    organisation_id = Column(Integer, ForeignKey("organisation.id"), primary_key=True)
    geography_id = Column(Integer, ForeignKey("geography.id"), primary_key=True)
    start_date = Column(Date)
    end_date = Column(Date)
    geography = relationship("Geography", back_populates="organisation")
    organisation = relationship("Organisation", back_populates="geographies")


policy_document = Table(
    "policy_document",
    Base.metadata,
    Column("policy", Integer, ForeignKey("policy.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
)


class Policy(Base):
    __tablename__ = "policy"
    id = Column(Integer, primary_key=True)
    prefix = Column(String)  # Should this be a foreign key to slug.prefix ?
    category_id = Column(Integer, ForeignKey("category.id"))
    reference = Column(String)
    name = Column(String, unique=True)

    category = relationship("Category", back_populates="policy")
    documents = relationship(
        "Document", secondary=policy_document, back_populates="policies"
    )

    def __repr__(self):
        return "Policy({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    prefix = Column(String)
    document = Column(String, unique=True)
    reference = Column(String)
    organisation_id = Column(Integer, ForeignKey("organisation.id"))
    geography_id = Column(Integer, ForeignKey("geography.id"))
    name = Column(String)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("category.id"))
    document_url = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="document")
    organisation = relationship("Organisation", back_populates="document")
    geography = relationship("Geography", back_populates="document")
    category = relationship("Category", back_populates="document")
    policies = relationship(
        "Policy", secondary=policy_document, back_populates="documents"
    )

    def __repr__(self):
        return "Document({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )
