const { BadRequestError, NotFoundError } = require('../middlewares/errorHandler');

function createUserController({ db, userModel }) {
  return {
    async remove(req, res) {
      const id = Number(req.params.id);
      if (!Number.isInteger(id) || id <= 0) throw new BadRequestError('ID inválido');

      const deleted = await db.transaction(() => userModel.deleteWithRelations(id));
      if (!deleted) throw new NotFoundError('Usuário não encontrado');

      res.status(200).json({ msg: 'Usuário deletado junto com matrículas e pagamentos.' });
    },
  };
}

module.exports = createUserController;
