import time
import logging as logger

from flask import Flask, render_template, request
from flask_restful import Resource, Api

from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


logger.basicConfig(level="DEBUG")

# instantiate flask app
app = Flask(__name__)

# instantiate flask api
api = Api(app)
# instantiate sqlalchemy engine
engine = create_engine("sqlite:///lunchBreak.db", echo=False)
# create a session
session = sessionmaker(bind=engine)()
# declarative base
Base = declarative_base()


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    def __init__(self, name):
        self.name = name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Person(Base):

    __tablename__ = "person"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    teamId = Column(String(10), ForeignKey("team.id"))
    email = Column(String(100), unique=True)
    contact = Column(String(20), unique=True)
    onLunchBreak = Column(Boolean)
    started = Column(Integer)

    def __init__(self, name: str, teamId: int, email: str = "", contact: str = ""):
        self.name = name
        self.teamId = teamId
        self.email = email
        self.contact = contact
        self.onLunchBreak = False
        self.started = None

    def __str__(self):
        return f"{self.name} ({self.email})"

    def json(self):
        return {
            "name": self.name,
            "teamId": self.teamId,
            "email": self.email,
            "contact": self.contact,
            "onLunchBreak": self.onLunchBreak,
            "started": self.started,
        }


class createTeam(Resource):
    def put(self):
        name = request.form.get("name")

        newTeam = Team(name)
        session.add(newTeam)
        session.commit()
        return newTeam.json(), 200


class createPerson(Resource):
    def put(self):
        name = request.json["name"]
        teamId = request.json["teamId"]
        email = request.json["email"]
        contact = request.json["contact"]

        new = Person(name, teamId, email, contact)
        session.add(new)
        session.commit()
        return new.json(), 200


class personByID(Resource):
    def get(self, id):
        exist = session.query(Person).filter(Person.id == id).count()
        if exist:
            for person in session.query(Person).filter(Person.id == id):
                return person.json(), 200
        else:
            return {"data": "Person Not Found"}, 404

    def post(self, id):
        onLunchBreak = request.json["onLunchBreak"]
        started = time.time()
        exist = session.query(Person).filter(Person.id == id).count()
        if exist:
            onLunchBreak = request.json["onLunchBreak"]
            if onLunchBreak:
                started = time.time()
                for person in session.query(Person).filter(Person.id == id):
                    person.onLunchBreak = True
                    person.started = started
                    return person.json(), 200

        else:
            return {"data": "Person Not Found"}, 404

    def delete(self, id):
        exist = session.query(Person).filter(Person.id == id).count()
        if exist:
            session.query(Person).filter(Person.id == id).delete()
            session.commit()
            return {"data": "Person Deleted"}, 200
        else:
            return {"data": "Person Not Found"}, 404


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":

    # CREATE TABLE
    # Base.metadata.create_all(engine)

    while False:
        t1 = Team(1, "SAP Date Intelligence")
        p1 = Person("Mark", 1, "mark.huang01@sap.com", "87810920")
        p2 = Person("Shide", 2, "shide.foo@sap.com", "")
        session.add(t1)
        session.add(p1)
        session.add(p2)
        session.commit()
        break

    # add api
    api.add_resource(personByID, "/api/v1/person/<int:id>")
    api.add_resource(createPerson, "/api/v1/person/")
    api.add_resource(createTeam, "/api/v1/team/")

    # log
    logger.debug("Starting Flask Server")

    # run app
    app.run(host="0.0.0.0", port=5000, debug=True)
