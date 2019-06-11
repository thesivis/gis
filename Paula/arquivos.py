import os

diretorio = '/home/raphael/Paula/resultados'
arq = open('anos.txt','w')


for dirname, dirnames, filenames in os.walk(diretorio):
	for filename in filenames:
		if(filename.endswith('BTS.tif')):
			data=dirname.replace('/home/raphael/Paula/resultados/','').strip().split('/')[1]
			arq.write(data+'\n')
arq.close()
