from owslib.wms import WebMapService
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import io
import datetime as dt
import numpy as np
from pyproj import Proj, transform


###### data e ora delle immagini
data_e_ora=str((dt.date.today())-dt.timedelta(days=1))+'T12:00:00.000Z'
proiezione='EPSG:4326' #proiezione di partenza (WGS 84 lat lon)
formato='image/png'
estensione = (-40, 25, 30, 70) # Left, bottom, right, top
size_map=(1024 , 800)

############   IMPORT MSG (immagine satellite VIS6)
wms_msg = WebMapService('http://eumetview.eumetsat.int/geoserver/wms')
name_msg='meteosat:msg_vis006'

img_msg = wms_msg.getmap(   layers=[name_msg],
                            styles=['raster'],
                            bbox=estensione,
                            size=size_map,
                            srs=proiezione,
                            time=data_e_ora,
                            format=formato,
                            transparent=True
                          )

############   IMPORT MSG (coastlines)
layer = wms_msg.contents[name_msg] #per lista dei WMS disponibili
name_cl='overlay:ne_10m_coastline'

img_cl = wms_msg.getmap(   layers=[name_cl],
                            bbox=estensione,
                            size=size_map,
                            srs=proiezione,
                            time=data_e_ora,
                            format=formato,
                            transparent=True
                          )

###########  IMPORT ECMWF (isolinee del geopotenziole a 500hPa)
wms_ecmwf = WebMapService('https://apps.ecmwf.int/wms/?token=MetOceanIE&')
name_ecmwf='z500_public'
  
img_ecmwf = wms_ecmwf.getmap(  layers=[name_ecmwf],
                               styles=['ct_red_i5_t2'],
                               bbox=estensione,
                               size=size_map,
                               srs=proiezione,
                               time=data_e_ora,
                               format=formato,
                               transparent=True
                              )

#
image_msg = io.BytesIO(img_msg.read())
data_msg = plt.imread(image_msg)
#
image_ecmwf = io.BytesIO(img_ecmwf.read())
data_ecmwf = plt.imread(image_ecmwf)
#
image_cl = io.BytesIO(img_cl.read())
data_cl = plt.imread(image_cl)

# impostazione del grafico
fig = plt.figure(figsize=(20,20*800/1024))

#LambertConformal 
proj = ccrs.LambertConformal(central_longitude=0, central_latitude=0.0, false_easting=0.0, false_northing=0.0, secant_latitudes=None, standard_parallels=None, globe=None, cutoff=-30)
proj_string = Proj("+proj=laea +lat_0=45.5 +lon_0=-114.125 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs")

#devo riproiettare i punti limite dell'estensione e scegliere i limiti più "interni"
LB=(estensione[0],estensione[1])
LT=(estensione[0],estensione[3])
RB=(estensione[2],estensione[1])
RT=(estensione[2],estensione[3])
x_lim=(LB[0],LT[0],RB[0],RT[0]) #coordinate x degli angoli della vista
y_lim=(LB[1],LT[1],RB[1],RT[1]) #coordinate y degli angoli della vista

#proiezione di partenza
p1 = Proj(proj='latlong',datum='WGS84')

#Proiezione di destinazione
p2 = proj_string

#converto le coordinate degli estremi
x_lim_p2 = np.zeros(len(x_lim))
y_lim_p2 = np.zeros(len(y_lim))
for i in range(len(x_lim)):
    x_lim_p2[i], y_lim_p2[i] = transform(p1, p2, x_lim[i], y_lim[i])

#scelgo i limiti più "esterni"
MinEst = min(x_lim_p2[0],x_lim_p2[1])
MaxEst = max(x_lim_p2[2],x_lim_p2[3])
MinNord = min(y_lim_p2[0],y_lim_p2[2])
MaxNord = max(y_lim_p2[1],y_lim_p2[3])

#estensione vista con coordinate convertite nel nuovo SDR
estensione = (MinEst, MinNord, MaxEst, MaxNord) #Left, bottom, right, top

ax = plt.axes(projection=proj)

ax.imshow ( data_msg  , origin="upper", extent=estensione, transform=proj )
ax.imshow ( data_ecmwf, origin="upper", extent=estensione, transform=proj )
ax.imshow ( data_cl, origin="upper", extent=estensione, transform=proj )

plt.savefig('sinottica' + str((dt.date.today())-dt.timedelta(days=1)) + '.png')
