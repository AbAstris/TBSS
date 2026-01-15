import os
import sys
import numpy as np

################################################################
########################## OVERVIEW ############################
################################################################

# Script 1 of 2

# This code is designed for a one-against-many analysis, i.e. an
# analysis where 1 patient is compared to 20 age- and sex-
# matched healthy controls. There needs to be at least 20 controls
# to reach a p-value < 0.05.

# Script 1 is designed to copy control and patient DTI 
# parameter maps (i.e. FA, MD, AD, RD) the the appropriate 
# location(s) for tract-based spatial statistics (TBSS).

# DTI parameter maps have previously been calculated using FSL's dtifit.

# Several things to change before running this script:
#### 1. Update the ControlProject# and Participant# for controls.
#### 2. Set the location of the control folders (two locations).
#### 3. Set the location of the patient folders.

#### UPDATE THIS SECTION ####
# Define the control folders, i.e. if controls are from Project folder
# different projects and have different participant numbers, then you
# can define a ControlProject# and Participant#.

controls = np.array([
    ['ControlProject1','Participant1'],
    ['ControlProject1','Participant2'],
    ['ControlProject1','Participant3'],
    ['ControlProject2','Participant1'],
    ['ControlProject2','Participant2'],
    ['ControlProject2','Participant3'],
    ['ControlProject2','Participant4'],
    ['ControlProject2','Participant5'],
    ['ControlProject3','Participant1'],
    ['ControlProject3','Participant2'],
    ['ControlProject3','Participant3'],
    ['ControlProject3','Participant4'],
    ['ControlProject3','Participant5'],
    ['ControlProject3','Participant6'],
    ['ControlProject3','Participant7'],
    ['ControlProject3','Participant8'],
    ['ControlProject3','Participant9'],
    ['ControlProject3','Participant10'] ,   
    ['ControlProject4','Participant1'],
    ['ControlProject4','Participant2']
]) #<-- Needs to be changed. 

project, id = zip(*controls)

# FA maps will be placed in the same directory as this script for TBSS.
# If you would like to analyse MD, AD and RD, they will need to be 
# placed in their own directory.

#This sets up the MD, AD, RD directories:
data_dir = './'
data_dir_MD = data_dir+'MD/'
data_dir_AD = data_dir+'AD/'
data_dir_RD = data_dir+'RD/'

os.system('mkdir '+data_dir_MD)
os.system('mkdir '+data_dir_AD)
os.system('mkdir '+data_dir_RD)

# The following code (1) moves the control and patient DTI parameter files into
# the appropriate locations for TBSS analyses, and (2) RD has to be calculated
# from the *_L2.nii.gz and *_L3.nii.gz files, which is also done prior to 
# moving it into the RD directory.

for i in range (0,len(project)):

    #### UPDATE THIS SECTION ####

    # The control directory needs to be set here (i.e. the locoation of the 
    # project and participant id directories.

    control_dir = '/Users/edm/MRI/control_data/' + project[i] + '/' + id[i] + '/' #<-- Needs to be changed. 

    #### UPDATE THIS SECTION ####

    # The below will need to be changed to get to the correct control path for the  
    # location of the 'dtifit' folder, i.e. where the FA, MD, AD, RD files are 
    # located after running FSL's dtifit.

    # Personally, I nest the 'dtifit' folder into another folder called 'bias_corr'
    # after running a bias correction (as in my preprocessing scripts on github),
    # but please use whatever folder structure is right for you.

    control_dir_dtifit = control_dir + 'bias_corr/dtifit/' #<-- Needs to be changed. 

    control_FA = control_dir_dtifit + 'CON_*FA.nii.gz'
    control_MD = control_dir_dtifit + 'CON_*MD.nii.gz'
    control_AD = control_dir_dtifit + 'CON_*L1.nii.gz'
    control_L2 = control_dir_dtifit + 'CON_*L2.nii.gz'
    control_L3 = control_dir_dtifit + 'CON_*L3.nii.gz'

    #Copy FA into TBSS directory, which is where this Python file is located.
    os.system('cp '+control_FA+' CON_'+project[i]+'_'+id[i]+'.nii.gz')

    #Copy MD into TBSS MD directory, which is in the MD directory.
    os.system('cp '+control_MD+' MD/CON_'+project[i]+'_'+id[i]+'.nii.gz')

    #Copy AD into TBSS AD directory, which is in the AD directory.
    os.system('cp '+control_AD+' AD/CON_'+project[i]+'_'+id[i]+'.nii.gz')

    #Calculate RD and copy into TBSS RD directory, which is in the RD directory.
    os.system('fslmaths '+control_L2+' -add '+control_L3+' -div 2 RD/CON_'+project[i]+'_'+id[i]+'.nii.gz')

#### UPDATE THIS SECTION ####

# This section copies the patient dtifit parameter maps to the correct location.
# The Patient ID should be updated accordingly to fit the naming of the dtifit files.

os.system('cp ../dtifit/PatientID*FA.nii.gz PatientID.nii.gz') #<-- Needs to be changed. 
os.system('cp ../dtifit/PatientID*MD.nii.gz MD/PatientID.nii.gz') #<-- Needs to be changed. 
os.system('cp ../dtifit/PatientID*L1.nii.gz AD/PatientID.nii.gz') #<-- Needs to be changed. 
os.system('fslmaths ../dtifit/PatientID*L2.nii.gz -add ../dtifit/PatientID*L3.nii.gz -div 2 RD/PatientID.nii.gz') #<-- Needs to be changed. 

# List files in each directory to show the data has been moved.
os.system('ls *.nii.gz')
os.system('ls MD/*')
os.system('ls AD/*')
os.system('ls RD/*')



