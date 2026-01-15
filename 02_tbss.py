import os
import sys
import numpy as np

################################################################
########################## OVERVIEW ############################
################################################################

# Script 2 of 2

# This code is designed for a one-against-many analysis, i.e. an
# analysis where 1 patient is compared to 20 age- and sex-
# matched healthy controls. There needs to be at least 20 controls
# to reach a p-value < 0.05.

# First run Script 1 to copy control and patient DTI maps into correct folders.
# Script 2 is designed to run tract-based spatial statistics (TBSS) on 1 patient
# compared to 20 healthy age- and sex-matched controls. It compares DTI
# FA, MD, AD and RD.

# DTI parameter maps have previously been calculated using FSL's dtifit.

# Note: This code assumes all DTI parameter maps are in the following structure
# under the current directory:
##### (1) Control files should begin with name 'CON'
##### (2) Patient files should begin with 'PATIENT' and their ID.
##### (3) All FA files will be in the current directory.
##### (4) All MD, AD, RD files will be in a folders called MD, AD, or RD.

# Define the stats directory.
stats_dir = './stats/'

# We start with FA. Please run this script from its actual location (preferably under a folder called 'tbss').
# I do not recommend moving it. 

##### STEP 1

# Prepare the FA data in the TBSS working directory in the right format. The command erodes FA images slightly 
# and zeros the end slices (to remove outliers from diffusion tensor fitting).
os.system('tbss_1_preproc *.nii.gz')

input("Have you been a responsible neuroimaging researcher and checked the generated webpage? Press Enter.") 
input("Are you lying? No? Then, press Enter to continue...")

##### STEP 2

# Apply nonlinear registration of all FA images into standard space (1x1x1 mm). I use the '-T' flag, so 
# FMRIB58_FA standard-space image is used as the target. The '-t' flag can be used if you supply your own
# target image. The '-n' flag can be used to identify the 'most representative' image and use that as
# the target image, which is then transformed to MNI152 space.
os.system('tbss_2_reg -T')

##### STEP 3

# Create the mean FA image and skeletonise it. The nonlinear transforms found from Step 2 are applied to 
# all subjects to bring them into a standard space. These images are then merged into a single 4D image
# file called 'all_FA', created in a new subdirected called 'stats'. The mean of all FA images is created,
# called 'mean_FA' and this is then fed into the FA skeletonisation program to create 'mean_FA_skeleton'.
# The FA white matter skeleton corresponds to the FAs at the centre of the white matter tracts. 
# Note, the flag '-T' can be used instead, which means that a template white matter skeleton is instead
# used, from FMRIB58_FA. Here, we use the FA skeletonisation program to make a participant-specific 
# FA white matter skeleton.
os.system('tbss_3_postreg -S')

# Check the white matter skeleton to make sure it corresponds to the centre of the white matter tracts.
# You will be able to click through and check every participant to ensure that the white matter skeleton
# seems reasonable for all patients and controls. 

print('Check your white matter skeleton.')
os.system('fsleyes stats/all_FA.nii.gz -dr 0 0.8 stats/mean_FA_skeleton.nii.gz -dr 0.2 0.8 -cm green')

##### STEP 4

# Project all subjects' FA data onto the mean FA skeleton. This carries out the final steps necessary
# before running the voxelwise cross-subject stats. It thresholds the mean FA skeleton image at the 
# chosen threshold. Typically, the 0.2 threshold works (which is what was plotted above). The value
# '0.2' is used here, but it can be replaced with a different threshold if necessary.

os.system('tbss_4_prestats 0.2')

##### STEP 5: Voxelwise statistics

# Step 4 resulted in a 4D skeletonised FA image, called 'all_FA_skeletonised', located in 'stats'. 
# It is with this FA skeleton that you now use for voxelwise statistics, which tells you which FA
# skeleton voxels are significantly different between two groups of subjects.

# Check the order of your files. Make sure the 20 controls are listed before your 1 patient file
# if you are running a one-against-many analysis.
print('Check there are 20 controls before your 1 patient file.')
os.system('imglob FA/*_FA.*')

input("Does the correct number of controls before your 1 patient file exist? Are you sure? Press " \
    "Enter to continue...")

# In the simple case of a two-group comparison (or one-against-many comparison), you can use 
# design_ttest2. You need to put in the number of controls (which should have been listed first
# in your imglob command), and then the number of patients. This designs the design matrix and 
# contrasts files.
os.system('design_ttest2 stats/design_FA 20 1')

# The 'randomise' tool is used to do the stats. This is a non-parametric, permutation-based approach.
# A group of 20 controls for 1 patient is the minimum number required for significant of p<0.05,
# where the smallest attainable p-value is 1/Nperm and Nperm is the number of unique permutations.
# In this case, I put '500' as the number of permutations as a dummy variable. Only 21 permutations
# are possible in the one-against-many case. The '--T2' flag means 'threshold-free cluster enhancement'
# or TFCE, which improves the sensitivty of statistical detection by enhancing cluster-like structures
# in the data without requiring an arbitrary cluster-forming threshold.
os.system('randomise -i stats/all_FA_skeletonised.nii.gz -o stats/tbss_FA -m ' \
    'stats/mean_FA_skeleton_mask -d stats/design_FA.mat -t stats/design_FA.con -n 500 --T2')

# Check over the output. THIS IS *NOT* THE STATISTICALLY SIGNIFICANT VALUES.
print('Check over the TBSS analysis changes in the skeleton (these are not the significant changes).')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.8 ' \
    'stats/tbss_FA_tstat1.nii.gz -cm red-yellow -dr 3 6 stats/tbss_FA_tstat2.nii.gz -cm blue-lightblue -dr 3 6')

# Check over the output. This *is* the statistically significant values. Note: The scale is 1 - pvalue,
# so this means that thresholding at 0.95 corresponds to a p-value of 0.05. 
print('And now onto the p<0.05 results...')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.7 ' \
    'stats/tbss_FA_tfce_corrp_tstat1.nii.gz -cm red-yellow -dr 0.95 1 stats/tbss_FA_tfce_corrp_tstat2.nii.gz '
    '-cm blue-lightblue -dr 0.95 1')

##### STEP 6: Moving onto MD values

#Note: The FA white matter skeleton is used for MD, AD, and RD. No need to re-run the skeleton.
os.system('tbss_non_FA MD')

os.system('design_ttest2 stats/design_MD 20 1')
os.system('randomise -i stats/all_MD_skeletonised.nii.gz -o stats/tbss_MD -m stats/mean_FA_skeleton_mask '
    '-d stats/design_MD.mat -t stats/design_MD.con -n 500 --T2')

print('Check the MD TBSS analysis changes in the skeleton. These are not the significant changes.')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.8 ' \
    'stats/tbss_MD_tstat1.nii.gz -cm red-yellow -dr 3 6 stats/tbss_MD_tstat2.nii.gz -cm blue-lightblue -dr 3 6')

print('MD p<0.05 results...')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.7 ' \
    'stats/tbss_MD_tfce_corrp_tstat1.nii.gz -cm red-yellow -dr 0.95 1 stats/tbss_MD_tfce_corrp_tstat2.nii.gz '
    '-cm blue-lightblue -dr 0.95 1')

##### STEP 7: Moving onto AD values

#Note: The FA white matter skeleton is used for MD, AD, and RD. No need to re-run the skeleton.
os.system('tbss_non_FA AD')

os.system('design_ttest2 stats/design_AD 20 1')
os.system('randomise -i stats/all_AD_skeletonised.nii.gz -o stats/tbss_AD -m stats/mean_FA_skeleton_mask '
    '-d stats/design_AD.mat -t stats/design_AD.con -n 500 --T2')

print('Check the AD TBSS analysis changes in the skeleton. These are not the significant changes.')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.8 ' \
    'stats/tbss_AD_tstat1.nii.gz -cm red-yellow -dr 3 6 stats/tbss_AD_tstat2.nii.gz -cm blue-lightblue -dr 3 6')

print('AD p<0.05 results...')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.7 ' \
    'stats/tbss_AD_tfce_corrp_tstat1.nii.gz -cm red-yellow -dr 0.95 1 stats/tbss_AD_tfce_corrp_tstat2.nii.gz '
    '-cm blue-lightblue -dr 0.95 1')

##### STEP 8: Moving onto RD values

#Note: The FA white matter skeleton is used for MD, AD, and RD. No need to re-run the skeleton.
os.system('tbss_non_FA RD')

os.system('design_ttest2 stats/design_RD 20 1')
os.system('randomise -i stats/all_RD_skeletonised.nii.gz -o stats/tbss_RD -m stats/mean_FA_skeleton_mask '
    '-d stats/design_RD.mat -t stats/design_RD.con -n 500 --T2')

print('Check the RD TBSS analysis changes in the skeleton. These are not the significant changes.')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.8 ' \
'stats/tbss_RD_tstat1.nii.gz -cm red-yellow -dr 3 6 stats/tbss_RD_tstat2.nii.gz -cm blue-lightblue -dr 3 6')

print('RD p<0.05 results...')
os.system('fsleyes $FSLDIR/data/standard/MNI152_T1_1mm stats/mean_FA_skeleton -cm green -dr 0.2 0.7 ' \
    'stats/tbss_RD_tfce_corrp_tstat1.nii.gz -cm red-yellow -dr 0.95 1 stats/tbss_RD_tfce_corrp_tstat2.nii.gz '
    '-cm blue-lightblue -dr 0.95 1')

