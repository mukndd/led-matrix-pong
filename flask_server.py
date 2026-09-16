from flask import Flask, request
import threading

# Flask app
app = Flask(__name__)

# Paddle control variable
computer_paddle_move = "none"

@app.route("/")
def index():
    """Serve the control interface."""
    return """
    <h1>Control the Computer Paddle</h1>
    <button onclick="movePaddle('up')">Move Up</button>
    <button onclick="movePaddle('down')">Move Down</button>
    <script>
    function movePaddle(direction) {
        fetch('/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction: direction })
        });
    }
    </script>
    """

@app.route("/control", methods=["POST"])
def control_paddle():
    """Receive paddle control commands."""
    global computer_paddle_move
    data = request.json
    computer_paddle_move = data.get("direction", "none")
    return "", 204  # No content response

def get_computer_move():
    """Get the current paddle movement direction."""
    global computer_paddle_move
    move = computer_paddle_move
    computer_paddle_move = "none"  # Reset after reading
    return move

def run_flask():
    """Run the Flask server."""
    app.run(host="0.0.0.0", port=5000, debug=False)

# Start Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()
