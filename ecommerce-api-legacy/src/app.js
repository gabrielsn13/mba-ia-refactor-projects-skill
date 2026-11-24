const express = require('express');
const settings = require('./config/settings');
const logger = require('./utils/logger');
const { openDatabase } = require('./database/connection');
const { initDatabase } = require('./database/schema');
const createUserModel = require('./models/userModel');
const createCourseModel = require('./models/courseModel');
const createEnrollmentModel = require('./models/enrollmentModel');
const createPaymentModel = require('./models/paymentModel');
const createAuditModel = require('./models/auditModel');
const createCheckoutController = require('./controllers/checkoutController');
const createReportController = require('./controllers/reportController');
const createUserController = require('./controllers/userController');
const createRoutes = require('./views/routes');
const { notFoundHandler, errorHandler } = require('./middlewares/errorHandler');

async function createApp(db) {
  await initDatabase(db);

  const userModel = createUserModel(db);
  const courseModel = createCourseModel(db);
  const enrollmentModel = createEnrollmentModel(db);
  const paymentModel = createPaymentModel(db);
  const auditModel = createAuditModel(db);

  const routes = createRoutes({
    checkoutController: createCheckoutController({ db, userModel, courseModel, enrollmentModel, paymentModel, auditModel }),
    reportController: createReportController({ enrollmentModel }),
    userController: createUserController({ db, userModel }),
  });

  const app = express();
  app.use(express.json());
  app.use('/api', routes);
  app.use(notFoundHandler);
  app.use(errorHandler);
  return app;
}

async function main() {
  const db = await openDatabase(settings.dbPath);
  const app = await createApp(db);
  app.listen(settings.port, () => logger.info(`Frankenstein LMS rodando na porta ${settings.port}...`));
}

if (require.main === module) {
  main().catch((err) => {
    logger.error(err.stack || err.message);
    process.exit(1);
  });
}

module.exports = { createApp };
