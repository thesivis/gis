#!/bin/bash


#python testeshpFim.py MT/EstadoMT_UTM_Reprojetado.shp Imagens/CERRADO_2000.tif > CerradoEstadoMT2000.txt
#python testeshpFim.py ReservaLegal/Reservas_legais_MT_Reprojetado.shp Imagens/CERRADO_2016.tif > CerradoReservasMT2016.txt
#python testeshpFim.py ReservaLegal/Reservas_legais_MT_Reprojetado.shp Imagens/CERRADO_2000.tif > CerradoReservasMT2000.txt


#for entry in "Imagens"/*
#do
#  ano=${entry:16:4}
#  echo "python testeshpFim.py MT/EstadoMT_UTM_Reprojetado.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoMT$ano.txt"
#  python testeshpFim.py MT/EstadoMT_UTM_Reprojetado.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoMT$ano.txt
#done

FILES=/home/raphael/Juliana/Imagens/*

for entry in $FILES
do

  ano=${entry:38:4}
  #echo "python /home/raphael/Juliana/testeshpFim.py MT/EstadoMT_UTM_Reprojetado.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoMT$ano.txt" 
  #python /home/raphael/Juliana/testeshpFim.py /home/raphael/Juliana/MT/EstadoMT_UTM_Reprojetado.shp /home/raphael/Juliana/Imagens/CERRADO_$ano.tif > /home/raphael/Juliana/Resultado/CerradoMT$ano.txt

  #echo "python /home/raphael/Juliana/testeshpFim.py Shape_CERRADO/Cerrado_RL.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoReservasMT$ano.txt" 
  #python /home/raphael/Juliana/testeshpFim.py /home/raphael/Juliana/Shape_CERRADO/Cerrado_RL.shp /home/raphael/Juliana/Imagens/CERRADO_$ano.tif > /home/raphael/Juliana/Resultado/CerradoReservasMT$ano.txt

  #echo "python /home/raphael/Juliana/testeshpFim.py Shape_CERRADO/TI_Cerrado.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoReservasMT$ano.txt" 
  #python /home/raphael/Juliana/testeshpFim.py /home/raphael/Juliana/Shape_CERRADO/TI_Cerrado.shp /home/raphael/Juliana/Imagens/CERRADO_$ano.tif > /home/raphael/Juliana/Resultado/CerradoTerraIndigenaMT$ano.txt

  #echo "python /home/raphael/Juliana/testeshpFim.py Shape_CERRADO/UC_Cerrado.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoReservasMT$ano.txt" 
  #python /home/raphael/Juliana/testeshpFim.py /home/raphael/Juliana/Shape_CERRADO/UC_Cerrado.shp /home/raphael/Juliana/Imagens/CERRADO_$ano.tif > /home/raphael/Juliana/Resultado/CerradoUnidadeConservacaoMT$ano.txt


  echo "python /home/raphael/Juliana/calculaCadaFeicao.py Pontos/Buffer120.shp Imagens/CERRADO_$ano.tif > Resultado/CerradoBufferMT$ano.txt" 
  python /home/raphael/Juliana/calculaCadaFeicao.py /home/raphael/Juliana/Pontos/Buffer120.shp /home/raphael/Juliana/Imagens/CERRADO_$ano.tif > /home/raphael/Juliana/Resultado/CerradoBufferMT$ano.txt

  #mv /home/raphael/Juliana/Imagens/CERRADO_$ano.tif /home/raphael/Juliana/ImagensAntes/CERRADO_$ano.tif
done


