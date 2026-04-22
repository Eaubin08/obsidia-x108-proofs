/**
 * System Router — Health Check Réel
 * Détection dynamique + fallback secondaire
 * Statuts honnêtes : available / incomplete / missing / failed
 */

import { publicProcedure, router } from "../index";
import { execSync, spawnSync } from "child_process";
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
  const searchPaths = [
    process.cwd(),
    process.env.HOME,
    process.env.USERPROFILE,
    "/tmp",
    "/home/ubuntu",
    "/home/ubuntu/obsidia-workspace",
  ];

  for (const searchPath of searchPaths) {
    if (!searchPath) continue;

    try {
      if (!fs.existsSync(searchPath)) continue;
      const entries = fs.readdirSync(searchPath);
      for (const entry of entries) {
        if (entry.includes(repoName)) {
          const fullPath = path.join(searchPath, entry);
          if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
            return fullPath;
          }
        }
      }
    } catch {
      // continuer
    }
  }

  const fallbacks: Record<string, string> = {
    "obsidia-engine-proof-core": path.join(process.cwd()),
    "obsidia-x108-proofs": path.join(process.cwd()),
    "sigma": path.join(process.cwd(), "agents"),
  };

  const fallback = fallbacks[repoName];
  if (fallback && fs.existsSync(fallback)) return fallback;

  return null;
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
    execSync("py -3 --version", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function checkSigmaRepo(): ComponentStatus {
  const localSigmaPath = path.join(process.cwd(), "agents", "obsidia_sigma_v130.py");
  if (fs.existsSync(localSigmaPath)) return "available";

  const repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) return "missing";

  const sigmaPath = path.join(repoPath, "agents", "obsidia_sigma_v130.py");
  if (fs.existsSync(sigmaPath)) return "available";

  return "incomplete";
}

function checkProofRepo(): ComponentStatus {
  const localProofs = path.join(process.cwd(), "proofs");
  if (fs.existsSync(localProofs)) return "available";

  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";

  const verifyPath = path.join(repoPath, "proofs");
  if (fs.existsSync(verifyPath)) return "available";

  return "incomplete";
}

function checkVerifyAll(): ComponentStatus {
  const localVerify = path.join(process.cwd(), "proofs", "verify_all.py");
  if (fs.existsSync(localVerify)) return "available";

  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";

  const verifyPath = path.join(repoPath, "proofs", "verify_all.py");
  if (fs.existsSync(verifyPath)) return "available";

  return "incomplete";
}

function checkVerifyMerkle(): ComponentStatus {
  const localVerify = path.join(process.cwd(), "proofs", "verify_merkle.py");
  if (fs.existsSync(localVerify)) return "available";

  let repoPath = findRepo("obsidia-engine-proof-core");
  if (!repoPath) repoPath = findRepo("obsidia-x108-proofs");
  if (!repoPath) return "missing";

  const merklePath = path.join(repoPath, "proofs", "verify_merkle.py");
  if (fs.existsSync(merklePath)) return "available";

  return "incomplete";
}

function checkRFC3161(): ComponentStatus {
  const configPath = path.join(process.cwd(), "server", "config", "rfc3161.ts");
  if (!fs.existsSync(configPath)) return "missing";

  try {
    execSync("openssl version", { stdio: "pipe" });
    return "incomplete";
  } catch {
    return "incomplete";
  }
}

function resolveTlaRoot(): string | null {
  const candidates = [
    process.env.OBSIDIA_TLA_ROOT || "",
    path.join(process.cwd(), "proofs", "tla"),
  ];

  for (const p of candidates) {
    if (!p) continue;
    try {
      if (fs.existsSync(p) && fs.statSync(p).isDirectory()) {
        return p;
      }
    } catch {
      // continuer
    }
  }

  return null;
}

function resolveJavaCmd(): string | null {
  try {
    const res = spawnSync("where.exe", ["java"], {
      encoding: "utf-8",
      windowsHide: true,
    });

    if (res.status === 0) {
      const found = (res.stdout || "")
        .split(/\r?\n/)
        .map((s) => s.trim())
        .find(Boolean);

      if (found && fs.existsSync(found)) {
        return found;
      }
    }
  } catch {
    // continuer
  }

  return "java";
}

function resolveTlcJarPath(): string | null {
  const envCmd = process.env.OBSIDIA_TLA_TLC_CMD || "";
  const envJarMatch =
    envCmd.match(/-cp\s+"([^"]+\.jar)"/i) ||
    envCmd.match(/-cp\s+([^\s]+\.jar)/i);

  if (envJarMatch?.[1] && fs.existsSync(envJarMatch[1])) {
    return envJarMatch[1];
  }

  const candidates = [
    path.join(process.cwd(), "tools", "tla", "tla2tools.jar"),
    path.join(process.cwd(), "proofs", "tla", "tla2tools.jar"),
  ];

  for (const jar of candidates) {
    if (fs.existsSync(jar)) return jar;
  }

  return null;
}

function checkTLC(): ComponentStatus {
  const jarPath = resolveTlcJarPath();
  if (!jarPath) return "missing";

  const javaCmd = resolveJavaCmd();
  if (!javaCmd) return "failed";

  try {
    const res = spawnSync(javaCmd, ["-cp", jarPath, "tlc2.TLC", "-help"], {
      encoding: "utf-8",
      timeout: 15000,
      windowsHide: true,
      env: process.env,
      shell: false,
    });

    const out = `${res.stdout || ""}\n${res.stderr || ""}`;

    if (
      out.includes("TLC - provides model checking") ||
      out.includes("Version 2.") ||
      out.includes("SYNOPSIS") ||
      out.includes("NAME")
    ) {
      return "available";
    }

    if (res.error) return "failed";
    return res.status === 0 ? "available" : "failed";
  } catch {
    return "failed";
  }
}

function checkTLA(): ComponentStatus {
  const tlaRoot = resolveTlaRoot();
  if (!tlaRoot) return "missing";

  const hasSpecs =
    fs.existsSync(path.join(tlaRoot, "X108.tla")) &&
    fs.existsSync(path.join(tlaRoot, "ObsidiaDistX108A12.tla"));

  if (!hasSpecs) return "incomplete";

  const tlc = checkTLC();
  return tlc === "available" ? "available" : "incomplete";
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
