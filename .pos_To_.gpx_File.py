//timestamp,latitude,longitude,elevation
import xml.etree.ElementTree as ET
from datetime import datetime

def pos_to_gpx(pos_file, gpx_file):
    """
    Convert a .pos file to .gpx format.
    pos_file: Path to the input .pos file
    gpx_file: Path where the .gpx file will be saved
    """
    # Create the root of the GPX XML file
    gpx = ET.Element("gpx", version="1.1", creator="My GPS Converter")

    # Create a track (trk) and track segment (trkseg)
    trk = ET.SubElement(gpx, "trk")
    trkname = ET.SubElement(trk, "name")
    trkname.text = "GPS Track"
    trkseg = ET.SubElement(trk, "trkseg")

    # Read the .pos file and convert data to GPX format
    with open(pos_file, 'r') as file:
        for line in file:
            # Split each line by commas and parse the values
            data = line.strip().split(',')
            timestamp_str, lat, lon, _ = data

            # Convert the timestamp to a datetime object
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

            # Create a track point (trkpt) with lat, lon, and timestamp
            trkpt = ET.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
            time = ET.SubElement(trkpt, "time")
            time.text = timestamp.isoformat()

    # Write the GPX XML tree to the output file
    tree = ET.ElementTree(gpx)
    tree.write(gpx_file, encoding="UTF-8", xml_declaration=True)

    print(f"Converted {pos_file} to {gpx_file}")

# Example usage:
pos_file = "/path/to/your/file.pos"
gpx_file = "/path/to/your/output.gpx"
pos_to_gpx(pos_file, gpx_file)
