#!/usr/bin/env python3
import argparse
import datetime
import requests
import yaml

PROMETHEUS_SERVER = "http://slurm02:9390/api/v1"
QUERY_RANGE_ENDPOINT = f"{PROMETHEUS_SERVER}/query_range"
QUERY_ENDPOINT = f"{PROMETHEUS_SERVER}/query"
STEP_SECONDS = 60


def get_overall_metric(resp):
    results = resp["data"]["result"]
    name = None
    overall = {}
    for result in results:
        metric = result["metric"]
        name = get_node_name(result)
        if metric.get("step") or metric.get("task"):
            continue
        overall[name] = result

    if not overall:
        raise KeyError(f"cannot find overall metrics for {name}")

    return overall


def get_metric_name(result):
    metric = result["metric"]
    name = metric["__name__"]

    if name == 'cgroup_cpu_system_seconds':
        return 'cpu/system-seconds'
    elif name == 'cgroup_cpu_total_seconds':
        return 'cpu/total-seconds'
    elif name == 'cgroup_cpu_user_seconds':
        return 'cpu/user-seconds'

    raise Exception(f'unsupported metric found {name}')


def get_node_name(result):
    metric = result["metric"]
    instance = metric["instance"]
    return instance.split(":")[0]


def get_job_id(result):
    metric = list(result.values())[0]["metric"]
    return metric["jobid"]


def get_metric_data(result):
    retyped_results = list(map(lambda x: [x[0], float(x[1])], result["values"]))
    return retyped_results


def zipper_metric_data(a, b, c):
    output = []
    for key in a.keys():
        a_overall = a[key]
        b_overall = b[key]
        c_overall = c[key]

        a_name = get_metric_name(a_overall)
        b_name = get_metric_name(b_overall)
        c_name = get_metric_name(c_overall)

        # NOTE(@broarr): This is probably overkill for what I'm trying to do
        # TODO(@broarr): Remove the extra node checks from inside this loop
        a_node = get_node_name(a_overall)
        b_node = get_node_name(b_overall)
        c_node = get_node_name(c_overall)

        a_values = get_metric_data(a_overall)
        b_values = get_metric_data(b_overall)
        c_values = get_metric_data(c_overall)

        for [a_timestamp, a_value] in a_values:
            for [b_timestamp, b_value] in b_values:
                for [c_timestamp, c_value] in c_values:
                    if (
                        a_timestamp == b_timestamp == c_timestamp
                        and a_node == b_node == c_node
                    ):
                        output.append(
                            {
                                "timestamp": a_timestamp,
                                a_name: a_value,
                                b_name: b_value,
                                c_name: c_value,
                                "node": a_node,
                                "duration": STEP_SECONDS / 60,
                            }
                        )

    return output


def parse_responses(a, b, c):
    a_overall = get_overall_metric(a)
    b_overall = get_overall_metric(b)
    c_overall = get_overall_metric(c)

    job_id = get_job_id(a_overall)

    inputs = zipper_metric_data(a_overall, b_overall, c_overall)

    return {"tree": {"children": {f"job{job_id}": {"inputs": inputs}}}}


def system_cpu_seconds(jobid, start, end):
    query = f"cgroup_cpu_system_seconds{{cluster='oscar',jobid='{jobid}'}}"
    r = requests.get(
        QUERY_RANGE_ENDPOINT,
        {
            "query": query,
            "start": start,
            "end": end,
            "step": f"{STEP_SECONDS}s",
        },
    )
    return r.json()


def total_cpu_seconds(jobid, start, end):
    query = f"cgroup_cpu_total_seconds{{cluster='oscar',jobid='{jobid}'}}"
    r = requests.get(
        QUERY_RANGE_ENDPOINT,
        {
            "query": query,
            "start": start,
            "end": end,
            "step": f"{STEP_SECONDS}s",
        },
    )
    return r.json()


def user_cpu_seconds(jobid, start, end):
    query = f"cgroup_cpu_user_seconds{{cluster='oscar',jobid='{jobid}'}}"
    r = requests.get(
        QUERY_RANGE_ENDPOINT,
        {
            "query": query,
            "start": start,
            "end": end,
            "step": f"{STEP_SECONDS}s",
        },
    )
    return r.json()


def main():
    parser = argparse.ArgumentParser(
        description="generate observations for impact framework manifest"
    )
    parser.add_argument("jobid", help="job id to analyze")
    parser.add_argument("start", help="start time for job", type=str)
    parser.add_argument("end", help="end time for job", type=str)
    args = parser.parse_args()
    start_date = datetime.datetime.strptime(args.start, "%Y-%m-%dT%H:%M:%S").timestamp()
    end_date = datetime.datetime.strptime(args.end, "%Y-%m-%dT%H:%M:%S").timestamp()
    cpu_total_resp = total_cpu_seconds(args.jobid, start_date, end_date)
    cpu_user_resp = user_cpu_seconds(args.jobid, start_date, end_date)
    cpu_system_resp = system_cpu_seconds(args.jobid, start_date, end_date)
    print(yaml.dump(parse_responses(cpu_system_resp, cpu_total_resp, cpu_user_resp)))


if __name__ == "__main__":
    main()
