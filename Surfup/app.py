import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup

engine = create_engine('sqlite:///hawaii.sqlite')

Base = automap()

Base.prepare(engine, reflect=True)

Measurement = Base/classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Routes


@app.route("/")
def home():
    # List all available api routes
    return (
        f"Available Routes:"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/start"
        f"/api/v1.0/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    # Query all prcp values from the last year date
    recent_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()[0]
    one_year_back = dt.datetime.strptime(
        recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_back).all()

    session.close()

    prcp_data = {}
    for result in results:
        prcp_data[result[0]] = result[1]

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def names():

    session = Session(engine)
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    # Query all temperature from most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == "USC00519281").filter(Measurement.date > '2016-08-23').all()

    session.close()

    # list of temp observations of most active station
    active_station = []
    for date, tobs in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["tobs"] = tobs
        active_station.append(precipitation_dict)

    return jsonify(active_station)


@app.route("/api/v1.0/<start>")
def single_date(start):
    if start >= "2010-01-01" and start <= "2017-08-23":

        session = Session(engine)

        sel = [func.min(Measurement.tobs), func.avg(
            Measurement.tobs), func.max(Measurement.tobs)]

        results = session.query(*sel).filter(Measurement.date >= start).all()

        session.close()

        summary = []
        for min, avg, max in results:
            summary_dict = {}
            summary_dict["tmin"] = min
            summary_dict["tavg"] = avg
            summary_dict["tmax"] = max
            summary.append(summary_dict)

        return jsonify(summary)
    else:
        return jsonify({"error": f"Date not in range, must be between 2010-01-01 and 2017-08-23."}), 404


@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):

    if (start >= "2010-01-01" and start <= "2017-08-23") and (end >= "2010-01-01" and end <= "2017-08-23"):

        session = Session(engine)

        sel = [func.min(Measurement.tobs), func.avg(
            Measurement.tobs), func.max(Measurement.tobs)]

        results = session.query(*sel).filter(Measurement.date >= start).all()

        session.close()

        summary = []
        for min, avg, max in results:
            summary_dict = {}
            summary_dict["tmin"] = min
            summary_dict["tavg"] = avg
            summary_dict["tmax"] = max
            summary.append(summary_dict)

        return jsonify(summary)
    else:
        return jsonify({"error": f"Date not in range, must be between 2010-01-01 and 2017-08-23."}), 404


if __name__ == '__main__':
    app.run(debug=True)
