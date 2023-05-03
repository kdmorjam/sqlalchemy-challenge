# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measure = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
#----- WILL OPEN & CLOSE SESSION WITHIN EACH ROUTE  --------
#session = Session(engine)

######################################################
# Initializing Global variables
######################################################
start_date = '2016-08-23'           #start of 12-month period
end_date = '2017-08-23'             #last date in table/12-month period
most_active = 'USC00519281'         #most active station

#column list for query
sel = [measure.date, func.min(measure.tobs), 
       func.max(measure.tobs), func.avg(measure.tobs)]


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/start_date<br/>"
        f"/api/v1.0/start/start_date/end/end_date"
    )

#Display dictionary of dates & precipitation for 12-month period
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    result = session.query(measure.date,measure.prcp).filter(measure.date >= start_date).all()
    session.close()

    prcp_dict = []
    for date, prcp in result:
        output = {}
        output["date"] = date
        output["prcp"] = prcp
        prcp_dict.append(output)

    return jsonify(prcp_dict)

#Display list of stations
@app.route("/api/v1.0/station")
def station():
    session = Session(engine)
    result = session.query(station.station).all()
    session.close() 

    station_lst = list(np.ravel(result))
    return jsonify(station_lst)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    result = session.query(measure.date,measure.tobs).filter(measure.station == most_active).\
                    filter(measure.date >= start_date, measure.date <= end_date)
    session.close() 

    tobs_lst = list(np.ravel(result))
    return jsonify(tobs_lst)


@app.route("/api/v1.0/start/<start>")
def start(start_date):
    session = Session(engine)
    result = session.query(*sel).filter(measure.date == start_date).group_by(measure.date)

    session.close() 

    start_lst = list(np.ravel(result))
    return jsonify(start_lst)


@app.route("/api/v1.0/start/<start>/end/<end>")
def start_end(start_date,end_date):
    session = Session(engine)

    result = session.query(*sel).filter(measure.date >= start_date, measure.date <= end_date).\
                group_by(measure.date)
    session.close() 

    start_end_lst = list(np.ravel(result))
    return jsonify(start_end_lst)
  

if __name__ == "__main__":
    app.run(debug=True)
