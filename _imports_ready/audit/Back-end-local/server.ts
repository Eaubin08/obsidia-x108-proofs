import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import fs from "fs";
import crypto from "crypto";

// --- Merkle Tree Implementation ---
class MerkleTree {
  leaves: string[];
  layers: string[][];

  constructor(leaves: string[]) {
    this.leaves = leaves.map(l => this.hash(l));
    this.layers = [this.leaves];
    this.createHashes(this.leaves);
  }

  hash(data: string): string {
    return crypto.createHash("sha256").update(data).digest("hex");
  }

  createHashes(nodes: string[]) {
    if (nodes.length <= 1) return;
    const layer: string[] = [];
    for (let i = 0; i < nodes.length; i += 2) {
      const left = nodes[i];
      const right = nodes[i + 1] || left;
      layer.push(this.hash(left + right));
    }
    this.layers.push(layer);
    this.createHashes(layer);
  }

  getRoot(): string {
    return this.layers[this.layers.length - 1][0] || "";
  }

  getProof(index: number): string[] {
    const proof: string[] = [];
    let layerIndex = index;
    for (let i = 0; i < this.layers.length - 1; i++) {
      const layer = this.layers[i];
      const isRightNode = layerIndex % 2;
      const pairIndex = isRightNode ? layerIndex - 1 : layerIndex + 1;
      if (pairIndex < layer.length) {
        proof.push(layer[pairIndex]);
      } else {
        proof.push(layer[layerIndex]);
      }
      layerIndex = Math.floor(layerIndex / 2);
    }
    return proof;
  }
}

// --- System Engine ---
interface DecisionTicket {
  id: string;
  verdict: "BLOCK" | "HOLD" | "ALLOW";
  risk: number;
  uncertainty: number;
  timestamp: number;
  signature_kernel: string;
}

const auditLog: DecisionTicket[] = [];

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok" });
  });

  app.get("/api/explorer", (req, res) => {
    const rootDir = process.cwd();
    
    interface FileNode {
      name: string;
      path: string;
      type: "directory" | "file";
      children?: FileNode[];
    }

    const getFiles = (dir: string): FileNode[] => {
      const items = fs.readdirSync(dir);
      return items
        .filter(item => !item.startsWith('.') && item !== 'node_modules' && item !== 'dist')
        .map((item) => {
          const fullPath = path.join(dir, item);
          const relativePath = path.relative(rootDir, fullPath);
          const stats = fs.statSync(fullPath);
          if (stats.isDirectory()) {
            return {
              name: item,
              path: relativePath,
              type: "directory",
              children: getFiles(fullPath),
            };
          }
          return {
            name: item,
            path: relativePath,
            type: "file",
          };
        });
    };

    res.json(getFiles(rootDir));
  });

  app.get("/api/system", (req, res) => {
    // Mock system tree
    const systemTree = [
      {
        name: "OS0 KERNEL",
        path: "system/os0_kernel",
        type: "directory",
        children: [
          { name: "core.sys", path: "system/os0_kernel/core.sys", type: "file" },
          { name: "memory.sys", path: "system/os0_kernel/memory.sys", type: "file" },
        ],
      },
      {
        name: "OS1 REFLEX",
        path: "system/os1_reflex",
        type: "directory",
        children: [
          { name: "signal.sys", path: "system/os1_reflex/signal.sys", type: "file" },
          { name: "response.sys", path: "system/os1_reflex/response.sys", type: "file" },
        ],
      },
      {
        name: "OS2 QUANTUM",
        path: "system/os2_quantum",
        type: "directory",
        children: [
          { name: "entanglement.sys", path: "system/os2_quantum/entanglement.sys", type: "file" },
          { name: "superposition.sys", path: "system/os2_quantum/superposition.sys", type: "file" },
        ],
      },
      {
        name: "OS3 WORLD",
        path: "system/os3_world",
        type: "directory",
        children: [
          { name: "physics.sys", path: "system/os3_world/physics.sys", type: "file" },
          { name: "interaction.sys", path: "system/os3_world/interaction.sys", type: "file" },
        ],
      },
      {
        name: "OS4 PROOF",
        path: "system/os4_proof",
        type: "directory",
        children: [
          { name: "logic.sys", path: "system/os4_proof/logic.sys", type: "file" },
          { name: "verification.sys", path: "system/os4_proof/verification.sys", type: "file" },
        ],
      },
      {
        name: "OS5 FOUNDATIONS",
        path: "system/os5_foundations",
        type: "directory",
        children: [
          { name: "base.sys", path: "system/os5_foundations/base.sys", type: "file" },
          { name: "structure.sys", path: "system/os5_foundations/structure.sys", type: "file" },
        ],
      },
    ];
    res.json(systemTree);
  });

  app.get("/api/file", (req, res) => {
    const filePath = req.query.path as string;
    if (!filePath) {
      return res.status(400).json({ error: "Path is required" });
    }

    const fullPath = path.join(process.cwd(), filePath);
    if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
      return res.status(404).json({ error: "File not found" });
    }

    const content = fs.readFileSync(fullPath, "utf-8");
    res.json({ content });
  });

  app.get("/api/status", (req, res) => {
    const tree = new MerkleTree(auditLog.map(t => JSON.stringify(t)));
    res.json({
      kernel: "ACTIVE",
      reflex: "NOMINAL",
      quantum: "STABLE",
      world: "SYNCED",
      merkle_root: tree.getRoot(),
      audit_count: auditLog.length
    });
  });

  app.post("/api/ingest", (req, res) => {
    const { risk, uncertainty } = req.body;
    
    let verdict: "BLOCK" | "HOLD" | "ALLOW" = "ALLOW";
    if (risk > 0.8) verdict = "BLOCK";
    else if (uncertainty > 0.5) verdict = "HOLD";

    const ticket: DecisionTicket = {
      id: `TKT-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      verdict,
      risk,
      uncertainty,
      timestamp: Date.now(),
      signature_kernel: crypto.randomBytes(16).toString("hex")
    };

    auditLog.push(ticket);
    
    const tree = new MerkleTree(auditLog.map(t => JSON.stringify(t)));
    const proof = tree.getProof(auditLog.length - 1);

    res.json({
      ticket,
      merkle_root: tree.getRoot(),
      proof
    });
  });

  app.get("/api/audit", (req, res) => {
    const tree = new MerkleTree(auditLog.map(t => JSON.stringify(t)));
    res.json({
      logs: auditLog,
      merkle_root: tree.getRoot()
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
