import numpy as np
import pandas as pd
from datetime import datetime
from gurobipy import *


df=pd.read_csv('teste.csv') #Cria Data Frame 
df=df.values                #Cria matriz apenas com os valores do df

#Arrays das concentrações de cada componente pelo horário
CO_GT=[]        #True hourly averaged concentration CO in mg/m^3 (reference analyzer)
CO_PT08=[]      #PT08.S1 (tin oxide) hourly averaged sensor response (nominally CO targeted)
NMHC_GT=[]      #True hourly averaged overall Non Metanic HydroCarbons concentration in microg/m^3 (reference analyzer)
C6H6_GT=[]      #True hourly averaged Benzene concentration in microg/m^3 (reference analyzer)
NMHC_PT08=[]    #PT08.S2 (titania) hourly averaged sensor response (nominally NMHC targeted)        
NOx_GT=[]       #True hourly averaged NOx concentration in ppb (reference analyzer)
NOx_PT08=[]     #PT08.S3 (tungsten oxide) hourly averaged sensor response (nominally NOx targeted)
NO2_GT=[]       #True hourly averaged NO2 concentration in microg/m^3 (reference analyzer)
NO2_PT08=[]     #PT08.S4 (tungsten oxide) hourly averaged sensor response (nominally NO2 targeted)
O3_PT08=[]      #PT08.S5 (indium oxide) hourly averaged sensor response (nominally O3 targeted)
T=[]            #Temperature in °C
RH=[]           #Relative Humidity (%)
AH=[]           #Absolute Humidity
Time=[]         #Time (HH.MM.SS)
Date=[]         #Date (DD/MM/YYYY)

t_c=[1,1,1,1]          #Toxicidade do componente c

def inicia():
    for i in range(len(df[:,:])):
        Date.append(df[i,0])
        Time.append(df[i,1])
        CO_GT.append(df[i,2].replace(',','.'))
        CO_PT08.append(df[i,3])
        NMHC_GT.append(df[i,4])
        C6H6_GT.append(df[i,5].replace(',','.'))
        NMHC_PT08.append(df[i,6])
        NOx_GT.append(df[i,7])
        NOx_PT08.append(df[i,8])
        NO2_GT.append(df[i,9])
        NO2_PT08.append(df[i,10])
        O3_PT08.append(df[i,11])
        T.append(df[i,12].replace(',','.'))
        RH.append(df[i,13].replace(',','.'))
        AH.append(df[i,14].replace(',','.'))
    
    for i in range(len(df[:,:])):
        CO_GT[i]=float(CO_GT[i])
        C6H6_GT[i]=float(C6H6_GT[i])
        T[i]=float(T[i])
        RH[i]=float(RH[i])
        AH[i]=float(AH[i])

def trataValor(vet): #Troca valores '-200'(valores faltantes) pela media da hora
    if vet.count(-200)!=0:
        for j in range(0,25): #Procura de Hora em Hora
            aux1=0 #aux para achar a média
            aux2=0
            vetAux=[]
            for i in range(0+j,len(vet),24): #pega valores de determinada HR
                vetAux.append(vet[i])
            for i in range(len(vetAux)): #pega apenas valores validos
                if vetAux[i]!=-200:
                    aux1=aux1+vetAux[i]
                    aux2=aux2+1
            for i in range(0+j,len(vet),24): #substitui média dos valores validos de uma hr no vet original
                if vet[i]==-200:
                    vet[i]=round(aux1/aux2,4)
            vetAux.clear()

def hora(a):    #transforma hr de str para int
    j=18
    for i in range(0,len(a)):
        if j<24:
            a[i]=j
            j=j+1
        else:
            j=0
            a[i]=j
            j=j+1

def data(a):
    for i in range(len(a)):
        a[i]=datetime.strptime(a[i],'%d/%m/%Y') 
        
       

inicia()

trataValor(CO_GT)
trataValor(CO_PT08)
trataValor(NMHC_GT)
trataValor(C6H6_GT)
trataValor(NMHC_PT08)    
trataValor(NOx_GT)
trataValor(NOx_PT08)
trataValor(NO2_GT)
trataValor(NO2_PT08)
trataValor(O3_PT08)
trataValor(T)
trataValor(RH)
trataValor(AH)
    
hora(Time)
data(Date)

Q_ch=np.zeros([4,len(CO_GT)]) # Quantidade do componente 'c' no horario 'h'
for i in range(len(CO_GT)):
    Q_ch[0][i]=CO_GT[i]
    Q_ch[1][i]=C6H6_GT[i]
    Q_ch[2][i]=NOx_GT[i]
    Q_ch[3][i]=NO2_GT[i]

lim_c=[] #limites de concentração saudáveis
lim_c.append(10)    #mg/m3
lim_c.append(5)     #microg/m3
lim_c.append(60)    #ppb
lim_c.append(100)   #microg/m3

def soma(a):
    b=0
    for i in range(9357):
        b+=a[i]
    return b
#Modelo
m=Model('Modelo')

#Variáveis
y={}
for h in range(9357):
    y[h]=m.addVar(vtype = GRB.BINARY)
m.update()

#Restrições
#r1=m.addConstr ((sum(y[h]) for h in range(9357))==1)
#r2=m.addConstr ((Q_ch[c][h]*y[h] <= lim_c[c]) for c in range(4) for h in range(9357)) # Quantidade do componente 'c' no horario 'h'
#r3=m.addConstr ((T[h] for h in T),GRB.LESS_EQUAL,25.0)    #Temperatura Máxima
#r4=m.addConstr (T[h] >= 20 for h in range(9357))    #Temperatura Mínima
#r5=m.addConstr (RH[h] >= 30 for h in range(9357))   #Humidade relativa do ar Mínima

m.addConstr ((sum(y[h]) for h in range(9357))==1)
for h in range(9357):
#    m.addConstr (T[h]*y[h]<=25,h)
#    m.addConstr (T[h]*y[h]>=20)
#    m.addConstr (RH[h]*y[h]>=30)
    for c in range(4):
        m.addConstr (Q_ch[c][h]*y[h] <= lim_c[c])

#Objetivo
m.setObjective(sum(sum(t_c[c]*Q_ch[c][h] for c in range(4))*y[h] for h in range(9357)),GRB.MINIMIZE)

    
#m.setObjective(((sum(sum(t_c[c]*Q_ch[c][h]))*y[h]) for c in range(4) for h in range(9357)),GRB.MINIMIZE)

m.optimize ()
























