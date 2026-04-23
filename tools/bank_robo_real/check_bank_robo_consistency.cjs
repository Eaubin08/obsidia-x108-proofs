#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

function arg(flag, def = null) {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : def;
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8").replace(/^\uFEFF/, ""));
}

function readJsonl(p) {
  const raw = fs.readFileSync(p, "utf8").replace(/^\uFEFF/, "");
  return raw.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
}

function mapDecisionToGate(decision) {
  const d = String(decision || "").trim().toUpperCase();
  if (d === "AUTORISER") return "ALLOW";
  if (d === "ANALYSER") return "HOLD";
  if (d === "BLOQUER") return "BLOCK";
  return null;
}

function normalizeText(value) {
  return String(value ?? "")
    .normalize("NFKC")
    .replace(/\s+/g, " ")
    .trim();
}

function extractRecentRows(payload) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== "object") return [];
  if (Array.isArray(payload.result?.data?.json)) return payload.result.data.json;
  if (Array.isArray(payload.result?.json)) return payload.result.json;
  if (Array.isArray(payload.json)) return payload.json;
  if (Array.isArray(payload.data)) return payload.data;
  if (Array.isArray(payload.rows)) return payload.rows;
  return [];
}

function normalizeRecentRow(tx) {
  return {
    id: tx.id ?? null,
    scenarioName: tx.scenarioName ?? tx.scenario_name ?? null,
    decision: tx.decision ?? null,
    actualGate: tx.actualGate ?? tx.actual_gate ?? mapDecisionToGate(tx.decision),
    reason: tx.reason ?? null,
    createdAt: tx.createdAt ?? tx.created_at ?? null,
  };
}

function readEnvMap(envFile) {
  const map = {};
  if (!envFile || !fs.existsSync(envFile)) return map;
  const lines = fs.readFileSync(envFile, "utf8").replace(/^\uFEFF/, "").split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (m) {
      map[m[1]] = String(m[2]).trim().replace(/^["']|["']$/g, "");
    }
  }
  return map;
}

async function queryDb(bankRoboSrc, databaseUrl, limit) {
  const mysqlPath = require.resolve("mysql2/promise", { paths: [bankRoboSrc] });
  const mysql = require(mysqlPath);

  const safeLimit = Math.max(1, Math.min(Number(limit) || 1, 10000));

  const conn = await mysql.createConnection(databaseUrl);
  const sql = `
    SELECT
      id,
      scenario_name AS scenarioName,
      decision,
      reason,
      created_at AS createdAt
    FROM transactions
    ORDER BY created_at DESC, id DESC
    LIMIT ${safeLimit}
  `;
  const [rows] = await conn.query(sql);
  await conn.end();

  return rows.map((r) => ({
    id: r.id,
    scenarioName: r.scenarioName,
    decision: r.decision,
    actualGate: mapDecisionToGate(r.decision),
    reason: r.reason,
    createdAt: r.createdAt,
  }));
}

function bestMatch(target, rows) {
  const targetDecision = normalizeText(target.decision).toUpperCase();
  const targetScenario = normalizeText(target.scenario_name);
  const targetReason = normalizeText(target.reason);

  return rows.find((r) =>
    normalizeText(r.decision).toUpperCase() === targetDecision &&
    normalizeText(r.scenarioName) === targetScenario &&
    normalizeText(r.reason) === targetReason
  ) || null;
}

function findDbMatch(row, recentMatch, dbRows) {
  if (recentMatch && recentMatch.id != null) {
    const byId = dbRows.find((r) => String(r.id) === String(recentMatch.id));
    if (byId) return byId;
  }
  return bestMatch(row, dbRows);
}

async function main() {
  const runDir = arg("--run-dir");
  const bankRoboSrc = arg("--bank-robo-src");
  const envFileArg = arg("--env-file");
  const outJson = arg("--out-json");
  const outJsonl = arg("--out-jsonl");

  if (!runDir || !outJson || !outJsonl) {
    throw new Error("Missing --run-dir / --out-json / --out-jsonl");
  }

  const metaFile = path.join(runDir, "meta.json");
  const rowsFile = path.join(runDir, "batch_probe_rows.jsonl");
  const meta = fs.existsSync(metaFile) ? readJson(metaFile) : {};
  const rows = readJsonl(rowsFile);

  const resolvedBankRoboSrc = bankRoboSrc || meta.bank_robo_src || "";
  const resolvedEnvFile = envFileArg || meta.env_file || "";

  let dbRows = [];
  let dbStatus = { ok: false, reason: "no_database_url" };

  const envMap = readEnvMap(resolvedEnvFile);
  if (envMap.DATABASE_URL && resolvedBankRoboSrc) {
    try {
      dbRows = await queryDb(
        resolvedBankRoboSrc,
        envMap.DATABASE_URL,
        Math.max(200, rows.length * 5)
      );
      dbStatus = { ok: true, count: dbRows.length };
    } catch (err) {
      dbStatus = { ok: false, reason: String(err && err.message || err) };
    }
  }

  const resultRows = rows.map((row) => {
    const recentRows = extractRecentRows(row.recent_raw).map(normalizeRecentRow);
    const expectedGate = mapDecisionToGate(row.decision);
    const recentMatch = bestMatch(row, recentRows);
    const dbMatch = dbStatus.ok ? findDbMatch(row, recentMatch, dbRows) : null;
    const requestIndex = Number(row.request_index || 0);
    const recentRowCount = Number(
      row.recent_row_count != null
        ? row.recent_row_count
        : row.recent_route_row_count != null
          ? row.recent_route_row_count
          : recentRows.length
    );

    let klass = "MATCH";

    if (!row.process_ok) {
      klass = "PROCESS_ERROR";
    } else if (!row.recent_ok) {
      klass = "RECENT_ERROR";
    } else if (requestIndex === 1 && recentRowCount === 0) {
      klass = "FIRST_READ_EMPTY";
    } else if (!recentMatch) {
      klass = "MISSING_IN_RECENT";
    } else if (dbStatus.ok && !dbMatch) {
      klass = "MISSING_IN_DB";
    } else if (recentMatch && recentMatch.actualGate !== expectedGate) {
      klass = "RECENT_GATE_MISMATCH";
    } else if (dbStatus.ok && dbMatch && dbMatch.actualGate !== expectedGate) {
      klass = "DB_GATE_MISMATCH";
    }

    return {
      request_index: requestIndex,
      scenario_name: row.scenario_name ?? null,
      decision: row.decision ?? null,
      expected_actual_gate: expectedGate,
      process_ok: !!row.process_ok,
      recent_ok: !!row.recent_ok,
      recent_attempts: row.recent_attempts ?? null,
      recent_route_row_count: recentRowCount,
      recent_match: !!recentMatch,
      db_match: !!dbMatch,
      recent_id: recentMatch ? recentMatch.id : null,
      db_id: dbMatch ? dbMatch.id : null,
      recent_actual_gate: recentMatch ? recentMatch.actualGate : null,
      db_actual_gate: dbMatch ? dbMatch.actualGate : null,
      invariant_decision_recent: !!recentMatch,
      invariant_decision_db: !!dbMatch,
      invariant_actual_gate_recent: recentMatch ? recentMatch.actualGate === expectedGate : false,
      invariant_actual_gate_db: dbMatch ? dbMatch.actualGate === expectedGate : false,
      recent_top_ids: recentRows.slice(0, 5).map((r) => r.id),
      recent_top_created_at: recentRows.slice(0, 5).map((r) => r.createdAt),
      class: klass,
    };
  });

  const classes = {};
  for (const r of resultRows) {
    classes[r.class] = (classes[r.class] || 0) + 1;
  }

  const summary = {
    status: "ok",
    run_dir: runDir,
    bank_robo_src: resolvedBankRoboSrc,
    env_file: resolvedEnvFile || null,
    db_status: dbStatus,
    total: resultRows.length,
    match: resultRows.filter((r) => r.class === "MATCH").length,
    mismatch: resultRows.filter((r) => r.class !== "MATCH").length,
    classes,
    recent_route_available: resultRows.some((r) => r.recent_ok),
    out_jsonl: outJsonl,
    out_json: outJson,
  };

  fs.writeFileSync(
    outJsonl,
    resultRows.map((r) => JSON.stringify(r)).join("\n") + (resultRows.length ? "\n" : ""),
    "utf8"
  );
  fs.writeFileSync(outJson, JSON.stringify(summary, null, 2), "utf8");

  console.log(JSON.stringify(summary));
}

main().catch((err) => {
  console.error(JSON.stringify({
    status: "error",
    error: String(err && err.stack || err)
  }));
  process.exit(1);
});