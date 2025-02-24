# geo-rwi-meta

This repository is to ingest relative wealth index from Meta to geospatial data format.

The RWI data can be accessed at https://dataforgood.facebook.com/dfg/tools/relative-wealth-index#accessdata.

## Prepare

Download data from https://data.humdata.org/dataset/76f2a2ea-ba50-40f5-b79c-db95d668b843/resource/bff723a4-6b55-4c51-8790-6176a774e13c/download/relative-wealth-index-april-2021.zip

unzip and place it under `data` folder.

## Install

```shell
pop install -r requirement.txt
```

## Usage

```shell

python rwi2fgb.py
```

flatgeobuf is generated for each country CSV file under `/data/output_fgb` folder, and merged fgb is also stored under `data` folder.

`rwi2tiff.py` is not working currently.

