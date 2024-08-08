from helpers import create_json_file, plot_param_distributions

ensemble_name = "acang_single_param_tuning"

output_file = f"./param_tables/{ensemble_name}.json"
pdf_file = f"./param_tables/{ensemble_name}_param_distributions.pdf"

#  default parameter set from “acang” (MetOffice C4MIP run from 2006)
default_params = {
    "F0": [0.875, 0.875, 0.900, 0.800, 0.900],
    "LAI_MIN": [4.0, 4.0, 1.0, 1.0, 1.0],
    "NL0": [0.050, 0.030, 0.060, 0.030, 0.030],
    "R_GROW": [0.25, 0.25, 0.25, 0.25, 0.25],
    "TLOW": [0.0, -5.0, 0.0, 13.0, 0.0],
    "TUPP": [36.0, 31.0, 36.0, 45.0, 36.0],
    "V_CRIT_ALPHA": [0.343],
}

# define perturbation values each parameter
# if absolute ranges are defined for BL, other PFTs are changed pro-rata based on the
# BL difference from the default
perturbed_BL_params = {
    "F0": [
        0.8,
        0.85,
        0.90,
        0.95,
    ],  # absolute values for BL, other PFTs changed pro-rata
    "LAI_MIN": [
        1.0,
        2.0,
        3.0,
        4.0,
    ],  # absolute values for trees; keep at 1.0 for grass/shrubs
    "NL0": [
        0.035,
        0.045,
        0.055,
        0.065,
    ],  # absolute values for BL, other PFTs changed pro-rata
    "R_GROW": [0.150, 0.185, 0.22, 0.30],  # absolute values; same for all PFTs
    "TLOW": [-5.0, -2.5, 2.5, 5.0],  # delta range around the default
    "V_CRIT_ALPHA": [0.0, 0.25, 0.5, 0.75, 1.0],  # absolute values; single value
}


def generate_perturbed_params(default_params, new_params):
    perturbed_sets = []
    # generate perturbed sets for each key individually
    for key in new_params:
        perturbed_sets.extend(perturb_params(key, default_params, new_params))
    return perturbed_sets


def perturb_params(key, defaults, new_params):
    perturbed_sets = []
    # generate a new set for each defined perturbed value
    for idx in range(len(new_params[key])):
        # copy default set first and then onlu update the current key
        perturbed_set = defaults.copy()
        perturbed_set[key] = perturb_list(defaults[key], key, new_params[key][idx])
        if key == "TLOW":
            perturbed_set["TUPP"] = perturb_list(
                defaults["TUPP"], "TUPP", new_params["TLOW"][idx]
            )
        perturbed_sets.append(perturbed_set)
    return perturbed_sets


# Function to perturb a list of values
def perturb_list(defaults, key, new_bl_param):
    perturbed_list = defaults.copy()
    if key == "F0" or key == "NL0":
        delta_bl = new_bl_param - defaults[0]
        for i in range(0, len(defaults)):
            perturbed_list[i] += delta_bl
    elif key == "LAI_MIN":
        perturbed_list[0] = new_bl_param
        perturbed_list[1] = new_bl_param
    elif key == "R_GROW" or key == "V_CRIT_ALPHA":
        perturbed_list = [new_bl_param for _ in perturbed_list]
    elif key == "TLOW" or key == "TUPP":
        perturbed_list = [default + new_bl_param for default in perturbed_list]

    perturbed_list = [round(value, 3) for value in perturbed_list]
    return perturbed_list


perturbed_sets = generate_perturbed_params(default_params, perturbed_BL_params)

# save the parameters to a JSON file with custom formatting
create_json_file(output_file, perturbed_sets, default_params)

print(
    f"generated {len(perturbed_sets) + 1} parameter sets and saved to '{output_file}'"
)

plot_param_distributions(perturbed_sets, perturbed_BL_params, pdf_file, ensemble_name)
