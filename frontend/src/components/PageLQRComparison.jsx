import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8088/api';

// ─────────────────────────────────────────────────────────────
//  INLINE SVG LINE CHART
// ─────────────────────────────────────────────────────────────
function LineChart({ data, title, yLabel, height = 240 }) {
  if (!data || !data.time || data.time.length === 0) return null;

  const W = 560, H = height;
  const PAD = { top: 32, right: 20, bottom: 44, left: 58 };
  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;

  const allYVals = [
    ...(data.lqr_pitch || []), ...(data.pid_pitch || []),
    ...(data.lqr_yaw || []),   ...(data.pid_yaw || []),
    ...(data.sp_pitch || []),  ...(data.sp_yaw || [])
  ].filter(v => v !== undefined && !isNaN(v));

  if (allYVals.length === 0) return null;

  const minY = Math.min(...allYVals);
  const maxY = Math.max(...allYVals);
  const padY  = (maxY - minY) * 0.08 || 0.01;
  const lo = minY - padY, hi = maxY + padY;
  const rangeY = hi - lo;
  const minX = data.time[0];
  const maxX = data.time[data.time.length - 1];
  const rangeX = maxX - minX || 1;

  const px = t => PAD.left + ((t - minX) / rangeX) * plotW;
  const py = v => PAD.top  + (1 - (v - lo)  / rangeY) * plotH;

  const toPath = (arr, timeArr) => {
    if (!arr || arr.length === 0) return '';
    return arr.map((v, i) => `${i === 0 ? 'M' : 'L'}${px(timeArr[i]).toFixed(1)},${py(v).toFixed(1)}`).join(' ');
  };

  const yTicks = 5;
  const yTickVals = Array.from({ length: yTicks + 1 }, (_, i) => lo + (rangeY * i) / yTicks);
  const xTicks = 6;
  const xTickVals = Array.from({ length: xTicks + 1 }, (_, i) => minX + (rangeX * i) / xTicks);

  return (
    <div style={{ width: '100%' }}>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`}
        style={{ background: '#ffffff', borderRadius: 4, display: 'block' }}>
        {/* Horizontal Gridlines (Light Grey) */}
        {yTickVals.map((v, i) => (
          <g key={`hgrid-${i}`}>
            <line x1={PAD.left} y1={py(v)} x2={W - PAD.right} y2={py(v)}
              stroke="#e5e7eb" strokeWidth="1" strokeDasharray="4,4" />
          </g>
        ))}

        {/* Setpoints */}
        {data.sp_pitch && (
          <path d={toPath(data.sp_pitch, data.time)} fill="none" stroke="#000000"
            strokeWidth="2.0" strokeDasharray="5,5" />
        )}
        {data.sp_yaw && (
          <path d={toPath(data.sp_yaw, data.time)} fill="none" stroke="#000000"
            strokeWidth="2.0" strokeDasharray="5,5" />
        )}

        {/* LQR (Blue) */}
        {data.lqr_pitch && (
          <path d={toPath(data.lqr_pitch, data.time)} fill="none" stroke="#1f77b4" strokeWidth="2.5" />
        )}
        {data.lqr_yaw && (
          <path d={toPath(data.lqr_yaw, data.time)} fill="none" stroke="#1f77b4"
            strokeWidth="2.5" strokeDasharray="2,3" />
        )}

        {/* PID (Red) */}
        {data.pid_pitch && (
          <path d={toPath(data.pid_pitch, data.time)} fill="none" stroke="#d62728"
            strokeWidth="2.5" strokeDasharray="6,2,2,2" />
        )}
        {data.pid_yaw && (
          <path d={toPath(data.pid_yaw, data.time)} fill="none" stroke="#d62728"
            strokeWidth="2.5" strokeDasharray="8,4" />
        )}

        {/* X and Y Axes (Bottom & Left Spines) */}
        <path d={`M ${PAD.left} ${PAD.top} L ${PAD.left} ${PAD.top + plotH} L ${W - PAD.right} ${PAD.top + plotH}`} 
          fill="none" stroke="#000000" strokeWidth="1.2" />

        {/* Y-Axis Ticks & Labels */}
        {yTickVals.map((v, i) => (
          <g key={`yax-${i}`}>
            <line x1={PAD.left - 4} y1={py(v)} x2={PAD.left} y2={py(v)} stroke="#000000" strokeWidth="1.2" />
            <text x={PAD.left - 6} y={py(v) + 3} fill="#000000" fontSize="10" fontFamily="serif" textAnchor="end">
              {v.toFixed(3)}
            </text>
          </g>
        ))}

        {/* X-Axis Ticks & Labels */}
        {xTickVals.map((v, i) => (
          <g key={`xax-${i}`}>
            <line x1={px(v)} y1={PAD.top + plotH} x2={px(v)} y2={PAD.top + plotH + 4} stroke="#000000" strokeWidth="1.2" />
            <text x={px(v)} y={PAD.top + plotH + 16} fill="#000000" fontSize="10" fontFamily="serif" textAnchor="middle">
              {v.toFixed(1)}
            </text>
          </g>
        ))}

        {/* Axis Titles */}
        <text transform={`translate(16,${H / 2}) rotate(-90)`} fill="#000000" fontSize="11" fontFamily="serif" textAnchor="middle" fontWeight="bold">
          {yLabel}
        </text>
        <text x={W / 2} y={H - 6} fill="#000000" fontSize="11" fontFamily="serif" textAnchor="middle" fontWeight="bold">
          Time (s)
        </text>
      </svg>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  METRIC CARD  (improved layout)
// ─────────────────────────────────────────────────────────────
function MetricCard({ label, lqrVal, pidVal, unit = 'rad', higherBetter = false }) {
  const lqrBetter = typeof lqrVal === 'number' && typeof pidVal === 'number'
    ? (higherBetter ? lqrVal > pidVal : lqrVal < pidVal)
    : null;
    
  let improvement = '—';
  if (pidVal > 0 && typeof lqrVal === 'number') {
    if (lqrBetter) {
      improvement = ((pidVal - lqrVal) / pidVal * 100).toFixed(1);
    } else {
      improvement = ((lqrVal - pidVal) / lqrVal * 100).toFixed(1);
    }
  }

  return (
    <div style={{
      background: 'rgba(20,24,40,0.9)', borderRadius: 12, padding: '16px 20px',
      border: '1px solid #374151', display: 'flex', flexDirection: 'column', gap: 12
    }}>
      <div style={{ color: '#9ca3af', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1 }}>
        {label}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr auto', gap: 16, alignItems: 'center' }}>
        
        {/* LQR */}
        <div>
          <div style={{ fontSize: 10, color: '#60a5fa', marginBottom: 4, fontWeight: 600 }}>LQR (MIMO)</div>
          <div style={{ fontSize: 20, fontWeight: 700, fontFamily: 'monospace',
            color: lqrBetter === true ? '#4ade80' : lqrBetter === false ? '#f87171' : '#60a5fa' }}>
            {typeof lqrVal === 'number' ? lqrVal.toFixed(5) : '—'}
            <span style={{ fontSize: 11, color: '#6b7280', marginLeft: 4 }}>{unit}</span>
          </div>
        </div>

        {/* VS */}
        <div style={{ color: '#4b5563', fontSize: 12, fontWeight: 700, fontStyle: 'italic' }}>vs</div>

        {/* PID */}
        <div>
          <div style={{ fontSize: 10, color: '#f87171', marginBottom: 4, fontWeight: 600 }}>Dec. PID (SISO)</div>
          <div style={{ fontSize: 20, fontWeight: 700, fontFamily: 'monospace',
            color: lqrBetter === false ? '#4ade80' : lqrBetter === true ? '#f87171' : '#f87171' }}>
            {typeof pidVal === 'number' ? pidVal.toFixed(5) : '—'}
            <span style={{ fontSize: 11, color: '#6b7280', marginLeft: 4 }}>{unit}</span>
          </div>
        </div>

        {/* Delta */}
        <div style={{
          background: lqrBetter === true ? 'rgba(74,222,128,0.1)' : 'rgba(248,113,113,0.1)',
          border: `1px solid ${lqrBetter === true ? '#4ade80' : '#f87171'}`,
          borderRadius: 8, padding: '8px 12px', textAlign: 'center', minWidth: 80
        }}>
          <div style={{ fontSize: 9, color: '#9ca3af', marginBottom: 2 }}>
            {lqrBetter === true ? 'LQR Tốt hơn' : lqrBetter === false ? 'PID Tốt hơn' : 'Độ lệch'}
          </div>
          <div style={{ fontSize: 15, fontWeight: 700,
            color: lqrBetter === true ? '#4ade80' : '#f87171' }}>
            +{improvement}%
          </div>
        </div>
        
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  CHART LEGEND
// ─────────────────────────────────────────────────────────────
function Legend() {
  const items = [
    { color: '#1f77b4', dash: 'none',    label: 'LQR – Pitch' },
    { color: '#1f77b4', dash: '2,3',     label: 'LQR – Yaw' },
    { color: '#d62728', dash: '6,2,2,2', label: 'PID – Pitch' },
    { color: '#d62728', dash: '8,4',     label: 'PID – Yaw' },
    { color: '#000000', dash: '5,5',     label: 'Setpoint' },
  ];
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px 24px', marginBottom: 14, background: '#ffffff', padding: '12px 16px', borderRadius: 8, border: '1px solid #e5e7eb' }}>
      {items.map(({ color, dash, label }) => (
        <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <svg width="30" height="12">
            <line x1="0" y1="6" x2="30" y2="6" stroke={color} strokeWidth="2.2"
              strokeDasharray={dash} />
          </svg>
          <span style={{ color: '#000000', fontSize: 12, fontFamily: 'serif', fontWeight: 500 }}>{label}</span>
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  SCENARIO PANEL
// ─────────────────────────────────────────────────────────────
function ScenarioPanel({ scKey, scData, label }) {
  if (!scData) return null;
  const m = scData.metrics || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Scenario badge */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(167,139,250,0.12), rgba(96,165,250,0.08))',
        border: '1px solid rgba(167,139,250,0.25)', borderRadius: 10,
        padding: '12px 18px', display: 'flex', alignItems: 'center', gap: 12
      }}>
        <span style={{ fontSize: 22 }}>{scKey === 'scenario1' ? '🎯' : '〰️'}</span>
        <div>
          <div style={{ color: '#a78bfa', fontWeight: 700, fontSize: 14 }}>{label}</div>
          <div style={{ color: '#6b7280', fontSize: 11, marginTop: 2 }}>
            {scKey === 'scenario1'
              ? 'Pitch nhận lệnh step. Yaw = 0.0 rad. Đo nhiễu chéo bị lan sang Yaw.'
              : 'Pitch theo quỹ đạo Sine liên tục. Yaw = 0.0 rad. Đo gợn sóng nhiễu chéo.'}
          </div>
        </div>
      </div>

      <Legend />

      {/* Charts side-by-side */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, maxWidth: 1100, margin: '0 auto', width: '100%' }}>
        <LineChart 
          data={{ ...scData, lqr_yaw: undefined, pid_yaw: undefined, sp_yaw: undefined }} 
          title="📐 Trục Pitch" yLabel="Góc (rad)" height={360} 
        />
        <LineChart
          data={{ ...scData, lqr_pitch: undefined, pid_pitch: undefined, sp_pitch: undefined }}
          title="⚡ Trục Yaw — Nhiễu Chéo (Setpoint = 0)"
          yLabel="Góc (rad)" height={360}
        />
      </div>

      {/* Metric cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <MetricCard label="Yaw RMSE (Cross-Error)"     lqrVal={m.lqr_yaw_rmse}              pidVal={m.pid_yaw_rmse}              unit="rad" />
        <MetricCard label="Yaw Max Cross-Error"         lqrVal={m.lqr_yaw_max_cross_error}   pidVal={m.pid_yaw_max_cross_error}   unit="rad" />
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  SMALL CONFIG INPUT
// ─────────────────────────────────────────────────────────────
function ConfigInput({ label, value, onChange, step, min, max }) {
  return (
    <div>
      <label style={{ color: '#9ca3af', fontSize: 11, marginBottom: 4, display: 'block' }}>{label}</label>
      <input
        type="number" step={step} min={min} max={max} value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          background: 'rgba(0,0,0,0.35)', border: '1px solid #374151', color: 'white',
          padding: '6px 10px', borderRadius: 6, width: '100%', fontSize: 13,
          fontFamily: 'inherit'
        }}
      />
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
//  MAIN PAGE
// ─────────────────────────────────────────────────────────────
export default function PageLQRComparison() {
  const [loading, setLoading]           = useState(false);
  const [results, setResults]           = useState(null);
  const [error, setError]               = useState('');
  const [activeScenario, setActiveScenario] = useState('scenario1');

  // Config
  const [tMax, setTMax]                 = useState(10.0);
  const [spPitchStep, setSpPitchStep]   = useState(0.5);
  const [sineAmplitude, setSineAmplitude] = useState(0.4);
  const [sineFreq, setSineFreq]         = useState(0.25);
  const [windP, setWindP]               = useState(0.01);
  const [windY, setWindY]               = useState(0.01);
  const [sensorNoise, setSensorNoise]   = useState(0.005);
  const [massPayload, setMassPayload]   = useState(0.01);

  const handleRun = async () => {
    setLoading(true);
    setError('');
    setResults(null);
    try {
      const resp = await axios.post(`${API_BASE}/compare_lqr_pid`, {
        t_max: tMax,
        sp_pitch_step: spPitchStep,
        sp_yaw_fixed: 0.0,
        sine_amplitude: sineAmplitude,
        sine_freq: sineFreq,
        disturbance_config: {
          wind_torque_p: windP, wind_torque_y: windY,
          sensor_noise_std: sensorNoise, mass_payload: massPayload
        }
      });
      setResults(resp.data);
      setActiveScenario('scenario1');
    } catch (e) {
      setError(`Lỗi: ${e.response?.data?.detail || e.message}`);
    }
    setLoading(false);
  };

  return (
    // Outer wrapper: fills the route outlet, scrolls vertically
    <div style={{
      display: 'flex', flexDirection: 'column', flex: 1,
      height: '100%', overflowY: 'auto', overflowX: 'hidden',
      paddingRight: 10,           // space for scrollbar
      color: 'white', fontFamily: 'Inter, sans-serif',
    }}>
      {/* Inner content constrained to readable width */}
      <div style={{ maxWidth: 1380, margin: '0 auto', padding: '4px 0 32px 0', width: '100%' }}>

        {/* ── Page Header ─────────────────────────────────────────── */}
        <div style={{ marginBottom: 20 }}>
          <h2 style={{
            color: '#a78bfa', fontSize: 20, fontWeight: 700,
            margin: '0 0 4px 0', textTransform: 'uppercase', letterSpacing: 2
          }}>
            LQR vs Decentralized PID
          </h2>
          <p style={{ color: '#6b7280', fontSize: 12, margin: 0 }}>
            So sánh hiệu quả chống nhiễu chéo (cross-coupling robustness) giữa bộ điều khiển MIMO-LQR và SISO Decentralized PID
          </p>
        </div>

        {/* ── Config Panel ────────────────────────────────────────── */}
        <div style={{
          background: 'rgba(15,18,35,0.8)', border: '1px solid #1f2937',
          borderRadius: 12, padding: '18px 20px', marginBottom: 20
        }}>
          {/* Header row */}
          <div style={{
            color: '#e5e7eb', fontWeight: 700, fontSize: 13,
            borderBottom: '1px solid #1f2937', paddingBottom: 10, marginBottom: 14
          }}>
            ⚙️ Cấu hình Thực nghiệm
          </div>

          {/* Two-column config grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px 28px', marginBottom: 14 }}>
            {/* Left column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ color: '#6b7280', fontSize: 10, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 2 }}>
                Thông số chung
              </div>
              <ConfigInput label="Thời gian mô phỏng (s)"       value={tMax}         onChange={setTMax}         step="1"    min="5"   max="30" />
              <ConfigInput label="Kịch bản 1 – Pitch Step (rad)" value={spPitchStep}  onChange={setSpPitchStep}  step="0.1" />
              <ConfigInput label="Kịch bản 3 – Biên độ Sine (rad)" value={sineAmplitude} onChange={setSineAmplitude} step="0.05" />
              <ConfigInput label="Kịch bản 3 – Tần số Sine (Hz)"  value={sineFreq}    onChange={setSineFreq}     step="0.05" />
            </div>

            {/* Right column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ color: '#6b7280', fontSize: 10, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 2 }}>
                Nhiễu môi trường
              </div>
              <ConfigInput label="Wind Pitch (Nm)"  value={windP}       onChange={setWindP}       step="0.005" />
              <ConfigInput label="Wind Yaw (Nm)"    value={windY}       onChange={setWindY}       step="0.005" />
              <ConfigInput label="Sensor Noise σ"   value={sensorNoise} onChange={setSensorNoise} step="0.001" />
              <ConfigInput label="Payload Ratio"    value={massPayload} onChange={setMassPayload} step="0.01" />
            </div>
          </div>

          {/* Run button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <button
              onClick={handleRun}
              disabled={loading}
              style={{
                background: loading ? '#374151' : 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                border: 'none', borderRadius: 8, padding: '10px 28px',
                color: 'white', fontWeight: 700, fontSize: 14,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', gap: 8,
                transition: 'opacity 0.2s', opacity: loading ? 0.7 : 1,
                flexShrink: 0
              }}
            >
              {loading ? (
                <>
                  <span style={{
                    display: 'inline-block', width: 15, height: 15,
                    border: '2px solid #9ca3af', borderTopColor: 'white',
                    borderRadius: '50%', animation: 'lqr-spin 0.8s linear infinite'
                  }} />
                  Đang chạy mô phỏng...
                </>
              ) : '▶  Chạy So sánh LQR vs PID'}
            </button>

            {error && (
              <div style={{
                color: '#f87171', fontSize: 12,
                background: 'rgba(248,113,113,0.08)', padding: '8px 14px',
                borderRadius: 6, border: '1px solid rgba(248,113,113,0.2)', flex: 1
              }}>
                ⚠️ {error}
              </div>
            )}
          </div>
        </div>
        <style>{`@keyframes lqr-spin { to { transform: rotate(360deg); } }`}</style>

        {/* ── Results ─────────────────────────────────────────────── */}
        {results && (
          <div>
            {/* Scenario tab switcher */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
              {[
                { key: 'scenario1', label: '🎯 Kịch bản 1: Asymmetric Step' },
                { key: 'scenario3', label: '〰️ Kịch bản 3: Sine Tracking' },
              ].map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setActiveScenario(key)}
                  style={{
                    background: activeScenario === key
                      ? 'linear-gradient(135deg, #7c3aed, #4f46e5)'
                      : 'rgba(15,18,35,0.8)',
                    border: activeScenario === key ? '1px solid #7c3aed' : '1px solid #374151',
                    borderRadius: 8, padding: '8px 20px', color: 'white',
                    fontWeight: activeScenario === key ? 700 : 400,
                    cursor: 'pointer', fontSize: 13,
                    transition: 'all 0.18s ease'
                  }}
                >
                  {label}
                </button>
              ))}
            </div>

            {activeScenario === 'scenario1' && (
              <ScenarioPanel scKey="scenario1" scData={results.scenario1} label="Kịch bản 1: Asymmetric Step Test" />
            )}
            {activeScenario === 'scenario3' && (
              <ScenarioPanel scKey="scenario3" scData={results.scenario3} label="Kịch bản 3: Sine Trajectory Tracking" />
            )}
          </div>
        )}

      </div>
    </div>
  );
}
