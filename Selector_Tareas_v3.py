# **SELECTOR DE TAREAS**

##### Deseamos crear una herramienta en la que le decimos los parámetros que deseamos obtener y
##### el programa nos devuelve una tarea que completa los requerimientos
#### En la v2 se pueden elegir 2 parametros. Hemos cambiado los selectores manuales por barras de max y min. Codigo optimizado.

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

def Tarea(time, var1, min1, max1, var2=None, min2=None, max2=None):
    # Convertir min y max a numéricos
    min1, max1 = pd.to_numeric(min1), pd.to_numeric(max1)
    min2, max2 = pd.to_numeric(min2), pd.to_numeric(max2) if var2 else (None, None)
    time = pd.to_numeric(time)
    
    # Dado el tiempo calculo el valor de las variables en ese tiempo
    df_entreno_x_tareas[var1] = df_entreno_x_tareas[var1]*time*60
    if var2 and var2 != 'Ninguna':
        df_entreno_x_tareas[var2] = df_entreno_x_tareas[var2]*time*60

    # Filtrar las filas que cumplen con la primera variable
    filtro_var1 = (df_entreno_x_tareas[var1] >= min1) & (df_entreno_x_tareas[var1] <= max1)
    
    # Filtrar si hay segunda variable, de lo contrario tomar solo el filtro de la primera
    if var2 and min2 is not None and max2 is not None:
        filtro_var2 = (df_entreno_x_tareas[var2] >= min2) & (df_entreno_x_tareas[var2] <= max2)
    else:
        filtro_var2 = True 
    
    # Aplicar los filtros
    df_filtrado = df_entreno_x_tareas[filtro_var1 & filtro_var2]
    df_filtrado.reset_index(inplace=True)
    
    columnas = [
        'Drill Title', 'Distance Total_s', 'High Speed Running (Absolute)_s', 'High Speed Running (Relative)_s',
        'HSR Per Minute (Absolute)_s', 'Sprint Distance_s', 'Sprints_s', 'Fatigue Index_s', 'HML Distance_s',
        'HML Distance Per Minute_s', 'HML Efforts_s', 'Accelerations_s', 'Max Acceleration_s', 'Decelerations_s',
        'Distance Per Min_s', 'Max Speed_s', 'Dynamic Stress Load_s'
    ]
    
    # Crear DataFrame con los resultados filtrados
    # df_filtrado[columnas] = df_filtrado[columnas]*time*60
    for col in columnas:
        if pd.api.types.is_numeric_dtype(df_filtrado[col]):
            if (col == var1)|(col == var2):
                df_filtrado[col] = df_filtrado[col]
            else:
                df_filtrado[col] = df_filtrado[col].fillna(0) * time * 60
    df_resultado = df_filtrado[columnas].copy()
    
    # Renombrar la columna de "Drill Title" a "Tarea"
    df_resultado.rename(columns={'Drill Title': 'Tarea'}, inplace=True)

    return df_resultado
  

def obtener_rango(time,variable):
    time = pd.to_numeric(time)
    min_val = (df_entrenos_sel_vbles_sin_part[variable]*time*60).min()
    max_val = (df_entrenos_sel_vbles_sin_part[variable]*time*60).max()
    return min_val, max_val

## 4. Widgets de la app
# Intorduzco titulo del dashboard
st.write("<h1 style='text-align: center;'>SELECTOR DE TAREAS</h1>", unsafe_allow_html=True)

# Titulo de la barra lateral de la app
st.sidebar.header("SELECTOR")

# Crear widgets para seleccionar los parametros
lista_variables = ['Distance Total_s', 'High Speed Running (Absolute)_s','High Speed Running (Relative)_s',
                   'HSR Per Minute (Absolute)_s', 'Sprint Distance_s', 'Sprints_s',
                   'Fatigue Index_s', 'HML Distance_s', 'HML Distance Per Minute_s',
                   'HML Efforts_s', 'Accelerations_s', 'Max Acceleration_s', 'Decelerations_s',
                   'Distance Per Min_s', 'Max Speed_s', 'Dynamic Stress Load_s',
                   'HSR Per Minute (Relative)_s','Total Loading_s']
lista_variables_con_ninguna = ["Ninguna"] + lista_variables

time = st.sidebar.number_input('Selecciona el tiempo en minutos:', min_value=0.5, max_value=120.0, value=5.0, step=0.5)
Variable_seleccionada_1 = st.sidebar.selectbox('Selecciona una variable 1:', lista_variables)
# Obtenemos el rango dinámico para la variable seleccionada
min_rango_1, max_rango_1 = obtener_rango(time,Variable_seleccionada_1)
Valor_min_1, Valor_max_1 = st.sidebar.slider(
    f'Selecciona el rango para {Variable_seleccionada_1}:',
    min_value=float(min_rango_1), max_value=float(max_rango_1),
    value=(float(min_rango_1), float(max_rango_1)), step=(max_rango_1 - min_rango_1) / 100)
Variable_seleccionada_2 = st.sidebar.selectbox('Selecciona una variable 2:', lista_variables_con_ninguna)
# Obtenemos el rango dinámico para la variable seleccionada
if Variable_seleccionada_2 != 'Ninguna':
  min_rango_2, max_rango_2 = obtener_rango(time,Variable_seleccionada_2)
  Valor_min_2, Valor_max_2 = st.sidebar.slider(
      f'Selecciona el rango para {Variable_seleccionada_2}:',
      min_value=float(min_rango_2), max_value=float(max_rango_2),
      value=(float(min_rango_2), float(max_rango_2)), step=(max_rango_2 - min_rango_2) / 100)
   

# Widgets de la app para seleccionar los parametros
if st.sidebar.button('Resultado'):
    # Verificar si se selecciona una segunda variable
    if Variable_seleccionada_2 == "Ninguna":  # Si no se selecciona una segunda variable
        resultado = Tarea(time, Variable_seleccionada_1, Valor_min_1, Valor_max_1)
    else:
        resultado = Tarea(time, Variable_seleccionada_1, Valor_min_1, Valor_max_1, Variable_seleccionada_2, Valor_min_2, Valor_max_2)

    # Mostrar el DataFrame en la interfaz de Streamlit
    if not resultado.empty:
        st.write("Tareas que cumplen con los criterios:")
        st.dataframe(resultado)  # Mostrar el DataFrame completo
    else:
        st.write("No se encontraron tareas que cumplan los criterios.")