import React from 'react';
import { NavLink, Outlet, useMatch } from 'react-router-dom';
import { Activity, Monitor, BookOpen, History } from 'lucide-react';

export default function Layout() {
    // NavLink className helper: returns 'nav-btn active' when route matches, 'nav-btn' otherwise
    const navClass = ({ isActive }) => `nav-btn${isActive ? ' active' : ''}`;

    // Detect if any /experiments/* route is active for the top-level tab highlight
    const isOnExperiments = useMatch('/experiments/*');

    return (
        <div className="app-container" style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
            {/* ── Top Navigation ─────────────────────────────────────────────── */}
            <div className="top-nav" style={{
                display: 'flex', alignItems: 'center', padding: '12px 24px',
                background: 'rgba(20, 25, 40, 0.8)', backdropFilter: 'blur(16px)',
                borderBottom: '1px solid rgba(255,255,255,0.1)', zIndex: 100,
                flexShrink: 0
            }}>
                <h2 style={{ color: '#a78bfa', margin: '0 32px 0 0', fontSize: 20, textTransform: 'uppercase', letterSpacing: 2 }}>
                    Viettel Auto-Tuner
                </h2>

                <div style={{ display: 'flex', gap: 16, flex: 1 }}>
                    {/* "Experiments" highlights when URL matches /experiments/* */}
                    <NavLink
                        to="/experiments/ideal"
                        className={`nav-btn${isOnExperiments ? ' active' : ''}`}
                        id="nav-experiments"
                    >
                        <Activity size={18} /> Experiments
                    </NavLink>

                    <NavLink to="/simulation" className={navClass} id="nav-simulation">
                        <Monitor size={18} /> 3D Simulation
                    </NavLink>

                    <NavLink to="/wiki" className={navClass} id="nav-wiki">
                        <BookOpen size={18} /> Theory Wiki
                    </NavLink>

                    <NavLink to="/history" className={navClass} id="nav-history">
                        <History size={18} /> History
                    </NavLink>
                </div>
            </div>

            {/* ── Page Content (rendered by the matched route) ────────────────── */}
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                <div className="main-content" style={{ display: 'flex', flexDirection: 'column', flex: 1, padding: 20, overflow: 'hidden' }}>
                    <Outlet />
                </div>
            </div>
        </div>
    );
}
