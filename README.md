# NCI Data Collection Intake Catalogue

## Usage

The catalogue is available in intake's default catalogue list in the CLEX Conda
environment

```python
import intake

print(list(intake.cat.acs))
```

Individual datasets are catalogued using intake-esm

## Admin

This catalogue exists on Gadi's NCI filesystem under /g/data/ia39/aus-ref-clim-data-nci/acs-intake/catalogue.yaml

Use `git pull` to download changes from Github

Catalogue csv listings themselves need to be generated, they are not in the
repository due to their size. This may be done by running `make` within the
directory

The intake data package is under the directory `package/`, it simply provides
an intake entry point pointing to the catalogue directory


## Contributing

If you would like to contribute you can clone the repository, create a new branch to work on. Once you added a new dataset push your new branch and create a amerge request.

## Adding a new dataset listing 

To add a new dataset you need:

* add the main dataset metadata to the catalogue.yaml file
* create a directory for the dataset
* add here:
    * a catalogue.csv.xz file listing all files, good option for stable or "smaller" collections
    * or a ingest.yaml file to generate one on the fly

The catalogue.yaml file lists the main metadata for each dataset:

```yaml
cmip6_etccdi:
        description: |
            Replica of the Climate extreme indices and heat stress indicators derived from CMIP6 ...
        Project: ia39
        Maintained By: CLEX
        Contact: cws_help@nci.org.au
        Documentation: https://github.com/aus-ref-clim-data-nci/CMIP6_ETCCDI
        License: https://cds.climate.copernicus.eu/api/v2/terms/static/cicero-cmip6-indicators-licence.pdf
        Citation: Sandstad, M., Schwingshackl, C., Iles, ...
        References:
                -  https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-extreme-indices-cmip6?tab=overview
                - ... 
        driver: intake_esm.esm_datastore
        args:
            esmcol_obj: '{{CATALOG_DIR}}/cmip6_etccdi/catalogue.json'
```
NB. As shown quotes are not needed for the fields, but they should used when they contain `:`, urls are scanned correctly.

The catalogue.csv.xz file is a compressed csv file that lists every file in the dataset and the corresponding values for each of attributes defined for the dataset.
As an example a snippet of the catalogue for the cmip6_etccdi dataset:

```csv
path,index_type,base,frequency,experiment,model,ensemble,variable,date_range
/g/data/ia39/aus-ref-clim-data-nci/cmip6-etccdi/data/v1-0/etccdi/base_independent/yr/ssp370/ACCESS-CM2/txxETCCDI_yr_ACCESS-CM2_ssp370_r1i1p1f1_no-base_v20191108_2015-2100_v1-0.nc,etccdi,base_independent,yr,ssp370,ACCESS-CM2,r1i1p1f1,txx,2015-2100
/g/data/ia39/aus-ref-clim-data-nci/cmip6-etccdi/data/v1-0/etccdi/base_independent/yr/ssp370/ACCESS-CM2/r10mmETCCDI_yr_ACCESS-CM2_ssp370_r1i1p1f1_no-base_v20191108_2015-2100_v1-0.nc,etccdi,base_independent,yr,ssp370,ACCESS-CM2,r1i1p1f1,r10mm,2015-2100
...
```

As mentioned above, you can provide this list but especially if you're dealing with big datasets or datasets that are regularly updated it is easier to provide a ingest.yaml file to generate this on the fly.
Examples of ingest.yaml are available in the existing dataset directories.

The ingest.yaml is composed of 4 main sections:
* The main dataset metadata, as added to the main catalogue.yaml
* `find` section where you define the main path and any "find" options

```yaml
find:
    paths:
        - /g/data/ub4/erai/netcdf/
    options: -not -type d -not -path */fx/* -name *.nc
```

* `drs` section where you can use Python regular expression to retrieve attributes from the directory structure and filenames
```yaml
#   /g/data/ia39/aus-ref-clim-data-nci/gpcp/data/mon/v2-3/2021/gpcp_v02r03_monthly_d202106_c20210907.nc
drs: |
    ^(?P<path>/g/data/ia39/aus-ref-clim-data-nci/gpcp/data
    /(?P<frequency>[^/]+)
    /(?P<version>[^/]+)
    /(?P<year>[^/]+)
    /gpcp_(.*[^_]_){2}(?P<date>[^_]+)
    _(.*[^\.]+)
    .nc)
```
 
We provided a simple code `test_drs.py` to test your DRS regex separately.
 
* `assets` section, here the `path` is added as an attribute column, all the others are automatically generated based on the DRS pattern. This is also where the attributes used to groupby and aggregate the data are defined.

```yaml
assets:
    column_name: path
    format: netcdf
aggregation_control:
    # Name of the variable in the file
    variable_column_name: variable
    # Grouping keys are made of these columns, joined by '.'
    groupby_attrs:
        - realm
        - frequency
        - variable
        - version
    aggregations:
        # Join along the existing time dimension
        - type: join_existing
          attribute_name: date_range
          options:
              dim: time
```

Sometimes you need to do some further processing of the attributes you can derived from the DRS in that case you can do that by coding in a postprocess.py script. You add this script and any input files that you might need in the dataset directory, this will be automatically run after the ingest.yaml. There are examples both in the `gpcc` and `frogs` datasets. 

More information is available in the official [intake-esm](https://intake-esm.readthedocs.io/en/latest/) documentation.
