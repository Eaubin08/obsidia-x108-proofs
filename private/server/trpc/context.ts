/**
 * tRPC Context
 * Contexte minimal pour accès aux services
 */

import { CreateExpressContextOptions } from "@trpc/server/adapters/express";

export async function createContext(opts: CreateExpressContextOptions) {
  const { req, res } = opts;
  
  return {
    user: (req as any).user || null,
    req,
    res,
  };
}

export type Context = Awaited<ReturnType<typeof createContext>>;
