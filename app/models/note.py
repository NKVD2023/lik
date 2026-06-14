# app/models/note.py
import os
from datetime import datetime
from .. import db
from ..paths import NOTES_DIR

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    content = db.Column(db.Text, default="")
    is_pinned = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_title = db.Column(db.String(150), nullable=True)

    def save_to_file(self):
        safe_title = self.title.replace("/", "-").replace("\\", "-")
        filepath = os.path.join(NOTES_DIR, f"{safe_title}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Pinned: {self.is_pinned}\n")
            f.write(f"Archived: {self.is_archived}\n")
            f.write(f"Created: {self.created_at.isoformat()}\n")
            f.write(f"Updated: {(self.updated_at or self.created_at).isoformat()}\n")
            f.write(f"Parent: {self.parent_title or ''}\n")
            f.write("---\n")
            f.write(self.content or "")

    def delete_file(self):
        safe_title = self.title.replace("/", "-").replace("\\", "-")
        filepath = os.path.join(NOTES_DIR, f"{safe_title}.txt")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass