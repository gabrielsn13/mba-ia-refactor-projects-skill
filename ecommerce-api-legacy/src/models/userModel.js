function createUserModel(db) {
  return {
    findByEmail: (email) => db.get('SELECT id, name, email FROM users WHERE email = ?', [email]),
    findById: (id) => db.get('SELECT id, name, email FROM users WHERE id = ?', [id]),
    async create({ name, email, passwordHash }) {
      const { lastID } = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
      return lastID;
    },
    async deleteWithRelations(id) {
      await db.run(
        'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
        [id],
      );
      await db.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
      const { changes } = await db.run('DELETE FROM users WHERE id = ?', [id]);
      return changes > 0;
    },
  };
}

module.exports = createUserModel;
