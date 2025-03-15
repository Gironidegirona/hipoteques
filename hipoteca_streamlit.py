import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
sns.set_theme()

# Set page to wide mode (optional)
st.set_page_config(layout="wide")

# Inject custom CSS to force desktop-like layout on mobile
st.markdown("""
    <style>
    @media (max-width: 768px) {
        body {
            zoom: 0.8 !important;  /* Adjust zoom to make it look like a desktop */
            overflow-x: scroll !important; /* Enable horizontal scrolling */
        }
    }
    </style>
    """, unsafe_allow_html=True)


# Mobile-friendly settings
#st.set_page_config(layout="centered")

pc_notari = 0.015
pc_impostos = 0.1

def calculateAtMaxEstalvis(souMensual_1, souMensual_2, estalvis0, interesrate, anys, altresIngressos=0, altresCredits=0,pcentrada=20, stressTarget=35):
    
    stress_ = 100
    vivenda_ = 0
    cuotamensual_ = 0

    error = 100
    pcentradamax = 1
    pcentradamin = 0.2
    
    ii = 0
    while error > 0.1:
        pcentrada_ = 0.5*(pcentradamax + pcentradamin)
        souMensual = (souMensual_1 + souMensual_2)
        

        vivenda_ =  estalvis0/(pc_impostos +  pcentrada_ + pc_notari)

        entrada_, impostos_, notaris_ = despeses(vivenda_, pcentrada = pcentrada_) 

        cuotamensual_ = round(calculateCuota(vivenda_-entrada_, interesrate, anys = anys),1)
        estalvisnecessaris_ = round(entrada_+impostos_+notaris_,1)

        stress_ = round((altresCredits+cuotamensual_)*100/(souMensual+altresIngressos),1)
  
        if stress_ > stressTarget:
            pcentradamin = pcentrada_
                
        if stress_ < stressTarget:
            pcentradamax = pcentrada_
        
        error = abs(stress_-stressTarget)
        #print(estalvis0, vivenda_, pcentrada_, pcentradamax, pcentradamin, stress_)
                

        ii+=1

        if ii > 10:
            break

    
    return vivenda_, entrada_, estalvisnecessaris_, cuotamensual_

def calculateAtMaxStress(souMensual_1, souMensual_2, estalvis0, interesrate, anys, altresIngressos=0, altresCredits=0,pcentrada=20, stressTarget=35):
    vivendamin, vivendamax = 0, 6000
    stress_ = 100
    vivenda_ = 0
    cuotamensual_ = 0

    ii = 0
    while abs(stress_-stressTarget)>0.025:
        souMensual = (souMensual_1 + souMensual_2)
            
        vivenda_ = 0.5*(vivendamin+vivendamax)
        entrada_, impostos_, notaris_ = despeses(vivenda_, pcentrada = pcentrada/100.) 
        
        
        cuotamensual_ = round(calculateCuota(vivenda_-entrada_, interesrate, anys = anys),1)
        estalvisnecessaris_ = round(entrada_+impostos_+notaris_,1)

        stress_ = round((altresCredits+cuotamensual_)*100/(souMensual+altresIngressos),1)
    
        if stress_ > stressTarget:
            vivendamax = vivenda_
                    
        if stress_ < stressTarget:
            vivendamin = vivenda_
      
        ii+=1
        if ii>10:
            break
            
                


    return vivenda_, entrada_, estalvisnecessaris_, cuotamensual_
    
def calculateCuota(c0, rate, anys = 30):
    ratem = rate/1200
    cuota = round((c0*(ratem*(1+ratem)**(anys*12))/((1+ratem)**(12*anys)-1))*1000,1)

    return cuota

def despeses(vivenda, pcentrada = 0.2, pc_notari = 0.015, pc_impostos = 0.1):
    entrada = vivenda*pcentrada
    impostos = vivenda*pc_impostos
    notaris = vivenda*pc_notari

    return entrada, impostos, notaris

def calculateStress(cuota):
    percentatgeHipotecaSou = 0.25
    impostos = 0.27
    minSalaries = cuota/percentatgeHipotecaSou
    minSalaries = round((minSalaries/2*12)/(1-impostos)/1000,1)

    return minSalaries

def pivot_dataframe(df, row = 'A', columns = 'B', values = 'C'):
    # Pivot the DataFrame with column A as the index, B as columns, and C as values
    new_df = df.pivot(index=row, columns=columns, values=values)
    return new_df

def calculateRangesEntrada(casa0, rate0, entradapc0):
    dades = {'casa':[], 'entrada':[], 'interes':[],'cuota':[], 'entradapc':[]}
    rates = np.arange(rate0-0.35,rate0+0.35,0.05)

    for rate in rates:
        for casa in [casa0]:#np.arange(casa0-75,casa0,5):
            for entradapc in np.arange(0.9,0.6,-0.025):
                entrada, impostos, notaris = despeses(casa, pcentrada = 1-entradapc, pc_notari = pc_notari, pc_impostos = pc_impostos) 
                cuota = calculateCuota(casa-entrada, rate, anys = 30)

                dades['casa'].append(casa)
                dades['entrada'].append(int(entrada+impostos+notaris))
                dades['entradapc'].append(int(float(1-entradapc)*100))
                dades['interes'].append(round(rate,2))
                dades['cuota'].append(int(cuota))

    dades = pd.DataFrame.from_dict(dades)
    df0 = dades[dades.casa == casa0]
    df1 = pivot_dataframe(df0, row = 'interes', columns = 'entrada', values = 'cuota')
    df1_ = pivot_dataframe(df0, row = 'interes', columns = 'entradapc', values = 'cuota')
    return df1, df1_

def calculateRangesCasa(casa0, rate0, entradapc0):
    rates = np.arange(rate0-0.35,rate0+0.35,0.05)
    dades = {'casa':[], 'entrada':[], 'interes':[],'cuota':[], 'entradapc':[]}
    for rate in rates:
        for casa in np.arange(casa0-65,casa0+5,5):
            for entradapc in np.arange(0.9,0.6,-0.025):
                entrada, impostos, notaris = despeses(casa, pcentrada = 1-entradapc, pc_notari = pc_notari, pc_impostos = pc_impostos) 
                cuota = calculateCuota(casa-entrada, rate, anys = 30)

                dades['casa'].append(int(casa))
                dades['entrada'].append(int(entrada+impostos+notaris))
                dades['entradapc'].append(round(1-entradapc,2))
                dades['interes'].append(round(rate,2))
                dades['cuota'].append(int(cuota))

    dades = pd.DataFrame.from_dict(dades)
    df2 = dades[dades.entradapc == entradapc0]
    df2 = pivot_dataframe(df2, row = 'interes', columns = 'casa', values = 'cuota')
    
    return df2

def highlight(df, row, col):
    def highlight_cell(val):
        color = 'background-color: green'
        # Apply green highlight only for the specific cell
        if (df.index[row] == val.name) and (df.columns[col] == val.index[0]):
            return [color if i == col else '' for i in range(len(val))]
        return [''] * len(val)
    
    # Apply the highlighting and the colormap
    styled_df = df.style.apply(highlight_cell, axis=1)
    return styled_df.background_gradient(cmap='coolwarm')
	
# https://www.bankinter.com/blog/economia/como-varia-sueldo-neto-funcion-salario-bruto-graficos
# https://www.ara.cat/economia/comptes-publics/1-sou-brut-diferencia-pagar-irpf-catalunya-madrid_1_4529828.amp.html
def calcularIRPF(Xn, extraIRPF_pc = 5):
    if(0):
        # Sort the dictionary by keys (X values)
        IRPF = {9:0.00, 12:0.00,14:0.00,15:0.00,18:0.05,21:0.10,27:0.15,30:0.16,33:0.17,36:0.17,40:0.19,
            42:0.20,45:0.21,48:0.22,50:0.22,55:0.24,60:0.24,65:0.25,70:0.26,75:0.27,80:0.29,85:0.29,
            90:0.30,95:0.31,100:0.32}
        sorted_dict = dict(sorted(IRPF.items()))
        
        X = np.array(list(sorted_dict.keys()))
        Y = np.array(list(sorted_dict.values()))
    else:
        X = [9,12,14,15,18,21,27,30,33,36,40,42,45,48,50,55,60,65,70,75,80,85,90,95,100]
        Y = [0.,0.,0.,0.,0.05,0.1,0.15,0.16,0.17,0.17,0.19,0.2,0.21,0.22,0.22,0.24,0.24,0.25,0.26,0.27,0.29,0.29,0.3,0.31,0.32]
    
    # Perform linear interpolation
    Yn = np.interp(Xn, X, Y)
    
    return round(Yn*(1+extraIRPF_pc/100)*Xn,3)

def calcularSS(souBrut, pc_SS = 6.47):
    if souBrut<60:
        SS = (pc_SS/100)*souBrut
    else:
        SS = 4.7250

    return round(SS,3)

def calcularSouNet(souBrut):
    SS = calcularSS(souBrut, pc_SS = 6.47)
    IRPF = calcularIRPF(souBrut, extraIRPF_pc = 5)

    souNetAny = round(souBrut-SS-IRPF,3)
    return souNetAny

def calculateNewTAE(cuotaMensual, P, C_total, anys):
    
    jj = 0
    error = 1000000
    cuotaReal = cuotaMensual + C_total/(anys*12)
    interesMax = 15
    interesMin = 0
    while error>0.001:
        
        interesi = 0.5*(interesMax+interesMin)
        cuotai = calculateCuota(P, interesi, anys = anys)
        

        if cuotai > cuotaReal:
            interesMax = interesi
            
        if cuotai < cuotaReal:
            interesMin = interesi
        
        jj+=1
        if jj>10:
            break
        
    
    return interesi

def fillSpaces(num):
    spaces = ''
    for i in range(num):
        spaces += '&nbsp;'
        
    return spaces


# First level: Tabs with text entries
st.title("Calculador Hipoteques")


# In the second tab, put the content for "Banc"

tab1, tab2, tab3, tab4 = st.tabs(["Hipoteca", "Capacitat", "Amortització", "Sensibilitat"])

with tab1:
    # In the first tab, use two columns
    col1, col2, col3 = st.columns(3)

    with col1:

        st.header("Casa")
        vivenda = float(st.text_input("Preu Compra [k€]", value="500"))
        reforma = 0
        #reforma = float(st.text_input("Preu reforma [k€]", value="0"))

        st.header("Sous")
        sou_1 = float(st.text_input("Sou 1 [k€]", value="40"))
        sou_2 = float(st.text_input("Sou 2 [k€]", value="40"))

        altresCredits = float(st.text_input("Altres Credits [€/mes]", value="0"))
        altresIngressos = float(st.text_input("Altres Ingressos [€/mes]", value="0"))

        souMensual_1 = round(calcularSouNet(sou_1)/12,3)*1000
        souMensual_2 = round(calcularSouNet(sou_2)/12,3)*1000


        if(0):
            st.markdown("""---""")
            IBI = float(st.text_input("IBI", value="450"))
            assvida = float(st.text_input("Ass. Vida", value="700"))
            assvivenda = float(st.text_input("Ass. Vivenda", value="450"))    
            if(0):
                st.text_input("Alarma", value="50")

    with col2:
        st.header("Banc")
        pcentrada = float(st.text_input("Entrada [%]", value="20"))
        anys = float(st.text_input("Anys hipoteca", value="30"))
        rate = float(st.text_input("Interes [%]", value="2.81"))

    with col3:

        entrada, impostos, notaris = despeses(vivenda, pcentrada = pcentrada/100., pc_notari = pc_notari, pc_impostos = pc_impostos)  
        cuotamensual = round(calculateCuota(vivenda+reforma-entrada, rate, anys = anys),1)
        estalvisnecessaris = round(entrada+impostos+notaris,1)
        costtotalhipoteca = round(anys*12*cuotamensual/1000.,1)
        mensualitattotal = round(cuotamensual,1)


        souMensual = souMensual_1 + souMensual_2
        stress = round((altresCredits+cuotamensual)*100/(souMensual+altresIngressos),1)

        st.header("Result")

        maxLen = 30
        frase = "Stress: "
        spaces = fillSpaces(maxLen-len(frase)+12)
        st.warning(f"{frase}{spaces}{stress}%")

        frase = "Cuota mensual: "
        spaces = fillSpaces(maxLen-len(frase))
        st.success(f"{frase}{spaces}{cuotamensual}€")
        
        frase = "Estalvis necessaris: "
        spaces = fillSpaces(maxLen-len(frase))
        st.success(f"{frase}{spaces}{estalvisnecessaris}k€")

        frase = "Cost total hipoteca: "
        spaces = fillSpaces(maxLen-len(frase))
        st.success(f"{frase}{spaces}{costtotalhipoteca}k€")


        if(0):

            mensualitatextres = round(cuotamensual+ IBI/12 + assvida/12 + assvivenda/12,1)

            st.markdown("""---""")

            st.markdown("Mensulitat amb Extres [€]: ")
            st.warning(f"{mensualitatextres}")

            st.markdown("Mensualitat Extres i despeses [€]: ")
            st.warning(f"{mensualitattotal}")

    if(0):
        df1, df1_  = calculateRangesEntrada(vivenda, rate, pcentrada/100.)
        df2 = calculateRangesCasa(vivenda, rate, pcentrada/100.)


        # Second level: Dataframes with colored cells inside a container
        with st.container():

            # Display the first dataframe with the cell (2,2) marked in red
            st.write("ENTRADA-vs-INTERES")

            # Set Seaborn plot background to transparent
            #sns.set(rc={'axes.facecolor': (0, 0, 0, 0.5),  # RGBA tuple for transparent
            #            'figure.facecolor': (0, 0, 0, 0.5)})

            # Load the example flights dataset and convert to long-form

            # Draw a heatmap with the numeric values in each cell
            f, ax = plt.subplots(figsize=(9, 6))
            sns.heatmap(df1_, annot=True, fmt="d", linewidths=.5, ax=ax, cbar=False)
            plt.yticks(rotation=0) 

            rect = patches.Rectangle((4, 7), 1, 1,  # width, height
                linewidth=2, edgecolor='blue', facecolor='none'  # Customize as needed
                )
            ax = plt.gca()
            ax.add_patch(rect)
            # Get the current x-ticksxticks = ax.get_xticks()
            xticks = ax.get_xticks()

            xticklabels = ax.get_xticklabels()

            # Print x-tick values and labels
            xticks_labels = [f'{int(label.get_text())}%\n{int(int(label.get_text())/100*vivenda+impostos+notaris)}k€' for label in xticklabels]
            ax.set_xticklabels(xticks_labels)

            plt.xlabel('Entrada')
            plt.ylabel('Interes [%]')

            st.pyplot(f)
            
            
            st.write("VIVENDA-vs-INTERES")
            f, ax = plt.subplots(figsize=(9, 6))
            sns.heatmap(df2, annot=True, fmt="d", linewidths=.5, ax=ax, cbar=False)
            plt.yticks(rotation=0) 
            ax.invert_xaxis()

            rect = patches.Rectangle((13, 7), 1, 1,  # width, height
                linewidth=2, edgecolor='blue', facecolor='none'  # Customize as needed
                )
            ax = plt.gca()
            ax.add_patch(rect)
            plt.ylabel('Interes [%]')
            plt.xlabel('Vivenda [k€]')

            st.pyplot(f)
            #st.dataframe(highlight(df1, row=8, col=2), use_container_width=True, height=400)
            # Display the second dataframe with the cell (4,4) marked in red
            #st.write("DataFrame 2")
            #st.dataframe(highlight(df2, row=4, col=4), use_container_width=True, height=400)



with tab2:

    col1, col2= st.columns(2)
    with col1:
        st.header("Casa")
        estalvis0 = float(st.text_input("Estalvis que aportarem (valor o sino el min) [k€]", value="0"))
        interesrate = float(st.text_input("interes calcular [%]", value="2.81"))
        stressTarget = float(st.text_input("Màxim stress permet [%]", value="35"))

    with col2:

        st.header("Result")
        
        souMensual_1 = round(calcularSouNet(sou_1)/12,3)*1000
        souMensual_2 = round(calcularSouNet(sou_2)/12,3)*1000

        souMensual = souMensual_1 + souMensual_2
        
        print(souMensual)

        if estalvis0 >0:
            vivenda_, entrada_, estalvisnecessaris_, cuotamensual_ = calculateAtMaxEstalvis(souMensual_1, souMensual_2, estalvis0, interesrate, anys, altresIngressos=altresIngressos,altresCredits=altresCredits,pcentrada=pcentrada, stressTarget=stressTarget)

        else:
            vivenda_, entrada_, estalvisnecessaris_, cuotamensual_ = calculateAtMaxStress(souMensual_1, souMensual_2, estalvis0, interesrate, anys, altresIngressos=altresIngressos,altresCredits=altresCredits,pcentrada=pcentrada, stressTarget=stressTarget)
            
            
        st.markdown("Preu màxim assequible [k€]: ")
        st.success(f"{round(vivenda_,1)}")

        st.markdown("Entrada real [%]: ")
        st.warning(f"{round(entrada_/vivenda_*100,2)}")

        st.markdown("Entrada necessaria [k€]: ")
        st.warning(f"{round(estalvisnecessaris_,2)}")


        st.markdown("Cuota mensual [€]: ")
        st.warning(f"{cuotamensual_}")


with tab3:

    col1, col2= st.columns(2)
    with col1:

        st.header("Casa")
        hipoteca0 = float(st.text_input("Remanent a pagar [k€]", value="140"))
        interesactual = float(eval(st.text_input("Interes actual [%]", value="3.3"))*12)/12
        anyspagar =  int(eval(st.text_input("Anys a pagar (pot ser 22.5) [anys]", value="22.7"))*12)/12
        valoramortitzat = float(eval(st.text_input("Valor a amortitzar [k€]", value="0")))
        
        costosFixes = float(st.text_input("Costos fixes [€]", value="1500"))/1000
        costosVariables = float(eval(st.text_input("Costos Variables anuals [€]", value="350 + 350")))
        
        
        ncuotamensual = round(calculateCuota(hipoteca0-valoramortitzat, interesactual, anys = anyspagar),1)


        cuota0 = round(calculateCuota(hipoteca0, interesactual, anys = anyspagar),1)
        ncuota = 10
        anysmax = anyspagar
        anysmin = 0

        jj = 0
        while abs(cuota0-ncuota)>0.01:
            nanyspagar = int(0.5*(anysmax+anysmin)*12+1)/12
            ncuota = round(calculateCuota(hipoteca0-valoramortitzat, interesactual, anys = nanyspagar),1)

            if cuota0 > ncuota:
                anysmax = nanyspagar
                
            if cuota0 < ncuota:
                anysmin = nanyspagar
            jj+=1
            if jj>15:
                break
            
        
        

    with col2:
        
        st.header("Resultat")
        st.markdown("Cuota actual [€]: ")
        st.warning(f"{round(cuota0,2)}")


        st.markdown("""---""")

        st.markdown("Nova cuota (reduïnt capital) [€]: ")
        st.warning(f"{round(ncuotamensual,2)}")
        
        
        C_total = (costosFixes + costosVariables*anyspagar)
        TAE = calculateNewTAE(ncuotamensual, hipoteca0-valoramortitzat, C_total, anyspagar)
        
        st.markdown("Nou TAE (reduïnt capital) [%]: ")
        st.success(f"{round(TAE,2)}")
        

        
        st.markdown("""---""")


        st.markdown("Nou periode (reduïnt anys) [anys]: ")
        st.warning(f"{round(nanyspagar,2)}")
        
        C_total = (costosFixes + costosVariables*nanyspagar)
        TAE = calculateNewTAE(cuota0, hipoteca0-valoramortitzat, C_total, nanyspagar)
        
        st.markdown("Nou TAE (reduïnt anys) [%]: ")
        st.success(f"{round(TAE,2)}")
        
        
with tab4:

    col1, col2, col3 = st.columns(3)
    with col1:
        deute0 = float(st.text_input("Remanent a pagar [k€]", key = "deute0", value="136.4"))
    with col2:
        interes0 = float(eval(st.text_input("Interes actual [%]", key = "interes0", value="2.2"))*12)/12
    with col3:
        anys0 =  int(eval(st.text_input("Anys a pagar (pot ser 22.5) [anys]", key = "anys0", value="21"))*12)/12
        
    st.markdown("""---""")
    
    cola1, cola2  = st.columns(2)
    with cola1:
        deltaSteps =  float(eval(st.text_input("deltaSteps [%]", key = "deltaSteps0", value="0.1")))
    with cola2:
        numSteps =  int(eval(st.text_input("nombre de passos []", key = "numSteps0", value="5")))

        
    st.markdown("""---""")
    
    ncuotamensual = round(calculateCuota(deute0, interes0, anys = anys0),1)

    st.header("Quotes en funció de interes")
    n = numSteps
    dn = deltaSteps
    
    datashow = {}
    print(interes0-dn*n, interes0+dn*n)
    for interesi in np.arange(interes0-dn*n, interes0+dn*(1+n), dn):   
        quotai = round(calculateCuota(deute0, interesi, anys = anys0),1)
        datashow[str(round(interesi,2))] = [round(quotai,1)]
        
        
    df = pd.DataFrame(datashow)
    colis = st.columns(len(df.columns))

        

    # Loop through columns
    for i, (col, (key, value)) in enumerate(zip(colis, df.iloc[0].items())):
        # Highlight if it matches interes0
        colorline = 'color: #ff4b4b;' if key == str(interes0) else ''

        # Add a right border to all columns except the last one
        border_style = "border-right: 2px solid #ddd; padding-right: 10px;" if i < len(df.columns) - 1 else ""

        col.markdown(
            f"""
            <div style="text-align: center; {border_style}">
                <p style="font-size: 20px; font-weight: bold; margin-bottom: 5px;">{key}%</p>
                <p style="font-size: 20px; font-weight: normal; {colorline}">{value}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
