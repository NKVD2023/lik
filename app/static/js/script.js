// =========================================
// 1. ЛОКАЛЬНЫЕ ФУНКЦИИ (ДЛЯ СТРАНИЦЫ ЗАМЕТКИ)
// =========================================
function toggleEdit() {
    const viewMode = document.getElementById('view-mode');
    const editMode = document.getElementById('edit-mode');
    
    if (viewMode.style.display === 'none') {
        viewMode.style.display = 'block';
        editMode.style.display = 'none';
    } else {
        viewMode.style.display = 'none';
        editMode.style.display = 'block';
    }
}

// =========================================
// 2. УПРАВЛЕНИЕ МОДАЛЬНЫМИ ОКНАМИ
// =========================================
const modalOverlay = document.getElementById('note-modal-overlay');
const modalCard = document.getElementById('note-modal-card');
const modalTitle = document.getElementById('modal-title');
const modalContentHtml = document.getElementById('modal-content-html');
const modalEditLink = document.getElementById('modal-edit-link');

function openModal(title) {
    modalTitle.innerText = "ИНИЦИАЛИЗАЦИЯ...";
    modalContentHtml.innerHTML = '<div class="pulse-small" style="font-size:3rem; text-align:center; color: var(--accent); margin-top: 50px;">● ● ●</div>';
    modalOverlay.classList.add('active');
    
    updateModalContent(title);
}

function updateModalContent(title) {
    modalCard.style.opacity = '0.4';
    
    fetch(`/api/note/${encodeURIComponent(title)}`)
        .then(response => response.json())
        .then(data => {
            // НОВАЯ ЛОГИКА: Если заметка пустая — мгновенно открываем редактор
            if (data.is_empty) {
                window.location.href = `/note/${encodeURIComponent(data.title)}`;
                return; // Останавливаем выполнение кода модального окна
            }
            modalTitle.innerText = data.title;
            modalContentHtml.innerHTML = data.content_html;
            modalEditLink.setAttribute('href', `/note/${encodeURIComponent(data.title)}`);
            modalCard.style.opacity = '1';
        })
        .catch(error => {
            console.error('Ошибка связи с ядром:', error);
            modalContentHtml.innerHTML = '<div style="color:#ef4444;">Сбой. Ошибка загрузки.</div>';
            modalCard.style.opacity = '1';
        });
}

function closeModal() {
    modalOverlay.classList.remove('active');
    setTimeout(() => {
        if (modalTitle) modalTitle.innerText = "";
        if (modalContentHtml) modalContentHtml.innerHTML = "";
    }, 300);
}

const taskModalOverlay = document.getElementById('task-modal-overlay');

function openTaskModal() {
    if (taskModalOverlay) {
        taskModalOverlay.classList.add('active');
    }
}

function closeTaskModal() {
    if (taskModalOverlay) {
        taskModalOverlay.classList.remove('active');
    }
}

// =========================================
// 3. ИНИЦИАЛИЗАЦИЯ ПОСЛЕ ЗАГРУЗКИ СТРАНИЦЫ
// =========================================
document.addEventListener('DOMContentLoaded', () => {

    // --- А. ПЕРЕХВАТ КЛИКОВ ДЛЯ МОДАЛЬНОГО ОКНА ЗАМЕТОК ---
    const noteCards = document.querySelectorAll('.note-card');
    
    noteCards.forEach(card => {
        card.addEventListener('click', (e) => {
            // Игнорируем клик, если он был по кнопке ЗАКРЕПИТЬ или АРХИВ
            if (e.target.closest('.pin-btn') || e.target.closest('.archive-btn')) {
                return;
            }

            e.preventDefault();
            const title = card.getAttribute('data-title');
            if (title) {
                openModal(title);
            }
        });
    });

    // Перехват кликов внутри самой карточки (по внутренним ссылкам [[Текст]])
    const modalContent = document.getElementById('modal-content-html');
    if (modalContent) {
        modalContent.addEventListener('click', (e) => {
            if (e.target.classList.contains('internal-link')) {
                e.preventDefault();
                const url = e.target.getAttribute('href');
                const title = url.split('/').pop();
                updateModalContent(decodeURIComponent(title));
            }
        });
    }

    // Закрытие окон по клику на пустой фон
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) closeModal();
        });
    }

    if (taskModalOverlay) {
        taskModalOverlay.addEventListener('click', (e) => {
            if (e.target === taskModalOverlay) closeTaskModal();
        });
    }

    // --- Б. ЖИВОЙ БЕСШОВНЫЙ ПОИСК ---
    const searchInput = document.getElementById('live-search');
    const searchItems = document.querySelectorAll('.search-item');
    const emptyMsgCard = document.getElementById('empty-msg-card');
    const emptyMsgText = document.getElementById('empty-msg-text');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            let visibleCount = 0;

            searchItems.forEach(item => {
                const titleElement = item.querySelector('.note-title');
                const textElement = item.querySelector('.task-text');
                
                let combinedText = '';
                if (titleElement) combinedText += titleElement.textContent.replace('●', '').toLowerCase();
                if (textElement) combinedText += textElement.textContent.toLowerCase();

                if (query === '' || combinedText.includes(query)) {
                    item.style.display = 'flex';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });

            if (emptyMsgCard && emptyMsgText) {
                if (visibleCount === 0 && searchItems.length > 0) {
                    emptyMsgCard.style.display = 'flex';
                    emptyMsgText.textContent = 'СОВПАДЕНИЙ НЕ НАЙДЕНО';
                } else {
                    emptyMsgCard.style.display = 'none';
                }
            }
        });
    }

    // --- В. ДИНАМИЧЕСКИЙ РАСЧЕТ ДЕДЛАЙНОВ ЗАДАЧ (7 ДНЕЙ) ---
    function calculateUrgency() {
        const tasks = document.querySelectorAll('.task-card');
        const now = new Date();

        tasks.forEach(task => {
            const dueStr = task.getAttribute('data-due');
            if (!dueStr) return;

            const dueDate = new Date(dueStr);
            const timeDiffMs = dueDate - now;
            const hoursLeft = timeDiffMs / (1000 * 60 * 60);

            const alertWindowHours = 168; // Ровно 1 неделя (7 дней * 24 часа)
            const indicator = task.querySelector('.due-indicator');

            if (hoursLeft <= 0) {
                // Время вышло - максимальный красный
                task.style.borderColor = '#ef4444';
                task.style.background = 'rgba(239, 68, 68, 0.08)';
                if (indicator) indicator.style.color = '#ef4444';
            } else if (hoursLeft < alertWindowHours) {
                // Расчет пропорции: 0.0 (осталась неделя) -> 1.0 (осталось 0 часов)
                const ratio = 1 - (hoursLeft / alertWindowHours);
                
                let rBorder, gBorder, bBorder;

                if (ratio < 0.5) {
                    // Первая половина недели: Плавный переход от Серого к Желтому
                    const localRatio = ratio * 2;
                    rBorder = Math.round(51 + (234 - 51) * localRatio);
                    gBorder = Math.round(51 + (179 - 51) * localRatio);
                    bBorder = Math.round(51 + (8 - 51) * localRatio);
                } else {
                    // Вторая половина недели: Плавный переход от Желтого к Красному
                    const localRatio = (ratio - 0.5) * 2;
                    rBorder = Math.round(234 + (239 - 234) * localRatio);
                    gBorder = Math.round(179 + (68 - 179) * localRatio);
                    bBorder = Math.round(8 + (68 - 8) * localRatio);
                }

                // Применяем вычисленный цвет
                task.style.borderColor = `rgb(${rBorder}, ${gBorder}, ${bBorder})`;
                task.style.background = `rgba(${rBorder}, ${gBorder}, ${bBorder}, ${ratio * 0.06})`;
                
                if (indicator) indicator.style.color = `rgb(${rBorder}, ${gBorder}, ${bBorder})`;
            } else {
                // Если до дедлайна БОЛЬШЕ недели — возвращаем стандартные цвета
                task.style.borderColor = 'var(--border-color)';
                task.style.background = 'var(--bg-surface)';
                if (indicator) indicator.style.color = 'var(--text-muted)';
            }
        });
    }

    // Запускаем расчет сразу при загрузке и обновляем каждую минуту
    calculateUrgency();
    setInterval(calculateUrgency, 60000);
});

// Динамическое добавление полей для подзадач
function addSubtaskInput() {
    const container = document.getElementById('subtasks-container');
    
    // Создаем обертку
    const wrapper = document.createElement('div');
    wrapper.style.display = 'flex';
    wrapper.style.gap = '8px';
    wrapper.style.alignItems = 'center';

    // Создаем поле ввода
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'subtasks[]'; // Квадратные скобки нужны, чтобы Flask считал это как массив
    input.className = 'cyber-input';
    input.placeholder = 'Шаг задачи...';
    input.style.flex = '1';
    input.style.padding = '6px 10px';

    // Создаем кнопку удаления (крестик)
    const delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.className = 'archive-btn';
    delBtn.innerHTML = '✕';
    delBtn.style.width = '28px';
    delBtn.style.height = '28px';
    delBtn.onclick = () => wrapper.remove(); // Удаляем поле при клике

    wrapper.appendChild(input);
    wrapper.appendChild(delBtn);
    container.appendChild(wrapper);
    
    // Фокусируемся на новом поле
    input.focus();
}

// Очистка формы при закрытии модального окна (опционально, но полезно)
function closeTaskModal() {
    if (taskModalOverlay) {
        taskModalOverlay.classList.remove('active');
        // Очищаем подзадачи через полсекунды, чтобы не было видно дергания при закрытии
        setTimeout(() => {
            const container = document.getElementById('subtasks-container');
            if(container) container.innerHTML = '';
        }, 300);
    }
}