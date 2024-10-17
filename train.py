import os
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from common import *

def load_data(data_path):
    X = []
    y = []
    for idx, label in enumerate(CLASSES):
        folder = os.path.join(data_path, label)
        for file in os.listdir(folder):
            if file.endswith('.wav') or file.endswith('.mp3'):
                file_path = os.path.join(folder, file)
                # Load audio file
                signal, sr = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
                # Ensure that all signals are the same length
                if len(signal) < SAMPLE_RATE * DURATION:
                    pad_width = SAMPLE_RATE * DURATION - len(signal)
                    signal = np.pad(signal, (0, pad_width), 'constant')
                else:
                    signal = signal[:int(SAMPLE_RATE * DURATION)]
                # Compute Mel spectrogram
                mel_spect = librosa.feature.melspectrogram(y=signal, sr=sr, n_mels=N_MELS, hop_length=HOP_LENGTH)
                mel_spect = librosa.power_to_db(mel_spect, ref=np.max)
                # Normalize
                mel_spect = (mel_spect - mel_spect.min()) / (mel_spect.max() - mel_spect.min() + 1e-6)
                X.append(mel_spect)
                y.append(idx)
    X = np.array(X)
    y = np.array(y)
    return X, y

# Load and preprocess the data
print("Loading data...")
X, y = load_data(DATA_DIR)
print(f"Data loaded. Number of samples: {len(X)}")

# Reshape X for CNN input
X = X[..., np.newaxis]  # Add channel dimension

# Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

print (f"X_train.shape: {X_train.shape}")

# Build the model
model = models.Sequential([
    layers.Input(shape=(N_MELS, 9, 1)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(len(CLASSES), activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
print("Training model...")
history = model.fit(X_train, y_train, epochs=100, 
                    validation_data=(X_val, y_val))
print("Model trained.")

# Save the model
model.save(MODEL_NAME)
print(f"Model saved as {MODEL_NAME}.")