# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:34:36 2019

@author: mranci
"""

from owslib.wms import WebMapService
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import io
import datetime as dt


###### data e ora delle immagini
data_e_ora=str((dt.date.today())-dt.timedelta(days=1))+'T12:00:00.000Z'
print("\n DATA E ORA: " + data_e_ora)
proiezione='EPSG:4326'
formato='image/png'
estensione = (-40, 25, 30, 70) # Left, bottom, right, top
size_map=(1024 , 800)

############   IMPORT MSG 
print("IMPORT MSG\n")

wms_msg = WebMapService('http://eumetview.eumetsat.int/geoserver/wms')
name_msg='meteosat:msg_vis006'
list(wms_msg.contents)
#print (wms_msg[name_msg].crsOptions)

  
img_msg = wms_msg.getmap(   layers=[name_msg],
                            styles=['raster'],
                            bbox=estensione,
                            size=size_map,
                            srs=proiezione,
                            time=data_e_ora,
                            format=formato,
                            transparent=True
                          )

### MSG SU FILE
#out_msg = open('msg.jpg', 'wb')
#out_msg.write(img_msg.read())
#out_msg.close()


############   IMPORT MSG
#layer = wms_msg.contents[name_msg] #per lista dei WMS disponibili
print("IMPORT coastline\n")
name_cl='overlay:ne_10m_coastline'

#print (wms_msg[name_cl].crsOptions)

  
img_cl = wms_msg.getmap(   layers=[name_cl],
#                            styles=['raster'],
                            bbox=estensione,
                            size=size_map,
                            srs=proiezione,
                            time=data_e_ora,
                            format=formato,
                            transparent=True
                          )

###########  IMPORT ECMWF
print("IMPORT ECMWF\n")
wms_ecmwf = WebMapService('https://apps.ecmwf.int/wms/?token=MetOceanIE&')
name_ecmwf='z500_public'
#print (wms_ecmwf[name_ecmwf].crsOptions)
#print (wms_ecmwf[name_ecmwf].styles)
  
img_ecmwf = wms_ecmwf.getmap(  layers=[name_ecmwf],
                               styles=['ct_red_i5_t2'],
                               bbox=estensione,
                               size=size_map,
                               srs=proiezione,
                               time=data_e_ora,
                               format=formato,
                               transparent=True
                              )
### ECMWF SU FILE
#out_ecmwf = open('ecmwf.jpg', 'wb')
#out_ecmwf.write(img_ecmwf.read())
#out_ecmwf.close()

print("plot MSG e ECMWF\n")
image_msg = io.BytesIO(img_msg.read())
data_msg = plt.imread(image_msg)

image_ecmwf = io.BytesIO(img_ecmwf.read())
data_ecmwf = plt.imread(image_ecmwf)

image_cl = io.BytesIO(img_cl.read())
data_cl = plt.imread(image_cl)

fig = plt.figure(figsize=(20,20*800/1024))

#proj = ccrs.UTM(zone=32)
proj = ccrs.PlateCarree()
#proj = ccrs.Geodetic()

#ax = fig.add_axes([0,0,1,1], projection=cartopy.crs.PlateCarree())
#ax = plt.axes(projection=proj)
ax = plt.axes(projection=proj)


ax.imshow ( data_msg  , origin="upper", extent=estensione, transform=proj )
ax.imshow ( data_ecmwf, origin="upper", extent=estensione, transform=proj )
ax.imshow ( data_cl, origin="upper", extent=estensione, transform=proj )
#ax.coastlines('50m',color='red')
ax.set_extent(estensione)

plt.savefig('sinottica.png')

