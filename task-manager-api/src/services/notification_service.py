import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


class NotificationService:
    """Envio de e-mails. Configuracao vem de Settings (variaveis de ambiente)."""

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @property
    def enabled(self):
        return bool(self.host and self.user and self.password)

    def send_email(self, to, subject, body):
        if not self.enabled:
            logger.warning('SMTP nao configurado; e-mail para %s ignorado', to)
            return False
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = self.user
        message['To'] = to
        message.set_content(body)
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(message)
            logger.info('Email enviado para %s', to)
            return True
        except Exception:
            logger.exception('Erro ao enviar email para %s', to)
            return False

    def notify_task_assigned(self, user, task):
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        return self.send_email(user.email, f'Nova task atribuída: {task.title}', body)

    def notify_task_overdue(self, user, task):
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        return self.send_email(user.email, f'Task atrasada: {task.title}', body)
