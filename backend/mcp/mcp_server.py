def get_weather(city):

    weather_data = {
        "Delhi": "35°C, Sunny",
        "Mumbai": "30°C, Humid",
        "Bangalore": "25°C, Cloudy"
    }

    return weather_data.get(city, "Weather data not available")


if __name__ == "__main__":

    city = "Delhi"

    result = get_weather(city)

    print("Weather Result:", result)