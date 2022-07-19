import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy_financial as npf
import numpy as np
import random


def crazyVariable(euribor):
    way = 1
    for i in range(0, len(euribor)):
        if way == 1:
            if euribor[i - 1] > 1.5:
                euribor[i] = euribor[i - 1] + 1.5
            if euribor[i - 1] < 1.5:
                euribor[i] = euribor[i - 1] + 0.1
            if euribor[i - 1] > 5:
                euribor[i] = euribor[i - 1] - 1
                way = -1
        if way == -1:
            if euribor[i - 1] > 0:
                euribor[i] = euribor[i - 1] - 1
                way = -1
            if euribor[i - 1] < 0:
                euribor[i] = euribor[i - 1] + 0.05
                way = 1
        euribor[i] += 0.5 * random.random()
    return euribor

def calcularAmortitzacio(loan_amount = 10, anys = 30, interest_rate0_primerany = 1, interest_rate0_pos = 1,interest_rate0_neg = 1, euribor = [], amortitzacio = []):
    payment_months = anys * 12
    payment_months0 = payment_months


    principal_remaining = np.zeros(payment_months)
    interest_pay_arr = np.zeros(payment_months)
    principal_pay_arr = np.zeros(payment_months)
    monthly_payment = np.zeros(payment_months)

    loan_amount = loan_amount * 10 ** 3
    previous_principal_remaining = loan_amount
    currentPrincipal = previous_principal_remaining


    i = 0
    while currentPrincipal > 0:

        if i == 0:
            previous_principal_remaining = loan_amount
        else:
            try:
                previous_principal_remaining = principal_remaining[i - 1]
            except:
                print(previous_principal_remaining, i)

        if i % 12 == 0:
            try:
                euribori = euribor[i // 12]
            except:
                euribori = 0

            if euribori < 0:
                interest_rate0 = interest_rate0_neg
            else:
                interest_rate0 = interest_rate0_pos

            if i < 12:
                interest_rate0 = interest_rate0_primerany

            try:
                ai, wi = amortitzacio[i//12][0], amortitzacio[i//12][1]
            except:
                ai = 0
                wi = 'C'
            previous_principal_remaining0 = previous_principal_remaining
            previous_principal_remaining = previous_principal_remaining - ai*1000

            if wi == 'T':
                interest_rate = (interest_rate0 + euribori) / 100.
                periodic_interest_rate = (1 + interest_rate) ** (1 / 12.) - 1
                monthly_installment0 = -1 * npf.pmt(periodic_interest_rate, payment_months - i, previous_principal_remaining0)

                newmonths = []
                error = []
                for newpayment_months in range(i, payment_months):
                    monthly_installment = -1 * npf.pmt(periodic_interest_rate, newpayment_months - i,previous_principal_remaining)
                    error.append(abs(monthly_installment-monthly_installment0))
                    newmonths.append(newpayment_months)

                min_index = error.index(min(error))
                payment_months = newmonths[min_index]



            else:
                interest_rate = (interest_rate0 + euribori) / 100.
                periodic_interest_rate = (1 + interest_rate) ** (1 / 12.) - 1
                monthly_installment = -1 * npf.pmt(periodic_interest_rate, payment_months - i, previous_principal_remaining)

        interest_payment = round(previous_principal_remaining * periodic_interest_rate, 2)
        principal_payment = round(monthly_installment - interest_payment, 2)

        monthly_installment = interest_payment + principal_payment

        if previous_principal_remaining - principal_payment <= 0:
            principal_payment = previous_principal_remaining

        try:
            interest_pay_arr[i] = interest_payment
            principal_pay_arr[i] = principal_payment
            currentPrincipal = previous_principal_remaining - principal_payment
            principal_remaining[i] = previous_principal_remaining - principal_payment
            monthly_payment[i] = monthly_installment
        except:
            pass

        i+=1

        if i > payment_months0:
            break

    principal_pay_arr[-1] = principal_pay_arr[-2]


    return monthly_payment, interest_pay_arr, principal_pay_arr, principal_remaining

def calcularMensualitat(interest_rate0, euribori,payment_months, previous_principal_remaining):
    interest_rate = (interest_rate0 + euribori) / 100.
    periodic_interest_rate = (1 + interest_rate) ** (1 / 12.) - 1
    monthly_installment = -1 * npf.pmt(periodic_interest_rate, payment_months, previous_principal_remaining)

    return monthly_installment



st.set_page_config(page_title="Calculadora Hipoteques", layout = 'wide')
st.title("Calculadora Hipoteques")


col1, col2 = st.columns(2)

with col1:
    st.header("**Calculadora Hipoteques**")
    vivenda = st.number_input("Valor Vivenda (milers euros): ", min_value=0.0, format='%.1f', value = 250.)
    reformes = st.number_input("Reformes a hipotecar (milers euros): ", min_value=0.0, format='%.1f', value = 0.)
    home_value = vivenda + reformes

    down_payment_percent = st.number_input("Entrada (%): ", min_value=0.0, format='%.2f', value = 20.)

    interest_rate_pos = st.number_input("Interes (%): ", min_value=0.0, format='%.2f', value = 2.5)
    interest_rate_primer = st.number_input("Interes primer any (%): ", min_value=0.0, format='%.2f', value = 2.5)

    payment_years = st.number_input("Duracio Hipoteca (anys): ", min_value=3, max_value = 30, format='%d', value = 30)

    st.header("**Personal Details**")
    altres_prestecs = st.number_input("Altres prestecs mensuals (euros): ", min_value=0.0, format='%.0f', value = 0.)


    optionImpostos = ['10%','7.5%', '5%']
    impostos = st.selectbox('Quins impostos us apliquen (>33anys o >32keuros sou = 10%)', optionImpostos)
    impostos = float(impostos.replace('%',''))


with col2:

    st.header("**Interes Variable (si aplica)**")

    etext = ''
    for ei in range(0, 30):
        etext += '1.0;'
    etext = etext[:-1]


    euribortext = st.text_input('Entre el interes variable pels anys 0-30 separat per ";"  (10 valors)', etext)

    historic_euribor = {1999: 3.327, 2000: 5.202, 2001: 5.346, 2002: 4.009, 2003: 3.234, 2004: 2.504, 2005: 2.403, 2006: 3.669, 2007: 4.669, 2008: 5.44, 2009: 5.508, 2010: 1.514, 2011: 2.185, 2012: 2.127, 2013: 0.623, 2014: 0.616, 2015: 0.336, 2016: 0.065, 2017: -0.072, 2018: -0.132, 2019: -0.1, 2020: -0.062, 2021: -0.469, 2022: 1.111}
    optionlist = ['CrazyVariable', 'Custom-list', 'ZeroVariable','----']
    for anyi, eui in historic_euribor.items():
        optionlist.append(str(anyi)+ '+ CrazyVariable')
    option = st.selectbox('Variable interest option', optionlist)

    euribor = [0]*30
    if option == 'Custom-list':
        euribor = [0]*40
        i = 0
        for ei in euribortext.split(';'):
            try:
                euribor[i] = float(ei)
            except:
                euribor[i] = 0
            i += 1
    elif option == 'CrazyVariable':
        euribor = [random.random()] * 40
        extraEuribor = crazyVariable(euribor)


    elif '+ CrazyVariable' in option:
        startYear = int(option.split('+')[0])
        for i in range(0, len(euribor)):
            try:
                euribor[i] = historic_euribor[i + startYear]
            except:
                brokeAt = i
                break
        seedEuribor = [euribor[i]]*30
        extraEuribor = crazyVariable(seedEuribor)
        for j in range(brokeAt, 30):
            euribor[j] = extraEuribor[j-brokeAt]
    else:

        etext = ''
        for ei in range(0, 30):
            etext += '0;'
        etext = etext[:-1]


    amortitzacions = st.text_input('Amortitzacio en anys puntuals separts per ";"  (anys:valorenmilerseuros:K on K = T per temps o C capital)', '5:0:C;10:0:T')

    amortitzacio = {}
    amortitzacions = amortitzacions.split(';')
    for ai in amortitzacions:
        ass = ai.split(':')

        yi_, ai_, wi_ = int(ass[0]), float(ass[1]), ass[2]
        amortitzacio[yi_] = [ai_, wi_]


    x_years = np.arange(0, 30)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_years,
            y=euribor,
            name="Interest varaible afegit"
        )
    )


    fig.update_layout(title='Interest varaible afegit',
                      xaxis_title='anys',
                      yaxis_title='Interest varaible afegit (%)',
                      )

    st.plotly_chart(fig, use_container_width=True)


st.header(" ")
st.header("**Resultats Analisis**")

col1, col2 = st.columns(2)
with col1:
    deute = home_value * (1 - down_payment_percent / 100.)
    deute = st.number_input("Capital hipotecat (milers euros): ", min_value=0., max_value=10000.,  format='%.1f', value=deute)

    mensualitat = calcularMensualitat(interest_rate_pos, euribor[0], payment_years*12, deute)*1000

    monthly_payment, interest_pay_arr, principal_pay_arr, principal_remaining = calcularAmortitzacio(loan_amount=deute,
                                                                                                     anys=payment_years,
                                                                                                     interest_rate0_primerany=interest_rate_primer,
                                                                                                     interest_rate0_pos=interest_rate_pos,
                                                                                                     interest_rate0_neg=interest_rate_pos,
                                                                                                     euribor=euribor,
                                                                                                     amortitzacio = amortitzacio)

    st.number_input("Mensualitat (euros): ", min_value=mensualitat-0.01, max_value=mensualitat+0.01,  format='%.1f', value=mensualitat)
    credits = altres_prestecs + mensualitat
    st.number_input("Ingressos nets minims mensuals (<35%): ", min_value=credits/0.35-0.01, max_value=credits/0.35+0.01,  format='%.1f', value=credits/0.35)

    costTotal = sum(monthly_payment)/1000. + sum([vals[0] for ki, vals in amortitzacio.items()])
    st.number_input("Cost total hipoteca (milers euros): ", min_value=costTotal-0.01, max_value=costTotal+0.01,  format='%.1f', value=costTotal)



with col2:
    entrada = home_value * (down_payment_percent / 100.)
    st.number_input("Entrada Hipoteca (milers euros): ", min_value=entrada-0.01, max_value=entrada+0.01,  format='%.1f', value=entrada)

    honoraris = 5.0
    st.number_input("Honoraris (milers euros): ", min_value=3.5, max_value=15.0,  format='%.1f', value=honoraris, step = 0.25)

    impostosCompraVenta = vivenda*impostos/100.
    st.number_input("Impostos Compra-Venta (milers euros): ", min_value=impostosCompraVenta-0.01, max_value=impostosCompraVenta+0.01,  format='%.1f', value=impostosCompraVenta)

    minEstalvis = honoraris + entrada + impostosCompraVenta
    st.number_input("Minim Estalvis necessaris (milers euros): ", min_value=minEstalvis-0.01, max_value=minEstalvis+0.01,  format='%.1f', value=minEstalvis)





anys_plot = [round(i/12,2) for i in range(0, len(monthly_payment))]
anys_data, month_data, capital_data, interest_data, capitalrem_data = [], [], [], [], []
principal_remaining_ = [pi/1000. for pi in principal_remaining]

for i in np.arange(0, len(monthly_payment), 12):
    anys_data.append(i//12)
    capital_data.append(round(principal_pay_arr[i],2))
    month_data.append(round(monthly_payment[i],2))
    interest_data.append(round(interest_pay_arr[i],2))
    capitalrem_data.append(round(principal_remaining[i]/1000.,2))




fig = make_subplots(
    rows=3, cols=1,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           [{"type": "scatter"}],
           [{"type": "scatter"}]
          ]
)

fig.add_trace(
        go.Table(
            header=dict(
                    values=['Any','Mensualitat', 'Pagament Capital (euros)', 'Pagament Ineteressos (euros)', 'Capital Restant (milers euros)']
                ),
            cells = dict(
                    values =[anys_data, month_data, capital_data, interest_data, capitalrem_data]
                )
            ),
        row=1, col=1
    )

fig.add_trace(
        go.Scatter(
                x=anys_plot,
                y=monthly_payment,
                name= "Mensualitat"
            ),
        row=2, col=1
    )


fig.add_trace(
        go.Scatter(
                x=anys_plot,
                y=principal_pay_arr,
                name= "Pagament de capital"
            ),
        row=2, col=1
    )

fig.append_trace(
        go.Scatter(
            x=anys_plot,
            y=interest_pay_arr,
            name="Pagament Interessos"
        ),
        row=2, col=1
    )

fig.append_trace(
        go.Scatter(
            x=anys_plot,
            y=principal_remaining_,
            name="Capital Restant"
        ),
        row=3, col=1
    )

fig.update_layout(title='',
                   xaxis_title='Anys',
                   yaxis_title='Quanitat (euros)',
                   height= 1200,
                   width = 1200,
                   legend= dict(
                           orientation="h",
                           yanchor='top',
                           y=0.66,
                           xanchor= 'left',
                           x= 0.01,bgcolor = 'rgba(0,0,0,0)'
                       )
                  )

st.plotly_chart(fig, use_container_width=True)
