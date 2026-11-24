const crypto = require('crypto');
const settings = require('../config/settings');
const { hashPassword } = require('../utils/password');

async function createSchema(db) {
  await db.run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
  await db.run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
  await db.run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
  await db.run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
  await db.run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seed(db) {
  const existing = await db.get('SELECT COUNT(*) AS total FROM users');
  if (existing.total > 0) return;

  const password = settings.seedUserPassword || crypto.randomBytes(12).toString('hex');
  const hash = await hashPassword(password);

  await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', hash]);
  await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)', [
    'Clean Architecture', 997.0, 'Docker', 497.0,
  ]);
  await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
  await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, ?)', [settings.paymentStatus.PAID]);
}

async function initDatabase(db) {
  await createSchema(db);
  await seed(db);
}

module.exports = { initDatabase };
