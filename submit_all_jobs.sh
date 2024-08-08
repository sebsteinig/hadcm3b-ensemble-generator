#!/bin/bash

# File containing the experiment IDs
logfile="./logs/xqab.log"

# Loop through each line in the log file
while IFS= read -r experiment_id
do
  # Run the command with the current experiment ID
  clustersubmit -s y -c n -a y -r bc4 -q veryshort -w 6:00:00 "$experiment_id"
done < "$logfile"