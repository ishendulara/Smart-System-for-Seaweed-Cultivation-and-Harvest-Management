import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# Load dataset
data = pd.read_csv("gracilaria_data.csv")
t = data["day"].values
w = data["weight_g"].values

# Logistic growth model
def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

# Initial guesses
initial_guess = [500, 0.1, 20]

# Train model
params, _ = curve_fit(logistic, t, w, p0=initial_guess)
K, r, t0 = params

print("Training complete")
print("K =", round(K, 2))
print("r =", round(r, 4))
print("t0 =", round(t0, 2))
