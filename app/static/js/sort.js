function sortNotes(method) {
    const grid = document.getElementById('notes-grid');
    if (!grid) return;

    // Собираем все карточки заметок в массив
    const cards = Array.from(grid.querySelectorAll('.note-card'));

    cards.sort((a, b) => {
        // 1. Всегда держим закрепленные сверху
        const pinA = parseInt(a.getAttribute('data-pinned') || '0');
        const pinB = parseInt(b.getAttribute('data-pinned') || '0');
        if (pinA !== pinB) return pinB - pinA;

        // Читаем даты
        const dateA = parseFloat(a.getAttribute('data-date') || '0');
        const dateB = parseFloat(b.getAttribute('data-date') || '0');

        if (method === 'structure') {
            const titleA = a.getAttribute('data-title').toLowerCase();
            const titleB = b.getAttribute('data-title').toLowerCase();
            const parentA = a.getAttribute('data-parent').toLowerCase();
            const parentB = b.getAttribute('data-parent').toLowerCase();

            // Определяем "семью" (либо родитель, либо само название, если карточка и есть родитель)
            const familyA = parentA || titleA;
            const familyB = parentB || titleB;

            // Группируем семьи по алфавиту
            if (familyA < familyB) return -1;
            if (familyA > familyB) return 1;

            // Если карточки из одной семьи:
            const isChildA = parentA ? 1 : 0;
            const isChildB = parentB ? 1 : 0;

            // Родитель всегда выше детей
            if (isChildA !== isChildB) return isChildA - isChildB;

            // Если это два ребенка одного родителя — сортируем их по дате (новые выше)
            return dateB - dateA;
        } else {
            // Классическая сортировка: просто по дате (новые выше)
            return dateB - dateA;
        }
    });

    // Очищаем сетку и вставляем карточки в новом порядке
    grid.innerHTML = '';
    cards.forEach(card => grid.appendChild(card));

    // Обновляем визуальное состояние кнопок (подсветку)
    document.getElementById('btn-sort-date').classList.remove('active');
    document.getElementById('btn-sort-structure').classList.remove('active');
    document.getElementById(`btn-sort-${method}`).classList.add('active');
}