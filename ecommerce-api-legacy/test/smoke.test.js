const test = require('node:test');
const assert = require('node:assert/strict');
const { openDatabase } = require('../src/database/connection');
const { initDatabase } = require('../src/database/schema');
const { createApp } = require('../src/app');

test('checkout and admin route protection', async (t) => {
  const db = await openDatabase(':memory:');
  t.after(() => db.close());
  await initDatabase(db);
  const app = await createApp(db);
  const server = app.listen(0);
  t.after(() => server.close());

  const base = `http://127.0.0.1:${server.address().port}`;

  const unauthorized = await fetch(`${base}/api/admin/financial-report`);
  assert.equal(unauthorized.status, 401);

  const checkout = await fetch(`${base}/api/checkout`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      usr: 'Guilherme',
      eml: 'gui@fullcycle.com.br',
      pwd: 'senhaforte',
      c_id: 2,
      card: '4111222233334444',
    }),
  });
  assert.equal(checkout.status, 200);
});
