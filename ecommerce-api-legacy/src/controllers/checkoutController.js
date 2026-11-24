const settings = require('../config/settings');
const logger = require('../utils/logger');
const { hashPassword } = require('../utils/password');
const paymentGateway = require('../services/paymentGateway');
const { BadRequestError, NotFoundError } = require('../middlewares/errorHandler');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function parseCheckoutBody(body = {}) {
  const { usr: userName, eml: email, pwd: password, c_id: rawCourseId, card: cardNumber } = body;

  if (!userName || !email || !rawCourseId || !cardNumber) throw new BadRequestError('Bad Request');
  if (typeof userName !== 'string' || typeof email !== 'string' || typeof cardNumber !== 'string') {
    throw new BadRequestError('Bad Request');
  }
  if (!EMAIL_PATTERN.test(email)) throw new BadRequestError('E-mail inválido');
  if (password !== undefined && typeof password !== 'string') throw new BadRequestError('Senha inválida');

  const courseId = Number(rawCourseId);
  if (!Number.isInteger(courseId) || courseId <= 0) throw new BadRequestError('Bad Request');

  return { userName, email, password, courseId, cardNumber };
}

function createCheckoutController({ db, userModel, courseModel, enrollmentModel, paymentModel, auditModel }) {
  return {
    async checkout(req, res) {
      const { userName, email, password, courseId, cardNumber } = parseCheckoutBody(req.body);

      const course = await courseModel.findActiveById(courseId);
      if (!course) throw new NotFoundError('Curso não encontrado');

      const existingUser = await userModel.findByEmail(email);
      if (!existingUser && !password) throw new BadRequestError('Senha obrigatória para novos usuários');

      logger.info(`Processando pagamento do curso ${courseId} (cartão final ${cardNumber.slice(-4)})`);
      const status = paymentGateway.authorize(cardNumber);
      if (status === settings.paymentStatus.DENIED) throw new BadRequestError('Pagamento recusado');

      const passwordHash = existingUser ? null : await hashPassword(password);

      const enrollmentId = await db.transaction(async () => {
        const userId = existingUser
          ? existingUser.id
          : await userModel.create({ name: userName, email, passwordHash });
        const newEnrollmentId = await enrollmentModel.create({ userId, courseId });
        await paymentModel.create({ enrollmentId: newEnrollmentId, amount: course.price, status });
        await auditModel.record(`Checkout curso ${courseId} por ${userId}`);
        return newEnrollmentId;
      });

      res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    },
  };
}

module.exports = createCheckoutController;
