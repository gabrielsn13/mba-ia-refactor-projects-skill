const settings = require('../config/settings');

function buildReport(rows) {
  const courses = new Map();

  rows.forEach((row) => {
    if (!courses.has(row.course_id)) {
      courses.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
    }
    if (row.enrollment_id === null) return;

    const entry = courses.get(row.course_id);
    if (row.payment_status === settings.paymentStatus.PAID) entry.revenue += row.amount;
    entry.students.push({ student: row.student_name || 'Unknown', paid: row.amount || 0 });
  });

  return [...courses.values()];
}

function createReportController({ enrollmentModel }) {
  return {
    async financialReport(req, res) {
      const rows = await enrollmentModel.findFinancialRows();
      res.json(buildReport(rows));
    },
  };
}

module.exports = createReportController;
