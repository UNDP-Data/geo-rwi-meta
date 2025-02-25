import os
import pandas as pd
import mercantile
import geopandas as gpd
from shapely.geometry import Polygon
from pathlib import Path
import subprocess

def quadkey_to_polygon(quadkey):
    """
    Converts a quadkey into a polygon using its tile boundaries.
    """
    tile = mercantile.quadkey_to_tile(str(quadkey))  # Convert quadkey to tile
    bounds = mercantile.bounds(tile)  # Get tile boundaries (west, south, east, north)
    return Polygon([
        (bounds.west, bounds.south),  # Bottom-left
        (bounds.west, bounds.north),  # Top-left
        (bounds.east, bounds.north),  # Top-right
        (bounds.east, bounds.south),  # Bottom-right
        (bounds.west, bounds.south)   # Close the polygon
    ])

def rwi2fgb(csv_file: str, output_file: str):
    """
    Converts a CSV file containing quadkeys into a FlatGeobuf (FGB) file.
    Each quadkey is transformed into a polygon and stored in the output FGB file.
    """
    df = pd.read_csv(csv_file, dtype={"quadkey": str})  # Ensure quadkeys are treated as strings

    if df.empty:
        print(f"Skipping {csv_file}: empty file")
        return

    # Generate polygons from quadkeys
    df["geometry"] = df["quadkey"].apply(quadkey_to_polygon)

    # Add a new column storing the original CSV filename
    source_filename = Path(csv_file).name
    df["source"] = source_filename

    # Convert to a GeoDataFrame with EPSG:4326 (WGS84) projection
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    # Ensure the output directory exists
    output_folder = os.path.dirname(output_file)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the data as a FlatGeobuf file
    gdf.to_file(output_file, driver="FlatGeobuf")
    print(f"FGB created: {output_file}")

def process_csv_to_fgb(input_dir: str, output_dir: str):
    """
    Processes all CSV files in the given input directory and converts them into FlatGeobuf (FGB) files.
    Each CSV file is converted separately.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    folder_path = Path(input_dir)
    csv_files = list(folder_path.glob("*.csv"))

    # Process each CSV file and convert it to FGB
    for csv_file in csv_files:
        output_file = f"{output_dir}{csv_file.name.replace('.csv', '.fgb')}"
        rwi2fgb(csv_file, output_file)

def merge_fgb_with_ogr2ogr(output_dir: str, merged_fgb: str, layer_name: str):
    """
    Merges all FlatGeobuf (FGB) files in the specified directory into a single FGB file using `ogr2ogr`.
    """
    fgb_files = list(Path(output_dir).glob("*.fgb"))

    if not fgb_files:
        print("No FGB files found. Skipping merge process.")
        return

    # Create the initial merged FGB file with the first dataset
    first_fgb = str(fgb_files[0])
    merge_command = [
        "ogr2ogr", "-f", "FlatGeobuf", merged_fgb, first_fgb, "-nln", layer_name
    ]
    subprocess.run(merge_command, check=True)
    print(f"Created initial merged FGB: {merged_fgb}")

    # Append remaining FGB files to the merged file
    for fgb_file in fgb_files[1:]:
        append_command = [
            "ogr2ogr", "-f", "FlatGeobuf", "-update", "-append",
            merged_fgb, str(fgb_file), "-nln", layer_name, "-skipfailures"
        ]
        subprocess.run(append_command, check=True)
        print(f"Appended {fgb_file}")

if __name__ == '__main__':
    # Convert all CSV files in the input directory to FlatGeobuf format
    input_dir = "./data/relative-wealth-index-april-2021/"
    output_dir = "./data/output_fgb/"
    # process_csv_to_fgb(input_dir, output_dir)

    # Merge all generated FGB files into a single FlatGeobuf file
    merged_fgb = "./data/relative_wealth_index.fgb"
    merge_fgb_with_ogr2ogr(output_dir, merged_fgb, 'relative_wealth_index')

    # Example of processing a single file manually (commented out)
    # input_dir = './data/relative-wealth-index-april-2021/LCA_relative_wealth_index.csv'
    # output_dir = './data/output_fgb/LCA_relative_wealth_index.fgb'
    # rwi2fgb(input_dir, output_dir)
