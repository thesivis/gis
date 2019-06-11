import gdal, ogr, osr, numpy
import sys
from gdalconst import *
import csv


def calculo(x,y, cols, rows, band, grid):
	data = band.ReadAsArray(x, y, cols, rows).astype(numpy.float)
	unique_elements, counts_elements = numpy.unique(data, return_counts=True)
	
	media = 0.0
	soma = 0.0
	for i in xrange(len(unique_elements)):
		if(unique_elements[i] >= 0):
			media = media + unique_elements[i]*counts_elements[i]
			soma = soma + counts_elements[i]

	if(soma > 0):
		antes = media
		media = media / soma
		grid.append({"x":x,"y":y,"media":media})
		#print(unique_elements,'media2 = ', media,soma,antes)
		return media
	#print(unique_elements,'media = ', media)
	return ""
	
def calculoPastagem(x,y, cols, rows, band, grid):
	
	data = band.ReadAsArray(x, y, cols, rows).astype(numpy.float)
	unique_elements, counts_elements = numpy.unique(data, return_counts=True)
	
	media = 0.0
	soma = 0.0
	for i in xrange(len(unique_elements)):
		if(unique_elements[i] >= 0 and unique_elements[i] < 100):
			if(unique_elements[i] == 0):
				valor = 1.0
			else:
				valor = 0.0
			media = media + valor*counts_elements[i]
			soma = soma + counts_elements[i]
	
	if(soma > 0):
		media = media / soma
		grid.append({"x":x,"y":y,"media":media})
		
		return media
	return ""

adequabilidade= 'RASTERS_RAPHAEL/ADEQUABILIDADE ONCA1.tif'
adequabilidadeRaster = gdal.Open(adequabilidade)
adequabilidadeBand = adequabilidadeRaster.GetRasterBand(1)
adequabilidadeBandNoDataValue = adequabilidadeBand.GetNoDataValue()


pousadas = 'RASTERS_RAPHAEL/DENSIDADE POUSADAS1.tif'
pousadasRaster = gdal.Open(pousadas)
pousadasBand = pousadasRaster.GetRasterBand(1)
pousadasBandNoDataValue = pousadasBand.GetNoDataValue()


pastagem = 'RASTERS_RAPHAEL/PASTAGEM_INVERSO1.tif'
pastagemRaster = gdal.Open(pastagem)
pastagemBand = pastagemRaster.GetRasterBand(1)
pastagemBandNoDataValue = pastagemBand.GetNoDataValue()

print(adequabilidadeBandNoDataValue,pousadasBandNoDataValue,pastagemBandNoDataValue)


block_sizes = adequabilidadeBand.GetBlockSize()
x_block_size = block_sizes[0]
y_block_size = block_sizes[1]
xsize = adequabilidadeBand.XSize
ysize = adequabilidadeBand.YSize

x_block_size = 79
y_block_size = 79


print(xsize,ysize,x_block_size,y_block_size)

yInicial = 0
xInicial = 0

adequabilidadeGrid=[]
pousadasGrid=[]
pastagemGrid=[]
grid=[]


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
		#print(x,y,cols,rows,x_block_size, y_block_size)

		mediaAdequabilidade = calculo(x,y, cols, rows, adequabilidadeBand,adequabilidadeGrid)
		mediaPousada = calculo(x,y, cols, rows, pousadasBand, pousadasGrid)
		mediaPastagem = calculoPastagem(x,y, cols, rows, pastagemBand, pastagemGrid)
		if(mediaAdequabilidade != "" or mediaPastagem != "" or mediaPousada != ""):
			grid.append({"x":x,"y":y,"mediaAdequabilidade":mediaAdequabilidade,"mediaPousada":mediaPousada,"mediaPastagem":mediaPastagem})
			

with open('resultado/resultados.csv','w') as f:
	d = csv.DictWriter(f, grid[0].keys())
	d.writeheader()
	d.writerows(grid)

with open('resultado/adequabilidade.csv','w') as f:
	d = csv.DictWriter(f, adequabilidadeGrid[0].keys())
	d.writeheader()
	d.writerows(adequabilidadeGrid)
	
with open('resultado/pousadas.csv','w') as f:
	d = csv.DictWriter(f, pousadasGrid[0].keys())
	d.writeheader()
	d.writerows(pousadasGrid)
	
with open('resultado/pastagem.csv','w') as f:
	d = csv.DictWriter(f, pastagemGrid[0].keys())
	d.writeheader()
	d.writerows(pastagemGrid)
