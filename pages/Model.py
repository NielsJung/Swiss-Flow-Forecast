import streamlit as st


st.set_page_config(
    page_title="Model",
)
#cwd = os.getcwd()
# Streamlit App
st.header('Modeling', divider='rainbow')
st.write("The live hydro data of the rivers and the weather forecasts of various weather models (ICON, GFS, JMA, GEM) are queried every hour  and saved in a database. The shown model then predicts the hourly discharge for the next 5 days based on the different weather forecasts and the measured discharges. For the prediction, the model uses the following features from the weatherforecasts:")
st.write("• Temperature")
st.write("• Snowdepth")
st.write("• Precipitation")
st.write("• Snowfall")
st.write("• Soil Moisture")
st.write("• Cloud Cover")
st.write("A separate forecast is created and displayed for each weather model.")
img_path="./data/Model Architecture.jpg"
output_image_path="./data/Model Architecture2.jpg"
st.image(img_path, caption="Model Architecture", use_column_width=True)

