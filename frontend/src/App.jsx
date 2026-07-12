import React, { useState, useEffect, useRef } from 'react';
import { Layers, Activity, BookOpen, Monitor } from 'lucide-react';
import Helicopter3D from './components/Helicopter3D';
import { Joystick } from 'react-joystick-component';
import './App.css';
import axios from 'axios';

const API_BASE = 'http://localhost:8088/api';

// Import New Pages
import PageIdealTuning from './components/PageIdealTuning';
import PageRobustness from './components/PageRobustness';
import PageGainScheduling from './components/PageGainScheduling';
import PageDocumentation from './components/PageDocumentation';
import PageHistory from './components/PageHistory';
import PageLQRComparison from './components/PageLQRComparison';

function App() {
  const [mainTab, setMainTab] = useState('experiments'); // 'experiments', '3d', 'wiki'
  const [expTab, setExpTab] = useState('ideal'); // 'ideal', 'robustness', 'gainscheduling'
  const [wikiDoc, setWikiDoc] = useState('intro'); // Add global wikiDoc state

  // Global Parameters
  const [manualParams, setManualParams] = useState([30.0, 15.0, 10.0, 40.0, 10.0, 15.0]);
  const [manualParamsLarge, setManualParamsLarge] = useState([50.0, 20.0, 15.0, 60.0, 15.0, 20.0]);
  
  const [tunedParams, setTunedParams] = useState({});
  const [tunedParamsLarge, setTunedParamsLarge] = useState({}); // For future use

  const [spPitch, setSpPitch] = useState(15.0); // degrees
  const [spYaw, setSpYaw] = useState(30.0); // degrees
  const [trajectoryType, setTrajectoryType] = useState('step');
  const [simDuration, setSimDuration] = useState(20.0);

  // Disturbances (Independent per tab)
  const [distIdeal] = useState({ wind_torque_p: 0, wind_torque_y: 0, sensor_noise_std: 0, mass_payload: 0 }); // Ideal is zeroed
  const [distRobustness, setDistRobustness] = useState({ wind_torque_p: 0.01, wind_torque_y: 0.01, sensor_noise_std: 0.1, mass_payload: 1.0 });
  const [distGainSched, setDistGainSched] = useState({ wind_torque_p: 0.01, wind_torque_y: 0.01, sensor_noise_std: 0.1, mass_payload: 1.0 });
  const [distSim, setDistSim] = useState({ wind_torque_p: 0.01, wind_torque_y: 0.01, sensor_noise_std: 0.1, mass_payload: 1.0 });

  // 3D View State
  const [joyPitch, setJoyPitch] = useState(0);
  const [joyYaw, setJoyYaw] = useState(0);
  const [actualPitch, setActualPitch] = useState(0);
  const [actualYaw, setActualYaw] = useState(0);
  const [simController, setSimController] = useState('Manual');
  const wsRef = useRef(null);

  useEffect(() => {
    if (mainTab === '3d') {
      const ws = new WebSocket('ws://localhost:8088/api/ws/simulate');
      wsRef.current = ws;
      ws.onopen = () => console.log("HIL WebSocket Connected");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setActualPitch(data.pitch);
        setActualYaw(data.yaw);
      };
      return () => { ws.close(); wsRef.current = null; };
    }
  }, [mainTab]);

  useEffect(() => {
    if (mainTab === '3d') {
      const interval = setInterval(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          let activeParams = manualParams;
          if (simController === 'GA' && tunedParams.GA) activeParams = tunedParams.GA;
          if (simController === 'PSO' && tunedParams.PSO) activeParams = tunedParams.PSO;
          if (simController === 'TPE' && tunedParams.TPE) activeParams = tunedParams.TPE;
          if (simController === 'CMA-ES' && tunedParams['CMA-ES']) activeParams = tunedParams['CMA-ES'];
          if (simController === 'GWO' && tunedParams.GWO) activeParams = tunedParams.GWO;

          wsRef.current.send(JSON.stringify({
            setpoint_pitch: joyPitch, setpoint_yaw: joyYaw,
            params: activeParams, disturbances: distSim, gs_method: 'step', params_large: manualParamsLarge
          }));
        }
      }, 33);
      return () => clearInterval(interval);
    }
  }, [mainTab, joyPitch, joyYaw, manualParams, manualParamsLarge, distSim, simController, tunedParams]);

  return (
    <div className="app-container" style={{display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden'}}>
      {/* Top Navigation */}
      <div className="top-nav" style={{
        display: 'flex', alignItems: 'center', padding: '12px 24px', 
        background: 'rgba(20, 25, 40, 0.8)', backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(255,255,255,0.1)', zIndex: 100
      }}>
        <h2 style={{ color: '#a78bfa', margin: '0 32px 0 0', fontSize: 20, textTransform: 'uppercase', letterSpacing: 2 }}>Viettel Auto-Tuner</h2>
        
        <div style={{display: 'flex', gap: 16, flex: 1}}>
          <button className={`nav-btn ${mainTab === 'experiments' ? 'active' : ''}`} onClick={() => setMainTab('experiments')}>
            <Activity size={18}/> Experiments
          </button>
          <button className={`nav-btn ${mainTab === '3d' ? 'active' : ''}`} onClick={() => setMainTab('3d')}>
            <Monitor size={18}/> 3D Simulation
          </button>
            <button className={`nav-btn ${mainTab === 'wiki' ? 'active' : ''}`} onClick={() => setMainTab('wiki')}>
              <BookOpen size={18} /> Theory Wiki
            </button>
            <button className={`nav-btn ${mainTab === 'history' ? 'active' : ''}`} onClick={() => setMainTab('history')}>
              <Monitor size={18} /> History
            </button>
        </div>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div className="main-content" style={{ display: 'flex', flexDirection: 'column', flex: 1, padding: 20, overflow: 'hidden' }}>
          {/* Render Navigation Level 2 if in Experiments Tab */}
          {mainTab === 'experiments' && (
            <div style={{display: 'flex', gap: 10, marginBottom: 20}}>
              <button className={`secondary-btn ${expTab === 'ideal' ? 'active-sub' : ''}`} onClick={() => setExpTab('ideal')}>1. Ideal Tuning</button>
              <button className={`secondary-btn ${expTab === 'robustness' ? 'active-sub' : ''}`} onClick={() => setExpTab('robustness')}>2. Robustness Sweep</button>
              <button className={`secondary-btn ${expTab === 'gainscheduling' ? 'active-sub' : ''}`} onClick={() => setExpTab('gainscheduling')}>3. Gain Scheduling</button>
              <button className={`secondary-btn ${expTab === 'lqrcompare' ? 'active-sub' : ''}`} onClick={() => setExpTab('lqrcompare')}>4. LQR vs PID</button>
            </div>
          )}

        <div style={{flex: 1, overflow: 'hidden'}}>
            <div style={{ display: mainTab === '3d' ? 'block' : 'none', position: 'relative', width: '100%', height: '100%', borderRadius: 12, overflow: 'hidden' }}>
                <Helicopter3D pitch={actualPitch} yaw={actualYaw} />
                {/* Settings Panel */}
                <div style={{position: 'absolute', top: 20, left: 20, width: 320, backgroundColor: 'rgba(0, 0, 0, 0.7)', borderRadius: 12, padding: 15, border: '1px solid #444', color: 'white'}}>
                    <h3 style={{margin: '0 0 15px 0', borderBottom: '1px solid #444', paddingBottom: 5, color: '#10b981'}}>3D SIMULATION SETTINGS</h3>
                    
                    <div className="form-group" style={{marginBottom: 15}}>
                        <label style={{fontSize: 12}}>Controller Algorithm</label>
                        <select value={simController} onChange={e => setSimController(e.target.value)} style={{background: 'rgba(0,0,0,0.5)', border: '1px solid #666', color: 'white', padding: '6px', borderRadius: 4, width: '100%'}}>
                            <option value="Manual">Manual Baseline</option>
                            <option value="GA">Genetic Algorithm (GA)</option>
                            <option value="PSO">Particle Swarm (PSO)</option>
                            <option value="TPE">TPE</option>
                            <option value="CMA-ES">CMA-ES</option>
                            <option value="GWO">Grey Wolf (GWO)</option>
                        </select>
                        {simController !== 'Manual' && !tunedParams[simController] && (
                            <div style={{color: '#f87171', fontSize: 11, marginTop: 5}}>⚠️ Controller {simController} has not been tuned yet. Falling back to Manual. Please run Ideal Tuning first.</div>
                        )}
                    </div>

                    <div style={{borderTop: '1px solid #444', paddingTop: 10}}>
                        <h4 style={{margin: '0 0 10px 0', fontSize: 13, color: '#a78bfa'}}>Disturbances</h4>
                        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10}}>
                            <div className="form-group" style={{marginBottom: 0}}>
                                <label style={{fontSize: 11}}>Wind Pitch</label>
                                <input type="number" step="0.01" value={distSim.wind_torque_p} onChange={e => setDistSim({...distSim, wind_torque_p: parseFloat(e.target.value)})} style={{padding: 4, width: '100%'}} />
                            </div>
                            <div className="form-group" style={{marginBottom: 0}}>
                                <label style={{fontSize: 11}}>Wind Yaw</label>
                                <input type="number" step="0.01" value={distSim.wind_torque_y} onChange={e => setDistSim({...distSim, wind_torque_y: parseFloat(e.target.value)})} style={{padding: 4, width: '100%'}} />
                            </div>
                            <div className="form-group" style={{marginBottom: 0}}>
                                <label style={{fontSize: 11}}>Sensor Noise</label>
                                <input type="number" step="0.01" value={distSim.sensor_noise_std} onChange={e => setDistSim({...distSim, sensor_noise_std: parseFloat(e.target.value)})} style={{padding: 4, width: '100%'}} />
                            </div>
                            <div className="form-group" style={{marginBottom: 0}}>
                                <label style={{fontSize: 11}}>Payload Ratio</label>
                                <input type="number" step="0.1" value={distSim.mass_payload} onChange={e => setDistSim({...distSim, mass_payload: parseFloat(e.target.value)})} style={{padding: 4, width: '100%'}} />
                            </div>
                        </div>
                    </div>
                </div>
                {/* HUD */}
                <div style={{position: 'absolute', top: 20, right: 20, width: 250, backgroundColor: 'rgba(0, 0, 0, 0.7)', borderRadius: 12, padding: 15, border: '1px solid #444', color: '#0f0', fontFamily: 'monospace'}}>
                    <h3 style={{margin: '0 0 10px 0', borderBottom: '1px solid #0f0', paddingBottom: 5}}>TELEMETRY</h3>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}><span>TGT PITCH:</span><span>{(joyPitch*180/Math.PI).toFixed(1)}°</span></div>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}><span>CUR PITCH:</span><span>{(actualPitch*180/Math.PI).toFixed(1)}°</span></div>
                    <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 5}}><span>TGT YAW:</span><span>{(joyYaw*180/Math.PI).toFixed(1)}°</span></div>
                    <div style={{display: 'flex', justifyContent: 'space-between'}}><span>CUR YAW:</span><span>{(actualYaw*180/Math.PI).toFixed(1)}°</span></div>
                </div>
                {/* Joystick */}
                <div style={{position: 'absolute', bottom: 30, right: 30, background: 'rgba(0,0,0,0.5)', borderRadius: '50%', padding: 10}}>
                    <Joystick size={120} stickSize={40} baseColor="rgba(255,255,255,0.1)" stickColor="rgba(167,139,250,0.8)"
                        move={(e) => {
                            setJoyYaw(e.x * 6.28); // Max 360 degrees
                            setJoyPitch(e.y * 1.05); // Max ~60 degrees
                        }}
                        stop={() => { setJoyYaw(0); setJoyPitch(0); }}
                    />
                </div>
            </div>

            <div style={{ display: mainTab === 'experiments' && expTab === 'ideal' ? 'block' : 'none', height: '100%', overflowY: 'auto' }}>
                <PageIdealTuning manualParams={manualParams} setManualParams={setManualParams} spPitch={spPitch} setSpPitch={setSpPitch} spYaw={spYaw} setSpYaw={setSpYaw} simDuration={simDuration} setSimDuration={setSimDuration} trajectoryType={trajectoryType} setTrajectoryType={setTrajectoryType} onUpdateTunedParams={(newTuned) => { setTunedParams(newTuned); setTunedParamsLarge(newTuned); }} setMainTab={setMainTab} setWikiDoc={setWikiDoc} />
            </div>

            <div style={{ display: mainTab === 'experiments' && expTab === 'robustness' ? 'block' : 'none', height: '100%', overflowY: 'auto' }}>
                <PageRobustness manualParams={manualParams} setManualParams={setManualParams} tunedParams={tunedParams} spPitch={spPitch} setSpPitch={setSpPitch} spYaw={spYaw} setSpYaw={setSpYaw} simDuration={simDuration} setSimDuration={setSimDuration} trajectoryType={trajectoryType} setTrajectoryType={setTrajectoryType} />
            </div>

            <div style={{ display: mainTab === 'experiments' && expTab === 'gainscheduling' ? 'block' : 'none', height: '100%', overflowY: 'auto' }}>
                <PageGainScheduling manualParams={manualParams} setManualParams={setManualParams} manualParamsLarge={manualParamsLarge} setManualParamsLarge={setManualParamsLarge} spPitch={spPitch} setSpPitch={setSpPitch} spYaw={spYaw} setSpYaw={setSpYaw} simDuration={simDuration} setSimDuration={setSimDuration} trajectoryType={trajectoryType} setTrajectoryType={setTrajectoryType} />
            </div>

            <div style={{ display: mainTab === 'wiki' ? 'block' : 'none', height: '100%', overflowY: 'auto' }}>
                <PageDocumentation activeDoc={wikiDoc} setActiveDoc={setWikiDoc} />
            </div>

            <div style={{ display: mainTab === 'history' ? 'block' : 'none', height: '100%', overflowY: 'auto' }}>
                <PageHistory />
            </div>

            <div style={{ display: mainTab === 'experiments' && expTab === 'lqrcompare' ? 'block' : 'none', height: '100%', overflowY: 'auto' }}>
                <PageLQRComparison />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
