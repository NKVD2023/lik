# routes/tasks.py
from datetime import datetime
from flask import request, redirect, url_for
from .blueprint import main_bp
from ..models import Task, db

@main_bp.route('/create_task', methods=['POST'])
def create_task():
    title = request.form.get('title')
    content = request.form.get('content', '')
    parent_id = request.form.get('parent_id')
    due_date_str = request.form.get('due_date')
    subtask_titles = request.form.getlist('subtasks[]') 
    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else datetime.utcnow()
    
    new_task = Task(title=title, content=content, due_date=due_date, parent_id=int(parent_id) if parent_id else None)
    db.session.add(new_task)
    db.session.flush() 
    
    for st_title in subtask_titles:
        if st_title.strip(): 
            subtask = Task(title=st_title.strip(), due_date=due_date, parent_id=new_task.id)
            db.session.add(subtask)
            
    db.session.commit()
    new_task.save_to_file()
    return redirect(url_for('main.index'))
    
@main_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.delete_file()       # 1. Удаляем TXT-файл
    db.session.delete(task)  # 2. Удаляем из БД (и все подзадачи тоже)
    db.session.commit()      # 3. Сохраняем изменения
    return redirect(request.referrer or url_for('main.archive'))


@main_bp.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_completed = True
    db.session.commit()
    task.save_to_file()
    return redirect(url_for('main.index'))

@main_bp.route('/toggle_archive_task/<int:task_id>', methods=['POST'])
def toggle_archive_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_archived = not task.is_archived
    db.session.commit()
    task.save_to_file()
    return redirect(request.referrer or url_for('main.index'))