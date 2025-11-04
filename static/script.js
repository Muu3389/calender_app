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
        document.getElementById('event-color').value = selectedColor;
    };
});

// 保存ボタン
document.getElementById('save-event').onclick = async (e) => {
    e.preventDefault();

    const id = document.getElementById('event-id').value;
    const date = document.getElementById('event-date').value;
    const time = document.getElementById('event-time').value;
    const title = document.getElementById('event-text').value;
    const color = document.getElementById('event-color').value || "#e8f0fe";
    const action = id ? "/update" : "/add";

    if (!title) return;

    const response = await fetch(action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, date, time, title, color })
    });

    if (response.ok) {
        const cell = document.querySelector(`td[data-date="${date}"]`);
        let list = cell.querySelector('.event-list');
        if (!list) {
            list = document.createElement('div');
            list.className = 'event-list';
            cell.appendChild(list);
        }

        // 既存要素があるなら削除（複製防止）
        if (id) {
            const old = list.querySelector(`.event[data-id="${id}"]`);
            if (old) old.remove();
        }

        const result = await response.json(); // サーバー側がidを返すようにする
        const eventId = result.id || id;

        const div = document.createElement('div');
        div.className = 'event';
        div.dataset.id = eventId;
        div.style.backgroundColor = color;
        div.innerHTML = time
            ? `<span class="event-time">${time}<br></span><span class="event-title">${title}</span>`
            : `<span class="event-title">${title}</span>`;

        list.appendChild(div);

        // 入力リセット
        document.getElementById('event-form').style.display = 'none';
        document.getElementById('event-id').value = '';
        document.getElementById('event-text').value = '';
        document.getElementById('event-time').value = '';
    }
};

// クリックで週を展開（他の週が開いていたら閉じる）
document.querySelectorAll('table tr').forEach(row => {
    row.addEventListener('click', () => {
        // 曜日行はスキップ
        if (row.classList.contains('weekday-row')) return;

        // 現在開いている行を閉じる
        const expanded = document.querySelector('tr.expanded');
        if (expanded && expanded !== row) {
            expanded.classList.remove('expanded');
        }

        // 自分を展開（既に開いていてもそのまま）
        if (!row.classList.contains('expanded')) {
            row.classList.add('expanded');
        }
    });
});

// 既存の document.querySelectorAll('.event') ... を削除して、代わりに：
document.querySelector('table').addEventListener('click', e => {
    const ev = e.target.closest('.event');
    if (!ev) return;

    const row = ev.closest('tr');
    if (!row.classList.contains('expanded')) return;
    e.stopPropagation();

    const date = ev.closest('td').dataset.date;
    const timeEl = ev.querySelector('.event-time');
    const time = timeEl ? timeEl.textContent.trim() : "";
    const title = ev.querySelector('.event-title')
        ? ev.querySelector('.event-title').textContent.trim()
        : ev.textContent.trim();
    const color = ev.style.backgroundColor || '#e8f0fe';
    const id = ev.dataset.id;

    document.getElementById('event-id').value = id;
    document.getElementById('event-date').value = date;
    document.getElementById('event-time').value = time;
    document.getElementById('event-text').value = title;
    document.getElementById('event-color').value = color;

    document.querySelectorAll('.color-option').forEach(opt => {
        opt.classList.toggle('selected', opt.dataset.color === color);
    });

    const form = document.getElementById('event-form');
    form.action = '/update';
    form.style.display = 'block';
});

// 削除ボタン
document.getElementById('delete-event').onclick = () => {
    const id = document.getElementById('event-id').value;
    if (!id) return;
    fetch(`/delete/${id}`, { method: 'POST' })
        .then(() => location.reload());
};

// キャンセル
document.getElementById('cancel-event').onclick = () => {
    document.getElementById('event-form').style.display = 'none';
};
