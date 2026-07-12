import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import { ShieldAlert, Plus, Trash2 } from 'lucide-react';
import GlobalConfigPanel from './GlobalConfigPanel';

const API_BASE = 'http://localhost:8088/api';

export default function PageRobustnessRejection() {
    const {
        manualParams,
        tunedParams,
        spPitch, spYaw,
        simDuration, trajectoryType
    } = useAppContext();

    const [events, setEvents] = useState([
        { id: 1, start: 10, end: 15, config: { wind_torque_p: 0.1, wind_torque_y: 0.05, mass_payload: 0.0, sensor_noise_std: 0.0 } },
        { id: 2, start: 30, end: 35, config: { wind_torque_p: 0.0, wind_torque_y: 0.0, mass_payload: 0.5, sensor_noise_std: 0.0 } }
    ]);
    
    const [baseDist, setBaseDist] = useState({ wind_torque_p: 0.0, wind_torque_y: 0.0, sensor_noise_std: 0.0, mass_payload: 0.0 });
    const [visiblePlots, setVisiblePlots] = useState({ Manual: true, GA: true, PSO: true, TPE: false, "CMA-ES": false, GWO: false, "MIMO LQR": true });
    const [loading, setLoading] = useState(false);
    const [simData, setSimData] = useState(null);

    const handleAddEvent = () => {
        const newId = events.length > 0 ? Math.max(...events.map(e => e.id)) + 1 : 1;
        setEvents([...events, { id: newId, start: 0, end: 5, config: { wind_torque_p: 0.0, wind_torque_y: 0.0, mass_payload: 0.0, sensor_noise_std: 0.0 } }]);
    };

    const handleRemoveEvent = (id) => {
        setEvents(events.filter(e => e.id !== id));
    };

    const updateEvent = (id, field, value) => {
        setEvents(events.map(e => e.id === id ? { ...e, [field]: parseFloat(value) || 0 } : e));
    };

    const updateEventConfig = (id, key, value) => {
        setEvents(events.map(e => {
            if (e.id === id) {
                return { ...e, config: { ...e.config, [key]: parseFloat(value) || 0 } };
            }
            return e;
        }));
    };

    const handleRunTest = async () => {
        setLoading(true);
        try {
            const results = {};
            
            // Format disturbance sequence for API
            const seq = events.map(e => ({ start: e.start, end: e.end, config: e.config }));
            
            const runModel = async (name, params, type = 'classic') => {
                if (!params) return;
                const res = await axios.post(`${API_BASE}/simulate`, {
                    params: params,
                    setpoint_pitch: spPitch * Math.PI / 180,
                    setpoint_yaw: spYaw * Math.PI / 180,
                    t_max: simDuration,
                    trajectory_type: trajectoryType,
                    controller_type: type,
                    disturbance_config: baseDist,
                    disturbance_sequence: seq
                });
                results[name] = res.data;
            };

            await runModel('Manual', manualParams);
            if (tunedParams.GA) await runModel('GA', tunedParams.GA);
            if (tunedParams.PSO) await runModel('PSO', tunedParams.PSO);
            if (tunedParams.TPE) await runModel('TPE', tunedParams.TPE);
            if (tunedParams['CMA-ES']) await runModel('CMA-ES', tunedParams['CMA-ES']);
            if (tunedParams.GWO) await runModel('GWO', tunedParams.GWO);
            if (tunedParams['MIMO LQR']) await runModel('MIMO LQR', tunedParams['MIMO LQR'], 'mimo_lqr');

            setSimData(results);
        } catch (error) {
            console.error(error);
        }
        setLoading(false);
    };

    // Prepare ECharts Options
    const getChartOption = (metricIndex, title, yAxisLabel) => {
        if (!simData) return {};

        const series = [];
        const colors = { 'Manual': '#ef4444', 'GA': '#3b82f6', 'PSO': '#10b981', 'TPE': '#ec4899', 'CMA-ES': '#f59e0b', 'GWO': '#8b5cf6', 'MIMO LQR': '#06b6d4' };

        // Determine markArea from events
        const markAreaData = events.map(e => [
            { xAxis: e.start, itemStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
            { xAxis: e.end }
        ]);

        let timeArr = [];
        let setpointArr = [];
        
        Object.keys(simData).forEach(model => {
            if (!visiblePlots[model]) return;
            const data = simData[model];
            if (timeArr.length === 0) {
                timeArr = data.time;
                setpointArr = metricIndex === 0 ? data.sp_pitch : data.sp_yaw;
            }
            
            const signal = metricIndex === 0 ? data.pitch : data.yaw;
            // Downsample for rendering
            const step = Math.max(1, Math.floor(timeArr.length / 500));
            const dsSignal = signal.filter((_, i) => i % step === 0).map(v => v * 180 / Math.PI); // Convert to degrees
            
            series.push({
                name: model,
                type: 'line',
                data: dsSignal,
                showSymbol: false,
                lineStyle: { width: 2 },
                itemStyle: { color: colors[model] },
                markArea: {
                    data: markAreaData,
                    label: { show: true, position: 'insideTop', color: '#fff', fontSize: 10, formatter: 'Disturbance' }
                }
            });
        });

        // Add setpoint line
        if (setpointArr.length > 0) {
            const step = Math.max(1, Math.floor(timeArr.length / 500));
            series.push({
                name: 'Setpoint',
                type: 'line',
                data: setpointArr.filter((_, i) => i % step === 0).map(v => v * 180 / Math.PI),
                showSymbol: false,
                lineStyle: { type: 'dashed', color: '#aaa', width: 2 },
            });
        }

        return {
            title: { text: title, textStyle: { color: '#ffffff', fontSize: 14 } },
            tooltip: { trigger: 'axis' },
            legend: { top: 25, textStyle: { color: '#fff' } },
            grid: { top: 60, bottom: 40, left: 50, right: 20 },
            xAxis: { 
                type: 'category', 
                data: timeArr.filter((_, i) => i % Math.max(1, Math.floor(timeArr.length / 500)) === 0).map(t => t.toFixed(2)),
                name: 'Time (s)', nameLocation: 'middle', nameGap: 25,
                axisLabel: { color: '#fff' }
            },
            yAxis: { type: 'value', name: yAxisLabel, splitLine: { lineStyle: { color: '#444' } }, axisLabel: { color: '#fff' } },
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
                        <h3 style={{marginTop: 0, color: '#f43f5e'}}>Dynamic Disturbance Rejection</h3>
                        <p style={{fontSize: 13, color: '#ddd', margin: 0}}>Evaluate control recovery from time-varying environmental shocks.</p>
                    </div>
                    <button className="secondary" onClick={handleAddEvent} style={{height: 40}}>
                        <Plus size={16}/> Add Event
                    </button>
                    <button className="primary" onClick={handleRunTest} disabled={loading} style={{height: 40}}>
                        {loading ? <div className="loader"/> : <><ShieldAlert size={16}/> Run Test</>}
                    </button>
                </div>

                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 12}}>
                    {events.map((ev, idx) => (
                        <div key={ev.id} style={{backgroundColor: 'rgba(0,0,0,0.3)', padding: 12, borderRadius: 8, border: '1px solid #444', position: 'relative'}}>
                            <button onClick={() => handleRemoveEvent(ev.id)} style={{position: 'absolute', top: 8, right: 8, background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer'}}>
                                <Trash2 size={16}/>
                            </button>
                            <h4 style={{margin: '0 0 10px 0', fontSize: 13, color: '#60a5fa'}}>Event {idx + 1}</h4>
                            <div style={{display: 'flex', gap: 8, marginBottom: 8}}>
                                <div style={{flex: 1}}>
                                    <label style={{fontSize: 11, color: '#aaa', display: 'block'}}>Start Time (s)</label>
                                    <input type="number" value={ev.start} onChange={e => updateEvent(ev.id, 'start', e.target.value)} style={{width: '100%', padding: '4px', fontSize: 12}}/>
                                </div>
                                <div style={{flex: 1}}>
                                    <label style={{fontSize: 11, color: '#aaa', display: 'block'}}>End Time (s)</label>
                                    <input type="number" value={ev.end} onChange={e => updateEvent(ev.id, 'end', e.target.value)} style={{width: '100%', padding: '4px', fontSize: 12}}/>
                                </div>
                            </div>
                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8}}>
                                <div>
                                    <label style={{fontSize: 11, color: '#aaa', display: 'block'}}>Wind Pitch (Nm)</label>
                                    <input type="number" step="0.01" value={ev.config.wind_torque_p} onChange={e => updateEventConfig(ev.id, 'wind_torque_p', e.target.value)} style={{width: '100%', padding: '4px', fontSize: 12}}/>
                                </div>
                                <div>
                                    <label style={{fontSize: 11, color: '#aaa', display: 'block'}}>Wind Yaw (Nm)</label>
                                    <input type="number" step="0.01" value={ev.config.wind_torque_y} onChange={e => updateEventConfig(ev.id, 'wind_torque_y', e.target.value)} style={{width: '100%', padding: '4px', fontSize: 12}}/>
                                </div>
                                <div>
                                    <label style={{fontSize: 11, color: '#aaa', display: 'block'}}>Payload Mass</label>
                                    <input type="number" step="0.01" value={ev.config.mass_payload} onChange={e => updateEventConfig(ev.id, 'mass_payload', e.target.value)} style={{width: '100%', padding: '4px', fontSize: 12}}/>
                                </div>
                                <div>
                                    <label style={{fontSize: 11, color: '#aaa', display: 'block'}}>Sensor Noise</label>
                                    <input type="number" step="0.01" value={ev.config.sensor_noise_std} onChange={e => updateEventConfig(ev.id, 'sensor_noise_std', e.target.value)} style={{width: '100%', padding: '4px', fontSize: 12}}/>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {simData && (
                <div style={{display: 'flex', gap: 8, padding: '0 16px', zIndex: 10, flexWrap: 'wrap'}}>
                   <button className={visiblePlots.Manual ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, Manual: !visiblePlots.Manual})} style={{padding: '4px 12px', fontSize: 12}}>Manual</button>
                   <button className={visiblePlots.GA ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GA: !visiblePlots.GA})} style={{padding: '4px 12px', fontSize: 12}}>GA</button>
                   <button className={visiblePlots.PSO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, PSO: !visiblePlots.PSO})} style={{padding: '4px 12px', fontSize: 12}}>PSO</button>
                   <button className={visiblePlots.TPE ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, TPE: !visiblePlots.TPE})} style={{padding: '4px 12px', fontSize: 12}}>TPE</button>
                   <button className={visiblePlots['CMA-ES'] ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, 'CMA-ES': !visiblePlots['CMA-ES']})} style={{padding: '4px 12px', fontSize: 12}}>CMA-ES</button>
                   <button className={visiblePlots.GWO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GWO: !visiblePlots.GWO})} style={{padding: '4px 12px', fontSize: 12}}>GWO</button>
                   <button className={visiblePlots['MIMO LQR'] ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, 'MIMO LQR': !visiblePlots['MIMO LQR']})} style={{padding: '4px 12px', fontSize: 12}}>MIMO LQR</button>
                </div>
            )}

            {simData && (
                <div className="glass-panel" style={{padding: 16, display: 'flex', flexDirection: 'column', gap: 16}}>
                    <ReactECharts option={getChartOption(0, 'Pitch Angle Tracking under Disturbances', 'Theta (deg)')} notMerge={true} style={{height: 350, width: '100%'}} />
                    <ReactECharts option={getChartOption(1, 'Yaw Angle Tracking under Disturbances', 'Psi (deg)')} notMerge={true} style={{height: 350, width: '100%'}} />
                </div>
            )}
        </div>
    );
}
