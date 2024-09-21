import random
from helpers import create_json_file, plot_param_distributions

ensemble_name = "xqau"

output_file = f"./param_tables/{ensemble_name}.json"
pdf_file = f"./param_tables/{ensemble_name}_param_distributions.pdf"

N = 256  # number of perturbed parameter sets to generate

#  default parameter set from “acang” (MetOffice C4MIP run from 2006)
default_params = {
    "ALPHA": [0.08, 0.08, 0.08, 0.05, 0.08],
    "G_AREA": [0.004, 0.004, 0.10, 0.10, 0.05],
    "LAI_MIN": [4.0, 4.0, 1.0, 1.0, 1.0],
    "NL0": [0.050, 0.030, 0.060, 0.030, 0.030],
    "R_GROW": [0.25, 0.25, 0.25, 0.25, 0.25],
    "TLOW": [0.0, -5.0, 0.0, 13.0, 0.0],
    "TUPP": [36.0, 31.0, 36.0, 45.0, 36.0],
    "V_CRIT_ALPHA": [0.343],
}

# define perturbation ranges for each parameter
# new parameter sets will generate a random value for each parameter within the defined ranges
# new, random values are defined for BL, other PFTs are changed pro-rata based on the
# BL difference from the default
perturbed_BL_params = {
    "ALPHA": [0.04, 0.16], # min/max values for BL, other PFTs changed pro-rata
    "G_AREA": [0.002, 0.008],  # min/max values for BL, other PFTs changed pro-rata
    "LAI_MIN": [2.0, 4.0],  # min/max values for trees; keep at 1.0 for grass/shrubs
    "NL0": [0.040, 0.065],  # min/max values for BL, other PFTs changed pro-rata
    "R_GROW": [0.15, 0.30],  # min/max values; same for all PFTs
    "TLOW": [
        -5.0,
        5.0,
    ],  # min/max delta range around the default; co-vary TLOW and TUPP
    "V_CRIT_ALPHA": [0.3, 1.0],  # min/max absolute values; single value
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
    if key in ["F0", "NL0", "ALPHA", "G_AREA"]:
        delta_bl = new_bl_param - defaults[0]
        for i in range(len(defaults)):
            perturbed_list[i] += delta_bl
    elif key == "LAI_MIN":
        perturbed_list[0] = new_bl_param
        perturbed_list[1] = new_bl_param
    elif key == "R_GROW" or key == "V_CRIT_ALPHA":
        perturbed_list = [new_bl_param for _ in perturbed_list]
    elif key == "TLOW" or key == "TUPP":
        perturbed_list = [default + new_bl_param for default in perturbed_list]

    perturbed_list = [round(value, 5) for value in perturbed_list]
    return perturbed_list


perturbed_sets = generate_random_perturbed_params(
    default_params, perturbed_BL_params, N
)

# save the parameters to a JSON file with custom formatting
create_json_file(output_file, perturbed_sets, default_params)

print(f"Generated {len(perturbed_sets)} parameter sets and saved to '{output_file}'")

plot_param_distributions(perturbed_sets, perturbed_BL_params, pdf_file, ensemble_name)
