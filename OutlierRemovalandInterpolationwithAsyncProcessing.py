import asyncio
import xml.etree.ElementTree as ET
from geopy.distance import geodesic

async def remove_outliers_async(gpx_file, threshold_km=0.1):
    """
    Remove outliers from the GPX file asynchronously.
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
    
    trkseg = root.find(".//trkseg")
    for trkpt in trkseg.findall("trkpt"):
        trkseg.remove(trkpt)

    for trkpt in valid_trkpts:
        trkseg.append(trkpt)

    tree.write(f"cleaned_{gpx_file}")
    print(f"Outliers removed from {gpx_file} and saved as cleaned_{gpx_file}")

async def interpolate_gpx_async(gpx_file):
    """
    Interpolate missing points in the GPX file asynchronously.
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

    interpolated_points = []
    for i in range(1, len(points)):
        point1 = points[i-1]
        point2 = points[i]

        interpolated_points.append(point1)
        lat1, lon1, time1 = point1
        lat2, lon2, time2 = point2
        interpolated_points.append((lat2, lon2, time2))

    trkseg.clear()
    for lat, lon, timestamp in interpolated_points:
        trkpt = ET.SubElement(trkseg, "trkpt", lat=str(lat), lon=str(lon))
        time = ET.SubElement(trkpt, "time")
        time.text = timestamp

    tree.write(f"interpolated_{gpx_file}")
    print(f"Interpolation completed for {gpx_file}. Saved as interpolated_{gpx_file}")

async def process_gpx_file_async(input_gpx_file):
    """
    Complete preprocessing workflow: outlier removal and interpolation.
    """
    await remove_outliers_async(input_gpx_file)
    await interpolate_gpx_async(f"cleaned_{input_gpx_file}")

async def process_directory_async(directory):
    """
    Process all GPX files in the directory and subdirectories for preprocessing.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.gpx'):
                input_gpx_file = os.path.join(root, file)
                await process_gpx_file_async(input_gpx_file)

# Running async processing for a directory
directory = "path_to_your_directory_with_gpx_files"  # Change this to your directory path
asyncio.run(process_directory_async(directory))
