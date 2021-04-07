import sys
import logging
import rds_config
import pymysql

rds_host  = rds_config.rds_instance_name
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def handler(event, context):
    item_count = 0

    with conn.cursor() as cur:
        cur.execute("create table Users (EmpID int NOT NULL, Name varchar(255) NOT NULL, LastName varchar(255) NOT NULL, PRIMARY KEY (EmpID))")
        cur.execute('insert into Users (EmpID, Name, LastName) values(00000001, "Kledson", "Basso")')
        cur.execute('insert into Users (EmpID, Name, LastName) values(00000002, "Augusto", "Corvo")')
        cur.execute('insert into Users (EmpID, Name, LastName) values(00000003, "Mariana", "Silva")')
        conn.commit()
        cur.execute("select * from Users")
        for row in cur:
            item_count += 1
            logger.info(row)
    conn.commit()

    return "Added %d items from RDS MySQL table" %(item_count)
