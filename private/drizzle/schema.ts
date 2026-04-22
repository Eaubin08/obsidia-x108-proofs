import {
  bigint,
  float,
  int,
  json,
  mysqlEnum,
  mysqlTable,
  text,
  timestamp,
  varchar,
} from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// ─── Decision Tickets (Guard X-108) ───────────────────────────────────────────
export const decisionTickets = mysqlTable("decision_tickets", {
  id: int("id").autoincrement().primaryKey(),
  intentId: varchar("intentId", { length: 64 }).notNull(),
  domain: mysqlEnum("domain", ["trading", "bank", "ecom", "system"]).notNull(),
  decision: mysqlEnum("decision", ["ALLOW", "HOLD", "BLOCK"]).notNull(),
  reasons: json("reasons").notNull(), // string[]
  thresholds: json("thresholds").notNull(), // Record<string, number>
  x108: json("x108").notNull(), // { tau: number; elapsed: number; irr: boolean; gate_active: boolean }
  auditTrail: json("auditTrail").notNull(), // { hash_prev, hash_now, merkle_root, anchor_ref, ts_utc }
  replayRef: varchar("replayRef", { length: 128 }), // seed:step
  userId: int("userId"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type DecisionTicket = typeof decisionTickets.$inferSelect;
export type InsertDecisionTicket = typeof decisionTickets.$inferInsert;

// ─── Simulation Runs ──────────────────────────────────────────────────────────
export const simulationRuns = mysqlTable("simulation_runs", {
  id: int("id").autoincrement().primaryKey(),
  domain: mysqlEnum("domain", ["trading", "bank", "ecom"]).notNull(),
  seed: bigint("seed", { mode: "number" }).notNull(),
  steps: int("steps").notNull(),
  params: json("params").notNull(),
  stateHash: varchar("stateHash", { length: 64 }).notNull(),
  merkleRoot: varchar("merkleRoot", { length: 64 }).notNull(),
  userId: int("userId"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type SimulationRun = typeof simulationRuns.$inferSelect;
export type InsertSimulationRun = typeof simulationRuns.$inferInsert;

// ─── Audit Log (hash chain) ───────────────────────────────────────────────────
export const auditLog = mysqlTable("audit_log", {
  id: int("id").autoincrement().primaryKey(),
  ticketId: int("ticketId").notNull(),
  hashPrev: varchar("hashPrev", { length: 64 }).notNull(),
  hashNow: varchar("hashNow", { length: 64 }).notNull(),
  merkleRoot: varchar("merkleRoot", { length: 64 }).notNull(),
  anchorRef: varchar("anchorRef", { length: 128 }),
  payload: json("payload").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type AuditLogEntry = typeof auditLog.$inferSelect;

// ─── Portfolios (OAuth-linked) ────────────────────────────────────────────────
export const wallets = mysqlTable("wallets", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull().unique(),
  capital: float("capital").notNull().default(125000),
  pnl24h: float("pnl24h").notNull().default(0),
  pnl24hPct: float("pnl24hPct").notNull().default(0),
  guardBlocks: int("guardBlocks").notNull().default(0),
  capitalSaved: float("capitalSaved").notNull().default(0),
  bankBalance: float("bankBalance").notNull().default(125000),
  bankLiquidity: float("bankLiquidity").notNull().default(0.82),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});
export type Wallet = typeof wallets.$inferSelect;
export type InsertWallet = typeof wallets.$inferInsert;

export const positions = mysqlTable("positions", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  domain: mysqlEnum("domain", ["trading", "bank", "ecom"]).notNull(),
  asset: varchar("asset", { length: 32 }).notNull(),
  quantity: float("quantity").notNull().default(0),
  avgEntryPrice: float("avgEntryPrice").notNull().default(0),
  currentValue: float("currentValue").notNull().default(0),
  unrealizedPnl: float("unrealizedPnl").notNull().default(0),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});
export type Position = typeof positions.$inferSelect;
export type InsertPosition = typeof positions.$inferInsert;

export const portfolioSnapshots = mysqlTable("portfolio_snapshots", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),
  capital: float("capital").notNull(),
  pnl: float("pnl").notNull(),
  guardBlocks: int("guardBlocks").notNull(),
  capitalSaved: float("capitalSaved").notNull(),
  domain: mysqlEnum("domain", ["trading", "bank", "ecom"]).default("trading"),
  scenarioName: varchar("scenarioName", { length: 128 }),
  snapshotAt: timestamp("snapshotAt").defaultNow().notNull(),
});
export type PortfolioSnapshot = typeof portfolioSnapshots.$inferSelect;

// ─── Prediction History ─────────────────────────────────────────────────────────
export const predictionHistory = mysqlTable("prediction_history", {
  id: int("id").autoincrement().primaryKey(),
  predictionId: varchar("predictionId", { length: 64 }).notNull(),
  title: varchar("title", { length: 128 }).notNull(),
  domain: mysqlEnum("domain", ["trading", "bank", "ecom"]).notNull(),
  level: mysqlEnum("level", ["high", "medium", "low"]).notNull(),
  probability: float("probability").notNull(),
  window: varchar("window", { length: 32 }).notNull(),
  outcome: mysqlEnum("outcome", ["confirmed", "refuted", "pending"]).notNull().default("pending"),
  btcVolatility: float("btcVolatility"),
  bankRiskScore: float("bankRiskScore"),
  ecomDemandIndex: float("ecomDemandIndex"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  resolvedAt: timestamp("resolvedAt"),
});
export type PredictionHistoryRow = typeof predictionHistory.$inferSelect;

// ─── Prediction Snapshots (24h probability trend) ────────────────────────────────────────────────────────
export const predictionSnapshots = mysqlTable("prediction_snapshots", {
  id: int("id").autoincrement().primaryKey(),
  domain: mysqlEnum("domain", ["trading", "bank", "ecom"]).notNull(),
  predictionId: varchar("predictionId", { length: 64 }).notNull(),
  probability: int("probability").notNull(), // 0-100
  btcVolatility: float("btcVolatility"),
  bankRiskScore: float("bankRiskScore"),
  ecomDemandIndex: float("ecomDemandIndex"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});
export type PredictionSnapshot = typeof predictionSnapshots.$inferSelect;
