import numpy as np
import matplotlib.pyplot as plt

# Load results from the saved file
results = np.load("lstm_results.npy", allow_pickle=True).item()

train_dates = results['dates']['train']
test_dates = results['dates']['test']
train_actual = results['train']['actual']
train_predicted = results['train']['predicted']
test_actual = results['test']['actual']
test_predicted = results['test']['predicted']

# Plot training and testing predictions
plt.figure(figsize=(12, 6))

# Plot training data
plt.plot(train_dates, train_actual, label="Train Actual", color="blue")
plt.plot(train_dates, train_predicted, label="Train Predicted", color="cyan", linestyle="dashed")

# Plot testing data
plt.plot(test_dates, test_actual, label="Test Actual", color="orange")
plt.plot(test_dates, test_predicted, label="Test Predicted", color="red", linestyle="dashed")

plt.title("LSTM Predictions vs Actual Data")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid()
plt.show()
