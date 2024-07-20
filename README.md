# hadcm3b-ensembles
scripts to create parameter ensemble jobs for HadCM3B

read land CC paramters from namelis (mods for model):
`$PV_UPDATES/znamelist_hadcm3m21_land_cc.mod`

create default land CC parameter namelist (post-processings scripts): 
`~ssteinig/scripts/land_cc_acang`

copy vanilla job from PUMA2 to BC4:
`rsync -avz -e 'ssh -J ssteinig@login.archer2.ac.uk:' ssteinig@puma2:~/umui_jobs/xpzna ~/umui_jobs`

