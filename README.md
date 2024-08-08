# hadcm3b-ensembles
scripts to create parameter ensemble jobs for HadCM3B

read land CC paramters from namelis (mods for model):
`$PV_UPDATES/znamelist_hadcm3m21_land_cc.mod`

create default land CC parameter namelist (post-processings scripts): 
`~ssteinig/scripts/land_cc_acang`


### use pre-compiled binary for all ensemble members
1. compile vanilla job
2. copy executable to `~/dump2hold/execs_cc_seb`
3. set `MY_EXECS` (Sub-Model Independent > File & Directory Naming) and the exec directory and file name (Compilation and Modifications > Compile options for the model) to this new file path

### create new ensemble
1. copy vanilla job from PUMA2 to BC4:
`rsync -avz -e 'ssh -J ssteinig@login.archer2.ac.uk:' ssteinig@puma2:~/umui_jobs/xpzna ~/umui_jobs`
2. create a parameter table (JSON) containing the new sets of model parameters for each ensemble member:
   `python create_param_table.py` or `python create_param_table_random.py`
