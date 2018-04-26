<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
Crea mappe pluvio_giorno ad uso del bollettino meteogiorno: plot cumulate del giorno 
precedente interrogando IRIS per i confini regionali e DBmeteo per i dati da pluviometro

Created on Fri Apr 20 12:02:05 2018
@author: mranci
"""
#per interrogare i DB
from sqlalchemy import *
import pg8000
import geopandas as gpd                           
from geopandas import GeoDataFrame
import pandas as pd                               

#per i grafici
import datetime as dt 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import Point
from mpl_toolkits.axes_grid1 import make_axes_locatable

# per schedulazione
##import schedule
##import time

def pluvio_graf():
    # definisco periodo 
    ieri=str((dt.date.today())-dt.timedelta(days=4))
    oggi=str(dt.date.today())                   

    # recupero confini ...
    engine = create_engine('postgresql+pg8000://'+IRIS_USER_ID+':'+IRIS_USER_PWD+'@'+IRIS_DB_HOST+'/'+IRIS_DB_NAME)
    conn=engine.connect()
    # ...regionali
    Query='Select * from "dati_di_base"."limite_regionale";'
    regione = gpd.read_postgis(Query, conn, 
                        geom_col='the_geom', crs={'init': 'epsg:3003'}, 
                        coerce_float=False)
    regione = regione.to_crs({'init': 'epsg:32632'})
    # ...provinciali
    Query='Select * from "dati_di_base"."limiti_provinciali";'
    province = gpd.read_postgis(Query, conn, 
                        geom_col='the_geom', crs={'init': 'epsg:32632'}, 
                        coerce_float=False)

    #recupero dati da pluviometro
    engine = create_engine('mysql+pymysql://'+MYSQL_USER_ID+':'+MYSQL_USER_PWD+'@'+MYSQL_DB_HOST+'/'+MYSQL_DB_NAME)
    conn=engine.connect()
    query="select  A_Sensori.IDsensore,  X(A_Sensori.CoordUTM ) as UTM_X, Y(A_Sensori.CoordUTM ) as UTM_Y,  date(Data_e_ora) as Data, sum(Misura) as Cumulata   from  A_Sensori ,  A_Stazioni ,  M_Pluviometri   where A_Sensori.IDstazione =A_Stazioni.IDstazione  and A_Sensori.IDsensore=M_Pluviometri.IDsensore and M_Pluviometri.Data_e_ora>='" + ieri + "' and M_Pluviometri.Data_e_ora<='"+ oggi+"' and (Flag_manuale='G' or Flag_manuale_DBunico in (-100,-101,-102) or (Flag_manuale='M' and Flag_automatica='P')) and A_Sensori.IDsensore not in (SELECT IDsensore from A_ListaNera where DataFine IS NULL) and A_Sensori.IDsensore in (select IDsensore from A_Sensori2Destinazione where Destinazione=12 and DataFine is null)  group by A_Sensori.IDsensore"
    result=pd.read_sql(query, conn)
    df = pd.DataFrame({"IDsensore": result['IDsensore'], "UTM_X": result['UTM_X'],"UTM_Y": result['UTM_Y'],"Cumulata": result['Cumulata']})
    # conversione a campi geometrici
    geometry = [Point(xy) for xy in zip(df['UTM_X'], df['UTM_Y'])]
    gdf = GeoDataFrame(df, crs={'init': 'epsg:32632'}, geometry=geometry)

    #GRAFICO
    # dimensioni 
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 10
    fig_size[1] = 10
    plt.rcParams["figure.figsize"] = fig_size
    
    ax=regione.plot(cmap='hot', alpha=0.1)  # grafico regione 
    ax.axes.get_xaxis().set_visible(False)  # tolgo label assi
    ax.axes.get_yaxis().set_visible(False)
    province.plot(ax=ax,facecolor='none',edgecolor='black', alpha=1) #sovrascrivo province

    # puntino in corrispondenza dei pluviometri
    graf=plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],marker='.',color='white')  
    # aggiungo cumulate con scala di colore cmap e dimensioni marker proporzionale ai mm
    cmap = plt.get_cmap('Blues')
    graf=plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],marker='s', s=df['Cumulata']*10, c=df['Cumulata'],cmap=cmap, alpha=1,vmin=0)  
    plt.title("Precipitazioni da " + ieri + " a " + oggi + "-- max=" + str(max(df['Cumulata'])) +"mm") #aggiungo titolo

    # aggiungo colorbar con le stesse dimensioni del grafico
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(graf, cax=cax, label="mm")

    plt.savefig("pluvio_giorno_III" + ieri + ".png", format='png') #eseguo e salvo il grafico

schedule.every().day.at("06:00").do(pluvio_graf)
while True:
    schedule.run_pending()
=======
# -*- coding: utf-8 -*-
"""
Crea mappe pluvio_giorno ad uso del bollettino meteogiorno: plot cumulate del giorno 
precedente interrogando IRIS per i confini regionali e DBmeteo per i dati da pluviometro

Created on Fri Apr 20 12:02:05 2018
@author: mranci
"""
#per interrogare i DB
from sqlalchemy import *
import pg8000
import geopandas as gpd                           
from geopandas import GeoDataFrame
import pandas as pd                               

#per i grafici
import datetime as dt 
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import Point
from mpl_toolkits.axes_grid1 import make_axes_locatable

# per schedulazione
##import schedule
##import time

def pluvio_graf():
    # definisco periodo 
    ieri=str((dt.date.today())-dt.timedelta(days=4))
    oggi=str(dt.date.today())                   

    # recupero confini ...
    engine = create_engine('postgresql+pg8000://'+IRIS_USER_ID+':'+IRIS_USER_PWD+'@'+IRIS_DB_HOST+'/'+IRIS_DB_NAME)
    conn=engine.connect()
    # ...regionali
    Query='Select * from "dati_di_base"."limite_regionale";'
    regione = gpd.read_postgis(Query, conn, 
                        geom_col='the_geom', crs={'init': 'epsg:3003'}, 
                        coerce_float=False)
    regione = regione.to_crs({'init': 'epsg:32632'})
    # ...provinciali
    Query='Select * from "dati_di_base"."limiti_provinciali";'
    province = gpd.read_postgis(Query, conn, 
                        geom_col='the_geom', crs={'init': 'epsg:32632'}, 
                        coerce_float=False)

    #recupero dati da pluviometro
    engine = create_engine('mysql+pymysql://'+MYSQL_USER_ID+':'+MYSQL_USER_PWD+'@'+MYSQL_DB_HOST+'/'+MYSQL_DB_NAME)
    conn=engine.connect()
    query="select  A_Sensori.IDsensore,  X(A_Sensori.CoordUTM ) as UTM_X, Y(A_Sensori.CoordUTM ) as UTM_Y,  date(Data_e_ora) as Data, sum(Misura) as Cumulata   from  A_Sensori ,  A_Stazioni ,  M_Pluviometri   where A_Sensori.IDstazione =A_Stazioni.IDstazione  and A_Sensori.IDsensore=M_Pluviometri.IDsensore and M_Pluviometri.Data_e_ora>='" + ieri + "' and M_Pluviometri.Data_e_ora<='"+ oggi+"' and (Flag_manuale='G' or Flag_manuale_DBunico in (-100,-101,-102) or (Flag_manuale='M' and Flag_automatica='P')) and A_Sensori.IDsensore not in (SELECT IDsensore from A_ListaNera where DataFine IS NULL) and A_Sensori.IDsensore in (select IDsensore from A_Sensori2Destinazione where Destinazione=12 and DataFine is null)  group by A_Sensori.IDsensore"
    result=pd.read_sql(query, conn)
    df = pd.DataFrame({"IDsensore": result['IDsensore'], "UTM_X": result['UTM_X'],"UTM_Y": result['UTM_Y'],"Cumulata": result['Cumulata']})
    # conversione a campi geometrici
    geometry = [Point(xy) for xy in zip(df['UTM_X'], df['UTM_Y'])]
    gdf = GeoDataFrame(df, crs={'init': 'epsg:32632'}, geometry=geometry)

    #GRAFICO
    # dimensioni 
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 10
    fig_size[1] = 10
    plt.rcParams["figure.figsize"] = fig_size
    
    ax=regione.plot(cmap='hot', alpha=0.1)  # grafico regione 
    ax.axes.get_xaxis().set_visible(False)  # tolgo label assi
    ax.axes.get_yaxis().set_visible(False)
    province.plot(ax=ax,facecolor='none',edgecolor='black', alpha=1) #sovrascrivo province

    # puntino in corrispondenza dei pluviometri
    graf=plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],marker='.',color='white')  
    # aggiungo cumulate con scala di colore cmap e dimensioni marker proporzionale ai mm
    cmap = plt.get_cmap('Blues')
    graf=plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],marker='s', s=df['Cumulata']*10, c=df['Cumulata'],cmap=cmap, alpha=1,vmin=0)  
    plt.title("Precipitazioni da " + ieri + " a " + oggi + "-- max=" + str(max(df['Cumulata'])) +"mm") #aggiungo titolo

    # aggiungo colorbar con le stesse dimensioni del grafico
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(graf, cax=cax, label="mm")

    plt.savefig("pluvio_giorno_III" + ieri + ".png", format='png') #eseguo e salvo il grafico

schedule.every().day.at("06:00").do(pluvio_graf)
while True:
    schedule.run_pending()
>>>>>>> 6bb4ab2c43cedbd7b135a8e7f8dc5a7dab60f107
    time.sleep(1)