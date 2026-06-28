import React, { useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import { Layers, Play, Settings } from 'lucide-react';
import GlobalConfigPanel from './GlobalConfigPanel';

const API_BASE = 'http://localhost:8088/api';

function ConsolidatedMetricsTable({ seriesData }) {
    if (!seriesData || seriesData.length === 0) return null;
    return (
        <div style={{overflowX: 'auto', marginTop: 0}}>
            <table style={{width: '100%', fontSize: 12, borderCollapse: 'collapse', textAlign: 'right'}}>
                <thead>
                    <tr style={{borderBottom: '1px solid #333'}}>
                        <th style={{textAlign:'left', padding:4}}>Controller Option</th>
                        <th style={{padding:4, color: '#60a5fa'}}>Rise (P)</th>
                        <th style={{padding:4, color: '#60a5fa'}}>Set (P)</th>
                        <th style={{padding:4, color: '#60a5fa'}}>OS (P)</th>
                        <th style={{padding:4, color: '#60a5fa'}}>SSE (P)</th>
                        <th style={{padding:4, color: '#60a5fa'}}>ITAE (P)</th>
                        <th style={{padding:4, color: '#60a5fa'}}>Energy (P)</th>
                        <th style={{padding:4, color: '#a78bfa'}}>Rise (Y)</th>
                        <th style={{padding:4, color: '#a78bfa'}}>Set (Y)</th>
                        <th style={{padding:4, color: '#a78bfa'}}>OS (Y)</th>
                        <th style={{padding:4, color: '#a78bfa'}}>SSE (Y)</th>
                        <th style={{padding:4, color: '#a78bfa'}}>ITAE (Y)</th>
                        <th style={{padding:4, color: '#a78bfa'}}>Energy (Y)</th>
                    </tr>
                </thead>
                <tbody>
                    {seriesData.map(ds => {
                        const mP = ds.data?.metrics?.pitch;
                        const mY = ds.data?.metrics?.yaw;
                        if (!mP || !mY) return null;
                        return (
                            <tr key={ds.name} style={{borderBottom: '1px solid #222'}}>
                                <td style={{textAlign:'left', padding:4, fontWeight: 'bold', color: ds.colorP}}>{ds.name}</td>
                                <td style={{padding:4}}>{mP?.rise_time?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mP?.settling_time?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mP?.overshoot?.toFixed(1) || '-'}</td>
                                <td style={{padding:4}}>{mP?.steady_state_error?.toFixed(4) || '-'}</td>
                                <td style={{padding:4}}>{mP?.itae?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mP?.control_energy?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mY?.rise_time?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mY?.settling_time?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mY?.overshoot?.toFixed(1) || '-'}</td>
                                <td style={{padding:4}}>{mY?.steady_state_error?.toFixed(4) || '-'}</td>
                                <td style={{padding:4}}>{mY?.itae?.toFixed(2) || '-'}</td>
                                <td style={{padding:4}}>{mY?.control_energy?.toFixed(2) || '-'}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

function TimeResponseChart({ title, dataSeries, timeAxis, spPitchData, spYawData, height = 400 }) {
    const series = [];
    const legendPitch = [];
    const legendYaw = [];

    dataSeries.forEach(ds => {
        if (!ds.data) return;
        series.push({ name: `${ds.name} P`, type: 'line', xAxisIndex: 0, yAxisIndex: 0, data: ds.data.pitch.map(p => (p * 180 / Math.PI).toFixed(2)), smooth: true, itemStyle: { color: ds.colorP } });
        series.push({ name: `${ds.name} Y`, type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: ds.data.yaw.map(p => (p * 180 / Math.PI).toFixed(2)), smooth: true, itemStyle: { color: ds.colorY } });
        legendPitch.push(`${ds.name} P`);
        legendYaw.push(`${ds.name} Y`);
    });

    if (spPitchData && spYawData && timeAxis.length > 0) {
        series.push({ name: 'Target P', type: 'line', xAxisIndex: 0, yAxisIndex: 0, data: spPitchData, lineStyle: { type: 'dashed', color: '#60a5fa' } });
        series.push({ name: 'Target Y', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: spYawData, lineStyle: { type: 'dashed', color: '#a78bfa' } });
        legendPitch.push('Target P');
        legendYaw.push('Target Y');
    }

    const option = {
        title: { text: title, textStyle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' }, top: 0, left: 10 },
        tooltip: { trigger: 'axis' },
        legend: [
            // Pitch Legend
            { type: 'scroll', data: legendPitch, textStyle: { color: '#ffffff', fontWeight: 'bold' }, top: '5%', left: 'center', width: '80%' },
            // Yaw Legend
            { type: 'scroll', data: legendYaw, textStyle: { color: '#ffffff', fontWeight: 'bold' }, top: '55%', left: 'center', width: '80%' }
        ],
        grid: [{ top: '15%', height: '35%', left: '10%', right: '5%' }, { top: '65%', height: '35%', left: '10%', right: '5%' }],
        dataZoom: [
            { type: 'inside', xAxisIndex: [0, 1] },
            { type: 'slider', xAxisIndex: [0, 1], bottom: 0, height: 16, textStyle: {color: '#ffffff', fontWeight: 'bold'} }
        ],
        xAxis: [
            { gridIndex: 0, type: 'category', data: timeAxis.map(t => t), show: false },
            { gridIndex: 1, type: 'category', data: timeAxis.map(t => t), name: 'Time (s)', nameLocation: 'middle', nameGap: 20, axisLabel: {color: '#ffffff', fontWeight: 'bold'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} }
        ],
        yAxis: [
            { gridIndex: 0, type: 'value', name: 'Pitch (deg)', splitLine: { lineStyle: { color: '#444' } }, axisLabel: {color: '#ffffff', fontWeight: 'bold'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} },
            { gridIndex: 1, type: 'value', name: 'Yaw (deg)', splitLine: { lineStyle: { color: '#444' } }, axisLabel: {color: '#ffffff', fontWeight: 'bold'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} }
        ],
        series: series,
        backgroundColor: 'transparent'
    };

    return <ReactECharts option={option} notMerge={true} style={{ height, width: '100%' }} opts={{ renderer: 'canvas' }} />;
}

export default function PageGainScheduling({ 
    manualParams, setManualParams, 
    manualParamsLarge, setManualParamsLarge, 
    spPitch, setSpPitch, 
    spYaw, setSpYaw, 
    simDuration, setSimDuration, 
    trajectoryType, setTrajectoryType 
}) {
    const [tuningMethod, setTuningMethod] = useState('PSO'); // Manual, GA, PSO, BO
    const [tuningIters, setTuningIters] = useState(20);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [results, setResults] = useState(null); // stores { None, Classic, ModelBased, Fuzzy }
    
    const [visiblePlots, setVisiblePlots] = useState({ None: true, Classic: true, ModelBased: true, Fuzzy: true, Target: true });
    const [disturbances, setDisturbances] = useState({ wind_torque_p: 0.01, wind_torque_y: 0.01, sensor_noise_std: 0.1, mass_payload: 1.0 });
    const [abortController, setAbortController] = useState(null);

    const handleLoadLQR = async () => {
        try {
            const res = await axios.get(`${API_BASE}/lqr_baseline`);
            if (res.data && res.data.baseline_params) {
                setManualParams(res.data.baseline_params);
                setManualParamsLarge(res.data.baseline_params); // set same for large by default
            }
        } catch(e) { console.error(e); }
    };

    const handleRunAnalysis = async () => {
        setLoading(true);
        setProgress(0);
        setResults(null);
        const controller = new AbortController();
        setAbortController(controller);
        window.currentProgressInterval = null;

        try {
            const resData = { None: null, Classic: null, ModelBased: null, Fuzzy: null };
            
            // Helper to run simulation directly
            const runSim = async (params, paramsLarge, gsMethod, cType) => {
                const req = await axios.post(`${API_BASE}/simulate`, {
                    params: params, params_large: paramsLarge,
                    setpoint_pitch: spPitch * Math.PI / 180, 
                    setpoint_yaw: spYaw * Math.PI / 180,
                    t_max: simDuration, disturbance_config: disturbances,
                    trajectory_type: trajectoryType, gs_method: gsMethod, controller_type: cType
                }, { signal: controller.signal });
                return req.data;
            };

            if (tuningMethod === 'Manual') {
                setProgress(10);
                resData.None = await runSim(manualParams, null, 'step', 'classic'); // No GS
                setProgress(30);
                resData.Classic = await runSim(manualParams, manualParamsLarge, 'sigmoid', 'classic');
                setProgress(60);
                resData.ModelBased = await runSim(manualParams, null, 'step', 'model_based');
                setProgress(90);
                resData.Fuzzy = await runSim(manualParams, null, 'step', 'fuzzy');
                setProgress(100);
            } else {
                const taskId = Date.now().toString();
                
                // Track progress of the tuning backend
                window.currentProgressInterval = setInterval(async () => {
                    try {
                        const progRes = await axios.get(`${API_BASE}/progress?task_id=${taskId}`);
                        // The backend returns progress for the current single algorithm tuning
                        const currProg = progRes.data.progress || 0;
                        setProgress((completedRuns * 25) + (currProg / 4)); 
                    } catch (e) {}
                }, 500);

                let completedRuns = 0;
                const iters_dict = {};
                iters_dict[tuningMethod] = [tuningIters];

                // Options to test
                const options = [
                    { key: 'None', reqData: { controller_type: 'classic', gs_method: 'step' } }, // we will slice 6 params
                    { key: 'Classic', reqData: { controller_type: 'classic', gs_method: 'sigmoid' } }, // 12 params
                    { key: 'ModelBased', reqData: { controller_type: 'model_based', gs_method: 'step' } },
                    { key: 'Fuzzy', reqData: { controller_type: 'fuzzy', gs_method: 'step' } },
                ];

                for (const opt of options) {
                    const reqData = {
                        task_id: taskId,
                        setpoint_pitch: spPitch * Math.PI / 180, 
                        setpoint_yaw: spYaw * Math.PI / 180,
                        iters_dict, t_max: simDuration, disturbance_config: disturbances,
                        controller_type: opt.reqData.controller_type,
                        gs_method: opt.reqData.gs_method
                    };
                    
                    const optRes = await axios.post(`${API_BASE}/compare_algorithms`, reqData, { signal: controller.signal });
                    
                    if (optRes.data && optRes.data[tuningMethod] && optRes.data[tuningMethod].best_overall) {
                        const bp = optRes.data[tuningMethod].best_overall.best_params;
                        // Simulate best result
                        let simParams = [];
                        let simParamsLarge = null;
                        
                        if (opt.key === 'None' || opt.key === 'ModelBased' || opt.key === 'Fuzzy') {
                            simParams = bp.slice(0, 6);
                        } else if (opt.key === 'Classic') {
                            simParams = bp.slice(0, 6);
                            simParamsLarge = bp.length === 12 ? bp.slice(6, 12) : null;
                        }

                        resData[opt.key] = await runSim(simParams, simParamsLarge, opt.reqData.gs_method, opt.reqData.controller_type);
                    }
                    completedRuns += 1;
                    setProgress(completedRuns * 25);
                }
                
                clearInterval(window.currentProgressInterval);
                setProgress(100);
            }
            setResults(resData);

            // Log Experiment
            try {
                const exp = {
                    experiment_name: "SOTA Options Analysis (Gain Scheduling)",
                    tuning_method: tuningMethod,
                    runs: []
                };
                
                const optionKeys = ['None', 'Classic', 'ModelBased', 'Fuzzy'];
                for (const key of optionKeys) {
                    if (resData[key]) {
                        // Extract params from backend response or frontend state
                        // The sim result unfortunately doesn't return params, but we can just leave it blank or grab manual ones
                        let params = tuningMethod === 'Manual' ? manualParams : [];
                        let paramsLarge = tuningMethod === 'Manual' ? manualParamsLarge : null;
                        
                        exp.runs.push({
                            condition: key,
                            algorithm: tuningMethod,
                            params: params,
                            params_large: paramsLarge,
                            disturbances: disturbances,
                            metrics: resData[key].metrics || {},
                            cost_history: []
                        });
                    }
                }
                await axios.post(`${API_BASE}/history`, exp);
            } catch (err) {
                console.error("Failed to log history:", err);
            }
        } catch (error) {
            console.error("Error during GS tuning:", error);
            if (window.currentProgressInterval) clearInterval(window.currentProgressInterval);
        } finally {
            setLoading(false);
            setAbortController(null);
        }
    };

    const handleStop = () => {
        if (abortController) {
            abortController.abort();
            setAbortController(null);
            setLoading(false);
            if (window.currentProgressInterval) clearInterval(window.currentProgressInterval);
        }
    };

    const refData = results?.None || results?.Classic;
    const timeAxis = refData ? refData.time.map(t => t.toFixed(2)) : [];
    const spPitchData = refData ? refData.sp_pitch.map(p => (p * 180 / Math.PI).toFixed(2)) : [];
    const spYawData = refData ? refData.sp_yaw.map(p => (p * 180 / Math.PI).toFixed(2)) : [];

    const mainSeries = [];
    if (results) {
        if (visiblePlots.None && results.None) mainSeries.push({ name: 'None (PID)', data: results.None, colorP: '#9ca3af', colorY: '#d1d5db' });
        if (visiblePlots.Classic && results.Classic) mainSeries.push({ name: 'Classic GS', data: results.Classic, colorP: '#3b82f6', colorY: '#93c5fd' });
        if (visiblePlots.ModelBased && results.ModelBased) mainSeries.push({ name: 'Model-Based', data: results.ModelBased, colorP: '#10b981', colorY: '#6ee7b7' });
        if (visiblePlots.Fuzzy && results.Fuzzy) mainSeries.push({ name: 'Fuzzy Adaptive', data: results.Fuzzy, colorP: '#ec4899', colorY: '#f9a8d4' });
    }

    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: 16, height: '100%', overflowY: 'auto', paddingRight: 10}}>
            <GlobalConfigPanel 
                manualParams={manualParams} setManualParams={setManualParams}
                spPitch={spPitch} setSpPitch={setSpPitch}
                spYaw={spYaw} setSpYaw={setSpYaw}
                simDuration={simDuration} setSimDuration={setSimDuration}
                trajectoryType={trajectoryType} setTrajectoryType={setTrajectoryType}
            />

            <div className="glass-panel" style={{padding: 16, display: 'flex', flexDirection: 'column', gap: 16}}>
                <div style={{display: 'flex', alignItems: 'flex-start', gap: 16}}>
                    <div style={{flex: 1}}>
                        <h3 style={{marginTop: 0, color: '#f59e0b'}}>SOTA Options Analysis</h3>
                        <p style={{fontSize: 13, color: '#aaa', margin: 0}}>Evaluate 4 Gain Scheduling Options with the selected Tuning Method.</p>
                        
                        <div style={{display: 'flex', gap: 16, marginTop: 15}}>
                            <div className="form-group" style={{marginBottom: 0, width: 150}}>
                                <label style={{fontSize: 12}}>Tuning Method</label>
                                <select value={tuningMethod} onChange={e => setTuningMethod(e.target.value)} style={{width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: 'white', padding: 4, borderRadius: 4}}>
                                    <option value="Manual">Manual</option>
                                    <option value="GA">GA</option>
                                    <option value="PSO">PSO</option>
                                    <option value="BO">BO</option>
                                </select>
                            </div>

                            {tuningMethod !== 'Manual' && (
                                <div className="form-group" style={{marginBottom: 0, width: 100}}>
                                    <label style={{fontSize: 12}}>Iterations</label>
                                    <input type="number" min="1" value={tuningIters} onChange={e => setTuningIters(parseInt(e.target.value))} style={{width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: 'white', padding: 4, borderRadius: 4}} />
                                </div>
                            )}

                            {tuningMethod === 'Manual' && (
                                <button className="secondary-btn" onClick={handleLoadLQR} style={{alignSelf: 'flex-end', height: 28, fontSize: 12}}>
                                    Load LQR Baseline
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {tuningMethod === 'Manual' && (
                    <div style={{border: '1px dashed #444', padding: 12, borderRadius: 8}}>
                        <h4 style={{margin: '0 0 10px 0', fontSize: 12, color: '#aaa'}}>Classic GS Large Angle Parameters (Manual mode only)</h4>
                        <div style={{display: 'flex', gap: 10}}>
                            {['Kp_P', 'Ki_P', 'Kd_P', 'Kp_Y', 'Ki_Y', 'Kd_Y'].map((lbl, i) => (
                                <div key={lbl} style={{display: 'flex', flexDirection: 'column'}}>
                                    <label style={{fontSize: 10, color: '#888'}}>{lbl}</label>
                                    <input type="number" step="0.1" value={manualParamsLarge[i]} 
                                        onChange={e => {
                                            const np = [...manualParamsLarge];
                                            np[i] = parseFloat(e.target.value) || 0;
                                            setManualParamsLarge(np);
                                        }} 
                                        style={{width: 50, background: 'rgba(0,0,0,0.3)', border: '1px solid #555', color: 'white', padding: '2px 4px', fontSize: 11, borderRadius: 3}} 
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                <div style={{display: 'flex', gap: 16, padding: '10px 0', borderTop: '1px solid #333'}}>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Wind Pitch (Nm)</label>
                        <input type="number" step="0.01" value={disturbances.wind_torque_p} onChange={e => setDisturbances({...disturbances, wind_torque_p: parseFloat(e.target.value)})} style={{padding: 4}}/>
                    </div>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Wind Yaw (Nm)</label>
                        <input type="number" step="0.01" value={disturbances.wind_torque_y} onChange={e => setDisturbances({...disturbances, wind_torque_y: parseFloat(e.target.value)})} style={{padding: 4}}/>
                    </div>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Sensor Noise StdDev</label>
                        <input type="number" step="0.01" value={disturbances.sensor_noise_std} onChange={e => setDisturbances({...disturbances, sensor_noise_std: parseFloat(e.target.value)})} style={{padding: 4}}/>
                    </div>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Payload Ratio</label>
                        <input type="number" step="0.1" value={disturbances.mass_payload} onChange={e => setDisturbances({...disturbances, mass_payload: parseFloat(e.target.value)})} style={{padding: 4}}/>
                    </div>
                    
                    <div style={{flex: 1}}></div>
                    
                    <div style={{display: 'flex', alignItems: 'flex-end', gap: 10}}>
                        <button className="primary-btn" onClick={handleRunAnalysis} disabled={loading} style={{height: 32, fontSize: 12}}>
                            {loading ? `Analyzing... ${Math.round(progress)}%` : <><Play size={14} style={{marginRight: 4}} /> Run Analysis</>}
                        </button>
                        {loading && (
                            <button className="secondary-btn" onClick={handleStop} style={{height: 32, fontSize: 12, backgroundColor: '#dc2626', color: 'white', borderColor: '#dc2626'}}>
                                Stop
                            </button>
                        )}
                    </div>
                </div>
                {loading && (
                    <div style={{ background: '#333', borderRadius: 4, height: 6, overflow: 'hidden', width: '100%', gridColumn: '1 / -1' }}>
                        <div style={{ height: '100%', background: '#a78bfa', width: `${progress}%`, transition: 'width 0.3s ease' }}></div>
                    </div>
                )}
            </div>

            {/* Results Block */}
            {results && (
                <div className="glass-panel" style={{padding: 16, display: 'flex', gap: 16, flexDirection: 'column'}}>
                    <div style={{display:'flex', gap: 8, zIndex: 10}}>
                        <button className={visiblePlots.None ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, None: !visiblePlots.None})} style={{padding: '4px 12px', fontSize: 12}}>None (PID)</button>
                        <button className={visiblePlots.Classic ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, Classic: !visiblePlots.Classic})} style={{padding: '4px 12px', fontSize: 12}}>Classic GS</button>
                        <button className={visiblePlots.ModelBased ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, ModelBased: !visiblePlots.ModelBased})} style={{padding: '4px 12px', fontSize: 12}}>Model-Based</button>
                        <button className={visiblePlots.Fuzzy ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, Fuzzy: !visiblePlots.Fuzzy})} style={{padding: '4px 12px', fontSize: 12}}>Fuzzy Adaptive</button>
                        <button className="secondary-btn" onClick={() => setVisiblePlots({None:true, Classic:true, ModelBased:true, Fuzzy:true, Target:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>
                    </div>
                    
                    <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
                        <TimeResponseChart 
                            title={`Gain Scheduling Options Comparison (${tuningMethod})`} 
                            dataSeries={mainSeries} 
                            timeAxis={timeAxis} 
                            spPitchData={visiblePlots.Target ? spPitchData : null} 
                            spYawData={visiblePlots.Target ? spYawData : null} 
                            height={450} 
                        />
                        <ConsolidatedMetricsTable seriesData={mainSeries} />
                    </div>
                </div>
            )}
        </div>
    );
}
