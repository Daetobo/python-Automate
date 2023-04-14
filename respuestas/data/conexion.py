import pyodbc
import pandas as pd

def resultSet(data):
    try:
        connection = pyodbc.connect(
            driver='{iSeries Access ODBC Driver}',
            system='10.9.2.201',
            uid='NDAETOBO',
            pwd='colombia43'
        )
        
        if connection:
            cursor = connection.cursor()
            print('ANTES DE EJECUTAR ok!')
            sql = 'WITH temporalKey (key) AS (SELECT CXNAMK FROM VISIONR.CXREF WHERE CXNOAC in('+ data + ')) SELECT CNNAME FROM VISIONR.CNAME B,temporalKey C LEFT JOIN ON (C.CXNAMK = B.CNNAMK)  '
            print(sql)
            cursor.execute(sql)
            rs = pd.read_sql(sql,connection)
    except pyodbc.Error as ex:
        print('Error during connection: {}'.format(ex)) 
    finally:
        if connection:
            connection.close()
            print('connection closed')
    return rs