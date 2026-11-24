/**
 * Nexa SENAI - Sistema de Mensagens e Chat em Tempo Real
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-send-form');
  const chatMessagesList = document.getElementById('chat-messages-container');
  const chatInput = document.getElementById('chat-message-input');

  if (chatForm && chatMessagesList) {
    // Rola para a mensagem mais recente
    chatMessagesList.scrollTop = chatMessagesList.scrollHeight;

    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const content = chatInput.value.trim();
      const receiverId = document.getElementById('chat-receiver-id').value;

      if (!content) return;

      chatInput.value = '';

      try {
        const formData = new FormData();
        formData.append('receiver_id', receiverId);
        formData.append('content', content);

        const response = await fetch('/mensagens/enviar', {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData
        });

        const data = await response.json();
        if (data.success) {
          const msg = data.message;
          const msgElement = document.createElement('div');
          msgElement.className = 'chat-bubble-row sender';
          msgElement.innerHTML = `
            <div class="chat-bubble sender">
              <p class="chat-text">${escapeHtml(msg.content)}</p>
              <span class="chat-time">${msg.time}</span>
            </div>
          `;
          chatMessagesList.appendChild(msgElement);
          chatMessagesList.scrollTop = chatMessagesList.scrollHeight;
        }
      } catch (err) {
        console.error('Erro ao enviar mensagem:', err);
      }
    });

    // Polling a cada 4 segundos se houver chat aberto
    const receiverIdInput = document.getElementById('chat-receiver-id');
    if (receiverIdInput && receiverIdInput.value) {
      const activeReceiverId = receiverIdInput.value;
      setInterval(async () => {
        try {
          const res = await fetch(`/mensagens/api/conversa/${activeReceiverId}`);
          const resData = await res.json();
          if (resData.messages) {
            renderChatMessages(resData.messages);
          }
        } catch (e) {
          // Erro silencioso em background
        }
      }, 4000);
    }
  }

  function renderChatMessages(messages) {
    if (!chatMessagesList) return;
    const currentCount = chatMessagesList.querySelectorAll('.chat-bubble-row').length;
    if (messages.length > currentCount) {
      chatMessagesList.innerHTML = '';
      messages.forEach(msg => {
        const row = document.createElement('div');
        row.className = `chat-bubble-row ${msg.is_sender ? 'sender' : 'receiver'}`;
        row.innerHTML = `
          <div class="chat-bubble ${msg.is_sender ? 'sender' : 'receiver'}">
            <p class="chat-text">${escapeHtml(msg.content)}</p>
            <span class="chat-time">${msg.time}</span>
          </div>
        `;
        chatMessagesList.appendChild(row);
      });
      chatMessagesList.scrollTop = chatMessagesList.scrollHeight;
    }
  }

  function escapeHtml(string) {
    const div = document.createElement('div');
    div.innerText = string;
    return div.innerHTML;
  }
});
