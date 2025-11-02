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

    const date = document.getElementById('event-date').value;
    const time = document.getElementById('event-time').value;
    const title = document.getElementById('event-text').value;
    const color = document.getElementById('event-color').value;

    if (!title) return;

    const response = await fetch("/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date, time, title, color })
    });

    if (response.ok) {
        const cell = document.querySelector(`td[data-date="${date}"]`);

        // ✅ event-list がないセル(予定0)なら作る
        let list = cell.querySelector('.event-list');
        if (!list) {
            list = document.createElement('div');
            list.className = 'event-list';
            cell.appendChild(list);
        }

        const div = document.createElement('div');
        div.className = 'event';
        div.innerHTML = time
            ? `<span class="event-time">${time}<br></span><span class="event-title">${title}</span>`
            : `<span class="event-title">${title}</span>`;
        div.style.backgroundColor = color;

        list.appendChild(div);

        document.getElementById('event-form').style.display = 'none';
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
