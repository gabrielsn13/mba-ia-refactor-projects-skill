const sqlite3 = require('sqlite3');

class Database {
  constructor(connection) {
    this.connection = connection;
    this.lock = Promise.resolve();
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.run(sql, params, function onRun(err) {
        if (err) return reject(err);
        resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.connection.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
  }

  // Serializes transactions: a single connection cannot interleave BEGIN/COMMIT blocks.
  transaction(work) {
    const execute = async () => {
      await this.run('BEGIN');
      try {
        const result = await work();
        await this.run('COMMIT');
        return result;
      } catch (err) {
        await this.run('ROLLBACK');
        throw err;
      }
    };
    const next = this.lock.then(execute, execute);
    this.lock = next.catch(() => {});
    return next;
  }

  close() {
    return new Promise((resolve, reject) => {
      this.connection.close((err) => (err ? reject(err) : resolve()));
    });
  }
}

function openDatabase(path) {
  return new Promise((resolve, reject) => {
    const connection = new sqlite3.Database(path, (err) => {
      if (err) return reject(err);
      resolve(new Database(connection));
    });
  });
}

module.exports = { openDatabase, Database };
