import os
import subprocess
import json
from pathlib import Path
from pyproj import Geod


# Constant: Earth Circumference in Meters
EARTH_CIRCUMFERENCE = 40075016.6855784  # meters


def get_meters_per_degree_lat(lat: float = 0) -> float:
    geod = Geod(ellps="WGS84")
    _, _, distance = geod.inv(0, lat, 0, lat + 1)
    return distance

def calculate_pixel_size(zoom_level: int = 14, lat: float = 0):
    """
    Calculates the approximate pixel size in degrees for a given zoom level.
    Uses Web Mercator tile size and converts to WGS84 degrees.

    Returns:
    - Pixel size in degrees (for EPSG:4326)
    """
    tile_size_meters = EARTH_CIRCUMFERENCE / (2 ** zoom_level)
    pixel_size_meters = tile_size_meters / 256
    meters_per_degree = get_meters_per_degree_lat(lat)

    pixel_size_degrees = pixel_size_meters / meters_per_degree  # Convert meters to degrees
    return pixel_size_degrees


def get_fgb_extent(input_fgb: str):
    """
    Uses `ogrinfo` to get the bounding box (extent) of an FGB file.

    Returns:
    - min_x, min_y, max_x, max_y (bounding box in EPSG:4326)
    """
    command = ["ogrinfo", "-al", "-json", input_fgb]
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    data = json.loads(result.stdout)
    # Extract extent correctly from the first layer
    try:
        extent = data["layers"][0]["geometryFields"][0]["extent"]
        min_x, max_x = extent[0], extent[2]  # Longitude (West, East)
        min_y, max_y = extent[1], extent[3]  # Latitude (South, North)
        return min_x, min_y, max_x, max_y
    except (KeyError, IndexError) as e:
        print(f"Error extracting extent from {input_fgb}: {e}")
        return None


def rasterize_to_tiff(input_fgb: str, temp_tiff: str, zoom_level: int = 14):
    """
    Rasterizes an FGB file into a temporary TIFF using `gdal_rasterize`.

    Parameters:
    - input_fgb: Path to the input FGB file.
    - temp_tiff: Path to the output temporary raster file (GeoTIFF).
    - zoom_level: The zoom level to calculate pixel resolution (default: 14).
    """
    # Get the bounding box of the FGB file
    extent = get_fgb_extent(input_fgb)
    if extent is None:
        print(f"Skipping {input_fgb}: Could not determine extent.")
        return False

    min_x, min_y, max_x, max_y = extent

    # Calculate pixel size from zoom level
    pixel_size = calculate_pixel_size(zoom_level, lat=(min_y + max_y) / 2)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(temp_tiff), exist_ok=True)

    # Construct gdal_rasterize command
    command = [
        "gdal_rasterize",
        "-a", "rwi",  # Attribute field to burn into raster
        "-tr", str(pixel_size), str(pixel_size),  # Automatically set pixel size
        "-te", str(min_x), str(min_y), str(max_x), str(max_y),  # Set bounding box
        "-ot", "Float32",  # Output type
        "-a_nodata", "-9999",
        "-co", "COMPRESS=ZSTD",
        "-co", "BIGTIFF=YES",
        input_fgb, temp_tiff  # Input and Output files
    ]

    # Run the command
    subprocess.run(command, check=True)

    print(f"Rasterized TIFF created: {temp_tiff}")


def process_csv_files(input_dir: str, output_dir: str, zoom_level: int = 14):
    """
    Processes all CSV files in the given input directory and converts them into raster (GeoTIFF) format.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    folder_path = Path(input_dir)
    files = sorted(folder_path.glob("*.fgb"))

    # Process each FGB file and convert it to GeoTIFF
    for file in files:
        output_tiff = f"{output_dir}{file.name.replace('.fgb', '.tif')}"
        rasterize_to_tiff(str(file), output_tiff, zoom_level)


if __name__ == '__main__':
    # Define input directory (CSV) and output directory (GeoTIFF)
    input_dir = './data/output_fgb/'
    output_dir = './data/output_tiff_z11/'
    process_csv_files(input_dir, output_dir, zoom_level=10)

    # Example of processing a single file manually (commented out)
    # input_fgb = './data/relative_wealth_index.fgb'
    # output_cog = './data/relative_wealth_index.tif'
    # temp_tiff = './data/relative_wealth_index_temp.tif'

    # input_fgb = './data/output_fgb/albania_relative_wealth_index.fgb'
    # output_cog = './data/output_tiff/albania_relative_wealth_index.tif'
    # temp_tiff = './data/output_tiff/albania_relative_wealth_index_temp.tif'
    # rasterize_to_tiff(input_fgb, temp_tiff, zoom_level=10)
