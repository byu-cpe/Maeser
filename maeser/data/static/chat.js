/*
© 2024 Carson Bush, Blaine Freestone

This file is part of Maeser.

Maeser is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Maeser is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
Maeser. If not, see <https://www.gnu.org/licenses/>.
*/

// Initialize variables
let session = "";
let chat_branch = "";
const form = document.getElementById('message-form');
const input = document.getElementById('message-input');
const chat = document.getElementById('chat');
const scrollButton = document.getElementById('scroll-button');
const newChatButton = document.getElementById('reset-button');
const actionButtons = document.querySelectorAll('.action-button');
const sendButton = document.getElementById('send-button');
const notification = document.getElementById('notification');
const tabButton = document.getElementById('tab');
const sidebar = document.getElementById('side-bar');
const sidebarLinks = document.getElementById('side-bar-links');
const primaryView = document.getElementById('chat-application');
const rateLimit = rateLimiting ? document.getElementById('rate-limit') : null;
const chatHeadIcon = chatHead ? chatHead : '/maeser/static/maeser-part.png';
const logoutButton = document.getElementById('logout-button');
const trainButton = document.getElementById('train-button');
const logsButton = document.getElementById('logs-button');
const userManagementButton = document.getElementById('user-management-button');

// Notification functions
function showNotification(message, isSuccess = false, isCritical = false) {
    notification.innerHTML = `<p>${message}</p>`;
    notification.className = isCritical ? 'critical' : isSuccess ? 'success' : '';
    if (!isCritical) {
        notification.classList.add('show');
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
    } else {
        notification.innerHTML += '<p>Please refresh the page.</p>';
    }
}

function showCriticalNotification(message) {
    showNotification(message, false, true);
    disableForm();
    hideButtons();
}

function hideNotification() {
    notification.classList.remove('show', 'critical');
}

// Input management functions
function enableForm() {
    form.classList.remove('hide');
    input.disabled = false;
    newChatButton.disabled = false;
    sendButton.disabled = false;
    input.focus();
}

function disableForm() {
    form.classList.add('hide');
    input.disabled = true;
    sendButton.disabled = true;
    newChatButton.disabled = true;
}

function hideButtons() {
    actionButtons.forEach(button => {
        button.disabled = true;
    });
}

function showButtons() {
    actionButtons.forEach(button => {
        button.disabled = false;
    });
}

function highlightButton(selectedButton) {
    actionButtons.forEach(button => {
        button.classList.toggle('button-highlighted', button === selectedButton);
        button.classList.toggle('button-unimportant', button !== selectedButton);
    });
}

function unhighlightButtons() {
    actionButtons.forEach(button => {
        button.classList.remove('button-highlighted');
        button.classList.remove('button-unimportant');
    });
}

// Event listeners
actionButtons.forEach(button => {
    button.addEventListener('click', () => {
        const action = button.getAttribute('data-action');
        console.log(`Okay, I'll help you with ${action}!`);
        addMessageBubble(`Okay, I'll help you with ${action}!`, 'receiver');
        enableForm();
        input.focus();
        highlightButton(button);
        requestNewSession(action);
        hideButtons();
    });
});

form.addEventListener('submit', function(event) {
    event.preventDefault();
    sendMessage();
});

input.addEventListener('input', function(event) {
    if (event.inputType === 'insertParagraph') {
        input.value = input.value.replace(/\n/g, '');
    }
    this.style.height = 'auto';
    const msg_box_height = Math.min(this.scrollHeight, 200);
    this.style.height = `${msg_box_height}px`;
});

input.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// Session management functions
function requestNewSession(action) {
    const ses_req_type = {
        type: "new",
        from: "Maeser Frontend",
        action: action
    };
    fetch("/req_session", {
        method: "POST",
        body: JSON.stringify(ses_req_type),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
        .then(response => {
            if (!response.ok) {
                const errMsg = response.status >= 500 ? `Internal Server Error (${response.status})` : `Network response was not ok (${response.status})`;
                throw new Error(errMsg);
            }
            return response.json();
        })
        .then(json => {
            if (json && json.response === "invalid") {
                console.error(`Invalid session! Additional details: ${json.details}`);
                showCriticalNotification("Invalid session!");
            } else {
                chat_branch = action;
                session = json.response;
                console.log(`Your session ID is ${session}`);
                console.log(json);
                showNotification("Session started successfully.", true);
                addChatLink(session, action);
            }
        })
        .catch(error => {
            console.error('Error fetching session:', error);
            const errorMsg = error.message.includes('Internal Server Error') ? 'A server error occurred.' : `Error fetching session: ${error.message}`;
            showCriticalNotification(errorMsg);
        });
}

// Message functions
function sendMessage() {
    const messageText = input.value.trim();
    if (messageText !== '') {
        const messageContainer = addMessageBubble(messageText, 'sender');
        input.value = '';
        input.style.height = 'auto';
        disableForm();
        
        fetch(`/msg/${session}`, {
            method: "POST",
            body: JSON.stringify({
                message: messageText,
                from: "Maeser Frontend",
                action: chat_branch,
                session: session,
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        })
            .then(response => {
                if (!response.ok) {
                    let errMsg;
                    if (response.status >= 500) {
                        if (response.status === 503) {
                            errMsg = 'Service Unavailable (503). You have exceeded your server-wide OpenAI token quota.';
                        } else if (response.status === 502) {
                            errMsg = 'Bad Gateway (502). The web server is running, but Maeser cannot be accessed.';
                        } else {
                            errMsg = `Internal Server Error (${response.status})`;
                        }
                    } else if (response.status >= 400) {
                        if (response.status === 429) {
                            errMsg = 'Too Many Requests (429). You have exceeded your rate limit.';
                        } else {
                            errMsg = `Client Error (${response.status})`;
                        }
                    } else if (response.status >= 300) {
                        errMsg = `Redirection Error (${response.status})`;
                    } else {
                        errMsg = `Network response was not ok (${response.status})`;
                    }
                    throw new Error(errMsg);
                }
                return response.json();
            })
            .then(json => {
                rateLimiting ? updateRequestsRemaining(json.requests_remaining) : null;
                addMessageBubble(json.response, 'receiver', true, index=json.index);
                console.log(json);
                enableForm();
            })
            .catch(error => {
                console.error('Error sending message:', error);
                if (error.message.includes('Internal Server Error')) {
                    showCriticalNotification(error.message);
                } else {
                    showNotification(`Error sending message: ${error.message}`);
                    showNetworkErrorIcon(messageContainer);
                    enableForm();
                }
            });
    }
}

// Add this function to handle the like and dislike button clicks
function handleLikeDislike(event) {
    const button = event.target.closest('button');
    if (button.classList.contains('selected')) {return;}
    const messageContainer = button.closest('.message-container');
    const likerContainer = button.closest('.like-dislike-container');
    const isLike = button.classList.contains('like-button');
    const messageBubble = messageContainer.querySelector('.message-bubble');
    const messageText = messageBubble.textContent;
    const messageIndex = messageBubble.getAttribute('index');

    console.log(`${isLike ? 'Liked' : 'Disliked'} message: ${messageText} at index ${messageIndex}`);

    fetch('/feedback', {
        method: 'POST',
        body: JSON.stringify({
            message: messageText,
            like: isLike,
            index: messageIndex,
            session_id: session,
            branch: chat_branch
        }),
        headers: {
            'Content-type': 'application/json; charset=UTF-8'
        }
    })
    .then(response => response.json())
    .then(json => {
        console.log('Feedback response:', json);
        showNotification('Feedback sent!', true);
        likerContainer.childNodes.forEach(butt => {butt.classList.remove('selected');})
        button.classList.add('selected');
    })
    .catch(error => {
        console.error('Error sending feedback:', error);
        showNotification('Error sending feedback. Try again later.', false)
    });
}

function buildFeedbackContainer() {
    const container = document.createElement('div');
    container.classList.add('like-dislike-container');

    const likeButton = document.createElement('button');
    likeButton.classList.add('like-button', 'btn', 'btn-link', 'p-0');
    likeButton.innerHTML = '<i class="bi bi-hand-thumbs-up-fill"></i>';
    
    const dislikeButton = document.createElement('button');
    dislikeButton.classList.add('dislike-button', 'btn', 'btn-link', 'p-0');
    dislikeButton.innerHTML = '<i class="bi bi-hand-thumbs-down-fill"></i>';
    
    container.appendChild(dislikeButton);
    container.appendChild(likeButton);

    likeButton.addEventListener('click', handleLikeDislike);
    dislikeButton.addEventListener('click', handleLikeDislike);

    return container;
}

function addMessageBubble(message, type, includeButtons = false, index=false) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('flex', 'message-container', type);
    const messageControls = document.createElement('div');
    messageControls.classList.add('message-controls');
    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble');

    if (type === "sender") {
        message.split('\n').forEach(line => {
            const p = document.createElement('p');
            p.textContent = line;
            messageBubble.appendChild(p);
        });
    } else {
        const receiverIcon = document.createElement('img');
        receiverIcon.src = chatHeadIcon;
        messageContainer.appendChild(receiverIcon);
        messageBubble.innerHTML = message;
    }

    messageBubble.setAttribute('index', index);

    messageContainer.appendChild(messageControls)
    messageControls.appendChild(messageBubble);

    if (includeButtons && type === 'receiver') {
        const likeDislikeContainer = buildFeedbackContainer();
        messageControls.appendChild(likeDislikeContainer);
    }

    chat.appendChild(messageContainer);
    scrollToBottom();
    return messageContainer;
}

function showNetworkErrorIcon(messageContainer) {
    const errorIcon = document.createElement('i');
    errorIcon.classList.add('bi', 'bi-exclamation-circle-fill', 'network-error-icon');
    messageContainer.style.flexDirection = 'row-reverse';
    messageContainer.style.alignItems = 'end';
    messageContainer.appendChild(errorIcon);
}

// Scroll functions
window.scrollToBottom = function() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
    updateScrollButtonVisibility();
}

function updateScrollButtonVisibility() {
    const isNearBottom = window.scrollY >= (document.documentElement.scrollHeight - document.documentElement.clientHeight * 2);
    scrollButton.classList.toggle('hide', isNearBottom);
}

newChatButton.addEventListener('click', event => {
    clearChat();
});

// Event listeners for the tab button
tabButton.addEventListener('click', event => {
    sidebar.classList.toggle('hide');
    primaryView.classList.toggle('sidebar-open');
});

/// Function to attach event listener to a chat history button
function attachChatHistoryButtonListener(button) {
    button.addEventListener('click', function() {
        const sessionData = this.getAttribute('data-session');
        const branchData = this.getAttribute('data-branch');

        // Prepare the data to be sent in the POST request
        const requestData = { session: sessionData, branch: branchData };

        // Using the Fetch API to send the POST request
        fetch('conversation_history', {
            method: 'POST', // Specify the method
            headers: {
                'Content-Type': 'application/json', // Specify the content type
            },
            body: JSON.stringify(requestData), // Convert the JavaScript object to a JSON string
        })
        .then(response => response.json()) // Parse the JSON response
        .then(responseData => {
            console.log('Success:', responseData); // Handle success
            clearChat();
            // add session to response data
            responseData.session = sessionData;
            loadConversationHistory(responseData);
        })
        .catch((error) => {
            console.error('Error:', error); // Handle errors
            showNotification('Error getting conversation history from server.\nPlease reload and try again.', false)
        });
    });
}

// Event listeners for previous chats in the side tab
document.querySelectorAll('.chat-history-button').forEach(attachChatHistoryButtonListener);

// Clear chat function
function clearChat() {
    chat.innerHTML = '';
    disableForm();
    unhighlightButtons();
    showButtons();
}

// Load conversation history function
function loadConversationHistory(conversationHistory) {
    // set branch button and disable others
    branch = conversationHistory.branch;
    actionButtons.forEach(button => {
        if (button.getAttribute('data-action') === branch) {
            const action = button.getAttribute('data-action');
            addMessageBubble(`Okay, I'll help you with ${action}!`, 'receiver');
            input.focus();
            enableForm();
            hideButtons();

            highlightButton(button);
        } else {
            button.disabled = true;
        }
    });

    // load messages if any
    if (conversationHistory.messages) {
        conversationHistory.messages.forEach((message, index) => {
            type = message.role === 'user' ? 'sender' : 'receiver';
            addMessageBubble(message.content, type, true, index);
        });
    }
    session = conversationHistory.session;
    chat_branch = branch;
}

function addChatLink(session, branch) {
    // create a new button container
    const chatHistoryButtonContainer = document.createElement('div');
    chatHistoryButtonContainer.classList.add('chat-history-button-container');

    // create a new button and add its child elements
    const chatHistoryButton = document.createElement('button');
    chatHistoryButton.classList.add('chat-history-button');
    chatHistoryButton.setAttribute('data-session', session);
    chatHistoryButton.setAttribute('data-branch', branch);
    const chatHistoryName = document.createElement('p');
    const chatHistoryBranch = document.createElement('p');
    chatHistoryName.textContent = `New Chat`;
    chatHistoryName.classList.add('chat-history-name');
    chatHistoryBranch.textContent = branch;
    chatHistoryBranch.classList.add('chat-history-branch');
    chatHistoryButton.appendChild(chatHistoryName);
    chatHistoryButton.appendChild(chatHistoryBranch);
    
    // attach event listener to the button and append it to the button container
    attachChatHistoryButtonListener(chatHistoryButton);
    chatHistoryButtonContainer.appendChild(chatHistoryButton);
    
    // add the button container to the top of the sidebar links
    sidebarLinks.insertBefore(chatHistoryButtonContainer, sidebarLinks.firstChild);
}

if (rateLimiting) {
    function updateRequestsRemaining(value) {
        const requestsRemainingSpan = document.getElementById('requests-remaining');
        requestsRemainingSpan.textContent = value;
    }
}

if (rateLimiting) {
    // interval for requesting new rate limit information
    setInterval(() => {
        fetch('/get_requests_remaining', {
            method: 'GET',
            headers: {
            'Content-Type': 'application/json',
            // Add any other headers like authorization if needed
            }
        })
        .then(response => response.json())
        .then(data => {
            updateRequestsRemaining(data.requests_remaining);
            console.log('Success:', data)
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }, requestsRemainingIntervalMs);
}

// Event listeners for scroll events
window.addEventListener('scroll', updateScrollButtonVisibility);
window.addEventListener('resize', updateScrollButtonVisibility);

logoutButton.addEventListener('click', function() {
    window.location.href = '/logout';
  });

trainButton.addEventListener('click', function() {
    window.location.href = '/train';
});

logsButton.addEventListener('click', function() {
    window.location.href = '/logs';
});

userManagementButton.addEventListener('click', function() {
    window.location.href = '/users';
});