#!/usr/bin/env python
import sys
import numpy as np
from plotgrib import Plotgrib
from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec as gspec

def check(ncep_lats,ncep_lons,ec_value,ncep_value):
  #print(ncep_lons,ncep_lats)
  #print(ec_value,ncep_value)
  fig = plt.figure(figsize=(10,6),dpi=100)
  plt.subplots_adjust(top=0.85,bottom=0.15,right=0.95,left=0.05)
  gs = gspec.GridSpec(1,2)

  plt.subplot(gs[0])
  m = Basemap(projection='stere',lon_0=121,lat_0=23.5,lat_ts=23.5,\
            llcrnrlat=17.,urcrnrlat=30.,\
            llcrnrlon=115.,urcrnrlon=129,\
            rsphere=6371200.,resolution='l',area_thresh=10000)
  m.drawmapboundary(fill_color='white',linewidth=0.5)
  m.fillcontinents(color='k',lake_color='k',zorder=1)
  m.drawparallels(np.arange(-90,91,20), labels=[1,1,0,1])
  m.drawmeridians(np.arange(-180,180,40), labels=[1,1,0,1])

 # max and min values
  vmax = np.max(np.amax(ncep_value,axis=0))
  vmin = np.min(np.amin(ncep_value,axis=0))

  # increaments 
  inc = (vmax - vmin)/100.
  levels = np.arange(vmin,vmax,inc)
  clevels = np.arange(vmin,vmax,inc*10)

  x,y=m(ncep_lons,ncep_lats)
  shading1 = m.contourf(x, y, ec_value, levels, cmap='RdYlBu_r',  alpha=0.75, zorder=2)
  contour1 = m.contour(x, y, ec_value, clevels, colors='k', linewidths=0.8,zorder=3)
  plt.clabel(contour1, inline=True, fontsize=10, fmt='%5.1f')
  plt.title('0.5*(ECMWF+NCEP)')
  cbar_ax = fig.add_axes([0.05, 0.08, 0.4, 0.02 ])
  plt.colorbar(shading1, cax=cbar_ax, orientation='horizontal')

  plt.subplot(gs[1])

  m = Basemap(projection='stere',lon_0=121,lat_0=23.5,lat_ts=23.5,\
            llcrnrlat=17.,urcrnrlat=30.,\
            llcrnrlon=115.,urcrnrlon=129,\
            rsphere=6371200.,resolution='l',area_thresh=10000)
  m.drawmapboundary(fill_color='white',linewidth=0.5)
  m.fillcontinents(color='k',lake_color='k',zorder=1)
  m.drawparallels(np.arange(-90,91,20), labels=[1,1,0,1])
  m.drawmeridians(np.arange(-180,180,40), labels=[1,1,0,1])

  x,y=m(ncep_lons,ncep_lats)
  shading2 = m.contourf(x, y, ncep_value, levels, cmap='RdYlBu_r',  alpha=0.75, zorder=2)
  contour2 = m.contour(x, y, ncep_value, clevels, colors='k', linewidths=0.8, zorder=3)
  plt.clabel(contour2, inline=True, fontsize=10, fmt='%5.1f')
  plt.title('NCEP')
  cbar_ax = fig.add_axes([0.55, 0.08, 0.4, 0.02 ])
  plt.colorbar(shading2, cax=cbar_ax, orientation='horizontal')

def plot(ecgrib,ncepgrib):
  ecgrib.grbs.rewind()
  ncepgrib.grbs.rewind()

  level_list=['850','200','500']
  vname_dict={'850':['u-component of wind','v-component of wind','Temperature','Relative humidity','Geopotential height'],
              '200':['u-component of wind','v-component of wind'],
              '500':['Geopotential height']}

  for i,ecgrb in enumerate(ecgrib.grbs):
    parameterName,level = ecgrb.parameterName,ecgrb.level
    if str(level) in level_list:
      if parameterName in vname_dict[str(level)]:
        # select field 
        try:
          ncepgrb = ncepgrib.grbs.select(parameterName=parameterName,level=level)[0]
        except:
          continue

        # extract NCEP map with ECMWF domain area
        xi = 122 ; xe = 145 ;  yi = 232 ; ye = 255
        xi = 118 ; xe = 150 ;  yi = 228 ; ye = 260
        ncep_value = ncepgrb.values[xi:xe,yi:ye]
        ec_value = ecgrb.values[xi:xe,yi:ye]

        # get NCEP grib2 latitude and logitude information
        ncep_lats,ncep_lons = ncepgrb.latlons()

        ncep_lats = ncep_lats[xi:xe,yi:ye]
        ncep_lons = ncep_lons[xi:xe,yi:ye]
        print('%2.2d %s at %s hPa' % (i,parameterName,level) )

        # plot conbine
        check(ncep_lats,ncep_lons,ec_value,ncep_value)
        plt.suptitle('%s  %s hPa' % (ecgrb.parameterName,ecgrb.level))
        plt.savefig('%s_%s.png' % (ecgrb.parameterName,ecgrb.level))
        plt.close()

if __name__ == '__main__':
  if len(sys.argv) < 2:
    filename = 'gfs.pgrb2f00.18070718'
  else:
    filename = sys.argv[1]

  ecfile='./gfs.pgrb2f00.18080700.ecmwf'
  ncepfile='getAVN/18080700/gfs.pgrb2f00.18080700'
  ecgrib = Plotgrib(ecfile)
  ncepgrib = Plotgrib(ncepfile)

  plot(ecgrib,ncepgrib)

