#!/bin/bash

# File containing the experiment IDs
# logfile="./logs/xqaRd_generated_ids_20241028.log"
logfile="./logs/XqArn_generated_ids_20241028.log"

# Loop through each line in the log file
while IFS= read -r experiment_id
do
  # Run the command with the current experiment ID
  clustersubmit -s y -c n -a y -r bc4 -q cpu -w 12:00:00 "$experiment_id"
done < "$logfile"