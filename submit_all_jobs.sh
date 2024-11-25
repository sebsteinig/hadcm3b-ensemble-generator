#!/bin/bash

# File containing the experiment IDs
# logfile="./logs/xqab.log"
# logfile="./logs/xqap_generated_ids_20240907.log"
# logfile="./logs/xqaq_generated_ids_20240908.log"
# logfile="./logs/xqar_generated_ids_20240908.log"
# logfile="./logs/xqau_generated_ids_20240909.log"
# logfile="./logs/XqaqW_generated_ids_20240921.log"
# logfile="./logs/Xqarh_generated_ids_20240924.log"
# logfile="./logs/XqAuc_generated_ids_20240924.log"
# logfile="./logs/xQaup_generated_ids_20240924.log"
# logfile="./logs/XqaRq_generated_ids_20240924.log"
# logfile="./logs/XqAuf_generated_ids_20241003.log"
# logfile="./logs/Xqaul_generated_ids_20241003.log"
# logfile="./logs/xqare_generated_ids_20241003.log"
# logfile="./logs/xQaqc_generated_ids_20241003.log"
# logfile="./logs/XqAqs_generated_ids_20241005.log"
# logfile="./logs/Xqarp_generated_ids_20241005.log"
# logfile="./logs/Xqaqp_generated_ids_20241005.log"
# logfile="./logs/xqaRw_generated_ids_20241005.log"
# logfile="./logs/xqarE_generated_ids_20241005.log"
# logfile="./logs/XQarc_generated_ids_20241005.log"
# logfile="./logs/XqAqg_generated_ids_20241015.log"
# logfile="./logs/XqauI_generated_ids_20241015.log"
# logfile="./logs/xqaqg_generated_ids_20241015.log"
# logfile="./logs/xqaQs_generated_ids_20241015.log"
# logfile="./logs/xqauj_generated_ids_20241015.log"
# logfile="./logs/xqaQh_generated_ids_20241028.log"
# logfile="./logs/xqaRd_generated_ids_20241028.log"
logfile="./logs/XqArn_generated_ids_20241028.log"


# done < logs/.log

# Loop through each line in the log file
while IFS= read -r experiment_id
do
  # Run the command with the current experiment ID
  # clustersubmit -s y -c n -a y -r bc4 -q veryshort -w 6:00:00 "$experiment_id"
  clustersubmit -s y -c n -a y -r bc4 -q cpu -w 12:00:00 "$experiment_id"
done < "$logfile"