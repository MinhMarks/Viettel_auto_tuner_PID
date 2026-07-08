import React, { useState, useEffect, useRef } from 'react';
import { Joystick } from 'react-joystick-component';
import Helicopter3D from './Helicopter3D';
import { useAppContext } from '../context/AppContext';

/**
 * Page3DSimulation — Real-time Hardware-in-the-Loop (HIL) 3D view.
 *
 * WebSocket lifecycle is tied to this component's mount/unmount:
 *   - Connects on mount (when user navigates to /simulation)
 *   - Disconnects on unmount (when user leaves /simulation)
 * This prevents the socket from staying alive when the user is on other pages.
 */
export default function Page3DSimulation() {
    const { manualParams, manualParamsLarge, tunedParams, distSim, setDistSim } = useAppContext();

    const [joyPitch, setJoyPitch] = useState(0);
    const [joyYaw, setJoyYaw] = useState(0);
    const [actualPitch, setActualPitch] = useState(0);
    const [actualYaw, setActualYaw] = useState(0);
    const [simController, setSimController] = useState('Manual');
    const wsRef = useRef(null);

    // ── WebSocket: connect on mount, disconnect on unmount ──────────────────
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8088/api/ws/simulate');
        wsRef.current = ws;
        ws.onopen = () => console.log('HIL WebSocket Connected');
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setActualPitch(data.pitch);
            setActualYaw(data.yaw);
        };
        ws.onerror = (e) => console.warn('HIL WebSocket error', e);
        return () => {
            ws.close();
            wsRef.current = null;
            console.log('HIL WebSocket Disconnected');
        };
    }, []);

    // ── Send control commands at ~30 fps ────────────────────────────────────
    useEffect(() => {
        const interval = setInterval(() => {
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                let activeParams = manualParams;
                if (simController === 'GA'     && tunedParams.GA)         activeParams = tunedParams.GA;
                if (simController === 'PSO'    && tunedParams.PSO)        activeParams = tunedParams.PSO;
                if (simController === 'TPE'    && tunedParams.TPE)        activeParams = tunedParams.TPE;
                if (simController === 'CMA-ES' && tunedParams['CMA-ES'])  activeParams = tunedParams['CMA-ES'];
                if (simController === 'GWO'    && tunedParams.GWO)        activeParams = tunedParams.GWO;

                wsRef.current.send(JSON.stringify({
                    setpoint_pitch: joyPitch,
                    setpoint_yaw:   joyYaw,
                    params:         activeParams,
                    disturbances:   distSim,
                    gs_method:      'step',
                    params_large:   manualParamsLarge,
                }));
            }
        }, 33);
        return () => clearInterval(interval);
    }, [joyPitch, joyYaw, manualParams, manualParamsLarge, distSim, simController, tunedParams]);

    return (
        <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: 12, overflow: 'hidden' }}>
            <Helicopter3D pitch={actualPitch} yaw={actualYaw} />

            {/* ── Settings Panel ─────────────────────────────────────────────── */}
            <div style={{
                position: 'absolute', top: 20, left: 20, width: 320,
                backgroundColor: 'rgba(0, 0, 0, 0.7)', borderRadius: 12, padding: 15,
                border: '1px solid #444', color: 'white'
            }}>
                <h3 style={{ margin: '0 0 15px 0', borderBottom: '1px solid #444', paddingBottom: 5, color: '#10b981' }}>
                    3D SIMULATION SETTINGS
                </h3>

                <div className="form-group" style={{ marginBottom: 15 }}>
                    <label style={{ fontSize: 12 }}>Controller Algorithm</label>
                    <select
                        value={simController}
                        onChange={e => setSimController(e.target.value)}
                        style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid #666', color: 'white', padding: '6px', borderRadius: 4, width: '100%' }}
                    >
                        <option value="Manual">Manual Baseline</option>
                        <option value="GA">Genetic Algorithm (GA)</option>
                        <option value="PSO">Particle Swarm (PSO)</option>
                        <option value="TPE">TPE</option>
                        <option value="CMA-ES">CMA-ES</option>
                        <option value="GWO">Grey Wolf (GWO)</option>
                    </select>
                    {simController !== 'Manual' && !tunedParams[simController] && (
                        <div style={{ color: '#f87171', fontSize: 11, marginTop: 5 }}>
                            ⚠️ Controller {simController} has not been tuned yet. Falling back to Manual. Please run Ideal Tuning first.
                        </div>
                    )}
                </div>

                <div style={{ borderTop: '1px solid #444', paddingTop: 10 }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: 13, color: '#a78bfa' }}>Disturbances</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                        {[
                            { label: 'Wind Pitch',    key: 'wind_torque_p',    step: 0.01 },
                            { label: 'Wind Yaw',      key: 'wind_torque_y',    step: 0.01 },
                            { label: 'Sensor Noise',  key: 'sensor_noise_std', step: 0.01 },
                            { label: 'Payload Ratio', key: 'mass_payload',     step: 0.1  },
                        ].map(({ label, key, step }) => (
                            <div key={key} className="form-group" style={{ marginBottom: 0 }}>
                                <label style={{ fontSize: 11 }}>{label}</label>
                                <input
                                    type="number" step={step}
                                    value={distSim[key]}
                                    onChange={e => setDistSim({ ...distSim, [key]: parseFloat(e.target.value) })}
                                    style={{ padding: 4, width: '100%' }}
                                />
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* ── Telemetry HUD ──────────────────────────────────────────────── */}
            <div style={{
                position: 'absolute', top: 20, right: 20, width: 250,
                backgroundColor: 'rgba(0, 0, 0, 0.7)', borderRadius: 12, padding: 15,
                border: '1px solid #444', color: '#0f0', fontFamily: 'monospace'
            }}>
                <h3 style={{ margin: '0 0 10px 0', borderBottom: '1px solid #0f0', paddingBottom: 5 }}>TELEMETRY</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>TGT PITCH:</span><span>{(joyPitch * 180 / Math.PI).toFixed(1)}°</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>CUR PITCH:</span><span>{(actualPitch * 180 / Math.PI).toFixed(1)}°</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 5 }}><span>TGT YAW:</span><span>{(joyYaw * 180 / Math.PI).toFixed(1)}°</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>CUR YAW:</span><span>{(actualYaw * 180 / Math.PI).toFixed(1)}°</span></div>
            </div>

            {/* ── Joystick ───────────────────────────────────────────────────── */}
            <div style={{ position: 'absolute', bottom: 30, right: 30, background: 'rgba(0,0,0,0.5)', borderRadius: '50%', padding: 10 }}>
                <Joystick
                    size={120} stickSize={40}
                    baseColor="rgba(255,255,255,0.1)" stickColor="rgba(167,139,250,0.8)"
                    move={(e) => { setJoyYaw(e.x * 6.28); setJoyPitch(e.y * 1.05); }}
                    stop={() => { setJoyYaw(0); setJoyPitch(0); }}
                />
            </div>
        </div>
    );
}
