import React, { useState, useEffect, useCallback } from "react";
import {
  captureAcademicScreenshot,
  downloadScreenshot,
  type ScreenshotResult,
} from "../utils/screenshot";

export interface ShortcutConfig {
  ctrlOrMeta: boolean;
  shift: boolean;
  alt: boolean;
  key: string; // e.g. "s"
}

const DEFAULT_SHORTCUT: ShortcutConfig = {
  ctrlOrMeta: true,
  shift: true,
  alt: false,
  key: "s",
};

interface ScreenshotManagerProps {
  activePhaseName?: string;
  runId?: string;
  sha256?: string;
}

// Global hook or trigger listener
let globalTriggerScreenshot: (() => void) | null = null;
export const triggerAppScreenshot = () => {
  if (globalTriggerScreenshot) {
    globalTriggerScreenshot();
  }
};

export const ScreenshotManager: React.FC<ScreenshotManagerProps> = ({
  activePhaseName = "White Calculation Room",
  runId = "VELA-001",
  sha256 = "8a4c9b139f4e221d68019a28e932bce2",
}) => {
  // Shortcut settings stored in localStorage
  const [shortcut, setShortcut] = useState<ShortcutConfig>(() => {
    try {
      const saved = localStorage.getItem("z_zoa_screenshot_shortcut");
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.warn("Failed to load saved screenshot shortcut:", e);
    }
    return DEFAULT_SHORTCUT;
  });

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [toast, setToast] = useState<{
    visible: boolean;
    copied: boolean;
    sizeKb?: number;
    error?: string;
    blob?: Blob;
  }>({ visible: false, copied: false });

  // Save shortcut to localStorage
  const saveShortcut = (newCfg: ShortcutConfig) => {
    setShortcut(newCfg);
    try {
      localStorage.setItem("z_zoa_screenshot_shortcut", JSON.stringify(newCfg));
    } catch (e) {
      console.warn("Failed to save shortcut:", e);
    }
  };

  // Capture execution
  const executeCapture = useCallback(async () => {
    if (isCapturing) return;
    setIsCapturing(true);

    // 1. Camera Flash Animation
    setIsFlashing(true);
    setTimeout(() => setIsFlashing(false), 220);

    try {
      // Find main app container or root
      const appRoot =
        document.getElementById("z-zoa-app-container") ||
        document.getElementById("root") ||
        document.body;

      // 2. Perform Capture & Clipboard copy
      const result: ScreenshotResult = await captureAcademicScreenshot(appRoot, {
        phaseName: activePhaseName,
        runId,
        sha256,
      });

      if (result.success && result.blob) {
        const sizeKb = Math.round(result.blob.size / 1024);
        setToast({
          visible: true,
          copied: result.copiedToClipboard,
          sizeKb,
          blob: result.blob,
        });

        // Hide toast after 4.5s
        setTimeout(() => {
          setToast((prev) => ({ ...prev, visible: false }));
        }, 4500);
      } else {
        setToast({
          visible: true,
          copied: false,
          error: result.error || "Capture failed",
        });
      }
    } catch (err: any) {
      setToast({
        visible: true,
        copied: false,
        error: err?.message || String(err),
      });
    } finally {
      setIsCapturing(false);
    }
  }, [isCapturing, activePhaseName, runId, sha256]);

  // Register global trigger
  useEffect(() => {
    globalTriggerScreenshot = executeCapture;
    return () => {
      globalTriggerScreenshot = null;
    };
  }, [executeCapture]);

  // Global Keydown Listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger inside text inputs or textareas unless target is body
      const target = e.target as HTMLElement;
      if (
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable) &&
        e.key.toLowerCase() !== "s"
      ) {
        return;
      }

      const ctrlOrMetaPressed = e.ctrlKey || e.metaKey;
      const shiftPressed = e.shiftKey;
      const altPressed = e.altKey;
      const keyPressed = e.key.toLowerCase();

      const matchesCtrl = shortcut.ctrlOrMeta ? ctrlOrMetaPressed : !ctrlOrMetaPressed;
      const matchesShift = shortcut.shift ? shiftPressed : !shiftPressed;
      const matchesAlt = shortcut.alt ? altPressed : !altPressed;
      const matchesKey = keyPressed === shortcut.key.toLowerCase();

      if (matchesCtrl && matchesShift && matchesAlt && matchesKey) {
        e.preventDefault();
        e.stopPropagation();
        executeCapture();
      }
    };

    window.addEventListener("keydown", handleKeyDown, { capture: true });
    return () => {
      window.removeEventListener("keydown", handleKeyDown, { capture: true });
    };
  }, [shortcut, executeCapture]);

  // Shortcut string representation
  const shortcutDisplay = [
    shortcut.ctrlOrMeta ? (navigator.platform.includes("Mac") ? "⌘" : "Ctrl") : "",
    shortcut.alt ? "Alt" : "",
    shortcut.shift ? "Shift" : "",
    shortcut.key.toUpperCase(),
  ]
    .filter(Boolean)
    .join("+");

  return (
    <>
      {/* 1. Camera White Flash Overlay */}
      {isFlashing && (
        <div
          className="no-screenshot"
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "#FFFFFF",
            opacity: 0.85,
            zIndex: 99999,
            pointerEvents: "none",
            transition: "opacity 0.22s cubic-bezier(0.16, 1, 0.3, 1)",
          }}
        />
      )}

      {/* 2. Toast Notification */}
      {toast.visible && (
        <div
          className="no-screenshot"
          style={{
            position: "fixed",
            bottom: "28px",
            right: "28px",
            backgroundColor: "#0F172A",
            color: "#FFFFFF",
            borderRadius: "8px",
            padding: "14px 18px",
            boxShadow:
              "0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3)",
            display: "flex",
            alignItems: "center",
            gap: "14px",
            zIndex: 99998,
            fontFamily: "'Inter', -apple-system, sans-serif",
            fontSize: "13px",
            border: "1px solid #334155",
            animation: "fadeIn 0.2s ease-out",
          }}
        >
          {toast.copied ? (
            <span
              style={{
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                backgroundColor: "#059669",
                color: "#FFFFFF",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "12px",
                fontWeight: 700,
              }}
            >
              ✓
            </span>
          ) : (
            <span
              style={{
                width: "22px",
                height: "22px",
                borderRadius: "50%",
                backgroundColor: "#D97706",
                color: "#FFFFFF",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "12px",
                fontWeight: 700,
              }}
            >
              📷
            </span>
          )}

          <div>
            <div style={{ fontWeight: 600 }}>
              {toast.copied
                ? "Academic Screenshot Copied to Clipboard!"
                : "Academic Screenshot Captured"}
            </div>
            <div style={{ fontSize: "11px", color: "#94A3B8", marginTop: "2px" }}>
              {toast.copied
                ? `PNG image with metadata seal ready to paste (${toast.sizeKb} KB).`
                : toast.error ||
                  "Browser restricted direct clipboard write. Use the download button below."}
            </div>
          </div>

          <div style={{ display: "flex", gap: "8px", marginLeft: "6px" }}>
            {toast.blob && (
              <button
                onClick={() =>
                  toast.blob &&
                  downloadScreenshot(
                    toast.blob,
                    `z-zoa-${activePhaseName.toLowerCase().replace(/\s+/g, "_")}.png`
                  )
                }
                style={{
                  padding: "5px 10px",
                  fontSize: "11px",
                  fontWeight: 600,
                  backgroundColor: "#1E293B",
                  color: "#38BDF8",
                  border: "1px solid #475569",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Download PNG 🡇
              </button>
            )}

            <button
              onClick={() => setToast((prev) => ({ ...prev, visible: false }))}
              style={{
                padding: "5px 8px",
                fontSize: "11px",
                backgroundColor: "transparent",
                color: "#94A3B8",
                border: "none",
                cursor: "pointer",
              }}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* 3. Shortcut Settings Modal */}
      {isSettingsOpen && (
        <div
          className="no-screenshot"
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(15, 23, 42, 0.5)",
            backdropFilter: "blur(2px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 99999,
          }}
          onClick={() => setIsSettingsOpen(false)}
        >
          <div
            style={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #CBD5E1",
              borderRadius: "8px",
              padding: "24px",
              width: "420px",
              boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
              color: "#0F172A",
              fontFamily: "'Inter', -apple-system, sans-serif",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "16px",
                borderBottom: "1px solid #E2E8F0",
                paddingBottom: "10px",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "16px" }}>📷</span>
                <h3
                  style={{
                    fontFamily: "'Newsreader', serif",
                    fontSize: "17px",
                    fontWeight: 600,
                    margin: 0,
                  }}
                >
                  Screenshot Shortcut Settings
                </h3>
              </div>
              <button
                onClick={() => setIsSettingsOpen(false)}
                style={{
                  background: "none",
                  border: "none",
                  fontSize: "16px",
                  color: "#64748B",
                  cursor: "pointer",
                }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: "12px", color: "#64748B", marginBottom: "16px", lineHeight: "1.5" }}>
              Configure the global keyboard shortcut that captures a clean academic white screenshot
              and copies it directly to your clipboard anywhere on the frontend.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "20px" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
                <input
                  type="checkbox"
                  checked={shortcut.ctrlOrMeta}
                  onChange={(e) => saveShortcut({ ...shortcut, ctrlOrMeta: e.target.checked })}
                />
                <span>Include Ctrl / Cmd Key</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
                <input
                  type="checkbox"
                  checked={shortcut.shift}
                  onChange={(e) => saveShortcut({ ...shortcut, shift: e.target.checked })}
                />
                <span>Include Shift Key</span>
              </label>

              <label style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
                <input
                  type="checkbox"
                  checked={shortcut.alt}
                  onChange={(e) => saveShortcut({ ...shortcut, alt: e.target.checked })}
                />
                <span>Include Alt Key</span>
              </label>

              <div style={{ marginTop: "6px" }}>
                <span style={{ fontSize: "12px", fontWeight: 600, color: "#475569", display: "block", marginBottom: "4px" }}>
                  Trigger Key:
                </span>
                <input
                  type="text"
                  maxLength={1}
                  value={shortcut.key.toUpperCase()}
                  onChange={(e) => {
                    const char = e.target.value.toLowerCase().slice(-1);
                    if (char) saveShortcut({ ...shortcut, key: char });
                  }}
                  className="mono"
                  style={{
                    width: "60px",
                    padding: "6px 10px",
                    fontSize: "14px",
                    textAlign: "center",
                    border: "1px solid #CBD5E1",
                    borderRadius: "4px",
                    fontWeight: 700,
                  }}
                />
              </div>
            </div>

            <div
              style={{
                backgroundColor: "#F8FAFC",
                border: "1px solid #E2E8F0",
                borderRadius: "6px",
                padding: "10px 14px",
                marginBottom: "20px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: "12px", color: "#64748B" }}>Current Shortcut:</span>
              <kbd
                className="mono"
                style={{
                  backgroundColor: "#FFFFFF",
                  border: "1px solid #CBD5E1",
                  borderRadius: "4px",
                  padding: "4px 8px",
                  fontSize: "12px",
                  fontWeight: 600,
                  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                }}
              >
                {shortcutDisplay}
              </kbd>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <button
                onClick={() => saveShortcut(DEFAULT_SHORTCUT)}
                style={{
                  padding: "6px 12px",
                  fontSize: "11px",
                  backgroundColor: "#FFFFFF",
                  border: "1px solid #CBD5E1",
                  borderRadius: "4px",
                  color: "#64748B",
                  cursor: "pointer",
                }}
              >
                Reset Default
              </button>

              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  onClick={() => {
                    setIsSettingsOpen(false);
                    setTimeout(() => executeCapture(), 150);
                  }}
                  style={{
                    padding: "6px 14px",
                    fontSize: "12px",
                    fontWeight: 600,
                    backgroundColor: "#0F172A",
                    color: "#FFFFFF",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Test Capture Now
                </button>
                <button
                  onClick={() => setIsSettingsOpen(false)}
                  style={{
                    padding: "6px 14px",
                    fontSize: "12px",
                    fontWeight: 600,
                    backgroundColor: "#2563EB",
                    color: "#FFFFFF",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                  }}
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
