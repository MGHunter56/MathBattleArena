document.addEventListener('DOMContentLoaded', () => {
    // Elementos del DOM
    const lobby = document.getElementById('lobby');
    const gamePanel = document.getElementById('gamePanel');
    const resultsPanel = document.getElementById('resultsPanel');
    const findMatchBtn = document.getElementById('findMatchBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const waitingMsg = document.getElementById('waitingMsg');
    const submitBtn = document.getElementById('submitBtn');
    const playAgainBtn = document.getElementById('playAgainBtn');
    const answerInput = document.getElementById('answerInput');
    
    // Estado del juego
    const gameState = {
        socket: null,
        gameId: null,
        timer: null,
        startTime: null,
        playerId: null,
        currentTime: 0
    };
    
    // Inicializar Socket.IO
    function initSocket() {
        gameState.socket = io();
        
        gameState.socket.on('connect', () => {
            gameState.playerId = gameState.socket.id;
            console.log('Conectado al servidor con ID:', gameState.playerId);
        });
        
        gameState.socket.on('waiting', () => {
            lobby.classList.add('hidden');
            waitingMsg.classList.remove('hidden');
            console.log('Esperando oponente...');
        });
        
        gameState.socket.on('hide_lobby', () => {
            lobby.classList.add('hidden');
            waitingMsg.classList.add('hidden');
            console.log('Ocultando lobby...');
        });
        
        gameState.socket.on('match_found', (data) => {
            gameState.gameId = data.game_id;
            startGame(data.problem, data.formato_respuesta);
        });
        
        gameState.socket.on('game_results', (data) => {
            showResults(data);
        });
        
        gameState.socket.on('match_canceled', () => {
            waitingMsg.classList.add('hidden');
            lobby.classList.remove('hidden');
            findMatchBtn.disabled = false;
            console.log('Búsqueda cancelada');
        });
    }
    
    // Iniciar juego
	function startGame(problem, format) {
		gamePanel.classList.remove('hidden');
    
		// Usar pre para mantener formato de matriz
		document.getElementById('problemStatement').innerHTML = 
			`<pre>${problem}</pre>`;
    
		document.getElementById('answerFormat').textContent = format;
		answerInput.placeholder = `Ingresa ${problem.split('Tamaño: ')[1].split('x')[0]} valores...`;
		answerInput.value = '';
		answerInput.focus();
		startTimer();
}
    
    // Temporizador
    function startTimer() {
        gameState.startTime = Date.now();
        gameState.timer = setInterval(() => {
            gameState.currentTime = (Date.now() - gameState.startTime) / 1000;
            document.getElementById('timerDisplay').textContent = gameState.currentTime.toFixed(2);
        }, 10);
    }
    
    function stopTimer() {
        if (gameState.timer) {
            clearInterval(gameState.timer);
            gameState.timer = null;
        }
    }
    
    // Mostrar resultados
    function showResults(data) {
        stopTimer();
        
        const playerResult = data.results.find(r => r.player_id === gameState.playerId);
        const opponentResult = data.results.find(r => r.player_id !== gameState.playerId);
        
        document.getElementById('playerAnswerText').textContent = `Respuesta: ${playerResult.answer}`;
        document.getElementById('playerTime').textContent = `Tiempo: ${playerResult.time.toFixed(2)}s`;
        document.getElementById('playerError').textContent = `Error: ${playerResult.error.toExponential(2)}`;
        
        document.getElementById('opponentAnswerText').textContent = `Respuesta: ${opponentResult.answer}`;
        document.getElementById('opponentTime').textContent = `Tiempo: ${opponentResult.time.toFixed(2)}s`;
        document.getElementById('opponentError').textContent = `Error: ${opponentResult.error.toExponential(2)}`;
        
        const winnerDiv = document.getElementById('winnerAnnouncement');
        if (playerResult.error < opponentResult.error || 
            (playerResult.error === opponentResult.error && playerResult.time < opponentResult.time)) {
            winnerDiv.textContent = '¡Ganaste esta ronda! 🎉';
            winnerDiv.style.color = '#27ae60';
        } else {
            winnerDiv.textContent = 'El oponente ganó esta ronda';
            winnerDiv.style.color = '#e74c3c';
        }
        
        document.getElementById('correctSolution').textContent = `Solución correcta: ${data.correct_answer}`;
        
        gamePanel.classList.add('hidden');
        resultsPanel.classList.remove('hidden');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar';
    }
    
    // Manejadores de eventos
    findMatchBtn.addEventListener('click', () => {
        findMatchBtn.disabled = true;
        gameState.socket.emit('find_match');
        console.log('Buscando partida...');
    });
    
    cancelBtn.addEventListener('click', () => {
        gameState.socket.emit('cancel_match');
    });
    
    submitBtn.addEventListener('click', () => {
        const answer = answerInput.value.trim();
        if (!answer) {
            alert('Por favor ingresa una respuesta');
            return;
        }
        
        stopTimer();
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';
        
        gameState.socket.emit('submit_answer', {
            game_id: gameState.gameId,
            answer: answer
        });
    });
    
    answerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitBtn.click();
        }
    });
    
    playAgainBtn.addEventListener('click', () => {
        resultsPanel.classList.add('hidden');
        lobby.classList.remove('hidden');
        findMatchBtn.disabled = false;
    });
    
    // Inicializar
    initSocket();
});