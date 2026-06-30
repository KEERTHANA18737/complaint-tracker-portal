/**
 * main.js – ComplaintTracker global JavaScript
 * Handles sidebar toggle, auto-dismiss alerts, CSRF helpers.
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar toggle for mobile ──────────────────────────────────
  const toggleBtn = document.querySelector('.navbar-toggler');
  const sidebar   = document.getElementById('sidebar');

  if (toggleBtn && sidebar) {
    // Separate sidebar toggle from the Bootstrap navbar toggle
    const sidebarToggle = document.createElement('button');
    sidebarToggle.className = 'btn btn-link text-white d-lg-none me-2';
    sidebarToggle.innerHTML = '<i class="bi bi-layout-sidebar fs-5"></i>';
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    toggleBtn.before(sidebarToggle);

    // Close sidebar when clicking outside
    document.addEventListener('click', function (e) {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Auto-dismiss alerts after 5 s ─────────────────────────────
  document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert?.close();
    }, 5000);
  });

  // ── Active nav link highlighting ───────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.ct-sidebar-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── CSRF helper for fetch() ────────────────────────────────────
  window.getCsrfToken = function () {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  };

  // ── Mark notification read via fetch ──────────────────────────
  document.querySelectorAll('.ct-mark-read').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = btn.dataset.url;
      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken':      getCsrfToken(),
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
      .then(r => r.json())
      .then(() => {
        btn.closest('.ct-notification-item')?.classList.remove('ct-notification-unread');
        const badge = document.querySelector('.ct-notif-badge');
        if (badge) {
          const count = parseInt(badge.textContent) - 1;
          count > 0 ? (badge.textContent = count) : badge.remove();
        }
      });
    });
  });

  // ── Client-side duplicate-submit prevention ────────────────────
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function () {
      const btn = form.querySelector('[type=submit]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Please wait…';
      }
    });
  });

});
