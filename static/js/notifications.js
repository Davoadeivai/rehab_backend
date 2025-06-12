document.addEventListener('DOMContentLoaded', function() {
    const notificationList = document.getElementById('notificationList');

    if (notificationList) {
        fetch('/patients/notifications/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.length === 0) {
                    notificationList.innerHTML = '<li><a class="dropdown-item" href="#">هیچ اعلانی وجود ندارد</a></li>';
                } else {
                    notificationList.innerHTML = data.map(notification =>
                        `<li><a class="dropdown-item" href="#">${notification.title} - ${notification.message}</a></li>`
                    ).join('');
                }
            })
            .catch(error => console.error('Notification fetch failed:', error));
    }
});
