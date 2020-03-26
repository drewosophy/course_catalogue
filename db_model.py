#!/usr/bin/env python3

import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Creating classes for database tables

# User tables and serialised outputs


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    bio = Column(String(300), nullable=True)
    email = Column(String(250), nullable=False)
    profile_pic = Column(String, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'email': self.email,
            'profile_pic': self.profile_pic
        }

# Categories tables and serialised outputs


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


# Item tables and serialised outputs
class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(250), nullable=False)
    picture = Column(String, nullable=True)
    duration = Column(String(100), nullable=False)
    category_ref = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Categories)
    creator_ref = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'picture': self.picture,
            'duration': self.duration,
            'category_ref': self.category_ref,
            'category': self.category.serialize,
            'creator_ref': self.creator_ref,
            'creator': self.creator.serialize
        }


# Create SQL engine
engine = create_engine('sqlite:///catalogue.db')
Base.metadata.create_all(engine)
