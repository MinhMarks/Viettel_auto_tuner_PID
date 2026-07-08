import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import { ShieldCheck, Play } from 'lucide-react';
import GlobalConfigPanel from './GlobalConfigPanel';

const API_BASE = 'http://localhost:8088/api';

export default function PageRobustness() {
    const {
        manualParams, setManualParams,
        tunedParams,
        spPitch, setSpPitch,
        spYaw, setSpYaw,
        simDuration, setSimDuration,
        trajectoryType, setTrajectoryType,
    } = useAppContext();
    const [steps, setSteps] = useState(6);
    const [loading, setLoading] = useState(false);
    
    // Disturbance Configs
    const [disturbances, setDisturbances] = useState({ wind_torque_p: 0.0, wind_torque_y: 0.0, sensor_noise_std: 0.0, mass_payload: 1.0 });
    const [increments, setIncrements] = useState({ wind_torque_p: 0.01, wind_torque_y: 0.01, sensor_noise_std: 0.01, mass_payload: 0.1 });

    // Store results for each model
    // Shape: { Manual: { '0.00': metrics, ... }, GA: {...} }
    const [sweepResults, setSweepResults] = useState(null);
    const [visiblePlots, setVisiblePlots] = useState({ Manual: true, GA: true, PSO: false, TPE: false, "CMA-ES": false, GWO: false });

    const handleRunSweep = async () => {
        setLoading(true);
        try {
            const results = {};
            const runModel = async (name, params) => {
                if (!params) return;
                const res = await axios.post(`${API_BASE}/robustness_sweep`, {
                    params: params,
                    setpoint_pitch: spPitch * Math.PI / 180,
                    setpoint_yaw: spYaw * Math.PI / 180,
                    base_disturbance_config: disturbances,
                    step_increments: increments,
                    steps: steps,
                    t_max: simDuration,
                    trajectory_type: trajectoryType
                });
                results[name] = res.data;
            };

            await runModel('Manual', manualParams);
            if (tunedParams.GA) await runModel('GA', tunedParams.GA);
            if (tunedParams.PSO) await runModel('PSO', tunedParams.PSO);
            if (tunedParams.TPE) await runModel('TPE', tunedParams.TPE);
            if (tunedParams['CMA-ES']) await runModel('CMA-ES', tunedParams['CMA-ES']);
            if (tunedParams.GWO) await runModel('GWO', tunedParams.GWO);
            
            setSweepResults(results);

            // Log Experiment
            try {
                const exp = {
                    experiment_name: "Robustness Sweep",
                    tuning_method: "Multiple",
                    runs: []
                };
                
                Object.keys(results).forEach(alg => {
                    const runData = results[alg];
                    const params = alg === 'Manual' ? manualParams : tunedParams[alg];
                    Object.keys(runData).forEach(confLabel => {
                        const confData = runData[confLabel];
                        // E.g., confLabel is "Conf 1", or "0.000" if we parse it. The backend returns f"Conf {i+1}"
                        // Let's attach it as condition
                        exp.runs.push({
                            condition: `${alg} - ${confLabel}`,
                            algorithm: alg,
                            params: params || [],
                            disturbances: disturbances, // For robustness sweep, actual disturbance per step isn't tracked in history easily but base is.
                            metrics: confData.metrics || {},
                            cost_history: []
                        });
                    });
                });
                
                await axios.post(`${API_BASE}/history`, exp);
            } catch (err) {
                console.error("Failed to log history:", err);
            }
        } catch(e) { console.error(e); }
        setLoading(false);
    };

    const paramLabels = {
        'wind_torque_p': 'Wind Pitch (Nm)',
        'wind_torque_y': 'Wind Yaw (Nm)',
        'sensor_noise_std': 'Sensor Noise StdDev',
        'mass_payload': 'Payload Mass Ratio'
    };

    // Generate Robustness Line Chart Options
    const getChartOption = (metricKey, title) => {
        if (!sweepResults) return {};
        
        const series = [];
        let xAxisData = [];
        
        const colors = { 'Manual': '#ef4444', 'GA': '#3b82f6', 'PSO': '#10b981', 'TPE': '#ec4899', 'CMA-ES': '#f59e0b', 'GWO': '#8b5cf6' };

        Object.keys(sweepResults).forEach(model => {
            if (!visiblePlots[model]) return;
            const dataObj = sweepResults[model];
            xAxisData = Object.keys(dataObj).sort(); // Should be numeric strings like "0.000", "0.010"
            const yData = xAxisData.map(val => {
                const metric = dataObj[val].metrics.pitch[metricKey];
                return metric != null ? metric : null;
            });
            series.push({
                name: model,
                type: 'line',
                data: yData,
                smooth: true,
                itemStyle: { color: colors[model] }
            });
        });

        return {
            title: { text: title, textStyle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' }, top: 0, left: 'center' },
            tooltip: { trigger: 'axis' },
            legend: { data: Object.keys(sweepResults), top: 25, textStyle: { color: '#ffffff', fontSize: 12, fontWeight: 'bold' }, itemWidth: 10, itemHeight: 10 },
            dataZoom: [
                { type: 'inside', xAxisIndex: [0] },
                { type: 'slider', xAxisIndex: [0], bottom: 0, height: 16, textStyle: {color: '#ffffff'} }
            ],
            grid: { top: 60, bottom: 40, left: 50, right: 20 },
            xAxis: { type: 'category', data: xAxisData, name: 'Setup Config', nameLocation: 'middle', nameGap: 25, axisLabel: {fontSize: 11, color: '#ffffff', fontWeight: 'bold'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} },
            yAxis: { type: 'value', splitLine: { lineStyle: { color: '#444' } }, axisLabel: {color: '#ffffff', fontWeight: 'bold'} },
            series: series,
            backgroundColor: 'transparent'
        };
    };

    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: 16, height: '100%', overflowY: 'auto', paddingRight: 10}}>
            <GlobalConfigPanel />

            <div className="glass-panel" style={{padding: 16, display: 'flex', flexDirection: 'column', gap: 16}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap'}}>
                    <div style={{flex: 1, minWidth: 200}}>
                        <h3 style={{marginTop: 0, color: '#10b981'}}>Robustness Analysis</h3>
                        <p style={{fontSize: 13, color: '#ddd', margin: 0}}>Create custom testing configurations by defining base disturbance values and step increments.</p>
                    </div>
                    <div className="form-group" style={{marginBottom: 0, width: 120}}>
                        <label style={{fontSize: 12, color: '#ffffff'}}>Number of Configs</label>
                        <input type="number" min="2" value={steps} onChange={e => setSteps(parseInt(e.target.value))} />
                    </div>
                    <button className="primary" onClick={handleRunSweep} disabled={loading} style={{height: 40}}>
                        {loading ? <div className="loader"/> : <><ShieldCheck size={16}/> Run Sweep</>}
                    </button>
                </div>
                
                <table style={{width: '100%', fontSize: 13, borderCollapse: 'collapse', marginTop: 10}}>
                    <thead>
                        <tr style={{borderBottom: '1px solid #444', color: '#60a5fa'}}>
                            <th style={{textAlign: 'left', padding: '8px 4px'}}>Disturbance Type</th>
                            <th style={{padding: '8px 4px', width: '30%'}}>Base Value</th>
                            <th style={{padding: '8px 4px', width: '30%'}}>Step Increment</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.keys(paramLabels).map(key => (
                            <tr key={key} style={{borderBottom: '1px solid #333'}}>
                                <td style={{padding: '8px 4px', color: '#ffffff', fontWeight: 'bold'}}>{paramLabels[key]}</td>
                                <td style={{padding: '8px 4px'}}>
                                    <input type="number" step="0.01" value={disturbances[key]} onChange={e => setDisturbances({...disturbances, [key]: parseFloat(e.target.value)})} style={{width: '100%', padding: '6px 8px'}} />
                                </td>
                                <td style={{padding: '8px 4px'}}>
                                    <input type="number" step="0.01" value={increments[key]} onChange={e => setIncrements({...increments, [key]: parseFloat(e.target.value)})} style={{width: '100%', padding: '6px 8px'}} />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {sweepResults && (
                <div style={{display: 'flex', gap: 8, padding: '0 16px', zIndex: 10}}>
                   <button className={visiblePlots.Manual ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, Manual: !visiblePlots.Manual})} style={{padding: '4px 12px', fontSize: 12}}>Manual</button>
                   <button className={visiblePlots.GA ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GA: !visiblePlots.GA})} style={{padding: '4px 12px', fontSize: 12}}>GA</button>
                   <button className={visiblePlots.PSO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, PSO: !visiblePlots.PSO})} style={{padding: '4px 12px', fontSize: 12}}>PSO</button>
                   <button className={visiblePlots.TPE ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, TPE: !visiblePlots.TPE})} style={{padding: '4px 12px', fontSize: 12}}>TPE</button>
                   <button className={visiblePlots['CMA-ES'] ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, 'CMA-ES': !visiblePlots['CMA-ES']})} style={{padding: '4px 12px', fontSize: 12}}>CMA-ES</button>
                   <button className={visiblePlots.GWO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GWO: !visiblePlots.GWO})} style={{padding: '4px 12px', fontSize: 12}}>GWO</button>
                   <button className="secondary-btn" onClick={() => setVisiblePlots({Manual:true, GA:true, PSO:true, TPE:true, 'CMA-ES':true, GWO:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>
                </div>
            )}

            {sweepResults && (
                <div className="glass-panel" style={{padding: 16, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16}}>
                    <ReactECharts option={getChartOption('rise_time', 'Rise Time (s)')} notMerge={true} style={{height: 250}} />
                    <ReactECharts option={getChartOption('settling_time', 'Settling Time (s)')} notMerge={true} style={{height: 250}} />
                    <ReactECharts option={getChartOption('overshoot', 'Overshoot (%)')} notMerge={true} style={{height: 250}} />
                    <ReactECharts option={getChartOption('steady_state_error', 'Steady State Error')} notMerge={true} style={{height: 250}} />
                    <ReactECharts option={getChartOption('control_energy', 'Control Energy (V·s)')} notMerge={true} style={{height: 250}} />
                </div>
            )}
        </div>
    );
}
