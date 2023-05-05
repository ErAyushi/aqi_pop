from flask import Flask, render_template, request
import pandas as pd
import pickle
import folium
from folium.plugins import MarkerCluster

app = Flask(__name__, static_folder='templates')


@app.route('/')
def home():
    return render_template('home2.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Get user input values
    month = int(request.form['month'])
    year = int(request.form['year'])
    date = pd.to_datetime('{}-{}-01'.format(year, month))

    with open('xg2.pickle', 'rb') as f:
        xg = pickle.load(f)

        data = pd.read_csv("eda_lat_lon.csv")
    # Create a dictionary to store the predictions and coordinates for all cities
    predictions = {}

    # Iterate over all city-encoded values
    for city_encoded in range(1, 27):
        # Create a user input dataframe for the current city
        user_input = pd.DataFrame({

            'pm2.5': [0],
            'pm10': [0],
            'no': [0],
            'no2': [0],
            'nox': [0],
            'nh3': [0],
            'co': [0],
            'so2': [0],
            'o3': [0],
            'benzene': [0],
            'toluene': [0],
            'month': [month],
            'year': [year],
            'city_encoded': [city_encoded]
        })

        # Calculate the mean values for the other features for the specified city and month
        city_month_data = data[(data['city_encoded'] == city_encoded) & (data['month'] == month)]
        mean_pm2_5 = city_month_data['pm2.5'].mean()
        mean_pm10 = city_month_data['pm10'].mean()
        mean_no = city_month_data['no'].mean()
        mean_no2 = city_month_data['no2'].mean()
        mean_nox = city_month_data['nox'].mean()
        mean_nh3 = city_month_data['nh3'].mean()
        mean_co = city_month_data['co'].mean()
        mean_so2 = city_month_data['so2'].mean()
        mean_o3 = city_month_data['o3'].mean()
        mean_benzene = city_month_data['benzene'].mean()
        mean_toluene = city_month_data['toluene'].mean()

        # Update the user input dataframe with the mean values for the other features
        user_input['pm2.5'] = mean_pm2_5
        user_input['pm10'] = mean_pm10
        user_input['no'] = mean_no
        user_input['no2'] = mean_no2
        user_input['nox'] = mean_nox
        user_input['nh3'] = mean_nh3
        user_input['co'] = mean_co
        user_input['so2'] = mean_so2
        user_input['o3'] = mean_o3
        user_input['benzene'] = mean_benzene
        user_input['toluene'] = mean_toluene

        # Use the model to make prediction
        prediction = round(float(xg.predict(user_input)), 2)


        # Determine the color of the marker based on the predicted AQI value
        if prediction <= 50: #Good
            color = 'green'

        elif prediction <= 100: #Moderate
            color = 'yellow'

        # If the AQI is between 101 and 200, set the color to orange
        elif prediction <= 200: #Unhealthy for Sensitive Groups
            color = 'orange'

        # If the AQI is between 201 and 300, set the color to red
        elif prediction <= 300: #Unhealthy
            color = 'red'

        # If the AQI is greater than 300, set the color to purple
        else: #Very Unhealthy
            color = 'purple'

        # Get the latitude and longitude for the current city
        city_month_data = data[(data['city_encoded'] == city_encoded) & (data['month'] == month)]
        if not city_month_data.empty:
            city_lat = city_month_data['lat'].iloc[0]
            city_lon = city_month_data['lon'].iloc[0]
        else:
            city_lat = 0
            city_lon = 0

        # Add the prediction and coordinates to the dictionary
        predictions['City{}'.format(city_encoded)] = {'Prediction': prediction, 'lat': city_lat,
                                                      'lon': city_lon, 'Color': color}

    # Create a map with the markers for all cities
    city_map = folium.Map(location=[20.5937, 78.9629], zoom_start=4)
    marker_cluster = MarkerCluster().add_to(city_map)

    for city in predictions:
        folium.Marker([predictions[city]['lat'], predictions[city]['lon']],
                      popup='AQI Prediction: {}'.format(predictions[city]['Prediction']),
                      icon=folium.Icon(color=predictions[city]['Color'])).add_to(marker_cluster)

    # Save the map to an HTML file and display it
    city_map.save('templates/prediction.html')
    return render_template('prediction.html')

if __name__ == '__main__':
    app.run(debug=True, port=5007)