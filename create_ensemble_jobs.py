import os
import json
import subprocess
import argparse

from helpers import setup_logging, duplicate_job, generate_ensemble_jobid


# Setup logging directory
def setup_logging_directories(home_dir, ensemble_exp):
    log_dir = os.path.join(home_dir, "hadcm3b-ensemble-generator", "logs")
    logger, generated_ids_log_file, generated_params_log_file = setup_logging(
        ensemble_exp, log_dir
    )
    return logger, generated_ids_log_file, generated_params_log_file


def main(vanilla_job, parameter_file, ensemble_exp, singleJob=False):
    """
    Generates ensemble job directories based on a template job and new model parameters
    to generate a perturbed parameter ensemble.

    This script reads new model parameters from a JSON file, creates copies of a
    vanilla job template for each parameter set, and updates the job files with
    the new parameters. The generated jobs are saved in the specified directory.
    Logs the operations to both the console and a log file.
    """
    home_dir = os.path.expanduser("~")
    jobs_dir = os.path.join(home_dir, "umui_jobs")  # Fixed path for jobs_dir

    # Setup logging
    logger, generated_ids_log_file, generated_params_log_file = (
        setup_logging_directories(home_dir, ensemble_exp)
    )

    # Read JSON file with new model parameters
    try:
        with open(parameter_file, "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Input file not found: {parameter_file}")
        return
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON file: {parameter_file}")
        return

    num_records = len(json_data)

    # Prepare to log generated ensemble IDs and parameters to disk
    updated_params_data = []

    # Create a new ensemble job for each record in the JSON file
    for i in range(num_records):
        if singleJob:
            expid = f"{ensemble_exp}_{i:03d}"
        else:
            expid = generate_ensemble_jobid(ensemble_exp, i)

        with open(generated_ids_log_file, "a") as f:
            f.write(f"{expid}\n")

        # Create a copy of the vanilla job
        if not duplicate_job(vanilla_job, expid, force_overwrite=True):
            logger.error(f"Failed to duplicate job: {vanilla_job} to {expid}")
            continue

        # Get the new parameters for this ensemble member
        record = json_data[i]
        record["ensemble_id"] = expid
        updated_params_data.append(record)

        original_file = os.path.join(jobs_dir, expid, "CNTLATM")

        # Read the content of the namelist file
        try:
            with open(original_file, "r") as file:
                file_content = file.read()
        except FileNotFoundError:
            logger.error(f"File not found: {original_file}")
            continue

        # Loop over all keys (i.e., all parameters to change)
        for key, value in record.items():
            if key == "ensemble_id":
                continue
            # Check if the key exists in the namelist
            if f"{key}=" not in file_content:
                logger.warning(f"{expid}: Key {key} not found in {original_file}")
                continue

            # Convert value to string and remove square brackets if it is a list
            if isinstance(value, list):
                value_str = ",".join(map(str, value))
            else:
                value_str = str(value)

            # Update the parameters in the job namelist
            logger.info(f"{expid}: Setting {key} to {value_str}")

            # Replace whole line in namelist
            subprocess.run(
                ["sed", "-i", f"s|{key}=.*|{key}={value_str}|", original_file],
                check=True,
            )

    # Save the updated JSON data to a new file for logging
    with open(generated_params_log_file, "w") as f:
        json.dump(updated_params_data, f, indent=4)

    logger.info(
        f"Generation of {ensemble_exp} ensemble finished. {num_records} ensemble members have been created in {jobs_dir}."
    )
    logger.info(f"List of generated ensemble IDs saved to {generated_ids_log_file}.")
    logger.info(f"Updated JSON file saved to {generated_params_log_file}.")


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate perturbed parameter ensemble jobs."
    )
    parser.add_argument(
        "--vanilla_job",
        type=str,
        required=True,
        help="Path to the vanilla/template job ",
    )
    parser.add_argument(
        "--parameter_file",
        type=str,
        required=True,
        help="Path to the JSON file containing the parameters to update",
    )
    parser.add_argument("--ensemble_exp", type=str, required=True, help="Ensemble name")
    parser.add_argument(
        "--singleJob",
        action="store_true",
        help="Create variations of a single job (with underscores) or variations of letters a-z",
    )

    args = parser.parse_args()

    # Run the main function with input arguments
    main(args.vanilla_job, args.parameter_file, args.ensemble_exp, args.singleJob)
