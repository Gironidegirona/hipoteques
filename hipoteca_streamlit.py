import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
sns.set_theme()



# Mobile-friendly settings
st.set_page_config(layout="centered")

def calculateCuota(c0, rate, anys = 30):
    ratem = rate/1200
    cuota = round((c0*(ratem*(1+ratem)**(anys*12))/((1+ratem)**(12*anys)-1))*1000,1)

    return cuota

def despeses(vivenda, pcentrada = 0.2):
    entrada = vivenda*pcentrada
    impostos = vivenda*0.1
    notaris = vivenda*0.015

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
                entrada, impostos, notaris = despeses(casa, pcentrada = 1-entradapc)
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
                entrada, impostos, notaris = despeses(casa, pcentrada = 1-entradapc)
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


# First level: Tabs with text entries
st.title("Calculador Hipoteques")


# In the second tab, put the content for "Banc"

tab1, tab2, tab3 = st.tabs(["Hipoteca", "Stress", "Capacitat"])

with tab1:
    # In the first tab, use two columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Casa")
        vivenda = float(st.text_input("Preu Compra [k€]", value="500"))
        reforma = 0
        #reforma = float(st.text_input("Preu reforma [k€]", value="0"))

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
        rate = float(st.text_input("Interes [%]", value="2.51"))

    with col3:

        entrada, impostos, notaris = despeses(vivenda, pcentrada = pcentrada/100.) 
        cuotamensual = round(calculateCuota(vivenda+reforma-entrada, rate, anys = anys),1)
        estalvisnecessaris = round(entrada+impostos+notaris,1)
        costtotalhipoteca = round(anys*12*cuotamensual/1000.,1)
        mensualitatextres = round(cuotamensual+ IBI/12 + assvida/12 + assvivenda/12,1)
        mensualitattotal = round(cuotamensual,1)




        st.header("Result")
        st.markdown("Cuota mensual [€]: ")
        st.success(f"{cuotamensual}")
        
        st.markdown("Estalvis necessaris [k€]: ")
        st.success(f"{estalvisnecessaris}")


        st.markdown("Cost total hipoteca [k€]: ")
        st.success(f"{costtotalhipoteca}")

        st.markdown("""---""")

        st.markdown("Mensulitat amb Extres [€]: ")
        st.warning(f"{mensualitatextres}")

        if(0):
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
        sou_1 = float(st.text_input("Sou 1 [k€]", value="40"))
        sou_2 = float(st.text_input("Sou 2 [k€]", value="40"))

        st.markdown("""---""")
        altresCredits = float(st.text_input("Altres Credits [€/mes]", value="0"))
        altresIngressos = float(st.text_input("Altres Ingressos [€/mes]", value="0"))

        souMensual_1 = round(calcularSouNet(sou_1)/12,3)*1000
        souMensual_2 = round(calcularSouNet(sou_2)/12,3)*1000

        souMensual = souMensual_1 + souMensual_2
        stress = round((altresCredits+cuotamensual)*100/(souMensual+altresIngressos),1)

    
    with col2:

        st.header("Result")
        st.markdown("Stress [%]: ")
        if stress < 35:
            st.success(f"{stress}")
        if stress > 35 and stress < 40:
            st.warning(f"{stress}")
        if stress > 40:
            st.error(f"{stress}")


        st.markdown("Cuota mensual [€]: ")
        st.warning(f"{cuotamensual}")

        if(0):
            st.markdown("""---""")
            st.markdown("Sou net 12 pagues[€]: ")
            st.success(f"{souMensual_1}")

            st.markdown("Sou net 12 pagues[€]: ")
            st.success(f"{souMensual_2}")


with tab3:

    col1, col2= st.columns(2)
    with col1:
        st.header("Casa")
        estalvis = float(st.text_input("Estalvis que aportarem (valor o sino el min) [k€]", value="0"))
        interesrate = float(st.text_input("interes calcular [%]", value="2.71"))
        stressTarget = float(st.text_input("Màxim stress permet [%]", value="35"))


    with col2:

        st.header("Result")

        vivendamin, vivendamax = 0, 600
        stress_ = 100
        vivenda_ = 0
        cuotamensual_ = 0


        souMensual = (souMensual_1 + souMensual_2)

        if  (1):
	    ii = 0
            while abs(stress_-stressTarget)>1:
                vivenda_ = 0.5*(vivendamin+vivendamax)
                entrada_, impostos_, notaris_ = despeses(vivenda_, pcentrada = pcentrada/100.) 

                if estalvis > (entrada_+impostos_+notaris_):
                    entrada_ = estalvis - impostos_-notaris_

                cuotamensual_ = round(calculateCuota(vivenda_+reforma-entrada_, interesrate, anys = anys),1)
                estalvisnecessaris_ = round(entrada_+impostos_+notaris_,1)

                stress_ = round((altresCredits+cuotamensual_)*100/(souMensual+altresIngressos),1)

                if stress_ > stressTarget:
                    vivendamax = vivenda_
                
                if stress_ < stressTarget:
                    vivendamin = vivenda_
		ii+=1
		if ii>10:
                    break

            
            st.markdown("Preu màxim assequible [k€]: ")
            st.success(f"{round(vivenda_,1)}")

            st.markdown("Entrada real [%]: ")
            st.warning(f"{round(entrada_/vivenda_*100,2)}")

            st.markdown("Cuota mensual [€]: ")
            st.warning(f"{cuotamensual}")


