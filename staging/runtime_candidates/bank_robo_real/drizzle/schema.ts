import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
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

/**
 * Transaction table: stores all processed banking transactions
 */
export const transactions = mysqlTable("transactions", {
  id: int("id").autoincrement().primaryKey(),
  scenarioName: varchar("scenario_name", { length: 128 }).notNull(),
  decision: mysqlEnum("decision", ["AUTORISER", "ANALYSER", "BLOQUER"]).notNull(),
  reason: text("reason").notNull(),
  // Metrics
  ir: varchar("ir", { length: 10 }).notNull(), // Irréversibilité
  ciz: varchar("ciz", { length: 10 }).notNull(), // Conflit Interne
  dts: varchar("dts", { length: 10 }).notNull(), // Pression Temporelle
  tsg: varchar("tsg", { length: 10 }).notNull(), // Tension Globale
  // Ontological tests scores
  timeIsLaw: varchar("time_is_law", { length: 10 }).notNull(),
  absoluteHoldGate: varchar("absolute_hold_gate", { length: 10 }).notNull(),
  zeroToleranceFlag: varchar("zero_tolerance_flag", { length: 10 }).notNull(),
  irreversibilityIndex: varchar("irreversibility_index", { length: 10 }).notNull(),
  conflictZoneIsolation: varchar("conflict_zone_isolation", { length: 10 }).notNull(),
  decisionTimeSensitivity: varchar("decision_time_sensitivity", { length: 10 }).notNull(),
  totalSystemGuard: varchar("total_system_guard", { length: 10 }).notNull(),
  negativeMemoryReflexes: varchar("negative_memory_reflexes", { length: 10 }).notNull(),
  emergentBehaviorWatch: varchar("emergent_behavior_watch", { length: 10 }).notNull(),
  // ROI contribution
  roiContribution: int("roi_contribution").notNull().default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type Transaction = typeof transactions.$inferSelect;
export type InsertTransaction = typeof transactions.$inferInsert;

/**
 * Simulation sessions table: tracks batch simulation runs
 */
export const simulationSessions = mysqlTable("simulation_sessions", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("user_id").references(() => users.id),
  totalTransactions: int("total_transactions").notNull(),
  totalROI: int("total_roi").notNull(),
  authorizeCount: int("authorize_count").notNull(),
  analyzeCount: int("analyze_count").notNull(),
  blockCount: int("block_count").notNull(),
  avgIR: varchar("avg_ir", { length: 10 }).notNull(),
  avgCIZ: varchar("avg_ciz", { length: 10 }).notNull(),
  avgDTS: varchar("avg_dts", { length: 10 }).notNull(),
  avgTSG: varchar("avg_tsg", { length: 10 }).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type SimulationSession = typeof simulationSessions.$inferSelect;
export type InsertSimulationSession = typeof simulationSessions.$inferInsert;