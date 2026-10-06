/**
 * RFQ Tracker Client-Side Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
  // Validate quotation deadline is not before received date on form
  const rfqForm = document.getElementById('rfqForm');
  if (rfqForm) {
    const receivedInput = document.getElementById('received_date');
    const deadlineInput = document.getElementById('quotation_deadline');
    const slaInput = document.getElementById('sla_deadline');
    const prioritySelect = document.getElementById('priority');

    const slaDaysMap = {
      'Critical': 2,
      'High': 4,
      'Medium': 7,
      'Low': 14
    };

    function autoUpdateSla() {
      if (receivedInput && receivedInput.value && prioritySelect && slaInput && !slaInput.value) {
        const rec = new Date(receivedInput.value);
        const days = slaDaysMap[prioritySelect.value] || 7;
        rec.setDate(rec.getDate() + days);
        slaInput.value = rec.toISOString().split('T')[0];
      }
    }

    if (prioritySelect) {
      prioritySelect.addEventListener('change', autoUpdateSla);
    }

    rfqForm.addEventListener('submit', (e) => {
      if (receivedInput && deadlineInput && receivedInput.value && deadlineInput.value) {
        const rec = new Date(receivedInput.value);
        const dln = new Date(deadlineInput.value);
        if (dln < rec) {
          e.preventDefault();
          alert('Error: Quotation deadline date cannot be before the received date.');
          deadlineInput.focus();
        }
      }
    });
  }

  // Periodic poll or refresh of notification count (optional, gentle 60s)
  const refreshNotifications = async () => {
    try {
      const res = await fetch('/notifications/unread-count');
      if (res.ok) {
        const data = await res.json();
        const badge = document.querySelector('.notif-badge-dot');
        const sidebarBadge = document.querySelector('#sidebarNotificationCount');
        if (data.count > 0) {
          if (badge) {
            badge.innerText = data.count;
            badge.style.display = 'flex';
          }
          if (sidebarBadge) {
            sidebarBadge.innerText = data.count;
            sidebarBadge.style.display = 'inline';
          }
        } else {
          if (badge) badge.style.display = 'none';
          if (sidebarBadge) sidebarBadge.style.display = 'none';
        }
      }
    } catch (err) {
      // quiet fail on background count check
    }
  };
  if (document.querySelector('.notif-badge-dot')) {
    refreshNotifications();
    setInterval(refreshNotifications, 60000);
  }
});
