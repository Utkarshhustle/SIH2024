import os
import requests
import xml.etree.ElementTree as ET
from geopy.distance import geodesic
from datetime import datetime

# 1. Map Matching using GraphHopper API
def map_matching(gpx_file, result_file, vehicle='car'):
    """
    Send GPX file to GraphHopper for map matching and get back snapped data.
    """
    url = 'http://localhost:8989/match'
    headers = {'Content-Type': 'application/gpx+xml'}
    
    with open(gpx_file, 'rb') as f:
        response = requests.post(url, headers=headers, data=f, params={'vehicle': vehicle, 'type': 'json'})
    
    if response.status_code == 200:
        result_data = response.json()
        with open(result_file, 'w') as result_f:
            # Save the result as a new GPX file
            result_f.write(response.text)
        print(f"Map matching completed for {gpx_file}. Result saved to {result_file}")
    else:
        print(f"Error in map matching for {gpx_file}: {response.text}")


# 2. Detect Outliers (simple distance-based method)
def remove_outliers(gpx_file, threshold_km=0.1):
    """
    Remove outliers by calculating the distance between consecutive points. If the distance
    between points exceeds the threshold, it's considered an outlier.
    """
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    valid_trkpts = []
    prev_point = None

    for trkpt in root.findall(".//trkpt"):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        timestamp = trkpt.find("time").text

        if prev_point:
            distance = geodesic((prev_point['lat'], prev_point['lon']), (lat, lon)).km
            if distance <= threshold_km:
                valid_trkpts.append(trkpt)
        else:
            valid_trkpts.append(trkpt)

        prev_point = {'lat': lat, 'lon': lon, 'timestamp': timestamp}
    
    # Remove all trkpt elements and re-add valid ones
    trkseg = root.find(".//trkseg")
    for trkpt in trkseg.findall("trkpt"):
        trkseg.remove(trkpt)

    for trkpt in valid_trkpts:
        trkseg.append(trkpt)

    # Save the cleaned gpx file
    tree.write("cleaned_" + gpx_file)
    print(f"Outliers removed and saved as cleaned_{gpx_file}")


# 3. Interpolate Missing Points (linear interpolation)
def interpolate_gpx(gpx_file):
    """
    Interpolate missing points in the GPX file to fill gaps between valid points.
    """
    tree = ET.parse(gpx_file)
    root = tree.getroot()
    trkseg = root.find(".//trkseg")

    points = []
    for trkpt in trkseg.findall("trkpt"):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        timestamp = trkpt.find("time").text
        points.append((lat, lon, timestamp))

    # Interpolate between points if there are gaps
    interpolated_points = []
    for i in range(1, len(points)):
        point1 = points[i-1]
        point2 = points[i]

        interpolated_points.append(point1)

        # Linear interpolation between lat, lon and timestamp
        lat1, lon1, time1 = point1
        lat2, lon2, time2 = point2

        # You can add logic for interpolating time here if necessary

        interpolated_points.append((lat2, lon2, time2))

    # Rebuild the GPX file with interpolated points
    trkseg.clear()
    for lat, lon, timestamp in interpolated_points:
        trkpt = ET.SubElement(trkseg, "trkpt", lat=str(lat), lon=str(lon))
        time = ET.SubElement(trkpt, "time")
        time.text = timestamp

    # Save the interpolated GPX file
    tree.write("interpolated_" + gpx_file)
    print(f"Interpolation completed. Saved as interpolated_{gpx_file}")


# 4. Main workflow
def process_gpx_file(input_gpx_file, output_gpx_file):
    """
    Complete workflow: Map matching, outlier removal, and interpolation.
    """
    # Step 1: Map Matching using GraphHopper
    result_file = output_gpx_file.replace(".gpx", "_snapped.gpx")
    map_matching(input_gpx_file, result_file)

    # Step 2: Remove outliers from the snapped GPX file
    remove_outliers(result_file)

    # Step 3: Interpolate missing points in the cleaned GPX file
    interpolate_gpx("cleaned_" + result_file)


# Example usage
input_gpx_file = "merged_trajectory.gpx"  # Path to the merged GPX file
output_gpx_file = "final_snapped_trajectory.gpx"  # Path for the final output

process_gpx_file(input_gpx_file, output_gpx_file)
