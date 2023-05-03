# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

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
#----- WILL OPEN & CLOSE SESSION WITHIN EACH ROUTE (as taught in claa) --------
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
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2016-08-23<br/>"
        f"/api/v1.0/start/2016-08-23/2017-08-23"
    )
 

#Display dictionary of dates & precipitation for 12-month period
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    result = session.query(measure.date,measure.prcp).filter(measure.date >= start_date).all()
    session.close()

    # prcp_dict = []
    # for prcp in result:
    #     prcp_dict.append(dict(prcp))
    prcp_dict = dict(result)

    return jsonify(prcp_dict)


# #Display list of stations
@app.route("/api/v1.0/station")
def station():
    session = Session(engine)
    #Table station not being recognized. Changed query to use the measurement table
    #result = session.query(station.station).all()
    result = session.query(measure.station).distinct().all()
    session.close() 

    station_lst = list(np.ravel(result))
    return jsonify(station_lst)


#Display min, max and average temperature f0r the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    result = session.query(measure.date,measure.tobs).filter(measure.station == most_active).\
                    filter(measure.date >= start_date, measure.date <= end_date)
    session.close()  

    tobs_lst = dict(result)
    return jsonify(tobs_lst)


#Display min, max and average temperature for entered date
@app.route("/api/v1.0/start/<st_date>")
def start(st_date):

    #check if a valid date has been entered. If valid, do query and output JSON.
    #Otherwise, give error message
    try:
        dt.datetime.strptime(st_date, '%Y-%m-%d')
        session = Session(engine)
        result = session.query(*sel).filter(measure.date == st_date).group_by(measure.date)
        session.close() 
        #create dictionary to pass to jsonify
        start_lst = create_dict(result)

        return jsonify(start_lst)
    except ValueError:
        return jsonify('Invalid date format'),404


#Display min, max and average temperature for entered date range
@app.route("/api/v1.0/start/<st_date>/<end_date>")
def start_end(st_date,end_date):
    #check if both dates entered are valid. If valid, do query and output JSON.
    #Otherwise, give error message
    try:
        dt.datetime.strptime(st_date, '%Y-%m-%d') and dt.datetime.strptime(end_date, '%Y-%m-%d')
    
        session = Session(engine)
        result = session.query(*sel).filter(measure.date >= st_date, measure.date <= end_date).\
                group_by(measure.date)
        session.close()      
        #create dictionary to pass to jsonify
        start_end_lst = create_dict(result)

        return jsonify(start_end_lst)
    except ValueError:
        return jsonify('Invalid date format'),404


###################################################
# Other Functions
##################################################

#Create a dictionary from ORM Row object
def create_dict(orm_row_obj):
    output_dict = []
    for date, min, max, avg in orm_row_obj:
        output = {}
        output["date"] = date
        output["min"] = min
        output["max"] = max
        output["avg"] = avg
    
        output_dict.append(output)

    return(output_dict)

if __name__ == "__main__":
    app.run(debug=True)
