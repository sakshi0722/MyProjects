import numpy as np
from sklearn.linear_model import LinearRegression

# Sample training data
X = np.array([
    [25, 1],
    [40, 2],
    [30, 3],
    [50, 2]
])

y = np.array([15, 30, 45, 40])

model = LinearRegression()
model.fit(X, y)

def predict_recovery(age, severity):
    return int(model.predict([[age, severity]])[0])
