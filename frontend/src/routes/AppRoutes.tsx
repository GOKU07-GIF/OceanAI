import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";

// Pages
import Dashboard from "../pages/dashboard/Dashboard";
import OceanData from "../pages/ocean-data/OceanData";
import Map from "../pages/map/Map";
import Analytics from "../pages/analytics/Analytics";
import Alerts from "../pages/alerts/Alerts";
import Reports from "../pages/reports/Reports";
import Settings from "../pages/Settings/Settings";

import Login from "../pages/auth/Login";
import LandingPage from "../pages/Landing/LandingPage";

// Protected Route
import ProtectedRoute from "../components/auth/ProtectedRoute";

export default function AppRoutes(): React.JSX.Element {
  return (
    <BrowserRouter>
      <Routes>

        {/* Landing Page */}
        <Route
          path="/"
          element={<LandingPage />}
        />

        {/* Login */}
        <Route
          path="/login"
          element={<Login />}
        />

        {/* Protected Dashboard Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >

          {/* Dashboard Home */}
          <Route
            index
            element={<Dashboard />}
          />

          {/* Ocean Data */}
          <Route
            path="ocean-data"
            element={<OceanData />}
          />

          {/* Ocean Map */}
          <Route
            path="map"
            element={<Map />}
          />

          {/* AI Analytics */}
          <Route
            path="analytics"
            element={<Analytics />}
          />

          {/* Alerts */}
          <Route
            path="alerts"
            element={<Alerts />}
          />

          {/* Reports */}
          <Route
            path="reports"
            element={<Reports />}
          />

          {/* Settings */}
          <Route
            path="settings"
            element={<Settings />}
          />

          {/* Unknown Dashboard Route */}
          <Route
            path="*"
            element={<Navigate to="/dashboard" replace />}
          />

        </Route>

        {/* Unknown Route */}
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />

      </Routes>
    </BrowserRouter>
  );
}