import { eq, desc } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import {
  InsertUser,
  users,
  decisionTickets,
  simulationRuns,
  auditLog,
} from "../drizzle/schema";
import type { InsertDecisionTicket, InsertSimulationRun } from "../drizzle/schema";
import { ENV } from "./_core/env";

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

// ─── Users ────────────────────────────────────────────────────────────────────

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }
  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};
    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];
    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };
    textFields.forEach(assignNullable);
    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = "admin";
      updateSet.role = "admin";
    }
    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }
    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }
    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }
  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

// ─── Decision Tickets ─────────────────────────────────────────────────────────

export async function insertDecisionTicket(ticket: InsertDecisionTicket) {
  const db = await getDb();
  if (!db) return null;
  const result = await db.insert(decisionTickets).values(ticket);
  return result;
}

export async function getDecisionTickets(domain?: string, limit = 50) {
  const db = await getDb();
  if (!db) return [];
  if (domain) {
    return db
      .select()
      .from(decisionTickets)
      .where(eq(decisionTickets.domain, domain as "trading" | "bank" | "ecom" | "system"))
      .orderBy(desc(decisionTickets.createdAt))
      .limit(limit);
  }
  return db
    .select()
    .from(decisionTickets)
    .orderBy(desc(decisionTickets.createdAt))
    .limit(limit);
}

export async function getDecisionTicketById(id: number) {
  const db = await getDb();
  if (!db) return null;
  const rows = await db
    .select()
    .from(decisionTickets)
    .where(eq(decisionTickets.id, id))
    .limit(1);
  return rows[0] ?? null;
}

// ─── Simulation Runs ──────────────────────────────────────────────────────────

export async function insertSimulationRun(run: InsertSimulationRun) {
  const db = await getDb();
  if (!db) return null;
  return db.insert(simulationRuns).values(run);
}

export async function getSimulationRuns(domain?: string, limit = 20) {
  const db = await getDb();
  if (!db) return [];
  if (domain) {
    return db
      .select()
      .from(simulationRuns)
      .where(eq(simulationRuns.domain, domain as "trading" | "bank" | "ecom"))
      .orderBy(desc(simulationRuns.createdAt))
      .limit(limit);
  }
  return db
    .select()
    .from(simulationRuns)
    .orderBy(desc(simulationRuns.createdAt))
    .limit(limit);
}

export async function getSimulationRunById(id: number) {
  const db = await getDb();
  if (!db) return null;
  const rows = await db
    .select()
    .from(simulationRuns)
    .where(eq(simulationRuns.id, id))
    .limit(1);
  return rows[0] ?? null;
}

// ─── Audit Log ────────────────────────────────────────────────────────────────

export async function insertAuditEntry(entry: {
  ticketId: number;
  hashPrev: string;
  hashNow: string;
  merkleRoot: string;
  anchorRef?: string;
  payload: unknown;
}) {
  const db = await getDb();
  if (!db) return null;
  return db.insert(auditLog).values({
    ticketId: entry.ticketId,
    hashPrev: entry.hashPrev,
    hashNow: entry.hashNow,
    merkleRoot: entry.merkleRoot,
    anchorRef: entry.anchorRef,
    payload: entry.payload,
  });
}

export async function getAuditLog(limit = 100) {
  const db = await getDb();
  if (!db) return [];
  return db
    .select()
    .from(auditLog)
    .orderBy(desc(auditLog.createdAt))
    .limit(limit);
}

export async function getAuditLogByTicket(ticketId: number) {
  const db = await getDb();
  if (!db) return [];
  return db
    .select()
    .from(auditLog)
    .where(eq(auditLog.ticketId, ticketId))
    .orderBy(desc(auditLog.createdAt));
}
