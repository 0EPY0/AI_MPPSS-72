import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt

from keras.models import Sequential, load_model
from keras.layers import Dense


class NN():
    def __init__(self):
        super().__init__()

        self.model = Sequential()
        self.model.add(Dense(64, activation='relu', input_shape=(4,)))

        self.model.add(Dense(128, activation='relu'))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(128, activation='relu'))

        self.model.add(Dense(3, activation='softmax'))

        self.model.compile(
            optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        # self.label_encoder = LabelEncoder()
        self.start_weights = self.model.get_weights()
        # Print model summary
        # model.summary()
        # return model

    def classification(self, targets, labels):
        y_pred = np.argmax(self.model.predict(targets), axis=1)
        loss, accuracy = self.model.evaluate(targets, labels)
        print(f"Test accuracy: {accuracy:.4f}")
        print(f"Test loss: {loss:.4f}")
        return y_pred
    # self.label_encoder.inverse_transform(y_pred)

    def trained_model(self, X, y):
        self.model.fit(X, y, epochs=50, batch_size=16)

    def save_weights(self, path):
        self.model.save_weights(path)

    def load_weights(self, path):
        self.model.load_weights(path)

    def reset_weights(self):
        self.model.set_weights(self.start_weights)

    def preprocessing(self, rows):
        data = {'RB': [], 'DST': [],
                'COG': [], 'SOG': [],
                'Situations': []}

        for boat in rows:
            situation = 0 if boat.OV == 1 else 1 if boat.HO == 1 else 2

            data['RB'].append(boat.RB)
            data['DST'].append(boat.DST)
            data['COG'].append(boat.COG)
            data['SOG'].append(boat.SOG)
            data['Situations'].append(situation)

        data = pd.DataFrame(data)

        targets = data[['RB', 'DST', 'COG', 'SOG']]
        labels = data['Situations'].to_numpy()

        # encoded_labels = self.label_encoder.fit_transform(labels)
        # print(encoded_labels)

        scaler = StandardScaler()
        targets = scaler.fit_transform(targets)

        # print(labels)
        return targets, labels
