import numpy as np
import pandas as pd
from datetime import datetime
from gurobipy import *


df=pd.read_csv('instancias.csv')    #Cria Data Frame 
df=df.values                        #Cria matriz apenas com os valores do Data Frame

#Arrays das concentrações de cada componente pelo horário e outros dados, de acordo com a referência
CO=[]                               #Concentração horária média de CO em mg/m^3
NMHC=[]                             #Concentração horária média de Hidrocarbonetos não metanos em microg/m^3
C6H6=[]                             #Concentração horária média de Benzeno (C6H6) em microg/m^3
NOx=[]                              #Concentração horária média de NOx em ppb
NO2=[]                              #Concentração horária média de NO2 em microg/m^3
Temperatura=[]                      #Temperatura em °C
Umidade_Relativa=[]                 #Umidade Relativa (%)
Umidade_Absoluta=[]                 #Umidade Absoluta
Hora=[]                             #Hora (HH.MM.SS)
Data=[]                             #Data (DD/MM/YYYY)
    
Toxicidade=[3,2,1,1]                #Coeficiente de toxicidade dos componentes: [CO, C6H6, NOx, NO2]

def inicia():
    for i in range(len(df[:,:])):
        Data.append(df[i,0])
        Hora.append(df[i,1])
        CO.append(df[i,2].replace(',','.'))
        NMHC.append(df[i,4])
        C6H6.append(df[i,5].replace(',','.'))
        NOx.append(df[i,7])
        NO2.append(df[i,9])
        Temperatura.append(df[i,12].replace(',','.'))
        Umidade_Relativa.append(df[i,13].replace(',','.'))
        Umidade_Absoluta.append(df[i,14].replace(',','.'))
    
    for i in range(len(df[:,:])):
        CO[i]=float(CO[i])
        C6H6[i]=float(C6H6[i])
        Temperatura[i]=float(Temperatura[i])
        Umidade_Relativa[i]=float(Umidade_Relativa[i])
        Umidade_Absoluta[i]=float(Umidade_Absoluta[i])


#Troca valores '-200'(valores faltantes) pela media da hora
def trataValor(vet):
    if vet.count(-200)!=0:
        for j in range(0,25):                   #Procura de Hora em Hora
            aux1=0                              #aux para achar a média
            aux2=0
            vetAux=[]
            for i in range(0+j,len(vet),24):    #pega valores de determinada HR
                vetAux.append(vet[i])
            for i in range(len(vetAux)):        #pega apenas valores validos
                if vetAux[i]!=-200:
                    aux1=aux1+vetAux[i]
                    aux2=aux2+1
            for i in range(0+j,len(vet),24):    #substitui média dos valores validos de uma hr no vet original
                if vet[i]==-200:
                    vet[i]=round(aux1/aux2,4)
            vetAux.clear()


#transforma hr de str para int
def hora():
    j=18
    for i in range(0,len(Hora)):
        if j<24:
            Hora[i]=j
            j=j+1
        else:
            j=0
            Hora[i]=j
            j=j+1


#Transfora data de str para formato data no Python (Util para contar dias)
def data():     
    for i in range(len(Data)):
        Data[i]=datetime.strptime(Data[i],'%d/%m/%Y') 
        
       
inicia()

hora()
data()

#Substitui os "missing values" pela média das concentrações válidas naquele horário encontradas no conjunto de dados

trataValor(CO)
trataValor(C6H6)
trataValor(NOx)
trataValor(NO2)
trataValor(Umidade_Relativa)

#Armazena as concentrações horárias de cada componente c em Quantidade_Componente_Hora

Quantidade_Componente_Hora=np.zeros([4,len(CO)]) #Quantidade do componente 'c' no horario 'h'
for i in range(len(CO)):
    Quantidade_Componente_Hora[0][i]=CO[i]
    Quantidade_Componente_Hora[1][i]=C6H6[i]
    Quantidade_Componente_Hora[2][i]=NOx[i]
    Quantidade_Componente_Hora[3][i]=NO2[i]

#Armazena as concentrações horárias semanais de cada componente c em Quantidade_Componente_Semana_Hora

Quantidade_Componente_Semana_Hora=np.zeros([6,55,168])
aux=78  # Data[78] é o primeiro domingo da base de dados
for s in range(55):
    for h in range(168):
        Quantidade_Componente_Semana_Hora[0][s][h]=CO[aux]
        Quantidade_Componente_Semana_Hora[1][s][h]=C6H6[aux]
        Quantidade_Componente_Semana_Hora[2][s][h]=NOx[aux]
        Quantidade_Componente_Semana_Hora[3][s][h]=NO2[aux]
        Quantidade_Componente_Semana_Hora[4][s][h]=Umidade_Relativa[aux]
        aux+=1


#Dados relevantes sobre a elaboração das restrições do modelo e suas constantes

    # total de dados: 9357
    # índice do primeiro domingo às 0h: 78
    # índice do último sabado às 23h: 9317
    # total de semanas: 55
    # semana tem 168 horas
    # 78+168 = 246


#Modelo


m=Model('Modelo')


#Variáveis

y = {} # vetor com as horas possiveis - representa a variável do modelo
x = {}

for h in range(168):
    y[h] = m.addVar(vtype = GRB.BINARY, name = str(h))

#for h in range(23):
#    x[h] = m.addVar(vtype = GRB.BINARY, name = str(h)+"x")


maximoPorDia = 2
TotalDeHoras = 10

m.update()


#Restrições

m.addConstr ((sum(y[h] for h in range(168))) == TotalDeHoras, "c1")    #Garante que apenas um horário será selecionado (restrição binária)

#m.addConstr ((sum(x[h] for h in range (23))) == 2, "c2")


m.addConstrs((Hora[78+h]*y[h] >= 8*y[h] for h in range(168)), name='c')
m.addConstrs((Hora[78+h]*y[h] <= 20 for h in range(168)), name='d')

#m.addConstrs (((Quantidade_Componente_Semana_Hora[4][s][h]*y[h] >= 30*y[h]) for h in range(168) for s in range (55)),name="h" )


#m.addConstr (sum(Hora[78+h]*y[h] for h in range(168))>=8) #garante que o horário analisado pertence a um intervalo útil do dia

#for h in range(168):
#    m.addConstr ( Hora[78+h]*y[h] <= 20, "h1"+str(h) )  #Garante que o horário analisado pertence a um intervalo útil do dia
      #Garante que o horário analisado pertence a um intervalo útil do dia
#    for s in range (55):
#        m.addConstr ( Quantidade_Componente_Semana_Hora[4][s][h]*y[h] >=30*y[h],"h3"+str(h)+str(s) )  #Garante que a umidade relativa do ar está acima de 30%

m.addConstrs(sum(y[(i*24)+h] for h in range(23)) <= maximoPorDia for i in range(7))


#for i in range(7):
#    for h in range(23):
#        print((i*24)+h)


#Objetivo

m.setObjective(sum(sum(sum(Toxicidade[c]*Quantidade_Componente_Semana_Hora[c][s][h] for c in range(4))*y[h] for h in range(168))for s in range(55)),GRB.MINIMIZE)


#Execução e impressão do resultado

m.optimize ()

try:
    for v in m.getVars():
        if(v.x==1):
            print("Resultado = "+str(Hora[int(v.varName)+78])+"h   "+Data[int(v.varName)+78].strftime("%A"))
except:
    print ("")