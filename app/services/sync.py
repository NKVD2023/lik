# app/services/sync.py
import os
import glob
import re
from datetime import datetime
from .. import db
from ..models.note import Note
from ..models.tasks import Task
from ..paths import NOTES_DIR, TASKS_DIR

def run_full_two_way_sync():
    """ГЛУБОКАЯ СИНХРОНИЗАЦИЯ С ПРОВЕРКОЙ КОНТЕНТА И ВЛОЖЕННЫХ ЗАДАЧ"""
    
    # 1. ЗАМЕТКИ
    db_notes_titles = set()
    for filepath in glob.glob(os.path.join(NOTES_DIR, "*.txt")):
        title = os.path.basename(filepath).replace('.txt', '')
        db_notes_titles.add(title)
        with open(filepath, 'r', encoding='utf-8') as f:
            content_str = f.read()
        parts = content_str.split("---\n", 1)
        meta = parts[0]
        content = parts[1] if len(parts) > 1 else ""
        
        is_pinned = "Pinned: True" in meta
        is_archived = "Archived: True" in meta
        created_at, updated_at = datetime.utcnow(), datetime.utcnow()
        parent_title = None
        
        for line in meta.split('\n'):
            if line.startswith("Created: "):
                try: created_at = datetime.fromisoformat(line.split("Created: ")[1].strip())
                except ValueError: pass
            elif line.startswith("Updated: "):
                try: updated_at = datetime.fromisoformat(line.split("Updated: ")[1].strip())
                except ValueError: pass
            elif line.startswith("Parent: "):
                pt = line.split("Parent: ")[1].strip()
                if pt: parent_title = pt

        file_mtime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
        actual_file_time = max(updated_at, file_mtime)
        note = Note.query.filter_by(title=title).first()
        if not note:
            new_note = Note(title=title, content=content, is_pinned=is_pinned, is_archived=is_archived, 
                            created_at=created_at, updated_at=actual_file_time, parent_title=parent_title)
            db.session.add(new_note)
        else:
            is_diff = (note.content or "").strip() != content.strip() or note.is_pinned != is_pinned or note.is_archived != is_archived or note.parent_title != parent_title
            if is_diff:
                db_time = note.updated_at or note.created_at
                if actual_file_time > db_time:
                    note.content, note.is_pinned, note.is_archived, note.parent_title, note.updated_at = content, is_pinned, is_archived, parent_title, actual_file_time
                else: note.save_to_file()
            else:
                if "Updated:" not in meta: note.save_to_file()

    for note in Note.query.all():
        if note.title not in db_notes_titles: note.save_to_file()
    db.session.commit()

    # 2. ЗАДАЧИ
    db_tasks_ids = set()
    for filepath in glob.glob(os.path.join(TASKS_DIR, "*.txt")):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: head = f.read(256)
            if "ParentID: " in head and "ParentID: None" not in head and "ParentID: \n" not in head:
                os.remove(filepath)
        except Exception: pass
            
    for filepath in glob.glob(os.path.join(TASKS_DIR, "*.txt")):
        filename = os.path.basename(filepath).replace('.txt', '')
        task_id_str = filename.split('_')[0]
        if not task_id_str.isdigit(): continue
        
        main_task_id = int(task_id_str)
        db_tasks_ids.add(main_task_id)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        parts = full_text.split("---\n", 1)
        meta = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        
        content = rest.strip()
        subtasks_str = ""
        
        if "---ПОДЗАДАЧИ---" in rest:
            c_parts = rest.split("---ПОДЗАДАЧИ---")
            content = c_parts[0].strip()
            subtasks_str = c_parts[1].strip()
        
        title, due_date = "Без названия", datetime.utcnow()
        is_completed = "Completed: True" in meta
        is_archived = "Archived: True" in meta
        updated_at = datetime.utcnow()
        
        for line in meta.split('\n'):
            if line.startswith("Title: "): title = line.split("Title: ")[1].strip()
            elif line.startswith("Due: "):
                try: due_date = datetime.fromisoformat(line.split("Due: ")[1].strip())
                except ValueError: pass
            elif line.startswith("Updated: "):
                try: updated_at = datetime.fromisoformat(line.split("Updated: ")[1].strip())
                except ValueError: pass

        file_mtime = datetime.utcfromtimestamp(os.path.getmtime(filepath))
        actual_file_time = max(updated_at, file_mtime)
        
        task = Task.query.get(main_task_id)
        if not task:
            task = Task(id=main_task_id, title=title, content=content, due_date=due_date, 
                            is_completed=is_completed, is_archived=is_archived, updated_at=actual_file_time)
            db.session.add(task)
        else:
            is_diff = (task.content or "").strip() != content or task.title != title or task.is_completed != is_completed or task.is_archived != is_archived
            if is_diff:
                if actual_file_time > (task.updated_at or task.due_date):
                    task.title, task.content, task.due_date, task.is_completed, task.is_archived, task.updated_at = title, content, due_date, is_completed, is_archived, actual_file_time
                else: task.save_to_file()
            else:
                expected_safe_title = re.sub(r'[\\/*?:"<>|]', "", task.title).strip() or "Без_названия"
                if "Updated:" not in meta or os.path.basename(filepath) != f"{task.id}_{expected_safe_title}.txt":
                    task.save_to_file()
        
        file_subtask_ids = set()
        rewrite_file = False
        
        if subtasks_str:
            for line in subtasks_str.split('\n'):
                line = line.strip()
                if not line: continue
                
                st_is_completed = line.startswith("[x]")
                match = re.search(r'ID:(\d+)', line)
                st_id = int(match.group(1)) if match else None
                
                title_part = line.split('|', 1)
                if len(title_part) > 1: st_title = title_part[1].strip()
                else: st_title = line.replace('[x]', '').replace('[ ]', '').strip()
                
                if st_id:
                    file_subtask_ids.add(st_id)
                    db_tasks_ids.add(st_id)
                    st = Task.query.get(st_id)
                    if not st:
                        st = Task(id=st_id, title=st_title, parent_id=main_task_id, due_date=due_date, is_completed=st_is_completed, updated_at=actual_file_time)
                        db.session.add(st)
                    else:
                        if st.title != st_title or st.is_completed != st_is_completed:
                            st.title, st.is_completed, st.updated_at = st_title, st_is_completed, actual_file_time
                else:
                    st = Task(title=st_title, parent_id=main_task_id, due_date=due_date, is_completed=st_is_completed, updated_at=actual_file_time)
                    db.session.add(st)
                    db.session.flush() 
                    file_subtask_ids.add(st.id)
                    db_tasks_ids.add(st.id)
                    rewrite_file = True 
        
        if task:
            for existing_st in Task.query.filter_by(parent_id=main_task_id).all():
                if existing_st.id not in file_subtask_ids:
                    db.session.delete(existing_st)
        
        if rewrite_file and task:
            task.save_to_file()
                    
    for t in Task.query.filter_by(parent_id=None).all():
        if t.id not in db_tasks_ids: t.save_to_file()
            
    db.session.commit()