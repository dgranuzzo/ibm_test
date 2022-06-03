#coding: utf-8
import mysql.connector
from mysql.connector import errorcode


class MysqlDb:
    def __init__(self,config):
        """
        Conect to Mysql
        Args:
            config: {'server', 'database', 'user', 'password', 'port'}
        """
        self.db = config['database']
        self.user = config['user']
        self.passwd = config['password']
        self.host = config['server']
        self.port = config['port']
    
    def connect(self):
        try:
            connection = mysql.connector.connect(database = self.db,
                                         host = self.host,
                                         port = self.port,
                                         user = self.user,
                                         passwd = self.passwd)
            return connection, "ok"
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                msg = "invalid DB user or pass"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                msg = "invalid DB"
            else:
                msg = err
            return None, msg
   

    def get_urls(self,url):
        sql = "select * from urls where initial_url = '{}'".format(url)
        data = self.get_data(sql)
        return data


    def get_url_by_id(self,id):
        sql = "select * from urls where id = '{}'".format(id)
        data = self.get_data(sql)
        return data
        

    def get_all(self):
        sql = "select * from urls;"
        data = self.get_data(sql)
        return data

    def save_urls(self,vals):
        message = "no connection"
        sql = "INSERT INTO URLS ('initial_url','found_url') VALUES (%s, %s)"
        conn, status = self.connect()
        if conn != None:
            try:
                cursor = conn.cursor()
                cursor.executemany(sql, vals)
                conn.commit()
                return {"status":"ok","rows_count":cursor.rowcount,"message":"ok"}
            except Exception as e:
                message = str(e)
            finally:
                cursor.close()
                conn.close()
                return {"status":"except","rows_count":0,"message":message}
        else:
            return {"message":message,"rows_count":0,"status":status}


    def get_data(self,sql):
        conn, status = self.connect()
        if conn != None:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                results = cursor.fetchall() #fetchone()
                fields = cursor.description
                fields_names = [x[0] for x in fields]
                status = "ok"
            except Exception as e:
                results = str(e)
                fields_names = None
                status = "except"
            finally:
                cursor.close()
                conn.close()
                return {"items":results,"fields":fields_names,"status":status}
        else:
            return {"items":None,"fields":None,"status":status}


    def exec_sql(self,sql):
        print(sql)
        conn, status = self.connect()
        if conn != None:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                status = "ok"
            except Exception as e:
                status = str(e)
            finally:
                cursor.close()
                conn.close()
                return {"status":status}
        else:
            return {"status":status}


    def create_database(self):
        sql = """
            CREATE DATABASE urls_db;
        """
        self.exec_sql(sql)
        return {"status":"ok"}


    def create_url_table(self):
        sql = """
        CREATE TABLE urls (
            id int NOT NULL AUTO_INCREMENT,
            initial_url varchar(500),
            found_url varchar(500),
            found_url_searched boolean DEFAULT FALSE,
            parent_id_url int,
            PRIMARY KEY (id)
            );
        """
        self.exec_sql(sql)
        return {"status":"ok"}
