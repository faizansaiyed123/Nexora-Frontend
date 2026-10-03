import { FormEvent, useEffect, useState } from "react";
import { Bell, Check, Edit3, Plus, Trash2 } from "lucide-react";
import { alerts, offerings } from "../api";
import { useAuth } from "../auth";
import type { AlertLog, AlertRule, Offering } from "../types";
import {
  Button,
  Card,
  Empty,
  Input,
  Modal,
  Select,
  Spinner,
  StatusPill,
  Toast,
  useToast,
  fmtDate,
} from "../components/ui";

const alertTypes = [
  "PRICE_CHANGE",
  "PERCENTAGE_DROP",
  "UNDERCUT_THRESHOLD",
  "STOCK_CHANGE",
  "CIRCUIT_BREAKER_TRIPPED",
];

type RuleForm = {
  name: string;
  alert_type: string;
  threshold_value: string;
  offering_id: string;
  cooldown_minutes: string;
  email: boolean;
};

const blankForm: RuleForm = {
  name: "",
  alert_type: "PERCENTAGE_DROP",
  threshold_value: "5",
  offering_id: "",
  cooldown_minutes: "60",
  email: true,
};

export default function Alerts() {
  const { user } = useAuth();
  const canManage = user?.role === "ORG_ADMIN" || user?.role === "SUPER_ADMIN";
  const canAnalyze = canManage || user?.role === "ANALYST";

  const [rules, setRules] = useState<AlertRule[]>([]);
  const [logs, setLogs] = useState<AlertLog[]>([]);
  const [offeringsList, setOfferingsList] = useState<Offering[]>([]);
  const [editing, setEditing] = useState<AlertRule | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<RuleForm>({ ...blankForm });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const { toast, show } = useToast();

  const load = async () => {
    setLoading(true);
    try {
      const [ruleRows, logRows, offeringRows] = await Promise.all([
        alerts.listRules(),
        alerts.listLogs(),
        offerings.list({ page: 1, page_size: 500 }),
      ]);
      setRules(ruleRows);
      setLogs(logRows);
      setOfferingsList(offeringRows.items);
    } catch (e) {
      show(e instanceof Error ? e.message : "Alerts unavailable", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ ...blankForm });
    setModalOpen(true);
  };

  const openEdit = (rule: AlertRule) => {
    setEditing(rule);
    setForm({
      name: rule.name,
      alert_type: rule.alert_type,
      threshold_value: rule.threshold_value == null ? "" : String(rule.threshold_value),
      offering_id: rule.offering_id || "",
      cooldown_minutes: String(rule.cooldown_minutes),
      email: Boolean(rule.target_channels?.email),
    });
    setModalOpen(true);
  };

  const saveRule = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        alert_type: form.alert_type,
        threshold_value: form.threshold_value === "" ? null : Number(form.threshold_value),
        offering_id: form.offering_id || null,
        cooldown_minutes: Number(form.cooldown_minutes),
        is_active: editing?.is_active ?? true,
        target_channels: { email: form.email },
      };

      if (editing) {
        await alerts.updateRule(editing.id, payload);
        show("Alert rule updated.");
      } else {
        await alerts.createRule(payload);
        show("Alert rule created.");
      }

      setModalOpen(false);
      setEditing(null);
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Could not save alert rule", "error");
    } finally {
      setSaving(false);
    }
  };

  const toggleRule = async (rule: AlertRule) => {
    try {
      await alerts.updateRule(rule.id, { is_active: !rule.is_active });
      show(rule.is_active ? "Rule paused." : "Rule activated.");
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Could not update rule", "error");
    }
  };

  const deleteRule = async (rule: AlertRule) => {
    if (!confirm(`Delete "${rule.name}"?`)) return;
    try {
      await alerts.removeRule(rule.id);
      show("Rule deleted.");
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Could not delete rule", "error");
    }
  };

  const markRead = async (log: AlertLog) => {
    try {
      await alerts.markRead(log.id);
      show("Alert marked as read.");
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Could not update alert", "error");
    }
  };

  return (
    <div className="stack">
      <div className="toolbar">
        <div>
          <span className="eyebrow">SIGNAL MANAGEMENT</span>
          <h2>Alerts</h2>
          <p>Turn price, stock, and circuit-breaker events into persistent notification history.</p>
        </div>
        {canManage && (
          <Button onClick={openCreate}>
            <Plus size={16} /> New rule
          </Button>
        )}
      </div>

      {loading ? (
        <Spinner label="Loading alerts…" />
      ) : (
        <div className="grid-2">
          <Card>
            <div className="card-title">
              <div>
                <span className="eyebrow">RULES</span>
                <h3>Alert rules</h3>
              </div>
              <Bell size={18} />
            </div>
            {rules.length ? (
              <div className="list">
                {rules.map(rule => (
                  <div className="list-row" key={rule.id}>
                    <div>
                      <strong>{rule.name}</strong>
                      <span>
                        {rule.alert_type.replace(/_/g, " ")} ·{" "}
                        {rule.threshold_value == null ? "no threshold" : rule.threshold_value}
                      </span>
                    </div>
                    <div className="row-end">
                      <StatusPill value={rule.is_active ? "ACTIVE" : "PAUSED"} />
                      {canManage && (
                        <>
                          <button className="icon-btn" title="Edit rule" onClick={() => openEdit(rule)}>
                            <Edit3 size={16} />
                          </button>
                          <button className="icon-btn" title={rule.is_active ? "Pause rule" : "Activate rule"} onClick={() => toggleRule(rule)}>
                            <Bell size={15} />
                          </button>
                          <button className="icon-btn danger-icon" title="Delete rule" onClick={() => deleteRule(rule)}>
                            <Trash2 size={16} />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <Empty title="No rules configured" detail="Create a trigger for price, stock, or source health signals." />
            )}
          </Card>

          <Card>
            <div className="card-title">
              <div>
                <span className="eyebrow">EVENT LOG</span>
                <h3>Recent alerts</h3>
              </div>
              <span className="unread">{logs.filter(log => !log.is_read).length} unread</span>
            </div>
            {logs.length ? (
              <div className="list">
                {logs.slice(0, 30).map(log => (
                  <div className={`alert-row ${log.is_read ? "read" : ""}`} key={log.id}>
                    <div>
                      <strong>{log.title}</strong>
                      <span>{log.message}</span>
                      <small>{fmtDate(log.created_at)}</small>
                    </div>
                    {canAnalyze && <button
                      className="icon-btn"
                      title={log.is_read ? "Read" : "Mark as read"}
                      disabled={log.is_read}
                      onClick={() => markRead(log)}
                    >
                      <Check size={16} />
                    </button>}
                  </div>
                ))}
              </div>
            ) : (
              <Empty title="No alert events" detail="Triggered rules will appear here after a collection event." />
            )}
          </Card>
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "Edit alert rule" : "Create alert rule"}>
        <form onSubmit={saveRule}>
          <Input
            label="Rule name"
            required
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
          />
          <Select
            label="Alert type"
            value={form.alert_type}
            onChange={e => setForm({ ...form, alert_type: e.target.value })}
          >
            {alertTypes.map(type => <option key={type}>{type}</option>)}
          </Select>
          <Select
            label="Offering scope"
            value={form.offering_id}
            onChange={e => setForm({ ...form, offering_id: e.target.value })}
          >
            <option value="">All offerings</option>
            {offeringsList.map(offering => (
              <option key={offering.id} value={offering.id}>{offering.name}</option>
            ))}
          </Select>
          <div className="split-fields">
            <Input
              label="Threshold"
              type="number"
              step="0.01"
              value={form.threshold_value}
              onChange={e => setForm({ ...form, threshold_value: e.target.value })}
            />
            <Input
              label="Cooldown (minutes)"
              type="number"
              min="1"
              value={form.cooldown_minutes}
              onChange={e => setForm({ ...form, cooldown_minutes: e.target.value })}
            />
          </div>
          <label className="check">
            <input
              type="checkbox"
              checked={form.email}
              onChange={e => setForm({ ...form, email: e.target.checked })}
            />
            Deliver through email channel
          </label>
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : editing ? "Save changes" : "Create rule"}
            </Button>
          </div>
        </form>
      </Modal>

      <Toast toast={toast} />
    </div>
  );
}
