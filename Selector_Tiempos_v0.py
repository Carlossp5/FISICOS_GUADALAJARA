# **SELECTOR DE TIEMPOS**

##### Deseamos crear una herramienta en la que le decimos los parámetros que deseamos obtener y el ejercicio que queremos y
##### el programa nos devuelve cuanto tiempo lo debemos hacer

## 0. CARGA DE REQUERIMIENTOS

import pandas as pd
import streamlit as st

pd.set_option('display.max_rows', None)

## 1. CARGAR DATASETS

GUADALAJARA_FISICOS_AGO24 = pd.read_csv("https://raw.githubusercontent.com/Carlossp5/FISICOS_GUADALAJARA/main/GUADALAJARA24-25.csv", sep=',', index_col=False)

## 2. SELECCION DE VARIABLES
df_entrenos_sel_vbles = GUADALAJARA_FISICOS_AGO24[['Player Name','Total Time','Player Position','Drill Title','Distance Total','High Speed Running (Absolute)','High Speed Running (Relative)',
                                     'HSR Per Minute (Absolute)','Sprint Distance','Sprints','Fatigue Index','HML Distance','HML Distance Per Minute','HML Efforts',
                                     'Accelerations','Max Acceleration','Decelerations','Distance Per Min','Max Speed','Dynamic Stress Load','HSR Per Minute (Relative)',
                                     'Session Type','Total Loading']]

df_entrenos_sel_vbles_sin_part = df_entrenos_sel_vbles[~df_entrenos_sel_vbles['Drill Title'].isin(['Entire Session','SEGUNDA PARTE','PRIMERA PARTE'])]

### Calculo los segundos que ha durado cada tarea
df_entrenos_sel_vbles_sin_part['Segundos_Time'] = df_entrenos_sel_vbles_sin_part['Total Time'].astype(str).str.split(':').apply(lambda x: int(x[0])*3600 + int(x[1])*60 + int(x[2]))

### Calculo el valor de cada variable por segundo
columns_to_multiply = ['Distance Total', 'High Speed Running (Absolute)', 'High Speed Running (Relative)', 
                       'HSR Per Minute (Absolute)', 'Sprint Distance', 'Sprints', 'Fatigue Index', 'HML Distance',
                       'HML Distance Per Minute', 'HML Efforts', 'Accelerations', 'Max Acceleration', 
                       'Decelerations', 'Distance Per Min', 'Max Speed', 'Dynamic Stress Load', 
                       'HSR Per Minute (Relative)', 'Total Loading']

# Iterar sobre cada columna y crear la nueva columna multiplicada
for col in columns_to_multiply:
    new_col_name = col + '_s'  # Crear el nuevo nombre con el sufijo _s
    df_entrenos_sel_vbles_sin_part[new_col_name] = df_entrenos_sel_vbles_sin_part[col] / df_entrenos_sel_vbles_sin_part['Segundos_Time']

## 3. ALGORITMO DE SELECCION DE TAREAS
df_entreno_x_tareas = df_entrenos_sel_vbles_sin_part.groupby('Drill Title').agg({
                          'Distance Total_s':'mean', 'High Speed Running (Absolute)_s':'mean','High Speed Running (Relative)_s':'mean',
                          'HSR Per Minute (Absolute)_s':'mean', 'Sprint Distance_s':'mean', 'Sprints_s':'mean',
                          'Fatigue Index_s':'mean', 'HML Distance_s':'mean', 'HML Distance Per Minute_s':'mean',
                          'HML Efforts_s':'mean', 'Accelerations_s':'mean', 'Max Acceleration_s':'mean', 'Decelerations_s':'mean',
                          'Distance Per Min_s':'mean', 'Max Speed_s':'mean', 'Dynamic Stress Load_s':'mean',
                          'HSR Per Minute (Relative)_s':'mean',
                          'Total Loading_s':'mean'
                          })

# Reseteo el indice para Drill Title sea una variable
df_entreno_x_tareas.reset_index(inplace=True)

def Tiempo(Tarea, var1, valor1):
    # Cálculo de Tiempo_s y Tiempo_m
    df_entreno_x_tareas_selec = df_entreno_x_tareas[df_entreno_x_tareas['Drill Title']==Tarea]
    Tiempo_s = valor1 / df_entreno_x_tareas_selec[var1].values[0]
    Tiempo_m = Tiempo_s / 60
    
    # Definir las columnas que quieres extraer (excepto 'Drill Title')
    columnas = [
        'Distance Total_s', 'High Speed Running (Absolute)_s', 'High Speed Running (Relative)_s',
        'HSR Per Minute (Absolute)_s', 'Sprint Distance_s', 'Sprints_s', 'Fatigue Index_s', 'HML Distance_s',
        'HML Distance Per Minute_s', 'HML Efforts_s', 'Accelerations_s', 'Max Acceleration_s', 'Decelerations_s',
        'Distance Per Min_s', 'Max Speed_s', 'Dynamic Stress Load_s'
    ]
    
    # Extraer los valores de esas columnas y multiplicarlos por Tiempo_s
    valores_multiplicados = df_entreno_x_tareas_selec[columnas] * Tiempo_s

        # Añadir las columnas 'Drill Title', 'Tiempo_s' y 'Tiempo_m'
    valores_multiplicados['Drill Title'] = Tarea
    valores_multiplicados['Tiempo_s'] = Tiempo_s
    valores_multiplicados['Tiempo_m'] = Tiempo_m
    
    # Reordenar las columnas para que 'Drill Title', 'Tiempo_s' y 'Tiempo_m' sean las primeras
    columnas_finales = ['Drill Title', 'Tiempo_s', 'Tiempo_m'] + columnas
    valores_multiplicados = valores_multiplicados[columnas_finales]
    
    return valores_multiplicados, Tiempo_m

## 4. Widgets de la app
# Intorduzco titulo del dashboard
st.write("<h1 style='text-align: center;'>SELECTOR DE TIEMPOS</h1>", unsafe_allow_html=True)

# Titulo de la barra lateral de la app
st.sidebar.header("SELECTOR")

# Crear widgets para seleccionar los parametros
lista_variables = ['Distance Total_s', 'High Speed Running (Absolute)_s','High Speed Running (Relative)_s',
                   'HSR Per Minute (Absolute)_s', 'Sprint Distance_s', 'Sprints_s',
                   'Fatigue Index_s', 'HML Distance_s', 'HML Distance Per Minute_s',
                   'HML Efforts_s', 'Accelerations_s', 'Max Acceleration_s', 'Decelerations_s',
                   'Distance Per Min_s', 'Max Speed_s', 'Dynamic Stress Load_s',
                   'HSR Per Minute (Relative)_s','Total Loading_s']

Tarea_1 = st.sidebar.selectbox('Selecciona la tarea:', df_entreno_x_tareas['Drill Title'].to_list())
Variable_seleccionada_1 = st.sidebar.selectbox('Selecciona un parámetro:', lista_variables)
Valor_1 = st.sidebar.number_input('Selecciona el valor a alcanzar:', min_value=0, max_value=100000, value=0, step=1)
   

# # Widgets de la app para seleccionar los parametros
# if st.sidebar.button('Resultado'):
#     valores_multiplicados, Tiempo_m = Tiempo(Tarea_1, Variable_seleccionada_1, Valor_1)
    
#     Tiempo_min = Tiempo_m.astype(str).str.split('.').apply(lambda x: x[0])
#     Tiempo_min_seg = Tiempo_m.astype(str).str.split('.').apply(lambda x: x[1])
#     Tiempo_min_seg = pd.to_numeric(Tiempo_min_seg)
#     Tiempo_min_seg = Tiempo_min_seg*0.6

#     # Mostrar el DataFrame en la interfaz de Streamlit
#     if Tiempo_m <= 120:
#         st.write(f"Tiempo necesario para alcanzar los requerimientos: {Tiempo_min:.2f} minutos y {Tiempo_min_seg:.3f}")
#         st.write(valores_multiplicados)
#     else:
#         st.write("El tiempo necesario para llegar a los requerimientos superaría las 2 horas")

if st.sidebar.button('Resultado'):
    valores_multiplicados, Tiempo_m = Tiempo(Tarea_1, Variable_seleccionada_1, Valor_1)
    
    # Calcular minutos y segundos
    Tiempo_min = int(Tiempo_m)  # Obtiene la parte entera (minutos)
    Tiempo_seg = int((Tiempo_m - Tiempo_min) * 60)  # Convierte la parte decimal a segundos

    # Mostrar el DataFrame en la interfaz de Streamlit
    if Tiempo_m <= 120:
        st.write(f"Tiempo necesario para alcanzar los requerimientos: {Tiempo_min} minutos y {Tiempo_seg} segundos")
        st.write(valores_multiplicados)
    else:
        st.write("El tiempo necesario para llegar a los requerimientos superaría las 2 horas")