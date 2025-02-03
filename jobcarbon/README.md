# Job Carbon

`jobcarbon` is a quick script to pull data about OSCAR jobs into a format that is consumable by Impact Framework. `jobcarbon` uses the same database of information as `jobstats` to gather its the runtime statistics

## Prerequisites

`jobcarbon` uses `uv` to manage dependencies. To install `uv` refer to the [`uv` documentation](https://docs.astral.sh/uv/), or run:

```python
pip install uv
```

## Running

Run any of your slurm jobs normally. Any job that takes longer than a minute should work with `jobcarbon`. Once your job is completed, run

```sh
sacct -j $JOB_ID -o Job,Start,End
```

The output from that command will be the input to `jobcarbon`. To run `jobcarbon` run the following command:

```sh
./jobcarbon.py $JOB_ID $START_TIME $END_TIME
```

For example, I ran a test job. The job id of that job is 7980388. Running the `sacct` command gives me:

```sh
$ sacct -j 7980388 -o Job,Start,End
JobID                      Start                 End
------------ ------------------- -------------------
7980388      2025-02-03T11:17:18 2025-02-03T11:24:58
7980388.bat+ 2025-02-03T11:17:18 2025-02-03T11:24:58
7980388.ext+ 2025-02-03T11:17:18 2025-02-03T11:24:58
```

The first like of the output data are the arguments to `jobcarbon`. I can then run `jobcarbon`:

```sh
$ ./jobcarbon.py 7980388      2025-02-03T11:17:18 2025-02-03T11:24:58
tree:
  children:
    job7980388:
      children:
        node1735:
          inputs:
          - cgroup_cpu_system_seconds: '0.157958'
            cgroup_cpu_total_seconds: '22.014421'
            cgroup_cpu_user_seconds: '21.856462'
            duration: 0.5
            timestamp: 1738599468
          - cgroup_cpu_system_seconds: '0.306046'
            cgroup_cpu_total_seconds: '51.825791'
            cgroup_cpu_user_seconds: '51.519745'
            duration: 0.5
            timestamp: 1738599498
[...SNIP...]
```

The output of `jobcarbon` is `yaml` that can be used as observations in an Impact Framework manifest file
