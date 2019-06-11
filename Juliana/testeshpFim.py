import gdal, ogr, osr, numpy
import sys
from gdalconst import *

def zonal_stats(feat, input_zone_polygon, input_value_raster):

	# Open data
	raster = gdal.Open(input_value_raster)
	shp = ogr.Open(input_zone_polygon)
	lyr = shp.GetLayer()

	# Get raster georeference info
	transform = raster.GetGeoTransform()
	xOrigin = transform[0]
	yOrigin = transform[3]
	pixelWidth = transform[1]
	pixelHeight = transform[5]

	# Reproject vector geometry to same projection as raster
	sourceSR = lyr.GetSpatialRef()
	targetSR = osr.SpatialReference()
	targetSR.ImportFromWkt(raster.GetProjectionRef())
	coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
#	feat = lyr.GetNextFeature()
	geom = feat.GetGeometryRef()
	geom.Transform(coordTrans)

	# Get extent of feat
	geom = feat.GetGeometryRef()
	#print(feat,geom.GetGeometryName())
	if (geom.GetGeometryName() == 'MULTIPOLYGON'):
		count = 0
		pointsX = []; pointsY = []
		for polygon in geom:
			geomInner = geom.GetGeometryRef(count)
			ring = geomInner.GetGeometryRef(0)
			numpoints = ring.GetPointCount()
			for p in range(numpoints):
					lon, lat, z = ring.GetPoint(p)
					pointsX.append(lon)
					pointsY.append(lat)
			count += 1
	elif (geom.GetGeometryName() == 'POLYGON'):
		ring = geom.GetGeometryRef(0)
		numpoints = ring.GetPointCount()
		pointsX = []; pointsY = []
		for p in range(numpoints):
				lon, lat, z = ring.GetPoint(p)
				pointsX.append(lon)
				pointsY.append(lat)

	else:
		sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

	xmin = min(pointsX)
	xmax = max(pointsX)
	ymin = min(pointsY)
	ymax = max(pointsY)

	# Specify offset and rows and columns to read
	xoff = int((xmin - xOrigin)/pixelWidth)
	yoff = int((yOrigin - ymax)/pixelWidth)
	xcount = int((xmax - xmin)/pixelWidth)+1
	ycount = int((ymax - ymin)/pixelWidth)+1
	
	# Create memory target raster
	target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
	target_ds.SetGeoTransform((
		xmin, pixelWidth, 0,
		ymax, 0, pixelHeight,
	))

	# Create for target raster the same projection as for the value raster
	raster_srs = osr.SpatialReference()
	raster_srs.ImportFromWkt(raster.GetProjectionRef())
	target_ds.SetProjection(raster_srs.ExportToWkt())

	# Rasterize zone polygon to raster
	gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

	# Read raster as arrays
	banddataraster = raster.GetRasterBand(1)
	
	'''if(xoff < 0):
		xcount = xcount + xoff
		xoff = 0
	if(yoff < 0):
		ycount = ycount + yoff
		yoff = 0
	'''
	bandmask = target_ds.GetRasterBand(1)
	
	block_sizes = bandmask.GetBlockSize()
	x_block_size = block_sizes[0]
	y_block_size = block_sizes[1]
	xsize = bandmask.XSize
	ysize = bandmask.YSize
	
	contagem = {}
	#print(xsize,ysize,x_block_size,y_block_size)
	
	yInicial = 0
	xInicial = 0
	if(yoff < 0):
		yInicial = yoff*(-1)
	if(xoff < 0):
		xInicial = xoff*(-1)
	

	for y in xrange(yInicial, ysize, y_block_size):
		if y + y_block_size < ysize:
			rows = y_block_size
		else:
			rows = ysize - y
		for x in xrange(xInicial, xsize, x_block_size):
			if x + x_block_size < xsize:
				cols = x_block_size
			else:
				cols = xsize - x
			#print(x,y,cols,rows,xoff, yoff, xcount, ycount)
			dataraster = banddataraster.ReadAsArray(x+xoff, y+yoff, cols, rows).astype(numpy.float)
			#print(x,y,cols,rows,dataraster)
			datamask = bandmask.ReadAsArray(x, y, cols, rows).astype(numpy.float)
			
			# Mask zone of raster
			zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))
			unique_elements, counts_elements = numpy.unique(zoneraster.compressed(), return_counts=True)
			
			for i in xrange(len(unique_elements)):
				if(unique_elements[i] not in contagem):
					contagem[unique_elements[i]] = 0
					
				contagem[unique_elements[i]] = contagem[unique_elements[i]] + counts_elements[i]
				
	#print(contagem)
	return contagem
	
	'''
	print(banddataraster,xoff, yoff,xcount,ycount)
	dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)

	bandmask = target_ds.GetRasterBand(1)
	datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)

	# Mask zone of raster
	zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))

	# Calculate statistics of zonal raster
	#print(zoneraster)
	unique_elements, counts_elements = numpy.unique(zoneraster.compressed(), return_counts=True)
	#print(unique_elements,counts_elements)
	return numpy.average(zoneraster),numpy.mean(zoneraster),numpy.median(zoneraster),numpy.std(zoneraster),numpy.var(zoneraster),zip(unique_elements,counts_elements)
	'''

def loop_zonal_stats(input_zone_polygon, input_value_raster):

	shp = ogr.Open(input_zone_polygon)
	lyr = shp.GetLayer()
	featList = range(lyr.GetFeatureCount())
	statDict = {}

	tam = lyr.GetFeatureCount()
	lyrDefinition = lyr.GetLayerDefn()
	for FID in featList:
		feat = lyr.GetFeature(FID)
		print('Feature', FID,'de',tam,feat.GetField(lyrDefinition.GetFieldDefn(0).GetName()))
		meanValue = zonal_stats(feat, input_zone_polygon, input_value_raster)
		statDict[FID] = meanValue
	return statDict

def main(input_zone_polygon, input_value_raster):
	return loop_zonal_stats(input_zone_polygon, input_value_raster)


if __name__ == "__main__":


	if(len(sys.argv) != 3):
		print("[ERROR] voce deve colocar o shapefile e ou arquivo tif")	

	nomeArquivoEntradaSHP = sys.argv[1]
	nomeArquivoEntrada = sys.argv[2]
	
	entrada = gdal.Open(nomeArquivoEntrada,GA_ReadOnly)
	if  entrada is None:
		print 'Erro ao abrir o arquivo: ' + nomeArquivoEntrada
		sys.exit(1)


	linhas = entrada.RasterYSize
	colunas = entrada.RasterXSize
	NBandas = entrada.RasterCount
	driverEntrada = entrada.GetDriver()
	projecao = entrada.GetProjection()

	print 'linhas:',linhas,' colunas:',colunas,'bandas:',NBandas,'driver:',driverEntrada.ShortName,nomeArquivoEntradaSHP,nomeArquivoEntrada
	
	resultado = main(nomeArquivoEntradaSHP,nomeArquivoEntrada)
	final = {}
	for k in resultado:
		meio = resultado[k]
		for c in meio:
			if(c not in final):
				final[c]=0
			final[c]=final[c]+meio[c]
			
	print(final,sum(final.values()))
