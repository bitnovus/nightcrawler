from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
from models import City
import keysConfiguration, megabus, graphConfiguration

#=========================================================

app= Flask(__name__)

#=========================================================

def build_graph_for_date(db, cities, month, day, year):
    for city1 in cities:
        for city2 in cities:
            if city1 != city2:
                print city1.name + " " + city2.name
                print megabus(city1.megacode, city2.megacode, month, day, year, 0, 0, False)


def main():
    app.config.from_object(keysConfiguration.Config())
    db = SQLAlchemy(app)
    cities = db.session.query(City).all()

    app.config.from_object(graphConfiguration.Config())
    db = SQLAlchemy(app)
    build_graph_for_date(db, cities, 4, 26, 2013)
                

if __name__ == "__main__":
    main()
