import pandas as pd

df=pd.read_csv('teste.csv') #Cria Data Frame 
df=df.values                #Cria matriz apenas com os valores do df

#Arrays das concentrações de cada componente pelo horário
CO_GT=[]
CO_PT08=[]
NMHC_GT=[]
C6H6_GT=[]
NMHC_PT08=[]
NOx_GT=[]
NOx_PT08=[]
NO2_GT=[]
NO2_PT08=[]
O3_PT08=[]
T=[]
RH=[]
AH=[]

Time=[]
Date=[]

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


Dt = [(Date[i], Time[i]) for i in range(0, len(Date))] #Tupla de Data e Tempo

#Variáveis
y_h=[]  #Variável que representa o horário selecionado [0,1]
q_ch=[] #Quantidade do componente 'c' no horário 'h'
t_c=[]  #Toxicidade do componente 'c'

X_c=[]  #Valor máximodo componente 'c' em td período
W_h=[]  #Começo do intervalo selecionado no horário 'h'
Y_hd=[] #Horário 'h' do dia 'd'

D=2     #Constante que representa a duração do intervalo