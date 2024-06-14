import requests
import argparse
import os
from pathlib import Path

outputs_path = Path(os.environ["GITHUB_OUTPUT"])


def set_gha_output(name, value):
    """Set an action output using an environment file.

    Refs:
    * https://hynek.me/til/set-output-deprecation-github-actions/
    * https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter
    """
    with open(outputs_path, "a") as outputs_file:
        print(f"{name}={value}", file=outputs_file)


def get_weather(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # Use "imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad responses

        weather_data = response.json()
        if weather_data["cod"] != 200:
            return "Error: {}".format(weather_data["message"])

        weather_main = weather_data["weather"][0]["main"]
        temp = weather_data["main"]["temp"]
        temp_min = weather_data["main"]["temp_min"]
        temp_max = weather_data["main"]["temp_max"]

        return {
            "weather": weather_main,
            "temperature": temp,
            "min_temperature": temp_min,
            "max_temperature": temp_max,
        }

    except requests.exceptions.RequestException as e:
        return "Error fetching data: {}".format(e)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch weather details for a city")
    parser.add_argument("--city", type=str, required=True,
                        help="Name of the city")
    parser.add_argument(
        "--api_key", type=str, required=True, help="API key for OpenWeatherMap"
    )

    args = parser.parse_args()

    weather = get_weather(args.city, args.api_key)
    if isinstance(weather, dict):
        print("Weather in {}: {}".format(args.city, weather))
        set_gha_output("result", weather)
    else:
        print(weather)
        set_gha_output("result", "failure")


if __name__ == "__main__":
    main()
