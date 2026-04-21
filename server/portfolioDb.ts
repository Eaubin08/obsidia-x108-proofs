/**
 * portfolioDb.ts — OS4 v37
 * Database helpers for user portfolios (wallets, positions, snapshots).
 * All functions return raw Drizzle rows.
 */
import { getDb } from "./db";
import { wallets, positions, portfolioSnapshots } from "../drizzle/schema";
import { eq, and, desc } from "drizzle-orm";
import type { Wallet, InsertWallet, Position, InsertPosition } from "../drizzle/schema";

// ─── Wallet ────────────────────────────────────────────────────────────────────

export async function getOrCreateWallet(userId: number): Promise<Wallet> {
  const db = await getDb();
  if (!db) throw new Error("Database unavailable");

  const existing = await db
    .select()
    .from(wallets)
    .where(eq(wallets.userId, userId))
    .limit(1);

  if (existing.length > 0) return existing[0];

  // Create default wallet
  await db.insert(wallets).values({
    userId,
    capital: 125000,
    pnl24h: 0,
    pnl24hPct: 0,
    guardBlocks: 0,
    capitalSaved: 0,
    bankBalance: 125000,
    bankLiquidity: 0.82,
  });

  const created = await db
    .select()
    .from(wallets)
    .where(eq(wallets.userId, userId))
    .limit(1);

  return created[0];
}

export async function updateWallet(
  userId: number,
  data: Partial<Omit<InsertWallet, "userId" | "id">>
): Promise<Wallet> {
  const db = await getDb();
  if (!db) throw new Error("Database unavailable");

  await db.update(wallets).set(data).where(eq(wallets.userId, userId));
  const updated = await db
    .select()
    .from(wallets)
    .where(eq(wallets.userId, userId))
    .limit(1);
  return updated[0];
}

// ─── Positions ─────────────────────────────────────────────────────────────────

export async function getUserPositions(userId: number): Promise<Position[]> {
  const db = await getDb();
  if (!db) return [];
  return db.select().from(positions).where(eq(positions.userId, userId));
}

export async function upsertPosition(
  userId: number,
  domain: "trading" | "bank" | "ecom",
  asset: string,
  data: Partial<Omit<InsertPosition, "userId" | "domain" | "asset">>
): Promise<void> {
  const db = await getDb();
  if (!db) return;

  const existing = await db
    .select()
    .from(positions)
    .where(and(eq(positions.userId, userId), eq(positions.domain, domain), eq(positions.asset, asset)))
    .limit(1);

  if (existing.length > 0) {
    await db
      .update(positions)
      .set(data)
      .where(and(eq(positions.userId, userId), eq(positions.domain, domain), eq(positions.asset, asset)));
  } else {
    await db.insert(positions).values({
      userId,
      domain,
      asset,
      quantity: data.quantity ?? 0,
      avgEntryPrice: data.avgEntryPrice ?? 0,
      currentValue: data.currentValue ?? 0,
      unrealizedPnl: data.unrealizedPnl ?? 0,
    });
  }
}

// ─── Snapshots ─────────────────────────────────────────────────────────────────

export async function savePortfolioSnapshot(
  userId: number,
  capital: number,
  pnl: number,
  guardBlocks: number,
  capitalSaved: number,
  domain?: "trading" | "bank" | "ecom",
  scenarioName?: string
): Promise<void> {
  const db = await getDb();
  if (!db) return;
  await db.insert(portfolioSnapshots).values({
    userId,
    capital,
    pnl,
    guardBlocks,
    capitalSaved,
    ...(domain ? { domain } : {}),
    ...(scenarioName ? { scenarioName } : {}),
  });
}

export async function getPortfolioHistory(userId: number, limit = 30) {
  const db = await getDb();
  if (!db) return [];
  return db
    .select()
    .from(portfolioSnapshots)
    .where(eq(portfolioSnapshots.userId, userId))
    .orderBy(desc(portfolioSnapshots.snapshotAt))
    .limit(limit);
}
