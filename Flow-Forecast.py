import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pytz
import json
import numpy as np
from azure.cosmos import CosmosClient
from datetime import datetime
sns.set_theme()

def dict_to_df(data_dict):
    df=pd.Series(data=list(data_dict.values()), index=list(data_dict.keys()))
    df.index = pd.to_datetime(df.index)
    return df



def create_new_plot(station_id):
    river_data=query_forecast(station_id)

    measurements=river_data["Measurements"]
    measurements=dict_to_df(measurements)
    start, stopp=measurements.index.min(),measurements.index.max()
    max_value=np.max(measurements)
    try:
        forecasts=river_data["Prediction"]
    except:
        forecasts={}

    forecasts=json.loads(forecasts)


    for weather_model in forecasts:
        forecasts[weather_model]=dict_to_df(forecasts[weather_model])
        start=min([start, forecasts[weather_model].index.min().replace(tzinfo=pytz.UTC)])
        stopp=max([stopp, forecasts[weather_model].index.max().replace(tzinfo=pytz.UTC)])


    st.subheader(choosen_river)
    colors=["darkcyan", "limegreen", "olive", "red"]
    linestyles = ['dotted', 'dashed','dashdot', (0, (3, 5, 1, 5, 1, 5)),(0, (3, 10, 1, 10, 1, 10)),(0, (5, 1))]
    num=0
    fig, ax = plt.subplots()
    ax.plot(measurements.index, measurements.values,marker='o',c="b", markersize=2.0, label="Measured")
    for weather_model in forecasts:
        ax.plot(forecasts[weather_model].index, forecasts[weather_model].values, c=colors[num], label=weather_model.replace("_seamless", '').upper(),linestyle='dashed')
        num=num+1
        max_value=np.max([max_value,np.max(forecasts[weather_model])])

    ax.xaxis.set_major_locator(mdates.DayLocator())  # Ein Label pro Tag
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))  # Formatierung ohne Jahr
    ax.legend()
    ax.set_xlim(start, stopp)
    ax.set_ylim(0, np.max([10, 1.1*max_value]))
    ax.set_ylabel( "Flow [$m^3/s$]")
    aktueller_zeitstempel = datetime.now()
    ax.set_title("Forecasttime: "+str(aktueller_zeitstempel)[:19])
    return fig



def query_avilable_rivers():
    connection_string=st.secrets["DB_connection_string"]
    cosmos_client = CosmosClient.from_connection_string(connection_string)

    # Datenbank und Container auswählen
    database_name = "Rivers"
    container_name = "MeasuredFlow"

    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Cosmos DB-Abfrage, um alle Dokumente im Container abzurufen
    query = "SELECT * FROM c"

    # Cosmos DB-Abfrage durchführen
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    station_ids={}
    for item in items:
        station_ids[item['id']]=item['StationID']



    # Hier können Sie auf die IDs der Dokumente zugreifen
    return station_ids


def query_forecast(station_id):
    connection_string=st.secrets["DB_connection_string"]
    cosmos_client = CosmosClient.from_connection_string(connection_string)

    # Datenbank und Container auswählen
    database_name = "Rivers"
    container_name = "MeasuredFlow"

    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Cosmos DB-Abfrage, um alle Dokumente im Container abzurufen
    query=f"SELECT * FROM c WHERE c.StationID = {station_id}"

    # Cosmos DB-Abfrage durchführen
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    return items[0]

st.set_page_config(
    page_title="Flow Forecast",
    page_icon="🌦️🌤️",
)
#cwd = os.getcwd()
# Streamlit App
st.title('Swiss Riverflow Forecast')

station_ids=query_avilable_rivers()

rivers=list(station_ids.keys())


# Auswahl des Plots
choosen_river = st.selectbox('Rivers:',rivers )
fig=create_new_plot(station_ids[choosen_river])
st.pyplot(fig)





