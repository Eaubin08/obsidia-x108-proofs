/**
 * Merkle Real Adapter â€” Branchement RÃ‰EL sur verify_merkle.py
 * 
 * Appelle les VRAIS scripts Merkle/Seal
 * Pas de simulation, pas de Merkle tree local, pas de faux seal.
 */

import { spawnSync } from "child_process";
import path from "path";
import fs from "fs";

export interface MerkleRealAttestation {
  attestation_id: string;
  decision_id: string;
  merkle_root?: string | null;
  seal?: string | null;
  sealed_at: number;
  verified: boolean;
  status: "verified" | "incomplete" | "failed";
  source: "obsidia_verify_merkle" | "incomplete";
}

/**
 * Appelle le VRAI verify_merkle.py pour attester une dÃ©cision
 * Retour honnÃªte : merkle_root/seal null si pas d'artefact rÃ©el
 */
export function callRealMerkleVerify(decisionId: string): MerkleRealAttestation {
  const startedAt = Date.now();
  
  try {
    // DÃ©tection dynamique du repo
    const repoRoot = findObsidiaRepoRoot();
    if (!repoRoot) {
      return {
        attestation_id: `merkle-${decisionId}-${startedAt}`,
        decision_id: decisionId,
        merkle_root: null,
        seal: null,
        sealed_at: startedAt,
        verified: false,
        status: "incomplete",
        source: "incomplete",
      };
    }
    
    const verifyScript = path.join(repoRoot, "proofs", "verify_merkle.py");
    const proofsDir = path.join(repoRoot, "proofs");
    
    // Appeler le script Python
    const result = spawnSync("py", ["-3", verifyScript], {
      encoding: "utf-8",
      cwd: proofsDir,
      maxBuffer: 10 * 1024 * 1024,
      timeout: 5000,
    });
    
    // Lire les artefacts rÃ©els produits
    const merkleRootFile = path.join(proofsDir, "merkle_root.json");
    
    let merkleRoot: string | null = null;
    let seal: string | null = null;
    let verified = false;
    let status: "verified" | "incomplete" | "failed" = "incomplete";
    
    if (fs.existsSync(merkleRootFile)) {
      try {
        const data = JSON.parse(fs.readFileSync(merkleRootFile, "utf-8"));
        merkleRoot = data.merkle_root || null;
        seal = data.seal || null;
        verified = result.status === 0 && !!merkleRoot;
        status = verified ? "verified" : "failed";
      } catch (err) {
        console.warn("[MerkleReal] Failed to read merkle_root.json:", err);
        status = "failed";
      }
    } else {
      status = "incomplete";
    }
    
    return {
      attestation_id: `merkle-${decisionId}-${startedAt}`,
      decision_id: decisionId,
      merkle_root: merkleRoot,
      seal: seal,
      sealed_at: startedAt,
      verified,
      status,
      source: "obsidia_verify_merkle",
    };
  } catch (err) {
    console.warn("[MerkleReal] Exception:", err);
    return {
      attestation_id: `merkle-${decisionId}-${startedAt}`,
      decision_id: decisionId,
      merkle_root: null,
      seal: null,
      sealed_at: startedAt,
      verified: false,
      status: "failed",
      source: "incomplete",
    };
  }
}

/**
 * Appelle verify_all.py pour vÃ©rifier l'intÃ©gritÃ© complÃ¨te
 */
export function callRealVerifyAll(): {
  success: boolean;
  output: string;
  errors: string[];
} {
  try {
    const repoRoot = findObsidiaRepoRoot();
    if (!repoRoot) {
      return {
        success: false,
        output: "",
        errors: ["Obsidia repo not found"],
      };
    }
    
    const verifyAllScript = path.join(repoRoot, "proofs", "verify_all.py");
    const proofsDir = path.join(repoRoot, "proofs");
    
    const result = spawnSync("py", ["-3", verifyAllScript], {
      encoding: "utf-8",
      cwd: proofsDir,
      maxBuffer: 10 * 1024 * 1024,
      timeout: 10000,
    });
    
    return {
      success: result.status === 0,
      output: result.stdout || "",
      errors: result.stderr ? [result.stderr] : [],
    };
  } catch (err) {
    return {
      success: false,
      output: "",
      errors: [err instanceof Error ? err.message : String(err)],
    };
  }
}

function findObsidiaRepoRoot(): string | null {
  // DÃ©tection dynamique principale
  const possiblePaths = [
  process.cwd(),
  ".",
  "../",
  "../../",
  "../../../obsidia-engine-proof-core",
  "../../obsidia-engine-proof-core",
  "../obsidia-engine-proof-core",
  "./obsidia-engine-proof-core",
];
  
  for (const p of possiblePaths) {
    try {
      const resolved = path.resolve(p);
      const proofsPath = path.join(resolved, "proofs", "verify_merkle.py");
      if (fs.existsSync(proofsPath)) {
        return resolved;
      }
    } catch (err) {
      // Continuer
    }
  }
  
  // Fallback secondaire seulement
  const fallback = "/home/ubuntu/obsidia-engine-proof-core";
  try {
    const proofsPath = path.join(fallback, "proofs", "verify_merkle.py");
    if (fs.existsSync(proofsPath)) {
      return fallback;
    }
  } catch (err) {
    // Continuer
  }
  
  return null;
}

export function validateMerkleAttestation(attestation: MerkleRealAttestation): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  if (!attestation.attestation_id) {
    errors.push("attestation_id is required");
  }
  
  if (!attestation.decision_id) {
    errors.push("decision_id is required");
  }
  
  if (attestation.status === "verified" && !attestation.merkle_root) {
    errors.push("merkle_root is missing for verified attestation");
  }
  
  if (attestation.status === "verified" && !attestation.seal) {
    errors.push("seal is missing for verified attestation");
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}





