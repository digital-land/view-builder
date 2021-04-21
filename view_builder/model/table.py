from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import ForeignKey, Column, Integer, String, Date

Base = declarative_base()


class Slug(Base):
    __tablename__ = "slug"
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    slug = Column(String, unique=True)

    category = relationship("Category", back_populates="slug")

    def __repr__(self):
        return "Slug({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey("slug.id"))
    category = Column(String)
    reference = Column(String)
    name = Column(String)
    start_date = Column(Date)
    entry_date = Column(Date)
    end_date = Column(Date)

    slug = relationship("Slug", back_populates="category")

    def __repr__(self):
        return "Category({})".format(
            {key: getattr(self, key) for key in self.__table__.columns.keys()}
        )
