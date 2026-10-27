import glob
import random
import numpy as np
from scipy.signal import spectrogram
from sklearn.preprocessing import MinMaxScaler, StandardScaler,RobustScaler,MaxAbsScaler
import scipy.io
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D,Reshape
from tensorflow.keras.models import Sequential
from sklearn.metrics import confusion_matrix, precision_score, f1_score,accuracy_score



def load_data(num_samples, date, category):
    GNSS_dir = f"data/oct_{date}/S{category}*_*"
    spoofer_dir = f"data/oct_{date}/SS{category}*_*"
    
    # Get sorted list of all files
    full_list_GNSS = glob.glob(GNSS_dir)
    full_list_spoofer = glob.glob(spoofer_dir)
    
    # Randomly select num_samples from GNSS and spoofer datasets
    selected_GNSS = random.sample(full_list_GNSS, num_samples)
    selected_spoofer = random.sample(full_list_spoofer, num_samples)
    
    # Load the selected data
    train_data_GNSS = [abs(scipy.io.loadmat(file)["data"]) for file in selected_GNSS]
    train_data_spoofer = [abs(scipy.io.loadmat(file)["data"]) for file in selected_spoofer]
    
    # Combine both datasets
    train_data = np.array(train_data_GNSS + train_data_spoofer)
    
    # Create labels: 0 for GNSS, 1 for spoofer
    train_labels = np.zeros(len(train_data))
    train_labels[len(train_data_GNSS):] = 1
    
    return train_data, train_labels

def make_spectrogram(data, category):
    spectograms = []
    sample_per_seg = 11111
    nperseg = sample_per_seg * 2 if category == 3 else sample_per_seg

    for sample in data:
        frequencies, times, Sxx = spectrogram(sample.ravel(), nperseg=nperseg, return_onesided=True, mode='magnitude')

        # Scale and normalize
        Sxx = Sxx-np.mean(Sxx)
        Sxx = Sxx / np.std(Sxx)
        spectograms.append(Sxx)

    sp_data = np.array(spectograms)

    if category == 3:
        new_shape = (sp_data.shape[1] // (2), sp_data.shape[2])

        model = Sequential()
        model.add(Reshape((sp_data.shape[1], 1, sp_data.shape[2]), input_shape=(sp_data.shape[1], sp_data.shape[2])))
        model.add(MaxPooling2D(pool_size=(2, 1), strides=None, padding='valid'))
        reduced_data = model.predict(sp_data)
        sp_data = reduced_data.reshape(-1, new_shape[0], new_shape[1])

    return sp_data

def scale(data):
    # Remove the mean from each sample in a vectorized way
    data_mean_removed = data - np.mean(data, axis=(1, 2), keepdims=True)

    # Reshape the data to 2D (n_samples, n_rows * n_cols)
    n_samples, n_rows, n_cols = data.shape
    data_2d = data_mean_removed.reshape(n_samples, -1)

    # Scale the data using MaxAbsScaler
    scaler = MaxAbsScaler()
    data_scaled_2d = scaler.fit_transform(data_2d)

    # Reshape the data back to 3D
    data_scaled = data_scaled_2d.reshape(n_samples, n_rows, n_cols)

    return data_scaled

def load_NN_model(date,category):
    model = load_model(f"models\Fully_connected{date}_C{category}_SS20000_same_samples_lr001_red_1_samplemean.h5",compile=False)
    model.compile(optimizer=keras.optimizers.Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def return_category(category):
    if category == 1:
        return "Baseline"
    elif category == 2:
        return "Multipath"
    elif category == 3:
        return "High Sampling Rate"
    elif category == 4:
        return "Low Quantization"


# Load data
samples = 10       # Number of sample
test_date = 19      # Test data 18 for Oct 18 and 19 for Oct 19
test_category= 3    # Test category [1:Baseline, 2:Multipath, 3:High Sampling Rate, 4: Low Quantization]
model_date = 19     # Model date 18 for Oct 18 and 19 for Oct 19
model_category = 3  # Model category [1:Baseline, 2:Multipath, 3:High Sampling Rate, 4: Low Quantization]

print(f"Testing model trained on Oct{model_date} {return_category(model_category)} data on Oct{test_date} {return_category(test_category)} data")

data,labels = load_data(samples, test_date, test_category)

# Make spectrograms
spectrograms = make_spectrogram(data, test_category)

# Scale spectrograms
spectrograms = scale(spectrograms)

# Load model
model = load_NN_model(model_date, model_category)

# Predict
predictions = model.predict(spectrograms)

# Print confusion matrix
cm = confusion_matrix(labels, predictions.round())
print("Confusion Matrix:")
print(cm.astype('float') / cm.sum(axis=1)[:, np.newaxis])


# Print accuracy
print("Accuracy:", accuracy_score(labels, predictions.round()))
