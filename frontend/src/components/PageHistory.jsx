import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { RefreshCw, Trash2, Download } from 'lucide-react';

const API_BASE = 'http://localhost:8088/api'; 

export default function PageHistory() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE}/history`);
            if (res.data && res.data.history) {
                setHistory(res.data.history); // Already sorted desc by backend mostly
            }
        } catch (e) {
            console.error("Failed to fetch history", e);
        }
        setLoading(false);
    };

    const clearHistory = async () => {
        if (!window.confirm("Are you sure you want to clear all history? This will delete all experiment logs.")) return;
        try {
            await axios.delete(`${API_BASE}/history`);
            setHistory([]);
        } catch (e) {
            console.error("Failed to clear history", e);
        }
    };

    const exportCSV = () => {
        if (history.length === 0) return;
        
        // Comprehensive headers
        const headers = [
            "Experiment Name", "Timestamp", "Objective Structure", "Condition", "Algorithm", 
            "Wind Pitch (Nm)", "Wind Yaw (Nm)", "Sensor Noise Std", "Payload Mass Ratio",
            "Kp_p", "Ki_p", "Kd_p", "Kp_y", "Ki_y", "Kd_y",
            "Kp_p_large", "Ki_p_large", "Kd_p_large", "Kp_y_large", "Ki_y_large", "Kd_y_large",
            "Pitch Rise Time", "Pitch Settling Time", "Pitch Overshoot", "Pitch SSE", "Pitch ITAE", "Pitch Energy",
            "Yaw Rise Time", "Yaw Settling Time", "Yaw Overshoot", "Yaw SSE", "Yaw ITAE", "Yaw Energy",
            "Cost History"
        ];
        
        const rows = [];
        
        history.forEach(exp => {
            const expName = exp.experiment_name || "Unknown Experiment";
            const expTime = exp.timestamp ? new Date(exp.timestamp).toLocaleString() : "Unknown Time";
            const expObjType = exp.objective_type || "default_objective";
            
            if (exp.runs && Array.isArray(exp.runs)) {
                exp.runs.forEach(run => {
                    const p = run.params || [];
                    const pL = run.params_large || [];
                    const dist = run.disturbances || {};
                    const mP = run.metrics?.pitch || {};
                    const mY = run.metrics?.yaw || {};
                    const costHist = (run.cost_history && run.cost_history.length > 0) ? `"${run.cost_history.join('|')}"` : "";
                    
                    rows.push([
                        `"${expName}"`, `"${expTime}"`, `"${expObjType}"`, `"${run.condition || ''}"`, `"${run.algorithm || ''}"`,
                        dist.wind_torque_p ?? '', dist.wind_torque_y ?? '', dist.sensor_noise_std ?? '', dist.mass_payload ?? '',
                        p[0]??'', p[1]??'', p[2]??'', p[3]??'', p[4]??'', p[5]??'',
                        pL[0]??'', pL[1]??'', pL[2]??'', pL[3]??'', pL[4]??'', pL[5]??'',
                        mP.rise_time??'', mP.settling_time??'', mP.overshoot??'', mP.steady_state_error??'', mP.itae??'', mP.control_energy??'',
                        mY.rise_time??'', mY.settling_time??'', mY.overshoot??'', mY.steady_state_error??'', mY.itae??'', mY.control_energy??'',
                        costHist
                    ].join(','));
                });
            } else {
                // Backward compatibility for old single runs (just in case they weren't deleted)
                const p = exp.params || [];
                const mP = exp.metrics?.pitch || {};
                const mY = exp.metrics?.yaw || {};
                rows.push([
                    `"Legacy Single Run"`, `"${expTime}"`, `"N/A"`, `"${exp.type || ''}"`, `"${exp.algorithm || ''}"`,
                    '', '', '', '',
                    p[0]??'', p[1]??'', p[2]??'', p[3]??'', p[4]??'', p[5]??'',
                    '', '', '', '', '', '',
                    mP.rise_time??'', mP.settling_time??'', mP.overshoot??'', mP.steady_state_error??'', mP.itae??'', mP.control_energy??'',
                    mY.rise_time??'', mY.settling_time??'', mY.overshoot??'', mY.steady_state_error??'', mY.itae??'', mY.control_energy??'',
                    ""
                ].join(','));
            }
        });

        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows].join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "experiment_history.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    return (
        <div style={{ padding: 20, color: '#eee', height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h2>Experiment History</h2>
                <div style={{ display: 'flex', gap: 10 }}>
                    <button className="secondary-btn" onClick={fetchHistory} disabled={loading}>
                        <RefreshCw size={14} style={{ marginRight: 5, verticalAlign: 'middle' }} /> Refresh
                    </button>
                    <button className="primary-btn" onClick={exportCSV} disabled={history.length === 0} style={{backgroundColor: '#10b981', borderColor: '#10b981', color: 'white'}}>
                        <Download size={14} style={{ marginRight: 5, verticalAlign: 'middle' }} /> Export Unified CSV
                    </button>
                    <button className="secondary-btn" onClick={clearHistory} style={{ color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                        <Trash2 size={14} style={{ marginRight: 5, verticalAlign: 'middle' }} /> Clear
                    </button>
                </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', background: 'rgba(0,0,0,0.3)', borderRadius: 8, border: '1px solid #333' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                    <thead style={{ position: 'sticky', top: 0, background: '#1e1e1e', zIndex: 1 }}>
                        <tr style={{ borderBottom: '1px solid #444', textAlign: 'left' }}>
                            <th style={{ padding: 10 }}>Time</th>
                            <th style={{ padding: 10 }}>Experiment</th>
                            <th style={{ padding: 10 }}>Configurations Tested</th>
                            <th style={{ padding: 10 }}>Best Pitch ITAE</th>
                            <th style={{ padding: 10 }}>Best Yaw ITAE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.length === 0 ? (
                            <tr><td colSpan={5} style={{ padding: 20, textAlign: 'center', color: '#888' }}>No history found. Run some experiments!</td></tr>
                        ) : history.map((h, i) => {
                            const expTime = h.timestamp ? new Date(h.timestamp).toLocaleString() : "Unknown Time";
                            
                            // Find best metrics in runs
                            let bestPitch = Infinity;
                            let bestYaw = Infinity;
                            let runsCount = 0;
                            
                            if (h.runs) {
                                runsCount = h.runs.length;
                                h.runs.forEach(r => {
                                    if (r.metrics?.pitch?.itae < bestPitch) bestPitch = r.metrics.pitch.itae;
                                    if (r.metrics?.yaw?.itae < bestYaw) bestYaw = r.metrics.yaw.itae;
                                });
                            }
                            
                            return (
                                <tr key={i} style={{ borderBottom: '1px solid #333' }}>
                                    <td style={{ padding: 10 }}>{expTime}</td>
                                    <td style={{ padding: 10, fontWeight: 'bold', color: '#60a5fa' }}>{h.experiment_name || 'Legacy Run'}</td>
                                    <td style={{ padding: 10 }}>{runsCount} Runs</td>
                                    <td style={{ padding: 10 }}>{bestPitch !== Infinity ? bestPitch.toFixed(4) : '-'}</td>
                                    <td style={{ padding: 10 }}>{bestYaw !== Infinity ? bestYaw.toFixed(4) : '-'}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
