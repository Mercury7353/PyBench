
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

canvas.width = 288;
canvas.height = 512;

// Game variables and constants
const gravity = 0.25;
const bird = {
    x: 50,
    y: 150,
    width: 34,
    height: 24,
    velocity: 0
};

// Draw the bird
function drawBird() {
    ctx.fillStyle = '#FF0000';
    ctx.fillRect(bird.x, bird.y, bird.width, bird.height);
}

// Update the game state
function updateGame() {
    bird.velocity += gravity;
    bird.y += bird.velocity;

    // Draw the bird
    drawBird();
}

// Game loop
function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    updateGame();
    requestAnimationFrame(gameLoop);
}

// Start the game loop
gameLoop();
