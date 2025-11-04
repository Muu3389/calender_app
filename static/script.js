// =========================
// Calendar Event Controller
// =========================

// --- DOMキャッシュ ---
const form = document.getElementById('event-form');
const fields = {
    id: document.getElementById('event-id'),
    date: document.getElementById('event-date'),
    time: document.getElementById('event-time'),
    title: document.getElementById('event-text'),
    color: document.getElementById('event-color')
};
const cancelBtn = document.getElementById('cancel-event');
const deleteBtn = document.getElementById('delete-event');
const saveBtn = document.getElementById('save-event');
const colorOptions = document.querySelectorAll('.color-option');

let selectedColor = '#e8f0fe'; // 初期色

// ---------------------
// カレンダーセル関連
// ---------------------

// 日付セル：ダブルクリックでフォームを開く
document.querySelectorAll('.day-cell').forEach(cell => {
    cell.ondblclick = () => {
        fields.date.value = cell.dataset.date;
        form.style.display = 'block';
    };

    // シングルクリックで閉じる（フォームが開いている場合のみ）
    cell.onclick = () => {
        if (form.style.display === 'block') {
            form.style.display = 'none';
        }
    };
});

// ---------------------
// フォーム制御
// ---------------------

// キャンセルボタン → 閉じる＆リセット
cancelBtn.onclick = () => {
    form.style.display = 'none';
    resetForm();
};

// 削除ボタン → API呼び出し
deleteBtn.onclick = async () => {
    const id = fields.id.value;
    if (!id) return;

    await fetch(`/delete/${id}`, { method: 'POST' });
    location.reload();
};

// 色選択
colorOptions.forEach(option => {
    option.onclick = () => {
        colorOptions.forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');
        selectedColor = option.dataset.color;
        fields.color.value = selectedColor;
    };
});

// ---------------------
// 保存処理（追加・更新共通）
// ---------------------
saveBtn.onclick = async e => {
    e.preventDefault();

    const { id, date, time, title, color } = Object.fromEntries(
        Object.entries(fields).map(([k, v]) => [k, v.value])
    );
    if (!title) return;

    const isUpdate = Boolean(id);
    const endpoint = isUpdate ? '/update' : '/add';

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id,
            date,
            time,
            title,
            color: color || selectedColor
        })
    });

    if (!response.ok) return;
    const result = await response.json();
    const eventId = result.id || id;

    renderEvent({ eventId, date, time, title, color });
    resetForm();
    form.style.display = 'none';
};

// ---------------------
// イベント描画・編集
// ---------------------

// カレンダーにイベントを追加 or 更新
function renderEvent({ eventId, date, time, title, color }) {
    const cell = document.querySelector(`td[data-date="${date}"]`);
    if (!cell) return;

    let list = cell.querySelector('.event-list');
    if (!list) {
        list = document.createElement('div');
        list.className = 'event-list';
        cell.appendChild(list);
    }

    // 既存イベントを上書き（複製防止）
    list.querySelector(`.event[data-id="${eventId}"]`)?.remove();

    const div = document.createElement('div');
    div.className = 'event';
    div.dataset.id = eventId;
    div.style.backgroundColor = color;
    div.innerHTML = time
        ? `<span class="event-time">${time}</span> <span class="event-title">${title}</span>`
        : `<span class="event-title">${title}</span>`;

    list.appendChild(div);
}

// クリックで週を展開（他の週が開いていたら閉じる）
document.querySelectorAll('table tr').forEach(row => {
    row.addEventListener('click', e => {
        // 曜日行はスキップ
        if (row.classList.contains('weekday-row')) return;

        // イベントクリック時は展開トリガーを無効化
        if (e.target.closest('.event')) return;

        const expanded = document.querySelector('tr.expanded');

        // 他の行が展開されていたら閉じる
        if (expanded && expanded !== row) {
            expanded.classList.remove('expanded');
        }

        // まだ展開されていないときだけ展開
        if (!row.classList.contains('expanded')) {
            row.classList.add('expanded');
        }
        // すでに展開済みなら何もしない
    });
});


// 展開中のみイベントを編集可能
document.querySelector('table').addEventListener('click', e => {
    const eventEl = e.target.closest('.event');
    if (!eventEl) return;

    const row = eventEl.closest('tr');
    if (!row.classList.contains('expanded')) return;
    e.stopPropagation();

    const date = eventEl.closest('td').dataset.date;
    const time = eventEl.querySelector('.event-time')?.textContent.trim() || '';
    const title = eventEl.querySelector('.event-title')?.textContent.trim() || '';
    const color = eventEl.style.backgroundColor || '#e8f0fe';
    const id = eventEl.dataset.id;

    Object.assign(fields, {
        id: { value: id },
        date: { value: date },
        time: { value: time },
        title: { value: title },
        color: { value: color }
    });

    colorOptions.forEach(opt =>
        opt.classList.toggle('selected', opt.dataset.color === color)
    );

    form.style.display = 'block';
});

// ---------------------
// ユーティリティ
// ---------------------

function resetForm() {
    Object.values(fields).forEach(f => (f.value = ''));
    selectedColor = '#e8f0fe';
    colorOptions.forEach(o => o.classList.remove('selected'));
}
