import random
import json
from helpers import create_json_file, plot_param_distributions

ensemble_name = "xqac_csoil"

default_params_file = f"./input_params/top_random_candidates_parameters.json"

N = 50  # number of perturbed parameter sets to generate

# define perturbation ranges for each parameter
# new parameter sets will generate a random value for each parameter within the defined ranges
# new, random values are defined for BL, other PFTs are changed pro-rata based on the
# BL difference from the default
perturbed_BL_params = {
    "Q10": [1.5, 2.5],
    "KAPS": [2.5e-009, 7.5e-009],
}


def generate_random_perturbed_params(default_params, new_params, N):
    perturbed_sets = []
    for _ in range(N):
        perturbed_set = {}
        for key in new_params:
            random_value = random.uniform(new_params[key][0], new_params[key][1])
            perturbed_set[key] = perturb_list(default_params[key], key, random_value)
            if key == "TLOW":
                perturbed_set["TUPP"] = perturb_list(
                    default_params["TUPP"], "TUPP", random_value
                )
        perturbed_sets.append(perturbed_set)
    return perturbed_sets


# Function to perturb a list of values
def perturb_list(defaults, key, new_bl_param):
    perturbed_list = defaults.copy()
    if key == "F0" or key == "NL0":
        delta_bl = new_bl_param - defaults[0]
        for i in range(len(defaults)):
            perturbed_list[i] += delta_bl
    elif key == "LAI_MIN":
        perturbed_list[0] = new_bl_param
        perturbed_list[1] = new_bl_param
    elif key == "R_GROW" or key in ["V_CRIT_ALPHA", "Q10", "KAPS"]:
        perturbed_list = [new_bl_param for _ in perturbed_list]
    elif key == "TLOW" or key == "TUPP":
        perturbed_list = [default + new_bl_param for default in perturbed_list]

    if key == "KAPS":
        perturbed_list = [value for value in perturbed_list]
    else:
        perturbed_list = [round(value, 5) for value in perturbed_list]
    return perturbed_list


# load in the default parameter sets for each potential candidate

with open(default_params_file) as f:
    data = json.load(f)

    # Loop through each ensemble and read the parameters
    for ensemble in data:
        ensemble_id = ensemble.get("ensemble_id", "Unknown ID")

        default_params = {
            "ALPHA": ensemble.get("ALPHA", []),
            "G_AREA": ensemble.get("G_AREA", []),
            "LAI_MIN": ensemble.get("LAI_MIN", []),
            "NL0": ensemble.get("NL0", []),
            "R_GROW": ensemble.get("R_GROW", []),
            "TLOW": ensemble.get("TLOW", []),
            "TUPP": ensemble.get("TUPP", []),
            "V_CRIT_ALPHA": ensemble.get("V_CRIT_ALPHA", []),
            "Q10": [2.0],
            "KAPS": [5.0e-009],
        }

        perturbed_BL_params = {
            "ALPHA": [default_params["ALPHA"][0], default_params["ALPHA"][0]],
            "G_AREA": [default_params["G_AREA"][0], default_params["G_AREA"][0]],
            "LAI_MIN": [default_params["LAI_MIN"][0], default_params["LAI_MIN"][0]],
            "NL0": [default_params["NL0"][0], default_params["NL0"][0]],
            "R_GROW": [default_params["R_GROW"][0], default_params["R_GROW"][0]],
            "TLOW": [0, 0],
            "TUPP": [0, 0],
            "V_CRIT_ALPHA": [
                default_params["V_CRIT_ALPHA"][0],
                default_params["V_CRIT_ALPHA"][0],
            ],
            "Q10": [1.5, 2.5],
            "KAPS": [2.5e-009, 7.5e-009],
        }

        perturbed_sets = generate_random_perturbed_params(
            default_params, perturbed_BL_params, N
        )

        output_file = f"./param_tables/{ensemble_id}_csoil.json"
        pdf_file = f"./param_tables/{ensemble_id}_csoil_param_distributions.pdf"

        # save the parameters to a JSON file with custom formatting
        create_json_file(output_file, perturbed_sets, default_params)

        print(
            f"Generated {len(perturbed_sets)} parameter sets and saved to '{output_file}'"
        )

        plot_param_distributions(
            perturbed_sets, perturbed_BL_params, pdf_file, ensemble_id
        )
