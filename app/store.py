import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, MetaData, String, Table, create_engine, desc, select
from sqlalchemy.engine import Engine, RowMapping

from app.config import get_settings
from app.models import Conversation, Message


def _database_url() -> str:
    url = get_settings().DATABASE_URL
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    if os.environ.get("VERCEL") and url == "sqlite:///data/conversations.db":
        return "sqlite:////tmp/conversations.db"
    return url


metadata = MetaData()
conversations = Table(
    "conversations",
    metadata,
    Column("id", String, primary_key=True),
    Column("customer_id", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("domain", String, nullable=False),
    Column("messages", String, nullable=False),
    Column("context", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False, index=True),
    Column("status", String, nullable=False),
)


def init_engine() -> Engine:
    url = _database_url()
    if url.startswith("sqlite:///"):
        db_path = url.removeprefix("sqlite:///")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(url, pool_pre_ping=True)
    metadata.create_all(engine)
    return engine


class ConversationStore:
    def __init__(self):
        self.engine = init_engine()

    def get(self, conversation_id: str) -> Optional[Conversation]:
        with self.engine.begin() as conn:
            row = conn.execute(
                select(conversations).where(conversations.c.id == conversation_id)
            ).mappings().first()
        return self._row_to_conv(row) if row else None

    def get_or_create(self, conversation_id: str, customer_id: str, channel: str, domain: str) -> Conversation:
        conv = self.get(conversation_id)
        if conv:
            return conv
        conv = Conversation(
            id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            domain=domain,
        )
        self.save(conv)
        return conv

    def save(self, conv: Conversation):
        conv.updated_at = datetime.utcnow()
        row = {
            "id": conv.id,
            "customer_id": conv.customer_id,
            "channel": conv.channel,
            "domain": conv.domain,
            "messages": json.dumps([m.model_dump(mode="json") for m in conv.messages]),
            "context": json.dumps(conv.context),
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "status": conv.status,
        }
        with self.engine.begin() as conn:
            exists = conn.execute(
                select(conversations.c.id).where(conversations.c.id == conv.id)
            ).first()
            if exists:
                conn.execute(
                    conversations.update().where(conversations.c.id == conv.id).values(**row)
                )
            else:
                conn.execute(conversations.insert().values(**row))

    def list_recent(self, hours: int = 24) -> List[Conversation]:
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        with self.engine.begin() as conn:
            rows = conn.execute(
                select(conversations)
                .where(conversations.c.updated_at > since)
                .order_by(desc(conversations.c.updated_at))
            ).mappings().all()
        return [self._row_to_conv(row) for row in rows]

    def _row_to_conv(self, row: RowMapping | Dict[str, Any]) -> Conversation:
        return Conversation(
            id=row["id"],
            customer_id=row["customer_id"],
            channel=row["channel"],
            domain=row["domain"],
            messages=[Message(**m) for m in json.loads(row["messages"])],
            context=json.loads(row["context"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            status=row["status"],
        )


STORE = ConversationStore()
