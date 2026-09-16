import { useState, useEffect } from "react";
import { ThreeCosmicLab } from "./components/ThreeCosmicLab";
import { WhiteCalculationRoom } from "./components/WhiteCalculationRoom";
import {
  Phase1BigPicture,
  Phase2Datasets,
  Phase5LeakageGuard,
  Phase6ScienceChecks,
  Phase7ReconstructionEngine,
  Phase8FreezeScore,
  Phase9HybridIntegrity,
  Phase10PaperFactory,
} from "./components/PhaseViews";
import { ScreenshotManager, triggerAppScreenshot } from "./components/ScreenshotManager";

interface CatalogMeta {
  dataset_id: string;
  survey: string;
  release: string;
  role: string;
  file_path: string;
  sha256: string;
  row_count: number;
  citation: string;
  status: string;
}

interface AnchorReceiptData {
  project: string;
  network: string;
  network_id: number;
  run_id: string;
  stage: string;
  manifest_sha256: string;
  anchor_payload_sha256: string;
  git_commit: string;
  account: string;
  tx_hash: string;
  ledger_index: number;
  validated: boolean;
  transaction_result: string;
  previous_tx_hash: string | null;
  submitted_at: string;
  validated_at: string;
  disclaimer: string;
}

interface VerificationResultData {
  run_id: string;
  stage: string;
  status: string;
  local_hash: string;
  ledger_hash?: string;
  tx_hash?: string;
  ledger_index?: number;
  validated: boolean;
  transaction_result?: string;
  previous_tx_hash?: string;
  audit_report: string;
  checks: Record<string, boolean>;
  errors: string[];
}

export function App() {
  // Navigation State: 1 to 10 matching the 10 sheets
  const [activePhase, setActivePhase] = useState<number>(3); // Default to White Calculation Room
  const [threeLabMode, setThreeLabMode] = useState<
    "SURVEY_BASE" | "PREDICTION" | "HOLDOUT" | "HYBRID" | "DIFFERENTIAL"
  >("DIFFERENTIAL");

  const handleOpen3DLab = (
    mode?: "SURVEY_BASE" | "PREDICTION" | "HOLDOUT" | "HYBRID" | "DIFFERENTIAL"
  ) => {
    if (mode) setThreeLabMode(mode);
    setActivePhase(4);
  };

  // Catalogs & Datasets
  const [catalogs, setCatalogs] = useState<CatalogMeta[]>([]);

  // Experiment run state
  const [runManifest, setRunManifest] = useState<any | null>(null);
  const [runLoading, setRunLoading] = useState<boolean>(false);

  // Research anchor state
  const [anchorReceipt, setAnchorReceipt] = useState<AnchorReceiptData | null>(null);
  const [anchorLoading, setAnchorLoading] = useState<boolean>(false);
  const [verifyResult, setVerifyResult] = useState<VerificationResultData | null>(null);
  const [verifyLoading, setVerifyLoading] = useState<boolean>(false);

  const fetchCatalogs = async () => {
    try {
      const res = await fetch("/catalogs/");
      if (res.ok) {
        const data = await res.json();
        setCatalogs(data);
      }
    } catch (e) {
      console.error("Failed to load catalogs:", e);
    }
  };

  useEffect(() => {
    fetchCatalogs();
  }, []);

  const handleExecuteRun = async () => {
    setRunLoading(true);
    try {
      const res = await fetch("/experiments/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          run_id: "RUN_0001",
          experiment_name: "Vela holdout baseline",
          cosmology_name: "CF4_NOMINAL",
          dataset_ids: ["cf4_sample"],
          execution_mode: "TRAINING",
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setRunManifest(data.manifest);
        try {
          const recRes = await fetch(`/ledger/receipt/${data.run_id || "RUN_0001"}`);
          if (recRes.ok) {
            const recData = await recRes.json();
            setAnchorReceipt(recData);
          } else {
            setAnchorReceipt(null);
          }
        } catch {
          setAnchorReceipt(null);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setRunLoading(false);
    }
  };

  const handleAnchorRun = async (runId: string) => {
    setAnchorLoading(true);
    try {
      const res = await fetch("/ledger/anchor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, stage: "PREDICTION_FROZEN" }),
      });
      const data = await res.json();
      if (res.ok) {
        setAnchorReceipt(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAnchorLoading(false);
    }
  };

  const handleVerifyAnchor = async (runId: string) => {
    setVerifyLoading(true);
    try {
      const res = await fetch("/ledger/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, stage: "PREDICTION_FROZEN" }),
      });
      const data = await res.json();
      if (res.ok) {
        setVerifyResult(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setVerifyLoading(false);
    }
  };

  const phases = [
    { num: 1, title: "Big Picture" },
    { num: 2, title: "Datasets" },
    { num: 3, title: "Calculation Room" },
    { num: 4, title: "3D Lab" },
    { num: 5, title: "Leakage Guard" },
    { num: 6, title: "Science Checks" },
    { num: 7, title: "Reconstruction" },
    { num: 8, title: "Freeze & Score" },
    { num: 9, title: "Hybrid & XRPL" },
    { num: 10, title: "Paper Factory" },
  ];

  return (
    <div
      id="z-zoa-app-container"
      style={{
        maxWidth: "1400px",
        margin: "0 auto",
        padding: "20px 24px",
        color: "#111827",
        minHeight: "100vh",
        backgroundColor: "#FAF8F5",
      }}
    >
      {/* Top Header */}
      <header style={{ borderBottom: "1px solid #E2E8F0", paddingBottom: "16px", marginBottom: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <h1 style={{ fontSize: "20px", fontWeight: 800, letterSpacing: "-0.02em", margin: 0, color: "#0F172A" }}>
                Z-ZOA SCIENTIFIC WORKBENCH &amp; 3D LAB
              </h1>
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  backgroundColor: "#EFF6FF",
                  color: "#1D4ED8",
                  padding: "2px 8px",
                  borderRadius: "4px",
                  border: "1px solid #BFDBFE",
                }}
              >
                RESEARCH STUDY &bull; 10-PHASE PLAN
              </span>
            </div>
            <p style={{ fontSize: "12px", color: "#64748B", margin: "4px 0 0 0" }}>
              Out-of-Sample Cosmic Web Reconstruction across the Zone of Avoidance &bull; Cryptographic Holdout Validation Engine
            </p>
          </div>

          {/* System Status Badges & Screenshot Shortcut */}
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              onClick={triggerAppScreenshot}
              title="Capture White Screenshot to System Clipboard (Ctrl+Shift+S)"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                fontSize: "11px",
                fontWeight: 600,
                padding: "4px 10px",
                backgroundColor: "#FFFFFF",
                color: "#0F172A",
                border: "1px solid #CBD5E1",
                borderRadius: "4px",
                cursor: "pointer",
                boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
              }}
            >
              <span>📷</span>
              <span>Screenshot</span>
              <kbd
                className="mono"
                style={{
                  fontSize: "9px",
                  backgroundColor: "#F1F5F9",
                  padding: "1px 5px",
                  borderRadius: "3px",
                  color: "#64748B",
                  border: "1px solid #E2E8F0",
                }}
              >
                Ctrl+Shift+S
              </kbd>
            </button>

            <span
              className="mono"
              style={{
                fontSize: "11px",
                fontWeight: 600,
                padding: "3px 8px",
                backgroundColor: "#FEF2F2",
                color: "#991B1B",
                border: "1px solid #FCA5A5",
                borderRadius: "4px",
              }}
            >
              HOLDOUT GUARD: ARMED
            </span>

            <span
              className="mono"
              style={{
                fontSize: "11px",
                fontWeight: 600,
                padding: "3px 8px",
                backgroundColor: anchorReceipt ? "#F0FDF4" : "#F8FAFC",
                color: anchorReceipt ? "#166534" : "#64748B",
                border: `1px solid ${anchorReceipt ? "#86EFAC" : "#CBD5E1"}`,
                borderRadius: "4px",
              }}
            >
              {anchorReceipt ? "XRPL: ANCHORED" : "XRPL: TESTNET READY"}
            </span>

            <span
              className="mono"
              style={{
                fontSize: "11px",
                fontWeight: 600,
                padding: "3px 8px",
                backgroundColor: "#FAF5FF",
                color: "#6B21A8",
                border: "1px solid #E9D5FF",
                borderRadius: "4px",
              }}
            >
              COMMIT: df3536e
            </span>
          </div>
        </div>

        {/* 10-Phase Navigation Bar */}
        <nav
          style={{
            display: "flex",
            gap: "6px",
            marginTop: "16px",
            overflowX: "auto",
            paddingBottom: "4px",
          }}
        >
          {phases.map((p) => {
            const isActive = activePhase === p.num;
            return (
              <button
                key={p.num}
                onClick={() => setActivePhase(p.num)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "6px 12px",
                  borderRadius: "6px",
                  fontSize: "12px",
                  fontWeight: isActive ? 700 : 500,
                  backgroundColor: isActive ? "#0F172A" : "#FFFFFF",
                  color: isActive ? "#FFFFFF" : "#475569",
                  border: isActive ? "1px solid #0F172A" : "1px solid #E2E8F0",
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  transition: "all 0.15s ease",
                }}
              >
                <span
                  style={{
                    width: "18px",
                    height: "18px",
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "10px",
                    fontWeight: 700,
                    backgroundColor: isActive ? "#2563EB" : "#F1F5F9",
                    color: isActive ? "#FFFFFF" : "#64748B",
                  }}
                >
                  {p.num}
                </span>
                <span>{p.title}</span>
              </button>
            );
          })}
        </nav>
      </header>

      {/* Main Phase View Router */}
      <main style={{ minHeight: "680px" }}>
        {activePhase === 1 && (
          <Phase1BigPicture onNavigatePhase={(p) => setActivePhase(p)} />
        )}

        {activePhase === 2 && (
          <Phase2Datasets onNavigatePhase={(p) => setActivePhase(p)} />
        )}

        {activePhase === 3 && (
          <WhiteCalculationRoom
            onOpen3DLab={() => setActivePhase(4)}
            catalogs={catalogs}
            onExecuteRun={handleExecuteRun}
            runLoading={runLoading}
            runManifest={runManifest}
            anchorReceipt={anchorReceipt}
            onAnchorRun={handleAnchorRun}
            anchorLoading={anchorLoading}
            onVerifyAnchor={handleVerifyAnchor}
            verifyLoading={verifyLoading}
            verifyResult={verifyResult}
          />
        )}

        {activePhase === 4 && (
          <ThreeCosmicLab
            onNavigateToCalc={() => setActivePhase(3)}
            selectedRunId="VELA-001"
            initialMode={threeLabMode}
          />
        )}

        {activePhase === 5 && (
          <Phase5LeakageGuard onNavigatePhase={(p) => setActivePhase(p)} />
        )}

        {activePhase === 6 && (
          <Phase6ScienceChecks onNavigatePhase={(p) => setActivePhase(p)} />
        )}

        {activePhase === 7 && (
          <Phase7ReconstructionEngine
            onNavigatePhase={(p) => setActivePhase(p)}
            onOpen3DLab={() => handleOpen3DLab("PREDICTION")}
          />
        )}

        {activePhase === 8 && (
          <Phase8FreezeScore onNavigatePhase={(p) => setActivePhase(p)} />
        )}

        {activePhase === 9 && (
          <Phase9HybridIntegrity
            onNavigatePhase={(p) => setActivePhase(p)}
            onOpen3DLab={handleOpen3DLab}
          />
        )}

        {activePhase === 10 && (
          <Phase10PaperFactory onNavigatePhase={(p) => setActivePhase(p)} />
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          marginTop: "32px",
          borderTop: "1px solid #E2E8F0",
          paddingTop: "16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          fontSize: "11px",
          color: "#64748B",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <span style={{ fontWeight: 600, color: "#0F172A" }}>
            Z-ZOA &bull; Zone of Avoidance Research &bull; Made by Zhane
          </span>
          <span style={{ color: "#94A3B8" }}>&bull;</span>
          <span style={{ fontStyle: "italic", fontFamily: "'Newsreader', serif", color: "#475569" }}>
            &ldquo;Same sky. More galaxies. A clearer tomorrow.&rdquo;
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <a
            href="https://github.com/zrt219/z-zoa-lab"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "4px 10px",
              borderRadius: "4px",
              border: "1px solid #CBD5E1",
              backgroundColor: "#FFFFFF",
              color: "#0F172A",
              textDecoration: "none",
              fontSize: "11px",
              fontWeight: 500,
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <span>GitHub</span>
            <span style={{ color: "#64748B" }}>@zrt219 ↗</span>
          </a>
          <a
            href="https://www.linkedin.com/in/zhane-umattr"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "4px 10px",
              borderRadius: "4px",
              border: "1px solid #BAE6FD",
              backgroundColor: "#F0F9FF",
              color: "#0284C7",
              textDecoration: "none",
              fontSize: "11px",
              fontWeight: 500,
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <span>Zhane Grey</span>
            <span style={{ color: "#0369A1" }}>LinkedIn ↗</span>
          </a>
          <a
            href="https://umattr.ca"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "4px 10px",
              borderRadius: "4px",
              border: "1px solid #B88718",
              backgroundColor: "#D4AF37",
              color: "#181818",
              textDecoration: "none",
              fontSize: "11px",
              fontWeight: 600,
              display: "inline-flex",
              alignItems: "center",
              gap: "5px",
              boxShadow: "0 1px 2px rgba(184, 135, 24, 0.2)",
            }}
          >
            <span>UMATTR</span>
            <span style={{ opacity: 0.85, fontWeight: 500 }}>umattr.ca ↗</span>
          </a>
        </div>
      </footer>

      {/* Global Academic Screenshot & Clipboard Manager */}
      <ScreenshotManager
        activePhaseName={phases.find((p) => p.num === activePhase)?.title}
        runId="VELA-001"
        sha256="8a4c9b139f4e221d68019a28e932bce2"
      />
    </div>
  );
}

export default App;
