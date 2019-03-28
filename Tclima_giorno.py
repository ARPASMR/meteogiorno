#!/usr/bin/env python
#--------------

# scriptino per generare il file di precompilazione per tabella clima meteogiorno

# aprile, 2018, prima stesura in shell
# MS & UA

#marzo, 2019
# MR, UA & GC - passaggi a python, lettura DB e dockerizzazione
#----------------------------------------------------------------------

import os
from sqlalchemy import *
import pandas as pd
import datetime as dt

MYSQL_USER_ID  = os.getenv('MYSQL_USER_ID')
MYSQL_USER_PWD = os.getenv('MYSQL_USER_PWD')
MYSQL_DB_NAME  = os.getenv('MYSQL_DB_NAME')
MYSQL_DB_HOST  = os.getenv('MYSQL_DB_HOST')


    # definisco periodo
def tabella():
     DATAI=str((dt.date.today())-dt.timedelta(days=1))
     DATAF=str(dt.date.today())
     DATACLIMA="2010-" + DATAI[5:] 
     #
     file_out = open('Tabella_Clima_' + DATAI + '.txt','w')

     siti = [["Milano", 5897], ["Pavia", 8157], ["Mantova", 5121],["Brescia", 2414],["Sondrio", 2096]]
     for i in range(len(siti)):
        # sito
        file_out.write('\n\n' + str(siti[i][0]) + '\n')
        # recupero dati da clima
        file_max = open( "Massima_81-10_" + siti[i][0] + ".txt", "r")
        #.....
        #.....

        #recupero da DBmeteo i dati di temperatura di ieri
        engine = create_engine('mysql+mysqldb://'+MYSQL_USER_ID+':'+MYSQL_USER_PWD+'@'+MYSQL_DB_HOST+'/'+MYSQL_DB_NAME)  
        conn=engine.connect()
        query="select  min(Misura) as Tmin, max(Misura) as Tmax from M_Termometri where IDsensore=" + str(siti[i][1]) + " and Data_e_ora>='"  + DATAI + "' and Data_e_ora<='" + DATAF + "'"
        result=pd.read_sql(query, conn)
        file_out.write(str(result['Tmin']) + '\n')
        file_out.write(str(result['Tmax']) + '\n')

     file_out.close() 
 

tabella()