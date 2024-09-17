import json
import requests
from datetime import datetime, time
import os


def fetch_all_tube_stations(api_key):
    url = "https://api.tfl.gov.uk/StopPoint/Mode/tube"
    params = {"app_key": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching tube stations: {response.status_code}")
        return None


def create_station_naptan_mapping(stations_data):
    mapping = {}
    for station in stations_data.get('stopPoints', []):
        mapping[station['commonName']] = station['naptanId']
    return mapping


def fetch_crowding_data(api_key, naptan, day_of_week):
    url = f"https://api.tfl.gov.uk/Crowding/{naptan}/{day_of_week}"
    params = {"app_key": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"No crowding data available for NAPTAN {naptan} on {day_of_week}")
        return None
    else:
        print(f"Error fetching data for NAPTAN {naptan}: {response.status_code}")
        print(f"Response content: {response.text}")
        return None


def calculate_crowding_score(crowding_data):
    if crowding_data and 'timeBands' in crowding_data:
        am_peak = crowding_data.get('amPeakTimeBand', '08:00-10:00').split('-')
        pm_peak = crowding_data.get('pmPeakTimeBand', '17:00-19:00').split('-')

        am_start, am_end = [time.fromisoformat(t) for t in am_peak]
        pm_start, pm_end = [time.fromisoformat(t) for t in pm_peak]

        peak_crowding = 0
        for band in crowding_data['timeBands']:
            band_time = time.fromisoformat(band['timeBand'].split('-')[0])
            if (am_start <= band_time < am_end) or (pm_start <= band_time < pm_end):
                peak_crowding = max(peak_crowding, band['percentageOfBaseLine'])

        # Normalize to 1-10 scale
        crowding_score = min(max(int(peak_crowding * 10) + 1, 1), 10)

        return crowding_score
    return 5  # Default value if data structure is unexpected


def process_day(api_key, station_data, station_naptan_mapping, day_of_week):
    for station, connections in station_data.items():
        print(f"\nProcessing station: {station}")
        naptan = station_naptan_mapping.get(station)
        if naptan:
            print(f"NAPTAN code: {naptan}")
            crowding_data = fetch_crowding_data(api_key, naptan, day_of_week)
            if crowding_data:
                crowding_score = calculate_crowding_score(crowding_data)
                print(f"Calculated peak crowding score: {crowding_score}")

                for connected_station, details in connections.items():
                    if isinstance(details, dict):
                        details["crowding"] = crowding_score
                    else:
                        connections[connected_station] = {
                            "line": details,
                            "crowding": crowding_score
                        }
            else:
                print(f"No crowding data available for {station}")
        else:
            print(f"NAPTAN code not found for station: {station}")
    return station_data


def main():
    api_key = "fc3e9979b74244669ca0e274e93f0708"
    days_of_week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Create a directory to store the datasets if it doesn't exist
    output_dir = "london_tube_crowding_data"
    os.makedirs(output_dir, exist_ok=True)

    # Fetch all tube stations and create NAPTAN mapping
    all_stations = fetch_all_tube_stations(api_key)
    station_naptan_mapping = create_station_naptan_mapping(all_stations)

    # Load your existing station data
    with open('london_tube_with_real_crowding.json', 'r') as f:
        initial_station_data = json.load(f)

    for day in days_of_week:
        print(f"\nProcessing data for {day}")

        # Create a deep copy of the initial data for each day
        station_data = json.loads(json.dumps(initial_station_data))

        # Process the day's data
        updated_data = process_day(api_key, station_data, station_naptan_mapping, day)

        # Save the updated data for the day
        output_file = os.path.join(output_dir, f'london_tube_crowding_{day.lower()}.json')
        with open(output_file, 'w') as f:
            json.dump(updated_data, f, indent=2)

        print(f"Updated dataset for {day} has been saved to '{output_file}'")

    print("\nAll datasets have been processed and saved.")


if __name__ == "__main__":
    main()
