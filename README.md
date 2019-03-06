# gdc-readgroups

[![PyPI version](https://badge.fury.io/py/gdc-readgroups.svg)](https://badge.fury.io/py/gdc-readgroups)

## Purpose
This package will extract the Read Group header lines from a BAM file, and convert the contained metadata to a json or tsv file with appropriate values applied for creation of a Read Group node in the [NCI's Genomic Data Commons](https://gdc.cancer.gov/) (GDC). Optionally, it will take no input, and output a template which may be edited to create a submission to the GDC.

The generated file may contain some fields marked `REQUIRED<type>`, which indicates these fields could not be generated from the supplied BAM file. In this case, the user must apply their own desired values to the generated json. The `<type>` must be as indicated in the generated json file. For details, see the column `Acceptable Types or Values` at the [GDC Data Dictionary Viewer](https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=read_group).



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

#### pip install from pypi
`gdc-readgroups` may be used as a `pip` installed python package.

If you would like to install the package as root, for all users, run
    
```bash
sudo pip install gdc-readgroups
```
    
If you would like to install the package only for a local user, run

```bash
pip install gdc-readgroups --user
```

#### Build a Docker Image
The github repository for this package contains a Dockerfile, which may be used to build an image containing the package and all prerequisites. There are two ways to build the image.

1. Using `docker` directly.
    ```bash
    wget https://raw.githubusercontent.com/NCI-GDC/gdc-readgroups/master/Dockerfile
    docker build -t gdc-readgroups .
    ```

1. Using `cwltool` to build an image, and then run it, in one command.
    
    In this case the cwl tool will expect a BAM input, and produce a json output. To install the reference CWL engine, run
    ```bash
    pip install cwltool --user
    ```
    Then to build the `gdc-readgroups` Docker Image and run the Container, run

    ```bash
    wget https://raw.githubusercontent.com/NCI-GDC/gdc-readgroups/master/Dockerfile
    wget https://raw.githubusercontent.com/NCI-GDC/gdc-readgroups/master/gdc-readgroups.cwl
    cwltool gdc-readgroups.cwl --INPUT <your bam file>
    ```
    The above command will only build the Docker Image if it does not exist on the system. After the build is performed once, the image will remain on your system, and the next `cwltool` run will skip the build step.

## Usage

`gdc-readgroups` has two main modes: `bam-mode` and `template-mode`. 

#### bam-mode

In `bam-mode`, a path to a BAM file must be supplied as input. By default, `bam-mode` will output a json file, but optionally may output a tsv file.

The command to run the [pip installed package](#pip-install-from-pypi) is

```bash
gdc-readgroups bam-mode --bam_path <your bam file>
```

The generated json will be placed in the current working directory and have a filename of `<bam basename>.json`.
Any error messages will be written to stdout.

To output a tsv file, run

```bash
gdc-readgroups bam-mode --bam_path <your bam file> --output-format tsv
```

The generated tsv file will be placed in your current working directory, and be of the form `<bam basename>.tsv`


#### template-mode

In `template-mode`, no input is supplied, and two empty records are output within one file, either in json or tsv format.

To generate a json template, run

```bash
gdc-readgroups template-mode
```

The output will be placed in the current working directory and have a filename of `gdc_readgroups.json`

To generate a tsv template, run

```bash
gdc-readgroups template-mode --output-format tsv
```

The output will be placed in the current working directory and have a filename of `gdc_readgroups.tsv`
