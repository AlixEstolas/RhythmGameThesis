import numpy
import librosa
import sklearn
import joblib
import os
import pandas as pd
import csv


def genreDetect():
    mainPath = librosa.util.find_files("./songs/")
    walk = librosa.util.find_files("./songs/wav/")
    sample_rate = 44100
    hop_size = 1024
    frame_size = 2048

    fName = []
    
    #Convert to WAV
    for mp3Songs in mainPath:
        filename_w_ext = os.path.basename(mp3Songs)
        filename, file_extension = os.path.splitext(filename_w_ext)
        y, sr = librosa.load(mp3Songs,sr = 44100)
        librosa.output.write_wav('./songs/wav/'+filename+".wav", y, sr)
    
    #Get filenames of songs
    for filess in walk:
        filename_w_ext = os.path.basename(filess)
        filename, file_extension = os.path.splitext(filename_w_ext)
        fName.append(filename)
        print(filess)
        print('====' + filename)
    songs = []
    
    # with open('song_names.csv', mode='w') as songNameFile:
    #     songNameWriter = csv.writer(songNameFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     songNameWriter.writerows([fName])
    #     # for ff in fName:
    #     #     songNameWriter.write(ff)
    print("Extracting sample arrays for files...")

    #Getting samples from wav files
    for p in walk:
        print(p)
        x, sr = librosa.load(p, sr=sample_rate, offset=30, duration=30.0)
        songs.append(x)

    print("DONE!")

    print("Extracting features from sample arrays...")

    data = numpy.array([extract_features(x, sample_rate, frame_size, hop_size) for x in songs])

    print("DONE!")

    scaler = sklearn.preprocessing.MinMaxScaler(feature_range=(-1, 1))
    data = scaler.fit_transform(data)
    
    for xx in fName:
        print(xx)
        
    preds = []
    

    # get the model from pkl file
    svm = joblib.load('knn.pkl')

    print("----------------------------------- K Nearest Neigbor -----------------------------------\n")
    preds.insert(0,svm.predict(data))
    print(preds[0])
    pd.DataFrame(preds[0]).to_csv('knn.csv')
    print("")
    print("----------------------------------------------------------------------------------------")
    ##  print(type(predsKNN[1]))
    
    ###############################
    
    svm = joblib.load('forest.pkl')

    print("----------------------------------- Random Forest -----------------------------------\n")
    preds.insert(1,svm.predict(data))
    print(preds[1])
    pd.DataFrame(preds[1]).to_csv('forest.csv')
    print("")
    print("----------------------------------------------------------------------------------------")
    
    
    ##############################
    
    svm = joblib.load('svm.pkl')

    print("----------------------------------- Support Vector Machine -----------------------------------\n")
    preds.insert(2,svm.predict(data))
    print(preds[2])
    pd.DataFrame(preds[2]).to_csv('svm.csv')
    trialThis = list(zip(fName,preds[2]))
    
    #this makes a csv file with Song name and Genre
    datFrame = pd.DataFrame(data = trialThis, columns=['Song Name','Genre']).to_csv('tester.csv')
    
    # with open('song_names.csv', mode='w') as songNameFile:
    #     songNameWriter = csv.writer(songNameFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)   
    #     songNameWriter.writerows([preds[2]])
    print("")
    print("----------------------------------------------------------------------------------------")
    
    ##############################
    
    svm = joblib.load('neural.pkl')

    print("----------------------------------- Multi-layer Perceptron -----------------------------------\n")
    preds.insert(3,svm.predict(data))
    print(preds[3])
    pd.DataFrame(preds[3]).to_csv('neural.csv')
    print("")
    print("----------------------------------------------------------------------------------------")
    ##
    ##KNN = 0
    ##RF = 1
    ##SVM  = 2
    ##MLP = 3
    ##
    
    MLPval = 178
    SVMval = 181
    RFval = 168
    KNNval = 154
    
    counterSongs = 0
    for p in walk:
        counterSongs+=1
        
    genre = []
    score = []
    
    for x in range(counterSongs):
        print('hello')
        
    
    
    input('Press Enter to exit')

def extract_features(signal, sample_rate, frame_size, hop_size):

    zero_crossing_rate = librosa.feature.zero_crossing_rate(y=signal, frame_length=frame_size, hop_length=hop_size)
    spectral_centroid = librosa.feature.spectral_centroid(y=signal, sr=sample_rate, n_fft=frame_size,
                                                          hop_length=hop_size)
    spectral_contrast = librosa.feature.spectral_contrast(y=signal, sr=sample_rate, n_fft=frame_size,
                                                          hop_length=hop_size)
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=signal, sr=sample_rate, n_fft=frame_size,
                                                            hop_length=hop_size)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=signal, sr=sample_rate, n_fft=frame_size,
                                                        hop_length=hop_size)
    mfccs = librosa.feature.mfcc(y=signal, sr=sample_rate, n_fft=frame_size, hop_length=hop_size)

    return [

        numpy.mean(zero_crossing_rate),
        numpy.std(zero_crossing_rate),
        numpy.mean(spectral_centroid),
        numpy.std(spectral_centroid),
        numpy.mean(spectral_contrast),
        numpy.std(spectral_contrast),
        numpy.mean(spectral_bandwidth),
        numpy.std(spectral_bandwidth),
        numpy.mean(spectral_rolloff),
        numpy.std(spectral_rolloff),

        numpy.mean(mfccs[1, :]),
        numpy.std(mfccs[1, :]),
        numpy.mean(mfccs[2, :]),
        numpy.std(mfccs[2, :]),
        numpy.mean(mfccs[3, :]),
        numpy.std(mfccs[3, :]),
        numpy.mean(mfccs[4, :]),
        numpy.std(mfccs[4, :]),
        numpy.mean(mfccs[5, :]),
        numpy.std(mfccs[5, :]),
        numpy.mean(mfccs[6, :]),
        numpy.std(mfccs[6, :]),
        numpy.mean(mfccs[7, :]),
        numpy.std(mfccs[7, :]),
        numpy.mean(mfccs[8, :]),
        numpy.std(mfccs[8, :]),
        numpy.mean(mfccs[9, :]),
        numpy.std(mfccs[9, :]),
        numpy.mean(mfccs[10, :]),
        numpy.std(mfccs[10, :]),
        numpy.mean(mfccs[11, :]),
        numpy.std(mfccs[11, :]),
        numpy.mean(mfccs[12, :]),
        numpy.std(mfccs[12, :]),
        numpy.mean(mfccs[13, :]),
        numpy.std(mfccs[13, :]),
    ]


if __name__ == '__main__':
    genreDetect()
