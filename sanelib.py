# SANElib Prototype
# Standard-SQL Analytics for Numerical Estimation – SANE
# (c) 2020  Michael Kaufmann, Gabriel Stechschulte, Anna Huber, HSLU

import config as conf
import lib
from util.database import Database

if conf.DB_TYPE == "MYSQL":
    driver_name = "mysql+mysqlconnector"
    db_connection = {
        "drivername": driver_name,
        "host": conf.DB_HOST,
        "port": conf.DB_PORT,
        "username": conf.DB_USER,
        "password": conf.DB_PW,
        "database": conf.DB_NAME,
        "query": {"charset": "utf8"}
    }
elif conf.DB_TYPE == "MSSQL":
    driver_name = "mssql+pyodbc"
    db_connection = {
        "drivername": driver_name,
        "host": conf.DB_HOST,
        "database": conf.DB_NAME + '?trusted_connection=yes&driver=ODBC+Driver+13+for+SQL+Server'
    }
    dtc = lib.DecisionTreeClassifier
    pass
elif conf.DB_TYPE == "SQLITE":
    db_connection = {
        "drivername": "sqlite",
        "database": conf.DB_NAME,
        "path": conf.DB_PATH
    }
else:
    raise Exception("No valid DB_TYPE (config.py) provided! Please provide one of the following types: \n MYSQL\n SQLITE\n MSSQL (only for Decision Tree)")

if conf.DB_TYPE != "MSSQL":
    db = Database(db_connection)
    kmeans = lib.kmeans.KMeans(db)
    mdh = lib.mdh.MDH(db)
    linear_regression = lib.linear_regression.LinearRegression(db)
    dtc = lib.DecisionTreeClassifier
else:
    dtc = lib.DecisionTreeClassifier