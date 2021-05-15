import librosa
import matplotlib.pyplot as plt
import numpy as np
import librosa.display
import sklearn

y, sr = librosa.load('ex.wav')
mfccs = librosa.feature.mfcc(y=y, sr=sr)
print (mfccs)

mfccs = sklearn.preprocessing.scale(mfccs, axis=1)
print (mfccs)

plt.figure(figsize=(10, 4))
librosa.display.specshow(mfccs, sr=sr, x_axis='time')
plt.colorbar()
plt.title('MFCC')
plt.tight_layout()
plt.show()
