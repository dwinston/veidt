# coding: utf-8
# Copyright (c) Materials Virtual Lab
# Distributed under the terms of the BSD License.

from veidt.abstract import Model

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense


class NeuralNet(Model):

    def __init__(self, layer_sizes, describer, preprocessor=StandardScaler(),
                 activation="relu", loss="mae"):
        """
        :param layer_sizes: Hidden layer sizes, e.g., [3, 3]
        :param describer: Desciber object to convert input objects to
            descriptors.
        :param preprocessor: : Processor to use. Defaults to StandardScaler
        :param activation: Activation function
        :param loss: Loss function. Defaults to mae
        """
        self.layer_sizes = layer_sizes
        self.desciber = describer
        self.preprocessor = preprocessor
        self.activation = activation
        self.loss = loss
        self.model = None

    def fit(self, inputs, outputs, test_size=0.2, **kwargs):
        """
        :param inputs: List of inputs
        :param outputs: List of outputs
        :param test_size: Size of test set. Defaults to 0.2.
        :param kwargs: Passthrough to fit function in keras.models
        """
        descriptors = self.desciber.describe_all(inputs)
        scaled_descriptors = self.preprocessor.fit_transform(descriptors)
        adam = Adam(1e-2)
        x_train, x_test, y_train, y_test = train_test_split(
            scaled_descriptors, outputs, test_size=test_size)

        model = Sequential()
        model.add(Dense(self.layer_sizes[0], input_dim=len(x_train[0]),
                        activation=self.activation))
        for l in self.layer_sizes[1:]:
            model.add(Dense(l, activation=self.activation))
        model.add(Dense(1))
        model.compile(loss=self.loss, optimizer=adam, metrics=[self.loss])
        model.fit(x_train, y_train, verbose=0, validation_data=(x_test, y_test),
                  **kwargs)
        self.model = model

    def predict(self, inputs):
        descriptors = self.desciber.describe_all(inputs)
        scaled_descriptors = self.preprocessor.transform(descriptors)
        return self.model.predict(scaled_descriptors)

    def save(self, model_fname):
        self.model.save(model_fname)