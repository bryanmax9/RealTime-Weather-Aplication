import subprocess
import sys
import requests
import json

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
    necessary_packages = ['requests']

    install_packages(necessary_packages)
    
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
                        
                        # Create and open a text file for writing
                        with open(f"{city_name}_weather.txt", "w") as file:
                            file.write(json.dumps(data, indent=4))
                    else:
                        print(f"Failed to fetch city data for {city_name}.")
                        print(f"Status Code: {data.get('cod')}")
                        print(data.get('message', 'No additional message.'))
        except ValueError:
            print("Invalid input. Please enter a valid number or 'exit'.")

if __name__ == "__main__":
    main()
