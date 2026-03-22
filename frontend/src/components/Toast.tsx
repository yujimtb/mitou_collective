"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { createPortal } from "react-dom";

type ToastKind = "success" | "error";

interface ToastItem {
  id: string;
  kind: ToastKind;
  message: string;
}

interface ToastContextValue {
  pushToast: (toast: Omit<ToastItem, "id">) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let toastSequence = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const dismissToast = useCallback((toastId: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== toastId));
  }, []);

  const pushToast = useCallback(
    ({ kind, message }: Omit<ToastItem, "id">) => {
      const id = `toast-${toastSequence++}`;
      setToasts((current) => [...current, { id, kind, message }]);
      window.setTimeout(() => {
        dismissToast(id);
      }, 3000);
    },
    [dismissToast],
  );

  const value = useMemo(() => ({ pushToast }), [pushToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {mounted
        ? createPortal(
            <div className="toast-viewport" aria-atomic="true" aria-live="polite">
              {toasts.map((toast) => (
                <div className={`toast toast-${toast.kind}`} key={toast.id} role="status">
                  <strong>{toast.kind === "success" ? "Success" : "Error"}</strong>
                  <span>{toast.message}</span>
                </div>
              ))}
            </div>,
            document.body,
          )
        : null}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}
