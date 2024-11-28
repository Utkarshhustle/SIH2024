// This file will handle the preprocessing steps: speed calculation, outlier removal, and interpolation.

import xml.etree.ElementTree as ET
from geopy.distance import geodesic

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


def process_gpx_file(input_gpx_file):
    """
    Complete preprocessing workflow: outlier removal and interpolation.
    """
    # Step 1: Remove outliers
    remove_outliers(input_gpx_file)

    # Step 2: Interpolate missing points
    interpolate_gpx("cleaned_" + input_gpx_file)


# Example usage
input_gpx_file = "merged_trajectory.gpx"  # Path to the merged GPX file
process_gpx_file(input_gpx_file)
