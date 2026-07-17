// Vérifie le code HTTP de tous les liens de la table "aides" (Supabase)
// Échoue volontairement (process.exit(1)) si un lien est cassé, pour que
// GitHub Actions envoie une notification d'échec de job.

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SERVICE_KEY) {
  console.error("Variables d'environnement SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY manquantes.");
  process.exit(1);
}

async function fetchAides() {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/aides?select=id,nom,lien`, {
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}` }
  });
  if (!res.ok) {
    console.error('Erreur Supabase:', res.status, await res.text());
    process.exit(1);
  }
  return res.json();
}

async function checkLien(lien) {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    const r = await fetch(lien, {
      method: 'GET',
      redirect: 'follow',
      signal: controller.signal,
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
    });
    clearTimeout(timeout);
    return { lien, status: r.status, ok: r.ok };
  } catch (e) {
    return { lien, status: 'ERROR', error: e.message };
  }
}

async function main() {
  const aides = await fetchAides();

  const byLien = {};
  aides.forEach(a => {
    if (!a.lien) return;
    (byLien[a.lien] = byLien[a.lien] || []).push(a.nom);
  });
  const liens = Object.keys(byLien);

  const results = [];
  const BATCH = 8;
  for (let i = 0; i < liens.length; i += BATCH) {
    const batch = liens.slice(i, i + BATCH);
    results.push(...(await Promise.all(batch.map(checkLien))));
  }

  const problems = results.filter(r => r.status === 'ERROR' || r.status >= 400);

  console.log(`${liens.length} lien(s) unique(s) vérifié(s) sur ${aides.length} aide(s).`);

  if (problems.length === 0) {
    console.log('Aucun problème détecté.');
    process.exit(0);
  }

  console.log(`\n⚠ ${problems.length} lien(s) cassé(s) :\n`);
  problems.forEach(p => {
    console.log(`- [${p.status}${p.error ? ' — ' + p.error : ''}] ${p.lien}`);
    console.log(`  Aide(s) concernée(s) : ${byLien[p.lien].join(', ')}`);
  });
  process.exit(1);
}

main();
