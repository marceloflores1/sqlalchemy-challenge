import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    one_year_ago = dt.date(2017,8,23) - relativedelta(months=12)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_year_ago).all()

    # Save the query results as dict
    rows = [{"Date":r[0], "precipitation":r[1]} for r in results]

    session.close()

    # Return the JSON representation of your dictionary.
    return jsonify(rows)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all stations
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        all_stations_dict = {}
        all_stations_dict["Station"] = station
        all_stations_dict["Name"] = name
        all_stations_dict["Latitude"] = latitude
        all_stations_dict["Longitude"] = longitude
        all_stations_dict["Elevation"] = elevation
        all_stations.append(all_stations_dict)

    # Return a JSON list of stations from the dataset.
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Adding useful variables
    one_year_ago = dt.date(2017,8,23) - relativedelta(months=12)
    most_active_station = 'USC00519281'

    # Query the dates and temperature observations of the most active station for the last year of data.    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_year_ago).\
        filter(Measurement.station == most_active_station).all()
    
    rows = [{"Date":r[0], "temperature":r[1]} for r in results]

    session.close()

    #  Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(rows)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.    
    min_temp = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        order_by(Measurement.tobs.asc()).first()
    max_temp = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        order_by(Measurement.tobs.desc()).first()
    total_temp = session.query(func.sum(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).one()
    total_count = session.query(Measurement.tobs).\
        filter(round(func.strftime("%Y-%m-%d", Measurement.date),2) >= start).count()
    avg_temp = total_temp[0]/total_count

    rows = [{"Min Temperature":min_temp},
        {"Max Temperature":max_temp},
        {"Avg Temperature":avg_temp}
    ]

    session.close()

    #  Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(rows)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.    
    min_temp = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
        order_by(Measurement.tobs.asc()).first()
    max_temp = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
        order_by(Measurement.tobs.desc()).first()
    total_temp = session.query(func.sum(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).one()
    total_count = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).count()
    avg_temp = total_temp[0]/total_count

    rows = [{"Min Temperature":min_temp},
        {"Max Temperature":max_temp},
        {"Avg Temperature":avg_temp}
    ]

    session.close()

    #  Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True)
