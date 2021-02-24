from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")


users = []
usersTyping = []


@app.route('/')
def sessions():
    return render_template('index.html')


@socketio.on('connect')
def connection(methods=['GET', 'POST']):
    user = {"username": request.args.get('username'), "sid": request.sid}
    print('connected - ' + user.get('username'))
    users.append(user)
    socketio.emit('users_connection_changed', getUsernamesList(users))


@socketio.on('user_message')
def handleUserMessage(msg, methods=['GET', 'POST']):
    socketio.emit('user_message', msg)
    curUserDict = {"username": msg.get('username'), "sid": request.sid}
    usersTyping.remove(curUserDict)
    socketio.emit('user_typing', getUsernamesList(usersTyping))


@socketio.on('disconnect')
def handleUserDisconnect(methods=['GET', 'POST']):
    global users, usersTyping
    def filterFn(x): return x.get('sid') != request.sid
    users = list(filter(filterFn, users))
    usersTyping = list(filter(filterFn, usersTyping))
    socketio.emit('users_connection_changed', getUsernamesList(users))
    socketio.emit('user_typing', getUsernamesList(usersTyping))


@socketio.on('user_typing')
def handleUserTyping(data, methods=['GET', 'POST']):
    curUserDict = {"username": data.get('username'), "sid": request.sid}
    if data.get('msg') != '':
        if not curUserDict in usersTyping:
            usersTyping.append(curUserDict)
            socketio.emit('user_typing', getUsernamesList(usersTyping))
    else:
        if curUserDict in usersTyping:
            usersTyping.remove(curUserDict)
            socketio.emit('user_typing', getUsernamesList(usersTyping))


def getUsernamesList(usersList):
    return list(map(lambda x: x.get('username'), usersList))


if __name__ == '__main__':
    socketio.run(app)
