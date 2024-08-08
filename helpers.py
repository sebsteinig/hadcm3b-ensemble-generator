import os
import shutil
import subprocess
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def generate_ensemble_jobid(experiment_name, index):
    """
    Generate a new job ID for an ensemble experiment based on the experiment name and index,
    making use of variations of the experiment name with lower and upper case letters.

    Parameters:
        experiment_name (str): The name of the ensemble experiment. Must be exactly 4 characters long.
        index (int): The index of the ensemble experiment. Must be between 0 and 259 inclusive.

    Returns:
        str: The generated job ID.

    History:
        2024-07-16: Created by Sebastian Steinig
    """
    if len(experiment_name) != 4:
        raise ValueError("Ensemble experiment name must be exactly 4 characters long.")

    if not (0 <= index < 260):
        raise ValueError("Index must be between 0 and 259 inclusive.")

    # Determine the modified character
    if 0 <= index < 26:
        modified_char = chr(ord("a") + index)
    elif 26 <= index < 52:
        modified_char = chr(ord("a") + (index - 26))
        experiment_name = experiment_name.capitalize()
    elif 52 <= index < 78:
        modified_char = chr(ord("a") + (index - 52))
        experiment_name = (
            experiment_name[0].lower()
            + experiment_name[1].upper()
            + experiment_name[2:]
        )
    elif 78 <= index < 104:
        modified_char = chr(ord("a") + (index - 78))
        experiment_name = (
            experiment_name[:2].lower()
            + experiment_name[2].upper()
            + experiment_name[3:]
        )
    elif 104 <= index < 130:
        modified_char = chr(ord("a") + (index - 104))
        experiment_name = experiment_name[:3].lower() + experiment_name[3].upper()
    elif 130 <= index < 156:
        modified_char = chr(ord("a") + (index - 130)).upper()
        experiment_name = experiment_name.lower()  # All lower, since next is upper
    elif 156 <= index < 182:
        modified_char = chr(ord("a") + (index - 156))
        experiment_name = (
            experiment_name[0].upper()
            + experiment_name[1].upper()
            + experiment_name[2:]
        )
    elif 182 <= index < 208:
        modified_char = chr(ord("a") + (index - 182))
        experiment_name = (
            experiment_name[0].upper()
            + experiment_name[1].lower()
            + experiment_name[2].upper()
            + experiment_name[3]
        )
    elif 208 <= index < 234:
        modified_char = chr(ord("a") + (index - 208))
        experiment_name = (
            experiment_name[0].upper()
            + experiment_name[1].lower()
            + experiment_name[2].lower()
            + experiment_name[3].upper()
        )
    elif 234 <= index < 260:
        modified_char = chr(ord("a") + (index - 234)).upper()
        experiment_name = experiment_name[0].upper() + experiment_name[1:].lower()

    new_jobid = experiment_name + modified_char

    return new_jobid


def duplicate_job(old_runid_input, new_RUNID, force_overwrite=True):
    """
    Duplicate a UMUI job. The input can have an arbitrary path, the new job will always be
    written to the `~/umui_jobs` directory.

    This is the Python implementation of the `new_expt_letter` script written by Paul Valdes.

    Args:
        old_runid_input (str): The path or ID of the old job to be duplicated.
        new_RUNID (str): The ID of the new job to be created.
        force_overwrite (bool, optional): Whether to overwrite an existing new job with the same ID. Defaults to True.

    Returns:
        bool: True if the job was successfully duplicated, False otherwise.

    History:
        2024-07-16: Created by Sebastian Steinig
    """
    # Extract old_RUNID from the input path
    old_RUNID = old_runid_input.split("/")[-1]

    # Check that old_RUNID and new_RUNID have exactly 5 characters
    if len(old_RUNID) != 5 or len(new_RUNID) != 5:
        print("Error: RUNIDs must have exactly 5 characters.")
        return False

    jobs_dir = os.path.expanduser("~/umui_jobs")

    # Check if old_JOBID exists
    new_job_path = os.path.join(jobs_dir, new_RUNID)

    if not os.path.isdir(old_runid_input):
        print(f"Error: old JOBID does not exist: {old_runid_input}")
        return False

    # Check for existing data
    if os.path.isdir(new_job_path):
        if force_overwrite:
            shutil.rmtree(new_job_path)
        else:
            print(f"Error: new JOBID already exists: {new_RUNID}")
            return False

    shutil.copytree(old_runid_input, new_job_path)
    os.chdir(new_job_path)

    # Extract substrings
    old_EXPTID, old_JOBID = old_RUNID[:4], old_RUNID[4:]
    new_EXPTID, new_JOBID = new_RUNID[:4], new_RUNID[4:]

    # Process files
    files_to_process = ["CNTLALL", "CNTLATM", "CONTCNTL", "INITHIS", "SCRIPT", "SUBMIT"]
    for file in files_to_process:
        file_path = os.path.join(new_job_path, file)
        backup_file_path = f"{file_path}.ORIGINAL"

        if os.path.exists(file_path):
            # Make a backup of the original file
            shutil.copyfile(file_path, backup_file_path)

            # Replace references to old jobs with new one
            subprocess.run(
                [
                    "sed",
                    "-i",
                    f"-e s/JOBID={old_JOBID}/JOBID={new_JOBID}/g",
                    f"-e s/RUNID={old_RUNID}/RUNID={new_RUNID}/g",
                    f"-e s/CJOBN={old_RUNID}/CJOBN={new_RUNID}/g",
                    f"-e s/JOB_ID='{old_JOBID}'/JOB_ID='{new_JOBID}'/g",
                    f"-e s/EXPT_ID='{old_EXPTID}'/EXPT_ID='{new_EXPTID}'/g",
                    f"-e s/EXPTID={old_EXPTID}/EXPTID={new_EXPTID}/g",
                    f"-e s/RUN_JOB_NAME='{old_RUNID}/RUN_JOB_NAME='{new_RUNID}/g",
                    f"-e s/Run {old_EXPTID}#{old_JOBID}/Run {new_EXPTID}#{new_JOBID}/g",
                    file_path,
                ]
            )

    print(f"Duplicated job {old_RUNID} to {new_RUNID}")
    return True


import logging
from datetime import datetime


def setup_logging(ensemble_exp, log_dir):
    """
    Sets up logging to both console and file.

    Args:
        ensemble_exp (str): The ensemble experiment name to include in the log file name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Define log directory and ensure it exists
    os.makedirs(log_dir, exist_ok=True)  # Create log directory if it does not exist

    # Get current date in YYYYMMDD format
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(
        log_dir, f"{ensemble_exp}_ensemble_jobs_generator_{current_date}.log"
    )

    # Remove existing log file if it exists
    if os.path.isfile(log_file):
        os.remove(log_file)

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create a console handler for logging to the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    generated_ids_log_file = os.path.join(
        log_dir, f"{ensemble_exp}_generated_ids_{current_date}.log"
    )
    generated_params_log_file = os.path.join(
        log_dir, f"{ensemble_exp}_updated_parameters_{current_date}.json"
    )
    if os.path.exists(generated_ids_log_file):
        os.remove(generated_ids_log_file)
    if os.path.exists(generated_params_log_file):
        os.remove(generated_params_log_file)

    return logger, generated_ids_log_file, generated_params_log_file


# save the parameters to a JSON file with custom formatting
# which will look like the following:
# {
#   "F0": [0.901, 0.859, 0.896, 0.733, 0.86],
#   "LAI_MIN": [4.0, 4.0, 1.0, 1.0, 1.0],
#   "NL0": [0.05, 0.03, 0.06, 0.03, 0.03],
#   "R_GROW": [0.25, 0.25, 0.25, 0.25, 0.25],
#   "TLOW": [0.0, -5.0, 0.0, 13.0, 0.0],
#   "TUPP": [36.0, 31.0, 36.0, 45.0, 36.0],
#   "V_CRIT_ALPHA": [0.343]
# },
def _format_json_string(item):
    formatted_str = "{\n"
    formatted_str += ",\n".join(
        f'  "{key}": {json.dumps(value)}' for key, value in item.items()
    )
    formatted_str += "\n}"
    return formatted_str


def create_json_file(filename, data, default_params):
    with open(filename, "w") as file:
        file.write("[\n")
        # write default parameters as first set
        formatted_str = _format_json_string(default_params)
        formatted_str += ","
        indented_str = "    " + formatted_str.replace("\n", "\n    ")
        file.write(indented_str)
        file.write("\n")
        # write all perturbed parameter sets
        for i, item in enumerate(data):
            formatted_str = _format_json_string(item)
            if i < len(data) - 1:
                formatted_str += ","
            indented_str = "    " + formatted_str.replace("\n", "\n    ")
            file.write(indented_str)
            if i < len(data) - 1:
                file.write("\n")
        file.write("\n]")


def plot_param_distributions(
    perturbed_sets, perturbed_BL_params, pdf_file, ensemble_name
):
    labels = ["BL", "NL", "C3 grass", "C4 grass", "Shrub"]

    # create a single PDF file to save the individual pages
    with PdfPages(pdf_file) as pdf:
        # loop over the PFTs
        for idx in range(5):
            print(f"Plotting paramater distributions for {labels[idx]}")
            fig, axs = plt.subplots(3, 2, figsize=(12, 12))
            fig.suptitle(
                f"Distributions of perturbed parameters for {labels[idx]} ({ensemble_name})"
            )

            param_keys = list(perturbed_BL_params.keys())

            for i, key in enumerate(param_keys):
                values = []
                for params in perturbed_sets:
                    if (
                        key == "V_CRIT_ALPHA"
                        and isinstance(params[key], list)
                        and len(params[key]) == 1
                    ):
                        values.append(params[key][0])
                    elif (
                        key in params
                        and isinstance(params[key], list)
                        and len(params[key]) > idx
                    ):
                        values.append(params[key][idx])
                    else:
                        print(
                            f"Warning: Skipping invalid entry for key '{key}' at index {idx}."
                        )
                        continue

                row = i // 2
                col = i % 2
                axs[row, col].hist(values, bins=30, color="skyblue", edgecolor="black")
                axs[row, col].set_title(f"{key} Distribution")
                axs[row, col].set_xlabel(f"{key}")
                axs[row, col].set_ylabel("Frequency")

            plt.tight_layout(rect=[0, 0, 1, 0.96])

            # Save the current figure to the PDF as a new page
            pdf.savefig(fig)

            # Close the current figure to release memory
            plt.close(fig)

    print(f"All plots saved to '{pdf_file}'")
