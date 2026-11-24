class AppError extends Error {
  constructor(message, status = 500) {
    super(message);
    this.status = status;
  }
}

class BadRequestError extends AppError {
  constructor(message = 'Bad Request') { super(message, 400); }
}
class UnauthorizedError extends AppError {
  constructor(message = 'Não autorizado') { super(message, 401); }
}
class ForbiddenError extends AppError {
  constructor(message = 'Acesso negado') { super(message, 403); }
}
class NotFoundError extends AppError {
  constructor(message = 'Não encontrado') { super(message, 404); }
}

const asyncHandler = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);

function notFoundHandler(req, res) {
  res.status(404).json({ error: 'Rota não encontrada' });
}

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  if (err instanceof AppError) {
    return res.status(err.status).json({ error: err.message });
  }
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({ error: 'JSON inválido' });
  }
  require('../utils/logger').error(err.stack || err.message);
  return res.status(500).json({ error: 'Erro interno do servidor' });
}

module.exports = {
  AppError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError,
  asyncHandler, notFoundHandler, errorHandler,
};
