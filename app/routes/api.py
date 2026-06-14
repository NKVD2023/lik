# routes/api.py
from flask import jsonify
from .blueprint import main_bp
from ..models import Note, db
from ..services import run_full_two_way_sync

@main_bp.route('/api/note/<string:title>')
def api_get_note(title):
    title = title.strip()
    note = Note.query.filter_by(title=title).first()
    
    if not note:
        note = Note(title=title, content="")
        db.session.add(note)
        db.session.commit()
        note.save_to_file()
        
    is_empty = not note.content or not note.content.strip()
    html_content = parse_internal_links(note.content) if not is_empty else ""
        
    return jsonify({
        'exists': True, 
        'title': note.title, 
        'content_html': html_content,
        'is_empty': is_empty
    })

@main_bp.route('/api/sync-all', methods=['POST'])
def api_sync_all():
    try:
        run_full_two_way_sync()
        return jsonify({'status': 'success', 'message': 'Синхронизация успешно завершена'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500