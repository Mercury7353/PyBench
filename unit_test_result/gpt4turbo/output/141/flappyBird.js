
const canvas = document.getElementById('birdGame');
const context = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let birdYPosition = canvas.height / 2;
let birdVelocity = 0;
const gravity = 0.5;

function drawBird() {
    context.fillStyle = 'yellow';
    context.beginPath();
    context.arc(50, birdYPosition, 20, 0, Math.PI * 2);
    context.fill();
}

function update() {
    birdVelocity += gravity;
    birdYPosition += birdVelocity;

    if (birdYPosition + 20 > canvas.height || birdYPosition - 20 < 0) {
        resetGame();
    }
}

function resetGame() {
    alert("Game Over!");
    birdYPosition = canvas.height / 2;
    birdVelocity = 0;
}

document.addEventListener('keydown', function(event) {
   if (event.code === 'Space') {
       birdVelocity -=10; // Make a jump
   }
});

function loop() {
   context.clearRect(0, 0, canvas.width, canvas.height);
   drawBird();
   update();

   requestAnimationFrame(loop);
}

loop();
