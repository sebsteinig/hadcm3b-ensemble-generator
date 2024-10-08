#!/bin/bash

# read job IDs from the log file and create a comma-separated list
# log_file="logs/xpzn_generated_ids_20240720.log"
log_file="logs/abcd_generated_ids_20240723.log"

if [ ! -f "$log_file" ]; then
    echo "Log file not found: $log_file"
    exit 1
fi

# read the log file and join the lines with commas
job_ids=$(paste -sd, "$log_file")
echo "Ensemble jobs to process: $job_ids"

create_ensemble -file demo -c n -g 2 -e $job_ids