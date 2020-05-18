import numpy as np
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

print(f"The tables in automap are: {Base.classes.keys()}")

app = Flask(__name__)

@app.route('/')
def welcome():
    return (
        f"Welcome to the temperature and precipitation report of Hawaii<br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>Precipitation<a/><br/>"
        f"<a href='/api/v1.0/station'>Station<a/><br/>"
        f"<a href='/api/v1.0/tobs'>TOBS<a/><br/>"
        f"<a href='/api/v1.0/<start>'>Start Date<a/><br/>"
        f"<a href='/api/v1.0/<start>/<end>'>Start/End Date<a/><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Return a JSON representation of precipitation dictionary
    session = Session(engine)
    
    # Calculate the date 1 year ago from the last data point in the database
    first = dt.datetime.strptime('2017-08-23', '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precip = session.query(Measurement.date, func.sum(Measurement.prcp)).filter(Measurement.date >= first).\
    group_by(Measurement.date).all()
    session.close()

    precip_data=[]
    for date, prcp in precip:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precip_data.append(prcp_dict)
    
    return jsonify(precip_data)

@app.route("/api/v1.0/station")
def station():
    #Return a JSON representation of station names
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    sta_list = session.query(Station.station).group_by(Station.station).all()
    session.close()

    sta_data=[]
    for name in sta_list:
        sta_data.append(name)
    
    return jsonify(sta_data)

@app.route("/api/v1.0/tobs")
def tobs():
    #Return a JSON representation of station names
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    mas = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    ma_station = mas[0][0]
    temp_min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.station == ma_station).all()

    temp_max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.station == ma_station).all()

    temp_avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.station == ma_station).all()

    session.close()

    tobs_data=["Station with the most data is: "+ma_station, "Station min temp: "+str(temp_min_temp[0][0]), \
        "Station max temp: "+str(temp_max_temp[0][0]), "Station avg temp: "+str(round(temp_avg_temp[0][0], 2))]

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    if start != "<start>":
        # Return a json list of the minimum temp, avg temp, and max temp for a given start or start/end range
        session = Session(engine)
        temp_start_max = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
        temp_start_min = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start).all()
        temp_start_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
        temp_start = ["Start date is: "+start, "Min temp: "+str(temp_start_min[0][1])+" Date: "+str(temp_start_min[0][0]), \
            "Avg Temp is: "+str(temp_start_avg[0][0]), "Max temp is: "+str(temp_start_max[0][1])+" Date: "+\
                str(temp_start_max[0][0])]
        session.close()
        return jsonify(temp_start)
    else:
        return "Please Enter Valid Values in URL"
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print(f"Start: {type(start)}, finish: {type(end)}")
    if (start != "<start>") and (end != "<end>"):
        # Return a json list of the minimum temp, avg temp, and max temp for a given start or start/end range
        session = Session(engine)
        temp_start_max = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
        temp_start_min = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temp_start_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temp_start = ["Start date is: "+start, "End date is: "+end, "Min temp: "+str(temp_start_min[0][1])+" Date: "+str(temp_start_min[0][0]), \
            "Avg Temp is: "+str(temp_start_avg[0][0]), "Max temp is: "+str(temp_start_max[0][1])+" Date: "+\
                str(temp_start_max[0][0])]
        session.close()
        return jsonify(temp_start)
    else:
        return "Please Enter Valid Values in URL"

if __name__ == "__main__":
    app.run(debug=True)