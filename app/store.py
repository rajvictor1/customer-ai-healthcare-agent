import os
import sqlite_utils
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models import Conversation, Message

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///data/conversations.db").replace("sqlite:///", "")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    db = sqlite_utils.Database(conn)
    if "conversations" not in db.table_names():
        db["conversations"].create({
            "id": str,
            "customer_id": str,
            "channel": str,
            "domain": str,
            "messages": str,
            "context": str,
            "created_at": str,
            "updated_at": str,
            "status": str,
        }, pk="id")
    return db

class ConversationStore:
    def __init__(self):
        self.db = init_db()

    def get_or_create(self, conversation_id: str, customer_id: str, channel: str, domain: str) -> Conversation:
        from sqlite_utils.db import NotFoundError
        try:
            row = self.db["conversations"].get(conversation_id)
        except NotFoundError:
            row = None
        if row:
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
        self.db["conversations"].upsert({
            "id": conv.id,
            "customer_id": conv.customer_id,
            "channel": conv.channel,
            "domain": conv.domain,
            "messages": json.dumps([m.model_dump(mode="json") for m in conv.messages]),
            "context": json.dumps(conv.context),
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "status": conv.status,
        }, pk="id")

    def list_recent(self, hours: int = 24) -> List[Conversation]:
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        rows = list(self.db["conversations"].rows_where("updated_at > ?", [since], order_by="updated_at DESC"))
        return [self._row_to_conv(r) for r in rows]

    def _row_to_conv(self, row: Dict[str, Any]) -> Conversation:
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
