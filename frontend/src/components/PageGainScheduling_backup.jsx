import React, { useState } from 'react';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import { Layers, Play } from 'lucide-react';
import GlobalConfigPanel from './GlobalConfigPanel';

const API_BASE = 'http://localhost:8088/api';

function ConsolidatedMetricsTable({ seriesData }) {
    if (!seriesData || seriesData.length === 0) return null;
    return (
        <div style={{overflowX: 'auto', marginTop: 0}}>
            <table style={{width: '100%', fontSize: 12, borderCollapse: 'collapse', textAlign: 'right'}}>
                <thead>
                    <tr style={{borderBottom: '1px solid #333'}}>
                        <th style={{textAlign:'left', padding:4}}>Model</th>
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
                        const mP = ds.data.metrics.pitch;
                        const mY = ds.data.metrics.yaw;
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

function TimeResponseChart({ title, dataSeries, timeAxis, spPitchData, spYawData, height = 300 }) {
    const series = [];
    const legend = [];

    dataSeries.forEach(ds => {
        if (!ds.data) return;
        series.push({ name: `${ds.name} P`, type: 'line', xAxisIndex: 0, yAxisIndex: 0, data: ds.data.pitch.map(p => (p * 180 / Math.PI).toFixed(2)), smooth: true, itemStyle: { color: ds.colorP } });
        series.push({ name: `${ds.name} Y`, type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: ds.data.yaw.map(p => (p * 180 / Math.PI).toFixed(2)), smooth: true, itemStyle: { color: ds.colorY } });
        legend.push(`${ds.name} P`, `${ds.name} Y`);
    });

    if (spPitchData && spYawData && timeAxis.length > 0) {
        series.push({ name: 'Target P', type: 'line', xAxisIndex: 0, yAxisIndex: 0, data: spPitchData, lineStyle: { type: 'dashed', color: '#60a5fa' } });
        series.push({ name: 'Target Y', type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: spYawData, lineStyle: { type: 'dashed', color: '#a78bfa' } });
        legend.push('Target P', 'Target Y');
    }

    const option = {
        title: { text: title, textStyle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' }, top: 0, left: 10 },
        tooltip: { trigger: 'axis' },
        legend: { type: 'scroll', data: legend, textStyle: { color: '#ffffff', fontWeight: 'bold' }, top: 0, right: 10, width: '50%' },
        grid: [{ top: '20%', height: '30%', left: '10%', right: '5%' }, { top: '65%', height: '30%', left: '10%', right: '5%' }],
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

    return <ReactECharts option={option} style={{ height, width: '100%' }} opts={{ renderer: 'canvas' }} />;
}

function GSMethodChartBlock({ alg, results, timeAxis, spPitchData, spYawData }) {
    const [visibleMethods, setVisibleMethods] = React.useState({ Step: true, Linear: true, Sigmoid: true });

    if (!results || !results[alg] || !results[alg].Step) return null;

    const seriesData = [];
    if (visibleMethods.Step) seriesData.push({ name: `${alg}-Step`, data: results[alg].Step, colorP: '#ef4444', colorY: '#fca5a5' });
    if (visibleMethods.Linear) seriesData.push({ name: `${alg}-Linear`, data: results[alg].Linear, colorP: '#f59e0b', colorY: '#fcd34d' });
    if (visibleMethods.Sigmoid) seriesData.push({ name: `${alg}-Sigmoid`, data: results[alg].Sigmoid, colorP: '#10b981', colorY: '#6ee7b7' });

    return (
        <div className="glass-panel" style={{padding: 16, display: 'flex', gap: 16, flexDirection: 'column'}}>
            <div style={{display:'flex', gap: 8, zIndex: 10}}>
               <button className={visibleMethods.Step ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisibleMethods({...visibleMethods, Step: !visibleMethods.Step})} style={{padding: '4px 12px', fontSize: 12}}>Step</button>
               <button className={visibleMethods.Linear ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisibleMethods({...visibleMethods, Linear: !visibleMethods.Linear})} style={{padding: '4px 12px', fontSize: 12}}>Linear</button>
               <button className={visibleMethods.Sigmoid ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisibleMethods({...visibleMethods, Sigmoid: !visibleMethods.Sigmoid})} style={{padding: '4px 12px', fontSize: 12}}>Sigmoid</button>
               <button className="secondary-btn" onClick={() => setVisibleMethods({Step:true, Linear:true, Sigmoid:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
                <TimeResponseChart title={`${alg}: Step vs Linear vs Sigmoid GS`} dataSeries={seriesData} timeAxis={timeAxis} spPitchData={spPitchData} spYawData={spYawData} height={350} />
                <ConsolidatedMetricsTable seriesData={seriesData} />
            </div>
        </div>
    );
}

export default function PageGainScheduling({ 
    manualParams, setManualParams, 
    manualParamsLarge, setManualParamsLarge, 
    spPitch, setSpPitch, 
    spYaw, setSpYaw, 
    simDuration, setSimDuration, 
    trajectoryType, setTrajectoryType 
}) {
    const [controllerType, setControllerType] = useState('classic'); // 'classic', 'model_based', 'fuzzy'
    const [itersInput, setItersInput] = useState({ GA: "", PSO: "20", BO: "" });
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [results, setResults] = useState(null);
    const [visiblePlots, setVisiblePlots] = useState({ Manual: true, GA: true, PSO: true, BO: true, Target: true });
    const [disturbances, setDisturbances] = useState({ wind_torque_p: 0.01, wind_torque_y: 0.01, sensor_noise_std: 0.1, mass_payload: 1.0 });
    
    const [tunedParamsGS, setTunedParamsGS] = useState({});
    const [tunedParamsLargeGS, setTunedParamsLargeGS] = useState({});
    const [abortController, setAbortController] = useState(null);

    const handleRunTuning = async () => {
        setLoading(true);
        setProgress(0);
        const controller = new AbortController();
        setAbortController(controller);
        window.currentProgressInterval = null;
        try {
            const iters_dict = {};
            ['GA', 'PSO', 'BO'].forEach(alg => {
                if (itersInput[alg].trim() !== '') {
                    const it = parseInt(itersInput[alg].trim());
                    if (!isNaN(it) && it > 0) iters_dict[alg] = [it]; // Just one target iteration for GS
                }
            });

            if (Object.keys(iters_dict).length === 0) {
                alert("Please enter iterations for at least one algorithm.");
                setLoading(false);
                return;
            }

            const taskId = Date.now().toString();
            window.currentProgressInterval = setInterval(async () => {
                try {
                    const progRes = await axios.get(`${API_BASE}/progress?task_id=${taskId}`);
                    setProgress(progRes.data.progress || 0);
                } catch (e) {}
            }, 500);
            
            // If classic GS, we optimize 12 dims using sigmoid gs_method.
            // If SOTA, we optimize 6 dims (base params) by setting controller_type and NO gs_method.
            const reqData = {
                task_id: taskId,
                setpoint_pitch: spPitch * Math.PI / 180, 
                setpoint_yaw: spYaw * Math.PI / 180,
                iters_dict, t_max: simDuration, disturbance_config: disturbances
            };
            
            if (controllerType === 'classic') {
                reqData.gs_method = 'sigmoid';
                reqData.controller_type = 'classic';
            } else {
                reqData.gs_method = 'step'; // Not used really, but keep default
                reqData.controller_type = controllerType;
            }

            const res = await axios.post(`${API_BASE}/compare_algorithms`, reqData, { signal: controller.signal });
            
            clearInterval(window.currentProgressInterval);
            setProgress(100);

            if (res.data) {
                const newTuned = { ...tunedParamsGS };
                const newTunedLarge = { ...tunedParamsLargeGS };
                
                ['GA', 'PSO', 'BO'].forEach(alg => {
                    if (res.data[alg]?.best_overall) {
                        const bp = res.data[alg].best_overall.best_params;
                        if (controllerType === 'classic' && bp.length === 12) {
                            newTuned[alg] = bp.slice(0, 6);
                            newTunedLarge[alg] = bp.slice(6, 12);
                        } else {
                            newTuned[alg] = bp.slice(0, 6);
                            // SOTA doesn't need large params
                        }
                    }
                });
                
                setTunedParamsGS(newTuned);
                setTunedParamsLargeGS(newTunedLarge);
                alert('Optimization Completed for selected algorithms!');
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

    const handleRun = async () => {
        setLoading(true);
        try {
            const resData = { Manual: {}, GA: {}, PSO: {}, BO: {} };

            const runSim = async (params, paramsLarge, gsMethod, cType) => {
                if (!params) return null;
                const req = await axios.post(`${API_BASE}/simulate`, {
                    params: params, params_large: paramsLarge,
                    setpoint_pitch: spPitch * Math.PI / 180, 
                    setpoint_yaw: spYaw * Math.PI / 180,
                    t_max: simDuration, disturbance_config: disturbances,
                    trajectory_type: trajectoryType, gs_method: gsMethod, controller_type: cType
                });
                return req.data;
            };

            if (controllerType === 'classic') {
                resData.Manual['None'] = await runSim(manualParams, null, 'step', 'classic');
                resData.Manual['Sigmoid'] = await runSim(manualParams, manualParamsLarge, 'sigmoid', 'classic');

                if (tunedParamsGS.GA) resData.GA['Sigmoid'] = await runSim(tunedParamsGS.GA, tunedParamsLargeGS.GA || tunedParamsGS.GA, 'sigmoid', 'classic');
                if (tunedParamsGS.PSO) resData.PSO['Sigmoid'] = await runSim(tunedParamsGS.PSO, tunedParamsLargeGS.PSO || tunedParamsGS.PSO, 'sigmoid', 'classic');
                if (tunedParamsGS.BO) resData.BO['Sigmoid'] = await runSim(tunedParamsGS.BO, tunedParamsLargeGS.BO || tunedParamsGS.BO, 'sigmoid', 'classic');

                const methods = ['Step', 'Linear'];
                for (let m of methods) {
                    if (tunedParamsGS.GA) resData.GA[m] = await runSim(tunedParamsGS.GA, tunedParamsLargeGS.GA || tunedParamsGS.GA, m.toLowerCase(), 'classic');
                    if (tunedParamsGS.PSO) resData.PSO[m] = await runSim(tunedParamsGS.PSO, tunedParamsLargeGS.PSO || tunedParamsGS.PSO, m.toLowerCase(), 'classic');
                    if (tunedParamsGS.BO) resData.BO[m] = await runSim(tunedParamsGS.BO, tunedParamsLargeGS.BO || tunedParamsGS.BO, m.toLowerCase(), 'classic');
                }
            } else {
                // SOTA Controllers (Model-Based or Fuzzy)
                resData.Manual['None'] = await runSim(manualParams, null, 'step', 'classic');
                resData.Manual['SOTA'] = await runSim(manualParams, null, 'step', controllerType);
                if (tunedParamsGS.GA) resData.GA['SOTA'] = await runSim(tunedParamsGS.GA, null, 'step', controllerType);
                if (tunedParamsGS.PSO) resData.PSO['SOTA'] = await runSim(tunedParamsGS.PSO, null, 'step', controllerType);
                if (tunedParamsGS.BO) resData.BO['SOTA'] = await runSim(tunedParamsGS.BO, null, 'step', controllerType);
            }

            setResults(resData);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    const refData = results?.Manual?.None;
    const timeAxis = refData ? refData.time.map(t => t.toFixed(2)) : [];
    const spPitchData = refData ? refData.sp_pitch.map(p => (p * 180 / Math.PI).toFixed(2)) : [];
    const spYawData = refData ? refData.sp_yaw.map(p => (p * 180 / Math.PI).toFixed(2)) : [];

    const mainSeries = [];
    if (results) {
        if (controllerType === 'classic') {
            if (visiblePlots.Manual && results.Manual.None) mainSeries.push({ name: 'Manual (NO GS)', data: results.Manual.None, colorP: '#666666', colorY: '#999999' });
            if (visiblePlots.Manual && results.Manual.Sigmoid) mainSeries.push({ name: 'Manual (GS)', data: results.Manual.Sigmoid, colorP: '#ef4444', colorY: '#f59e0b' });
            if (visiblePlots.GA && results.GA?.Sigmoid) mainSeries.push({ name: 'GA (GS)', data: results.GA.Sigmoid, colorP: '#3b82f6', colorY: '#93c5fd' });
            if (visiblePlots.PSO && results.PSO?.Sigmoid) mainSeries.push({ name: 'PSO (GS)', data: results.PSO.Sigmoid, colorP: '#10b981', colorY: '#6ee7b7' });
            if (visiblePlots.BO && results.BO?.Sigmoid) mainSeries.push({ name: 'BO (GS)', data: results.BO.Sigmoid, colorP: '#ec4899', colorY: '#f9a8d4' });
        } else {
            // SOTA
            if (visiblePlots.Manual && results.Manual.None) mainSeries.push({ name: 'Manual Baseline', data: results.Manual.None, colorP: '#666666', colorY: '#999999' });
            if (visiblePlots.Manual && results.Manual.SOTA) mainSeries.push({ name: `Manual (${controllerType})`, data: results.Manual.SOTA, colorP: '#ef4444', colorY: '#f59e0b' });
            if (visiblePlots.GA && results.GA?.SOTA) mainSeries.push({ name: `GA (${controllerType})`, data: results.GA.SOTA, colorP: '#3b82f6', colorY: '#93c5fd' });
            if (visiblePlots.PSO && results.PSO?.SOTA) mainSeries.push({ name: `PSO (${controllerType})`, data: results.PSO.SOTA, colorP: '#10b981', colorY: '#6ee7b7' });
            if (visiblePlots.BO && results.BO?.SOTA) mainSeries.push({ name: `BO (${controllerType})`, data: results.BO.SOTA, colorP: '#ec4899', colorY: '#f9a8d4' });
        }
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
                <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
                    <div style={{flex: 1}}>
                        <h3 style={{marginTop: 0, color: '#f59e0b'}}>Adaptive Control Analysis</h3>
                        <p style={{fontSize: 13, color: '#aaa', margin: 0}}>Compare Classic GS with SOTA Real-time Adaptive Control.</p>
                    </div>
                    <div className="form-group" style={{marginBottom: 0, width: 220}}>
                        <label style={{fontSize: 12}}>Controller Type</label>
                        <select value={controllerType} onChange={e => { setControllerType(e.target.value); setResults(null); }} style={{width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: 'white', padding: 4, borderRadius: 4}}>
                            <option value="classic">Classic GS (Interpolation)</option>
                            <option value="model_based">Model-Based Compensation</option>
                            <option value="fuzzy">Fuzzy Adaptive PID</option>
                        </select>
                    </div>
                </div>
                
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
                    <div style={{display: 'flex', gap: 12, alignItems: 'flex-end'}}>
                        {['GA', 'PSO', 'BO'].map(alg => (
                            <div key={alg} style={{display: 'flex', flexDirection: 'column'}}>
                                <label style={{fontSize: 11, color: '#aaa'}}>{alg} Iters</label>
                                <input type="text" value={itersInput[alg]} onChange={e => setItersInput({...itersInput, [alg]: e.target.value})} style={{width: 60, background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: 'white', padding: 4, borderRadius: 4}} />
                            </div>
                        ))}
                    </div>
                    <div style={{display: 'flex', alignItems: 'flex-end', gap: 10}}>
                        <button className="primary-btn" onClick={handleRunTuning} disabled={loading} style={{height: 32, fontSize: 12}}>
                            {loading ? `Tuning... ${Math.round(progress)}%` : 'Auto-Tune'}
                        </button>
                        {loading && (
                            <button className="secondary-btn" onClick={handleStop} style={{height: 32, fontSize: 12, backgroundColor: '#dc2626', color: 'white', borderColor: '#dc2626'}}>
                                Stop
                            </button>
                        )}
                        <button className="primary" onClick={handleRun} disabled={loading} style={{height: 32, fontSize: 12}}>
                            {loading ? <div className="loader"/> : <><Layers size={14}/> Simulate</>}
                        </button>
                    </div>
                </div>
                {loading && (
                    <div style={{ background: '#333', borderRadius: 4, height: 6, overflow: 'hidden', width: '100%', gridColumn: '1 / -1' }}>
                        <div style={{ height: '100%', background: '#a78bfa', width: `${progress}%`, transition: 'width 0.3s ease' }}></div>
                    </div>
                )}
            </div>

            {/* Block 1: Main */}
            <div className="glass-panel" style={{padding: 16, display: 'flex', gap: 16, flexDirection: 'column'}}>
                <div style={{display:'flex', gap: 8, zIndex: 10}}>
                   <button className={visiblePlots.Manual ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, Manual: !visiblePlots.Manual})} style={{padding: '4px 12px', fontSize: 12}}>Manual</button>
                   <button className={visiblePlots.GA ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GA: !visiblePlots.GA})} style={{padding: '4px 12px', fontSize: 12}}>GA</button>
                   <button className={visiblePlots.PSO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, PSO: !visiblePlots.PSO})} style={{padding: '4px 12px', fontSize: 12}}>PSO</button>
                   <button className={visiblePlots.BO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, BO: !visiblePlots.BO})} style={{padding: '4px 12px', fontSize: 12}}>BO</button>
                   <button className="secondary-btn" onClick={() => setVisiblePlots({Manual:true, GA:true, PSO:true, BO:true, Target:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>
                </div>
                <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
                    <TimeResponseChart title={controllerType === 'classic' ? "Comparison of Best Models (GS)" : "SOTA Controller Performance"} dataSeries={mainSeries} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} height={400} />
                    <ConsolidatedMetricsTable seriesData={mainSeries} />
                </div>
            </div>

            {/* Sub-blocks only for Classic GS */}
            {controllerType === 'classic' && (
                <>
                    <GSMethodChartBlock alg="GA" results={results} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
                    <GSMethodChartBlock alg="PSO" results={results} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
                    <GSMethodChartBlock alg="BO" results={results} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
                </>
            )}
        </div>
    );
}
