from flask import Flask, render_template, request
from flask_socketio import SocketIO
import random
import time
import sys
from methods import generar_problema_aleatorio, evaluar_respuesta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_123'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Estado del servidor
waiting_players = []
active_games = {}

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect(auth=None):
    print(f'\n\nCliente conectado: {request.sid}\n', flush=True)

@socketio.on('disconnect')
def handle_disconnect(auth=None):
    print(f'\n\nCliente desconectado: {request.sid}\n', flush=True)
    cancel_match(request.sid)

def cancel_match(player_id):
    if player_id in waiting_players:
        waiting_players.remove(player_id)
        socketio.emit('match_canceled', room=player_id)

@socketio.on('find_match')
def handle_find_match():
    try:
        player_id = request.sid
        print(f'\nBuscando partida para: {player_id}', flush=True)
        
        if len(waiting_players) >= 1:
            opponent_id = waiting_players.pop()
            game_id = f"game_{random.randint(1000,9999)}"
            
            problema = generar_problema_aleatorio()
            print(f'\nProblema generado ({problema["tipo"]}): {problema["enunciado"][:50]}...', flush=True)
            
            active_games[game_id] = {
                'players': [player_id, opponent_id],
                'problem': problema,
                'answers': {},
                'start_time': time.time()
            }
            
            # Ocultar lobby para ambos jugadores primero
            socketio.emit('hide_lobby', room=player_id)
            socketio.emit('hide_lobby', room=opponent_id)
            
            # Luego iniciar el juego
            socketio.emit('match_found', {
                'game_id': game_id,
                'problem': problema['enunciado'],
                'formato_respuesta': problema['formato']
            }, room=player_id)
            
            socketio.emit('match_found', {
                'game_id': game_id,
                'problem': problema['enunciado'],
                'formato_respuesta': problema['formato']
            }, room=opponent_id)
            
        else:
            waiting_players.append(player_id)
            socketio.emit('waiting', room=player_id)
            print(f'Jugador {player_id} en espera...', flush=True)
            
    except Exception as e:
        print(f'\nERROR en find_match: {str(e)}\n', flush=True, file=sys.stderr)

@socketio.on('submit_answer')
def handle_submit_answer(data):
    game_id = data.get('game_id')
    player_id = request.sid
    answer = data.get('answer')
    
    if not game_id or not answer or game_id not in active_games:
        return
    
    game = active_games[game_id]
    problema = game['problem']
    
    resultado = evaluar_respuesta(problema, answer)
    
    game['answers'][player_id] = {
        'answer': answer,
        'error': resultado['error'],
        'time': time.time() - game['start_time']
    }
    
    if len(game['answers']) == 2:
        determinar_ganador(game_id)

def determinar_ganador(game_id):
    game = active_games[game_id]
    players = game['players']
    
    resultados = []
    for player_id in players:
        resultados.append({
            'player_id': player_id,
            **game['answers'][player_id]
        })
    
    resultados.sort(key=lambda x: (x['error'], x['time']))
    
    response = {
        'results': resultados,
        'correct_answer': game['problem']['solucion']
    }
    
    for player_id in players:
        socketio.emit('game_results', response, room=player_id)
    
    del active_games[game_id]

if __name__ == '__main__':
    socketio.run(app)
