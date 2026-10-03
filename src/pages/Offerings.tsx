import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Archive,
  Download,
  Edit3,
  FileJson,
  Plus,
  Search,
  Settings2,
  ToggleLeft,
  ToggleRight,
  Trash2,
  Upload,
} from "lucide-react";
import { offerings } from "../api";
import { useAuth } from "../auth";
import type { DynamicFieldDefinition, Offering, OfferingDetail, Pagination } from "../types";
import {
  Button,
  Card,
  Empty,
  Notice,
  Input,
  Modal,
  Select,
  Spinner,
  StatusPill,
  Textarea,
  Toast,
  fmtDate,
  money,
  useToast,
} from "../components/ui";

const types = [
  "PRODUCT","SERVICE","PLAN","SUBSCRIPTION","SAAS_PLAN","ROOM","HOTEL_ROOM",
  "RENTAL","COURSE","PACKAGE","LISTING","BOOKING","BUNDLE","SKU_BUNDLE","CUSTOM",
];

type OfferingForm = {
  name: string;
  offering_type: string;
  sku: string;
  current_price: string;
  currency: string;
  market: string;
  url: string;
  category: string;
  image_url: string;
  description: string;
  attributes: string;
  is_monitored: boolean;
};

const emptyForm: OfferingForm = {
  name: "",
  offering_type: "PRODUCT",
  sku: "",
  current_price: "",
  currency: "USD",
  market: "US",
  url: "",
  category: "",
  image_url: "",
  description: "",
  attributes: "{}",
  is_monitored: true,
};

function formFromOffering(o: Offering): OfferingForm {
  return {
    name: o.name,
    offering_type: o.offering_type,
    sku: o.sku || "",
    current_price: o.current_price == null ? "" : String(o.current_price),
    currency: o.currency || "USD",
    market: o.market || "US",
    url: o.url || "",
    category: o.category || "",
    image_url: o.image_url || "",
    description: o.description || "",
    attributes: JSON.stringify(o.attributes || {}, null, 2),
    is_monitored: o.is_monitored,
  };
}

function buildOfferingPayload(form: OfferingForm) {
  return {
    name: form.name,
    offering_type: form.offering_type,
    sku: form.sku || null,
    current_price: form.current_price ? Number(form.current_price) : null,
    currency: form.currency.toUpperCase(),
    market: form.market.toUpperCase(),
    url: form.url || null,
    category: form.category || null,
    image_url: form.image_url || null,
    description: form.description || null,
    attributes: JSON.parse(form.attributes || "{}"),
    is_monitored: form.is_monitored,
  };
}

export default function Offerings() {
  const { user } = useAuth();
  const canManage = user?.role === "ORG_ADMIN" || user?.role === "SUPER_ADMIN";
  const canAnalyze = canManage || user?.role === "ANALYST";
  const [data, setData] = useState<Pagination<Offering> | null>(null);
  const [fields, setFields] = useState<DynamicFieldDefinition[]>([]);
  const [q, setQ] = useState("");
  const [type, setType] = useState("");
  const [page, setPage] = useState(1);
  const [history, setHistory] = useState<import("../types").ObservationHistoryResponse | null>(null);
  const [historyPage, setHistoryPage] = useState(1);
  const [editor, setEditor] = useState<Offering | null>(null);
  const [detail, setDetail] = useState<OfferingDetail | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [fieldsOpen, setFieldsOpen] = useState(false);
  const [fieldCreateOpen, setFieldCreateOpen] = useState(false);
  const [fieldForm, setFieldForm] = useState({ field_name: "", display_name: "", data_type: "STRING", unit: "", category: "GENERAL" });
  const [form, setForm] = useState<OfferingForm>({ ...emptyForm });
  const [importText, setImportText] = useState("[]");
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const { toast, show } = useToast();

  const load = async () => {
    setLoading(true);
    try {
      const response = await offerings.list({
        q: q || undefined,
        offering_type: type || undefined,
        page,
        page_size: 50,
      });
      setData(response);
      setSelected([]);
    } catch (e) {
      show(e instanceof Error ? e.message : "Failed to load offerings", "error");
    } finally {
      setLoading(false);
    }
  };

  const loadFields = async () => {
    if (!canManage && !fieldsOpen) return;
    try {
      setFields(await offerings.fields());
    } catch (e) {
      show(e instanceof Error ? e.message : "Failed to load dynamic fields", "error");
    }
  };

  useEffect(() => {
    const timer = setTimeout(load, 250);
    return () => clearTimeout(timer);
  }, [q, type, page]);

  useEffect(() => {
    if (fieldsOpen) loadFields();
  }, [fieldsOpen]);

  const list = data?.items || [];
  const monitored = useMemo(() => list.filter(x => x.is_monitored && !x.is_archived).length, [list]);

  useEffect(() => { setPage(1); }, [q, type]);

  const openCreate = () => {
    setEditor(null);
    setForm({ ...emptyForm });
    setEditorOpen(true);
  };

  const openEdit = async (id: string) => {
    setSaving(true);
    try {
      const full = await offerings.get(id);
      setEditor(full);
      setForm(formFromOffering(full));
      setEditorOpen(true);
    } catch (e) {
      show(e instanceof Error ? e.message : "Failed to load offering", "error");
    } finally {
      setSaving(false);
    }
  };

  const openDetail = async (id: string) => {
    setDetailLoading(true);
    try {
      const [detailResponse, historyResponse] = await Promise.all([
        offerings.get(id),
        offerings.history(id, { page: 1, page_size: 20 }),
      ]);
      setDetail(detailResponse);
      setHistory(historyResponse);
      setHistoryPage(1);
    } catch (e) {
      show(e instanceof Error ? e.message : "Failed to load offering detail", "error");
    } finally {
      setDetailLoading(false);
    }
  };

  const save = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = buildOfferingPayload(form);
      if (editor) {
        await offerings.update(editor.id, payload);
        show("Offering updated.");
      } else {
        await offerings.create(payload);
        show("Offering created.");
      }
      setEditorOpen(false);
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Could not save offering", "error");
    } finally {
      setSaving(false);
    }
  };

  const importBulk = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const parsed = JSON.parse(importText);
      const items = Array.isArray(parsed) ? parsed : parsed.items;
      if (!Array.isArray(items) || items.length < 1 || items.length > 1000) {
        throw new Error("Import must contain between 1 and 1,000 offering objects.");
      }
      const result = await offerings.bulk(items);
      show(`${String(result.successful_count ?? result.archived_count ?? "Bulk operation")} processed.`);
      setImportOpen(false);
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Bulk import failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const archiveSelected = async () => {
    if (!selected.length || !canManage) return;
    if (!confirm(`Archive ${selected.length} selected offering(s)?`)) return;
    setSaving(true);
    try {
      await offerings.bulkArchive(selected);
      show(`${selected.length} offerings archived.`);
      await load();
    } catch (e) {
      show(e instanceof Error ? e.message : "Bulk archive failed", "error");
    } finally {
      setSaving(false);
    }
  };

  const createField = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await offerings.createField({
        ...fieldForm,
        unit: fieldForm.unit || null,
        category: fieldForm.category || null,
        is_selected: true,
        confidence: "HIGH",
        is_required: false,
        is_comparable: true,
        options: null,
      });
      show("Dynamic field created.");
      setFieldCreateOpen(false);
      setFieldForm({ field_name: "", display_name: "", data_type: "STRING", unit: "", category: "GENERAL" });
      await loadFields();
    } catch (e) {
      show(e instanceof Error ? e.message : "Could not create dynamic field", "error");
    } finally {
      setSaving(false);
    }
  };

  const selectedCount = selected.length;
  const allSelected = list.length > 0 && list.every(x => selected.includes(x.id));

  return (
    <div className="stack">
      <div className="toolbar">
        <div>
          <span className="eyebrow">CATALOG CONTROL</span>
          <h2>Offerings</h2>
          <p>Manage the canonical catalog that feeds competitive monitoring.</p>
        </div>
        <div className="toolbar-actions">
          <Button variant="secondary" onClick={() => offerings.export("csv").catch(e => show(e.message, "error"))}>
            <Download size={16} /> CSV
          </Button>
          <Button variant="secondary" onClick={() => offerings.export("json").catch(e => show(e.message, "error"))}>
            <FileJson size={16} /> JSON
          </Button>
          {canManage && (
            <>
              <Button variant="secondary" onClick={() => setImportOpen(true)}>
                <Upload size={16} /> Bulk import
              </Button>
              <Button variant="secondary" onClick={() => setFieldsOpen(true)}>
                <Settings2 size={16} /> Dynamic fields
              </Button>
              <Button onClick={openCreate}>
                <Plus size={16} /> Add offering
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="filter-row">
        <label className="search-box">
          <Search size={17} />
          <input placeholder="Search name, SKU, category…" value={q} onChange={e => setQ(e.target.value)} />
        </label>
        <Select value={type} onChange={e => setType(e.target.value)}>
          <option value="">All types</option>
          {types.map(t => <option key={t}>{t}</option>)}
        </Select>
        <span className="filter-meta">{data?.total_count ?? 0} total · {monitored} monitored on this page</span>
        {canManage && selectedCount > 0 && (
          <Button variant="danger" onClick={archiveSelected} disabled={saving}>
            <Trash2 size={16} /> Archive {selectedCount}
          </Button>
        )}
      </div>

      {loading ? (
        <Spinner label="Loading catalog…" />
      ) : list.length ? (
        <Card className="table-card">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {canManage && (
                    <th>
                      <input
                        aria-label="Select all"
                        type="checkbox"
                        checked={allSelected}
                        onChange={e => setSelected(e.target.checked ? list.map(x => x.id) : [])}
                      />
                    </th>
                  )}
                  <th>Offering</th><th>Type</th><th>Price</th><th>Market</th><th>Monitoring</th><th>Updated</th><th />
                </tr>
              </thead>
              <tbody>
                {list.map(o => {
                  const checked = selected.includes(o.id);
                  return (
                    <tr key={o.id}>
                      {canManage && (
                        <td>
                          <input
                            aria-label={`Select ${o.name}`}
                            type="checkbox"
                            checked={checked}
                            onChange={e => setSelected(prev => e.target.checked ? [...prev, o.id] : prev.filter(id => id !== o.id))}
                          />
                        </td>
                      )}
                      <td>
                        <div className="row-main">
                          {o.image_url ? <img className="thumb-image" src={o.image_url} alt="" /> : <div className="thumb">{o.name[0]}</div>}
                          <div>
                            {canAnalyze ? <button className="link-button" onClick={() => openDetail(o.id)}>{o.name}</button> : <strong>{o.name}</strong>}
                            <span>{o.sku || "No SKU"} · {o.category || "Uncategorized"}</span>
                          </div>
                        </div>
                      </td>
                      <td>{o.offering_type}</td>
                      <td><strong>{money(o.current_price, o.currency || "USD")}</strong></td>
                      <td>{o.market}</td>
                      <td><StatusPill value={o.is_monitored ? "MONITORED" : "PAUSED"} /></td>
                      <td>{fmtDate(o.updated_at)}</td>
                      <td>
                        <div className="row-actions">
                          {canManage && (
                            <>
                              <button className="icon-btn" title="Edit" onClick={() => openEdit(o.id)}><Edit3 size={16} /></button>
                              <button className="icon-btn" title="Toggle monitoring" onClick={async () => { try { await offerings.monitor(o.id); show("Monitoring state updated."); await load(); } catch (e) { show(e instanceof Error ? e.message : "Update failed", "error"); } }}>
                                {o.is_monitored ? <ToggleRight size={18} /> : <ToggleLeft size={18} />}
                              </button>
                              <button className="icon-btn danger-icon" title="Archive" onClick={async () => { if (!confirm("Archive this offering?")) return; try { await offerings.archive(o.id); show("Offering archived."); await load(); } catch (e) { show(e instanceof Error ? e.message : "Archive failed", "error"); } }}>
                                <Archive size={17} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Empty title="Your catalog is empty" detail="Add an offering manually or use Discovery to scan your website." />
      )}

      <Modal open={editorOpen} onClose={() => setEditorOpen(false)} title={editor ? `Edit ${editor.name}` : "Add catalog offering"}>
        <form className="form-grid" onSubmit={save}>
          <Input label="Name" value={form.name} required onChange={e => setForm({ ...form, name: e.target.value })} />
          <Select label="Offering type" value={form.offering_type} onChange={e => setForm({ ...form, offering_type: e.target.value })}>
            {types.map(t => <option key={t}>{t}</option>)}
          </Select>
          <Input label="SKU" value={form.sku} onChange={e => setForm({ ...form, sku: e.target.value })} />
          <div className="split-fields">
            <Input label="Current price" value={form.current_price} onChange={e => setForm({ ...form, current_price: e.target.value })} type="number" min="0" step="0.0001" />
            <Input label="Currency" value={form.currency} onChange={e => setForm({ ...form, currency: e.target.value.toUpperCase() })} />
          </div>
          <div className="split-fields">
            <Input label="Market" value={form.market} onChange={e => setForm({ ...form, market: e.target.value.toUpperCase() })} />
            <Input label="Category" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} />
          </div>
          <Input label="Product URL" value={form.url} onChange={e => setForm({ ...form, url: e.target.value })} placeholder="https://…" />
          <Input label="Image URL" value={form.image_url} onChange={e => setForm({ ...form, image_url: e.target.value })} />
          <Textarea label="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          <Textarea label="Dynamic attributes (JSON)" value={form.attributes} onChange={e => setForm({ ...form, attributes: e.target.value })} />
          <label className="check"><input type="checkbox" checked={form.is_monitored} onChange={e => setForm({ ...form, is_monitored: e.target.checked })} /> Start monitoring immediately</label>
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setEditorOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>{saving ? "Saving…" : editor ? "Save changes" : "Create offering"}</Button>
          </div>
        </form>
      </Modal>

      <Modal open={!!detail} onClose={() => { setDetail(null); setHistory(null); setHistoryPage(1); }} title={detail?.name || "Offering detail"}>
        {detailLoading ? <Spinner /> : detail && (
          <div className="detail-grid">
            <div><span className="eyebrow">CURRENT PRICE</span><strong className="big-number">{money(detail.current_price, detail.currency || "USD")}</strong></div>
            <div><span className="eyebrow">MONITORING</span><StatusPill value={detail.is_monitored ? "MONITORED" : "PAUSED"} /></div>
            <div className="detail-block"><span>Competitor matches</span><strong>{detail.competitor_matches_count}</strong></div>
            <div className="detail-block"><span>Min competitor price</span><strong>{money(detail.min_competitor_price, detail.currency || "USD")}</strong></div>
            <div className="detail-block"><span>Average competitor price</span><strong>{money(detail.avg_competitor_price, detail.currency || "USD")}</strong></div>
            <div className="detail-block"><span>Price delta</span><strong>{detail.price_delta_percent == null ? "—" : `${Number(detail.price_delta_percent).toFixed(2)}%`}</strong></div>
            <div className="detail-block"><span>Category</span><strong>{detail.category || "—"}</strong></div>
            <div className="detail-block"><span>SKU</span><strong>{detail.sku || "—"}</strong></div>
            <div className="detail-block full-span"><span>Matches</span><div className="list">{detail.matches.map((m, i) => <div className="list-row" key={String(m.match_id || i)}><div><strong>{String(m.competitor_name || "Competitor")}</strong><span>{String(m.source_name || "Source")}</span></div><div className="row-end"><StatusPill value={String(m.match_status || "")} /> <a href={String(m.target_url || "#")} target="_blank" rel="noreferrer">Open</a></div></div>)}</div></div>
            <div className="detail-block full-span"><span>Price & availability history</span>{history?.items.length ? <div className="list">{history.items.map(item => <div className="list-row" key={item.id}><div><strong>{money(item.observed_price,item.currency||detail.currency||"USD")}</strong><span>{item.competitor_name} · {item.source_name} · {fmtDate(item.observed_at)}</span></div><div className="row-end"><StatusPill value={item.availability}/><span className="subtle">{item.http_status_code}</span></div></div>)}{history.total_pages>1&&<div className="pagination"><Button variant="secondary" disabled={historyPage<=1} onClick={async()=>{const next=Math.max(1,historyPage-1);setHistoryPage(next);setHistory(await offerings.history(detail.id,{page:next,page_size:20}))}}>Previous</Button><span>Page {history.page} of {history.total_pages}</span><Button variant="secondary" disabled={!history.has_more} onClick={async()=>{const next=historyPage+1;setHistoryPage(next);setHistory(await offerings.history(detail.id,{page:next,page_size:20}))}}>Next</Button></div>}</div> : <Empty title="No observations yet" detail="Run a collection to begin the historical price series." />}</div>
            <div className="detail-block full-span"><span>Attributes</span><pre>{JSON.stringify(detail.attributes || {}, null, 2)}</pre></div>
          </div>
        )}
      </Modal>

      <Modal open={importOpen} onClose={() => setImportOpen(false)} title="Bulk import offerings">
        <form className="form-grid" onSubmit={importBulk}>
          <Notice>Paste a JSON array of offering objects, or an object containing an <strong>items</strong> array. Maximum 1,000 items.</Notice>
          <Textarea label="Offering JSON" value={importText} onChange={e => setImportText(e.target.value)} />
          <div className="modal-actions">
            <Button variant="secondary" onClick={() => setImportOpen(false)}>Cancel</Button>
            <Button type="submit" disabled={saving}>Import offerings</Button>
          </div>
        </form>
      </Modal>

      <Modal open={fieldsOpen} onClose={() => setFieldsOpen(false)} title="Dynamic field definitions">
        <div className="stack">
          <div className="modal-actions"><Button onClick={() => setFieldCreateOpen(true)}><Plus size={16} /> Add field</Button></div>
          {fields.length ? <div className="list">{fields.map(f => <div className="list-row" key={f.id}><div><strong>{f.display_name}</strong><span>{f.field_name} · {f.data_type} · {f.category || "GENERAL"}</span></div><button className="icon-btn danger-icon" onClick={async () => { if (!confirm(`Delete field ${f.display_name}?`)) return; try { await offerings.removeField(f.id); show("Dynamic field deleted."); await loadFields(); } catch (e) { show(e instanceof Error ? e.message : "Delete failed", "error"); } }}><Trash2 size={16} /></button></div>)}</div> : <Empty title="No dynamic fields" detail="Create one when you need a tenant-specific catalog attribute." />}
        </div>
      </Modal>

      <Modal open={fieldCreateOpen} onClose={() => setFieldCreateOpen(false)} title="Create dynamic field">
        <form onSubmit={createField}>
          <Input label="Machine name" required value={fieldForm.field_name} onChange={e => setFieldForm({ ...fieldForm, field_name: e.target.value })} placeholder="battery_life_hours" />
          <Input label="Display name" required value={fieldForm.display_name} onChange={e => setFieldForm({ ...fieldForm, display_name: e.target.value })} />
          <div className="split-fields">
            <Input label="Data type" value={fieldForm.data_type} onChange={e => setFieldForm({ ...fieldForm, data_type: e.target.value.toUpperCase() })} />
            <Input label="Unit" value={fieldForm.unit} onChange={e => setFieldForm({ ...fieldForm, unit: e.target.value })} />
          </div>
          <Input label="Category" value={fieldForm.category} onChange={e => setFieldForm({ ...fieldForm, category: e.target.value })} />
          <div className="modal-actions"><Button variant="secondary" onClick={() => setFieldCreateOpen(false)}>Cancel</Button><Button type="submit" disabled={saving}>Create field</Button></div>
        </form>
      </Modal>

      {data && data.total_pages > 1 && (
        <div className="pagination">
          <Button variant="secondary" disabled={page <= 1 || loading} onClick={() => setPage(value => Math.max(1, value - 1))}>Previous</Button>
          <span>Page {data.page} of {data.total_pages}</span>
          <Button variant="secondary" disabled={!data.has_more || loading} onClick={() => setPage(value => value + 1)}>Next</Button>
        </div>
      )}
      <Toast toast={toast} />
    </div>
  );
}
