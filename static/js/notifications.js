document.addEventListener('DOMContentLoaded', function() {
    const notificationList = document.getElementById('notificationList');
    const notificationBadge = document.getElementById('notification-badge');
    const notificationCount = document.getElementById('notification-count');

    function fetchNotifications() {
        if (!notificationList || !notificationBadge || !notificationCount) {
            return; // Exit if elements are not found
        }

        document.dispatchEvent(new CustomEvent('fetchStart'));

        fetch('/patients/notifications/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                const notifications = Array.isArray(data) ? data : [];
                
                // Update notification badge
                if (notifications.length > 0) {
                    notificationCount.textContent = notifications.length;
                    notificationBadge.classList.remove('d-none');
                } else {
                    notificationBadge.classList.add('d-none');
                }

                // Build dropdown HTML
                let listHtml = '<li><h6 class="dropdown-header">اعلان‌های اخیر</h6></li>';
                if (notifications.length === 0) {
                    listHtml += '<li><a class="dropdown-item" href="#">هیچ اعلانی وجود ندارد</a></li>';
                } else {
                    listHtml += notifications.map(notification =>
                        `<li><a class="dropdown-item" href="${notification.url || '#'}">${notification.message}</a></li>`
                    ).join('');
                }
                listHtml += '<li><hr class="dropdown-divider"></li>';
                listHtml += '<li><a class="dropdown-item text-center" href="#">مشاهده همه اعلان‌ها</a></li>';
                
                notificationList.innerHTML = listHtml;
            })
            .catch(error => {
                console.error('Notification fetch failed:', error);
                notificationList.innerHTML = `
                    <li><h6 class="dropdown-header">اعلان‌های اخیر</h6></li>
                    <li><a class="dropdown-item text-danger" href="#">خطا در بارگذاری اعلان‌ها</a></li>
                `;
                notificationBadge.classList.add('d-none');
            })
            .finally(() => {
                document.dispatchEvent(new CustomEvent('fetchEnd'));
            });
    }

    fetchNotifications();
    // Uncomment the line below to refresh notifications every 60 seconds
    // setInterval(fetchNotifications, 60000);
});
