import { FormEvent, useState, type ReactNode } from "react";
import { ArrowRight, CheckCircle2, KeyRound, Mail, Shield, Sparkles, LockKeyhole } from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { auth } from "../api";
import { useAuth } from "../auth";
import { Button, Card, Input, Notice } from "../components/ui";

function AuthLayout({ children, eyebrow, title, detail, mode = "default" }: {
  children: ReactNode; eyebrow: string; title: string; detail: string; mode?: "default" | "success";
}) {
  return <div className={"auth-screen auth-" + mode}>
    <div className="auth-panel">
      <div className="auth-brand-row">
        <Link to="/welcome" className="brand-link"><div className="brand-mark">N</div><div className="brand-copy"><strong>Nexora</strong><span>MARKET INTELLIGENCE</span></div></Link>
        <span className="auth-secure"><LockKeyhole size={13} /> Secure workspace</span>
      </div>
      <div className="auth-content">
        <div className="auth-copy"><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{detail}</p></div>
        {children}
      </div>
      <div className="auth-footer"><span>© {new Date().getFullYear()} Nexora</span><span>Built for focused market decisions</span></div>
    </div>

    <div className="auth-visual">
      <div className="auth-noise" /><div className="visual-grid" />
      <div className="visual-copy"><span className="visual-kicker"><span className="live-pulse" /> Intelligence in motion</span><h2>Turn market signals into calm, confident action.</h2><p>Catalog coverage, competitor pricing, source health, discovery, jobs and alerts—unified in one private workspace.</p></div>
      <div className="signal-stack">
        <div className="signal-window signal-window-main">
          <div className="signal-window-top"><span>MARKET PULSE</span><b>LIVE</b></div>
          <div className="signal-chart"><span className="chart-grid-line line-1" /><span className="chart-grid-line line-2" /><svg viewBox="0 0 320 100" preserveAspectRatio="none" aria-hidden="true"><path d="M0 78 C25 72, 38 80, 62 63 S105 67, 124 52 S155 60, 176 38 S211 50, 230 28 S266 44, 284 20 S305 29, 320 10" /></svg></div>
          <div className="signal-metrics"><div><span>Tracked</span><strong>Catalog</strong></div><div><span>Signals</span><strong>Realtime</strong></div><div><span>Boundary</span><strong>Private</strong></div></div>
        </div>
        <div className="signal-window signal-window-float signal-window-one"><Sparkles size={15} /><strong>Discovery ready</strong><span>Map a public storefront into your catalog.</span></div>
        <div className="signal-window signal-window-float signal-window-two"><Shield size={15} /><strong>Workspace protected</strong><span>Tenant-level access boundaries stay intact.</span></div>
      </div>
    </div>
  </div>;
}

export function Login() {
  const { signIn } = useAuth(); const nav = useNavigate();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  return <AuthLayout eyebrow="Secure workspace" title="See what changed before it becomes obvious." detail="Sign in to your private Nexora workspace and get a focused view of pricing, sources, jobs and alerts.">
    <Card className="auth-card">
      <div className="auth-card-kicker"><span className="auth-kicker-dot" /> Workspace access</div>
      <form onSubmit={async event => { event.preventDefault(); setError(""); setBusy(true); try { await signIn(email, password); nav("/"); } catch (err) { setError(err instanceof Error ? err.message : "Unable to sign in"); } finally { setBusy(false); } }}>
        <Input label="Work email" value={email} onChange={event => setEmail(event.target.value)} type="email" required autoComplete="email" placeholder="you@company.com" />
        <Input label="Password" value={password} onChange={event => setPassword(event.target.value)} type="password" required autoComplete="current-password" placeholder="Enter your password" />
        {error ? <Notice type="error">{error}</Notice> : null}
        <Button type="submit" disabled={busy} loading={busy} className="full">{busy ? "Signing in…" : "Sign in"} <ArrowRight size={16} /></Button>
      </form>
      <div className="auth-links"><Link to="/forgot-password">Forgot password?</Link><span>New to Nexora? <Link to="/register">Create an account</Link></span></div>
    </Card>
  </AuthLayout>;
}

export function Register() {
  const [org, setOrg] = useState(""); const [name, setName] = useState(""); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [resendError, setResendError] = useState(""); const [done, setDone] = useState(false); const [verifyRequired, setVerifyRequired] = useState(true); const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => { event.preventDefault(); setError(""); setBusy(true); try { const result = await auth.register(org, name, email, password); setVerifyRequired(result.email_verification_required !== false); setDone(true); } catch (err) { setError(err instanceof Error ? err.message : "Unable to create account"); } finally { setBusy(false); } };
  if (done && !verifyRequired) return <AuthLayout mode="success" eyebrow="Workspace created" title="Your workspace is ready." detail="Sign in with the credentials you just created to enter your workspace.">
    <Card className="auth-card success-card"><div className="success-icon"><CheckCircle2 size={28} /></div><span className="eyebrow">ALL SET</span><h3>Workspace created</h3><p><strong>{org}</strong> is ready. Email verification is disabled in this environment, so you can sign in now.</p>
      <div className="success-actions"><Button className="full" onClick={() => window.location.assign("/login")}>Continue to sign in <ArrowRight size={16} /></Button></div>
    </Card>
  </AuthLayout>;
  if (done) return <AuthLayout mode="success" eyebrow="Step 2 of 2 · Verify" title="Your workspace is almost ready." detail="Open the verification email, activate your account, then sign in to enter your workspace.">
    <Card className="auth-card success-card"><div className="success-icon"><CheckCircle2 size={28} /></div><span className="eyebrow">CHECK YOUR INBOX</span><h3>Verification required</h3><p>We sent a secure verification link to <strong>{email}</strong>.</p>
      <div className="success-actions"><Button variant="secondary" className="full" onClick={async () => { setResendError(""); try { await auth.resendVerification(email); } catch (err) { setResendError(err instanceof Error ? err.message : "Could not resend the verification email."); } }}>Resend email</Button><Button className="full" onClick={() => window.location.assign("/login")}>Continue to sign in <ArrowRight size={16} /></Button></div>
      {resendError ? <Notice type="error">{resendError}</Notice> : null}
    </Card>
  </AuthLayout>;
  return <AuthLayout eyebrow="Step 1 of 2 · Create workspace" title="Start with a private intelligence workspace." detail="Your organization becomes the tenant boundary for catalog, competitors, collection jobs and alerts.">
    <Card className="auth-card"><form onSubmit={submit}>
      <div className="auth-step-row"><span className="step active">1</span><span className="step-line" /><span className="step">2</span><span className="step-label">Verify your email next</span></div>
      <Input label="Organization name" value={org} onChange={event => setOrg(event.target.value)} required placeholder="Acme Retail" autoComplete="organization" />
      <Input label="Your full name" value={name} onChange={event => setName(event.target.value)} required placeholder="Jane Smith" autoComplete="name" />
      <Input label="Work email" value={email} onChange={event => setEmail(event.target.value)} required type="email" placeholder="jane@acme.com" autoComplete="email" />
      <Input label="Password" value={password} onChange={event => setPassword(event.target.value)} required type="password" minLength={8} placeholder="Use at least 8 characters" autoComplete="new-password" hint="Use a unique password for this workspace." />
      {error ? <Notice type="error">{error}</Notice> : null}
      <Button type="submit" disabled={busy} loading={busy} className="full">{busy ? "Creating workspace…" : "Create workspace"} <ArrowRight size={16} /></Button>
    </form><div className="auth-links"><span>Already have an account? <Link to="/login">Sign in</Link></span></div></Card>
  </AuthLayout>;
}

export function ForgotPassword() {
  const [email, setEmail] = useState(""); const [sent, setSent] = useState(false); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  return <AuthLayout eyebrow="Account recovery" title="Reset access without losing your workspace." detail="We’ll send a one-time reset link when an account matches the address.">
    <Card className="auth-card">{sent ? <div className="recovery-success"><div className="success-icon"><Mail size={24} /></div><h3>Check your inbox</h3><p>If the account exists, a password reset email has been sent.</p></div> :
      <form onSubmit={async event => { event.preventDefault(); setBusy(true); setError(""); try { await auth.forgot(email); setSent(true); } catch (err) { setError(err instanceof Error ? err.message : "Request failed"); } finally { setBusy(false); } }}>
        <Input label="Work email" value={email} onChange={event => setEmail(event.target.value)} type="email" required autoComplete="email" placeholder="you@company.com" />
        {error ? <Notice type="error">{error}</Notice> : null}<Button type="submit" disabled={busy} loading={busy} className="full">{busy ? "Sending…" : "Send reset link"} <ArrowRight size={16} /></Button>
      </form>}<div className="auth-links"><Link to="/login">Back to sign in</Link></div></Card>
  </AuthLayout>;
}

export function ResetPassword() {
  const [params] = useSearchParams(); const token = params.get("token") || "";
  const [password, setPassword] = useState(""); const [done, setDone] = useState(false); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  return <AuthLayout eyebrow="New password" title="Choose a fresh password." detail="Reset links expire quickly and can only be used once.">
    <Card className="auth-card">{done ? <div className="recovery-success"><div className="success-icon"><CheckCircle2 size={24} /></div><h3>Password updated</h3><p>Your password has been reset successfully. You can now sign in.</p><Link className="btn btn-primary full" to="/login">Continue to sign in <ArrowRight size={16} /></Link></div> :
      <form onSubmit={async event => { event.preventDefault(); setError(""); setBusy(true); try { await auth.reset(token, password); setDone(true); } catch (err) { setError(err instanceof Error ? err.message : "Reset failed"); } finally { setBusy(false); } }}>
        <Input label="New password" value={password} onChange={event => setPassword(event.target.value)} type="password" minLength={8} required autoComplete="new-password" placeholder="Use at least 8 characters" />
        {error ? <Notice type="error">{error}</Notice> : null}<Button type="submit" disabled={busy} loading={busy} className="full"><KeyRound size={16} />{busy ? "Updating…" : "Update password"}</Button>
      </form>}<div className="auth-links"><Link to="/login">Back to sign in</Link></div></Card>
  </AuthLayout>;
}

export function VerifyEmail() {
  const [params] = useSearchParams(); const token = params.get("token") || "";
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle"); const [message, setMessage] = useState("");
  const run = async () => { setStatus("loading"); try { const result = await auth.verify(token); setMessage(result.message); setStatus("success"); } catch (err) { setMessage(err instanceof Error ? err.message : "Verification failed"); setStatus("error"); } };
  return <AuthLayout eyebrow="Identity verification" title="Verify your Nexora identity." detail="Activate the account created for your organization and continue into your workspace.">
    <Card className="auth-card"><div className="verify-icon"><Shield size={24} /></div>
      {status === "idle" ? <><h3>One secure step</h3><p className="muted">Use the verification link that was sent to your work email.</p><Button onClick={run} className="full"><Shield size={16} /> Verify email</Button></> : null}
      {status === "loading" ? <Notice>Verifying your email…</Notice> : null}
      {status === "success" ? <><Notice type="success">{message}</Notice><Link className="btn btn-primary full" to="/login">Continue to sign in</Link></> : null}
      {status === "error" ? <Notice type="error">{message}</Notice> : null}
      <div className="auth-links"><Link to="/login">Back to sign in</Link></div>
    </Card>
  </AuthLayout>;
}
