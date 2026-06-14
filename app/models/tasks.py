# app/models/task.py
import os
import glob
import re
from datetime import datetime
from .. import db
from ..paths import TASKS_DIR

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, default="")
    due_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    
    subtasks = db.relationship('Task', backref=db.backref('parent', remote_side=[id]), cascade="all, delete-orphan")

    def save_to_file(self):
        if self.parent_id is not None:
            if self.parent:
                self.parent.save_to_file()
            return

        safe_title = re.sub(r'[\\/*?:"<>|]', "", self.title).strip() or "Без_названия"
        new_filename = f"{self.id}_{safe_title}.txt"
        filepath = os.path.join(TASKS_DIR, new_filename)
        
        old_files = glob.glob(os.path.join(TASKS_DIR, f"{self.id}_*.txt")) + glob.glob(os.path.join(TASKS_DIR, f"{self.id}.txt"))
        for old_file in old_files:
            if os.path.basename(old_file) != new_filename:
                try: os.remove(old_file)
                except OSError: pass

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {self.title}\n")
            f.write(f"Due: {self.due_date.isoformat()}\n")
            f.write(f"Completed: {self.is_completed}\n")
            f.write(f"Archived: {self.is_archived}\n")
            f.write(f"Updated: {(self.updated_at or datetime.utcnow()).isoformat()}\n")
            f.write("---\n")
            f.write(self.content or "")
            
            active_subtasks = [st for st in self.subtasks if not st.is_archived]
            if active_subtasks:
                f.write("\n\n---ПОДЗАДАЧИ---\n")
                for st in active_subtasks:
                    status = "[x]" if st.is_completed else "[ ]"
                    f.write(f"{status} ID:{st.id} | {st.title}\n")

    def delete_file(self):
        # Удаляем все файлы, начинающиеся с ID этой задачи
        old_files = glob.glob(os.path.join(TASKS_DIR, f"{self.id}_*.txt")) + glob.glob(os.path.join(TASKS_DIR, f"{self.id}.txt"))
        for old_file in old_files:
            try:
                os.remove(old_file)
            except OSError:
                pass