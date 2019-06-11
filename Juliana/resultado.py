import ast
import csv

matrix = [[0]*28 for x in range(2000,2017)]
porcentagem = [[0]*28 for x in range(2000,2017)]

for ano in range(2000,2017):
	dados = open('Resultado/CerradoMT'+str(ano)+'.txt').readlines()
	linha = dados[-1].replace('\n','')
	linha = linha[linha.index('{'):linha.index('}')+1]
	dic = ast.literal_eval(linha)
	a = ano - 2000
	matrix[a][0] = ano
	porcentagem[a][0] = ano
	soma = 0
	for k,v in dic.iteritems():
		if(k!=0):
			soma = soma + v
	for k,v in dic.iteritems():
		if(k!=0):
			matrix[a][int(k)] = v
			porcentagem[a][int(k)] = (v*100.0)/soma
		

with open("pixels.csv", "wb") as f:
    writer = csv.writer(f,delimiter=';')
    writer.writerow(['ano',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
    writer.writerows(matrix)

with open("porcentagem.csv", "wb") as f:
    writer = csv.writer(f,delimiter=';')
    writer.writerow(['ano',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
    writer.writerows(porcentagem)
    
def gerar(titulo):
	matrixReservas = [[0]*28 for x in range(2000,2017)]
	porcentagemReservas = [[0]*28 for x in range(2000,2017)]
	porcentagemReservasRelacaoCerrado = [[0]*28 for x in range(2000,2017)]

	for ano in range(2000,2017):
		dados = open('Resultado/Cerrado'+titulo+'MT'+str(ano)+'.txt').readlines()
		linha = dados[-1].replace('\n','')
		linha = linha[linha.index('{'):linha.index('}')+1]
		dic = ast.literal_eval(linha)
		a = ano - 2000
		matrixReservas[a][0] = ano
		porcentagemReservas[a][0] = ano
		porcentagemReservasRelacaoCerrado[a][0] = ano
		soma = 0
		for k,v in dic.iteritems():
			if(k!=0):
				soma = soma + v
		for k,v in dic.iteritems():
			if(k!=0):
				matrixReservas[a][int(k)] = v
				porcentagemReservas[a][int(k)] = (v*100.0)/soma
				print(a,k,matrix[a][int(k)],v)
				porcentagemReservasRelacaoCerrado[a][int(k)] = v/float(matrix[a][int(k)])*100.0
			

	with open("pixels"+titulo+".csv", "wb") as f:
		writer = csv.writer(f,delimiter=';')
		writer.writerow(['ano',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
		writer.writerows(matrixReservas)

	with open("porcentagem"+titulo+".csv", "wb") as f:
		writer = csv.writer(f,delimiter=';')
		writer.writerow(['ano',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
		writer.writerows(porcentagemReservas)
		
	with open("porcentagem"+titulo+"RelacaoCerrado.csv", "wb") as f:
		writer = csv.writer(f,delimiter=';')
		writer.writerow(['ano',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27])
		writer.writerows(porcentagemReservasRelacaoCerrado)


gerar('Reservas')

gerar('TerraIndigena')

gerar('UnidadeConservacao')

