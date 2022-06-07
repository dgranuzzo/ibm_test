#coding: utf-8
#import mysql.connector
#from mysql.connector import errorcode
import psycopg2
from psycopg2.extras import execute_values


class SqlDbClass:
    def __init__(self,config):
        """
        Conect to db
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
            connection = psycopg2.connect(database = self.db,
                                    user = self.user,
                                    password = self.passwd,
                                    host = self.host,
                                    port = self.port)
             
            return connection, "ok"
        except Exception as e:
            msg = str(e)
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

    def save_urls(self,values):
        message = "no connection"
        #sql = """INSERT INTO URLS (initial_url ,found_url) VALUES (%s, %s)"""
        # values format: [(1, 2), (4, 5), (7, 8)]
        sql = "INSERT INTO URLS (initial_url ,found_url) VALUES %s"

        conn, status = self.connect()
        if conn != None:
            try:
                cursor = conn.cursor()
                #cursor.executemany(sql, values)
                execute_values(cursor,sql, values)
                conn.commit()
                #print(values)
                print("rows count:".format(cursor.rowcount))
                return {"status":"ok","rows_count":cursor.rowcount,"message":"ok"}
            except Exception as e:
                message = str(e)
                conn.rollback()
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

    def insert_into_urls(self, initial_url,search_url):
        sql = "insert into URLS ( initial_url ,found_url ) VALUES ('{}' ,'{}')".format(initial_url,search_url)
        r = self.exec_sql(sql)
        return r

    def exec_sql(self,sql):
        print("exec_sql: {}".format(sql))
        conn, status = self.connect()
        rows_count = 0
        if conn != None:
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows_count = cursor.rowcount
                conn.commit()
                status = "ok"
            except Exception as e:
                status = str(e)
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
                return {"status":status,"rows_count":rows_count}
        else:
            return {"status":status,"rows_count":rows_count}


    def create_url_table(self):
        sql = """
        CREATE TABLE  IF NOT EXISTS URLS1 (
            id SERIAL PRIMARY KEY,
            initial_url TEXT,
            found_url TEXT
            );
        """
        response = self.exec_sql(sql)
        return response
