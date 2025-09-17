import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("logs/can_log.csv")
values = df["Decoded_Value"].tail(20).tolist()

plt.figure()
plt.plot(values, marker='o')
plt.title("Speed Snapshot")
plt.xlabel("Sample")
plt.ylabel("Speed (km/h)")
plt.savefig("speed_snapshot.png")
print("Plot saved to speed_snapshot.png")
