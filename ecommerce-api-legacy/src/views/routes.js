const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');
const { requireAdmin } = require('../middlewares/adminAuth');

function createRoutes({ checkoutController, reportController, userController }) {
  const router = express.Router();

  router.post('/checkout', asyncHandler(checkoutController.checkout));
  router.get('/admin/financial-report', requireAdmin, asyncHandler(reportController.financialReport));
  router.delete('/users/:id', requireAdmin, asyncHandler(userController.remove));

  return router;
}

module.exports = createRoutes;
