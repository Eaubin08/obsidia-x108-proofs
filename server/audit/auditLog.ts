/**
 * Audit Log â€” Append-only immuable
 * 
 * Enregistre chaque dÃ©cision avec :
 * - decision_id, trace_id, ticket_id
 * - domain, verdict
 * - timestamps
 * - evidence refs
 * - hash / chaÃ®nage
 */

import fs from "fs";
import path from "path";
import crypto from "crypto";

export interface AuditLogEntry {
  decision_id: string;
  trace_id: string;
  ticket_id: string | null;
  domain: "trading" | "bank" | "ecom";
  kernel_verdict: "ALLOW" | "HOLD" | "BLOCK";
  consensus_verdict: "ALLOW" | "HOLD" | "BLOCK";
  x108_gate: "ALLOW" | "HOLD" | "BLOCK";
  confidence: number;
  severity: "S0" | "S1" | "S2" | "S3" | "S4";
  reasons: string[];
  evidence_refs: string[];
  created_at: number;
  kernel_at: number;
  consensus_at: number;
  hash: string;
  prev_hash: string;
}

export class AuditLog {
  private logFile: string;
  private entries: AuditLogEntry[] = [];
  private lastHash: string = "0";
  
  constructor(logDir: string = path.join(process.cwd(), "traces", "audit")) {
    this.logFile = path.join(logDir, "audit.jsonl");
    
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    
    this.load();
  }
  
  private load(): void {
    if (!fs.existsSync(this.logFile)) {
      return;
    }
    
    try {
      const content = fs.readFileSync(this.logFile, "utf-8");
      const lines = content.trim().split("\n").filter(l => l);
      
      for (const line of lines) {
        const entry = JSON.parse(line) as AuditLogEntry;
        this.entries.push(entry);
        this.lastHash = entry.hash;
      }
    } catch (err) {
      console.warn("[AuditLog] Failed to load:", err);
    }
  }
  
  public append(
    decision_id: string,
    trace_id: string,
    ticket_id: string | null,
    domain: "trading" | "bank" | "ecom",
    kernel_verdict: "ALLOW" | "HOLD" | "BLOCK",
    consensus_verdict: "ALLOW" | "HOLD" | "BLOCK",
    x108_gate: "ALLOW" | "HOLD" | "BLOCK",
    confidence: number,
    severity: "S0" | "S1" | "S2" | "S3" | "S4",
    reasons: string[],
    evidence_refs: string[],
    created_at: number,
    kernel_at: number,
    consensus_at: number
  ): AuditLogEntry {
    const recordData = {
      decision_id,
      trace_id,
      ticket_id,
      domain,
      kernel_verdict,
      consensus_verdict,
      x108_gate,
      confidence,
      severity,
      reasons,
      evidence_refs,
      created_at,
      kernel_at,
      consensus_at,
      prev_hash: this.lastHash,
    };
    
    const hash = crypto
      .createHash("sha256")
      .update(JSON.stringify(recordData))
      .digest("hex");
    
    const entry: AuditLogEntry = {
      ...recordData,
      hash,
      prev_hash: this.lastHash,
    };
    
    fs.appendFileSync(this.logFile, JSON.stringify(entry) + "\n");
    this.entries.push(entry);
    this.lastHash = hash;
    
    return entry;
  }
  
  public getByDecisionId(decision_id: string): AuditLogEntry | undefined {
    return this.entries.find(e => e.decision_id === decision_id);
  }
  
  public getByTraceId(trace_id: string): AuditLogEntry | undefined {
    return this.entries.find(e => e.trace_id === trace_id);
  }
  
  public getAll(): AuditLogEntry[] {
    return [...this.entries];
  }
  
  public getByDomain(domain: "trading" | "bank" | "ecom"): AuditLogEntry[] {
    return this.entries.filter(e => e.domain === domain);
  }
  
  public validateChain(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    let prevHash = "0";
    for (let i = 0; i < this.entries.length; i++) {
      const entry = this.entries[i];
      
      if (entry.prev_hash !== prevHash) {
        errors.push(`Entry ${i}: prev_hash mismatch`);
      }
      
      const recordData = { ...entry };
      delete (recordData as any).hash;
      const expectedHash = crypto
        .createHash("sha256")
        .update(JSON.stringify(recordData))
        .digest("hex");
      
      if (entry.hash !== expectedHash) {
        errors.push(`Entry ${i}: hash mismatch`);
      }
      
      prevHash = entry.hash;
    }
    
    return {
      valid: errors.length === 0,
      errors,
    };
  }
  
  public count(): number {
    return this.entries.length;
  }
  
  public getLastHash(): string {
    return this.lastHash;
  }
}

let globalAuditLog: AuditLog | null = null;

export function getAuditLog(): AuditLog {
  if (!globalAuditLog) {
    globalAuditLog = new AuditLog();
  }
  return globalAuditLog;
}

