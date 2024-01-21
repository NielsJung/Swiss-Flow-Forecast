import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pytz
import json
from azure.cosmos import CosmosClient
from datetime import datetime
sns.set_theme()

def dict_to_df(data_dict):
    df=pd.Series(data=list(data_dict.values()), index=list(data_dict.keys()))
    df.index = pd.to_datetime(df.index)
    return df

def query_forecast_times():
    
    with open(r'data/PlotCreationTime.json', 'r', encoding='utf-8') as json_file:
        data_dict = json.load(json_file)
    station_ids, forecast_times={},{}
    for river in data_dict:
        station_ids[river]=data_dict[river]["StationID"]
        forecast_times[river]=data_dict[river]["Forecasttime"]

    return station_ids, forecast_times

def search_for_forecast_plot(river,station_id, forecast_time):
    
    img_folder="data/Plots"
    aktueller_zeitstempel = datetime.now()
    forecast_time=datetime.strptime(forecast_time, '%Y-%m-%d %H:%M:%S')

    timedelta=(aktueller_zeitstempel - forecast_time).total_seconds()

    img_path=img_folder+"/"+river+".png"
    if timedelta>=3600:
        create_new_plot(station_id, img_path)
        forecast_time=update_forecast_time(river)

    return img_path, str(forecast_time)

def create_new_plot(station_id, img_path):
    river_data=query_forecast(station_id)

    measurements=river_data["Measurements"]
    measurements=dict_to_df(measurements)
    start, stopp=measurements.index.min(),measurements.index.max()

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
    linestyles = ['dotted', 'dashed','dashdot', (0, (3, 5, 1, 5, 1, 5)),(0, (3, 10, 1, 10, 1, 10)),(0, (5, 1))]
    num=0
    fig, ax = plt.subplots()
    ax.plot(measurements.index, measurements.values,marker='o',c="b", markersize=2.0, label="Measured")
    for weather_model in forecasts:
        ax.plot(forecasts[weather_model].index, forecasts[weather_model].values, c="limegreen", label=weather_model.replace("_seamless", '').upper(),linestyle=linestyles[num])
        num=num+1

    ax.xaxis.set_major_locator(mdates.DayLocator())  # Ein Label pro Tag
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))  # Formatierung ohne Jahr
    ax.legend()
    ax.set_xlim(start, stopp)
    ax.set_ylabel( "Flow [$m^3/s$]")
    plt.savefig(img_path, dpi=800)
    plt.close()

def update_forecast_time(river):

    with open(r'data/PlotCreationTime.json', 'r', encoding='utf-8') as json_file:
        data_dict = json.load(json_file)
    data_dict[river]["Forecasttime"]=str(datetime.now())[:-7]
    with open(r'data/PlotCreationTime.json', 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, indent=2, ensure_ascii=False)

    return data_dict[river]["Forecasttime"]


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

station_ids, forecast_times=query_forecast_times()
rivers=list(forecast_times.keys())




# Auswahl des Plots
choosen_river = st.selectbox('Rivers:',rivers )
img_path, new_forecast_time=search_for_forecast_plot(choosen_river,station_ids[choosen_river], forecast_times[choosen_river])
forecast_times[choosen_river]=new_forecast_time

st.image(img_path, caption="Forecasttime: "+forecast_times[choosen_river], use_column_width=True)



