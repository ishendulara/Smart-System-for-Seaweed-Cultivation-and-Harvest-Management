import numpy as np
import pandas as pd

# Model parameters (copy from training output)
K = 490.23
r = 0.1284
t0 = 24.31

def logistic(t):
    return K / (1 + np.exp(-r * (t - t0)))

days = np.arange(0, 43)
weights = logistic(days)

df = pd.DataFrame({
    "day": days,
    "predicted_weight_g": weights
})

df.to_csv("daily_growth_predictions.csv", index=False)
print("Daily growth data saved")
