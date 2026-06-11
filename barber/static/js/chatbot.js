class ChatBot {
    constructor() {
        this.messages = [];
        this.isOpen = false;
        this.initWidget();
    }

    initWidget() {
        const chatWidget = document.getElementById('chatbot-widget');
        if (!chatWidget) {
            console.error('Chatbot widget element not found');
            return;
        }

        const closeBtn = chatWidget.querySelector('.chatbot-close');
        closeBtn?.addEventListener('click', () => this.toggleWidget());

        const sendBtn = chatWidget.querySelector('.chatbot-input button');
        const input = chatWidget.querySelector('.chatbot-input input');
        sendBtn?.addEventListener('click', () => this.sendMessage());
        input?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleWidget() {
        this.isOpen = !this.isOpen;
        const widget = document.getElementById('chatbot-widget');
        widget.style.display = this.isOpen ? 'flex' : 'none';
    }

    sendMessage() {
        const input = document.querySelector('.chatbot-input input');
        const message = input.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        input.value = '';

        fetch('/chatbot/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                this.addMessage(data.answer, 'bot');
            } else {
                this.addMessage('Greška pri obradi. Pokušajte kasnije.', 'bot');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            this.addMessage('Greška pri slanju poruke.', 'bot');
        });
    }

    addMessage(text, sender) {
        const messagesDiv = document.querySelector('.chatbot-messages');
        const messageEl = document.createElement('div');
        messageEl.classList.add('message', sender);
        messageEl.textContent = text;
        messagesDiv.appendChild(messageEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// Inicijalizuj chatbot
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});
