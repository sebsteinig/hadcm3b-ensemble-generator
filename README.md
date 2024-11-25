# HadCM3B land carbon cycle ensembles
This repo contains scripts and instructions to automatically generate ensembles of UM jobs. These ensembles are intended to test a large range of model parameters for the interactive land carbon cylce component added by Chris Jones. The goal is to run the short, standard preindustrial simulation with hundreds (or thousands) of different tuning parameters to ultimately identify one (or several) promising parameter sets to use as a baseline configuration for the new HadCM3BL version with a fully coupled carbon cycle. 

## example workflow
Let's assume we want to create and run an ensemble of 250 simulations, each with random values of a configurable list land carbon cycle parameters to assess the model sensitivity against the parameter choice. For this, we would need to go through the following steps:

1. create vanilla UMUI job
- create the standard experiment job within the UMUI on PUMA2, i.e. define the scientific settings, restart files and run length which should be the same for all ensemble members
- importantly, add the following mod to the list of modifications within the UMUI: `/user/home/wb19586/um_updates/znamelist_hadcm3m21_land_cc_v2.mod`
and this post-processing script: `~ssteinig/scripts/land_cc_v2`
- the mod will allow to read in the otherwise hard-coded land carbon cycle parameters from the external `CNTLATM` namelist, while the script will populate the namelist with some standard values to get started 
- once finished, click `Processing` within the UMUI and copy the output directory from `umui_jobs` on PUMA2 to BC4 (from BC4: `rsync -avz -e 'ssh -J ssteinig@login.archer2.ac.uk:' ssteinig@puma2:~/umui_jobs/<JOBID> ~/umui_jobs`)

2. compile the vanilla job
- compile executable with `clustersubmit -s y -r bc4 <JOBID>`
- move the executable to any directory of your choice and point to it in `~/umui_jobs/<JOBID>/SCRIPT` under `LOADMODULE=...`
- this will allow us to always use the same executable for all ensemble members without the need to recompile again

3. generate ensemble parameters
- we need to create a list of parameter sets (one set for each ensemble member) that we actually want to insert into the respective `CNTLATM` namelists
- this can be done with the `create_param_table_random.py` script (there are also similar script available to only vary a single parameter at a time (`create_param_table_single.py`) or to create soil carbon tuning parameters based on previous random configurations `create_param_table_csoil_from_candidates.py`)
- in `create_param_table_random.py` we need to define the ensemble experiment name (you might want to reserve this namespace within the UMUI) and the number of ensemble members we want to create (N)
- next, we specify the list of parameters we want to modify in our namelist (e.g. "ALPHA", "G_AREA", ...) and reasonable min/max values for each
- the script will then randomly pick a value for the BL parameter and also change the values for the other PFTS pro-rata
- the final parameter sets and a quick visualisation are written to the `param_tables/` directory
- the script can easily be modified to change the name of the parameters and how the new values are generated (e.g. random, explicit, ...) 

4. create ensemble jobs
- we can now create the actual ensemble jobs within `~/umui_jobs/` with `create_ensemble_jobs.py`
- as inputs we need to spcify the vanilla job from steps 1+2, the ensemble parameter file from step 3 and 
- example: `python create_ensemble_jobs.py --vanilla_job ~/hadcm3b-ensemble-generator/vanilla_jobs/xqapa --parameter_file ./param_tables/xqaRw_csoil.json --ensemble_exp xqaRw`

5. submit ensemble jobs
- to avoid disk quota issues on BC4, we can run the ensemble jobs on the private BRIDGE partition `/mnt/storage/private/bridge/um_output` with `create_job_dirs.sh` to create only symlinks in the user's dump2hold directory
- input to this is the log fiile of generated IDs from step 4
- finally, submit all jobs to the BC4 queue with `submit_all_jobs.sh`, again, using the previous logfile to loop over all new IDs 