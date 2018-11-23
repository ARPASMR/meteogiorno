#!/usr/bin/env python
"""
Crea mappe pluvio_giorno ad uso del bollettino meteogiorno: plot cumulate del giorno 
precedente interrogando IRIS per i confini regionali e DBmeteo per i dati da pluviometro

Created on Fri Apr 20 12:02:05 2018
@author: mranci
"""

#per interrogare i DB
import os
import pg8000
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from sqlalchemy import *

#per i grafici
import datetime as dt
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Point
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

IRIS_USER_ID=os.getenv('IRIS_USER_ID')
IRIS_USER_PWD=os.getenv('IRIS_USER_PWD')
IRIS_DB_NAME=os.getenv('IRIS_DB_NAME')
IRIS_DB_HOST=os.getenv('IRIS_DB_HOST')

MYSQL_USER_ID=os.getenv('MYSQL_USER_ID')
MYSQL_USER_PWD=os.getenv('MYSQL_USER_PWD')
MYSQL_DB_NAME=os.getenv('MYSQL_DB_NAME')
MYSQL_DB_HOST=os.getenv('MYSQL_DB_HOST')

def make_cmap(colors, position=None, bit=False):
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256, gamma=1)
    return cmap

def pluvio_graf():
    # definisco periodo
    ieri=str((dt.date.today())-dt.timedelta(days=1))
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
     # ...laghi
    Query='Select * from "dati_di_base"."laghi";'
    laghi = gpd.read_postgis(Query, conn,
                        geom_col='the_geom', crs={'init': 'epsg:32632'},
                        coerce_float=False)
    
      
    #recupero dati da pluviometro
    engine = create_engine('mysql+mysqldb://'+MYSQL_USER_ID+':'+MYSQL_USER_PWD+'@'+MYSQL_DB_HOST+'/'+MYSQL_DB_NAME)  
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
    #plt.rcParams["figure.figsize"] = fig_size
    ax=regione.plot(cmap='binary', alpha=0.1)  # grafico regione
    ax.axes.get_xaxis().set_visible(False)  # tolgo label assi
    ax.axes.get_yaxis().set_visible(False)
    
    # aggiungo cumulate con scala di colore cmap e dimensioni marker proporzionale ai mm
    white      = (255,255,255)
    lightgray  = (200,200,200)
    gray       = (155,125,150)
    blue       = (  0,100,255)
    green      = (  5,140, 45)
    lightgreen = (  5,255,  5)
    yellow     = (255,255,  0)
    lightorange= (255,200,  0)
    orange     = (255,125,  0)
    red        = (255, 25,  0)
    violet     = (175,  0,220)
    darkviolet = (130,  0,220)
    darkdark   = (100,  0,220)
    colors = [white,lightgray, gray, blue, green, lightgreen, yellow, lightorange, orange, red, violet, darkviolet, darkdark]
    n_bins = [0, 0.5, 1, 5, 10, 20, 40, 60, 80, 100, 150, 200, 250]  # Discretizes the interpolation into bins
    tick = ["0.1", "0.5", "1", "5", "10", "20", "40", "60", "80", "100", "150", "200", "250"]
    cmap=make_cmap(colors, bit=True)
    norm = mpl.colors.BoundaryNorm(n_bins, cmap.N)
     
    # puntino in corrispondenza dei pluviometri
    #graf=plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],marker='.',color='gray')
    graf = plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],c="black",s=100)
    graf = plt.scatter(gdf['UTM_X'], gdf['UTM_Y'],c=df['Cumulata'],s=100,cmap=cmap, norm=norm, vmin=0)
    plt.title("cumulata massima=" + str(max(df['Cumulata'])) +"mm") #aggiungo titolo
    
    # aggiungo colorbar con le stesse dimensioni del grafico
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar= plt.colorbar(graf, cax=cax, label="mm", ticks=n_bins)
        
    province.plot(ax=ax,facecolor='none',edgecolor='gray', alpha=1) #sovrascrivo province
    laghi.plot(ax=ax,facecolor='skyblue',edgecolor='none', alpha=1) #sovrascrivo laghi
    
    plt.savefig("pluvio_giorno_" + ieri + ".png", format='png') #eseguo e salvo il grafico

pluvio_graf()


