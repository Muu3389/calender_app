// 日付セルをダブルクリック → フォーム表示
document.querySelectorAll('.day-cell').forEach(cell => {
    cell.ondblclick = () => {
        const date = cell.getAttribute('data-date');
        document.getElementById('event-date').value = date;
        document.getElementById('event-form').style.display = 'block';
    };

    // シングルクリック → フォーム非表示
    cell.onclick = () => {
        const form = document.getElementById('event-form');
        if (form.style.display === 'block') {
            form.style.display = 'none';
        }
    };
});

// キャンセルボタン
document.getElementById('cancel-event').onclick = () => {
    document.getElementById('event-form').style.display = 'none';
};

// 色選択
let selectedColor = "#e8f0fe"; // デフォルト

document.querySelectorAll('.color-option').forEach(option => {
    option.onclick = () => {
        document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');
        selectedColor = option.dataset.color;
    };
});

// 保存ボタン
document.getElementById('save-event').onclick = () => {
    const date = document.getElementById('event-date').value;
    const time = document.getElementById('event-time').value;
    const text = document.getElementById('event-text').value;
    if (!text) return;

    const targetCell = document.querySelector(`td[data-date="${date}"]`);
    const div = document.createElement('div');
    div.className = 'event';
    div.textContent = time ? `${time} ${text}` : text;
    div.style.backgroundColor = selectedColor;
    targetCell.appendChild(div);

    document.getElementById('event-form').style.display = 'none';
    document.getElementById('event-text').value = '';
    document.getElementById('event-time').value = '';
    document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
    selectedColor = "#e8f0fe";
};
