# routes/pages.py
from flask import render_template
from .blueprint import main_bp
from ..models import Note, Task

@main_bp.route('/')
def index():
    tasks = Task.query.filter_by(is_completed=False, is_archived=False, parent_id=None).order_by(Task.due_date.asc()).all()
    notes = Note.query.filter_by(is_archived=False).order_by(Note.is_pinned.desc(), Note.created_at.desc()).all()
    return render_template('index.html', tasks=tasks, notes=notes)

@main_bp.route('/archive')
def archive():
    tasks = Task.query.filter_by(is_archived=True, parent_id=None).order_by(Task.due_date.desc()).all()
    notes = Note.query.filter_by(is_archived=True).order_by(Note.created_at.desc()).all()
    return render_template('archive.html', tasks=tasks, notes=notes)