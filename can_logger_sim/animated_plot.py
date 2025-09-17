# animated_plot.py

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

LOG_CSV = "logs/can_log.csv"

plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots()
fig.set_tight_layout(True)

x_data = []
speed_data = []
rpm_data = []
temp_data = []

line1, = ax.plot([], [], label="Speed (km/h)")
line2, = ax.plot([], [], label="RPM")
line3, = ax.plot([], [], label="Temp (°C)")

ax.legend(loc='upper right')
ax.set_title("Real-Time CAN Signal Plot")
ax.set_xlabel("Time")
ax.set_ylabel("Value")

def animate(frame):
    try:
        df = pd.read_csv(LOG_CSV)
        df['Time'] = pd.to_datetime(df['Timestamp'])

        # Interpret CAN_IDs
        df['Signal'] = df['CAN_ID'].map({
            '0x101': 'Speed',
            '0x102': 'RPM',
            '0x103': 'Temp'
        })

        recent = df.tail(100)

        x = recent['Time']

        y_speed = recent[recent['Signal'] == 'Speed']['Decoded_Value'].astype(float)
        y_rpm   = recent[recent['Signal'] == 'RPM']['Decoded_Value'].astype(float)
        y_temp  = recent[recent['Signal'] == 'Temp']['Decoded_Value'].astype(float)

        line1.set_data(x[:len(y_speed)], y_speed)
        line2.set_data(x[:len(y_rpm)], y_rpm)
        line3.set_data(x[:len(y_temp)], y_temp)

        ax.relim()
        ax.autoscale_view()

    except Exception as e:
        print(f"[Error in animate]: {e}")

    return line1, line2, line3

from matplotlib.animation import FuncAnimation

anim = FuncAnimation(fig, animate, interval=1000, frames=30)

print("Saving animation to live_signals.gif...")
anim.save("live_signals.gif", writer="pillow", fps=1)
print("GIF saved as live_signals.gif")
