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
import matplotlib.lines
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


    def reorderLegend(ax=None, order=None):
        handles, labels = ax.get_legend_handles_labels()
        info = dict(zip(labels, handles))


        new_handles = [info[l] for l in order]
        return new_handles, order

    st.subheader(choosen_river)
    colors=["darkcyan", "limegreen", "olive", "red"]
    linestyles = ['dotted', 'dashed','dashdot', (0, (3, 5, 1, 5, 1, 5)),(0, (3, 10, 1, 10, 1, 10)),(0, (5, 1))]
    num=0
    
    title="$\\bf{Weathermodels}$"
    fig, ax = plt.subplots()
    ax.plot(measurements.index, measurements.values,marker='o',c="b", markersize=2.0, label="Measurements")
    ax.add_line(matplotlib.lines.Line2D([], [], color="none", label=title))
    all_labels=["Measurements", title]

    for weather_model in forecasts:
        label=weather_model.replace("_seamless", '').upper()
        ax.plot(forecasts[weather_model].index, forecasts[weather_model].values, c=colors[num],linestyle='dashed', label=label)
        num=num+1
        max_value=np.max([max_value,np.max(forecasts[weather_model])])
        all_labels.append(label)
        

    handles, labels = reorderLegend(ax=ax, order=all_labels)
    leg = ax.legend(handles=handles, labels=labels)
    for item, label in zip(leg.legendHandles, leg.texts):
        if label._text  in [title]:
            width=item.get_window_extent(fig.canvas.get_renderer()).width
            label.set_ha('left')
            label.set_position((-2*width,0))
    

    

    ax.xaxis.set_major_locator(mdates.DayLocator())  # Ein Label pro Tag
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))  # Formatierung ohne Jahr


    #ax.legend()
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





