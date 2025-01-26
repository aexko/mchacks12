from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from main import TetrisApp  # Import your Tetris game class

# Flask and SocketIO setup
app = Flask(__name__)
socketio = SocketIO(app)

# Initialize the Tetris game
game = TetrisApp()

@app.route('/')
def index():
    return render_template('index.html')  # Ensure "index.html" exists with your canvas setup

def run_tetris():
    # Ensure game attributes are initialized properly
    game.anim_trigger = False  # Initialize anim_trigger
    game.speed_trigger = False  # Initialize speed_trigger
    
    while True:
        frame_data = []
        # Generate frame data from the game state
        for block in game.tetris.tetromino.blocks:
            frame_data.append({
                'x': int(block.position.x * 50),  # Adjust based on your TILE_SIZE
                'y': int(block.position.y * 50),
                'color': '#FF0000'  # Hardcoded color for simplicity
            })
        socketio.emit('frame', frame_data)  # Send frame data to clients
        game._update()  # Update the game logic

def run_flask():
    socketio.run(app, debug=True, use_reloader=False)

if __name__ == '__main__':
    # Start Flask on the main thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run Tetris logic on another thread
    tetris_thread = Thread(target=run_tetris, daemon=True)
    tetris_thread.start()

    flask_thread.join()
