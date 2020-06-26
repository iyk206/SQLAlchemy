from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
import pathlib
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import numpy as np

sqlite_path= pathlib.Path("Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{sqlite_path}")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results= session.query(measurement.date, measurement.prcp).\
            filter(measurement.date.between('2016-08-23','2017-08-23')).all()
    session.close()
    prcp_dict = dict()
    for date,prcp in results: 
        prcp_dict.setdefault(date, []).append(prcp)  
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [measurement.station]
    station_names = (session.query(*sel)).all()
    station_list = list(np.ravel(station_names))
    return jsonify(station_list)

        
@app.route("/api/v1.0/tobs")
def precipitation_last_year():
    session = Session(engine)
    results2= session.query(measurement.date, measurement.prcp).\
            filter(measurement.date.between('2016-08-23','2017-08-23')).\
            filter(measurement.station == 'USC00519281').all()
    session.close()
    prcp_dict = dict()
    for date,prcp in results2: 
        prcp_dict.setdefault(date, []).append(prcp)  
    return jsonify(prcp_dict)
        
@app.route("/api/v1.0/<start>")
def starting(start):
    session = Session(engine)
    starting_date = session.query(measurement.date,func.avg(measurement.tobs),func.min(measurement.tobs),func.max(measurement.tobs)).\
             filter(measurement.date >= start).\
             group_by(measurement.date).all()

    return jsonify(starting_date)

@app.route("/api/v1.0/<start>/<end>")
def ending_date(start,end):
    session = Session(engine)
    range = session.query(measurement.date,func.avg(measurement.tobs),func.min(measurement.tobs),func.max(measurement.tobs)) \
             .filter(measurement.date >= start).filter(measurement.date <= end) \
             .group_by(measurement.date).all()
    return jsonify(range)

        
if __name__ == "__main__":
    app.run(debug=True)
