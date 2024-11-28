from xml.etree import ElementTree as ET

def kml_to_gpx(kml_file, gpx_file):
    """
    Convert a .kml file to .gpx format.
    kml_file: Path to the input .kml file
    gpx_file: Path where the .gpx file will be saved
    """
    # Parse the KML file
    tree = ET.parse(kml_file)
    root = tree.getroot()

    # Create the root of the GPX XML file
    gpx = ET.Element("gpx", version="1.1", creator="My GPS Converter")

    # Create a track (trk) and track segment (trkseg)
    trk = ET.SubElement(gpx, "trk")
    trkname = ET.SubElement(trk, "name")
    trkname.text = "GPS Track"
    trkseg = ET.SubElement(trk, "trkseg")

    # Iterate through each <Placemark> in the KML file
    for placemark in root.iter('Placemark'):
        # Get coordinates from <coordinates> tag
        coords = placemark.find('.//coordinates')
        if coords is not None:
            coord_list = coords.text.strip().split()

            for coord in coord_list:
                lon, lat, _ = coord.split(',')

                # Create a track point (trkpt)
                trkpt = ET.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
                # Add timestamp if available (optional)
                time = ET.SubElement(trkpt, "time")
                time.text = "2024-01-01T00:00:00Z"  # Example timestamp, replace with real timestamp if available

    # Write the GPX XML tree to the output file
    tree = ET.ElementTree(gpx)
    tree.write(gpx_file, encoding="UTF-8", xml_declaration=True)

    print(f"Converted {kml_file} to {gpx_file}")

# Example usage:
kml_file = "/path/to/your/file.kml"
gpx_file = "/path/to/your/output.gpx"
kml_to_gpx(kml_file, gpx_file)
