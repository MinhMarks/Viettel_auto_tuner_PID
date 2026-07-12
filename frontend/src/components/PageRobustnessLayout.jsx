import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

/**
 * Nested layout for /experiments/robustness
 * Renders the top toggle bar (Sweep vs Rejection) + an Outlet.
 */
export default function PageRobustnessLayout() {
    const subNavClass = ({ isActive }) => `secondary-btn${isActive ? ' active-sub' : ''}`;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
            {/* ── Toggle bar ────────────────────────────────────────────────── */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 15, flexShrink: 0, justifyContent: 'center' }}>
                <NavLink to="sweep" className={subNavClass} style={{padding: '6px 16px', borderRadius: 4}}>
                    <i className="fas fa-th-list" style={{marginRight: 8}}></i> Static Sweep Test
                </NavLink>
                <NavLink to="rejection" className={subNavClass} style={{padding: '6px 16px', borderRadius: 4}}>
                    <i className="fas fa-wave-square" style={{marginRight: 8}}></i> Dynamic Disturbance Rejection
                </NavLink>
            </div>

            {/* ── Active sub-page ─────────────────────────────────────── */}
            <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <Outlet />
            </div>
        </div>
    );
}
