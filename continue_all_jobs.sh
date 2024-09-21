#!/bin/bash

# File containing the experiment IDs
# logfile="./logs/xqab.log"
# logfile="./logs/xqac_generated_ids_20240815.log"
# logfile="./logs/xqab_generated_ids_20240808.log"
# logfile="./logs/xqap_generated_ids_20240907.log"
# logfile="./logs/xqaq_generated_ids_20240908.log"
# logfile="./logs/xqar_generated_ids_20240908.log"
logfile="./logs/xqau_generated_ids_20240909.log"

# Loop through each line in the log file
while IFS= read -r experiment_id
do
  # Run the command with the current experiment ID
  clustersubmit -s y -c y -a y -r bc4 -q veryshort -w 6:00:00 "$experiment_id"
done < "$logfile"
