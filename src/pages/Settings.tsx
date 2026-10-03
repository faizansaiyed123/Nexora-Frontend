import { FormEvent, useEffect, useState } from "react";
import { Building2, KeyRound, Save, ShieldCheck } from "lucide-react";
import { auth } from "../api";
import { useAuth } from "../auth";
import { Button, Card, Input, Notice, SectionHeader, StatusPill, Toast, useToast } from "../components/ui";

export default function Settings() {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState<Record<string, any>>({});
  const [password, setPassword] = useState({ current_password: "", new_password: "" });
  const { toast, show } = useToast();
  useEffect(() => { auth.profile().then(setProfile).catch(error => show(error instanceof Error ? error.message : "Could not load profile", "error")); }, []);
  const saveProfile = async (event: FormEvent) => { event.preventDefault(); try { await auth.updateProfile(profile); await refreshUser(); show("Workspace profile updated."); } catch (error) { show(error instanceof Error ? error.message : "Profile update failed", "error"); } };
  const savePassword = async (event: FormEvent) => { event.preventDefault(); try { await auth.changePassword(password); setPassword({ current_password: "", new_password: "" }); show("Password updated. Other active sessions may need to re-authenticate."); } catch (error) { show(error instanceof Error ? error.message : "Password update failed", "error"); } };
  return <div className="stack">
    <SectionHeader eyebrow="ACCOUNT & TENANT" title="Settings" detail="Keep your workspace identity and account security current." />
    <div className="settings-layout">
      <Card className="settings-card"><div className="section-heading"><div className="section-icon icon-green"><Building2 size={18} /></div><div><span className="eyebrow">ORGANIZATION</span><h3>Workspace profile</h3><p>These details shape how your private workspace is identified.</p></div></div>
        <form onSubmit={saveProfile}>
          <Input label="Organization name" value={profile.name || ""} onChange={e => setProfile({ ...profile, name: e.target.value })} />
          <Input label="Company name" value={profile.company_name || ""} onChange={e => setProfile({ ...profile, company_name: e.target.value })} />
          <div className="split-fields"><Input label="Country" value={profile.country || ""} onChange={e => setProfile({ ...profile, country: e.target.value })} /><Input label="Default currency" value={profile.default_currency || ""} onChange={e => setProfile({ ...profile, default_currency: e.target.value.toUpperCase() })} /></div>
          <div className="split-fields"><Input label="Market" value={profile.default_market || ""} onChange={e => setProfile({ ...profile, default_market: e.target.value.toUpperCase() })} /><Input label="Industry" value={profile.industry || ""} onChange={e => setProfile({ ...profile, industry: e.target.value })} /></div>
          <Input label="Timezone" value={profile.timezone || ""} onChange={e => setProfile({ ...profile, timezone: e.target.value })} />
          {(user?.role === "ORG_ADMIN" || user?.role === "SUPER_ADMIN") ? <div className="form-end"><Button type="submit"><Save size={16} /> Save profile</Button></div> : null}
        </form>
      </Card>
      <div className="stack">
        <Card className="security-summary"><div className="security-mark"><ShieldCheck size={21} /></div><div><span className="eyebrow">ACCOUNT</span><h3>{user?.full_name}</h3><p>{user?.email}</p><StatusPill value={user?.role || "USER"} /></div></Card>
        <Card className="settings-card"><div className="section-heading"><div className="section-icon icon-purple"><KeyRound size={18} /></div><div><span className="eyebrow">SECURITY</span><h3>Password</h3><p>Use a strong password that is unique to Nexora.</p></div></div>
          <form onSubmit={savePassword}><Input label="Current password" type="password" value={password.current_password} onChange={e => setPassword({ ...password, current_password: e.target.value })} required autoComplete="current-password" /><Input label="New password" type="password" minLength={8} value={password.new_password} onChange={e => setPassword({ ...password, new_password: e.target.value })} required autoComplete="new-password" hint="At least 8 characters. Longer is better." /><Notice>Signed in as <strong>{user?.email}</strong>. Sensitive credential changes are audited by the workspace.</Notice><div className="form-end"><Button type="submit"><KeyRound size={16} /> Update password</Button></div></form>
        </Card>
      </div>
    </div>
    <Toast toast={toast} />
  </div>;
}
