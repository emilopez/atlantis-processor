import math 
import os
import sys
import glob
import subprocess
import random
 
# path to the GRASS GIS launch script
# MS Windows
grass7bin_win = r'C:\OSGeo4W\bin\grass70svn.bat'
# uncomment when using standalone WinGRASS installer
# grass7bin_win = r'C:\Program Files (x86)\GRASS GIS 7.0.0beta3\grass70.bat'
# Linux
grass7bin_lin = 'grass70'
# Mac OS X
# this is TODO
grass7bin_mac = '/Applications/GRASS/GRASS-7.0.app/'
 
# DATA
# define GRASS DATABASE
# add your path to grassdata (GRASS GIS database) directory
gisdb = os.path.join(os.path.expanduser("~"), "Escritorio/agrodatos")
#gisdb = "/home/daniel/grassdata"

# the following path is the default path on MS Windows
# gisdb = os.path.join(os.path.expanduser("~"), "Documents/grassdata")
 
# specify (existing) location and mapset
location = "land"
mapset   = "pre"
 
 
########### SOFTWARE
if sys.platform.startswith('linux'):
    # we assume that the GRASS GIS start script is available and in the PATH
    # query GRASS 7 itself for its GISBASE
    grass7bin = grass7bin_lin
elif sys.platform.startswith('win'):
    grass7bin = grass7bin_win
else:
    raise OSError('Platform not configured.')
                                                                                                            
# query GRASS 7 itself for its GISBASE
startcmd = [grass7bin, '--config', 'path']
 
gisbase = '/usr/lib/grass70'
 
# Set GISBASE environment variable
os.environ['GISBASE'] = gisbase
# the following not needed with trunk
os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
# add path to GRASS addons
home = os.path.expanduser("~")
os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')
 
# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)
 
########### DATA
# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb



# import GRASS Python bindings (see also pygrass)
import grass.script as grass
import grass.script.setup as gsetup
 
metaFile =''
dirName =''

if len(sys.argv) < 3:
	sys.exit('ERROR: ARGUMENT MISSING' )
else :
	dirName = sys.argv[1]
	outShape = sys.argv[2]
	if not os.path.exists(dirName):
		sys.exit('ERROR: Invalid')
	else:
		for file in os.listdir(dirName):
			if os.path.splitext(file)[-1] == '.txt':
				metaFile = file
				break
		if not metaFile:
			sys.exit('ERROR: Non metadata file in selected directory' )

###########
# launch session
gsetup.init(gisbase, gisdb, location, mapset)


def get_timestamp(mapset):
    try:
        metafile = glob.glob(mapset + '/*MTL.txt')[0]
    except IndexError:
        return
 
    result = dict()
    try:
        fd = open(metafile)
        for line in fd.readlines():
            line = line.rstrip('\n')
            if len(line) == 0:
                continue
            if any(x in line for x in ('DATE_ACQUIRED', 'ACQUISITION_DATE')):
                result['date'] = line.strip().split('=')[1].strip()
    finally:
        fd.close()
 
    return result
 
def import_tifs(mapset):
    meta = get_timestamp(mapset)
    for file in os.listdir(mapset):
        if os.path.splitext(file)[-1] != '.TIF':
            continue
        ffile = os.path.join(mapset, file)
        if ('VCID') in ffile:
            name = "".join((os.path.splitext(file)[0].split('_'))[1::2])
        else:
            name = os.path.splitext(file)[0].split('_')[-1]
        if len(name) == 3 and name[-1] == '0':
            band = int(name[1:2])
        elif len(name) == 3 and name[-1] != '0':
            band = int(name[1:3])
        else:
            band = int(name[-1:])
        grass.message('Importing %s -> %s@%s...' % (file, name, mapset))

        grass.run_command('r.in.gdal',
                          input = ffile,
                          output = name,
                          flags = 'oe', 
                          quiet = True,
                          overwrite = True,
                          title = 'band %d' % band)
        if meta:
            year, month, day = meta['date'].split('-')
            if month == '01':
                month = 'jan'
            elif month == '02':
                month = 'feb'
            elif month == '03':
                month = 'mar'
            elif month == '04':
                month = 'apr'
            elif month == '05':
                month = 'may'
            elif month == '06':
                month = 'jun'
            elif month == '07':
                month = 'jul'
            elif month == '08':
                month = 'aug'
            elif month == '09':
                month = 'sep'
            elif month == '10':
                month = 'oct'
            elif month == '11':
                month = 'nov'
            elif month == '12':
                month = 'dec'
 
            grass.run_command('r.timestamp',
                              map = name,
                              date = ' '.join((day, month, year)))



def main():
    if len(sys.argv) == 3:
		import_tifs(dirName)
		print metaFile
		print "entra a hacer de todo"
		grass.run_command("i.landsat.toar", input = "B", output= "B_TOAR_", metfile= dirName +"/"+ metaFile , overwrite=True)
		grass.run_command('r.mapcalc', overwrite=True, expression="mndwi=(B_TOAR_3 - B_TOAR_6)/(B_TOAR_3 + B_TOAR_6)")
		grass.run_command('r.mapcalc', overwrite=True, expression="nubes=if((B1>7000) && (B2>12000), 1, 0)")
		grass.run_command('r.mapcalc', overwrite=True, expression="umbral=if((mndwi>0.01) && (nubes==0),1,null())")

		grass.run_command('r.to.vect', input='umbral', output='umbral_vec', type ='area', overwrite=True)

		grass.run_command('v.out.ogr', input='umbral_vec', output=outShape, overwrite=True)

		#grass.run_command('r.mask', vect='cuerpos_agua_base', overwrite=True)

		#grass.run_command('r.mapcalc', overwrite=True, expression="resta=if(umbral=cuespos_agua_base,0,1)")
		#grass.run_command('r.mapcalc', overwrite=True, expression="final=if(umbral=1,mndwi,0)")


    else:
        import_tifs(sys.argv[1])
 
if __name__ == "__main__":
    main()