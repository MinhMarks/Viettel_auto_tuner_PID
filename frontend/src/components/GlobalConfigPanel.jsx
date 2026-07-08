import React from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';

const API_BASE = 'http://localhost:8088/api';

export default function GlobalConfigPanel() {
    const {
        manualParams, setManualParams,
        spPitch, setSpPitch,
        spYaw, setSpYaw,
        simDuration, setSimDuration,
        trajectoryType, setTrajectoryType,
    } = useAppContext();
    return (
        <div style={{ display: 'flex', gap: 20, marginBottom: 20, flexShrink: 0 }}>
            {/* Simulation & Trajectory Settings */}
            <div className="glass-panel" style={{ flex: 1, padding: 15, display: 'flex', flexDirection: 'column', gap: 10 }}>
                <h4 style={{ margin: 0, color: '#a78bfa' }}>Global Setpoints</h4>
                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                    <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
                        <label style={{ fontSize: 11 }}>Trajectory Type</label>
                        <select value={trajectoryType} onChange={e => setTrajectoryType(e.target.value)} style={{ background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: 'white', padding: '4px', borderRadius: 4, width: '100%' }}>
                            <option value="step">Step (Constant)</option>
                            <option value="sine">Sine Wave</option>
                            <option value="square">Square Wave</option>
                            <option value="multi-step">Multi-Step</option>
                        </select>
                    </div>
                    <div className="form-group" style={{ marginBottom: 0, width: 80 }}>
                        <label style={{ fontSize: 11 }}>Sim Duration</label>
                        <input type="number" step="1" min={5} max={120} value={simDuration} onChange={(e) => setSimDuration(parseFloat(e.target.value))} style={{ padding: 4, width: '100%' }} />
                    </div>
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                    <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
                        <label style={{ fontSize: 11 }}>Base Amplitude Pitch (deg)</label>
                        <input type="number" step="1" min={-60} max={60} value={spPitch} onChange={(e) => setSpPitch(parseFloat(e.target.value))} style={{ padding: 4, width: '100%' }} />
                    </div>
                    <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
                        <label style={{ fontSize: 11 }}>Base Amplitude Yaw (deg)</label>
                        <input type="number" step="1" min={-360} max={360} value={spYaw} onChange={(e) => setSpYaw(parseFloat(e.target.value))} style={{ padding: 4, width: '100%' }} />
                    </div>
                </div>
            </div>

            {/* Manual PID Baseline */}
            <div className="glass-panel" style={{ flex: 1.5, padding: 15, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <h4 style={{ margin: 0, color: '#a78bfa' }}>Manual PID Baseline</h4>
                    <button className="secondary-btn" style={{ fontSize: 10, padding: '2px 8px' }} onClick={async () => {
                        try {
                            const res = await axios.get(`${API_BASE}/lqr_baseline`);
                            if (res.data && res.data.baseline_params) setManualParams(res.data.baseline_params);
                        } catch(e) { console.error(e); }
                    }}>Load LQR</button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 8 }}>
                    {['Kp_p', 'Ki_p', 'Kd_p', 'Kp_y', 'Ki_y', 'Kd_y'].map((label, idx) => (
                        <div key={idx} className="form-group" style={{ marginBottom: 0 }}>
                            <label style={{ fontSize: 11, textAlign: 'center', display: 'block' }}>{label}</label>
                            <input type="number" step="0.5" min={0} max={200} value={manualParams[idx]}
                                onChange={e => {
                                    const newP = [...manualParams];
                                    newP[idx] = parseFloat(e.target.value);
                                    setManualParams(newP);
                                }} style={{ padding: 4, width: '100%', textAlign: 'center' }} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
