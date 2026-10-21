import { Children, cloneElement, useEffect, useId, useRef, useState, type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactElement, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { AlertTriangle, Check, CheckCircle2, ChevronDown, Info, Loader2, Sparkles, Timer, X } from "lucide-react";
import { formatRateLimitCountdown, useRateLimitCountdown } from "../rateLimit";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  disabled = false,
  className = "",
  loading = false,
  rateLimitKey,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  variant?: ButtonVariant;
  disabled?: boolean;
  className?: string;
  loading?: boolean;
  rateLimitKey?: string;
}) {
  const retrySeconds = useRateLimitCountdown(rateLimitKey);
  const rateLimited = retrySeconds > 0;
  const countdown = formatRateLimitCountdown(retrySeconds);

  return (
    <button
      className={"btn btn-" + variant + " " + className + (rateLimited ? " is-rate-limited" : "")}
      onClick={onClick}
      type={type}
      disabled={disabled || loading || rateLimited}
      aria-busy={loading}
      aria-disabled={disabled || loading || rateLimited}
      title={rateLimited ? `Try again in ${countdown}` : undefined}
    >
      {loading ? <Loader2 size={16} className="spin" /> : null}
      {rateLimited ? <><Timer size={15} aria-hidden="true" /><span aria-live="polite">Try again in {countdown}</span></> : children}
    </button>
  );
}

export function RateLimitIconButton({
  children,
  onClick,
  disabled = false,
  title,
  rateLimitKey,
}: {
  children: ReactNode;
  onClick?: ButtonHTMLAttributes<HTMLButtonElement>["onClick"];
  disabled?: boolean;
  title: string;
  rateLimitKey: string;
}) {
  const retrySeconds = useRateLimitCountdown(rateLimitKey);
  const rateLimited = retrySeconds > 0;
  const countdown = formatRateLimitCountdown(retrySeconds);
  const label = rateLimited ? `Try again in ${countdown}` : title;

  return (
    <button
      className={"icon-btn rate-limit-icon-btn" + (rateLimited ? " is-rate-limited" : "")}
      title={label}
      aria-label={label}
      aria-disabled={disabled || rateLimited}
      disabled={disabled || rateLimited}
      onClick={onClick}
    >
      {rateLimited ? <span className="rate-limit-icon-countdown" aria-live="polite">{countdown}</span> : children}
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
          {required ? <em aria-hidden="true">*</em> : null}
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
  error,
  children,
  ...props
}: {
  label?: string;
  hint?: string;
  error?: string;
} & SelectHTMLAttributes<HTMLSelectElement>) {
  const generatedId = useId();
  const describedBy = [hint ? generatedId + "-hint" : "", error ? generatedId + "-error" : ""].filter(Boolean).join(" ") || undefined;
  const wrapRef = useRef<HTMLSpanElement>(null);
  const [open, setOpen] = useState(false);
  const [internalValue, setInternalValue] = useState<string | undefined>(props.value as string | undefined);

  const options = Children.toArray(children)
    .filter((c): c is ReactElement =>
      c !== null && typeof c === "object" && c !== undefined && "props" in (c as any)
    )
    .map(c => {
      const p = (c as any).props;
      const label = p.children;
      const value = p.value !== undefined ? p.value : label;
      return { value, label };
    });

  const controlled = props.value !== undefined;
  const currentValue = controlled ? props.value : internalValue;
  const currentOption = options.find(o => String(o.value) === String(currentValue)) || options[0];
  const hasValue = currentValue !== undefined && currentValue !== "" && currentValue !== null;

  useEffect(() => {
    if (!open) return;
    const onDown = (event: MouseEvent) => {
      if (!wrapRef.current || wrapRef.current.contains(event.target as Node)) return;
      setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const selectValue = (value: any) => {
    if (!controlled) setInternalValue(value);
    setOpen(false);
    props.onChange?.({ target: { value } } as unknown as React.ChangeEvent<HTMLSelectElement>);
  };

  const move = (dir: 1 | -1) => {
    const idx = options.findIndex(o => String(o.value) === String(currentValue));
    const next = options[(idx + dir + options.length) % options.length];
    if (next) selectValue(next.value);
  };

  const onKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      setOpen(v => !v);
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      if (!open) setOpen(true);
      else move(1);
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      if (!open) setOpen(true);
      else move(-1);
    }
  };

  return (
    <label className={"field " + (error ? "has-error" : "")}>
      {label ? (
        <span className="field-label">
          {label}
          {props.required ? <em aria-hidden="true">*</em> : null}
        </span>
      ) : null}
      <span
        className={"select-wrap" + (error ? " is-invalid" : "") + (hasValue ? " has-value" : "") + (open ? " is-open" : "")}
        ref={wrapRef}
      >
        <select
          id={props.id ?? generatedId}
          aria-invalid={Boolean(error)}
          aria-describedby={describedBy}
          aria-required={props.required}
          className="sr-only"
          tabIndex={-1}
          style={{
            position: "absolute",
            width: "1px",
            height: "1px",
            padding: 0,
            margin: "-1px",
            overflow: "hidden",
            clip: "rect(0, 0, 0, 0)",
            whiteSpace: "nowrap",
            border: 0,
            opacity: 0,
            pointerEvents: "none",
          }}
          value={controlled ? props.value : internalValue}
          onChange={event => {
            if (!controlled) setInternalValue(event.target.value);
            props.onChange?.(event);
          }}
          {...props}
          required={false}
        >{children}</select>

        <button
          type="button"
          className="select-trigger"
          aria-expanded={open}
          aria-haspopup="listbox"
          aria-controls={open ? generatedId + "-listbox" : undefined}
          aria-invalid={Boolean(error)}
          disabled={props.disabled}
          onMouseDown={event => {
            event.preventDefault();
            setOpen(v => !v);
          }}
          onKeyDown={onKeyDown}
        >
          <span className="select-value">{currentOption ? String(currentOption.label) : ""}</span>
          <ChevronDown size={16} aria-hidden="true" />
        </button>

        {open ? (
          <ul
            id={generatedId + "-listbox"}
            className="select-options"
            role="listbox"
          >
            {options.map((o, i) => (
              <li
                key={o.value === undefined ? "opt-" + i : String(o.value)}
                className={"select-option" + (String(o.value) === String(currentValue) ? " is-selected" : "")}
                role="option"
                aria-selected={String(o.value) === String(currentValue)}
                onMouseDown={event => {
                  event.preventDefault();
                  selectValue(o.value);
                }}
              >
                {o.label}
              </li>
            ))}
          </ul>
        ) : null}
      </span>
      {hint ? <small id={generatedId + "-hint"} className="field-hint">{hint}</small> : null}
      {error ? <small id={generatedId + "-error"} className="error-text">{error}</small> : null}
    </label>
  );
}

export type DropdownDirection = "up" | "down";
export type DropdownTriggerProps = {
  className?: string;
  onClick?: (event: React.MouseEvent) => void;
  "aria-expanded"?: boolean;
  "aria-haspopup"?: "menu" | "listbox" | "tree" | "grid" | "dialog" | undefined;
  "aria-controls"?: string;
};

export function Dropdown({
  trigger,
  children,
  direction = "down",
  align = "right",
  menuClassName = "",
  menuId,
}: {
  trigger: React.ReactElement<DropdownTriggerProps>;
  children: ReactNode;
  direction?: DropdownDirection;
  align?: "left" | "right";
  menuClassName?: string;
  menuId?: string;
}) {
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);
  const generatedId = useId();
  const menuMenuId = menuId ?? generatedId + "-menu";

  useEffect(() => {
    if (!open) return;
    const onDown = (event: MouseEvent) => {
      if (!wrapRef.current || wrapRef.current.contains(event.target as Node)) return;
      setOpen(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const enhancedTrigger = cloneElement(trigger, {
    className: [trigger.props.className, "dropdown-trigger", open ? "is-open" : ""].filter(Boolean).join(" "),
    onClick: (event: React.MouseEvent) => {
      trigger.props.onClick?.(event);
      setOpen(value => !value);
    },
    "aria-expanded": open,
    "aria-haspopup": "menu",
    "aria-controls": open ? menuMenuId : undefined,
  });

  return (
    <div
      className={"dropdown" + (open ? " is-open" : "") + (direction === "up" ? " dropdown-up" : "")}
      ref={wrapRef}
    >
      {enhancedTrigger}
      {open ? (
        <div
          id={menuMenuId}
          className={"dropdown-menu dropdown-menu-" + align + " " + menuClassName}
          role="menu"
          aria-orientation="vertical"
        >
          {children}
        </div>
      ) : null}
    </div>
  );
}

export function DropdownItem({
  children,
  onClick,
  icon,
  danger = false,
  disabled = false,
}: {
  children: ReactNode;
  onClick?: () => void;
  icon?: ReactNode;
  danger?: boolean;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      className={"dropdown-item " + (danger ? "is-danger" : "")}
      disabled={disabled}
      onClick={onClick}
      role="menuitem"
    >
      {icon ? <span className="dropdown-item-icon" aria-hidden="true">{icon}</span> : null}
      <span>{children}</span>
    </button>
  );
}

export function DropdownSeparator() {
  return <div className="dropdown-separator" role="separator" />;
}

export function DropdownLabel({ children }: { children: ReactNode }) {
  return <div className="dropdown-label">{children}</div>;
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

let openModalsCount = 0;

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
    openModalsCount++;
    document.body.classList.add("modal-open");
    window.addEventListener("keydown", onKeyDown);
    return () => {
      openModalsCount = Math.max(0, openModalsCount - 1);
      if (openModalsCount === 0) {
        document.body.classList.remove("modal-open");
      }
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
        <div className="modal-body">
          {children}
        </div>
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
