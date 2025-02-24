import os
import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import from_origin
import mercantile
from pathlib import Path

# 📌 quadkey を x, y タイル座標に変換する関数
def quadkey_to_tile(quadkey, zoom_level: int = 14):
    """quadkey を x, y タイル座標に変換"""
    tile = mercantile.quadkey_to_tile(str(quadkey).zfill(zoom_level))  # ゼロ埋めして安定化
    return tile.x, tile.y


# 📌 データを処理してラスターを作成
def rwi2tiff(csv_file: str, output_file: str, zoom_level: int = 14):
    df = pd.read_csv(csv_file)

    if df.empty:
        print(f"Skipping {csv_file}: empty file")
        return

    # quadkey を x, y タイル座標に変換
    df["x"], df["y"] = zip(*df["quadkey"].apply(lambda qk: quadkey_to_tile(qk, zoom_level)))

    # X, Y の範囲を取得
    min_x, max_x = df["x"].min(), df["x"].max()
    min_y, max_y = df["y"].min(), df["y"].max()

    # 🌍 タイルの境界から緯度・経度リストを作成
    lons = [mercantile.ul(x, min_y, zoom_level).lng for x in range(min_x, max_x + 2)]
    lats = [mercantile.ul(min_x, y, zoom_level).lat for y in range(min_y, max_y + 2)]
    lats.reverse()  # ラスターの行方向と合わせるため逆順

    # ラスターの行列サイズ
    cols = len(lons) - 1
    rows = len(lats) - 1

    # 空のラスターを作成（NaN 初期化）
    raster = np.full((rows, cols), np.nan, dtype=np.float32)

    # 📌 x, y の位置をラスターのインデックスに変換
    for _, row in df.iterrows():
        # **整数に変換**
        col = int(row["x"]) - min_x
        row_idx = int(max_y - row["y"])

        # **範囲外を防ぐ**
        col = max(0, min(cols - 1, col))
        row_idx = max(0, min(rows - 1, row_idx))

        raster[row_idx, col] = row["rwi"]

    # 🌍 GeoTIFF の変換行列を設定
    transform = from_origin(lons[0], lats[0], lons[1] - lons[0], lats[0] - lats[1])

    # 🚀 GeoTIFF を保存
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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    folder_path = Path(input_dir)

    csv_files = list(folder_path.glob("*.csv"))

    for csv_file in csv_files:
        output_file = f"{output_dir}{csv_file.name.replace('.csv', '.tif')}"
        rwi2tiff(csv_file, output_file)

if __name__ == '__main__':
    # input_dir = './data/relative-wealth-index-april-2021/'
    # output_dir = './data/output/'
    # process_csv_files(input_dir, output_dir)

    input_dir = './data/relative-wealth-index-april-2021/LCA_relative_wealth_index.csv'
    output_dir = './data/output/LCA_relative_wealth_index.tif'

    # input_dir = './data/relative-wealth-index-april-2021/ETH_relative_wealth_index.csv'
    # output_dir = './data/output/ETH_relative_wealth_index.tif'
    rwi2tiff(input_dir, output_dir)
