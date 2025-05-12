import os
class Config:
    SERVER = os.environ["Server"]
    DATABASE = os.environ["Database"]
    USERNAME = os.environ["Username"]
    PASSWORD = os.environ["Password"]
    DRIVER = os.environ["Driver"]

    #SERVER = 'hexango.clqoi2aemq8p.ap-south-1.rds.amazonaws.com'
    #DATABASE = "foretale"
    #USERNAME = "admin"
    #PASSWORD = "foreHEX!2025"
    #DRIVER = "{ODBC Driver 18 for SQL Server}"
