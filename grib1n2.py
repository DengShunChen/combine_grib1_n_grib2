#!/usr/bin/env python
import pygrib
import numpy as np

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

if __name__ == '__main__':
  import os.path
  import sys
  if len(sys.argv) < 3 or len(sys.argv) > 4: 
    sys.stdout.write("'grib1n2 <ECMWF grib filename>' '<NCEP grib filename>' '<OUT grib filename>'\n")
    sys.exit(1)
  else: 
    if len(sys.argv) == 4:
      ecfile = sys.argv[1] 
      ncepfile = sys.argv[2] 
      outfile = sys.argv[3] 
    elif len(sys.argv) == 3:
      ecfile = sys.argv[1] 
      ncepfile = sys.argv[2] 
      outfile = os.path.basename(ncepfile) + '.ecmwf' 
    else:
      sys.stdout.write("'grib1n2 <ECMWF grib filename>' '<NCEP grib filename>' '<OUT grib filename>'\n")
      sys.exit(1)
      
#  ecfile='ec0p1/C1D08070000080700001'
#  ncepfile='getAVN/18080700/gfs.pgrb2f00.18080700'
  ecgrib = Plotgrib(ecfile)
  ncepgrib = Plotgrib(ncepfile) 
 
  print('ecmwfile : ',ecfile) 
  print('ncpefile : ',ncepfile) 
  print('outfile  : ',outfile) 
  merge(outfile,ecgrib,ncepgrib) 
