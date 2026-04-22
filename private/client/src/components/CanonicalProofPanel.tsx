import React from "react";

export interface ReplayResult {
  status?: "PASS" | "FAIL" | "UNAVAILABLE";
  trace_id?: string;
  available?: boolean;
  reason?: string;
}

export interface VerifyResult {
  valid?: boolean;
  ticket_id?: string;
  reason?: string | null;
}

export interface AttestationResult {
  day?: string;
  status?: "OK" | string;
  ref?: string;
  merkle_root?: string;
  entries?: number;
}

const STATUS_COLOR: Record<string, string> = {
  PASS: "oklch(0.72 0.18 145)",
  OK:   "oklch(0.72 0.18 145)",
  FAIL: "oklch(0.65 0.25 25)",
  UNAVAILABLE: "oklch(0.55 0.05 240)",
};

function short(s?: string | null, n = 20) {
  if (!s) return "—";
  return s.length > n ? s.slice(0, n) + "…" : s;
}

export default function CanonicalProofPanel({
  replay,
  verify,
  attestation,
}: {
  replay?: ReplayResult | null;
  verify?: VerifyResult | null;
  attestation?: AttestationResult | null;
}) {
  if (!replay && !verify && !attestation) return null;

  return (
    <div
      className="rounded border border-white/10 p-4 mb-4"
      style={{ background: "oklch(0.13 0.02 145 / 0.4)" }}
    >
      <div className="text-xs font-mono font-bold mb-3" style={{ color: "oklch(0.72 0.18 145)" }}>
        PREUVES BACKEND — replay / ticket / attestation
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">

        {/* Replay */}
        <div>
          <div className="text-muted-foreground text-[10px] mb-1">Replay trace</div>
          <div
            className="font-bold text-sm"
            style={{ color: STATUS_COLOR[replay?.status ?? ""] ?? "oklch(0.55 0.05 240)" }}
          >
            {replay?.status ?? "—"}
          </div>
          <div className="break-all text-[10px] text-muted-foreground mt-0.5">
            {short(replay?.trace_id, 24)}
          </div>
          {replay?.reason && (
            <div className="text-[9px] text-muted-foreground/60 mt-0.5 italic">{replay.reason}</div>
          )}
        </div>

        {/* Verify ticket */}
        <div>
          <div className="text-muted-foreground text-[10px] mb-1">Verify ticket</div>
          <div
            className="font-bold text-sm"
            style={{
              color: verify?.valid
                ? STATUS_COLOR["PASS"]
                : verify
                ? STATUS_COLOR["FAIL"]
                : "oklch(0.55 0.05 240)",
            }}
          >
            {verify ? (verify.valid ? "VALID" : "INVALID") : "—"}
          </div>
          <div className="break-all text-[10px] text-muted-foreground mt-0.5">
            {short(verify?.ticket_id, 20)}
          </div>
        </div>

        {/* Attestation */}
        <div>
          <div className="text-muted-foreground text-[10px] mb-1">Attestation</div>
          <div
            className="font-bold text-sm"
            style={{ color: STATUS_COLOR[attestation?.status ?? ""] ?? "oklch(0.55 0.05 240)" }}
          >
            {attestation?.status ?? "—"}
          </div>
          <div className="text-[10px] text-muted-foreground mt-0.5">{attestation?.day ?? "—"}</div>
          <div className="break-all text-[10px] text-muted-foreground/60 mt-0.5">
            {short(attestation?.ref, 24)}
          </div>
        </div>

      </div>
    </div>
  );
}
