import json
from datetime import datetime
from urllib.parse import urlencode

from customchromedriver import CustomChromeDriver
from selenium.webdriver.common.by import By


def get_temperature_by_date(date_str, latitude=35.6895, longitude=139.6917):
    """Fetch daily minimum and maximum temperature for a given date.

    Parameters
    ----------
    date_str : str
        Date in ``YYYY-MM-DD`` format.
    latitude : float, optional
        Latitude of the location. Defaults to Tokyo.
    longitude : float, optional
        Longitude of the location. Defaults to Tokyo.

    Returns
    -------
    tuple of (float, float)
        Minimum and maximum temperature in Celsius.
    """

    # Validate the date string
    date = datetime.strptime(date_str, "%Y-%m-%d").date()

    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date.isoformat(),
        "end_date": date.isoformat(),
        "daily": "temperature_2m_min,temperature_2m_max",
        "timezone": "Asia/Tokyo",
    }

    url = f"{base_url}?{urlencode(params)}"

    driver = CustomChromeDriver(headless=True)
    try:
        driver.get(url)
        json_text = driver.find_element(By.TAG_NAME, "pre").text
    finally:
        driver.quit()

    data = json.loads(json_text)
    try:
        min_temp = data["daily"]["temperature_2m_min"][0]
        max_temp = data["daily"]["temperature_2m_max"][0]
    except (KeyError, IndexError) as e:
        raise ValueError("Temperature data not available for the given date") from e

    return min_temp, max_temp


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch temperature for a given date")
    parser.add_argument("date", help="Date in YYYY-MM-DD format")
    parser.add_argument("--latitude", type=float, default=35.6895, help="Latitude")
    parser.add_argument("--longitude", type=float, default=139.6917, help="Longitude")

    args = parser.parse_args()
    min_temp, max_temp = get_temperature_by_date(args.date, args.latitude, args.longitude)
    print(f"{args.date}: min={min_temp}°C, max={max_temp}°C")
