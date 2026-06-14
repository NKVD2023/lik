function triggerSystemSync() {
    const syncBtn = document.getElementById('btn-sync-system');
    if (!syncBtn) return;

    // Защита от повторных нажатий и индикация процесса
    syncBtn.disabled = true;
    syncBtn.innerText = 'СИНХРОНИЗАЦИЯ...';
    syncBtn.style.opacity = '0.6';
    syncBtn.style.cursor = 'not-allowed';

    fetch('/api/sync-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Мгновенно перезагружаем страницу для отображения изменений
            window.location.reload();
        } else {
            alert('Ошибка при синхронизации: ' + data.message);
            resetSyncButton(syncBtn);
        }
    })
    .catch(error => {
        console.error('Критический сбой подсистемы синхронизации:', error);
        alert('Не удалось связаться с сервером для выполнения синхронизации.');
        resetSyncButton(syncBtn);
    });
}

function resetSyncButton(btn) {
    btn.disabled = false;
    btn.innerText = 'СИНХРОНИЗИРОВАТЬ С ДИСКОМ';
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
}