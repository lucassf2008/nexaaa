/**
 * Nexa SENAI - Funções Globais e Interatividade
 */

document.addEventListener('DOMContentLoaded', () => {
  // Fechamento de alertas flash
  document.querySelectorAll('.alert-close-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const alert = e.target.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Curtir Publicação via AJAX
  document.querySelectorAll('.btn-like-ajax').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault();
      const postId = button.getAttribute('data-post-id');
      try {
        const response = await fetch(`/post/${postId}/curtir`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        if (data.success) {
          const countEl = button.querySelector('.like-counter');
          const iconEl = button.querySelector('i');
          if (countEl) countEl.textContent = data.likes_count;
          if (data.liked) {
            button.classList.add('liked');
            if (iconEl) iconEl.className = 'fas fa-heart text-danger';
          } else {
            button.classList.remove('liked');
            if (iconEl) iconEl.className = 'far fa-heart';
          }
        }
      } catch (err) {
        console.error('Erro ao curtir post:', err);
      }
    });
  });

  // Salvar Vaga via AJAX
  document.querySelectorAll('.save-job-btn').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault();
      const jobId = button.getAttribute('data-job-id');
      try {
        const response = await fetch(`/vagas/${jobId}/salvar`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        if (data.success) {
          const icon = button.querySelector('i');
          if (data.saved) {
            button.classList.add('saved');
            if (icon) icon.className = 'fas fa-bookmark';
          } else {
            button.classList.remove('saved');
            if (icon) icon.className = 'far fa-bookmark';
          }
        }
      } catch (err) {
        console.error('Erro ao salvar vaga:', err);
      }
    });
  });

  // Seguir Empresa via AJAX
  document.querySelectorAll('.btn-follow-ajax').forEach(button => {
    button.addEventListener('click', async (e) => {
      e.preventDefault();
      const companyId = button.getAttribute('data-company-id');
      try {
        const response = await fetch(`/empresa/${companyId}/seguir`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        if (data.success) {
          if (data.following) {
            button.classList.remove('btn-senai');
            button.classList.add('btn-senai-outline');
            button.textContent = 'Seguindo';
          } else {
            button.classList.remove('btn-senai-outline');
            button.classList.add('btn-senai');
            button.textContent = '+ Seguir';
          }
          const followersEl = document.querySelector('.followers-count-number');
          if (followersEl) followersEl.textContent = data.followers_count;
        }
      } catch (err) {
        console.error('Erro ao seguir empresa:', err);
      }
    });
  });

  // Modal helpers
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  };

  // Fechar modal ao clicar fora da caixa
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
      }
    });
  });
});
