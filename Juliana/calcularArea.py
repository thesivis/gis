import gdal, ogr, osr, numpy
import sys
from gdalconst import *


def loop_zonal_stats(input_zone_polygon):

	shp = ogr.Open(input_zone_polygon)
	lyr = shp.GetLayer()
	featList = range(lyr.GetFeatureCount())

	tam = lyr.GetFeatureCount()
	lyrDefinition = lyr.GetLayerDefn()
	
	print(lyrDefinition.GetFieldCount())
	
	posicao = lyrDefinition.GetFieldCount() - 1
	for i in range(lyrDefinition.GetFieldCount()):
		print(lyrDefinition.GetFieldDefn(i).GetName())
		if(lyrDefinition.GetFieldDefn(i).GetName().lower()=='shape_area'):
			posicao = i
			break
	
	area = 0
	for FID in featList:
		feat = lyr.GetFeature(FID)
		print('Feature', FID,'de',tam,feat.GetField(lyrDefinition.GetFieldDefn(posicao).GetName()))
		area = area + float(feat.GetField(lyrDefinition.GetFieldDefn(posicao).GetName()))
	return area

def main(input_zone_polygon):
	return loop_zonal_stats(input_zone_polygon)


if __name__ == "__main__":


	#nomeArquivoEntradaSHP = sys.argv[1]
	nomeArquivoEntradaSHP = 'Pontos/CerradoPerimetro_UTM.shp'
	resultado = main(nomeArquivoEntradaSHP)
	print('Area:',resultado)
	
