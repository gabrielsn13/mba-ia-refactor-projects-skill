const settings = require('../config/settings');

// Simulated gateway: cards starting with the approved prefix are paid, others are denied.
function authorize(cardNumber) {
  return cardNumber.startsWith(settings.approvedCardPrefix)
    ? settings.paymentStatus.PAID
    : settings.paymentStatus.DENIED;
}

module.exports = { authorize };
