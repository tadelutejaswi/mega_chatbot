document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatWindow = document.getElementById('chatWindow');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const voiceButton = document.getElementById('voiceButton');
    const clearButton = document.getElementById('clearButton');
    const themeButton = document.getElementById('themeButton');
    const randomQuestion = document.getElementById('randomQuestion');
    
    // Variables
    let isDarkMode = localStorage.getItem('darkMode') === 'true';
    let recognition;
    let isListening = false;
    
    // Initialize
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        themeButton.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Load random question
    fetchRandomQuestion();
    
    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    voiceButton.addEventListener('click', toggleVoiceRecognition);
    clearButton.addEventListener('click', clearChat);
    themeButton.addEventListener('click', toggleTheme);
    randomQuestion.addEventListener('click', useExampleQuestion);
    
    // Functions
    function fetchRandomQuestion() {
        fetch('http://localhost:5000/random-question')
            .then(response => response.json())
            .then(data => {
                if (data.question) {
                    randomQuestion.textContent = data.question;
                } else {
                    randomQuestion.textContent = "What can you do?";
                }
            })
            .catch(error => {
                console.error('Error fetching random question:', error);
                randomQuestion.textContent = "What can you do?";
            });
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send to backend
        fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, user_id: 'web_user' }),
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            removeTypingIndicator();
            addMessage("Sorry, I'm having trouble connecting to the server.", 'bot');
            console.error('Error:', error);
        });
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.innerHTML = `
            <div class="${sender}-message">${text}</div>
            <div class="message-time">${getCurrentTime()}</div>
        `;
        
        // Remove welcome message if it's the first user message
        if (sender === 'user' && document.querySelector('.welcome-message')) {
            document.querySelector('.welcome-message').remove();
        }
        
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;
        chatWindow.appendChild(typingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    function toggleVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
            addMessage("Your browser doesn't support speech recognition.", 'bot');
            return;
        }
        
        if (!isListening) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onstart = function() {
                isListening = true;
                voiceButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                addMessage("Listening...", 'bot');
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                sendMessage();
            };
            
            recognition.onerror = function(event) {
                addMessage("Error occurred in recognition: " + event.error, 'bot');
                stopVoiceRecognition();
            };
            
            recognition.onend = function() {
                stopVoiceRecognition();
            };
            
            recognition.start();
        } else {
            stopVoiceRecognition();
        }
    }
    
    function stopVoiceRecognition() {
        if (recognition) {
            recognition.stop();
        }
        isListening = false;
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
    }
    
    function clearChat() {
        chatWindow.innerHTML = `
            <div class="welcome-message">
                <p>Hello! I'm MegaBot, your advanced AI assistant. Ask me anything!</p>
                <p>Try questions like: <span class="example-question" id="randomQuestion">${randomQuestion.textContent}</span></p>
            </div>
        `;
        // Reattach event listener to the new random question element
        document.getElementById('randomQuestion').addEventListener('click', useExampleQuestion);
    }
    
    function toggleTheme() {
        isDarkMode = !isDarkMode;
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        
        if (isDarkMode) {
            themeButton.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            themeButton.innerHTML = '<i class="fas fa-moon"></i>';
        }
    }
    
    function useExampleQuestion() {
        userInput.value = randomQuestion.textContent;
        userInput.focus();
    }
});
