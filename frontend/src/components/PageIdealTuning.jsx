import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import axios from 'axios';
import ReactECharts from 'echarts-for-react';
import { Target, Play, Activity, Info } from 'lucide-react';
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
            { type: 'scroll', data: legendPitch, textStyle: { color: '#ffffff', fontWeight: 'bold' }, top: '5%', left: 'center', width: '80%' },
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

    const chartKey = dataSeries.map(ds => ds.name).join('_') || 'empty';
    return <ReactECharts key={chartKey} option={option} notMerge={true} style={{ height, width: '100%' }} opts={{ renderer: 'canvas' }} />;
}

function ErrorChart({ title, dataSeries, timeAxis, spPitchData, spYawData, height = 300 }) {
    if (!spPitchData || !spYawData || timeAxis.length === 0) return null;
    
    const series = [];
    const legendPitch = [];
    const legendYaw = [];

    dataSeries.forEach(ds => {
        if (!ds.data) return;
        const errP = ds.data.pitch.map((p, i) => (parseFloat(spPitchData[i]) - (p * 180 / Math.PI)).toFixed(2));
        const errY = ds.data.yaw.map((y, i) => (parseFloat(spYawData[i]) - (y * 180 / Math.PI)).toFixed(2));
        
        series.push({ name: `${ds.name} Err P`, type: 'line', xAxisIndex: 0, yAxisIndex: 0, data: errP, smooth: true, itemStyle: { color: ds.colorP } });
        series.push({ name: `${ds.name} Err Y`, type: 'line', xAxisIndex: 1, yAxisIndex: 1, data: errY, smooth: true, itemStyle: { color: ds.colorY } });
        legendPitch.push(`${ds.name} Err P`);
        legendYaw.push(`${ds.name} Err Y`);
    });

    const option = {
        title: { text: title, textStyle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' }, top: 0, left: 10 },
        tooltip: { trigger: 'axis' },
        legend: [
            { type: 'scroll', data: legendPitch, textStyle: { color: '#ffffff', fontWeight: 'bold' }, top: '5%', left: 'center', width: '80%' },
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
            { gridIndex: 0, type: 'value', name: 'Error Pitch (deg)', splitLine: { lineStyle: { color: '#444' } }, axisLabel: {color: '#ffffff', fontWeight: 'bold'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} },
            { gridIndex: 1, type: 'value', name: 'Error Yaw (deg)', splitLine: { lineStyle: { color: '#444' } }, axisLabel: {color: '#ffffff', fontWeight: 'bold'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} }
        ],
        series: series,
        backgroundColor: 'transparent'
    };

    const chartKey = dataSeries.map(ds => ds.name).join('_') || 'empty';
    return <ReactECharts key={chartKey} option={option} notMerge={true} style={{ height, width: '100%' }} opts={{ renderer: 'canvas' }} />;
}

function ConvergenceChart({ compareResult, height = 300 }) {
    if (!compareResult) return null;

    let maxIters = 0;
    const series = [];

    const colors = {
        'GA': '#3b82f6',
        'PSO': '#10b981',
        'TPE': '#ec4899',
        'CMA-ES': '#8b5cf6',
        'GWO': '#f59e0b'
    };

    let sliced = false;
    ['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO'].forEach(alg => {
        if (compareResult[alg] && compareResult[alg].best_overall && compareResult[alg].best_overall.cost_history) {
            const raw_hist = compareResult[alg].best_overall.cost_history;
            sliced = raw_hist.length > 3;
            const hist = sliced ? raw_hist.slice(3) : raw_hist; 
            if (hist.length > maxIters) maxIters = hist.length;
            
            series.push({
                name: alg,
                type: 'line',
                data: hist,
                smooth: true,
                itemStyle: { color: colors[alg] },
                symbol: 'none'
            });
        }
    });

    if (maxIters === 0) return null;

    const xAxisData = Array.from({length: maxIters}, (_, i) => sliced ? i + 4 : i + 1);

    const option = {
        title: { text: 'Convergence Chart (Cost vs Iterations)', textStyle: { color: '#ffffff', fontSize: 14, fontWeight: 'bold' }, top: 0, left: 10 },
        tooltip: { trigger: 'axis' },
        legend: { type: 'scroll', data: series.map(s => s.name), textStyle: { color: '#ffffff', fontWeight: 'bold' }, top: '5%', left: 'center', width: '80%' },
        grid: { top: '20%', bottom: '15%', left: '10%', right: '5%' },
        xAxis: { type: 'category', data: xAxisData, name: 'Iteration', nameLocation: 'middle', nameGap: 25, axisLabel: {color: '#ffffff'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} },
        yAxis: { type: 'value', name: 'Cost', splitLine: { lineStyle: { color: '#444' } }, axisLabel: {color: '#ffffff'}, nameTextStyle: {color: '#ffffff', fontWeight: 'bold'} },
        series: series,
        backgroundColor: 'transparent'
    };

    return <ReactECharts option={option} notMerge={true} style={{ height, width: '100%' }} opts={{ renderer: 'canvas' }} />;
}

function IterationChartBlock({ alg, compareResult, colorsP, colorsY, timeAxis, spPitchData, spYawData }) {
    const [visibleIters, setVisibleIters] = React.useState({});

    const iterations = compareResult?.[alg]?.iterations_data;

    React.useEffect(() => {
        if (iterations && Object.keys(visibleIters).length === 0) {
            const initial = {};
            // Make all visible by default
            iterations.forEach(item => initial[item.iters] = true);
            setVisibleIters(initial);
        }
    }, [iterations]);

    if (!iterations) return null;

    const seriesData = [];
    iterations.forEach((item, idx) => {
        if (visibleIters[item.iters]) {
            seriesData.push({
                name: `${alg}-${item.iters}`,
                data: item.simData,
                colorP: colorsP[idx % colorsP.length],
                colorY: colorsY[idx % colorsY.length]
            });
        }
    });

    return (
        <div className="glass-panel" style={{padding: 16, display: 'flex', gap: 16, flexDirection: 'column'}}>
            <div style={{display:'flex', gap: 8, zIndex: 10, flexWrap: 'wrap'}}>
               {iterations.map(item => (
                   <button key={item.iters} 
                       className={visibleIters[item.iters] ? 'primary-btn' : 'secondary-btn'} 
                       onClick={() => {
                           const newVisible = {...visibleIters, [item.iters]: !visibleIters[item.iters]};
                           setVisibleIters(newVisible);
                       }} 
                       style={{padding: '4px 12px', fontSize: 12}}>
                       {alg}-{item.iters}
                   </button>
               ))}
               <button className="secondary-btn" onClick={() => {
                   const allOn = {};
                   iterations.forEach(item => allOn[item.iters] = true);
                   setVisibleIters(allOn);
               }} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>
            </div>
            <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
                <TimeResponseChart title={`${alg} Time Response`} dataSeries={seriesData} timeAxis={timeAxis} spPitchData={spPitchData} spYawData={spYawData} height={350} />
                <ErrorChart title={`${alg} Error Tracking`} dataSeries={seriesData} timeAxis={timeAxis} spPitchData={spPitchData} spYawData={spYawData} height={300} />
                <ConvergenceChart compareResult={{ [alg]: compareResult?.[alg] }} height={300} />
                <ConsolidatedMetricsTable seriesData={seriesData} />
            </div>
        </div>
    );
}

export default function PageIdealTuning() {
    const navigate = useNavigate();
    const {
        manualParams, setManualParams,
        spPitch, setSpPitch,
        spYaw, setSpYaw,
        simDuration, setSimDuration,
        trajectoryType, setTrajectoryType,
        tunedParams, setTunedParams, setTunedParamsLarge,
        wikiDoc, setWikiDoc,
    } = useAppContext();

    // onUpdateTunedParams: update both tunedParams and tunedParamsLarge in context
    const onUpdateTunedParams = (newTuned) => {
        setTunedParams(newTuned);
        setTunedParamsLarge(newTuned);
    };
    const [itersInput, setItersInput] = useState({ GA: "10, 20", PSO: "10, 20", TPE: "10, 20", "CMA-ES": "10, 20", GWO: "10, 20" });
    const [disturbances, setDisturbances] = useState({ wind_torque_p: 0.0, wind_torque_y: 0.0, sensor_noise_std: 0.0, mass_payload: 0.0 });
    const [tuningProfile, setTuningProfile] = useState("balanced");
    const [objectiveTypes, setObjectiveTypes] = useState([]);
    const [selectedObjectiveType, setSelectedObjectiveType] = useState('default_objective');

    React.useEffect(() => {
        axios.get(`${API_BASE}/objective_functions`).then(res => {
            if (res.data && res.data.objectives) {
                setObjectiveTypes(res.data.objectives);
            }
        }).catch(err => console.error("Failed to fetch objective functions:", err));
    }, []);

    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [abortController, setAbortController] = useState(null);

    React.useEffect(() => {
        return () => {
            if (window.currentProgressInterval) {
                clearInterval(window.currentProgressInterval);
                window.currentProgressInterval = null;
            }
        };
    }, []);

    const [visiblePlots, setVisiblePlots] = useState({ Manual: true, GA: true, PSO: false, TPE: false, "CMA-ES": false, GWO: false, Target: true });
    const [showTooltip, setShowTooltip] = useState(false);
    
    // Results
    const [manualSim, setManualSim] = useState(null);
    const [mimoLqrSim, setMimoLqrSim] = useState(null);
    const [compareResult, setCompareResult] = useState(null);

    const handleRun = async () => {
        setLoading(true);
        setProgress(0);
        
        const controller = new AbortController();
        setAbortController(controller);
        if (window.currentProgressInterval) clearInterval(window.currentProgressInterval);
        window.currentProgressInterval = null;

        try {
            // 0. Fetch MIMO LQR params
            let mimoLqrParamsRes = { data: { baseline_params: [] } };
            try {
                mimoLqrParamsRes = await axios.get(`${API_BASE}/mimo_lqr_baseline`);
            } catch (e) { console.error("Failed to fetch MIMO LQR params", e); }

            // 1. Simulate Manual and MIMO LQR concurrently
            const simPromises = [
                axios.post(`${API_BASE}/simulate`, {
                    params: manualParams,
                    setpoint_pitch: spPitch * Math.PI / 180,
                    setpoint_yaw: spYaw * Math.PI / 180,
                    t_max: simDuration, 
                    disturbance_config: disturbances, 
                    trajectory_type: trajectoryType,
                    tuning_profile: tuningProfile,
                    objective_type: selectedObjectiveType
                })
            ];

            if (mimoLqrParamsRes.data && mimoLqrParamsRes.data.baseline_params.length > 0) {
                simPromises.push(
                    axios.post(`${API_BASE}/simulate`, {
                        params: mimoLqrParamsRes.data.baseline_params,
                        setpoint_pitch: spPitch * Math.PI / 180,
                        setpoint_yaw: spYaw * Math.PI / 180,
                        t_max: simDuration, 
                        disturbance_config: disturbances, 
                        trajectory_type: trajectoryType,
                        controller_type: 'mimo_lqr',
                        tuning_profile: tuningProfile,
                        objective_type: selectedObjectiveType
                    })
                );
            }

            const simResults = await Promise.all(simPromises);
            setManualSim(simResults[0].data);
            if (simResults.length > 1) {
                setMimoLqrSim(simResults[1].data);
            }

            // 2. Parse Iters and Run Compare
            const iters_dict = {};
            ['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO'].forEach(alg => {
                iters_dict[alg] = itersInput[alg].split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x) && x > 0);
            });

            const taskId = Date.now().toString();
            const progressInterval = setInterval(async () => {
                try {
                    const progRes = await axios.get(`${API_BASE}/progress?task_id=${taskId}`);
                    setProgress(progRes.data.progress || 0);
                } catch (e) {}
            }, 500);

            const compRes = await axios.post(`${API_BASE}/compare_algorithms`, {
                task_id: taskId,
                setpoint_pitch: spPitch * Math.PI / 180,
                setpoint_yaw: spYaw * Math.PI / 180,
                iters_dict: iters_dict, 
                t_max: simDuration, 
                trajectory_type: trajectoryType, 
                disturbance_config: disturbances,
                tuning_profile: tuningProfile,
                objective_type: selectedObjectiveType
            }, { signal: controller.signal });
            
            clearInterval(progressInterval);
            setProgress(100);

            // 3. Simulate all returned iterations to get full time response
            const fullResults = compRes.data;
            for (const alg of ['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO']) {
                if (fullResults[alg]) {
                    // Simulate Best
                    if (fullResults[alg].best_overall) {
                        const sRes = await axios.post(`${API_BASE}/simulate`, {
                            params: fullResults[alg].best_overall.best_params, setpoint_pitch: spPitch * Math.PI / 180, setpoint_yaw: spYaw * Math.PI / 180,
                            t_max: simDuration, disturbance_config: disturbances, trajectory_type: trajectoryType, tuning_profile: tuningProfile, objective_type: selectedObjectiveType
                        });
                        fullResults[alg].best_overall.simData = sRes.data;
                    }
                    // Simulate Each Iteration
                    for (let item of fullResults[alg].iterations_data) {
                        const sRes = await axios.post(`${API_BASE}/simulate`, {
                            params: item.best_params, setpoint_pitch: spPitch * Math.PI / 180, setpoint_yaw: spYaw * Math.PI / 180,
                            t_max: simDuration, disturbance_config: disturbances, trajectory_type: trajectoryType, tuning_profile: tuningProfile, objective_type: selectedObjectiveType
                        });
                        item.simData = sRes.data;
                    }
                }
            }
            setCompareResult(fullResults);

            // Log Experiment
            try {
                const exp = {
                    experiment_name: "Ideal Tuning Analysis",
                    objective_type: selectedObjectiveType,
                    runs: []
                };
                
                if (manualRes.data) {
                    exp.runs.push({
                        condition: "Manual Config",
                        algorithm: "Manual",
                        params: manualParams,
                        disturbances: disturbances,
                        metrics: manualRes.data.metrics || {}
                    });
                }
                
                for (const alg of ['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO']) {
                    if (fullResults[alg] && fullResults[alg].best_overall) {
                        exp.runs.push({
                            condition: `Best ${alg}`,
                            algorithm: alg,
                            params: fullResults[alg].best_overall.best_params,
                            disturbances: disturbances,
                            metrics: fullResults[alg].best_overall.simData?.metrics || {},
                            cost_history: fullResults[alg].best_overall.cost_history || []
                        });
                        for (let item of fullResults[alg].iterations_data) {
                            exp.runs.push({
                                condition: `${alg} (Iters=${item.iters})`,
                                algorithm: alg,
                                params: item.best_params,
                                disturbances: disturbances,
                                metrics: item.simData?.metrics || {},
                                cost_history: item.cost_history || []
                            });
                        }
                    }
                }
                
                await axios.post(`${API_BASE}/history`, exp);
            } catch (err) {
                console.error("Failed to log history:", err);
            }

            if (onUpdateTunedParams) {
                const newTuned = {};
                if (fullResults.GA?.best_overall) newTuned.GA = fullResults.GA.best_overall.best_params;
                if (fullResults.PSO?.best_overall) newTuned.PSO = fullResults.PSO.best_overall.best_params;
                if (fullResults.TPE?.best_overall) newTuned.TPE = fullResults.TPE.best_overall.best_params;
                if (fullResults["CMA-ES"]?.best_overall) newTuned["CMA-ES"] = fullResults["CMA-ES"].best_overall.best_params;
                if (fullResults.GWO?.best_overall) newTuned.GWO = fullResults.GWO.best_overall.best_params;
                onUpdateTunedParams(newTuned);
            }

        } catch (error) {
            console.error("Error during run:", error);
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

    // Prepare time axis and reference data
    const refData = manualSim || (compareResult && compareResult.GA?.best_overall?.simData);
    const timeAxis = refData ? refData.time.map(t => t.toFixed(2)) : [];
    const spPitchData = refData ? refData.sp_pitch.map(p => (p * 180 / Math.PI).toFixed(2)) : [];
    const spYawData = refData ? refData.sp_yaw.map(p => (p * 180 / Math.PI).toFixed(2)) : [];

    // Main Chart Series
    const mainSeries = [];
    if (visiblePlots.Manual && manualSim) mainSeries.push({ name: 'Manual', data: manualSim, colorP: '#ef4444', colorY: '#f59e0b' });
    if (visiblePlots.MIMOLQR && mimoLqrSim) mainSeries.push({ name: 'MIMO LQR', data: mimoLqrSim, colorP: '#eab308', colorY: '#ca8a04' });
    if (visiblePlots.GA && compareResult?.GA?.best_overall?.simData) mainSeries.push({ name: 'Best GA', data: compareResult.GA.best_overall.simData, colorP: '#3b82f6', colorY: '#93c5fd' });
    if (visiblePlots.PSO && compareResult?.PSO?.best_overall?.simData) mainSeries.push({ name: 'Best PSO', data: compareResult.PSO.best_overall.simData, colorP: '#10b981', colorY: '#6ee7b7' });
    if (visiblePlots.TPE && compareResult?.TPE?.best_overall?.simData) mainSeries.push({ name: 'Best TPE', data: compareResult.TPE.best_overall.simData, colorP: '#ec4899', colorY: '#fbcfe8' });
    if (visiblePlots["CMA-ES"] && compareResult?.["CMA-ES"]?.best_overall?.simData) mainSeries.push({ name: 'Best CMA-ES', data: compareResult["CMA-ES"].best_overall.simData, colorP: '#8b5cf6', colorY: '#c4b5fd' });
    if (visiblePlots.GWO && compareResult?.GWO?.best_overall?.simData) mainSeries.push({ name: 'Best GWO', data: compareResult.GWO.best_overall.simData, colorP: '#f59e0b', colorY: '#fcd34d' });

    const colorsP = ['#ef4444', '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6', '#ec4899'];
    const colorsY = ['#f87171', '#fbbf24', '#34d399', '#22d3ee', '#a78bfa', '#f472b6'];

    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: 16, height: '100%', overflowY: 'auto', paddingRight: 10}}>
            <GlobalConfigPanel />

            <div className="glass-panel" style={{padding: 16, display: 'flex', alignItems: 'center', gap: 16}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap'}}>
                    <div style={{flex: 1, minWidth: 200}}>
                        <h3 style={{marginTop: 0, color: '#3b82f6'}}>Controller Tuning Analysis</h3>
                        <p style={{fontSize: 13, color: '#aaa', margin: 0}}>Compare Manual PID baseline against Auto-Tuned controllers.</p>
                    </div>
                    <div style={{display: 'flex', gap: 12}}>
                        {['GA', 'PSO', 'TPE', 'CMA-ES', 'GWO'].map(alg => (
                            <div key={alg} style={{display: 'flex', flexDirection: 'column'}}>
                                <label style={{fontSize: 12, color: '#aaa'}}>{alg} Iters</label>
                                <input type="text" value={itersInput[alg]} onChange={e => setItersInput({...itersInput, [alg]: e.target.value})} style={{width: 70, background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: 'white', padding: 4, borderRadius: 4}} />
                            </div>
                        ))}
                        <div style={{display: 'flex', flexDirection: 'column', marginLeft: 10}}>
                            <label style={{fontSize: 12, color: '#aaa', display: 'flex', alignItems: 'center', gap: 4, zIndex: 999}}>
                                <Target size={12}/> Tuning Profile (Weights)
                                <div style={{position: 'relative', display: 'inline-block'}} 
                                     onMouseEnter={() => setShowTooltip(true)} 
                                     onMouseLeave={() => setShowTooltip(false)}>
                                    <button 
                                        onClick={() => {
                                            setWikiDoc('objective_func');
                                            navigate('/wiki');
                                            
                                            let attempts = 0;
                                            const interval = setInterval(() => {
                                                const el = document.getElementById('tuning-profiles-section');
                                                if (el) {
                                                    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                                                    clearInterval(interval);
                                                }
                                                attempts++;
                                                if (attempts > 20) clearInterval(interval);
                                            }, 100);
                                        }} 
                                        style={{
                                            background: '#3b82f6', color: 'white', border: 'none', 
                                            borderRadius: '50%', width: 16, height: 16, fontSize: 11,
                                            fontWeight: 'bold', cursor: 'pointer', display: 'flex', 
                                            alignItems: 'center', justifyContent: 'center', marginLeft: 4
                                        }}
                                    >
                                        !
                                    </button>
                                    {showTooltip && (
                                        <div style={{
                                            position: 'absolute', bottom: '120%', left: -100, zIndex: 99999, 
                                            background: 'rgba(30, 41, 59, 0.98)', color: '#e2e8f0', padding: '12px', 
                                            borderRadius: 8, width: 320, fontSize: 12,
                                            boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)',
                                            border: '1px solid #475569',
                                            pointerEvents: 'none',
                                            lineHeight: 1.5
                                        }}>
                                            <strong style={{color: '#60a5fa'}}>Ý Nghĩa 4 Tuning Profiles:</strong><br/>
                                            <ul style={{margin: '8px 0', paddingLeft: 20}}>
                                                <li><strong style={{color: '#34d399'}}>1. Balanced:</strong> Cân bằng tốt giữa độ chính xác và hao pin.</li>
                                                <li><strong style={{color: '#f87171'}}>2. Aggressive:</strong> Bám mục tiêu gắt nhất, bất chấp tốn điện và giật.</li>
                                                <li><strong style={{color: '#fbb6ce'}}>3. Eco & Smooth:</strong> Ưu tiên mượt mà, tiết kiệm điện, chấp nhận bám chậm.</li>
                                                <li><strong style={{color: '#fbbf24'}}>4. Strict Safety:</strong> Tránh tuyệt đối cháy nổ do quá dòng (quá 24V).</li>
                                            </ul>
                                            <em style={{color: '#94a3b8'}}>Nhấn icon ! để xem chi tiết trong Theory Wiki.</em>
                                        </div>
                                    )}
                                </div>
                            </label>
                            <select value={tuningProfile} onChange={e => setTuningProfile(e.target.value)} style={{width: 160, background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: '#60a5fa', padding: 4, borderRadius: 4, height: 26, fontWeight: 'bold'}}>
                                <option value="balanced">1. Balanced</option>
                                <option value="aggressive">2. Aggressive Tracking</option>
                                <option value="eco">3. Eco & Smooth</option>
                                <option value="safety">4. Strict Safety</option>
                            </select>
                        </div>
                        <div style={{display: 'flex', flexDirection: 'column', marginLeft: 10}}>
                            <label style={{fontSize: 12, color: '#aaa', display: 'flex', alignItems: 'center', gap: 4}}>
                                <Activity size={12}/> Objective Function Structure
                            </label>
                            <select value={selectedObjectiveType} onChange={e => setSelectedObjectiveType(e.target.value)} style={{width: 220, background: 'rgba(0,0,0,0.2)', border: '1px solid #444', color: '#34d399', padding: 4, borderRadius: 4, height: 26, fontWeight: 'bold'}}>
                                {objectiveTypes.length > 0 ? (
                                    objectiveTypes.map(obj => (
                                        <option key={obj.id} value={obj.id} title={obj.description}>{obj.name}</option>
                                    ))
                                ) : (
                                    <option value="default_objective">Default Multi-Objective (J1+J2+J3)</option>
                                )}
                            </select>
                        </div>
                    </div>
                    <div style={{gridColumn: '1 / -1', display: 'flex', gap: 10, marginTop: 10}}>
                        <button className="primary-btn" onClick={handleRun} disabled={loading} style={{ flex: 1 }}>
                            {loading ? `Running Optimization... ${Math.round(progress)}%` : 'Run Analysis'}
                            <Play size={16} style={{ marginLeft: 5, verticalAlign: 'middle' }} />
                        </button>
                        {loading && (
                            <button className="secondary-btn" onClick={handleStop} style={{ backgroundColor: '#dc2626', color: 'white', borderColor: '#dc2626' }}>
                                Stop
                            </button>
                        )}
                    </div>
                    {loading && (
                        <div style={{ gridColumn: '1 / -1', marginTop: 10, background: '#333', borderRadius: 4, height: 6, overflow: 'hidden' }}>
                            <div style={{ height: '100%', background: '#a78bfa', width: `${progress}%`, transition: 'width 0.3s ease' }}></div>
                        </div>
                    )}
                </div>
                <div style={{display: 'flex', gap: 16, padding: '10px 0', borderTop: '1px solid #333'}}>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Wind Pitch (Nm)</label>
                        <input type="number" step="0.01" value={disturbances.wind_torque_p} onChange={e => setDisturbances({...disturbances, wind_torque_p: parseFloat(e.target.value)})} style={{padding: 4}} />
                    </div>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Wind Yaw (Nm)</label>
                        <input type="number" step="0.01" value={disturbances.wind_torque_y} onChange={e => setDisturbances({...disturbances, wind_torque_y: parseFloat(e.target.value)})} style={{padding: 4}} />
                    </div>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Sensor Noise StdDev</label>
                        <input type="number" step="0.01" value={disturbances.sensor_noise_std} onChange={e => setDisturbances({...disturbances, sensor_noise_std: parseFloat(e.target.value)})} style={{padding: 4}} />
                    </div>
                    <div className="form-group" style={{marginBottom: 0}}>
                        <label style={{fontSize: 11}}>Payload Ratio</label>
                        <input type="number" step="0.1" value={disturbances.mass_payload} onChange={e => setDisturbances({...disturbances, mass_payload: parseFloat(e.target.value)})} style={{padding: 4}} />
                    </div>
                </div>
            </div>

            {/* Block 1: Main Comparison */}
            <div className="glass-panel" style={{padding: 16, display: 'flex', gap: 16, flexDirection: 'column'}}>
                <div style={{display:'flex', gap: 8, zIndex: 10}}>
                   <button className={visiblePlots.Manual ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, Manual: !visiblePlots.Manual})} style={{padding: '4px 12px', fontSize: 12}}>Manual</button>
                   <button className={visiblePlots.MIMOLQR ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, MIMOLQR: !visiblePlots.MIMOLQR})} style={{padding: '4px 12px', fontSize: 12}}>MIMO LQR</button>
                   <button className={visiblePlots.GA ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GA: !visiblePlots.GA})} style={{padding: '4px 12px', fontSize: 12}}>GA</button>
                   <button className={visiblePlots.PSO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, PSO: !visiblePlots.PSO})} style={{padding: '4px 12px', fontSize: 12}}>PSO</button>
                   <button className={visiblePlots.TPE ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, TPE: !visiblePlots.TPE})} style={{padding: '4px 12px', fontSize: 12}}>TPE</button>
                   <button className={visiblePlots["CMA-ES"] ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, "CMA-ES": !visiblePlots["CMA-ES"]})} style={{padding: '4px 12px', fontSize: 12}}>CMA-ES</button>
                   <button className={visiblePlots.GWO ? 'primary-btn' : 'secondary-btn'} onClick={() => setVisiblePlots({...visiblePlots, GWO: !visiblePlots.GWO})} style={{padding: '4px 12px', fontSize: 12}}>GWO</button>
                   <button className="secondary-btn" onClick={() => setVisiblePlots({Manual:true, GA:true, PSO:true, TPE:true, "CMA-ES":true, GWO:true, Target:true})} style={{padding: '4px 12px', fontSize: 12, marginLeft: 'auto'}}>Show All</button>
                </div>
                <div style={{display: 'flex', flexDirection: 'column', gap: 16}}>
                    <TimeResponseChart title="Comparison of Best Models" dataSeries={mainSeries} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} height={400} />
                    <ErrorChart title="Error Dynamics (Best Models)" dataSeries={mainSeries} timeAxis={timeAxis} spPitchData={spPitchData} spYawData={spYawData} height={300} />
                    <ConvergenceChart compareResult={compareResult} height={300} />
                    <ConsolidatedMetricsTable seriesData={mainSeries} />
                </div>
            </div>

            {/* Block 2: GA Iterations */}
            <IterationChartBlock alg="GA" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />

            {/* Block 3: SOTA Iterations */}
            <IterationChartBlock alg="PSO" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
            <IterationChartBlock alg="TPE" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
            <IterationChartBlock alg="CMA-ES" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
            <IterationChartBlock alg="GWO" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />

            {/* Block 4: BO Iterations */}
            <IterationChartBlock alg="BO" compareResult={compareResult} colorsP={colorsP} colorsY={colorsY} timeAxis={timeAxis} spPitchData={visiblePlots.Target ? spPitchData : null} spYawData={visiblePlots.Target ? spYawData : null} />
        </div>
    );
}
