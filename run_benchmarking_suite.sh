#!/bin/bash

################################################################################
# configuration section
# JSON file containing labeled namelist blocks with each parameter set 
################################################################################
param_file="input_params/TOP20_LAND_CC_params_for_benchmarking.json"
benchmark_exp_name="xqbb"
data_dir="$HOME/dump2hold"
jobs_dir="$HOME/umui_jobs"
################################################################################
# list of benchmarking steps to run
steps_to_run=("step1" "step2")
# step 1: no dependencies -> can be started right away 
#     1a: CONC - spin-up eqbm TRIFFID (40 years)
#     1b: CONC - LGM Peltier (200 years from equilibrium)
#     1c: CONC - Scotese_097 (200 years from equilibrium)
# step 2: cont. of step 1 
#     2a: CONC - spin-up dyn TRIFFID (200 years)
# step 3: cont. of step 2
#     3a: CONC - lig127k (100 years)
#     3b: CONC - 1% CO2 scenario COU (150 years)
#     3c: CONC - 1% CO2 scenario BGC (150 years)
#     3d: CONC - 1% CO2 scenario RAD (150 years)
#     3e: CONC - abrupt-4xCO2 (150 years)
#     3f: CONC - historical (150+ years)
#     3g: EMMI - spin-up with zero emissions  (1200 years)
# step 4: cont. of step 3g at year 200
#     4a: EMMI - historical with emissions (150+ years)
#     4b: EMMI - flat10 (300 years)
# step 5: cont. of step 4b at year 100
#     5a: EMMI - flat10-zec, i.e. zero emissions (200 years)
#     5b: EMMI - flat10-cdr, i.e. negative emissions (200 years)

################################################################################
# some functions for code reusability
################################################################################

# check if ocean and atmosphere restart files exit for given model and year
restarts_exist() {
    local id=$1
    local year=$2
    
    local da_ATM="${data_dir}/${id}/datam/${id}a#da00000${year}c1+"
    local da_OCN="${data_dir}/${id}/datam/${id}o#da00000${year}c1+"

    if [ -f "$da_ATM" ] && [ -f "$da_OCN" ]; then
        echo "$da_ATM and $da_OCN found for $id at year $year. Continuing with next task ..."
        return 0
    elif [ ! -f "$da_ATM" ]; then
        echo "$da_ATM missing for $id at year $year"
        return 1
    elif [ ! -f "$da_OCN" ]; then
        echo "$da_OCN missing for $id at year $year"
        return 1
    fi
}

# check if SLURM job is already submitted (i.e. pending or running)
job_is_submitted() {
    local id=$1
    local job_name=${id}000
    job_status=$(squeue -h -n "$job_name" -o %t)  # get the status of the job by name (-n)

    if [[ "$job_status" == *"R"* ]] || [[ "$job_status" == *"PD"* ]]; then
        return 0  # job is running or pending
    else
        return 1  # job has completed or failed
    fi
}

# get reference/vanilla job template for current step
get_template_job() {
    local step=$1
    local ref_job
    local start_year

    case $step in
        "1a")
            ref_job="xqaza"
            start_year="1850"
            ;;
        "1b")
            ref_job="xqazb"
            start_year="1850"
            ;;
        "1c")
            ref_job="xqazc"
            start_year="1850"
            ;;
        "2a")
            ref_job="xqazd"
            start_year="1890"
            ;;
        *)
            echo "unknown step $step"
            return 1  # return non-zero for unknown steps (error)
            ;;
    esac

    echo "$ref_job $restart_year"  # output both variables separated by a space
    return 0  # success
}


check_progress() {
    local id=$1
    local step=$2
    local year=$3

    echo "checking step ${step} for ${id}"

    local job_name=${id}${step}

    if restarts_exist ${job_name} $year; then
        echo "Step ${step} completed. Nothing to do."
        return 0
    else
        if job_is_submitted ${job_name}; then
            echo "Job ${job_name} for step ${step} is already submitted. Nothing to do."
        else
            if [ ! -d ${jobs_dir}/${job_name} ]; then
                echo "No UMUI job ${job_name} for step ${step} found. Creating job now ..."
                template_properties=$(get_template_job "$step")

                if [ $? -eq 0 ]; then
                    template_job=$(echo "$template_properties" | awk '{print $1}')
                    start_year=$(echo "$template_properties" | awk '{print $2}')
                    echo "Template Job: $template_job, Restart Year: $restart_year"
                else
                    echo "Failed to get template job for step $template_job"
                    break
                fi
                # use script from Paul at /mnt/storage/private/bridge/swsvalde/bin/new_expt_letter
                new_expt_letter "${template_job}" ${job_name}

                # overwrite namelist parameters in CNTLATM
                escaped_params=$(echo "$params" | sed ':a;N;$!ba;s/\n/\\n/g')
                sed -i "/^ &LAND_CC/,/^ &END/c\\
                ${escaped_params}
                " "${jobs_dir}/${job_name}/CNTLATM"

                echo "submitting job for step ${step}"
                clustersubmit -s y -c n -a y -r bc4 -q cpu -w 14-00:00:00 ${job_name}
            fi
        fi
        return 1
    fi

}

################################################################################
# MAIN starts here
################################################################################

# main loop over each experiment in the JSON file
jq -r 'keys[]' "$param_file" | while read -r experiment_label; do

    ensemble_id=$benchmark_exp_name$experiment_label

    # get information from JSON file
    description=$(jq -r .$experiment_label.description $param_file)
    params_raw=$(jq .$experiment_label.params $param_file)
    # format parameters
    params=$(printf '%s\n' "${params_raw[@]}" | tr -d '"' | sed '1d;$d' | sed 's/,$//')
    params=$(echo "$params" | sed '1s/^[[:space:]]*//' | sed '2,$s/^[[:space:]]*/ /')

    # some log output
    echo "######################################################################"
    echo "checking on ensemble $ensemble_id"
    echo "description:" $description
    echo "params:" "$params"

    # check on all benchmarking steps
    for step in "${steps_to_run[@]}"; do
        echo "######################################################################"
        echo "checking step $step for $ensemble_id"
        case $step in
            "step1")   
                check_progress ${ensemble_id} "1b" 2050
                check_progress ${ensemble_id} "1c" 2050
                if ! check_progress ${ensemble_id} "1a" 1890; then
                    echo "!!!step 1a not completed yet. Continuing with next ensemble!!!"
                break 
            fi
                ;;
            "step2")
                if ! check_progress ${ensemble_id} "2a" 2090; then
                    echo "!!!step 2a not completed yet. Continuing with next ensemble!!!"
                break 
                ;;
            *)
                echo "unknown step $step"
                ;;
        esac
    done


done