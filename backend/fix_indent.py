with open("/home/jupyter-iec_duongnt/New Project/Viettel_auto_tuner_PID/backend/visualization/plot_utils.py", "r") as f:
    lines = f.readlines()

for i in range(48, 115):
    lines[i] = "    " + lines[i]

with open("/home/jupyter-iec_duongnt/New Project/Viettel_auto_tuner_PID/backend/visualization/plot_utils.py", "w") as f:
    f.writelines(lines)
