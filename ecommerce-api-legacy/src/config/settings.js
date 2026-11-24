const settings = {
  port: Number(process.env.PORT) || 3000,
  dbPath: process.env.DB_PATH || ':memory:',
  adminToken: process.env.ADMIN_TOKEN || '',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  seedUserPassword: process.env.SEED_USER_PASSWORD || '',
  approvedCardPrefix: '4',
  paymentStatus: Object.freeze({ PAID: 'PAID', DENIED: 'DENIED' }),
  scrypt: Object.freeze({ keyLength: 64, saltBytes: 16 }),
};

module.exports = settings;
