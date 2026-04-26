const { spawn } = require('child_process');
const express = require('express');
const app = express();
app.use(express.json());

app.post('/kernel/ragnarok', (req, res) => {
    // -u force Python à envoyer ses logs immédiatement sans attendre
    const py = spawn('python', ['-u', 'sigma/run_pipeline.py'], {
        env: { ...process.env, PYTHONPATH: process.cwd() }
    });

    let result = '';

    // Capture des logs classiques (stdout)
    py.stdout.on('data', (data) => {
        const str = data.toString();
        if (str.trim().startsWith('{')) {
            result += str;
        } else {
            console.log(`\x1b[36m🐍 [PYTHON_INFO]:\x1b[0m ${str.trim()}`);
        }
    });

    // Capture des traces internes (stderr) - C'est ici que nos logs s'affichent
    py.stderr.on('data', (data) => {
        console.error(`\x1b[33m📢 [KERNEL_TRACE]:\x1b[0m ${data.toString().trim()}`);
    });

    py.stdin.write(JSON.stringify(req.body));
    py.stdin.end();

    py.on('close', () => {
        try { res.json(JSON.parse(result)); }
        catch (e) { res.status(500).json({ error: "Pipeline crash", raw: result }); }
    });
});

app.listen(3001, () => {
    console.log("\x1b[44m\x1b[37m %s \x1b[0m", " LOGS ACTIVÉS : LE KERNEL VA PARLER ");
    console.log("🚀 Listening on port 3001...");
});
