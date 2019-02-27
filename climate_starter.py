
# get_ipython().run_line_magic('matplotlib', 'inline')
# from matplotlib import style
# style.use('fivethirtyeight')
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc 
from flask import Flask, jsonify


# setting up SQLAlchemy
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table   #this is a class equal to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<br> Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

## Exploratory Climate Analysis
@app.route("/api/v1.0/precipitation")
# Convert the query results to a Dictionary using date as the key and prcp as the value.
def precipitation():
    latest_date = dt.date(2017, 8, 23) 
    delta = latest_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    one_yr_prcp_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= delta).all()
    #loop through and add date and prcp to 2 different lists to create a dataframe
    one_yr_date = []
    one_yr_prcp = []

    for row in one_yr_prcp_data:
        one_yr_date.append(row.date)
        one_yr_prcp.append(row.prcp)

    # creating a dictionary with the 2 lists  
    one_yr_dict = {"date": one_yr_date, "precipitation": one_yr_prcp}   
    return jsonify(one_yr_dict)


#************STATION DATA***************

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to show how many stations are available in this dataset?
    station_data = session.query(Station.station).distinct().all()
    station_count = session.query(Station.station).distinct().count()

    # List the stations and the counts in descending order.
    station_counts_desc = session.query(Measurement.station,func.\
        count(Measurement.station).\
        label("scount")).\
        group_by(Measurement.station).\
        order_by(desc("scount")).\
        all()
    return jsonify(stations=station_data) 


# ********** Temperature Observations (tobs) **************

@app.route("/api/v1.0/tobs")
def tobs():
    latest_date = dt.date(2017, 8, 23) 
    delta = latest_date - dt.timedelta(days=365)

    #Station with the most records(most active)
    # (station_max, count_max) = station_counts_desc[0]

    # lowest & highest temperature recorded, and average temperature @ most active station
    # station_temp_stats = session.query(func.min(Measurement.tobs),func.\
    #     max(Measurement.tobs),func.avg(Measurement.tobs)).\
    #     filter(Measurement.station == station_max).\
    #     all()
    # station_temp_stats

    # For station with the highest number of temperature observations... 
    # ... count of only the tobs (temperature observations)
    station_tobs_counts = session.query(Measurement.station,func.count(Measurement.tobs).\
        label("count_tobs")).\
        filter(Measurement.date > delta).\
        group_by(Measurement.station).\
        order_by(desc("count_tobs")).all()

    #because it is in desc order the station at index 0 has the most tobs
    (tobs_station_max , tobs_count_max) = station_tobs_counts[0] 

    station_temps = session.query(Measurement.tobs).filter(Measurement.date > delta).\
        filter(Measurement.station ==  tobs_station_max).\
        all()

    tobs_list = []

    for row in station_temps:
        tobs_list.append(row)

    print(count)
    tobs_list = [float(str(i)[1:-2]) for i in tobs_list]
    tobs_dict = {"Temperature" : tobs_list}
    return jasonify(tobs_dict)


# runs the apps (in debug mode)
if __name__ == '__main__':
    app.run(debug=True)
