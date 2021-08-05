# SANElib Prototype
# Standard-SQL Analytics for Numerical Estimation – SANE
# (c) 2020  Giesser Patrick, Michael Kaufmann, Gabriel Stechschulte, Anna Huber, HSLU

import config as conf
import lib
from util.database import Database

if conf.DB_TYPE == "MYSQL":
    db_connection = {
        "drivername": "mysql+mysqlconnector",
        "host": conf.DB_HOST,
        "port": conf.DB_PORT,
        "username": conf.DB_USER,
        "password": conf.DB_PW,
        "database": conf.DB_NAME,
        "query": {"charset": "utf8"}
    }
elif conf.DB_TYPE == "SQLITE":
    db_connection = {
        "drivername": "sqlite",
        "database": conf.DB_NAME,
        "path": conf.DB_PATH
    }
else:
    raise Exception("No valid DB_TYPE (config.py) provided! Please provide one of the following types: \n MYSQL\n SQLITE")

db = Database(db_connection)

mdh = lib.mdh.MDH(db)
linear_regression = lib.linear_regression.LinearRegression(db)

