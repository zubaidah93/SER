# -*- coding: utf-8 -*-
"""CAP5610_ProjectDataImproting.ipynb

Automatically generated by Colaboratory.


#Importing Libraries
"""

#Importing Libraries
import librosa
import soundfile
import os,glob,pickle
import numpy as np 
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn import tree , svm
from sklearn.neural_network import MLPClassifier

#Importing files from google drive
from google.colab import drive
drive.mount('/content/drive')

!gdown --id https://drive.google.com/drive/folders/1ZoxPz-3sqih87r6a7n0nRi3Phh8Kfx0w?usp=sharing

"""#Importing Different Data types and assigning their emotions

Datasets that are targetted in this function are: 
1. RADVESS
2. CREMA-D
3. SAVEE
4. TESS

Accessing the function and editing it:

1. You need to make sure filepaths are matching your google drive/local drive address upto the file 'combined data' which Inad prepared 
2. Adjust the size of observed emotions and edit that part for each dataset type. You can do it later after labeling. not necessary in the function. i.e. after labeling and combining all datasets, you can access the lists and adjust emotions as you'd like. 
3. Look at the code in the next section, its a suggested way of importing all data filepaths and their labels for training. 
"""

def load_dataa(Dataset): #Dataset = Dataset name

  #RADVESS Dataset Importing

  if Dataset == 'RADVESS':

#Emotions according to the labeling for RADVESS 

    emotions = {
      '01':'neutral',
      '02':'calm',
      '03':'happy',
      '04':'sad',
      '05':'angry',
      '06':'fearful',
      '07':'disgust',
      '08':'surprised'
    }
   
#filepath to the files which has to be adjusted according to the file location you have. 
    filepath = "/content/drive/MyDrive/combined_data/RAVDESS/Actor_*//*.wav"

    local_emotion,local_files_addresses = [] , [] # initializing the local lists that will be added to the global data 


    for file in glob.glob(filepath):
      file_name = os.path.basename(file)
      local_files_addresses.append(file)
      emotion = emotions[file_name.split('-') [2]]
      local_emotion.append(emotion)


#CREMA-D Dataset
  elif Dataset == 'CREMA-D':
    filepath = "/content/drive/MyDrive/combined_data/CREMA-D/" #File path in the drive / local PC
    dataset_files = os.listdir(filepath) #Saving the address of all .wav files 

    local_files_addresses, local_emotion = [] , []
    
    for file in dataset_files:
      local_files_addresses.append(filepath + file) 
      emotion = file.split('_')[2] #spliting the file address into words like 1001_DFA_NEU_XX to [1001, DFA, NEU, XX]
     
      if emotion == 'SAD':
        local_emotion.append('sad')
      elif emotion == 'ANG':
        local_emotion.append('angry')
      elif emotion == 'DIS':
        local_emotion.append('disgust')
      elif emotion == 'FEA':
        local_emotion.append('fearful')
      elif emotion == 'HAP':
        local_emotion.append('happy')
      elif emotion == 'NEU':
        local_emotion.append('neutral')
      else:
        continue

# SAVEE Dataset
  elif Dataset == 'SAVEE':
    filepath = "/content/drive/MyDrive/combined_data/SAVEE/" #File path in the drive / local PC
    dataset_files = os.listdir(filepath) #Saving the address of all .wav files 

    local_files_addresses, local_emotion = [] , []

    for file in dataset_files:
      local_files_addresses.append(filepath + file) 
      emotion = file.split('_')[1] #spliting the file address
      if file[-8:-6] == '_a':
        local_emotion.append('angry')
      elif file[-8:-6]=='_d':
        local_emotion.append('disgust')
      elif file[-8:-6]=='_f':
        local_emotion.append('fearful')
      elif file[-8:-6]=='_h':
        local_emotion.append('happy')
      elif file[-8:-6]=='_n':
        local_emotion.append('neutral')
      elif file[-8:-6]=='sa':
        local_emotion.append('sad')
      elif file[-8:-6]=='su':
        local_emotion.append('surprised') 
      else:
        continue

  elif Dataset == 'TESS':
    filepath = "/content/drive/MyDrive/combined_data/TESS/" #File path in the drive / local PC
    dataset_files = os.listdir(filepath)

    local_files_addresses,local_emotion = [], []

    emotions = {
          'neutral':'neutral',
          'ps':'surprised',
          'sad':'sad',
          'happy':'happy',
          'fear':'fearful',
          'disgust':'disgust',
          'angry':'angry'
        }
   
    for folder in dataset_files:
      folders = os.listdir(filepath + folder)
      for file in folders:
        emotion = file.split('.')[0]
        emotion = emotions[emotion.split('_')[2]]
        
        local_emotion.append(emotion)
        local_files_addresses.append(filepath + folder + '/' + file)



  return local_files_addresses, local_emotion

"""# Example 

In this example, datasets' filles path and their labels are imported using load_data() function where:

Glob_Files_Addresses = a dictionary that has a list of files path for each dataset
Glob_Emotions = a dictionary that has a list of labels for each datasets
"""

# Import all data, in aglobal emotional and file location [benchmark]
# Downsize_1: choose number of  emotions
# Downsize_2: 2 emotions - Positive/Negative 

Glob_Files_Addresses = []
Glob_Emotions = []

for i in range(0,4):

  if i == 0:
    dataset = 'RADVESS'
    local_files_addresses, local_emotion = load_dataa(dataset)
    Glob_Files_Addresses.append(local_files_addresses)
    Glob_Emotions.append(local_emotion)

  elif i == 1:
    dataset = 'CREMA-D'
    local_files_addresses, local_emotion = load_dataa(dataset)
    Glob_Files_Addresses.append(local_files_addresses)
    Glob_Emotions.append(local_emotion)

  elif i == 2:
    dataset = 'SAVEE'
    local_files_addresses, local_emotion = load_dataa(dataset)
    Glob_Files_Addresses.append(local_files_addresses)
    Glob_Emotions.append(local_emotion)

  elif i == 3:
    dataset = 'TESS'
    local_files_addresses, local_emotion = load_dataa(dataset)
    Glob_Files_Addresses.append(local_files_addresses)
    Glob_Emotions.append(local_emotion)


print(len(Glob_Files_Addresses))
print(len(Glob_Emotions))

len(Glob_Files_Addresses[3])

import itertools
Glob_Files_Addresses=list(itertools.chain.from_iterable(Glob_Files_Addresses))
len(Glob_Files_Addresses)

Glob_Emotions=list(itertools.chain.from_iterable(Glob_Emotions))
len(Glob_Emotions)

def extract_feature(file_name, **kwargs):
    """
    Extract feature from audio file `file_name`
        Features supported:
            - MFCC (mfcc)
            - Chroma (chroma)
            - MEL Spectrogram Frequency (mel)
            - Contrast (contrast)
            - Tonnetz (tonnetz)
        e.g:
        `features = extract_feature(path, mel=True, mfcc=True)`
    """
    mfcc = kwargs.get("mfcc")
    chroma = kwargs.get("chroma")
    mel = kwargs.get("mel")
    contrast = kwargs.get("contrast")
    tonnetz = kwargs.get("tonnetz")
    with soundfile.SoundFile(file_name) as sound_file:
        X = sound_file.read(dtype="float32")
        sample_rate = sound_file.samplerate
        if chroma or contrast:
            stft = np.abs(librosa.stft(X))
        result = np.array([])
        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            result = np.hstack((result, chroma))
        if mel:
            mel = np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
            result = np.hstack((result, mel))
        if contrast:
            contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)
            result = np.hstack((result, contrast))
        if tonnetz:
            tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0)
            result = np.hstack((result, tonnetz))
    return result

def load_data(test_size=0.2):
    X, y = [], []
    try :
      for file in Glob_Files_Addresses:
          i = 1
          # get the base name of the audio file
          basename = os.path.basename(file)
          print(basename)
          emotion = Glob_Emotions(i)
          # get the emotion label
          #emotion = int2emotion[basename.split("-")[2]]
          # we allow only AVAILABLE_EMOTIONS we set
         # if emotion not in AVAILABLE_EMOTIONS:
         #     continue
          # extract speech features
          features = extract_feature(file, tonnetz=True, contrast=True, mfcc=True, mel= True)
          # add to data
          X.append(features)
          y.append(emotion)
          i = i+1
    except :
         pass
    # split the data to training and testing and return it
    return train_test_split(np.array(X), y, test_size=test_size, random_state=7)

list_of_dict_values = list(Glob_Files_Addresses.values())
list_of_dict_values

X_train, X_test, y_train, y_test = load_data(test_size=0.1)
# print some details
# number of samples in training data
print("[+] Number of training samples:", X_train.shape[0])
# number of samples in testing data
print("[+] Number of testing samples:", X_test.shape[0])
# number of features used
# this is a vector of features extracted 
# using utils.extract_features() method
print("[+] Number of features:", X_train.shape[1])
