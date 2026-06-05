from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Using socketio.run allows the WebSocket connections to process concurrently
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)