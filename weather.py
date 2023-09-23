import subprocess
import sys
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import os

def append_to_excel(city_name, flattened_data):
    # Define the Excel file path
    excel_path = "all_cities_weather.xlsx"
    
    # Check if the Excel file already exists
    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path)
    else:
        df_existing = pd.DataFrame()
    
    # Convert the flattened data into a dataframe
    df_new = pd.DataFrame([flattened_data])
    df_new.insert(0, 'City', city_name)  # Inserting city as the first column
    
    # Append the new data to the existing dataframe
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    
    # Save the combined data to Excel
    df_combined.to_excel(excel_path, index=False)

def flatten_data(data):
    flattened = {}

    # Coords
    coords = data.get("coord", {})
    flattened["lon"] = coords.get("lon")
    flattened["lat"] = coords.get("lat")

    # Main weather details
    main = data.get("weather", [{}])[0]
    flattened["main"] = main.get("main")
    flattened["description"] = main.get("description")

    # Basic details
    flattened["temp"] = data.get("main", {}).get("temp")
    flattened["feels_like"] = data.get("main", {}).get("feels_like")
    flattened["pressure"] = data.get("main", {}).get("pressure")
    flattened["humidity"] = data.get("main", {}).get("humidity")
    
    # Visibility, wind, and clouds
    flattened["visibility"] = data.get("visibility")
    flattened["wind_speed"] = data.get("wind", {}).get("speed")
    flattened["wind_deg"] = data.get("wind", {}).get("deg")
    flattened["clouds"] = data.get("clouds", {}).get("all")

    # Others
    flattened["timezone"] = data.get("timezone")
    flattened["country"] = data.get("sys", {}).get("country")
    flattened["sunrise"] = data.get("sys", {}).get("sunrise")
    flattened["sunset"] = data.get("sys", {}).get("sunset")

    return flattened



def plot_weather_data(city_name, data):
    # Extracting the main data
    main_data = data.get('main', {})
    
    temperature = main_data.get('temp', 0) - 273.15  # Convert from Kelvin to Celsius
    pressure = main_data.get('pressure', 0)
    humidity = main_data.get('humidity', 0)

    # Create a bar chart
    labels = ['Temperature (°C)', 'Pressure (hPa)', 'Humidity (%)']
    values = [temperature, pressure, humidity]
    
    plt.bar(labels, values, color=['blue', 'red', 'green'])
    plt.title(f"Weather Data for {city_name}")
    plt.savefig(f"{city_name}_weather_plot.png")
    plt.show()


def save_to_excel(city_name, data):
    # Convert data to dataframe
    df = pd.DataFrame(data.get('main', {}), index=[0])
    
    # Save to Excel
    with pd.ExcelWriter(f"{city_name}_weather.xlsx", engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Weather Data")
        
        # Access the XlsxWriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets["Weather Data"]
        
        # Create a chart object
        chart = workbook.add_chart({'type': 'column'})

        # Configure the chart from the dataframe data.
        for i in range(2, df.shape[1] + 2):
            chart.add_series({
                'name':       [f"Weather Data", 0, i],
                'categories': [f"Weather Data", 1, 1, 1, df.shape[1]],
                'values':     [f"Weather Data", 1, i, 1, i],
            })
        chart.set_title({'name': f"Weather Data for {city_name}"})
        worksheet.insert_chart('F2', chart)


def install_packages(packages):
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def get_countries_and_cities():
    url = 'https://countriesnow.space/api/v0.1/countries'
    response = requests.get(url)
    data = response.json()
    return data.get('data', [])

def get_city_weather(city_name, api_key):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'
    response = requests.get(url)
    data = response.json()
    return data

def main():
    api_key = 'a82a6ba716f6d4aaf03bf78525caea4f'  # Replace with your actual OpenWeatherMap API key
    necessary_packages = ['requests', 'pandas', 'matplotlib', 'xlsxwriter']

    install_packages(necessary_packages)

    #libraries for visuals
    import pandas as pd 
    import matplotlib.pyplot as plt
    
    countries = get_countries_and_cities()

    while True:
        print("List of Countries:")
        for i, country in enumerate(countries, 1):
            print(f"{i}. {country['country']}")

        try:
            country_choice = int(input("Enter the number of a country (or type 'exit' to quit): "))
            if country_choice < 1 or country_choice > len(countries):
                if input("Invalid choice. Enter 'exit' to quit or anything else to try again: ").lower() == 'exit':
                    break
                else:
                    continue
            else:
                cities = countries[country_choice - 1]['cities']
                print("List of Cities:")
                for i, city in enumerate(cities, 1):
                    print(f"{i}. {city}")
                
                city_choice = int(input("Enter the number of a city: "))
                if city_choice < 1 or city_choice > len(cities):
                    print("Invalid choice. Please enter a valid number.")
                else:
                    city_name = cities[city_choice - 1]
                    data = get_city_weather(city_name, api_key)

                    if data.get('cod') == 200:
                        print("🦜 Weather Data:")
                        print(json.dumps(data, indent=4))

                        # Assuming data is the weather JSON:
                        flattened = flatten_data(data)

                        # Save flattened data directly to Excel
                        append_to_excel(city_name, flattened)

                        # Plotting the weather data
                        plot_weather_data(city_name, data)
                    else:
                        print(f"Failed to fetch city data for {city_name}.")
                        print(f"Status Code: {data.get('cod')}")
                        print(data.get('message', 'No additional message.'))
        except ValueError:
            print("Invalid input. Please enter a valid number or 'exit'.")

if __name__ == "__main__":
    main()
