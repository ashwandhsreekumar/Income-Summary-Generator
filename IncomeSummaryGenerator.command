#!/bin/bash
# Income Summary Generator Launcher

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the app directory
cd "$DIR"

# Run the CLI version
./venv/bin/python src/income_summary_cli.py
