
let bird = document.querySelector('.bird');
let gameContainer = document.querySelector('.game-container');
const gravity = 0.5;
let birdPosition = 200;
let isGameOver = false;

function control(e) {
    if (e.keyCode === 32) {
        jump();
    }
}

function jump() {
    if (birdPosition < 500) birdPosition -= 50;
}

function startGame() {
    birdPosition += gravity;
    bird.style.bottom = birdPosition + 'px';
    
    if (birdPosition <= 0 || checkCollision()) {
        gameOver();
        clearInterval(gameTimerId);
        
        window.removeEventListener('keydown', control);
        
        alert("Game Over!");
        
        return;
      }
}

function checkCollision() {
   // Simplified collision logic
   return false;
}

function gameOver() {
   console.log('Game over');
   isGameOver=true
}


document.addEventListener('keydown', control);

// Start moving the bird down
let gameTimerId=setInterval(startGame,20)
