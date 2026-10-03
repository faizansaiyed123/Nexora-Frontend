import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Shell from "./components/Shell";
import { ForgotPassword, Login, Register, ResetPassword, VerifyEmail } from "./pages/AuthPages";
import Dashboard from "./pages/Dashboard";
import Competitors from "./pages/Competitors";
import Discovery from "./pages/Discovery";
import Jobs from "./pages/Jobs";
import Alerts from "./pages/Alerts";
import Matches from "./pages/Matches";
import Offerings from "./pages/Offerings";
import Settings from "./pages/Settings";
import Sources from "./pages/Sources";
import Welcome from "./pages/Welcome";
import { Spinner } from "./components/ui";
import type { ReactNode } from "react";

function Protected({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner label="Restoring your secure workspace…" />;
  return user ? <Shell>{children}</Shell> : <Navigate to="/welcome" replace />;
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <Spinner label="Preparing Nexora…" />;
  return user ? <Navigate to="/" replace /> : <>{children}</>;
}

function HomeRoute() {
  const { user, loading } = useAuth();
  if (loading) return <Spinner label="Preparing Nexora…" />;
  return user ? <Shell><Dashboard /></Shell> : <Welcome />;
}

function WorkspaceRoutes() {
  return (
    <Routes>
      <Route path="/offerings" element={<Offerings />} />
      <Route path="/competitors" element={<Competitors />} />
      <Route path="/sources" element={<Sources />} />
      <Route path="/matches" element={<Matches />} />
      <Route path="/discovery" element={<Discovery />} />
      <Route path="/jobs" element={<Jobs />} />
      <Route path="/alerts" element={<Alerts />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRoute />} />
      <Route path="/welcome" element={<PublicOnly><Welcome /></PublicOnly>} />
      <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
      <Route path="/register" element={<PublicOnly><Register /></PublicOnly>} />
      <Route path="/forgot-password" element={<PublicOnly><ForgotPassword /></PublicOnly>} />
      <Route path="/reset-password" element={<PublicOnly><ResetPassword /></PublicOnly>} />
      <Route path="/verify-email" element={<PublicOnly><VerifyEmail /></PublicOnly>} />
      <Route path="/*" element={<Protected><WorkspaceRoutes /></Protected>} />
    </Routes>
  );
}
