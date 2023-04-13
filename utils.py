import pandas as pd 
import re
import os
import glob
import datetime

def convertData(df, column, regex, value):
    if column == 'cod_tipo_doc':
        df.loc[df[column]==int(regex),column] = value
    else:
        df.loc[df[column].str.contains(str(regex), flags=re.IGNORECASE, regex=True), column ] = value
    return df

def mapAnexo4():
    
    title = ['rub','fecha_radicacion','num_id_propietario','tipo_id_propietario','nombre_completo_titular','fecha_transaccion','tipo_producto','num_cuenta_producto','cuenta_conjunta','tipo_transaccion','valor_transaccion_debito','valor_transaccion_credito','saldo_final','descripcion_transaccion','tipo_id_beneficiario','num_id_beneficiario','digito_verificacion_beneficiario','nombre_completo_beneficiario','tipo_producto_beneficiario','num_cuenta_producto_beneficiario']
    return title

def findFile(anexo):
    ruta = os.getcwd() #Obtiene el directorio actual
    sep = os.sep #Obtiene el separador de directorios predefinido del sistema
    filetype = '*.xlsx' #Tipo de archivo a buscar

    filename = glob.glob(ruta + sep + anexo + sep + filetype)
    return filename

def output(ruta,fileName,sep,df):
        fechaActual = datetime.datetime.now().date()
        delimiter = fileName.split(sep='\\')
        rub = delimiter[-1][:-13].strip()
        os.makedirs(ruta + sep + f'respuestas', exist_ok=True)
        # df.to_excel(ruta + sep + f'respuestas{sep}{fechaActual}' + sep + rub + '.xlsx',index=False)
        
        return rub

def deleteSpaces(df):
    '''
        Función utiliza Regex para reemplazar los valores en blanco por "n" 
        que significa no aplica
    '''
    df.replace('^\s*$','n', regex=True, inplace=True)

def accountSQL(df,colum):
    lista = ''
    arrayCuentas = df[colum].tolist()
    cuentas = [str(x) for x in arrayCuentas if x!=0 and str(x).isnumeric()]
    lista = list(set(cuentas))
    uniqueAccount = '(' + ','.join(lista) + ')'
    return uniqueAccount

