import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

/**
 * ExperimentsLayout — nested layout for /experiments/*
 * Renders the secondary sub-tab bar + an Outlet for the active experiment page.
 */
export default function ExperimentsLayout() {
    const subNavClass = ({ isActive }) => `secondary-btn${isActive ? ' active-sub' : ''}`;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
            {/* ── Sub-tab bar ────────────────────────────────────────────────── */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexShrink: 0 }}>
                <NavLink to="/experiments/ideal"          className={subNavClass} id="subtab-ideal">
                    1. Ideal Tuning
                </NavLink>
                <NavLink to="/experiments/robustness"     className={subNavClass} id="subtab-robustness">
                    2. Robustness Sweep
                </NavLink>
                <NavLink to="/experiments/gainscheduling" className={subNavClass} id="subtab-gainscheduling">
                    3. Gain Scheduling
                </NavLink>
                <NavLink to="/experiments/lqr"            className={subNavClass} id="subtab-lqr">
                    4. LQR vs PID
                </NavLink>
            </div>

            {/* ── Active experiment page ─────────────────────────────────────── */}
            <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <Outlet />
            </div>
        </div>
    );
}
