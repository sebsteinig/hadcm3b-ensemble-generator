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

3. create ensemble parameters
- we need to create a list of parameter sets (one set for each ensemble member) that we actually want to insert into the respective `CNTLATM` namelist
- this can be done with the `create_param_table_random.py` script (there are also similar script available to only vary a single parameter at a time (`create_param_table_single.py`) or to create soil carbon tuning parameters based on previous random configurations `create_param_table_csoil_from_candidates.py`)

### use pre-compiled binary for all ensemble members
1. compile vanilla job
2. copy executable to `~/dump2hold/execs_cc_seb`
3. set `MY_EXECS` (Sub-Model Independent > File & Directory Naming) and the exec directory and file name (Compilation and Modifications > Compile options for the model) to this new file path

### create new ensemble
1. copy vanilla job from PUMA2 to BC4:
`rsync -avz -e 'ssh -J ssteinig@login.archer2.ac.uk:' ssteinig@puma2:~/umui_jobs/xpzna ~/umui_jobs`
2. create a parameter table (JSON) containing the new sets of model parameters for each ensemble member:
   `python create_param_table.py` or `python create_param_table_random.py`
