const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const express = require('express');
const app = express();

let lastAutoSealRoot = null;

function pick(obj, ...keys) {
    let cur = obj;
    for (const key of keys) {
        if (!cur || typeof cur !== "object") return undefined;
        cur = cur[key];
    }
    return cur;
}


function ansi(code, text) {
    return `\x1b[${code}m${text}\x1b[0m`;
}

function normalizeGate(gate) {
    return String(gate || "UNKNOWN").replaceAll('"', "").toUpperCase();
}

function kernelLabel() {
    return ansi("38;5;250", "[KERNEL]");
}

function domainOnlyLabel(domain) {
    const d = String(domain || "").toLowerCase();
    if (d.includes("bank")) return ansi("38;5;27", "[BANK]");
    if (d.includes("trading")) return ansi("38;5;201", "[TRADING]");
    if (d.includes("gps") || d.includes("aviation")) return ansi("38;5;223", "[GPS]");
    return ansi("1;97", "[UNKNOWN]");
}

function domainLabel(domain) {
    return `${kernelLabel()}${domainOnlyLabel(domain)}`;
}

function gateLabel(gate) {
    const g = String(gate || "").toUpperCase();
    if (g === "ALLOW") return ansi("38;5;208", "[ALLOW]");
    if (g === "BLOCK") return ansi("1;31", "[BLOCK]");
    if (g === "HOLD") return ansi("38;5;214", "[HOLD]");
    return ansi("1;97", `[${g || "UNKNOWN"}]`);
}

function sectionLabel(section) {
    const s = String(section || "").toUpperCase();
    if (s === "SCORE") return ansi("38;5;220", "[SCORE]");
    if (s === "PROOF") return ansi("38;5;51", "[PROOF]");
    if (s === "CRYPTO") return ansi("38;5;99", "[CRYPTO]");
    if (s === "AUTHORITY") return ansi("1;97", "[AUTHORITY]");
    if (s === "SAVE") return ansi("1;32", "[SAVE]");
    if (s === "BRIDGE") return ansi("38;5;197", "[BRIDGE]");
    if (s === "TRACE") return ansi("38;5;130", "[KERNEL_TRACE]");
    return ansi("1;97", `[${s}]`);
}

function printKernelDecisionSummary(domain, parsedResult) {
    const verdict =
        parsedResult.market_verdict ||
        pick(parsedResult, "domain_sigma_envelope", "market_verdict") ||
        pick(parsedResult, "data", "domain_sigma_envelope", "market_verdict");

    const gate =
        parsedResult.x108_gate ||
        pick(parsedResult, "domain_sigma_envelope", "x108_gate") ||
        pick(parsedResult, "data", "domain_sigma_envelope", "x108_gate");

    const reason =
        parsedResult.reason_code ||
        pick(parsedResult, "domain_sigma_envelope", "reason_code") ||
        pick(parsedResult, "data", "domain_sigma_envelope", "reason_code");

    const severity =
        parsedResult.severity ||
        pick(parsedResult, "domain_sigma_envelope", "severity") ||
        pick(parsedResult, "data", "domain_sigma_envelope", "severity");

    const decisionId =
        parsedResult.decision_id ||
        pick(parsedResult, "domain_sigma_envelope", "decision_id") ||
        pick(parsedResult, "data", "domain_sigma_envelope", "decision_id");

    const traceId =
        parsedResult.trace_id ||
        pick(parsedResult, "domain_sigma_envelope", "trace_id") ||
        pick(parsedResult, "data", "domain_sigma_envelope", "trace_id");

    const integrity =
        parsedResult.confidence_integrity ||
        parsedResult.integrity ||
        pick(parsedResult, "domain_sigma_envelope", "confidence_integrity");

    const governance =
        parsedResult.confidence_governance ||
        parsedResult.governance ||
        pick(parsedResult, "domain_sigma_envelope", "confidence_governance");

    const readiness =
        parsedResult.confidence_readiness ||
        parsedResult.readiness ||
        pick(parsedResult, "domain_sigma_envelope", "confidence_readiness");

    console.log(
        `${domainLabel(domain)} ${gateLabel(gate)} [DECISION] verdict=${verdict} reason=${reason} severity=${severity}`
    );
    console.log(
        `${domainLabel(domain)} ${sectionLabel("SCORE")} integrity=${integrity} governance=${governance} readiness=${readiness}`
    );
    console.log(
        `${domainLabel(domain)} ${sectionLabel("PROOF")} decision_id=${decisionId} trace_id=${traceId}`
    );
}

app.use(express.json());

app.post('/kernel/ragnarok', (req, res) => {
    const sigmaDir = path.join(__dirname, '..', 'sigma');
    const scriptPath = path.join(sigmaDir, 'run_pipeline.py');
    const tempFilePath = path.join(__dirname, 'input_temp.json');

    // --- CHIRURGIE DYNAMIQUE ---
    const domain = req.body.domain || "gps_defense_aviation";
    const dataToProcess = req.body.state || req.body;

    // 1. Écriture du fichier temporaire
    try {
        fs.writeFileSync(tempFilePath, JSON.stringify(dataToProcess, null, 2));
    } catch (err) {
        return res.status(500).json({ error: "Failed to write temp file", details: err.message });
    }

    console.log(`\x1b[38;5;197m[BRIDGE]\x1b[0m 🚀 Routing -> Domain: ${domain}`);

    // 2. Lancement du Kernel Python
    const py = spawn('python', ['-u', scriptPath, domain, tempFilePath], {
        env: { ...process.env, PYTHONPATH: path.join(__dirname, '..') }
    });

    let result = '';

    py.stdout.on('data', (data) => {
        const str = data.toString();
        if (str.trim().startsWith('{')) {
            result += str;
        } else {
            console.log(`\x1b[38;5;245m🐍 [PYTHON_INFO]:\x1b[0m ${str.trim()}`);
        }
    });

    py.stderr.on('data', (data) => {
        console.error(`\x1b[38;5;240m?? [KERNEL_TRACE]:\x1b[0m ${data.toString().trim()}`);
    });

    py.on('close', (code) => {
        // Nettoyage
        if (fs.existsSync(tempFilePath)) {
            try { fs.unlinkSync(tempFilePath); } catch(e) {}
        }

        if (code !== 0 && !result) {
            console.error(`\x1b[31m[ERROR]\x1b[0m Python a quitté avec le code ${code}`);
            return res.status(500).json({ error: "Python Crash Code " + code });
        }

        try {
            const parsedResult = JSON.parse(result);

            // --- PERSISTENCE DES PREUVES ---
            const allDataDir = path.join(__dirname, 'allData');
            if (!fs.existsSync(allDataDir)) fs.mkdirSync(allDataDir);

            const filename = `decision_${domain}_${Date.now()}.json`;
            fs.writeFileSync(path.join(allDataDir, filename), JSON.stringify(parsedResult, null, 2));
            printKernelDecisionSummary(domain, parsedResult);
            console.log(`\x1b[1;32m💾 [SAVE]\x1b[0m ${filename}`);

            res.json(parsedResult);
        } catch (e) {
            console.error("\x1b[31m[PARSE ERROR]\x1b[0m", result);
            res.status(500).json({ error: "Parsing error", raw: result });
        }
    });
});

// --- SYSTÈME DE SCELLAGE AUTOMATIQUE (Toutes les 60s) ---
// Note : On utilise ../ car audit_merkle.py est à la racine du projet
setInterval(() => {
    console.log("🔐 [AUTO-SEAL] Pulsation Merkle en cours...");

    const auditMerklePath = path.join(__dirname, '..', 'audit_merkle.py');
    exec(`python "${auditMerklePath}"`, { cwd: path.join(__dirname, '..') }, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ [AUTO-SEAL] Échec : ${error.message}`);
            return;
        }
        // Capture du Root Hash dans la console Python
        const rootHash = stdout.match(/ROOT HASH : (.*)/);
        if (rootHash) {
            const currentRoot = rootHash[1].trim();
            if (currentRoot !== lastAutoSealRoot) {
                lastAutoSealRoot = currentRoot;
                console.log(`[AUTO-SEAL] Nouveau Root: ${currentRoot.substring(0, 12)}...`);
            } else {
                console.log(`[AUTO-SEAL] Root inchange: ${currentRoot.substring(0, 12)}...`);
            }
        } else {
            console.log(`[AUTO-SEAL] Cycle complet - pas de nouveau Root Hash detecte`);
        }
    });
}, 60000);

app.listen(3001, () => {
    console.log("\x1b[45m\x1b[37m %s \x1b[0m", " ⚡ BRIDGE UNIVERSEL : MODE FICHIER TAMPON ⚡ ");
    console.log("🚀 Prêt pour Ragnarok sur http://localhost:3001");
});
