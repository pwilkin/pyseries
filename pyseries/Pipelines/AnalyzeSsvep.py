# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 11:21:35 2016

@author: user
"""
import sys
sys.path.insert(0, '/Users/user/Desktop/repo_for_pyseries/pyseries')

import pyseries.LoadingData as loading
import pyseries.Preprocessing as prep
import pyseries.Analysis as analysis
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import glob

#path = '/Users/user/Desktop/eeg/ssvep/Blazej 13.06.16/'
#epochs = loading.Read_edf.Combine_EDF_XML(path,True)
#prep.Epochs.mark_events(epochs,['EEG O2'] )


def calc_corr(path):
    #Read single subject data - eeg, info about eeg and info from experimental app (unity)
    recording = loading.Read_edf.Combine_EDF_XML(path + '/', 3, 70)
    #Display markers over the whole signal    
    prep.Epochs.mark_events(recording,['EEG O1'], subject_name = path)

    #Define epochs for analysis
    epochs_info= {"Please Count": [0, 500*10], "Only Look": [0, 500 *10]}
    #Create them by slicing the signal
    epochs = prep.Epochs.Make_Epochs_for_Channels(recording, ['EEG O1','EEG O2','EEG P3', 'EEG P4'],epochs_info)
    #Re-reference, because only by subtracting P from O-electrodes ssvep response becomes visible
    new_ref = {}
    new_ref['Only Look'] = epochs ['EEG O2']['Only Look'] - epochs['EEG P4']['Only Look']
    new_ref['Please Count'] = epochs ['EEG O2']['Please Count'] - epochs ['EEG P4']['Please Count']
    new_epochs  = {"O-P":new_ref}
    
    #Get the accuracy in counting condition
    responses = recording['events'][recording['events']["code"] == "responded"]
    accuracy = responses['response'] / responses['expected']
    
    #Get the power spectra in two conditions       
    power_density= analysis.Explore.PlotPowerSpectrum(new_epochs['O-P'], 498, mode = 'period', name = path)
    
    ssvep = analysis.Normalize.Z_score( power_density['Please Count'][1][:,49] )
    accuracy = analysis.Normalize.Z_score( accuracy )
    
    return ssvep, accuracy, power_density
    

def plot_slow_ssvep():
    #Slow is 5Hz flicker
    paths = glob.glob('/Users/user/Desktop/nagrania_eeg/ssvep/*')



    all_ssvep = []
    all_acc = []
    
    saving = {}
    for p in paths:
        print(p)
        ssvep, acc, pxx = calc_corr(p)
        all_ssvep.extend(ssvep)
        all_acc.extend(acc)
        
        saving[p] = ssvep
    
    sns.jointplot(x = np.array(all_ssvep),y =  np.array(all_acc), kind="reg")
    return saving





def plot_2speed_ssvep():
    paths = ['/Users/user/Desktop/nagrania_eeg/ssvep_2speed/Maciek_08_26_16',
             '/Users/user/Desktop/nagrania_eeg/ssvep_2speed/Gosia_08_31_16']

    #fast is 20 Hz flicker


    for path in paths:
        print(path)
        #Read single subject data - eeg, info about eeg and info from experimental app (unity)
        recording = loading.Read_edf.Combine_EDF_XML(path +'/', 0, 70)
        
        
        #Define epochs for analysis
        epochs_info= {'Please wait fast': [100, 500 *4], 'Please wait slow' : [100, 500 * 4]}
        #Create them by slicing the signal
        epochs = prep.Epochs.Make_Epochs_for_Channels(recording, ['EEG O1','EEG O2','EEG P3','EEG P4'],epochs_info)
        
        #Re-reference, because oonly then ssvep response becomes visible
        new_ref = {}
        new_ref['fast'] = epochs ['EEG O2']['Please wait fast'] - epochs['EEG P4']['Please wait fast']
        new_ref['slow'] = epochs ['EEG O2']['Please wait slow'] - epochs['EEG P4']['Please wait slow']
        new_epochs  = {"O-P":new_ref}
                
        #Get the power spectra in two conditions       
        power_density= analysis.Explore.PlotPowerSpectrum(new_epochs['O-P'], 500, mode = 'period', name = path)

    
