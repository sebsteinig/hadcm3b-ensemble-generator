import random
from helpers import create_json_file, plot_param_distributions

ensemble_name = "xqac_csoil"

output_file = f"./param_tables/{ensemble_name}.json"
pdf_file = f"./param_tables/{ensemble_name}_param_distributions.pdf"

N = 100  # number of perturbed parameter sets to generate

#  form xQabn, i.e. the ensemble memeber with best skill score from xqab
default_params = {
    "F0": [0.847, 0.847, 0.872, 0.772, 0.872],
    "LAI_MIN": [3.801, 3.801, 1.0, 1.0, 1.0],
    "NL0": [0.054, 0.034, 0.064, 0.034, 0.034],
    "R_GROW": [0.169, 0.169, 0.169, 0.169, 0.169],
    "TLOW": [3.703, -1.297, 3.703, 16.703, 3.703],
    "TUPP": [39.703, 34.703, 39.703, 48.703, 39.703],
    "V_CRIT_ALPHA": [0.765],
    "Q10": [2.0],
    "KAPS": [5.0e-009],

}

# define perturbation ranges for each parameter
# new parameter sets will generate a random value for each parameter within the defined ranges
# new, random values are defined for BL, other PFTs are changed pro-rata based on the
# BL difference from the default
perturbed_BL_params = {
    "F0": [0.847, 0.847],  # min/max values for BL, other PFTs changed pro-rata
    "LAI_MIN": [3.801, 3.801],  # min/max values for trees; keep at 1.0 for grass/shrubs
    "NL0": [0.054, 0.054],  # min/max values for BL, other PFTs changed pro-rata
    "R_GROW": [0.169, 0.169],  # min/max values; same for all PFTs
    "TLOW": [
        0.0,
        0.0,
    ],  # min/max delta range around the default; co-vary TLOW and TUPP
    "V_CRIT_ALPHA": [0.765, 0.765],  # min/max absolute values; single value
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
        perturbed_list = [round(value, 3) for value in perturbed_list]
    return perturbed_list


perturbed_sets = generate_random_perturbed_params(
    default_params, perturbed_BL_params, N
)

# save the parameters to a JSON file with custom formatting
create_json_file(output_file, perturbed_sets, default_params)

print(f"Generated {len(perturbed_sets)} parameter sets and saved to '{output_file}'")

plot_param_distributions(perturbed_sets, perturbed_BL_params, pdf_file, ensemble_name)
