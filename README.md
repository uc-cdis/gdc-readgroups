# bam_readgroup_to_gdc_json

## Purpose
This package will extract the Read Group header lines from a BAM file, and convert the contained metadata to a json file with appropriate values applied for creation of a Read Group node in the Genomic Data Commons (GDC).

The generated json file may contain some fields marked `REQUIRED<type>`. This indicates these fields could not be generated from the supplied BAM file, and the user must apply their own desired values to the generated json. The `<type>` must be as indicated in the generated json file. For details, see the column `Acceptable Types or Values` at

https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=read_group

Other fields are optional, and are marked `OPTIONAL<type>`. If these fields could not be generated from the supplied BAM file, they may be filled in as appropriate or removed.

## Usage
There are 2 ways to use `bam_readgroup_to_gdc_json`

### pip install
`bam_readgroup_to_gdc_json` may be used as a `pip` installed python package.

If you would like to install the package as root, for all users, run
```
sudo pip install bam_readgroup_to_gdc_json
```
If you would like to install the package only for a local user, run
```
pip install bam_readgroup_to_gdc_json --user
```

### docker image
The GDC supplies a prebuilt Docker Image, with all prerequisite packages installed. It is easiest to run the Docker Container using the supplied CWL (Common Workflow Language) CommandLineTool file.
To install the reference CWL engine, run
```
sudo pip install cwltool
```
or
```
pip install cwltool --user
```
Then to run the Docker Container, run
```
cwltool bam_readgroup_to_gdc_json.cwl --INPUT <your bam file>
```
The generated json file will be output as `<bam file basename>.json`, and any error messages will be written to `output.log`.
