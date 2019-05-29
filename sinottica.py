from owslib.wms import WebMapService
import cartopy.crs as ccrs
import matplotlib
matplotlib.use('Agg')
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
size_map=(1000 , 600)

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
fig = plt.figure(figsize=(10,10*600/1000))

proj=ccrs.PlateCarree()

ax = plt.axes(projection=proj)

ax.imshow ( data_msg  , origin="upper", extent=estensione, transform=proj )
ax.imshow ( data_ecmwf, origin="upper", extent=estensione, transform=proj )
ax.imshow ( data_cl, origin="upper", extent=estensione, transform=proj )

plt.savefig('sinottica' + str((dt.date.today())-dt.timedelta(days=1)) + '.png', bbox_inches='tight')
