#!/bin/bash


gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  2 Imagens/CERRADO_2001.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  3 Imagens/CERRADO_2002.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  4 Imagens/CERRADO_2003.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  5 Imagens/CERRADO_2004.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  6 Imagens/CERRADO_2005.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  7 Imagens/CERRADO_2006.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  8 Imagens/CERRADO_2007.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  9 Imagens/CERRADO_2008.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  10 Imagens/CERRADO_2009.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  11 Imagens/CERRADO_2010.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  12 Imagens/CERRADO_2011.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  13 Imagens/CERRADO_2012.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  14 Imagens/CERRADO_2013.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  15 Imagens/CERRADO_2014.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  16 Imagens/CERRADO_2015.tif
gdal_translate -a_nodata 0 Imagens/CERRADO.tif -b  17 Imagens/CERRADO_2016.tif


mv Imagens/CERRADO.tif ImagensAntes/CERRADO.tif

./script.sh
