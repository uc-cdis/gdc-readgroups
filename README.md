# gdc-readgroups

## Purpose
This package will extract the Read Group header lines from a BAM file, and convert the contained metadata to a json or tsv file with appropriate values applied for creation of a Read Group node in the Genomic Data Commons (GDC).

The generated file may contain some fields marked `REQUIRED<type>`. This indicates these fields could not be generated from the supplied BAM file, and the user must apply their own desired values to the generated json. The `<type>` must be as indicated in the generated json file. For details, see the column `Acceptable Types or Values` at

https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=read_group

Other fields are optional, and are marked `OPTIONAL<type>`. If these fields could not be generated from the supplied BAM file, they may be filled in as appropriate or removed.

#### Note

The tool will only run on complete BAM files - files which contain the suffix `.bam`.

If the BAM is truncated, the error
```
OSError: no BGZF EOF marker; file may be truncated
```
will be generated, and no json will be produced.


## Installation
There are 2 ways to install `gdc-readgroups`

#### pip install
`gdc-readgroups` may be used as a `pip` installed python package.

If you would like to install the package as root, for all users, run
```
sudo pip install gdc-readgroups
```
If you would like to install the package only for a local user, run
```
pip install gdc-readgroups --user
```

#### docker image
The github repository for this package contains a Dockerfile, which can be used to build an image containing the package. There are two ways to build the image.

1.
```
git clone https://github.com/NCI-GDC/gdc-readgroups.git
cd gdc-readgroups
docker build -t gdc-readgroups .
```

1. the Docker Container using the supplied CWL (Common Workflow Language) CommandLineTool file.
To install the reference CWL engine, run
```
sudo pip install cwltool
```
or
```
pip install cwltool --user
```
Then to build Docker Image and run the Container, run
```
cwltool gdc-readgroups.cwl --INPUT <your bam file>
```

The above command will only build the Docker Image if it does not exist on the system.

## Usage


The command to run the pip installed package is
```
gdc-readgroups --bam_path <your bam file>
```

The generated json file will be output as `<bam file basename>.json`, and any error messages will be written to stdout.
The generated json file will be output as `<bam file basename>.json`, and any error messages will be written to `output.log`.
