import os
import asyncio
import aiohttp
import xml.etree.ElementTree as ET

async def map_matching_async(gpx_file, result_file, vehicle='car'):
    """
    Asynchronous map matching using GraphHopper.
    """
    url = 'http://localhost:8989/match'
    headers = {'Content-Type': 'application/gpx+xml'}
    
    with open(gpx_file, 'rb') as f:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=f, params={'vehicle': vehicle, 'type': 'json'}) as response:
                if response.status == 200:
                    result_data = await response.json()
                    with open(result_file, 'w') as result_f:
                        result_f.write(response.text)
                    print(f"Map matching completed for {gpx_file}. Result saved to {result_file}")
                else:
                    print(f"Error in map matching for {gpx_file}: {response.text}")

async def process_directory(directory):
    """
    Process all GPS files in the directory and subdirectories for map matching.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.gpx'):
                input_gpx_file = os.path.join(root, file)
                result_file = input_gpx_file.replace(".gpx", "_snapped.gpx")
                await map_matching_async(input_gpx_file, result_file)

# Running the async processing for a directory
directory = "path_to_your_directory_with_gpx_files"  # Change this to your directory path
asyncio.run(process_directory(directory))
