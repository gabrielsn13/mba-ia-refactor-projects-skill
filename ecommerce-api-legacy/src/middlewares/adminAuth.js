const crypto = require('crypto');
const settings = require('../config/settings');
const { UnauthorizedError, ForbiddenError } = require('./errorHandler');

function tokensMatch(received, expected) {
  const a = Buffer.from(received);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function requireAdmin(req, res, next) {
  const token = req.get('X-Admin-Token');
  if (!token) return next(new UnauthorizedError('Token de administrador obrigatório'));
  if (!settings.adminToken || !tokensMatch(token, settings.adminToken)) {
    return next(new ForbiddenError());
  }
  return next();
}

module.exports = { requireAdmin };
