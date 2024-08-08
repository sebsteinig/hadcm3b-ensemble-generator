import os
import json
import subprocess

from helpers import setup_logging, duplicate_job, generate_ensemble_jobid

# define user input
home_dir = os.path.expanduser("~")
vanilla_job = os.path.join(
    home_dir, "hadcm3b-ensemble-generator", "vanilla_jobs", "xqaba"
)
ensemble_exp = "xqab"
parmater_file = "param_tables/acang_random_param_sets.json"
jobs_dir = os.path.join(home_dir, "umui_jobs")

# setup logging
log_dir = os.path.join(home_dir, "hadcm3b-ensemble-generator", "logs")
logger, generated_ids_log_file, generated_params_log_file = setup_logging(
    ensemble_exp, log_dir
)


def main():
    """
    Generates ensemble job directories based on a template job and new model parameters
    to generate a perturbed parameter ensemble.

    This script reads new model parameters from a JSON file, creates copies of a
    vanilla job template for each parameter set, and updates the job files with
    the new parameters. The generated jobs are saved in the specified directory.
    Logs the operations to both the console and a log file.
    """

    # read JSON file with new model parameters
    try:
        with open(parmater_file, "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Input file not found: {parmater_file}")
        return
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON file: {parmater_file}")
        return
    num_records = len(json_data)
    # prepare to log generated ensemble IDs and paramters to disk
    updated_params_data = []

    # create a new ensemble job for each record in the JSON file
    for i in range(num_records):
        expid = generate_ensemble_jobid(ensemble_exp, i)

        with open(generated_ids_log_file, "a") as f:
            f.write(f"{expid}\n")

        # create a copy of the vanilla job
        if not duplicate_job(vanilla_job, expid, force_overwrite=True):
            logger.error(f"Failed to duplicate job: {vanilla_job} to {expid}")
            continue

        # get the new parameters for this ensemble member
        record = json_data[i]
        record["ensemble_id"] = expid
        updated_params_data.append(record)

        original_file = os.path.join(jobs_dir, expid, "CNTLATM")

        # read the content of the namelist file
        try:
            with open(original_file, "r") as file:
                file_content = file.read()
        except FileNotFoundError:
            logger.error(f"File not found: {original_file}")
            continue

        # loop over all keys (i.e., all parameters to change)
        for key, value in record.items():
            if key == "ensemble_id":
                continue
            # check if the key exists in the namelist
            if f"{key}=" not in file_content:
                logger.warning(f"{expid}: Key {key} not found in {original_file}")
                continue

            # Convert value to string and remove square brackets if it is a list
            if isinstance(value, list):
                value_str = ",".join(map(str, value))
            else:
                value_str = str(value)

            # update the parameters in the job namelist
            logger.info(f"{expid}: Setting {key} to {value_str}")

            # replace whole line in namelist
            subprocess.run(
                ["sed", "-i", f"s|{key}=.*|{key}={value_str}|", original_file],
                check=True,
            )

    # save the updated JSON data to a new file for loggoing
    with open(generated_params_log_file, "w") as f:
        json.dump(updated_params_data, f, indent=4)

    logger.info(
        f"Generation of {ensemble_exp} ensemble finished. {num_records} ensemble members have been created in {jobs_dir}."
    )
    logger.info(f"List of generated ensemble IDs saved to {generated_ids_log_file}.")
    logger.info(f"Updated JSON file saved to {generated_params_log_file}.")


if __name__ == "__main__":
    main()
