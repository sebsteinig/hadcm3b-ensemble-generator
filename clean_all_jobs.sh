# create job directories for each ensemble job on larger, private BRIDGE disk 
# create symlinks in dump2hold for normal model I/O
user_name=$(whoami)
while IFS= read -r job_id; do
    cd "/mnt/storage/private/bridge/um_output/$user_name/$job_id/datam"
    ls *p[abcdf]00*
    rm -f *p[abcdf]00*
    ls -t *da00* | tail -n +21
    ls -t *da00* | tail -n +21 | while read -r file; do rm -f "$file"; done
# done < logs/xqab_generated_ids_20240808.log
# done < logs/xqac_generated_ids_20240815.log
# done < logs/xqap_generated_ids_20240907.log
# done < logs/xqaq_generated_ids_20240908.log
# done < logs/xqar_generated_ids_20240908.log
done < logs/xqau_generated_ids_20240909.log

