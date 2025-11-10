from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class Message:
    from_: str
    to: str
    text: str
    timestamp: int = int(datetime.now().timestamp())
    message_id: str = uuid.uuid4().hex

    def to_dict(self):
        """Converte o objeto em dict para salvar ou transmitir."""
        # asdict pega todos os campos automaticamente
        d = asdict(self)
        # se for desejado que o campo apareça como 'from' no JSON,
        # renomeie na hora de serializar para dict:
        d['from'] = d.pop('from_')
        return d

    @staticmethod
    def from_dict(data: dict):
        return Message(
            from_=data.get('from'),
            to=data.get('to'),
            text=data.get('text'),
            timestamp=data.get('timestamp', int(datetime.now().timestamp())),
            message_id=data.get('message_id', uuid.uuid4().hex),
        )