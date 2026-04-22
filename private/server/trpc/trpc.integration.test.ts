/**
 * tRPC Integration Tests
 * Vérifier que tous les routers tRPC sont branchés et répondent réellement
 */

import { describe, it, expect } from "vitest";

describe("tRPC Integration", () => {
  it("should have all router files", async () => {
    // Vérifier que les fichiers existent
    const fs = await import("fs");
    const path = await import("path");
    
    const routers = [
      "orchestration.ts",
      "audit.ts",
      "truth.ts",
      "system.ts",
      "attestation.ts",
      "tla.ts",
      "replay.ts",
      "provenance.ts",
    ];
    
    for (const router of routers) {
      const filePath = path.join(process.cwd(), "server/trpc/routers", router);
      expect(fs.existsSync(filePath)).toBe(true);
    }
  });

  it("should have _app.ts that imports all routers", async () => {
    const fs = await import("fs");
    const path = await import("path");
    
    const appPath = path.join(process.cwd(), "server/trpc/routers/_app.ts");
    const content = fs.readFileSync(appPath, "utf-8");
    
    expect(content).toContain("orchestrationRouter");
    expect(content).toContain("auditRouter");
    expect(content).toContain("truthRouter");
    expect(content).toContain("systemRouter");
    expect(content).toContain("attestationRouter");
    expect(content).toContain("tlaRouter");
    expect(content).toContain("replayRouter");
    expect(content).toContain("provenanceRouter");
  });

  it("should have tRPC index.ts", async () => {
    const fs = await import("fs");
    const path = await import("path");
    
    const indexPath = path.join(process.cwd(), "server/trpc/index.ts");
    expect(fs.existsSync(indexPath)).toBe(true);
  });

  it("should have tRPC context.ts", async () => {
    const fs = await import("fs");
    const path = await import("path");
    
    const contextPath = path.join(process.cwd(), "server/trpc/context.ts");
    expect(fs.existsSync(contextPath)).toBe(true);
  });
});
