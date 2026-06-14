# routes/notes.py
import re
from flask import render_template, request, redirect, url_for
from .blueprint import main_bp
from ..models import Note, db
from ..utils import parse_internal_links

@main_bp.route('/create', methods=['POST'])
def create_note():
    title = request.form.get('title')
    if title:
        title = title.strip()
        existing_note = Note.query.filter_by(title=title).first()
        if not existing_note:
            new_note = Note(title=title, content="")
            db.session.add(new_note)
            db.session.commit()
            new_note.save_to_file()
        return redirect(url_for('main.handle_note', title=title))
    return redirect(url_for('main.index'))



@main_bp.route('/note/<string:title>', methods=['GET', 'POST'])
def handle_note(title):
    note = Note.query.filter_by(title=title).first()
    if request.method == 'POST':
        content = request.form.get('content', '')
        if note: note.content = content
        else:
            note = Note(title=title, content=content)
            db.session.add(note)
        
        linked_titles = re.findall(r'\[\[(.*?)\]\]', content)
        new_ghosts = [] 
        
        for l_title in linked_titles:
            l_title = l_title.strip()
            if not Note.query.filter_by(title=l_title).first():
                new_ghost = Note(title=l_title, content="", parent_title=title)
                db.session.add(new_ghost)
                new_ghosts.append(new_ghost)

        db.session.commit()
        for ghost in new_ghosts: ghost.save_to_file()
        note.save_to_file()
        return redirect(url_for('main.handle_note', title=title))
        
    return render_template('note.html', title=title, note=note, content_html=parse_internal_links(note.content) if note else "")

@main_bp.route('/toggle_pin/<string:title>', methods=['POST'])
def toggle_pin(title):
    note = Note.query.filter_by(title=title).first_or_404()
    note.is_pinned = not note.is_pinned
    db.session.commit()
    note.save_to_file()
    return redirect(url_for('main.index'))

@main_bp.route('/toggle_archive_note/<string:title>', methods=['POST'])
def toggle_archive_note(title):
    note = Note.query.filter_by(title=title).first_or_404()
    note.is_archived = not note.is_archived
    note.is_pinned = False
    db.session.commit()
    note.save_to_file()
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/delete_note/<string:title>', methods=['POST'])
def delete_note(title):
    note = Note.query.filter_by(title=title).first_or_404()
    note.delete_file()       # 1. Стираем файл
    db.session.delete(note)  # 2. Стираем из БД
    db.session.commit()
    return redirect(request.referrer or url_for('main.archive'))