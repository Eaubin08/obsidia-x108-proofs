const fs = require("fs");
const mysql = require("mysql2/promise");

function parseEnvFile(path) {
  const raw = fs.readFileSync(path, "utf8").replace(/^\uFEFF/, "");
  const env = {};
  for (const line of raw.split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    let v = m[2].trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    env[m[1]] = v;
  }
  return env;
}

async function probeApi(url) {
  try {
    const res = await fetch(url);
    const text = await res.text();
    return {
      ok: res.ok,
      status: res.status,
      body_head: text.slice(0, 2000),
    };
  } catch (err) {
    return {
      ok: false,
      status: 0,
      error: String((err && err.stack) || err),
    };
  }
}

async function main() {
  const envFile = process.argv[2];
  const baseUrl = process.argv[3];
  const apiOut = process.argv[4];
  const dbOut = process.argv[5];

  if (!envFile || !baseUrl || !apiOut || !dbOut) {
    throw new Error("usage: node diagnose_bank_robo_db_read.cjs <envFile> <baseUrl> <apiOut> <dbOut>");
  }

  const env = parseEnvFile(envFile);
  const databaseUrl = env.DATABASE_URL;

  if (!databaseUrl) {
    throw new Error("DATABASE_URL missing in env file");
  }

  const recentUrl = `${baseUrl}/api/trpc/banking.getRecentTransactions?input=` +
    encodeURIComponent(JSON.stringify({ json: { limit: 1 } }));

  const apiProbe = await probeApi(recentUrl);
  fs.writeFileSync(apiOut, JSON.stringify(apiProbe, null, 2), "utf8");

  const result = {
    database_url_present: true,
    api_recent_url: recentUrl,
    api_recent_status: apiProbe.status,
    checks: {}
  };

  let conn = null;
  try {
    conn = await mysql.createConnection(databaseUrl);

    const [dbRows] = await conn.query("SELECT DATABASE() AS db");
    result.checks.current_database = dbRows;

    const [tableRows] = await conn.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = DATABASE()
        AND table_name IN ('transactions', 'users', 'simulation_sessions')
      ORDER BY table_name
    `);
    result.checks.tables_present = tableRows;

    try {
      const [countRows] = await conn.query("SELECT COUNT(*) AS n FROM transactions");
      result.checks.transactions_count = countRows;
    } catch (err) {
      result.checks.transactions_count_error = String((err && err.message) || err);
    }

    try {
      const [sampleRows] = await conn.query(`
        SELECT id, scenario_name, decision, created_at
        FROM transactions
        ORDER BY created_at DESC, id DESC
        LIMIT 5
      `);
      result.checks.transactions_sample = sampleRows;
    } catch (err) {
      result.checks.transactions_sample_error = String((err && err.message) || err);
    }

  } catch (err) {
    result.connection_error = String((err && err.stack) || err);
  } finally {
    if (conn) {
      try { await conn.end(); } catch {}
    }
  }

  fs.writeFileSync(dbOut, JSON.stringify(result, null, 2), "utf8");
  console.log(JSON.stringify({
    status: "ok",
    api_out: apiOut,
    db_out: dbOut
  }));
}

main().catch((err) => {
  console.error(JSON.stringify({ status: "error", error: String((err && err.stack) || err) }));
  process.exit(1);
});