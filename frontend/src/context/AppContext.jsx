import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
    // ── PID Parameters ─────────────────────────────────────────────────────────
    const [manualParams, setManualParams] = useState([30.0, 15.0, 10.0, 40.0, 10.0, 15.0]);
    const [manualParamsLarge, setManualParamsLarge] = useState([50.0, 20.0, 15.0, 60.0, 15.0, 20.0]);
    const [tunedParams, setTunedParams] = useState({});
    const [tunedParamsLarge, setTunedParamsLarge] = useState({});

    // ── Setpoints & Simulation Config ──────────────────────────────────────────
    const [spPitch, setSpPitch] = useState(15.0);
    const [spYaw, setSpYaw] = useState(30.0);
    const [trajectoryType, setTrajectoryType] = useState('step');
    const [simDuration, setSimDuration] = useState(20.0);

    // ── Disturbances (per-page, independent) ───────────────────────────────────
    const [distRobustness, setDistRobustness] = useState({
        wind_torque_p: 0.01, wind_torque_y: 0.01,
        sensor_noise_std: 0.1, mass_payload: 1.0
    });
    const [distGainSched, setDistGainSched] = useState({
        wind_torque_p: 0.01, wind_torque_y: 0.01,
        sensor_noise_std: 0.1, mass_payload: 1.0
    });
    const [distSim, setDistSim] = useState({
        wind_torque_p: 0.01, wind_torque_y: 0.01,
        sensor_noise_std: 0.1, mass_payload: 1.0
    });

    // ── Wiki state ─────────────────────────────────────────────────────────────
    const [wikiDoc, setWikiDoc] = useState('intro');

    const value = {
        manualParams, setManualParams,
        manualParamsLarge, setManualParamsLarge,
        tunedParams, setTunedParams,
        tunedParamsLarge, setTunedParamsLarge,
        spPitch, setSpPitch,
        spYaw, setSpYaw,
        trajectoryType, setTrajectoryType,
        simDuration, setSimDuration,
        distRobustness, setDistRobustness,
        distGainSched, setDistGainSched,
        distSim, setDistSim,
        wikiDoc, setWikiDoc,
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
    const ctx = useContext(AppContext);
    if (!ctx) throw new Error('useAppContext must be used within AppProvider');
    return ctx;
}

export default AppContext;
