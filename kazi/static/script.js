const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chatArea = document.getElementById("chatArea");
const typingIndicator = document.getElementById("typingIndicator");

// Автоматическое изменение высоты textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    chatArea.scrollTop = chatArea.scrollHeight;
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Блокируем интерфейс во время отправки
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Показываем сообщение пользователя
    const userMsg = document.createElement("div");
    userMsg.className = "message user-message";
    userMsg.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">></div>
            USER
        </div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    chatArea.appendChild(userMsg);

    // Очищаем поле ввода и сбрасываем высоту
    userInput.value = "";
    userInput.style.height = 'auto';

    // Прокручиваем вниз
    chatArea.scrollTop = chatArea.scrollHeight;

    // Показываем индикатор набора текста
    showTypingIndicator();

    try {
        const formData = new FormData();
        formData.append("message", message);

        const response = await fetch("/send", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            location.reload();
        } else {
            throw new Error('ОШИБКА СИСТЕМЫ');
        }

    } catch (error) {
        hideTypingIndicator();

        const errMsg = document.createElement("div");
        errMsg.className = "message ai-message";
        errMsg.innerHTML = `
            <div class="message-header">
                <div class="message-avatar">>></div>
                SYSTEM_ERROR
            </div>
            <div class="message-content">
                <em>ОШИБКА ПОДКЛЮЧЕНИЯ К СИСТЕМЕ. ПОВТОРИТЕ ПОПЫТКУ...</em>
            </div>
        `;
        chatArea.appendChild(errMsg);
        chatArea.scrollTop = chatArea.scrollHeight;
    } finally {
        // Разблокируем интерфейс
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Автофокус на поле ввода при загрузке
document.addEventListener('DOMContentLoaded', function() {
    userInput.focus();

    // Прокручиваем вниз при загрузке
    setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    }, 100);

    // Добавляем эффект печатания для существующих сообщений
    const messages = document.querySelectorAll('.message-content');
    messages.forEach(message => {
        const originalText = message.innerHTML;
        message.innerHTML = '';
        let i = 0;
        const typeText = () => {
            if (i < originalText.length) {
                message.innerHTML += originalText.charAt(i);
                i++;
                setTimeout(typeText, 1);
            }
        };
        typeText();
    });
});

// Обработка изменения размера окна
window.addEventListener('resize', function() {
    chatArea.scrollTop = chatArea.scrollHeight;
});

// Добавляем звуковые эффекты (опционально)
function playMatrixSound() {
    // Можно добавить звуковые эффекты при желании
    console.log('> SYSTEM BEEP');
}

// Добавляем эффект для кнопок
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', playMatrixSound);
});