import xml.etree.ElementTree as ET
from datetime import datetime

def parse_pos_file(pos_file):
    """
    Parse .pos file to extract GPS data points (latitude, longitude, timestamp).
    Returns a list of tuples (timestamp, lat, lon).
    """
    pos_data = []
    with open(pos_file, 'r') as f:
        for line in f:
            parts = line.split()  # Assuming the .pos file is space-separated
            timestamp = parts[0]  # Assuming the timestamp is the first element
            lat = float(parts[1])
            lon = float(parts[2])
            pos_data.append((timestamp, lat, lon))
    return pos_data

def parse_kml_file(kml_file):
    """
    Parse .kml file to extract GPS data points (latitude, longitude, timestamp).
    Returns a list of tuples (timestamp, lat, lon).
    """
    kml_data = []
    tree = ET.parse(kml_file)
    root = tree.getroot()

    # Extract all <trkpt> elements that represent track points in KML
    for trkpt in root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt'):
        lat = float(trkpt.attrib['lat'])
        lon = float(trkpt.attrib['lon'])
        time = trkpt.find('{http://www.topografix.com/GPX/1/1}time').text
        kml_data.append((time, lat, lon))
    return kml_data

def merge_data(pos_data, kml_data):
    """
    Merge data from .pos and .kml files by timestamp.
    Returns a list of tuples sorted by timestamp.
    """
    merged_data = pos_data + kml_data
    merged_data.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%S.%f"))  # Adjust format if necessary
    return merged_data

def create_gpx(merged_data, output_file):
    """
    Create a .gpx file from the merged data (timestamp, lat, lon).
    """
    gpx = ET.Element('gpx', version="1.1", creator="Merged GPX")

    trk = ET.SubElement(gpx, 'trk')
    trkseg = ET.SubElement(trk, 'trkseg')

    for timestamp, lat, lon in merged_data:
        trkpt = ET.SubElement(trkseg, 'trkpt', lat=str(lat), lon=str(lon))
        time = ET.SubElement(trkpt, 'time')
        time.text = timestamp

    tree = ET.ElementTree(gpx)
    tree.write(output_file)

    print(f"GPX file created: {output_file}")

# Main function to merge the .pos and .kml files and create a .gpx file
def merge_pos_kml_to_gpx(pos_file, kml_file, output_file):
    pos_data = parse_pos_file(pos_file)
    kml_data = parse_kml_file(kml_file)
    merged_data = merge_data(pos_data, kml_data)
    create_gpx(merged_data, output_file)

# Example usage:
pos_file = "/mnt/data/Dataset1 (1).pos"  # Replace with the actual .pos file path
kml_file = "/mnt/data/Dataset1 (1).kml"  # Replace with the actual .kml file path
output_file = "/mnt/data/merged_trajectory.gpx"  # Replace with the desired output .gpx file path

# Merge .pos and .kml and create .gpx
merge_pos_kml_to_gpx(pos_file, kml_file, output_file)
