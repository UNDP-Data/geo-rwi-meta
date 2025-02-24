import os
import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import from_origin
import mercantile
from pathlib import Path

# 📌 Function to convert a quadkey into x, y tile coordinates
def quadkey_to_tile(quadkey, zoom_level: int = 14):
    """
    Converts a quadkey into x, y tile coordinates at a given zoom level.
    Ensures that the quadkey is treated as a string and zero-padded for consistency.
    """
    tile = mercantile.quadkey_to_tile(str(quadkey).zfill(zoom_level))
    return tile.x, tile.y

# 📌 Process data and create a raster (GeoTIFF)
def rwi2tiff(csv_file: str, output_file: str, zoom_level: int = 14):
    """
    Converts a CSV file containing quadkeys and RWI values into a raster (GeoTIFF).
    The RWI values are mapped to a grid based on their corresponding tiles.

    Parameters:
    - csv_file: Path to the input CSV file.
    - output_file: Path to the output GeoTIFF file.
    - zoom_level: Zoom level for Mercator tile calculations (default is 14).
    """
    df = pd.read_csv(csv_file)

    if df.empty:
        print(f"Skipping {csv_file}: empty file")
        return

    # Convert quadkey to x, y tile coordinates
    df["x"], df["y"] = zip(*df["quadkey"].apply(lambda qk: quadkey_to_tile(qk, zoom_level)))

    # Determine the bounding range of X and Y tiles
    min_x, max_x = df["x"].min(), df["x"].max()
    min_y, max_y = df["y"].min(), df["y"].max()

    # 🌍 Generate a list of longitude and latitude values from tile boundaries
    lons = [mercantile.ul(x, min_y, zoom_level).lng for x in range(min_x, max_x + 2)]
    lats = [mercantile.ul(min_x, y, zoom_level).lat for y in range(min_y, max_y + 2)]
    lats.reverse()  # Reverse the list to match the raster's row order

    # Compute the number of rows and columns in the raster
    cols = len(lons) - 1
    rows = len(lats) - 1

    # Create an empty raster filled with NaN values
    raster = np.full((rows, cols), np.nan, dtype=np.float32)

    # 📌 Convert x, y tile coordinates to raster indices and assign RWI values
    for _, row in df.iterrows():
        # Convert x and y tile coordinates to integer indices
        col = int(row["x"]) - min_x
        row_idx = int(max_y - row["y"])

        # Ensure indices are within valid raster bounds
        col = max(0, min(cols - 1, col))
        row_idx = max(0, min(rows - 1, row_idx))

        # Assign the RWI value to the raster cell
        raster[row_idx, col] = row["rwi"]

    # 🌍 Define the GeoTIFF transformation matrix (origin at the top-left)
    transform = from_origin(lons[0], lats[0], lons[1] - lons[0], lats[0] - lats[1])

    # 🚀 Save the raster as a GeoTIFF file
    with rasterio.open(
            output_file,
            "w",
            driver="GTiff",
            height=rows,
            width=cols,
            count=1,
            dtype=raster.dtype,
            crs="EPSG:4326",
            transform=transform,
    ) as dst:
        dst.write(raster, 1)

    print(f"{output_file} was generated.")

def process_csv_files(input_dir: str, output_dir: str):
    """
    Processes all CSV files in the given input directory and converts them into raster (GeoTIFF) format.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    folder_path = Path(input_dir)
    csv_files = list(folder_path.glob("*.csv"))

    # Process each CSV file and convert it to GeoTIFF
    for csv_file in csv_files:
        output_file = f"{output_dir}{csv_file.name.replace('.csv', '.tif')}"
        rwi2tiff(csv_file, output_file)

if __name__ == '__main__':
    # Define input directory (CSV) and output directory (GeoTIFF)
    input_dir = './data/relative-wealth-index-april-2021/'
    output_dir = './data/output_tiff/'
    process_csv_files(input_dir, output_dir)

    # Example of processing a single file manually (commented out)
    # input_dir = './data/relative-wealth-index-april-2021/LCA_relative_wealth_index.csv'
    # output_dir = './data/output/LCA_relative_wealth_index.tif'

    # input_dir = './data/relative-wealth-index-april-2021/ETH_relative_wealth_index.csv'
    # output_dir = './data/output/ETH_relative_wealth_index.tif'
    # rwi2tiff(input_dir, output_dir)
