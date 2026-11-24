const crypto = require('crypto');
const { promisify } = require('util');
const settings = require('../config/settings');

const scrypt = promisify(crypto.scrypt);

async function hashPassword(password) {
  const salt = crypto.randomBytes(settings.scrypt.saltBytes).toString('hex');
  const derived = await scrypt(password, salt, settings.scrypt.keyLength);
  return `${salt}:${derived.toString('hex')}`;
}

async function verifyPassword(password, stored) {
  const [salt, hash] = stored.split(':');
  const derived = await scrypt(password, salt, settings.scrypt.keyLength);
  return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), derived);
}

module.exports = { hashPassword, verifyPassword };
