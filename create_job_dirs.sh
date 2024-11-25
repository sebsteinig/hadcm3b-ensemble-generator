# create job directories for each ensemble job on larger, private BRIDGE disk 
# create symlinks in dump2hold for normal model I/O
user_name=$(whoami)
while IFS= read -r job_id; do
    echo "ln -s /mnt/storage/private/bridge/um_output/$user_name/$job_id /user/home/$user_name/dump2hold/$job_id"
    mkdir -p "/mnt/storage/private/bridge/um_output/$user_name/$job_id"
    ln -s "/mnt/storage/private/bridge/um_output/$user_name/$job_id" "/user/home/$user_name/dump2hold/$job_id"
# done < logs/xqab_generated_ids_20240808.log
# done < logs/xqac_generated_ids_20240815.log
# done < logs/xqap_generated_ids_20240907.log
# done < logs/xqaq_generated_ids_20240908.log
# done < logs/xqar_generated_ids_20240908.log
# done < logs/xqau_generated_ids_20240909.log
# done < logs/XqaqW_generated_ids_20240921.log
# done < logs/Xqarh_generated_ids_20240924.log
# done < logs/XqAuc_generated_ids_20240924.log
# done < logs/xQaup_generated_ids_20240924.log
# done < logs/XqaRq_generated_ids_20240924.log
# done < logs/XqAuf_generated_ids_20241003.log
# done < logs/Xqaul_generated_ids_20241003.log
# done < logs/xqare_generated_ids_20241003.log
# done < logs/xQaqc_generated_ids_20241003.log
# done < logs/XqAqs_generated_ids_20241005.log
# done < logs/Xqarp_generated_ids_20241005.log
# done < logs/Xqaqp_generated_ids_20241005.log
# done < logs/xqaRw_generated_ids_20241005.log
# done < logs/xqarE_generated_ids_20241005.log
# done < logs/XQarc_generated_ids_20241005.log
# done < logs/XqAqg_generated_ids_20241015.log
# done < logs/XqauI_generated_ids_20241015.log
# done < logs/xqaqg_generated_ids_20241015.log
# done < logs/xqaQs_generated_ids_20241015.log
# done < logs/xqauj_generated_ids_20241015.log
# done < logs/xqaQh_generated_ids_20241028.log
# done < logs/xqaRd_generated_ids_20241028.log
done < logs/XqArn_generated_ids_20241028.log









