import { useEffect, useId, useState, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { AlertTriangle, Check, CheckCircle2, ChevronDown, Info, Loader2, Sparkles, X } from "lucide-react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  disabled = false,
  className = "",
  loading = false,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  variant?: ButtonVariant;
  disabled?: boolean;
  className?: string;
  loading?: boolean;
}) {
  return (
    <button
      className={"btn btn-" + variant + " " + className}
      onClick={onClick}
      type={type}
      disabled={disabled || loading}
      aria-busy={loading}
    >
      {loading ? <Loader2 size={16} className="spin" /> : null}
      {children}
    </button>
  );
}

export function Input({
  label,
  error,
  hint,
  required,
  ...props
}: {
  label?: string;
  error?: string;
  hint?: string;
  required?: boolean;
} & InputHTMLAttributes<HTMLInputElement>) {
  const [visible, setVisible] = useState(false);
  const isPassword = props.type === "password";
  const baseId = props.id ?? useId();
  const describedBy = [hint ? baseId + "-hint" : "", error ? baseId + "-error" : ""].filter(Boolean).join(" ") || undefined;

  return (
    <label className={"field " + (error ? "has-error" : "")}>
      {label ? (
        <span className="field-label">
          {label}
          {required || props.required ? <em aria-hidden="true">*</em> : null}
        </span>
      ) : null}
      <span className="input-wrap">
        <input
          {...props}
          id={props.id ?? baseId}
          type={isPassword && visible ? "text" : props.type}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy}
        />
        {isPassword ? (
          <button
            className="input-action"
            type="button"
            onClick={() => setVisible(value => !value)}
            aria-label={visible ? "Hide password" : "Show password"}
            title={visible ? "Hide password" : "Show password"}
          >
            {visible ? "Hide" : "Show"}
          </button>
        ) : null}
      </span>
      {hint ? <small id={baseId + "-hint"} className="field-hint">{hint}</small> : null}
      {error ? <small id={baseId + "-error"} className="error-text">{error}</small> : null}
    </label>
  );
}

export function Select({
  label,
  hint,
  children,
  ...props
}: {
  label?: string;
  hint?: string;
} & SelectHTMLAttributes<HTMLSelectElement>) {
  const generatedId = useId();
  return (
    <label className="field">
      {label ? <span className="field-label">{label}</span> : null}
      <span className="select-wrap">
        <select id={props.id ?? generatedId} {...props}>{children}</select>
        <ChevronDown size={16} aria-hidden="true" />
      </span>
      {hint ? <small className="field-hint">{hint}</small> : null}
    </label>
  );
}

export function Textarea({
  label,
  hint,
  ...props
}: {
  label?: string;
  hint?: string;
} & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <label className="field">
      {label ? <span className="field-label">{label}</span> : null}
      <textarea {...props} />
      {hint ? <small className="field-hint">{hint}</small> : null}
    </label>
  );
}

export function StatusPill({ value }: { value: string }) {
  const normalized = value.toLowerCase();
  const tone =
    normalized.includes("fail") ||
    normalized.includes("block") ||
    normalized.includes("open") ||
    normalized.includes("archiv") ||
    normalized.includes("error")
      ? "danger"
      : normalized.includes("warn") ||
        normalized.includes("pending") ||
        normalized.includes("suggest") ||
        normalized.includes("paused")
        ? "warn"
        : normalized.includes("active") ||
          normalized.includes("healthy") ||
          normalized.includes("complete") ||
          normalized.includes("verified") ||
          normalized.includes("approv") ||
          normalized.includes("in_stock") ||
          normalized.includes("running")
          ? "success"
          : "neutral";

  return (
    <span className={"pill pill-" + tone}>
      <span className="pill-dot" />
      {value.replaceAll("_", " ")}
    </span>
  );
}

export function Card({
  children,
  className = "",
  interactive = false,
}: {
  children: ReactNode;
  className?: string;
  interactive?: boolean;
}) {
  return <section className={"card " + (interactive ? "card-interactive " : "") + className}>{children}</section>;
}

export function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.body.classList.add("modal-open");
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.classList.remove("modal-open");
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="modal-backdrop"
      onMouseDown={event => {
        if (event.target === event.currentTarget) onClose();
      }}
      role="presentation"
    >
      <div className="modal modal-enter" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className="modal-head">
          <div>
            <span className="eyebrow">NEXORA WORKSPACE</span>
            <h3 id="modal-title">{title}</h3>
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Close dialog" title="Close">
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <div className="loading-orbit"><span /><span /><span /></div>
      <strong>{label}</strong>
      <small>Syncing the latest workspace state</small>
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={"skeleton " + className} aria-hidden="true" />;
}

export function Empty({
  title,
  detail,
  action,
}: {
  title: string;
  detail?: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <div className="empty-orb"><Sparkles size={20} /></div>
      <strong>{title}</strong>
      {detail ? <span>{detail}</span> : null}
      {action ? <div className="empty-action">{action}</div> : null}
    </div>
  );
}

export function Notice({
  type = "info",
  children,
}: {
  type?: "info" | "success" | "error" | "warning";
  children: ReactNode;
}) {
  const Icon =
    type === "error"
      ? AlertTriangle
      : type === "success"
        ? CheckCircle2
        : type === "warning"
          ? AlertTriangle
          : Info;

  return (
    <div className={"notice notice-" + type} role={type === "error" ? "alert" : "status"}>
      <Icon size={17} aria-hidden="true" />
      <span>{children}</span>
    </div>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  detail,
  actions,
}: {
  eyebrow?: string;
  title: string;
  detail?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
        <h2>{title}</h2>
        {detail ? <p>{detail}</p> : null}
      </div>
      {actions ? <div className="page-header-actions">{actions}</div> : null}
    </div>
  );
}

export function useToast() {
  const [toast, setToast] = useState<{ kind: "success" | "error"; text: string } | null>(null);

  const show = (text: string, kind: "success" | "error" = "success") => {
    setToast({ text, kind });
    window.setTimeout(() => setToast(null), 3800);
  };

  return { toast, show };
}

export function Toast({ toast }: { toast: { kind: "success" | "error"; text: string } | null }) {
  return toast ? (
    <div className={"toast toast-" + toast.kind} role={toast.kind === "error" ? "alert" : "status"} aria-live="polite">
      {toast.kind === "success" ? <Check size={17} /> : <AlertTriangle size={17} />}
      <span>{toast.text}</span>
    </div>
  ) : null;
}

export const fmtDate = (value?: string | null) =>
  value
    ? new Date(value).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })
    : "—";

export const money = (value: string | number | null | undefined, currency = "USD") =>
  value == null
    ? "—"
    : new Intl.NumberFormat(undefined, {
        style: "currency",
        currency,
        maximumFractionDigits: 2,
      }).format(Number(value));
