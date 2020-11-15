#Importing Dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
measurements = Base.classes.measurement
stations = Base.classes.station

#create app
app = Flask(__name__)

#defines endpoints
@app.route("/")
def index():
    return """
        Available routes: <br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/<start><br/>
        /api/v1.0/<start>/<end>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(measurements.date).order_by(measurements.date.desc()).first()
    format_str = '%Y-%m-%d' # The format
    last_date_obj = dt.datetime.strptime(last_date[0], format_str)
    query_date = last_date_obj - dt.timedelta(days=365)
    # Query the db for the last 12 months of prcp data
    results = session.query(measurements.date, measurements.prcp)\
        .filter(measurements.date >= query_date)\
        .all()
    session.close()
    precip_dict= {}
    for date, prcp in results:
        precip_dict[date] = prcp
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
 
    # Query the db for the stations
    results = session.query(measurements.station).distinct()
    session.close()
    station_list=[] 
    for station in results:
        station_list.append(station)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # find the target date
    last_date = session.query(measurements.date).order_by(measurements.date.desc()).first()
    format_str = '%Y-%m-%d' # The format
    last_date_obj = dt.datetime.strptime(last_date[0], format_str)
    query_date = last_date_obj - dt.timedelta(days=365)
    #find the target station
    target = session.query(measurements.station, func.count(measurements.id)).\
    group_by(measurements.station).\
    order_by(func.count(measurements.station).desc()).first()
    #Query the db for the prcp data
    results = session.query(measurements.tobs)\
    .filter(measurements.date >= query_date)\
    .filter(measurements.station == target[0])\
    .all()
    session.close()
    temp_list=[] 
    for temp in results:
        temp_list.append(temp)
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def startr(start):
    #converts user data into a datetime object
    format_str = '%Y-%m-%d'
    start_date = dt.datetime.strptime(start, format_str)
    #defines values to search for
    sel = [
       func.max(measurements.tobs), 
       func.min(measurements.tobs), 
       func.avg(measurements.tobs)
    ]
    #Query the db for the specified data
    session = Session(engine)
    results = session.query(*sel).\
        filter(measurements.date >= start_date)\
        .all()
    session.close()
    #turns results into a dictionary
    dict = {}
    dict['TMIN']= results[0][1]
    dict['TAVG']= results[0][2]
    dict['TMAX']= results[0][0]
    return jsonify(dict)


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    #converts user data into a datetime objects
    format_str = '%Y-%m-%d'
    start_date = dt.datetime.strptime(start, format_str)
    end_date = dt.datetime.strptime(end, format_str)    
    #defines values to search for 
    sel = [
       func.max(measurements.tobs), 
       func.min(measurements.tobs), 
       func.avg(measurements.tobs)
    ]
    session = Session(engine)
    results = session.query(*sel).\
        filter(measurements.date >= start_date).\
        filter(measurements.date <= end_date)\
        .all()
    session.close()
    #turns results into a dictionary
    dict = {}
    dict['TMIN']= results[0][1]
    dict['TAVG']= results[0][2]
    dict['TMAX']= results[0][0]
    return jsonify(dict)

if __name__=='__main__':
    app.run(debug=True)