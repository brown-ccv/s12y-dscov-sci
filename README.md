# Sustainability - DSCoV Software Carbon Intensity

This repository contains some code to calculate the Software Carbon Intensity (SCI) score of a CPU job on our high performance computer OSCAR. This code is meant to be a starting point to developing new, more interesting manifests

## Impact Framework

Impact Framework is a tool designed by the Green Software Foundation to calculate pipelines related to software sustainability. This workshop builds out a _very_ rudimentary SCI score from an example job

### Getting Started

Ensure you have a recent version of `node`. If you do not have node installed, please visit https://nodejs.org/en and follow the install instructions

Once `node` is installed, run `npm install` to install all the software packages

To run Impact Framework, use the `npx` command:

```sh
$ npx if-run --help
```

To run a pipeline in a given manifest file run:

```sh
$ npx if-run -m ${MANIFEST_FILE}
```

### Manifests

Manifest files are artifacts that contain observations about a system and a pipeline to compute metrics about those observations. Each manifest in this repository is meant to illustrate different parts of the SCI score

#### 01-basic-demo

This manifest file is there to show you the structure of a manifest file. This file takes observations and doubles the CPU utilization

#### 02-operational-emissions

This manifest file calculates the operational carbon of the CPU from a job on OSCAR. The CPU for a given node is contained within the `cpu-model.csv` file in the `resources` directory. The regional grid intensity is from the EPA's most recent eGrid dataset (a copy is provided in the `resources` directory)

The pipeline takes the CPU utilization for the different observations and calculates the kilowatt-hour used based on the Thermal Design Power of a given CPU

#### 03-embodied-emissions

This manifest file calculates the embodied carbon of the CPU by leveraging the [`SciEmbodied`](https://github.com/Green-Software-Foundation/if/tree/main/src/if-run/builtins/sci-embodied) plugin from Impact Framework. The [methodology](https://www.cloudcarbonfootprint.org/docs/embodied-emissions) used by the plugin is borrowed from the Cloud Carbon Footprint Dashboard

#### 04-sci-score

This manifest file calculates the SCI score of the OSCAR job by combining the operational and embodied embodied emissions. The contents of the pipeline are copied from `02-operational-emissions.yml` and `03-embodied-emissions.yml`

### `batch.sh`

Individual manifests can be analyzed individually using the above commands, but if you have a directory of manifests in a directory `manifests/`, you can use the `batch.sh` script to output a bunch of analyses in `analyses/` and genereate a CSV with the aggregate values called `outputs.csv`.

## Jobcarbon

Jobcarbon outputs yaml that is suitable for use as observations in an Impact Framework manifest. These observations are based on data in the Prometheus database. Prometheus is a timeseries database that stores information about recently run jobs

Jobcarbon requires an OSCAR job run within the last 30 days that took longer than a minute to complete

### Installing

Copy the `jobcarbon` directory to OSCAR:

```sh
$ scp -r jobcarbon sshcampus.ccv.brown.edu:~/
```

Log into OSCAR and load the `python` module:

```sh
$ module load python/3.9
```

Install `uv` to manage the `jobcarbon` project:

```sh
$ pip3 install uv
```

Sync the `jobcarbon` project using `uv`:

```sh
$ cd jobcarbon && uv sync
```

### Running

To run `jobcarbon` use `uv`:

```sh
$ uv run jobcarbon.py ${JOB_ID} ${START_TIME} ${END_TIME}
```

Copy the output of `jobcarbon` into a manifest file. Be careful about the indentation! Yaml is very picky. You'll still need to add the `defaults` and `pipeline` to the manifest alongside the `inputs`

The format of `$START_TIME` and `${END_TIME}` is "YYYY-mm-ddTHH:MM:S". The exact parameters can be grabbed from `sacct` (NB: you only need the line where the job id has no suffix):

```sh
$ sacct -j ${JOB_ID} -o Job,Start,End
```
