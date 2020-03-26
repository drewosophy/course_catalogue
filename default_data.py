#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from database_setup import Base, User, Course, Categories

engine = create_engine('sqlite:///catalogue.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# New user

defaultUser = User(name="Akin Aremu",
                   email="aremuakin918@gmail.com",
                   bio="Welcome to my space, I have a multitude of courses for you to enjoy",
                   profile_pic="https://cdn.britannica.com/36/198336-050-A9B8AA86/Chadwick-Boseman-Tchalla-Black-Panther-Black.jpg")

session.add(defaultUser)

# Some new categories
defaultCat1 = Categories(name="Music")
session.add(defaultCat1)

defaultCat2 = Categories(name="Design")
session.add(defaultCat2)

defaultCat3 = Categories(name="Tech")
session.add(defaultCat3)

defaultCat4 = Categories(name="Food")
session.add(defaultCat4)

defaultCat5 = Categories(name="Sport")
session.add(defaultCat5)

defaultCat6 = Categories(name="Science")
session.add(defaultCat6)

defaultCat7 = Categories(name="Psychology")
session.add(defaultCat7)

defaultCat8 = Categories(name="Business")
session.add(defaultCat8)

defaultCat9 = Categories(name="Design")
session.add(defaultCat9)

defaultCat10 = Categories(name="History")
session.add(defaultCat10)

# create items
default_Course = Course(
        title="How to make vegan steak burger",
        picture="https://www.bestsoccerbuys.com/content/images/thumbs/0000447_classic-collection-soccer-ball-black-white-butyl-bladder-japanese-pu-cover.jpeg",
        duration="3 months",
        description="Whether you're vegan or simply exploring, this course will help you make an amazing meatless steak burger!",
        category_ref=defaultCat4.name,
        creator_ref=1
        )
session.add(default_Course)

session.commit()

print("Great! Default data loaded!")
