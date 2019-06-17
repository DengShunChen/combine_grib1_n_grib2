#!/usr/bin/env python 
import pygrib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec as gspec
from mpl_toolkits.basemap import Basemap
import urllib.request as ur

# CWB Open Data 
def cwb_token(dataid):
  dataid="M-A0060-000"
  token="CWB-0F2C298D-3769-46D4-8A56-50A8B040EEC9"
  dataformat='GRIB2'
  url="https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/{}?Authorization={}&format={}".format(dataid,token,dataformat)
  url = 'https://opendata.cwb.gov.tw/dataset/mathematics/%s' % dataid
  return url

# local filename 
def get_filename(dataid):
  subfix = '.grb2'
  filename = dataid + subfix
  #filename = 'gfs.t18z.pgrb2.0p25.anl'
  return filename

# get data
def get_data(dataid):
  url = cwb_token(dataid)
  filename = get_filename(dataid)
  print('download data ',filename)
  print(url)
  ur.urlretrieve(url,filename)

  return filename

def read_grib(filename,field,level):
  # gread grib data
  grbs = pygrib.open(filename)

  # select field
  for grb in grbs:
      if grb.parameterName == field and grb.level == level: 
          pgrb = grb
  return pgrb
   
# plot data 
def plot_field(lons,lats,data,figurename):

  fig = plt.figure(figsize=(10,6),dpi=100)
  plt.subplots_adjust(top=0.85,bottom=0.15,right=0.95,left=0.05)
  gs = gspec.GridSpec(1,1)
  ax = plt.subplot(gs[0])

  # plot map 
  m = Basemap(lon_0=180,ax=ax)
  m.drawmapboundary(fill_color='white',linewidth=0.5)
  m.fillcontinents(color='k',lake_color='k',zorder=0)
  m.drawparallels(np.arange(-90,91,20), labels=[1,1,0,1])
  m.drawmeridians(np.arange(-180,180,40), labels=[1,1,0,1])

  # to map x y 
  x,y = m(lons,lats)

  # max and min values
  vmin = data.min()
  vmax = data.max()

  # increaments 
  inc = (vmax - vmin)/50.
  levels = np.arange(vmin,vmax,inc)
  clevels = np.arange(vmin,vmax,inc*2)

  # plot countourf
  shading = ax.contourf(x, y, data, levels, cmap='RdYlBu_r',  alpha=0.75)

  # plot contour
  contour = ax.contour(x, y, data, clevels, colors='k', linewidths=0.5)
  plt.clabel(contour, inline=True, fontsize=10, fmt='%5.1f')

  # plot title 
  plt.title('CWB GFS',fontsize='large',fontweight='bold')
  plt.suptitle('%s \n%s  valid at %s' % (var_substr,title_substr,vdate_substr),fontsize='x-large',fontweight='bold')

  cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02 ])
  plt.colorbar(shading, cax=cbar_ax, orientation='horizontal')

  plt.savefig(figurename)

  plt.show()

if __name__ == '__main__':

  global var_substr,title_substr,vdate_substr

  print('main program')

  # download open data
  dataid="M-A0060-000"
  filename = get_filename(dataid)
#  filename = get_data(dataid)

  # get field 
# field = 'Geopotential height'
  field = 'Temperature'
  level = 850  # hPa
  grb_data = read_grib(filename,field,level) 
  data = grb_data.values    
  lats,lons = grb_data.latlons()

  # set titile
  vdate_substr = str(grb_data.dataDate) + str(grb_data.dataTime)
  if level == 2 and name == 'Temperature':
    var_substr = str(level) + ' meters  ' + grb_data.name
  else:
    var_substr = str(level) + ' hPa  ' + grb_data.name
  title_substr = 'forecast hour %3.3d ' % (grb_data.forecastTime)
   
  figurename = field + '_' + str(level) + '.png'

  # plot field
  plot_field(lons,lats,data,figurename)

