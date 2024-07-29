// user-management.js

// Wait for the DOM to be fully loaded before executing the script
document.addEventListener('DOMContentLoaded', function() {
    // Constants
    // const manageUserAPI = '/path/to/manage/user/api'; // Replace with actual API endpoint

    // DOM Elements
    const userGrid = document.getElementById('user-grid');
    // const tabButtons = document.querySelectorAll('.tab-button');
    // const tabContents = document.querySelectorAll('.tab-content');
    const authFilterButtons = document.querySelectorAll('.auth-filters > .tab-button');
    const adminFilterButtons = document.querySelectorAll('.admin-filters > .tab-button');
    const banFilterButtons = document.querySelectorAll('.ban-filters > .tab-button');

    // Event Listeners
    // tabButtons.forEach(button => {
    //     button.addEventListener('click', handleTabClick);
    // });

    [authFilterButtons, adminFilterButtons, banFilterButtons].forEach(buttonGroup => {
        buttonGroup.forEach(button => {
            button.addEventListener('click', () => {
                updateActiveFilter(button, buttonGroup);
                fetchAndDisplayUsers();
            });
        });
    });

    // Initial fetch and display of users
    fetchAndDisplayUsers();

    // Tab Functionality
    // function handleTabClick() {
    //     const tabId = this.getAttribute('data-tab');
        
    //     tabButtons.forEach(btn => btn.classList.remove('active'));
    //     tabContents.forEach(content => content.classList.add('hide'));

    //     this.classList.add('active');
    //     document.getElementById(tabId).classList.remove('hide');
    // }

    // Filter Functionality
    function updateActiveFilter(clickedButton, buttonGroup) {
        buttonGroup.forEach(btn => btn.classList.remove('active'));
        clickedButton.classList.add('active');
    }

    // User Management Functions
    function fetchAndDisplayUsers() {
        const selectedAuthFilter = document.querySelector('.auth-filters .active')?.getAttribute('filter') || 'all';
        const selectedAdminFilter = document.querySelector('.admin-filters .active')?.getAttribute('filter') || 'all';
        const selectedBanFilter = document.querySelector('.ban-filters .active')?.getAttribute('filter') || 'all';

        jsonReq = JSON.stringify({
            type: 'list-users',
            'auth-filter': selectedAuthFilter,
            'admin-filter': selectedAdminFilter,
            'banned-filter': selectedBanFilter
        });

        console.log(jsonReq);

        fetch(manageUserAPI, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: jsonReq
        })
        .then(response => response.json())
        .then(users => {
            userGrid.innerHTML = '';
            users.forEach(user => {
                const userElement = createUserElement(user);
                userGrid.appendChild(userElement);
            });
        })
        .catch(error => console.error('Error fetching users:', error));
    }

    function createUserElement(user) {
        const userElement = document.createElement('div');
        userElement.classList.add('user-item');
        userElement.innerHTML = `
            <h3>${user.username}</h3>
            <p>Email: ${user.email}</p>
            <p>Admin: ${user.is_admin ? 'Yes' : 'No'}</p>
            <p>Banned: ${user.is_banned ? 'Yes' : 'No'}</p>
            <p>Requests left: ${user.requests_left}</p>
        `;
        userElement.addEventListener('click', () => showUserModal(user));
        return userElement;
    }

    function showUserModal(user) {
        const modal = document.createElement('div');
        modal.classList.add('modal');
        modal.innerHTML = `
            <div class="modal-content">
                <h2>User Options: ${user.username}</h2>
                <button id="toggle-admin">Toggle Admin Status</button>
                <button id="toggle-ban">Toggle Ban Status</button>
                <div class="request-adjust">
                    <button id="decrease-requests">-</button>
                    <span>Requests: ${user.requests_left}</span>
                    <button id="increase-requests">+</button>
                </div>
                <button id="remove-user">Remove User</button>
                <button id="close-modal">Close</button>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('#toggle-admin').addEventListener('click', () => updateUserStatus(user.id, 'toggle-admin'));
        modal.querySelector('#toggle-ban').addEventListener('click', () => updateUserStatus(user.id, 'toggle-ban'));
        modal.querySelector('#decrease-requests').addEventListener('click', () => updateUserRequests(user.id, 'decrease'));
        modal.querySelector('#increase-requests').addEventListener('click', () => updateUserRequests(user.id, 'increase'));
        modal.querySelector('#remove-user').addEventListener('click', () => removeUser(user.id));
        modal.querySelector('#close-modal').addEventListener('click', () => modal.remove());
    }

    function updateUserStatus(userId, action) {
        fetch(manageUserAPI, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: action, user_id: userId })
        })
        .then(response => response.json())
        .then(result => {
            console.log(`User status updated: ${result.message}`);
            fetchAndDisplayUsers();
        })
        .catch(error => console.error('Error updating user status:', error));
    }

    function updateUserRequests(userId, action) {
        fetch(manageUserAPI, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'update-requests', user_id: userId, action: action })
        })
        .then(response => response.json())
        .then(result => {
            console.log(`User requests updated: ${result.message}`);
            fetchAndDisplayUsers();
        })
        .catch(error => console.error('Error updating user requests:', error));
    }

    function removeUser(userId) {
        if (confirm('Are you sure you want to remove this user?')) {
            fetch(manageUserAPI, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'remove-user', user_id: userId })
            })
            .then(response => response.json())
            .then(result => {
                console.log(`User removed: ${result.message}`);
                fetchAndDisplayUsers();
            })
            .catch(error => console.error('Error removing user:', error));
        }
    }

    // New functions that need HTML changes
    
    // Note: This function needs a corresponding HTML button to trigger it
    function fetchUser() {
        const userId = prompt("Enter user ID to fetch:");
        if (userId) {
            fetch(manageUserAPI, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'fetch-user', user_id: userId })
            })
            .then(response => response.json())
            .then(user => {
                console.log('Fetched user:', user);
                // TODO: Display fetched user information
            })
            .catch(error => console.error('Error fetching user:', error));
        }
    }

    // Note: This function needs corresponding HTML buttons to trigger listing and executing the clean-up
    function handleCacheCleanup() {
        fetch(manageUserAPI, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'list-cleanables' })
        })
        .then(response => response.json())
        .then(cleanableUsers => {
            console.log('Cleanable users:', cleanableUsers);
            // TODO: Display list of cleanable users
            if (confirm('Are you sure you want to remove these users from the cache?')) {
                executeCacheCleanup();
            }
        })
        .catch(error => console.error('Error listing cleanable users:', error));
    }

    function executeCacheCleanup() {
        fetch(manageUserAPI, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'clean-cache' })
        })
        .then(response => response.json())
        .then(result => {
            console.log('Cache cleanup result:', result);
            fetchAndDisplayUsers();
        })
        .catch(error => console.error('Error cleaning cache:', error));
    }

    // Expose functions that need to be called from HTML
    window.fetchUser = fetchUser;
    window.handleCacheCleanup = handleCacheCleanup;
});