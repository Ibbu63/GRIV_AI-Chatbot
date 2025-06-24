document.getElementById('chat-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const input = document.getElementById('user-input');
    const userText = input.value;

    document.body.classList.add('chat-started');
    input.value = "";

    appendMessage("You", userText, "user");
    appendTypingMessage("GRIV");

    const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userText })
    });

    const data = await res.json();
    removeTypingMessage();

    if (/code|debug|error|program|syntax|```/i.test(userText)) {
        appendMessage("GRIV", data.answer, "bot");
    } else {
        await typeMessage("GRIV", data.answer, "bot");
    }
});


function saveToSession() {
    const chatBox = document.getElementById("chat-box");
    sessionStorage.setItem("griv_chat", chatBox.innerHTML);
}


function appendMessage(sender, text, className) {
    const box = document.getElementById('chat-box');
    const msg = document.createElement('div');
    msg.className = className;

    console.log("Incoming text:", text);

    const parts = text.split(/```(?:\w+)?\n?([\s\S]*?)```/g);
    msg.innerHTML = `<strong>${sender}:</strong><br>`;

    for (let i = 0; i < parts.length; i++) {
        if (i % 2 === 0) {
            msg.innerHTML += `<p>${escapeHTML(parts[i])}</p>`;
        } else {
            msg.innerHTML += `
    <pre class="code-block"><code>${escapeHTML(parts[i])}</code></pre>
    <button class="copy-btn" data-code="${escapeAttr(parts[i])}" onclick="copyCode(this)">Copy</button>
`;

        }
    }

    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
    saveToSession();
}

function escapeAttr(str) {
    return str.replace(/"/g, "&quot;").replace(/'/g, "&apos;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}


function escapeHTML(str) {
    return str.replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeJS(str) {
    return str.replace(/'/g, "\\'").replace(/`/g, "\\`").replace(/\$/g, "\\$");
}

function copyCode(btn) {
    const code = btn.getAttribute('data-code')
        .replace(/&quot;/g, '"')
        .replace(/&apos;/g, "'")
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">");

    navigator.clipboard.writeText(code).then(() => {
        btn.textContent = "Copied!";
        setTimeout(() => btn.textContent = "Copy", 2000);
    }).catch(err => {
        console.error("Copy failed:", err);
        btn.textContent = "Failed!";
    });
}


function appendTypingMessage(sender) {
    const box = document.getElementById('chat-box');
    const typing = document.createElement('div');
    typing.id = 'typing';
    typing.className = 'bot';

    typing.innerHTML = `
        <strong>${sender}:</strong>
        <img src="/static/typecircle2.png" alt="typing..." class="typing-indicator" />
    `;

    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;
}

function removeTypingMessage() {
    const typing = document.getElementById('typing');
    if (typing) typing.remove();
}

async function typeMessage(sender, text, className) {
    const box = document.getElementById('chat-box');
    const msg = document.createElement('div');
    msg.className = className;

    const strong = document.createElement('strong');
    strong.innerText = `${sender}: `;
    msg.appendChild(strong);

    const span = document.createElement('span');
    msg.appendChild(span);
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;

    for (let i = 0; i < text.length; i++) {
        span.textContent += text[i];
        box.scrollTop = box.scrollHeight;
        await new Promise(resolve => setTimeout(resolve, 20));
    }
    saveToSession();
}


document.getElementById('file-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // ✅ Show file name as user message
    appendMessage("You", `📄 ${file.name} - summarize`, "user");

    appendTypingMessage("GRIV");

    try {
        const res = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        removeTypingMessage();
        appendMessage("GRIV", "File Summary: " + data.summary, "bot");

        document.getElementById('summarize-btn').style.display = 'none';
        fileInput.value = "";

    } catch (err) {
        removeTypingMessage();
        appendMessage("GRIV", "⚠️ Error summarizing file.", "bot");
    }
});


document.getElementById('image-upload').addEventListener('change', async function () {
    const image = this.files[0];
    if (!image) return;

    const formData = new FormData();
    formData.append('image', image);

    appendTypingMessage("GRIV");

    const res = await fetch('/upload-image', {
        method: 'POST',
        body: formData
    });

    const data = await res.json();
    removeTypingMessage();
    appendMessage("GRIV", "Image Description: " + data.description, "bot");

    this.value = '';
});

document.getElementById('upload-icon').addEventListener('click', function () {
    const menu = document.getElementById('upload-options');
    menu.style.display = (menu.style.display === 'flex') ? 'none' : 'flex';
    document.getElementById('summarize-btn').style.display = 'none';
});

document.getElementById('file-upload').addEventListener('change', function () {
    if (this.files.length > 0) {
        document.getElementById('summarize-btn').style.display = 'inline-block';
        document.getElementById('upload-options').style.display = 'none';
    }
});

document.getElementById('image-upload').addEventListener('change', function () {
    if (this.files.length > 0) {
        alert("Image selected: " + this.files[0].name);
        document.getElementById('upload-options').style.display = 'none';
        document.getElementById('summarize-btn').style.display = 'none';
    }
});
