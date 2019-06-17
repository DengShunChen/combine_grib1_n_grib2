#!/usr/bin/env python
import sys
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


def mergeplot():
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

  x,y=m(ncep_lons,ncep_lats)
  shading1 = m.contourf(x, y, 0.5*(ec_value+ncep_value), cmap='RdYlBu_r',  alpha=0.75, zorder=2)
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
  shading2 = m.contourf(x, y, ncep_value, cmap='RdYlBu_r',  alpha=0.75, zorder=2)
  plt.title('NCEP')
  cbar_ax = fig.add_axes([0.55, 0.08, 0.4, 0.02 ])
  plt.colorbar(shading2, cax=cbar_ax, orientation='horizontal')

def check():
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

  x,y=m(ncep_lons,ncep_lats)
  shading1 = m.contourf(x, y, ec_value, cmap='RdYlBu_r',  alpha=0.75, zorder=2)
  plt.title('ECMWF')
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
  shading2 = m.contourf(x, y, ncep_value, cmap='RdYlBu_r',  alpha=0.75, zorder=2)
  plt.title('NCEP')
  cbar_ax = fig.add_axes([0.55, 0.08, 0.4, 0.02 ])
  plt.colorbar(shading2, cax=cbar_ax, orientation='horizontal')

def ec2ncep_varname(parameterName,level):
  if parameterName == 'V velocity':
    parameterName = 'v-component of wind'
  if parameterName == 'U velocity':
    parameterName = 'u-component of wind'
  if parameterName == 'Gepotential Height':
    parameterName = 'Geopotential height'
  return parameterName,level

def ncep2ec_varname(parameterName,level):
  if parameterName == 'v-component of wind':
    parameterName = 'V velocity'
  if parameterName == 'u-component of wind':
    parameterName = 'U velocity'
  if parameterName == 'Geopotential height':
    parameterName = 'Gepotential Height'
  return parameterName,level

def merge(outfilename,ecgrib,ncepgrib):

  level_list=['850','200','500']
  vname_dict={'850':['u-component of wind','v-component of wind','Temperature','Relative humidity','Geopotential height'],
              '200':['u-component of wind','v-component of wind'],
              '500':['Geopotential height']}

  # open outfile
  grbout = open(outfilename,'wb')

  # loop over ncep grib2 messages
  for ncepgrb in ncepgrib.grbs:    
    # get level and parameterName in current message
    level = ncepgrb['level']
    parameterName = ncepgrb['parameterName']

    if str(level) in level_list:
      if parameterName in vname_dict[str(level)]:
        print(ncepgrb)
        # convert NCEP variable name to ECMWF
        parameterName,level = ncep2ec_varname(parameterName,level)
        # select field for ECMWF
        try:
          ecgrb = ecgrib.grbs.select(parameterName=parameterName,level=level)[0]
        except:
          print('Warning : No field was selected from ECMWF.')
          continue
        # reduce resolution from 0.1 to 0.5 degrees
        ec_value = ecgrb.values[0:ecgrib.lats.shape[0]:5,0:ecgrib.lons.shape[1]:5]
        # extract NCEP map with ECMWF domain area
        xi = 122 ; xe = 145 ;  yi = 232 ; ye = 255
        ncep_value = ncepgrb.values[xi:xe,yi:ye]
        ncep_full = ncepgrb.values
        # combine NCEP and ECMWF and put back to NCEP grib2
        ncep_full[xi:xe,yi:ye] = 0.5*(ncep_value + ec_value)
        ncepgrb['values'] = ncep_full
        # write out message 
        msg = ncepgrb.tostring()
        ret = grbout.write(msg)
      else:
        # write out message 
        msg = ncepgrb.tostring()
        ret = grbout.write(msg)
    else:
      # write out message 
      msg = ncepgrb.tostring()
      ret = grbout.write(msg)
  # close outfile
  grbout.close()

def plot(ecgrib,ncepgrib):
  #print(ecgrib.lats.max(),ecgrib.lats.min(),ecgrib.lats.shape)
  #print(ecgrib.lons.max(),ecgrib.lons.min(),ecgrib.lons.shape)
  #print(ncepgrib.lats.max(),ncepgrib.lats.min(),ncepgrib.lats.shape)
  #print(ncepgrib.lons.max(),ncepgrib.lons.min(),ncepgrib.lons.shape)
  
  #print(np.where(ncepgrib.lats == ecgrib.lats.max()))
  #print(np.where(ncepgrib.lats == ecgrib.lats.min()))
  #print(np.where(ncepgrib.lons == ecgrib.lons.max()))
  #print(np.where(ncepgrib.lons == ecgrib.lons.min()))
 
  ecgrib.grbs.rewind()
  #ecgrb = ecgrib.grbs.readline()
  
  for i,ecgrb in enumerate(ecgrib.grbs):
    parameterName,level = ec2ncep_varname(ecgrb.parameterName,ecgrb.level)
    # select field 
    try:
      ncepgrb = ncepgrib.grbs.select(parameterName=parameterName,level=level)[0]
    except:
      continue

    # reduce resolution from 0.1 to 0.5 degrees
    ec_value = ecgrb.values[0:ecgrib.lats.shape[0]:5,0:ecgrib.lons.shape[1]:5]  
    # extract NCEP map with ECMWF domain area
    xi = 122 ; xe = 145 ;  yi = 232 ; ye = 255 
    ncep_value = ncepgrb.values[xi:xe,yi:ye]
    # get NCEP grib2 latitude and logitude information
    ncep_lats,ncep_lons = ncepgrb.latlons()
    # extact lats and lons as well
    ncep_lats=ncep_lats[xi:xe,yi:ye]
    ncep_lons=ncep_lons[xi:xe,yi:ye]   
    print('%2.2d %s at %s hPa' % (i,ecgrb.parameterName,ecgrb.level) )
    # plot conbine
    mergeplot()
    plt.suptitle('%s  %s hPa' % (ecgrb.parameterName,ecgrb.level))
    plt.savefig('%s_%s.png' % (ecgrb.parameterName,ecgrb.level))


if __name__ == '__main__':
  if len(sys.argv) < 3: 
    sys.stdout.write("'ecncepgrib <ECMWF grib filename>' '<NCEP grib filename>'\n")
    sys.exit(1)
  else: 
    ecfile = sys.argv[1] 
    ncepfile = sys.argv[2] 

#  ecfile='ec0p1/C1D08070000080700001'
#  ncepfile='getAVN/18080700/gfs.pgrb2f00.18080700'
  ecgrib = Plotgrib(ecfile)
  ncepgrib = Plotgrib(ncepfile) 

  #plot(ecgrib,ncepgrib)
 
  merge(ncepfile+'.ecmwf',ecgrib,ncepgrib) 
