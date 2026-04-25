const express = require('express');
const { Client } = require('pg');
const app = express();
const port = 3000;


const connectionString = 'postgresql://neondb_owner:npg_GjgAW9zx0yvV@ep-still-grass-a9kyfcp5-pooler.gwc.azure.neon.tech/neondb?sslmode=require&channel_binding=require';

const client = new Client({
    connectionString: connectionString,
});

client.connect()
    .then(() => console.log('? Connecté à PostgreSQL sur le Cloud !'))
    .catch(err => console.error('? Erreur de connexion', err.stack));

app.use(express.json());

// Initialisation de la table (Le Kernel prépare son terrain)
const initDb = async () => {
    const query = `
        CREATE TABLE IF NOT EXISTS obsidia_logs (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            decision TEXT DEFAULT 'VALIDATED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    `;
    await client.query(query);
};
initDb();

app.get('/', (req, res) => {
    res.send('Système Obsidia - Backend PostgreSQL Connecté');
});

app.post('/addData', async (req, res) => {
    const { name, age } = req.body;

    if (!name || !age) {
        return res.status(400).json({ error: 'Données incomplètes' });
    }

    try {
        const query = 'INSERT INTO obsidia_logs(name, age) VALUES($1, $2) RETURNING *';
        const values = [name, age];
        const result = await client.query(query, values);
        
        console.log(`Donnée persistée dans le Cloud : ${name}`);
        res.status(200).json({ 
            status: "success", 
            database_entry: result.rows[0] 
        });
    } catch (err) {
        res.status(500).json({ error: 'Erreur SQL', details: err.message });
    }
});

app.listen(port, () => {
    console.log(`?? Serveur PostgreSQL : http://localhost:${port}`);
});
