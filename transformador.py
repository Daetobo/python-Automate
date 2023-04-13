import pandas as pd 
import numpy as np
import re
import utils
import json
import os
import datetime

ruta = os.getcwd() #Obtiene el directorio actual
sep = os.sep #Obtiene el separador de directorios predefinido del sistema
filetype = '*.xlsx' #Tipo de archivo a buscar
fechaActual = datetime.datetime.now().date()

def anexo_04(anex, columns):
    '''
        Función encargada de obtener la información de los archivos
        de escalamiento para el anexo 02 y darle el formato que se requiere
        para generar la plantilla para el convertidor
    '''
   
    fileNames = utils.findFile(anexo='anexo_04')
    
    for fileName in fileNames:
        df = pd.read_excel(fileName,sheet_name=1)
        if df.empty:
            print('No hay nada por convertir')
            continue
        
        rub = utils.output(ruta,fileName,sep,df)
        
        #Elimina espacios en blanco del dataframe
        utils.deleteSpaces(df=df)
        
        #Leer Mapeo columnas Json anexo_04
        mapping = json.load(open('map_anexo' + anex + '.json'))
        
        '''
            Ciclo que transforma la descripción de la transacción según anexo 10
            Cuadro 6. tipo de operación
        '''       
  
        for i in columns:
            for k, v in mapping[i].items():
                df = utils.convertData(
                    df=df,
                    column=i,
                    regex=k, 
                    value=v)
        df['Fecha_Vinculada'] = pd.to_datetime(df['Fecha_Vinculada'],format='%Y%m%d')
        df.Fecha_Vinculada = df.Fecha_Vinculada.dt.strftime('%Y-%m-%d')
        
        # Organizar en el orden que se requiere según plantilla circular 032 anexo_04
        df = df[['Id_Cliente','cod_tipo_doc','Nombre_Cliente','Fecha_Vinculada','Tipo_Cuenta','Numero_Cuenta','Dto/Credi','Valor_Transa','Descripcion_Transac','BENEFICIARIO','CUENTA']] # TODO cambiar nombres beneficiario y cuenta desde el modelo captaciones
        
        # Cambio de nombres de las columnas según plantilla circular 032 anexo_04
        df.columns = ['num_id_propietario','tipo_id_propietario','nombre_completo_titular','fecha_transaccion','tipo_producto','num_cuenta_producto','tipo_transaccion','valor_transaccion_debito','descripcion_transaccion','nombre_completo_beneficiario','num_cuenta_producto_beneficiario']
        
        col = df.columns.tolist()
        
        fields = utils.mapAnexo4()
        map_salida = json.load(open('map_salida_anexo' + anex + '.json'))
        
        '''
            Ciclo que inserta las nuevas columnas según la plantilla final
            anexo_04 circular 032
        '''
        for i in fields:
            if i not in col:
                for k, v in map_salida[i].items():
                    if i == 'rub':
                        df.insert(fields.index(i),i,rub)
                    elif i == 'fecha_radicacion':
                        df.insert(fields.index(i),i,fechaActual)
                    else:
                        df.insert(fields.index(i),i,v)
                        
        '''
            Igualar tipo de transacción credito, el beneficiario es el mismo cliente
        '''

        df.loc[df['tipo_transaccion']=='2','valor_transaccion_credito'] = df['valor_transaccion_debito']
        df.loc[df['tipo_transaccion']=='2','tipo_id_beneficiario'] = df['tipo_id_propietario']
        df.loc[df['tipo_transaccion']=='2','num_id_beneficiario'] = df['num_id_propietario']
        df.loc[df['tipo_transaccion']=='2','nombre_completo_beneficiario'] = df['nombre_completo_titular']
        df.loc[df['tipo_transaccion']=='2','tipo_producto_beneficiario'] = df['tipo_producto']
        df.loc[df['tipo_transaccion']=='2','num_cuenta_producto_beneficiario'] = df['num_cuenta_producto']
        df.loc[df['tipo_transaccion']=='2','valor_transaccion_debito'] = 0
        
        # filtrar por solo los campos que beneficiario trajo como numericos y
        # se transfiere  a la columna de numero de cuenta.
        
        
        df.fillna('n',inplace=True)

        df.loc[df.nombre_completo_beneficiario.str.isnumeric(),'num_cuenta_producto_beneficiario'] = df['nombre_completo_beneficiario']
        df.loc[df.nombre_completo_beneficiario.str.isnumeric(),'nombre_completo_beneficiario'] = 0
        df.loc[df['nombre_completo_beneficiario']=='n','nombre_completo_beneficiario'] = 0
        df.loc[df['num_cuenta_producto_beneficiario']=='n','num_cuenta_producto_beneficiario'] = 0

        cuentas = utils.accountSQL(df,'num_cuenta_producto_beneficiario')

        '''
            Homologación campo descripcion_transaccion cuando NA 
            Ningún tipo de transacción con los especificados en la circular 032 -
            anexo 10 cuadros complementario Cuadro 6. tipo de operación 
        '''
        
        df.loc[(df['descripcion_transaccion']!='04-ABONOS') & (df['descripcion_transaccion']!='01-CONSIGNACION LOCAL') & (df['descripcion_transaccion']!='05-REMESAS') & (df['descripcion_transaccion']!='06-CONSIGNACION NACIONAL') & (df['descripcion_transaccion']!='07-GIROS'),'descripcion_transaccion'] = '11-OTRO '+df['descripcion_transaccion']
        
        '''
            Homologación campo tipo documento cuando NA 
            Ningún tipo documento con los especificados en la circular 032 -
            anexo 10 cuadros complementario Cuadro 4. Tipo de identificación 
        '''
        df.loc[(df['tipo_id_propietario']!='13') & (df['tipo_id_propietario']!='22') & (df['tipo_id_propietario']!='31') & (df['tipo_id_propietario']!='12') & (df['tipo_id_propietario']!='41') & (df['tipo_id_propietario']!='11'),'tipo_id_propietario'] = '00'
                
            
        
        df.sort_values(by=['fecha_transaccion'], inplace=True, ascending=False)
        
        investigados = df['num_id_propietario'].unique()
        # Exportar resultado       
        for investigado in investigados:
            params = df['num_id_propietario'] == investigado
            ft = df[params]
            # ft.sort_values(by=['fecha_transaccion'], inplace=True, ascending=False)
            ft.to_excel(ruta + sep + f'respuestas' + sep + str(investigado) + '.xlsx',index=False)


anexo_04(anex="04", columns=['Tipo_Cuenta', 'Descripcion_Transac', 'Dto/Credi','cod_tipo_doc'])