﻿"""Model inputs to run PyGEM"""

# Built-in libraries
import os
# External libraries
import pandas as pd
import numpy as np


#%% Functions to select specific glacier numbers
def get_same_glaciers(glac_fp):
    """
    Get same 1000 glaciers for testing of priors

    Parameters
    ----------
    glac_fp : str
        filepath to where netcdf files of individual glaciers are held

    Returns
    -------
    glac_list : list
        list of rgi glacier numbers
    """
    glac_list = []
    for i in os.listdir(glac_fp):
        if i.endswith('.nc'):
            glac_list.append(i.split('.')[1])
    glac_list = sorted(glac_list)
    return glac_list


def get_shean_glacier_nos(region_no, number_glaciers=0, option_random=0):
    """
    Generate list of glaciers that have calibration data and select number of glaciers to include.

    The list is currently sorted in terms of area such that the largest glaciers are modeled first.

    Parameters
    ----------
    region_no : int
        region number (Shean data available for regions 13, 14, and 15)
    number_glaciers : int
        number of glaciers to include in model run (default = 0)
    option_random : int
        option to select glaciers randomly for model run (default = 0, not random)

    Returns
    -------
    num : list of strings
        list of rgi glacier numbers
    """
    # safety, convert input to int
    region_no = int(region_no)
    # get shean's data, convert to dataframe, get
    # glacier numbers
    current_directory = os.getcwd()
    csv_path = current_directory + '/../DEMs/Shean_2019_0213/hma_mb_20190215_0815_std+mean_all_filled_bolch.csv'
    ds_all = pd.read_csv(csv_path)
    ds_reg = ds_all[(ds_all['RGIId'] > region_no) & (ds_all['RGIId'] < region_no + 1)].copy()
    if option_random == 1:
        ds_reg = ds_reg.sample(n=number_glaciers)
    else:
        ds_reg = ds_reg.sort_values('area_m2', ascending=False)
    ds_reg.reset_index(drop=True, inplace=True)
    
    
    # Glacier number and index for comparison
    ds_reg['glacno'] = ((ds_reg['RGIId'] % 1) * 10**5).round(0).astype(int)
    ds_reg['glacno_str'] = (ds_reg['glacno'] / 10**5).apply(lambda x: '%.5f' % x).astype(str).str.split('.').str[1]
    num = list(ds_reg['glacno_str'].values)
    num = sorted(num)
    return num


def glac_num_fromrange(int_low, int_high):
    """
    Generate list of glaciers for all numbers between two integers.

    Parameters
    ----------
    int_low : int64
        low value of range
    int_high : int64
        high value of range

    Returns
    -------
    y : list
        list of rgi glacier numbers
    """
    x = (np.arange(int_low, int_high+1)).tolist()
    y = [str(i).zfill(5) for i in x]
    return y

def glac_fromcsv(csv_fullfn, cn='RGIId'):
    """
    Generate list of glaciers from csv file
    
    Parameters
    ----------
    csv_fp, csv_fn : str
        csv filepath and filename
    
    Returns
    -------
    y : list
        list of glacier numbers, e.g., ['14.00001', 15.00001']
    """
    df = pd.read_csv(csv_fullfn)
    return [x.split('-')[1] for x in df['RGIId'].values]


#%%
# Model setup directory
main_directory = os.getcwd()
# Output directory
output_filepath = main_directory + '/../Output/'

# ===== GLACIER SELECTION =====
rgi_regionsO1 = [15]            # 1st order region number (RGI V6.0)
rgi_regionsO2 = 'all'           # 2nd order region number (RGI V6.0)
# RGI glacier number (RGI V6.0)
#  Two options: (1) use glacier numbers for a given region (or 'all'), must have glac_no set to None
#               (2) glac_no is not None, e.g., ['1.00001', 13.0001'], overrides rgi_glac_number
#rgi_glac_number = 'all'
rgi_glac_number = ['03473']
#rgi_glac_number = glac_num_fromrange(1,5)
#rgi_glac_number = get_same_glaciers(output_filepath + 'cal_opt1/reg1/')
#rgi_glac_number = get_shean_glacier_nos(rgi_regionsO1[0], 1, option_random=1)
glac_no = None
#glac_no = glac_fromcsv(main_directory + '/../qgis_himat/trishuli_and_naltar_RGIIds.csv')
#glac_no = ['13.26960', '15.00002', '14.01243']
if glac_no is not None:
    rgi_regionsO1 = sorted(list(set([int(x.split('.')[0]) for x in glac_no])))

# ===== CLIMATE DATA ===== 
# Reference period runs
#ref_gcm_name = 'ERA-Interim'    # reference climate dataset
ref_gcm_name = 'ERA5'           # reference climate dataset

#startyear = 1980                # first year of model run (reference dataset)
#endyear = 2017                  # last year of model run (reference dataset)
#option_wateryear = 1            # 1: water year, 2: calendar year, 3: custom defined 
startyear = 2000                # first year of model run (reference dataset)
endyear = 2018                  # last year of model run (reference dataset)
option_wateryear = 3            # 1: water year, 2: calendar year, 3: custom defined 

spinupyears = 0                 # spin up years
constantarea_years = 0          # number of years to not let the area or volume change

# Simulation runs (separate so calibration and simulations can be run at same time; also needed for bias adjustments)
gcm_startyear = 2000            # first year of model run (simulation dataset)
gcm_endyear = 2017              # last year of model run (simulation dataset)
#gcm_startyear = 2000            # first year of model run (simulation dataset)
#gcm_endyear = 2100              # last year of model run (simulation dataset)
gcm_spinupyears = 0             # spin up years for simulation
gcm_wateryear = 1               # water year for simmulation

# Hindcast option (flips array so 1960-2000 would run 2000-1960 ensuring that glacier area at 2000 is correct)
hindcast = 0                    # 1: run hindcast simulation, 0: do not
if hindcast == 1:
    constantarea_years = 18     # number of years to not let the area or volume change
    gcm_startyear = 1960        # first year of model run (simulation dataset)
    gcm_endyear = 2017          # last year of model run (simulation dataset)

# Synthetic options (synthetic refers to created climate data, e.g., repeat 1995-2015 for the next 100 years)
option_synthetic_sim = 0        # 1: run synthetic simulation, 0: do not
if option_synthetic_sim == 1:
    synthetic_startyear = 1995      # synthetic start year
    synthetic_endyear = 2015        # synethetic end year
    synthetic_spinupyears = 0       # synthetic spinup years
    synthetic_temp_adjust = 3       # Temperature adjustment factor for synthetic runs
    synthetic_prec_factor = 1.12    # Precipitation adjustment factor for synthetic runs

#%% SIMULATION OPTIONS
# MCMC options
sim_iters = 1   # number of simulations (needed for cal_opt 2)
sim_burn = 200  # number of burn-in (needed for cal_opt 2)

# Simulation output filepath
output_sim_fp = output_filepath + 'simulations/'
# Simulation output statistics (can include 'mean', 'std', '2.5%', '25%', 'median', '75%', '97.5%')
sim_stat_cns = ['mean', 'std']
# Bias adjustment options (0: no adjustment, 1: new prec scheme and temp from HH2015, 2: HH2015 methods)
option_bias_adjustment = 1

#%% ===== CALIBRATION OPTIONS =====
# Calibration option (1 = minimization, 2 = MCMC, 3=HH2015, 4=modified HH2015)
option_calibration = 2
# Calibration datasets ('shean', 'larsen', 'mcnabb', 'wgms_d', 'wgms_ee', 'group')
cal_datasets = ['shean']
# Calibration output filepath
output_fp_cal = output_filepath + 'cal_opt' + str(option_calibration) + '/'

# OPTION 1: Minimization
# Model parameter bounds for each calibration roun
#precfactor_bnds_list_init = [(0.9, 1.125), (0.8,1.25), (0.5,2), (0.33,3)]
#precgrad_bnds_list_init = [(0.0001,0.0001), (0.0001,0.0001), (0.0001,0.0001), (0.0001,0.0001)]
#ddfsnow_bnds_list_init = [(0.0036, 0.0046), (0.0036, 0.0046), (0.0026, 0.0056), (0.00185, 0.00635)]
#tempchange_bnds_list_init = [(-1,1), (-2,2), (-5,5), (-10,10)]
precfactor_bnds_list_init = [(0.8, 2.0), (0.8,2), (0.8,2), (0.2,5)]
precgrad_bnds_list_init = [(0.0001,0.0001), (0.0001,0.0001), (0.0001,0.0001), (0.0001,0.0001)]
ddfsnow_bnds_list_init = [(0.003, 0.003), (0.00175, 0.0045), (0.00175, 0.0045), (0.00175, 0.0045)]
tempchange_bnds_list_init = [(0,0), (0,0), (-2.5,2.5), (-10,10)]
# Minimization details 
method_opt = 'SLSQP'            # SciPy optimization scheme ('SLSQP' or 'L-BFGS-B')
ftol_opt = 1e-3                 # tolerance for SciPy optimization scheme
massbal_uncertainty_mwea = 0.1  # mass balance uncertainty [mwea] for glaciers lacking uncertainty data
zscore_tolerance_all = 1        # tolerance if multiple calibration points (shortcut that could be improved)
zscore_tolerance_single = 0.1   # tolerance if only a single calibration point (want this to be more exact)
zscore_update_threshold = 0.1   # threshold to update model params only if significantly better
extra_calrounds = 3             # additional calibration rounds in case optimization is getting stuck

# OPTION 2: MCMC
# Chain options
n_chains = 1                    # number of chains (min 1, max 3)
mcmc_sample_no = 10000          # number of steps (10000 was found to be sufficient in HMA)
mcmc_burn_no = 0                # number of steps to burn-in (0 records all steps in chain)
mcmc_step = None                # step option (None or 'am')
thin_interval = 1               # thin interval if need to reduce file size (best to leave at 1 if space allows)
# Precipitation factor distribution options
precfactor_disttype = 'gamma'   # distribution type ('gamma', 'lognormal', 'uniform')
precfactor_gamma_region_dict = {'Altun Shan': [8.52, 2.54],
                                'Central Himalaya': [2.52, 1.38],
                                'Central Tien Shan': [1.81, 1.37],
                                'Dzhungarsky Alatau': [2.85, 1.49],
                                'Eastern Himalaya': [3.03, 1.65],
                                'Eastern Hindu Kush': [2.86, 1.87],
                                'Eastern Kunlun Shan': [2.55, 1.45],
                                'Eastern Pamir': [1.21, 1.48],
                                'Eastern Tibetan Mountains': [3.92, 2.14],
                                'Eastern Tien Shan': [1.86, 1.24],
                                'Gangdise Mountains': [3.66, 1.73],
                                'Hengduan Shan': [4.88, 1.95],
                                'Karakoram': [1.29, 1.47],
                                'Northern/Western Tien Shan': [2.61, 1.48],
                                'Nyainqentanglha': [6.48, 2.33],
                                'Pamir Alay': [3.3, 1.88],
                                'Qilian Shan': [2.74, 1.36],
                                'Tanggula Shan': [9.03, 2.92],
                                'Tibetan Interior Mountains': [2.41, 1.35],
                                'Western Himalaya': [2.15, 1.53],
                                'Western Kunlun Shan': [1.21, 1.64],
                                'Western Pamir': [1.85, 1.44]}
precfactor_gamma_alpha = 3.0
precfactor_gamma_beta = 0.84
precfactor_lognorm_mu = 0
precfactor_lognorm_tau = 4
precfactor_mu = 0
precfactor_sigma = 1.5
precfactor_boundlow = 0.5
precfactor_boundhigh = 1.5
precfactor_start = 1
# Temperature bias distribution options
tempchange_disttype = 'normal'  # distribution type ('normal', 'truncnormal', 'uniform')
tempchange_norm_region_dict = {'Altun Shan': [-0.60, 1.09],
                               'Central Himalaya': [0.13, 0.9],
                               'Central Tien Shan': [0.4, 0.85],
                               'Dzhungarsky Alatau': [0.1, 0.51],
                               'Eastern Himalaya': [-0.01, 0.87],
                               'Eastern Hindu Kush': [0.08, 1.19],
                               'Eastern Kunlun Shan': [0.13, 0.58],
                               'Eastern Pamir': [0.93, 1.06],
                               'Eastern Tibetan Mountains': [0.06, 0.45],
                               'Eastern Tien Shan': [0.45, 1.58],
                               'Gangdise Mountains': [-0.06, 0.41],
                               'Hengduan Shan': [-0.28, 0.68],
                               'Karakoram': [1.39, 1.54],
                               'Northern/Western Tien Shan': [0.09, 0.66],
                               'Nyainqentanglha': [-0.41, 0.83],
                               'Pamir Alay': [-0.03, 0.72],
                               'Qilian Shan': [0.22, 0.83],
                               'Tanggula Shan': [-0.13, 0.33],
                               'Tibetan Interior Mountains': [0.15, 0.75],
                               'Western Himalaya': [0.11, 0.79],
                               'Western Kunlun Shan': [2.27, 1.79],
                               'Western Pamir': [0.54, 1.2]}
tempchange_mu = 0.91
tempchange_sigma = 1.4
tempchange_boundlow = -10
tempchange_boundhigh = 10
tempchange_start = tempchange_mu
tempchange_step = 0.1
# Degree-day factor of snow distribution options
ddfsnow_disttype = 'truncnormal' # distribution type ('truncnormal', 'uniform')
ddfsnow_mu = 0.0041
ddfsnow_sigma = 0.0015
ddfsnow_boundlow = 0
ddfsnow_boundhigh = np.inf
ddfsnow_start=ddfsnow_mu

#%% MODEL PARAMETERS
option_import_modelparams = 1       # 0: input values, 1: calibrated model parameters from netcdf files
precfactor = 1                      # precipitation factor [-] (k_p in Radic etal 2013; c_prec in HH2015)
precgrad = 0.0001                   # precipitation gradient on glacier [m-1]
ddfsnow = 0.0041                    # degree-day factor of snow [m w.e. d-1 degC-1]
ddfsnow_iceratio = 0.7              # Ratio degree-day factor snow snow to ice
ddfice = ddfsnow / ddfsnow_iceratio # degree-day factor of ice [m w.e. d-1 degC-1]
tempchange = 0                      # temperature bias [deg C]
lrgcm = -0.0065                     # lapse rate from gcm to glacier [K m-1]
lrglac = -0.0065                    # lapse rate on glacier for bins [K m-1]
tempsnow = 1.0                      # temperature threshold for snow [deg C] (HH2015 used 1.5 degC +/- 1 degC)
frontalablation_k = 2               # frontal ablation rate [yr-1]
af = 0.7                            # Bulk flow parameter for frontal ablation (m^-0.5)
# Calving width dictionary to override RGI elevation bins, which can be highly inaccurate at the calving front
width_calving_dict = {'RGI60-01.01390':5730,
                      'RGI60-01.03622':1860,
                      'RGI60-01.10689':4690,
                      'RGI60-01.13638':940,
                      'RGI60-01.14443':6010,
                      'RGI60-01.14683':2240,
                      'RGI60-01.14878':1570,
                      'RGI60-01.17807':2130,
                      'RGI60-01.17840':980,
                      'RGI60-01.17843':1030,
                      'RGI60-01.17876':1390,
                      'RGI60-01.20470':1200,
                      'RGI60-01.20783':760,
                      'RGI60-01.20841':420,
                      'RGI60-01.20891':2050,
                      'RGI60-01.21001':1580,
                      'RGI60-01.23642':2820,
                      'RGI60-01.26736':3560}
# Calving option
#  option 1 - use values from HH2015
#  option 2 - calibrate each glacier independently, use transfer functions for uncalibrated glaciers
option_frontalablation_k = 1
# Calving parameter dictionary (according to Supplementary Table 3 in HH2015)
frontalablation_k0dict = {
            1:  3.4,
            2:  0,
            3:  0.2,
            4:  0.2,
            5:  0.5,
            6:  0.3,
            7:  0.5,
            8:  0,
            9:  0.2,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 6,
            18: 0,
            19: 1}

# Model parameter column names and filepaths
modelparams_colnames = ['lrgcm', 'lrglac', 'precfactor', 'precgrad', 'ddfsnow', 'ddfice', 'tempsnow', 'tempchange']
# Model parameter filepath
if option_calibration == 1:
    modelparams_fp_dict = {
            1:  output_filepath + 'cal_opt1/reg1/',
            3:  output_filepath + 'cal_opt1/',
            4:  output_filepath + 'cal_opt1/',
            6:  output_filepath + 'cal_opt1/reg6/',
            13: output_filepath + 'cal_opt1/reg13/',
            14: output_filepath + 'cal_opt1/reg14/',
            15: output_filepath + 'cal_opt1/reg15/'}
elif option_calibration == 2:
#    modelparams_fp_dict = {
#            13: output_filepath + 'cal_opt2/',
#            14: output_filepath + 'cal_opt2/',
#            15: output_filepath + 'cal_opt2/'}
    modelparams_fp_dict = {
            13: output_filepath + 'cal_opt2_spc_20190806/',
            14: output_filepath + 'cal_opt2_spc_20190806/',
            15: output_filepath + 'cal_opt2_spc_20190806/'}

#%% CLIMATE DATA
# ERA-INTERIM (Reference data)
# Variable names
era_varnames = ['temperature', 'precipitation', 'geopotential', 'temperature_pressurelevels']
#  Note: do not change variable names as these are set to run with the download_erainterim_data.py script.
#        If option 2 is being used to calculate the lapse rates, then the pressure level data is unnecessary.
# Dates
eraint_start_date = '19790101'
eraint_end_date = '20180501'
# Resolution
grid_res = '0.5/0.5'
# Bounding box (N/W/S/E)
#bounding_box = '90/0/-90/360'
bounding_box = '50/70/25/105'
# Lapse rate option
#  option 0 - lapse rates are constant defined by input
#  option 1 (default) - lapse rates derived from gcm pressure level temperature data (varies spatially and temporally)
#  option 2 - lapse rates derived from surrounding pixels (varies spatially and temporally)
#    Note: Be careful with option 2 as the ocean vs land/glacier temperatures can causeƒ unrealistic inversions
#          This is the option used by Marzeion et al. (2012)
option_lr_method = 1

# ERA5
era5_fp = main_directory + '/../Climate_data/ERA5/'
era5_temp_fn = 'ERA5_temp_monthly.nc'
era5_tempstd_fn = 'ERA5_tempstd_monthly.nc'
era5_prec_fn = 'ERA5_totalprecip_monthly.nc'
era5_elev_fn = 'ERA5_geopotential_monthly.nc'
era5_pressureleveltemp_fn = 'ERA5_pressureleveltemp_monthly.nc'
era5_lr_fn = 'ERA5_lapserates_monthly.nc'

# ERA-Interim
eraint_fp = main_directory + '/../Climate_data/ERA_Interim/download/'
eraint_temp_fn = 'ERAInterim_Temp2m_DailyMeanMonthly_' + eraint_start_date + '_' + eraint_end_date + '.nc'
eraint_prec_fn = 'ERAInterim_TotalPrec_DailyMeanMonthly_' + eraint_start_date + '_' + eraint_end_date + '.nc'
eraint_elev_fn = 'ERAInterim_geopotential.nc'
eraint_pressureleveltemp_fn = 'ERAInterim_pressureleveltemp_' + eraint_start_date + '_' + eraint_end_date + '.nc'
eraint_lr_fn = ('ERAInterim_lapserates_' + eraint_start_date + '_' + eraint_end_date + '_opt' + str(option_lr_method) +
                '_world.nc')

# CMIP5 (GCM data)
cmip5_fp_var_prefix = main_directory + '/../Climate_data/cmip5/'
cmip5_fp_var_ending = '_r1i1p1_monNG/'
cmip5_fp_fx_prefix = main_directory + '/../Climate_data/cmip5/'
cmip5_fp_fx_ending = '_r0i0p0_fx/'
cmip5_fp_lr = main_directory + '/../Climate_data/cmip5/bias_adjusted_1995_2100/2018_0524/'
cmip5_lr_fn = 'biasadj_mon_lravg_1995_2015_R15.csv'

# COAWST (High-resolution climate data over HMA)
coawst_fp_unmerged = main_directory + '/../Climate_data/coawst/Monthly/'
coawst_fp = main_directory + '/../Climate_data/coawst/'
coawst_fn_prefix_d02 = 'wrfout_d02_Monthly_'
coawst_fn_prefix_d01 = 'wrfout_d01_Monthly_'
coawst_temp_fn_d02 = 'wrfout_d02_Monthly_T2_1999100100-2006123123.nc'
coawst_prec_fn_d02 = 'wrfout_d02_Monthly_TOTPRECIP_1999100100-2006123123.nc'
coawst_elev_fn_d02 = 'wrfout_d02_Monthly_HGHT.nc'
coawst_temp_fn_d01 = 'wrfout_d01_Monthly_T2_1999100100-2006123123.nc'
coawst_prec_fn_d01 = 'wrfout_d01_Monthly_TOTPRECIP_1999100100-2006123123.nc'
coawst_elev_fn_d01 = 'wrfout_d01_Monthly_HGHT.nc'
coawst_vns = ['T2', 'TOTPRECIP', 'HGHT']
coawst_d02_lon_min = 65
coawst_d02_lon_max = 99
coawst_d02_lat_min = 20
coawst_d02_lat_max = 38

#%% GLACIER DATA (RGI, ICE THICKNESS, ETC.)
# ===== RGI DATA =====
# Filepath for RGI files
rgi_filepath = main_directory + '/../RGI/rgi60/00_rgi60_attribs/'
# Column names
rgi_lat_colname = 'CenLat'
rgi_lon_colname = 'CenLon'
elev_colname = 'elev'
indexname = 'GlacNo'
rgi_O1Id_colname = 'glacno'
rgi_glacno_float_colname = 'RGIId_float'
# Column names from table to drop
rgi_cols_drop = ['GLIMSId','BgnDate','EndDate','Status','Connect','Linkages','Name']
# Dictionary of hypsometry filenames
rgi_dict = {
            1:  '01_rgi60_Alaska.csv',
            3:  '03_rgi60_ArcticCanadaNorth.csv',
            4:  '04_rgi60_ArcticCanadaSouth.csv',
            6:  '06_rgi60_Iceland.csv',
            7:  '07_rgi60_Svalbard.csv',
            8:  '08_rgi60_Scandinavia.csv',
            9:  '09_rgi60_RussianArctic.csv',
            13: '13_rgi60_CentralAsia.csv',
            14: '14_rgi60_SouthAsiaWest.csv',
            15: '15_rgi60_SouthAsiaEast.csv',
            16: '16_rgi60_LowLatitudes.csv',
            17: '17_rgi60_SouthernAndes.csv'}

# ===== ADDITIONAL DATA (hypsometry, ice thickness, width) =====
# Option to shift all elevation bins by 20 m
#  (required for Matthias' ice thickness and area since they are 20 m off, see email from May 24 2018)
option_shift_elevbins_20m = 1
# Elevation band height [m]
binsize = 10
# Filepath for the hypsometry files
hyps_filepath = main_directory + '/../IceThickness_Huss/bands_10m_DRR/'
# Dictionary of hypsometry filenames
# (Files from Matthias Huss should be manually pre-processed to be 'RGI-ID', 'Cont_range', and bins starting at 5)
hyps_filedict = {
                1:  'area_01_Huss_Alaska_10m.csv',
                3:  'area_RGI03_10.csv',
                4:  'area_RGI04_10.csv',
                6:  'area_RGI06_10.csv',
                7:  'area_RGI07_10.csv',
                8:  'area_RGI08_10.csv',
                9:  'area_RGI09_10.csv',
                13: 'area_13_Huss_CentralAsia_10m.csv',
                14: 'area_14_Huss_SouthAsiaWest_10m.csv',
                15: 'area_15_Huss_SouthAsiaEast_10m.csv',
                16: 'area_16_Huss_LowLatitudes_10m.csv',
                17: 'area_17_Huss_SouthernAndes_10m.csv'}
# Extra columns in hypsometry data that will be dropped
hyps_colsdrop = ['RGI-ID','Cont_range']
# Filepath for the ice thickness files
thickness_filepath = main_directory + '/../IceThickness_Huss/bands_10m_DRR/'
# Dictionary of thickness filenames
thickness_filedict = {
                1:  'thickness_01_Huss_Alaska_10m.csv',
                3:  'thickness_RGI03_10.csv',
                4:  'thickness_RGI04_10.csv',
                6:  'thickness_RGI06_10.csv',
                7:  'thickness_RGI07_10.csv',
                8:  'thickness_RGI08_10.csv',
                9:  'thickness_RGI09_10.csv',
                13: 'thickness_13_Huss_CentralAsia_10m.csv',
                14: 'thickness_14_Huss_SouthAsiaWest_10m.csv',
                15: 'thickness_15_Huss_SouthAsiaEast_10m.csv',
                16: 'thickness_16_Huss_LowLatitudes_10m.csv',
                17: 'thickness_17_Huss_SouthernAndes_10m.csv'}
# Extra columns in ice thickness data that will be dropped
thickness_colsdrop = ['RGI-ID','Cont_range']
# Filepath for the width files
width_filepath = main_directory + '/../IceThickness_Huss/bands_10m_DRR/'
# Dictionary of thickness filenames
width_filedict = {
                1:  'width_01_Huss_Alaska_10m.csv',
                3:  'width_RGI03_10.csv',
                4:  'width_RGI04_10.csv',
                6:  'width_RGI06_10.csv',
                7:  'width_RGI07_10.csv',
                8:  'width_RGI08_10.csv',
                9:  'width_RGI09_10.csv',
                13: 'width_13_Huss_CentralAsia_10m.csv',
                14: 'width_14_Huss_SouthAsiaWest_10m.csv',
                15: 'width_15_Huss_SouthAsiaEast_10m.csv',
                16: 'width_16_Huss_LowLatitudes_10m.csv',
                17: 'width_17_Huss_SouthernAndes_10m.csv'}
# Extra columns in ice thickness data that will be dropped
width_colsdrop = ['RGI-ID','Cont_range']

#%% MODEL TIME FRAME DATA
# Models require complete data for each year such that refreezing, scaling, etc. can be calculated
# Leap year option
option_leapyear = 1         # 1: include leap year days, 0: exclude leap years so February always has 28 days
# User specified start/end dates
#  note: start and end dates must refer to whole years
startmonthday = '06-01'
endmonthday = '05-31'
wateryear_month_start = 10  # water year starting month
winter_month_start = 10     # first month of winter (for HMA winter is October 1 - April 30)
summer_month_start = 5      # first month of summer (for HMA summer is May 1 - Sept 30)
option_dates = 1            # 1: use dates from date table (first of each month), 2: dates from climate data
timestep = 'monthly'        # time step ('monthly' only option at present)

# Seasonal dictionaries for WGMS data that is not provided
lat_threshold = 75
# Winter (start/end) and Summer (start/end)
monthdict = {'northernmost': [9, 5, 6, 8],
             'north': [10, 4, 5, 9],
             'south': [4, 9, 10, 3],
             'southernmost': [3, 10, 11, 2]}
# Latitude threshold
# 01 - Alaska - < 75
# 02 - W Can - < 75
# 03 - N Can - > 74
# 04 - S Can - < 74
# 05 - Greenland - 60 - 80
# 06 - Iceland - < 75
# 07 - Svalbard - 70 - 80
# 08 - Scandinavia - < 70
# 09 - Russia - 72 - 82
# 10 - N Asia - 46 - 77


#%% CALIBRATION DATASETS
# ===== SHEAN GEODETIC =====
shean_fp = main_directory + '/../DEMs/Shean_2019_0213/'
shean_fn = 'hma_mb_20190215_0815_std+mean_all_filled_bolch.csv'
shean_rgi_glacno_cn = 'RGIId'
shean_mb_cn = 'mb_mwea'
shean_mb_err_cn = 'mb_mwea_sigma'
shean_time1_cn = 't1'
shean_time2_cn = 't2'
shean_area_cn = 'area_m2'

# ===== BRUN GEODETIC =====
brun_fp = main_directory + '/../DEMs/'
brun_fn = 'Brun_Nature2017_MB_glacier-wide.csv'
brun_rgi_glacno_cn = 'GLA_ID'
brun_mb_cn = 'MB [m w.a a-1]'
brun_mb_err_cn = 'err. on MB [m w.e a-1]'
# NEED TO FINISH SETTING UP BRUN WITH CLASS_MBDATA

# ===== MAUER GEODETIC =====
mauer_fp = main_directory + '/../DEMs/'
mauer_fn = 'Mauer_geoMB_HMA_1970s_2000_min80pctCov.csv'
mauer_rgi_glacno_cn = 'RGIId'
mauer_mb_cn = 'geoMassBal'
mauer_mb_err_cn = 'geoMassBalSig'
mauer_time1_cn = 't1'
mauer_time2_cn = 't2'

# ===== MCNABB GEODETIC =====
mcnabb_fp = main_directory + '/../DEMs/McNabb_data/wgms_dv/'
mcnabb_fn = 'Alaska_dV_17jun_preprocessed.csv'
mcnabb_rgiid_cn = 'RGIId'
mcnabb_mb_cn = 'mb_mwea'
mcnabb_mb_err_cn = 'mb_mwea_sigma'
mcnabb_time1_cn = 'date0'
mcnabb_time2_cn = 'date1'
mcnabb_area_cn = 'area'

# ===== LARSEN GEODETIC =====
larsen_fp = main_directory + '/../DEMs/larsen/'
larsen_fn = 'larsen2015_supplementdata_wRGIIds_v3.csv'
larsen_rgiid_cn = 'RGIId'
larsen_mb_cn = 'mb_mwea'
larsen_mb_err_cn = 'mb_mwea_sigma'
larsen_time1_cn = 'date0'
larsen_time2_cn = 'date1'
larsen_area_cn = 'area'

# ===== WGMS =====
wgms_datasets = ['wgms_d', 'wgms_ee']
#wgms_datasets = ['wgms_d']
wgms_fp = main_directory + '/../WGMS/DOI-WGMS-FoG-2018-06/'
wgms_rgi_glacno_cn = 'glacno'
wgms_obs_type_cn = 'obs_type'
# WGMS lookup tables information
wgms_lookup_fn = 'WGMS-FoG-2018-06-AA-GLACIER-ID-LUT.csv'
rgilookup_fullfn = main_directory + '/../RGI/rgi60/00_rgi60_links/00_rgi60_links.csv'
rgiv6_fn_prefix = main_directory + '/../RGI/rgi60/00_rgi60_attribs/' + '*'
rgiv5_fn_prefix = main_directory + '/../RGI/00_rgi50_attribs/' + '*'

# WGMS (d) geodetic mass balance information
wgms_d_fn = 'WGMS-FoG-2018-06-D-CHANGE.csv'
wgms_d_fn_preprocessed = 'wgms_d_rgiv6_preprocessed.csv'
wgms_d_thickness_chg_cn = 'THICKNESS_CHG'
wgms_d_thickness_chg_err_cn = 'THICKNESS_CHG_UNC'
wgms_d_volume_chg_cn = 'VOLUME_CHANGE'
wgms_d_volume_chg_err_cn = 'VOLUME_CHANGE_UNC'
wgms_d_z1_cn = 'LOWER_BOUND'
wgms_d_z2_cn = 'UPPER_BOUND'

# WGMS (e/ee) glaciological mass balance information
wgms_e_fn = 'WGMS-FoG-2018-06-E-MASS-BALANCE-OVERVIEW.csv'
wgms_ee_fn = 'WGMS-FoG-2018-06-EE-MASS-BALANCE.csv'
wgms_ee_fn_preprocessed = 'wgms_ee_rgiv6_preprocessed.csv'
wgms_ee_mb_cn = 'BALANCE'
wgms_ee_mb_err_cn = 'BALANCE_UNC'
wgms_ee_t1_cn = 'YEAR'
wgms_ee_z1_cn = 'LOWER_BOUND'
wgms_ee_z2_cn = 'UPPER_BOUND'
wgms_ee_period_cn = 'period'

# ===== COGLEY DATA =====
cogley_fp = main_directory + '/../Calibration_datasets/'
cogley_fn_preprocessed = 'Cogley_Arctic_processed_wInfo.csv'
cogley_rgi_glacno_cn = 'glacno'
cogley_mass_chg_cn = 'geo_mass_kgm2a'
cogley_mass_chg_err_cn = 'geo_mass_unc'
cogley_z1_cn = 'Zmin'
cogley_z2_cn = 'Zmax'
cogley_obs_type_cn = 'obs_type'

# ===== REGIONAL DATA =====
# Regional data refers to all measurements that have lumped multiple glaciers together
#  - a dictionary linking the regions to RGIIds is required
mb_group_fp = main_directory + '/../Calibration_datasets/'
mb_group_dict_fn = 'mb_group_dict.csv'
mb_group_data_fn = 'mb_group_data.csv'
mb_group_t1_cn = 'begin_period'
mb_group_t2_cn = 'end_period'

#%% REGIONS
grouping = 'himap'
if grouping == 'watershed':
    reg_vn = 'watershed'
    reg_dict_fn = main_directory + '/../qgis_himat/rgi60_HMA_dict_watershed.csv'
    reg_csv = pd.read_csv(reg_dict_fn)
    reg_dict = dict(zip(reg_csv.RGIId, reg_csv[reg_vn]))
elif grouping == 'kaab':
    reg_vn = 'kaab_name'
    reg_dict_fn = main_directory + '/../qgis_himat/rgi60_HMA_dict_kaab.csv'
    reg_csv = pd.read_csv(reg_dict_fn)
    reg_dict = dict(zip(reg_csv.RGIId, reg_csv[reg_vn]))
elif grouping == 'himap':
    reg_vn = 'bolch_name'
    reg_dict_fn = main_directory + '/../qgis_himat/rgi60_HMA_dict_bolch.csv'
    reg_csv = pd.read_csv(reg_dict_fn)
    reg_dict = dict(zip(reg_csv.RGIId, reg_csv[reg_vn]))

#%% MASS BALANCE MODEL OPTIONS
# Initial surface type options
option_surfacetype_initial = 1
#  option 1 (default) - use median elevation to classify snow/firn above the median and ice below.
#   > Sakai et al. (2015) found that the decadal ELAs are consistent with the median elevation of nine glaciers in High
#     Mountain Asia, and Nuimura et al. (2015) also found that the snow line altitude of glaciers in China corresponded
#     well with the median elevation.  Therefore, the use of the median elevation for defining the initial surface type
#     appears to be a fairly reasonable assumption in High Mountain Asia.
#  option 2 (Need to code) - use mean elevation instead
#  option 3 (Need to code) - specify an AAR ratio and apply this to estimate initial conditions
option_surfacetype_firn = 1         # 1: firn included; 0: no included (firn is snow)
option_surfacetype_debris = 0       # 1: debris cover included; 0: not included

# Downscaling model options
# Reference elevation options for downscaling climate variables
option_elev_ref_downscale = 'Zmed'  # 'Zmed', 'Zmax', or 'Zmin' for median, maximum or minimum glacier elevations
# Downscale temperature to bins options
option_temp2bins = 1                # 1: lr_gcm and lr_glac to adjust temp from gcm to the glacier bins
option_adjusttemp_surfelev = 1      # 1: adjust temps based on surface elev changes; 0: no adjustment
# Downscale precipitation to bins options
option_prec2bins = 1                # 1: prec_factor and prec_grad to adjust precip from gcm to the glacier bins
option_preclimit = 1                # 1: limit the uppermost 25% using an expontial fxn

# Accumulation model options
#  option 1 - Single threshold (<= snow, > rain)
#  option 2 - single threshold +/- 1 deg uses linear interpolation
option_accumulation = 2

# Ablation model options
#  option 1 - use monthly temperature
#  option 2 - use standard deviation of monthly temperature enabling melt during transition season (Huss and Hock 2015)
option_ablation = 1
option_ddf_firn = 1                 # 0: ddf_firn = ddf_snow; 1: ddf_firn = mean of ddf_snow and ddf_ice
ddfdebris = ddfice                  # add options for handling debris-covered glaciers

# Refreezing model options
#  option 1 - heat conduction approach (Huss and Hock, 2015)
#  option 2 - annual air temperature appraoch (Woodward et al., 1997)
option_refreezing = 2
# Refreeze depth [m]
rf_month = 10                       # refreeze month (required for option 2)

# Mass redistribution / Glacier geometry change options
option_massredistribution = 1       # 1: mass redistribution (Huss and Hock, 2015)
option_glaciershape = 1             # 1: parabolic (Huss and Hock, 2015), 2: rectangular, 3: triangular
option_glaciershape_width = 1       # 1: include width, 0: do not include
icethickness_advancethreshold = 5   # advancing glacier ice thickness change threshold (5 m in Huss and Hock, 2015)
terminus_percentage = 20            # glacier (%) considered terminus (20% in HH2015), used to size advancing new bins

#%% OUTPUT OPTIONS
# Output package
#  option 0 - no netcdf package
#  option 1 - "raw package" [preferred units: m w.e.]
#              monthly variables for each bin (temp, prec, acc, refreeze, snowpack, melt, frontalablation,
#                                              massbal_clim)
#              annual variables for each bin (area, icethickness, surfacetype)
#  option 2 - "Glaciologist Package" output [units: m w.e. unless otherwise specified]:
#              monthly glacier-wide variables (prec, acc, refreeze, melt, frontalablation, massbal_total, runoff,
#                                              snowline)
#              annual glacier-wide variables (area, volume, ELA)
output_package = 2
output_glacier_attr_vns = ['glacno', 'RGIId_float', 'CenLon', 'CenLat', 'O1Region', 'O2Region', 'Area', 'Zmin', 'Zmax',
                           'Zmed', 'Slope', 'Aspect', 'Lmax', 'Form', 'TermType', 'Surging']
time_names = ['time', 'year', 'year_plus1']
# Output package variables
output_variables_package2 = ['temp_glac_monthly', 'prec_glac_monthly', 'acc_glac_monthly',
                            'refreeze_glac_monthly', 'melt_glac_monthly', 'frontalablation_glac_monthly',
                            'massbaltotal_glac_monthly', 'runoff_glac_monthly', 'snowline_glac_monthly',
                            'area_glac_annual', 'volume_glac_annual', 'ELA_glac_annual',
                            'offglac_prec_monthly', 'offglac_refreeze_monthly', 'offglac_melt_monthly',
                            'offglac_snowpack_monthly', 'offglac_runoff_monthly']

#%% MODEL PROPERTIES
density_ice = 900           # Density of ice [kg m-3] (or Gt / 1000 km3)
density_water = 1000        # Density of water [kg m-3]
area_ocean = 362.5 * 10**6  # Area of ocean [km2]
ch_ice = 1.89 * 10**6       # Heat capacity of ice [J K-1 kg-1]
k_ice = 2.33                # Thermal conductivity of ice [W K-1 m-1]
tolerance = 1e-12           # Model tolerance (used to remove low values caused by rounding errors)
gravity = 9.81              # Gravity [m s-2]
pressure_std = 101325       # Standard pressure [Pa]
temp_std = 288.15           # Standard temperature [K]
R_gas = 8.3144598           # Universal gas constant [J mol-1 K-1]
molarmass_air = 0.0289644   # Molar mass of Earth's air [kg mol-1]

# Pass variable to shell script
if __name__ == '__main__':
    print(rgi_regionsO1[0])
    print(rgi_glac_number[0:10])
