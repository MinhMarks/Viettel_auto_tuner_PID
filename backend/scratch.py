import requests

test_payload = {
    "params": [
        67.33652089197852, 29.478616076582114, 9.295320463458662, 83.55324824766073, 63.45391700509826, 0.8445007032434262,
        66.80423561611349, 46.63120092118578, 1.1934355975465145, 47.07352484424449, 29.995576463539805, 11.766616752898601
    ],
    "setpoint_pitch": 0.436,
    "setpoint_yaw": 0.52,
    "base_disturbance_config": {"wind_torque_p": 0.01, "wind_torque_y": 0.01, "sensor_noise_std": 0.005, "mass_payload": 0.01},
    "step_increments": {"wind_torque_p": 0.01, "wind_torque_y": 0.01, "sensor_noise_std": 0.005, "mass_payload": 0.01},
    "steps": 7,
    "t_max": 20.0,
    "trajectory_type": "multi-step",
    "gs_method": "linear",
    "controller_type": "classic"
}
URL_TEST = "http://localhost:8089/api/robustness_sweep"
res = requests.post(URL_TEST, json=test_payload)
print(f"Status Code: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"Keys returned: {list(data.keys())}")
    for k in data.keys():
        print(f"{k} metrics pitch: {data[k].get('metrics', {}).get('pitch', {}).get('rise_time')}")
