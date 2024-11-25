# create job directories for each ensemble job on larger, private BRIDGE disk 
# create symlinks in dump2hold for normal model I/O
user_name=$(whoami)
while IFS= read -r job_id; do
    echo "ln -s /mnt/storage/private/bridge/um_output/$user_name/$job_id /user/home/$user_name/dump2hold/$job_id"
    mkdir -p "/mnt/storage/private/bridge/um_output/$user_name/$job_id"
    ln -s "/mnt/storage/private/bridge/um_output/$user_name/$job_id" "/user/home/$user_name/dump2hold/$job_id"

# done < logs/xqaRd_generated_ids_20241028.log
done < logs/XqArn_generated_ids_20241028.log









