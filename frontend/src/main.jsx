import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import './index.css'

import { AppProvider } from './context/AppContext'
import Layout from './components/Layout'
import ExperimentsLayout from './components/ExperimentsLayout'
import PageIdealTuning from './components/PageIdealTuning'
import PageRobustness from './components/PageRobustness'
import PageGainScheduling from './components/PageGainScheduling'
import PageLQRComparison from './components/PageLQRComparison'
import Page3DSimulation from './components/Page3DSimulation'
import PageDocumentation from './components/PageDocumentation'
import PageHistory from './components/PageHistory'

// ── Router definition ────────────────────────────────────────────────────────
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      // Default: redirect / → /experiments/ideal
      { index: true, element: <Navigate to="/experiments/ideal" replace /> },

      // Experiments with nested sub-tab layout
      {
        path: 'experiments',
        element: <ExperimentsLayout />,
        children: [
          { index: true, element: <Navigate to="/experiments/ideal" replace /> },
          { path: 'ideal',          element: <PageIdealTuning /> },
          { path: 'robustness',     element: <PageRobustness /> },
          { path: 'gainscheduling', element: <PageGainScheduling /> },
          { path: 'lqr',            element: <PageLQRComparison /> },
        ],
      },

      // Top-level routes
      { path: 'simulation', element: <Page3DSimulation /> },
      { path: 'wiki',       element: <PageDocumentation /> },
      { path: 'history',    element: <PageHistory /> },
    ],
  },
]);

// ── Error Boundary ────────────────────────────────────────────────────────────
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, color: 'white', backgroundColor: 'red', minHeight: '100vh' }}>
          <h2>React Runtime Error:</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 14 }}>
            {this.state.error && this.state.error.toString()}
          </pre>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── Mount ─────────────────────────────────────────────────────────────────────
createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <AppProvider>
        <RouterProvider router={router} />
      </AppProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)
