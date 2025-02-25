# geo-rwi-meta

This repository is to ingest relative wealth index from Meta to geospatial data format.

The RWI data can be accessed at https://dataforgood.facebook.com/dfg/tools/relative-wealth-index#accessdata.

## Prepare

Download data from https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/bff723a4-6b55-4c51-8790-6176a774e13c/download/relative-wealth-index-april-2021.zip

unzip and place it under `data` folder.

Some countries are not included in zip file. Download rest of countries as well and put them in the same folder.

```shell
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/217f9381-a6fa-42a7-b8ba-9bf9938ba94b/download/romania_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/28f9d272-a5ee-4337-a907-8f907d9e9e52/download/ukraine_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/55bca2ec-6938-4347-89a0-b57b6c0c6028/download/serbia_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/be604d16-af51-4df0-9065-58f04c87a55e/download/moldova_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/c12ea7e5-5fd4-4365-9327-39aeb5a3428b/download/montenegro_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/0142e224-3fbe-44a2-a31a-b79aace6e9e8/download/north-macedonia_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/bb977fac-405d-4a6c-a101-9023f30059ec/download/georgia_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/df20627b-770e-438c-bd3e-b172ef2fbdae/download/bosnia-and-herzegovina_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/d3eced2c-170c-4d10-97f3-ba2e32ee121f/download/armenia_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/23ddad00-f8ed-461c-a9d1-33ef2386faa6/download/albania_relative_wealth_index.csv
wget https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/ca1dea6b-9cc1-4bed-9465-8fd8fd7e0941/download/tur_relative_wealth_index.csv
```

## Install

```shell
pop install -r requirement.txt
```

## Usage

- Firstly, convert CSV to FGB file for each country

```shell
python rwi2fgb.py
```

flatgeobuf is generated for each country CSV file under `/data/output_fgb` folder, and merged fgb is also stored under `data` folder.

- Then, rasterise FGB to Tiff file by using the below command.

```shell
python rwi2tiff.py
```

- create a virtual raster from tiff files and translate vrt to COG

```shell
python vrt.py
```