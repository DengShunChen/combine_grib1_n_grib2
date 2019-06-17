#!/usr/bin/env python 
import pygrib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec as gspec
from mpl_toolkits.basemap import Basemap
 
class Plotgrib():
  def __init__(self,filename):
    self.filename = filename
    # read grib data
    self.grbs = pygrib.open(filename)

    self.grbs.rewind()
    grb = self.grbs.readline()
    # keys
    self.keys = grb.keys()
    # lats and lons 
    self.lats, self.lons = grb.latlons()

  def show(self):
    self.grbs.rewind()
    for grb in self.grbs:
      print(grb)

  def read_grib(self,field,level):
    # select field
    self.grbs.rewind()
    for grb in self.grbs:
      if grb.parameterName == field and grb.level == level: 
        print(grb.parameterName,grb.level)
        pgrb = grb
    return pgrb

  def write_grib(self,grbout,grb):
    msg = grb.tostring()
    ret = grbout.write(msg)

  def grib_list(self,short=False,medium=False):
    import sys
    pygrib.tolerate_badgrib_on()
    fname = self.filename
    grbs = pygrib.open(fname)
    if short:
      for grb in grbs:
        sys.stdout.write(repr(grb)+'\n')
    elif medium:
      for grb in grbs:
        try:
            grb.expand_grid(False); data = grb.values
            sys.stdout.write(repr(grb)+':min/max=%g/%g'%(data.min(), data.max())+'\n')
        except:
            sys.stdout.write(repr(grb)+':min/max=NO DATA'+'\n')
    else:
      for grb in grbs:
        sys.stdout.write('------message %d------\n' % grb.messagenumber)
        for k in grb.keys():
            if k.startswith('mars'): continue
            if k in ['values','codedValues','packedValues','unpackedValues']: continue
            if grb.is_missing(k) and k not in ['analDate','validDate']:
                sys.stdout.write('%s = MISSING\n' % k)
            else:
                try:
                    v = getattr(grb,k)
                    sys.stdout.write('%s = %s\n'%(k,v))
                except:
                    sys.stdout.write('%s = NOT FOUND\n'%k)
    sys.stdout.write('packing = %s\n' % grb.packingType)
    grbs.close()
     
  # plot grib
  def plot_field(self,lons,lats,data,figurename):
    fig = plt.figure(figsize=(10,6),dpi=100)
    plt.subplots_adjust(top=0.85,bottom=0.15,right=0.95,left=0.05)
    gs = gspec.GridSpec(1,1)
    ax = plt.subplot(gs[0])
    # plot map 
   #m = Basemap(lon_0=180,ax=ax)
    print(lons.min(),lons.max(),lats.min(),lats.max())
    m = Basemap(projection='mill',llcrnrlon=lons.min(),llcrnrlat=lats.min(),urcrnrlon=lons.max(),urcrnrlat=lats.max(),lat_0=23.5,lon_0=121.)
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
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02 ])
    plt.colorbar(shading, cax=cbar_ax, orientation='horizontal')
    # plot contour
    contour = ax.contour(x, y, data, clevels, colors='k', linewidths=0.5)
    plt.clabel(contour, inline=True, fontsize=10, fmt='%5.1f')
    # plot title 
    plt.title('CWB GFS',fontsize='large',fontweight='bold')
    plt.suptitle('%s \n%s  valid at %s' % (var_substr,title_substr,vdate_substr),fontsize='x-large',fontweight='bold')
    # save   
    plt.savefig(figurename) 
    plt.show()

  def plot(self,field,level):
    global var_substr,title_substr,vdate_substr
    print('plot...')
    # get field 
    grb_data = self.read_grib(field,level) 
    data = grb_data.values    
    lats,lons = grb_data.latlons() 
    # set titile
    vdate_substr = str(grb_data.dataDate) + str(grb_data.dataTime)
    if level == 2 and name == 'Temperature':
      var_substr = str(level) + ' meters  ' + grb_data.name
    else:
      var_substr = str(level) + ' hPa  ' + grb_data.name
    title_substr = 'forecast hour %3.3d ' % (grb_data.forecastTime)
    # figure name
    figurename = field + '_' + str(level) + '.pdf'
    # plot field
    self.plot_field(lons,lats,data,figurename)

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 1:
      filename = 'gfs.pgrb2f00.18070718'
    else:
      filename = sys.argv[1]

    pg = Plotgrib(filename)
    pg.show()
    pg.showkeys()
    pg.grib_list()

#   field = 'Temperature'
#   level = 850  # hPa
#   pg.plot(field,level)
