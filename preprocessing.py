// This file will handle the preprocessing steps: speed calculation, outlier removal, and interpolation.

import geopy.distance
import numpy as np
import xml.etree.ElementTree as ET
from datetime import datetime
from scipy.interpolate import interp1d

def calculate_speed_and_interpolate(gpx_file, speed_threshold=150, interpolate=True):
    """
    Calculate speed, remove outliers, and interpolate the GPS data if necessary.
    Args:
        gpx_file (str): Path to the input GPX file.
        speed_threshold (float): Threshold to filter outliers based on speed.
        interpolate (bool): Whether to interpolate missing GPS points.

    Returns:
        list: Filtered and interpolated GPS data points (lat, lon, timestamp).
    """
    # Parse GPX file
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    latitudes = []
    longitudes = []
    timestamps = []
    speeds = []
    prev_point = None
    prev_time = None

    # Collect data points and calculate speeds
    for trkpt in root.findall(".//trkpt"):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        time_str = trkpt.find(".//time").text
        time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")

        latitudes.append(lat)
        longitudes.append(lon)
        timestamps.append(time_obj)

        if prev_point is not None:
            dist = geopy.distance.distance((lat, lon), prev_point).meters
            time_diff = (time_obj - prev_time).total_seconds()
            if time_diff > 0:
                speed = dist / time_diff * 3.6  # km/h
                speeds.append(speed)

        prev_point = (lat, lon)
        prev_time = time_obj

    # Remove outliers based on speed threshold
    speeds = [speed for speed in speeds if speed <= speed_threshold]

    # Interpolation if necessary
    if interpolate:
        time_seconds = np.array([(time_obj - timestamps[0]).total_seconds() for time_obj in timestamps])
        interp_lat = interp1d(time_seconds, latitudes, kind='linear', fill_value="extrapolate")
        interp_lon = interp1d(time_seconds, longitudes, kind='linear', fill_value="extrapolate")
        interpolated_lats = interp_lat(time_seconds)
        interpolated_lons = interp_lon(time_seconds)

        # Modify original GPX data with interpolated values
        for i, trkpt in enumerate(root.findall(".//trkpt")):
            trkpt.attrib['lat'] = str(interpolated_lats[i])
            trkpt.attrib['lon'] = str(interpolated_lons[i])
            trkpt.find(".//time").text = timestamps[i].strftime("%Y-%m-%dT%H:%M:%SZ")

        # Save interpolated GPX file
        tree.write("interpolated_trajectory.gpx")
        print("Interpolation completed and saved to interpolated_trajectory.gpx")
    
    return "interpolated_trajectory.gpx"
