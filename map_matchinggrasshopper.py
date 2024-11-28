import requests
import xml.etree.ElementTree as ET

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


def main(input_gpx_file, output_gpx_file):
    """
    Complete workflow: Map matching using GraphHopper.
    """
    # Step 1: Map Matching using GraphHopper
    result_file = output_gpx_file.replace(".gpx", "_snapped.gpx")
    map_matching(input_gpx_file, result_file)


# Example usage
input_gpx_file = "interpolated_trajectory.gpx"  # Path to the interpolated GPX file
output_gpx_file = "final_snapped_trajectory.gpx"  # Path for the final output

main(input_gpx_file, output_gpx_file)
