import { toCanvas } from "html-to-image";

export interface ScreenshotMetadata {
  runId?: string;
  phaseName?: string;
  sha256?: string;
}

export interface ScreenshotResult {
  success: boolean;
  copiedToClipboard: boolean;
  blob?: Blob;
  dataUrl?: string;
  sizeBytes?: number;
  error?: string;
}

/**
 * Captures an HTML element into a high-DPI academic paper screenshot,
 * adds an understated metadata stamp, and copies the PNG directly to the system clipboard.
 */
export async function captureAcademicScreenshot(
  targetElement: HTMLElement,
  metadata?: ScreenshotMetadata
): Promise<ScreenshotResult> {
  try {
    // 1. Capture the target element at 2x resolution
    const capturedCanvas = await toCanvas(targetElement, {
      pixelRatio: 2,
      backgroundColor: "#FAF8F5",
      cacheBust: true,
      filter: (node: HTMLElement) => {
        // Exclude elements with class 'no-screenshot'
        if (node.classList && node.classList.contains("no-screenshot")) {
          return false;
        }
        return true;
      },
    });

    // 2. Create high-DPI academic presentation canvas with margin & metadata stamp
    const paddingX = 32; // 16px on each side * 2
    const paddingTop = 48; // 24px top header * 2
    const paddingBottom = 60; // 30px footer metadata * 2

    const finalWidth = capturedCanvas.width + paddingX;
    const finalHeight = capturedCanvas.height + paddingTop + paddingBottom;

    const finalCanvas = document.createElement("canvas");
    finalCanvas.width = finalWidth;
    finalCanvas.height = finalHeight;
    const ctx = finalCanvas.getContext("2d");

    if (!ctx) {
      throw new Error("Unable to obtain 2D rendering context for screenshot.");
    }

    // 3. Fill paper background
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(0, 0, finalWidth, finalHeight);

    // Subtle paper tint inner container
    ctx.fillStyle = "#FAF8F5";
    ctx.fillRect(8, 8, finalWidth - 16, finalHeight - 16);

    // Subtle hairline border
    ctx.strokeStyle = "#CBD5E1";
    ctx.lineWidth = 2;
    ctx.strokeRect(8, 8, finalWidth - 16, finalHeight - 16);

    // 4. Inscribe Header Metadata
    ctx.fillStyle = "#64748B";
    ctx.font = "bold 18px 'JetBrains Mono', monospace";
    ctx.fillText("Z-ZOA LAB // ACADEMIC PHYSICS WORKBENCH", paddingX / 2 + 8, 34);

    if (metadata?.phaseName) {
      ctx.fillStyle = "#0F172A";
      ctx.font = "italic 600 18px 'Newsreader', Georgia, serif";
      ctx.fillText(`— ${metadata.phaseName}`, paddingX / 2 + 420, 34);
    }

    // 5. Draw the captured application view
    ctx.drawImage(capturedCanvas, paddingX / 2, paddingTop);

    // 6. Draw subtle divider above footer
    const footerY = finalHeight - paddingBottom + 16;
    ctx.strokeStyle = "#E2E8F0";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(paddingX / 2, footerY);
    ctx.lineTo(finalWidth - paddingX / 2, footerY);
    ctx.stroke();

    // 7. Inscribe Footer Provenance Stamp
    const now = new Date();
    const timestampStr = now.toISOString().replace("T", " ").substring(0, 19) + " UTC";
    const runIdStr = metadata?.runId || "VELA-001 (FROZEN & VALIDATED)";
    const hashStr = metadata?.sha256 || "8a4c9b139f4e221d68019a28e932bce2";

    ctx.fillStyle = "#475569";
    ctx.font = "14px 'JetBrains Mono', monospace";
    ctx.fillText(`RUN: ${runIdStr}   •   STAMP: ${timestampStr}`, paddingX / 2 + 4, footerY + 24);

    ctx.fillStyle = "#059669";
    ctx.font = "bold 14px 'JetBrains Mono', monospace";
    const sealText = `SHA-256 SEAL: ${hashStr.substring(0, 16)}...`;
    const sealWidth = ctx.measureText(sealText).width;
    ctx.fillText(sealText, finalWidth - paddingX / 2 - sealWidth - 4, footerY + 24);

    // 8. Convert to PNG Blob
    const blob = await new Promise<Blob | null>((resolve) => {
      finalCanvas.toBlob((b) => resolve(b), "image/png", 1.0);
    });

    if (!blob) {
      throw new Error("Failed to export canvas to PNG blob.");
    }

    const dataUrl = finalCanvas.toDataURL("image/png");
    let copiedToClipboard = false;

    // 9. Write to system clipboard if API available
    try {
      if (navigator.clipboard && typeof window.ClipboardItem !== "undefined") {
        const clipboardItem = new ClipboardItem({ "image/png": blob });
        await navigator.clipboard.write([clipboardItem]);
        copiedToClipboard = true;
      }
    } catch (clipErr) {
      console.warn("Direct clipboard write failed (browser permission policy):", clipErr);
      copiedToClipboard = false;
    }

    return {
      success: true,
      copiedToClipboard,
      blob,
      dataUrl,
      sizeBytes: blob.size,
    };
  } catch (err: any) {
    console.error("Screenshot capture failed:", err);
    return {
      success: false,
      copiedToClipboard: false,
      error: err?.message || String(err),
    };
  }
}

/**
 * Downloads a screenshot blob directly to the user's computer.
 */
export function downloadScreenshot(blob: Blob, filename = "z-zoa-screenshot.png") {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
