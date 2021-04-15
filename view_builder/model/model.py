from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import ForeignKey, Column, Integer, String

Base = declarative_base()


class Slug(Base):
    __tablename__ = 'slug'
    id = Column(Integer, primary_key=True)
    prefix = Column(String)
    slug = Column(String, unique=True)

    category = relationship("Category", back_populates="slug")

    def __repr__(self):
        return f"Slug(id={self.id!r}, prefix={self.prefix!r}, slug={self.slug!r})"


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    slug_id = Column(Integer, ForeignKey('slug.id'))
    category = Column(String)
    reference = Column(String)
    name = Column(String)

    slug = relationship("Slug", back_populates="category")

    def __repr__(self):
        return f"Category(id={self.id!r}, name={self.name!r}, category={self.category!r}, " \
               f"reference={self.reference!r}, slug={self.slug!r})"
