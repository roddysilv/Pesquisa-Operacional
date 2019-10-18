import numpy as np
import pandas as pd
from datetime import datetime
from gurobipy import *


df=pd.read_csv('teste.csv')     #Cria Data Frame 
df=df.values                    #Cria matriz apenas com os valores do df

#Arrays das concentrações de cada componente pelo horário
CO=[]                           #True hourly averaged concentration CO in mg/m^3 (reference analyzer)
NMHC=[]                         #True hourly averaged overall Non Metanic HydroCarbons concentration in microg/m^3 (reference analyzer)
C6H6=[]                         #True hourly averaged Benzene concentration in microg/m^3 (reference analyzer)
NOx=[]                          #True hourly averaged NOx concentration in ppb (reference analyzer)
NO2=[]                          #True hourly averaged NO2 concentration in microg/m^3 (reference analyzer)
Temperatura=[]                  #Temperature in °C
Humidade_Relativa=[]            #Relative Humidity (%)
Humidade_Absoluta=[]            #Absolute Humidity
Hora=[]                         #Hora (HH.MM.SS)
Data=[]                         #Data (DD/MM/YYYY)

Toxicidade=[1,1,1,1]            #Toxicidade do componente c
Limite_Componente=[10,5,60,100] #limites de concentração saudáveis

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
        Humidade_Relativa.append(df[i,13].replace(',','.'))
        Humidade_Absoluta.append(df[i,14].replace(',','.'))
    
    for i in range(len(df[:,:])):
        CO[i]=float(CO[i])
        C6H6[i]=float(C6H6[i])
        Temperatura[i]=float(Temperatura[i])
        Humidade_Relativa[i]=float(Humidade_Relativa[i])
        Humidade_Absoluta[i]=float(Humidade_Absoluta[i])


#Troca valores '-200'(valores faltantes) pela media da hora
def trataValor(vet):
    if vet.count(-200)!=0:
        for j in range(0,25):               #Procura de Hora em Hora
            aux1=0                          #aux para achar a média
            aux2=0
            vetAux=[]
            for i in range(0+j,len(vet),24): #pega valores de determinada HR
                vetAux.append(vet[i])
            for i in range(len(vetAux)):    #pega apenas valores validos
                if vetAux[i]!=-200:
                    aux1=aux1+vetAux[i]
                    aux2=aux2+1
            for i in range(0+j,len(vet),24): #substitui média dos valores validos de uma hr no vet original
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

trataValor(CO)
trataValor(NMHC)
trataValor(C6H6)
trataValor(NOx)
trataValor(NO2)
trataValor(Temperatura)
trataValor(Humidade_Relativa)
trataValor(Humidade_Absoluta)
    
Quantidade_Componente_Hora=np.zeros([4,len(CO)]) # Quantidade do componente 'c' no horario 'h'
for i in range(len(CO)):
    Quantidade_Componente_Hora[0][i]=CO[i]
    Quantidade_Componente_Hora[1][i]=C6H6[i]
    Quantidade_Componente_Hora[2][i]=NOx[i]
    Quantidade_Componente_Hora[3][i]=NO2[i]


#SIMPLEX


#Modelo

m=Model('Modelo')


#Variáveis

y={}
#9357
for h in range(9357):
    y[h]=m.addVar(vtype = GRB.BINARY, name=str(h))

m.update()


#Restrições

#r1=m.addConstr ((sum(y[h]) for h in range(9357))==1)
#r2=m.addConstr ((Quantidade_Componente_Hora[c][h]*y[h] <= Limite_Componente[c]) for c in range(4) for h in range(9357)) # Quantidade do componente 'c' no horario 'h'
#r3=m.addConstr ((Temperatura[h] for h in Temperatura),GRB.LESS_EQUAL,25.0)    #Temperatura Máxima
#r4=m.addConstr (Temperatura[h] >= 20 for h in range(9357))    #Temperatura Mínima
#r5=m.addConstr (Humidade_Relativa[h] >= 30 for h in range(9357))   #Humidade relativa do ar Mínima

m.addConstr ((sum(y[h] for h in range(9357))) == 1, "c1")
for h in range(9357):
##    m.addConstr (Temperatura[h]*y[h]<=25,h)
##    m.addConstr (Temperatura[h]*y[h]>=20)
##    m.addConstr (Humidade_Relativa[h]*y[h]>=30)
    for c in range(4):
        m.addConstr (Quantidade_Componente_Hora[c][h]*y[h] <= Limite_Componente[c])


#Objetivo
m.setObjective(sum(sum(Toxicidade[c]*Quantidade_Componente_Hora[c][h] for c in range(4))*y[h] for h in range(9357)),GRB.MINIMIZE)
test = [4,3,2,1]
#m.setObjective(sum (test[h]*y[h] for h in range(4)),GRB.MINIMIZE)


m.optimize ()























