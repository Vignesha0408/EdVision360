from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import google.generativeai as genai
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey123'

# Enable CORS for all routes
CORS(app, origins=["*"])

# Sample API endpoint
@app.route('/api/endpoint', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Hello from Flask"})

# Example root route
@app.route('/')
def home():
    return render_template_string("<h1>EdVision360 Flask Backend</h1>")

if __name__ == "__main__":
    app.run(debug=True)                const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                messageContent += `
                <div class="message-actions">
                    <span class="timestamp">${timestamp}</span>
                    ${sender === 'error' ? '<button class="retry-btn" onclick="retryLastMessage()"><i class="fas fa-redo"></i> Retry</button>' : ''}
                </div>`;
            }
            
            bubble.innerHTML = messageContent;
            
            if (messageId) {
                bubble.setAttribute('data-message-id', messageId);
            }
            
            row.appendChild(bubble);
            messagesContainer.appendChild(row);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        let lastMessage = '';
        
        function retryLastMessage() {
            if (lastMessage) {
                sendMessage(lastMessage);
            }
        }
        
        function sendMessage(retryMessage = null) {
            const input = document.getElementById('messageInput');
            const message = retryMessage || input.value.trim();
            
            if (!message) {
                appendMessage('Please enter a message to chat with the AI assistant.', 'error', null, true);
                return;
            }
            
            // Store last message for retry functionality
            lastMessage = message;
            
            if (!retryMessage) {
                appendMessage(message, 'user', ++messageCounter);
                input.value = '';
            }
            
            updateConnectionStatus('connecting', 'Sending message to AI...');
            showTypingIndicator();
            
            // Enhanced fetch with comprehensive error handling
            fetch('/ai_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({message: message}),
                timeout: 30000 // 30 second timeout
            })
            .then(response => {
                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                
                if (!response.ok) {
                    throw new Error(`Server responded with status ${response.status}: ${response.statusText}`);
                }
                
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Server did not return JSON response');
                }
                
                return response.json();
            })
            .then(data => {
                hideTypingIndicator();
                updateConnectionStatus('connected', 'AI Assistant Ready');
                
                console.log('AI Response Data:', data);
                
                if (data.status === 'success' && data.response) {
                    appendMessage(data.response, 'assistant', ++messageCounter, true);
                    appendMessage('Message delivered successfully!', 'success');
                } else if (data.response) {
                    appendMessage(data.response, 'error', ++messageCounter, true);
                } else {
                    throw new Error('No response data received from AI');
                }
            })
            .catch(error => {
                hideTypingIndicator();
                updateConnectionStatus('disconnected', 'Connection Error');
                
                console.error('Detailed Error:', error);
                
                let errorMessage;
                if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    errorMessage = 'Unable to connect to the AI service. Please check your internet connection and try again.';
                } else if (error.message.includes('timeout')) {
                    errorMessage = 'The AI service is taking too long to respond. Please try again with a shorter message.';
                } else if (error.message.includes('JSON')) {
                    errorMessage = 'Received an invalid response from the AI service. The service might be temporarily unavailable.';
                } else {
                    errorMessage = `AI Service Error: ${error.message}. Please try again or contact support if the problem persists.`;
                }
                
                appendMessage(errorMessage, 'error', ++messageCounter, true);
            });
        }
        
        function showTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'block';
        }
        
        function hideTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'none';
        }
        
        // Submit on Enter key
        document.getElementById('messageInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Focus on input when page loads and test connection
        window.onload = function() {
            document.getElementById('messageInput').focus();
            
            // Test initial connection
            fetch('/ai_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({message: 'test connection'})
            })
            .then(response => {
                if (response.ok) {
                    updateConnectionStatus('connected', 'AI Assistant Ready');
                } else {
                    updateConnectionStatus('disconnected', 'AI Service Unavailable');
                }
            })
            .catch(() => {
                updateConnectionStatus('disconnected', 'Unable to Connect to AI');
            });
        };
        
        // Periodic connection check
        setInterval(() => {
            if (!isConnected) {
                fetch('/ai_chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: 'ping'})
                })
                .then(response => {
                    if (response.ok) {
                        updateConnectionStatus('connected', 'AI Assistant Ready');
                    }
                })
                .catch(() => {
                    // Still disconnected
                });
            }
        }, 10000); // Check every 10 seconds
    </script>
</body>
</html>
    '''
    return render_template_string(template, 
                                 student_enrollments=student_enrollments,
                                 attendance_records=attendance_records,
                                 students_info=students_info)

if __name__ == '__main__':
    app.run(debug=True)











    

