/**
 * System Router — Health Check Réel
 * Détection dynamique + fallback secondaire
 * Statuts honnêtes : available / incomplete / missing
 */

import { publicProcedure, router } from "../index";
import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";

type ComponentStatus = "available" | "incomplete" | "missing" | "failed";

interface HealthReport {
  node: boolean;
  python: boolean;
  sigma_repo: ComponentStatus;
  proof_repo: ComponentStatus;
  verify_all: ComponentStatus;
  verify_merkle: ComponentStatus;
  rfc3161: ComponentStatus;
  tla: ComponentStatus;
  tlc: ComponentStatus;
  tsa_config: ComponentStatus;
  build_ready: boolean;
  tests_ready: boolean;
  timestamp: string;
}

function findRepo(repoName: string): string | null {
  // Détection dynamique : chercher dans les chemins courants
  const searchPaths = [
    process.cwd(),
    process.env.HOME,
    "/tmp",
    "/home/ubuntu",
    "/home/ubuntu/obsidia-workspace",
  ];
  
  for (const searchPath of searchPaths) {
    if (!searchPath) continue;
    
    try {
      const entries = fs.readdirSync(searchPath);
      for (const entry of entries) {
        if (entry.includes(repoName)) {
          const fullPath = path.join(searchPath, entry);
          if (fs.statSync(fullPath).isDirectory()) {
            return fullPath;
          }
        }
      }
    } catch {
      // Continuer
    }
  }
  
  // Fallback secondaire : chemins absolus connus
  const fallbacks: Record<string, string> = {
    "obsidia-engine-proof-core": "/home/ubuntu/obsidia-engine-proof-core",
    "obsidia-x108-proofs": "/home/ubuntu/obsidia-x108-proofs",
    "sigma": "/tmp/FINAL_SOURCES/obsidia-engine-proof-core-main(1)/obsidia-engine-proof-core-main/agents",
  };
  
  return fallbacks[repoName] || null;
}

function checkNodeHealth(): boolean {
  try {
    return process.version !== undefined;
  } catch {
    return false;
  }
}

function checkPythonHealth(): boolean {
  try {
    execSync("python3 --version", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function checkSigmaRepo(): ComponentStatus {
  // Chercher obsidia-engine-proof-core
  const repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) return "missing";
  
  const sigmaPath = path.join(repoPath, "agents", "obsidia_sigma_v130.py");
  if (fs.existsSync(sigmaPath)) return "available";
  
  return "incomplete";
}

function checkProofRepo(): ComponentStatus {
  // Chercher obsidia-engine-proof-core ou obsidia-x108-proofs
  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";
  
  const verifyPath = path.join(repoPath, "proofs");
  if (fs.existsSync(verifyPath)) return "available";
  
  return "incomplete";
}

function checkVerifyAll(): ComponentStatus {
  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";
  
  const verifyPath = path.join(repoPath, "proofs", "verify_all.py");
  if (fs.existsSync(verifyPath)) return "available";
  
  return "incomplete";
}

function checkVerifyMerkle(): ComponentStatus {
  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";
  
  const merkleePath = path.join(repoPath, "proofs", "verify_merkle.py");
  if (fs.existsSync(merkleePath)) return "available";
  
  return "incomplete";
}

function checkRFC3161(): ComponentStatus {
  // Vérifier si config TSA existe
  const configPath = path.join(process.cwd(), "server", "config", "rfc3161.ts");
  if (!fs.existsSync(configPath)) return "missing";
  
  // Vérifier si openssl est disponible
  try {
    execSync("openssl version", { stdio: "pipe" });
    return "incomplete"; // openssl disponible mais pas de TSA local
  } catch {
    return "incomplete";
  }
}

function checkTLA(): ComponentStatus {
  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";
  
  const tlaPath = path.join(repoPath, "proofs", "tla");
  if (fs.existsSync(tlaPath)) return "incomplete"; // TLA présent mais TLC peut ne pas être disponible
  
  return "missing";
}

function checkTLC(): ComponentStatus {
  try {
    execSync("tlc -version", { stdio: "pipe" });
    return "available";
  } catch {
    return "missing";
  }
}

function checkTSAConfig(): ComponentStatus {
  const configPath = path.join(process.cwd(), "server", "config", "rfc3161.ts");
  if (fs.existsSync(configPath)) {
    try {
      const content = fs.readFileSync(configPath, "utf-8");
      if (content.includes("TSA_URL")) return "incomplete";
    } catch {
      return "incomplete";
    }
  }
  return "missing";
}

function checkBuildReady(): boolean {
  try {
    const distPath = path.join(process.cwd(), "dist");
    return fs.existsSync(distPath);
  } catch {
    return false;
  }
}

function checkTestsReady(): boolean {
  try {
    const testPath = path.join(process.cwd(), "server", "orchestration", "orchestrationReal.test.ts");
    return fs.existsSync(testPath);
  } catch {
    return false;
  }
}

export const systemRouter = router({
  health: publicProcedure.query((): HealthReport => {
    return {
      node: checkNodeHealth(),
      python: checkPythonHealth(),
      sigma_repo: checkSigmaRepo(),
      proof_repo: checkProofRepo(),
      verify_all: checkVerifyAll(),
      verify_merkle: checkVerifyMerkle(),
      rfc3161: checkRFC3161(),
      tla: checkTLA(),
      tlc: checkTLC(),
      tsa_config: checkTSAConfig(),
      build_ready: checkBuildReady(),
      tests_ready: checkTestsReady(),
      timestamp: new Date().toISOString(),
    };
  }),
});
