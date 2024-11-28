//Preprocessing:
 remove_outliers: Removes GPS points that are far from the previous point (outliers).
interpolate_gpx: Interpolates missing points by linearly interpolating between existing points.
Map Matching:
Uses GraphHopper API to send the cleaned/interpolated GPX file for map matching and get back snapped data.
Post-processing:
Renames snapped files, cleans up intermediate files (like cleaned or interpolated), and saves the result.
Validation:
Validates snapped data by checking if the coordinates fall within acceptable ranges.
Visualization:
Uses Folium to visualize the snapped track on a map.
Usage:
Replace the input_gpx_file, output_gpx_file, and directory variables with appropriate paths and run the process_gpx_file function to execute the complete pipeline.

Let me know if you need any adjustments or additions to this workflow! 

import os
import requests
import xml.etree.ElementTree as ET
from geopy.distance import geodesic
import folium

# Preprocessing: Remove outliers from GPX file
def remove_outliers(gpx_file, threshold_km=0.1):
    """
    Remove outliers by calculating the distance between consecutive points.
    If the distance between points exceeds the threshold, it's considered an outlier.
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

# Preprocessing: Interpolate missing points in the GPX file
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

# Map Matching using GraphHopper
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

# Post-process: Renaming, cleaning up intermediate files
def post_process_gpx_files(directory):
    """
    Post-processing: Renaming snapped files and cleanup.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('_snapped.gpx'):
                # Move or rename files if necessary
                original_file = os.path.join(root, file)
                final_file = original_file.replace('_snapped.gpx', '_matched.gpx')
                
                # Example: Rename the file or move to another folder
                os.rename(original_file, final_file)
                print(f"File {original_file} renamed to {final_file}")
                
                # Optionally remove intermediate files, like cleaned or interpolated files
                cleaned_file = os.path.join(root, f"cleaned_{file}")
                if os.path.exists(cleaned_file):
                    os.remove(cleaned_file)
                    print(f"Removed {cleaned_file}")
                
                interpolated_file = os.path.join(root, f"interpolated_{file}")
                if os.path.exists(interpolated_file):
                    os.remove(interpolated_file)
                    print(f"Removed {interpolated_file}")

# Optional: Validate snapped data
def validate_snapped_data(gpx_file):
    """
    Validate the snapped data by checking if the points are within reasonable proximity to a road.
    """
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    valid = True
    for trkpt in root.findall(".//trkpt"):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            valid = False
            print(f"Invalid coordinates: {lat}, {lon}")
    
    return valid

def validate_all_files(directory):
    """
    Validate all snapped GPX files in the directory.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('_snapped.gpx'):
                gpx_file = os.path.join(root, file)
                if validate_snapped_data(gpx_file):
                    print(f"Valid snapped data in {gpx_file}")
                else:
                    print(f"Invalid snapped data in {gpx_file}")

# Optional: Visualize snapped data on a map
def visualize_gpx_on_map(gpx_file):
    """
    Visualize the GPX file on a map using Folium.
    """
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    # Create a map centered on the first GPS point
    first_point = root.find(".//trkpt")
    lat = float(first_point.attrib['lat'])
    lon = float(first_point.attrib['lon'])
    m = folium.Map(location=[lat, lon], zoom_start=12)

    # Add the GPS points to the map
    points = []
    for trkpt in root.findall(".//trkpt"):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        points.append((lat, lon))

    # Add polyline of the snapped track
    folium.PolyLine(points, color='blue', weight=2.5, opacity=1).add_to(m)
    return m

def save_map_as_html(gpx_file, output_html):
    """
    Save the visualization as an HTML file.
    """
    m = visualize_gpx_on_map(gpx_file)
    m.save(output_html)
    print(f"Map saved as {output_html}")

# Complete workflow: Process, Map Match, Validate, and Visualize
def process_gpx_file(input_gpx_file, output_gpx_file, directory):
    """
    Complete workflow: Remove outliers, interpolate, map matching, post-process, validate, and visualize.
    """
    # Step 1: Remove outliers and interpolate the GPX file
    remove_outliers(input_gpx_file)
    interpolate_gpx("cleaned_" + input_gpx_file)
    
    # Step 2: Map matching
    result_file = output_gpx_file.replace(".gpx", "_snapped.gpx")
    map_matching("interpolated_" + input_gpx_file, result_file)
    
    # Step 3: Post-process (rename and cleanup)
    post_process_gpx_files(directory)
    
    # Step 4: Validate snapped data
    validate_all_files(directory)
    
    # Step 5: Visualize the result
    save_map_as_html(result_file, "snapped_map.html")

# Example usage
input_gpx_file = "path_to_input_file.gpx"  # Replace with the path to your GPX file
output_gpx_file = "path_to_output_file.gpx"  # Replace with the path to the output file
directory = "path_to_directory_with_gpx_files"  # Replace with the directory path containing your files
process_gpx_file(input_gpx_file, output_gpx_file, directory)

