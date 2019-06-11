import numpy as np
from osgeo import gdal
from osgeo import ogr
import os, sys, struct
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from qgis.core import *
from numpy import zeros
from numpy import logical_and
import traceback
import os
import patoolib.programs.rar

#The imports below are done to enable the code in different directories to work in PyQGis
import sys
sys.path.append('~/Scripts/python')

def calcTMRadiance(thermalBand, outputPath, fileType, metadata):
        try:
            #The code below opens the datasets
            dsThermalBand = gdal.Open(thermalBand, gdal.GA_ReadOnly)
        except IOError, e:
            print(e)
        try:
            #Capture the Red and the NIR bands
            thermalBand = dsThermalBand.GetRasterBand(1)
                
            # get number of rows and columns in the Red and NIR bands
            cols = dsThermalBand.RasterXSize
            rows = dsThermalBand.RasterYSize
            #Read the metadata from the metadata file
            QCALMAX       = float(metadata['QCALMAX'])
            QCALMIN       = float(metadata['QCALMIN'])
            LMAX          = float(metadata['LMAX'])
            LMIN          = float(metadata['LMIN'])           
            # create the output image
            driver = gdal.GetDriverByName(fileType)
            radianceDS = driver.Create(outputPath, cols, rows, 1, gdal.GDT_Float32)
            radianceDS.SetGeoTransform(dsThermalBand.GetGeoTransform())
            radianceDS.SetProjection(dsThermalBand.GetProjection())
            radianceBand = radianceDS.GetRasterBand(1)
            
            #Read the block sizes of the thermal band being processed
            blockSizes = radianceBand.GetBlockSize()
            xBlockSize = blockSizes[0]
            yBlockSize = blockSizes[1]
                    
            # loop through rows of blocks
            for i in range(0, rows, yBlockSize):
                if i + yBlockSize < rows:
                    numRows = yBlockSize
                else:
                    numRows = rows - i
                
                # now loop through the blocks in the row
                for j in range(0, cols, xBlockSize):
                    if j + xBlockSize < cols:
                        numCols = xBlockSize
                    else:
                        numCols = cols - j
                    #If the band selected is TIRS band 11
                    thermalBandData = thermalBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                    # do the calculation
                    m = ((LMAX - LMIN) / (QCALMAX - QCALMIN))
                    x = np.subtract(thermalBandData, QCALMIN)
                    radiance = np.multiply(m, x)
                    radiance = np.add(radiance, LMIN)
                    # write the data
                    radianceDS.GetRasterBand(1).WriteArray(radiance,j,i)
            
            # set the histogram
            radianceDS.GetRasterBand(1).SetNoDataValue(-99)
            histogram = radianceDS.GetRasterBand(1).GetDefaultHistogram()
            radianceDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])

            radianceDS    = None
            dsThermalBand = None
                
        except RuntimeError, e:
            print(e)

def planckEquation(bt, lse, outputPath, unit, rasterType):
        try:
            #The code below opens the datasets
            dsBT  = gdal.Open(bt, gdal.GA_ReadOnly)
            dsLSE = gdal.Open(lse, gdal.GA_ReadOnly)
        except IOError, e:
            print(e)
        try:
            #Set the wavelengths of the emitted radiances according to the sensor selected

            wl = 11.45
            
            #Capture the LSE and the Brightness Temperature bands
            btBand = dsBT.GetRasterBand(1)
            lseBand = dsLSE.GetRasterBand(1)
                    
            # get numbers of rows and columns in the Red and NIR bands
            colsBT = dsBT.RasterXSize
            rowsBT = dsBT.RasterYSize
                
            colsLSE = dsLSE.RasterXSize
            rowsLSE = dsLSE.RasterYSize
                
            # create the output image
            driver = gdal.GetDriverByName(rasterType)
            lstDS = driver.Create(outputPath, colsBT, rowsBT, 1, gdal.GDT_Float32)
            lstDS.SetGeoTransform(dsBT.GetGeoTransform())
            lstDS.SetProjection(dsBT.GetProjection())
            lstBand = lstDS.GetRasterBand(1)

                    
            # loop through rows of blocks
            blockSize = 64
            for i in range(0, rowsBT, blockSize):
                if i + blockSize < rowsBT:
                    numRows = blockSize
                else:
                    numRows = rowsBT - i
                
                # now loop through the blocks in the row
                for j in range(0, colsBT, blockSize):
                    if j + blockSize < colsBT:
                        numCols = blockSize
                    else:
                        numCols = colsBT - j
                        
                    # get the data
                    lseData = lseBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                    btData  = btBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                
                    # do the calculation
                    cond_list   = [lseData > 0, lseData <= 0]
                    choice_list = [np.log(lseData), 0]
                    log_lse     = np.select(cond_list, choice_list)
                    lst_upper   = btData
                    lst_lower   = np.divide(btData, 14380)
                    lst_lower   = np.multiply(lst_lower, wl)
                    lst_lower   = np.multiply(lst_lower, log_lse)
                    lst_lower   = np.add(lst_lower, 1)
                    
                    #Convert the temperature according to the unit selected
                    if (unit == 'Kelvin'):
                        lst = np.divide(lst_upper, lst_lower)
                    elif (unit == 'Celsius'):
                        #Celsius = Kelvin - 273.15
                        lst = np.divide(lst_upper, lst_lower)
                        lst = np.subtract(lst, 273.15)
                    else:
                        #Fahrenheit = ((kelvin - 273.15) x 1.8) + 32
                        lst = np.divide(lst_upper, lst_lower)
                        lst = np.subtract(lst, 273.15)
                        lst = np.multiply(lst, 1.8)
                        lst = np.add(lst, 32)
                    # write the data
                    lstDS.GetRasterBand(1).WriteArray(lst, j, i)
                    

            # set the histogram
            lstDS.GetRasterBand(1).SetNoDataValue(-99)
            histogram = lstDS.GetRasterBand(1).GetDefaultHistogram()
            lstDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])
                
            lstDS    = None
            lseBand  = None
            btBand   = None

                
        except RuntimeError, e:
            print(e)

def calcNDVI(redBandPath, NIRBandPath, outputPath, rasterType):
        try:
            #The code below opens the datasets
            dsRedBand = gdal.Open(redBandPath, gdal.GA_ReadOnly)
            dsNIRBand = gdal.Open(NIRBandPath, gdal.GA_ReadOnly)

        except IOError, e:
            print(e)
        try:
            #Capture the Red and the NIR bands
            redBand = dsRedBand.GetRasterBand(1)
            NIRBand = dsNIRBand.GetRasterBand(1)

            # get numbers of rows and columns in the Red and NIR bands
            colsRed = dsRedBand.RasterXSize
            rowsRed = dsRedBand.RasterYSize

            # create the output image
            driver = gdal.GetDriverByName(rasterType)
            ndviDS = driver.Create(outputPath, colsRed, rowsRed, 1, gdal.GDT_Float32)
            ndviDS.SetGeoTransform(dsRedBand.GetGeoTransform())
            ndviDS.SetProjection(dsRedBand.GetProjection())
            ndviBand = ndviDS.GetRasterBand(1)
                
            # loop through rows of blocks
            blockSize = 64
            for i in range(0, rowsRed, blockSize):
                if i + blockSize < rowsRed:
                    numRows = blockSize
                else:
                    numRows = rowsRed - i

                # now loop through the blocks in the row
                for j in range(0, colsRed, blockSize):
                    if j + blockSize < colsRed:
                        numCols = blockSize
                    else:
                        numCols = colsRed - j
                    # get the data
                    redBandData = redBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                    NIRBandData = NIRBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                    # do the calculation
                    mask = np.greater(redBandData + NIRBandData, 0)
                    ndvi = np.choose(mask, (-99, (NIRBandData - redBandData) / (NIRBandData + redBandData)))
                    # write the data
                    ndviDS.GetRasterBand(1).WriteArray(ndvi, j, i)
            
            # set the histogram
            ndviDS.GetRasterBand(1).SetNoDataValue(-99)
            histogram = ndviDS.GetRasterBand(1).GetDefaultHistogram()
            ndviDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])

            ndviDS   = None
            redBand  = None
            NIRBand  = None
                    
        except RuntimeError, e:
            print(e)

def calcBrightnessTemp(radiance, outputPath, fileType):
        try:
            #The code below opens the datasets
            dsRadianceBand = gdal.Open(radiance, gdal.GA_ReadOnly)
        except IOError, e:
            print(e)
        try:
            radianceBand = dsRadianceBand.GetRasterBand(1)
                
            # get numbers of rows and columns in the Red and NIR bands
            cols = dsRadianceBand.RasterXSize
            rows = dsRadianceBand.RasterYSize

            K1 = 607.76
            K2 = 1260.56
                
            # Create the output image
            driver = gdal.GetDriverByName(fileType)
            brightnessDS = driver.Create(outputPath, cols, rows, 1, gdal.GDT_Float32)
            brightnessDS.SetGeoTransform(dsRadianceBand.GetGeoTransform())
            brightnessDS.SetProjection(dsRadianceBand.GetProjection())
            brightnessBand = brightnessDS.GetRasterBand(1)
            
            #Read the block sizes of the thermal band being processed
            blockSizes = brightnessBand.GetBlockSize()
            xBlockSize = blockSizes[0]
            yBlockSize = blockSizes[1]
                    
            # loop through rows of blocks
            for i in range(0, rows, yBlockSize):
                if i + yBlockSize < rows:
                    numRows = yBlockSize
                else:
                    numRows = rows - i
                
                # now loop through the blocks in the row
                for j in range(0, cols, xBlockSize):
                    if j + xBlockSize < cols:
                        numCols = xBlockSize
                    else:
                        numCols = cols - j
                        
                    radianceBandData = radianceBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                    # do the calculation
                    bt_upper = K2
                    bt_lower = np.divide(K1, radianceBandData)
                    bt_lower = np.add(bt_lower, 1)
                    bt_lower = np.log(bt_lower)
                    bt = np.divide(bt_upper, bt_lower)

                    # write the data
                    brightnessDS.GetRasterBand(1).WriteArray(bt,j,i)
      
            # set the histogram
            brightnessDS.GetRasterBand(1).SetNoDataValue(-99)
            histogram = brightnessDS.GetRasterBand(1).GetDefaultHistogram()
            brightnessDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])

            brightnessDS    = None
            dsRadianceBand  = None
                
        except RuntimeError, e:
            print(e)

def zhangLSEalgorithm(ndviRaster, outputPath, rasterType):
        try:
            #The code below opens the datasets
            dsNdviBand = gdal.Open(ndviRaster, gdal.GA_ReadOnly)
        except IOError, e:
            print(e)
            
        try:
            
            #Capture the Red and the NIR bands
            ndviBand = dsNdviBand.GetRasterBand(1)
                    
            # get number of rows and columns in the Red and NIR bands
            cols = dsNdviBand.RasterXSize
            rows = dsNdviBand.RasterYSize
                
            # create the output image
            driver = gdal.GetDriverByName(rasterType)
            lseDS = driver.Create(outputPath, cols, rows, 1, gdal.GDT_Float32)
            lseDS.SetGeoTransform(dsNdviBand.GetGeoTransform())
            lseDS.SetProjection(dsNdviBand.GetProjection())
            radianceBand = lseDS.GetRasterBand(1)
            
            #Read the block sizes of the thermal band being processed
            blockSizes = radianceBand.GetBlockSize()
            xBlockSize = blockSizes[0]
            yBlockSize = blockSizes[1]
                        
            # loop through rows of blocks
            for i in range(0, rows, yBlockSize):
                if i + yBlockSize < rows:
                    numRows = yBlockSize
                else:
                    numRows = rows - i
                    
                # now loop through the blocks in the row
                for j in range(0, cols, xBlockSize):
                    if j + xBlockSize < cols:
                        numCols = xBlockSize
                    else:
                        numCols = cols - j
                    # get the data
                    ndviData  = ndviBand.ReadAsArray(j, i, numCols, numRows).astype('f')
                    #Do the calculation here
                    conditionList = [np.logical_and(ndviData < -0.185, ndviData >= -1), np.logical_and(ndviData >= -0.185, ndviData <= 0.157), np.logical_and(ndviData >= 0.157, ndviData <= 0.727), np.logical_and(ndviData > 0.727, ndviData <= 1)]
                    mixedPixels   = np.log(ndviData)
                    mixedPixels   = np.multiply(mixedPixels, 0.047)
                    mixedPixels   = np.add(mixedPixels, 1.009)
                    choiceList    = [0.995, 0.985, mixedPixels, 0.990]
                    lse           = np.select(conditionList, choiceList)
                    
                    # write the data
                    lseDS.GetRasterBand(1).WriteArray(lse, j, i)
            
            # set the histogram
            lseDS.GetRasterBand(1).SetNoDataValue(-99)
            histogram = lseDS.GetRasterBand(1).GetDefaultHistogram()
            lseDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])
    
            lseDS      = None
            dsNdviBand = None
            
        except RuntimeError, e:
            print(e)


diretorio = '/home/raphael/Paula/imagens'

anos = range(1990,1991)
'''
for dirname, dirnames, filenames in os.walk(diretorio):
	tem = False
	for ano in anos:
		if(str(ano) in dirname):
			tem = True
	if(not tem):
		for filename in filenames:
			if(filename.endswith('tar.gz')):
				print(dirname+'/'+filename)
				patoolib.extract_archive(dirname+'/'+filename,outdir=dirname)

exit(1)
'''

for dirname, dirnames, filenames in os.walk(diretorio):
	tem = False
	#for ano in anos:
	#	if(str(ano) in dirname):
	#		tem = True
	if(not tem):
		for filename in filenames:
			if(filename.endswith('B3.TIF')):
				thermalBand=''
				redBandPath=''
				NIRBandPath=''
				
				base = filename.replace('3.TIF','')
				
				redBandPath=dirname+'/'+filename.replace('.zip','')
				if(not os.path.exists(redBandPath)):
					redBandPath=''
			
				thermalBand = dirname+'/'+base+'6.TIF'
				if(not os.path.exists(thermalBand)):
					thermalBand=''
					
				NIRBandPath = dirname+'/'+base+'4.TIF'
				if(not os.path.exists(NIRBandPath)):
					NIRBandPath=''
					
				if(thermalBand!='' and redBandPath != '' and NIRBandPath!= ''):
					try:
						print(thermalBand)
						dirname2=dirname.replace('/imagens/','/resultados/')
						base = dirname2 + '/' + base
						
						planckPath=base+'TS.tif'
						if(not os.path.exists(planckPath)):
							#print(base,dirname2)
							if(not os.path.exists(dirname2)):
								os.makedirs(dirname2)
							metadata={'QCALMAX':255,'QCALMIN':0,'LMAX':15.303,'LMIN':1.2378}
							radiancePath=base+'Radiance.tif'
							#print(radiancePath)
							fileType = 'GTiff'

							calcTMRadiance(thermalBand,radiancePath,fileType,metadata)

							ndviPath=base+'NDVI.tif'

							calcNDVI(redBandPath,NIRBandPath,ndviPath,fileType)

							BrightnessTempPath = base+'BT.tif'
							calcBrightnessTemp(radiancePath, BrightnessTempPath, fileType)

							zhangLSEPath = base+'zhangLSE.tif'
							zhangLSEalgorithm(ndviPath, zhangLSEPath, fileType)

							unit = 'Celsius'
							bt=''
							lse=''
							
							planckEquation(BrightnessTempPath, zhangLSEPath, planckPath, unit, fileType)
							#exit(1)
					except Exception as inst:
						print("Erro:"+thermalBand)
						print(inst)
						print(inst.args)
						print(sys.exc_info()[0])
						#exit(1)
