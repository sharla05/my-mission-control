import argparse
import json

from my_mission_control.parser.log_parser_v2 import process_log_file
from my_mission_control.utils.log_util import setup_logging
from my_mission_control.utils.pyproject_util import get_pyproject_metadata

PROJECT_NAME, PROJECT_VERSION = get_pyproject_metadata()


def main():
    parser = argparse.ArgumentParser(description="Process a log file and generate alerts.")
    parser.add_argument("logfile", nargs="?", default="data/sample.log", help="Path ot the log file to process (default: data/sample.log)")
    args = parser.parse_args()

    alerts = process_log_file(args.logfile)

    json_alerts = json.dumps(alerts, indent=4)

    # Output in JSON format
    print(json_alerts)


if __name__ == "__main__":
    if PROJECT_NAME and PROJECT_VERSION:
        setup_logging(service=PROJECT_NAME, version=PROJECT_VERSION)
    else:
        setup_logging(service="unknown-service", version="0.0.0")

    main()
