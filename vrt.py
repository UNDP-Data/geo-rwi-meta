import os
import subprocess
from pathlib import Path

def create_vrt(input_dir: str, output_vrt: str):
    """
    Creates a Virtual Raster (VRT) from all .tif files in the specified directory.
    """
    folder_path = Path(input_dir)
    tiff_files = sorted(folder_path.glob("*.tif"))  # Get all .tif files

    if not tiff_files:
        print("No TIFF files found in the directory. Skipping VRT creation.")
        return

    # Convert to a list of string paths
    tiff_list = [str(tiff) for tiff in tiff_files]

    # Construct the gdalbuildvrt command
    command = [
                "gdalbuildvrt",
                "-overwrite",
                output_vrt
              ] + tiff_list

    # Run the command
    subprocess.run(command, check=True)

    print(f"Virtual Raster (VRT) created: {output_vrt}")


def convert_tiff_to_cog(temp_tiff: str, output_cog: str, zoom_level=14):
    """
    Converts a standard TIFF into a Cloud-Optimized GeoTIFF (COG) using `gdal_translate`.

    Parameters:
    - temp_tiff: Path to the temporary TIFF file.
    - output_cog: Path to the final Cloud-Optimized GeoTIFF file.
    """
    command = [
        "gdal_translate",
        "-of", "COG",
        "-co", "TILING_SCHEME=GoogleMapsCompatible",
        "-co", f"ZOOM_LEVEL={zoom_level}",
        "-co", "COMPRESS=ZSTD",
        "-co", "PREDICTOR=2",
        "-co", "BIGTIFF=YES",
        "-CO", "RESAMPLING=NEAREST",
        "-CO", "OVERVIEW_RESAMPLING=NEAREST",
        "-co", "NUM_THREADS=ALL_CPUS",
        "-co", "OVERVIEWS=IGNORE_EXISTING",
        temp_tiff, output_cog  # Input and Output files
    ]

    env = os.environ.copy()
    env["GDAL_CACHEMAX"] = "10240"

    # Run the command
    subprocess.run(command, check=True, env=env)

    print(f"COG created: {output_cog}")


if __name__ == '__main__':
    input_dir = "./data/output_tiff/"
    output_vrt = "./relative_wealth_index.vrt"
    output_cog = "./relative_wealth_index.tif"
    create_vrt(input_dir, output_vrt)

    convert_tiff_to_cog(output_vrt, output_cog, zoom_level=7)

