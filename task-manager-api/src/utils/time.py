from datetime import datetime, timezone

from src.config.settings import DATE_FORMAT


def utc_now():
    """UTC atual sem tzinfo (compativel com as colunas DateTime naive do banco)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def parse_date(value):
    """Converte 'YYYY-MM-DD' em datetime. Levanta ValueError se invalido."""
    if not isinstance(value, str):
        raise ValueError('data deve ser string')
    return datetime.strptime(value, DATE_FORMAT)
