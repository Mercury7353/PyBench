
        let gameContainer = document.getElementById('game-container');
        let bird = document.createElement('div');
        bird.style.width = '30px';
        bird.style.height = '30px';
        bird.style.background = 'blue';
        bird.style.position = 'absolute';
        bird.style.top = '50%';
        bird.style.left = '50%';
        gameContainer.appendChild(bird);

        let pipes = [];
        let score = 0;
        let gravity = 0.2;
        let birdVelocity = 0;
        let pipeGap = 100;
        let pipeWidth = 50;
        let pipeSpeed = 2;

        function update() {
            // Update bird position
            birdVelocity += gravity;
            bird.style.top = `${parseFloat(bird.style.top) + birdVelocity}px`;

            // Create new pipes
            if (Math.random() < 0.05) {
                let pipe = document.createElement('div');
                pipe.style.width = `${pipeWidth}px`;
                pipe.style.height = `${Math.random() * 400}px`;
                pipe.style.background = 'green';
                pipe.style.position = 'absolute';
                pipe.style.top = '0px';
                pipe.style.left = `${gameContainer.offsetWidth}px`;
                gameContainer.appendChild(pipe);
                pipes.push(pipe);
            }

            // Update pipe positions
            pipes.forEach(pipe => {
                pipe.style.left = `${parseFloat(pipe.style.left) - pipeSpeed}px`;
                if (parseFloat(pipe.style.left) < -pipeWidth) {
                    pipe.remove();
                    pipes.splice(pipes.indexOf(pipe), 1);
                }
            });

            // Check collisions
            pipes.forEach(pipe => {
                if (checkCollision(bird, pipe)) {
                    alert('Game Over!');
                    location.reload();
                }
            });

            // Update score
            score++;
            document.title = `Flappy Bird - Score: ${score}`;

            requestAnimationFrame(update);
        }

        function checkCollision(bird, pipe) {
            let birdRect = bird.getBoundingClientRect();
            let pipeRect = pipe.getBoundingClientRect();
            if (birdRect.left + birdRect.width > pipeRect.left &&
                birdRect.left < pipeRect.left + pipeRect.width &&
                birdRect.top + birdRect.height > pipeRect.top &&
                birdRect.top < pipeRect.top + pipeRect.height) {
                return true;
            }
            return false;
        }

        document.addEventListener('keydown', event => {
            if (event.key === ' ') {
                birdVelocity = -5;
            }
        });

        update();
    
        document.addEventListener('DOMContentLoaded', () => {
            update();
        });
    
        function generatePipe() {
            let pipe = document.createElement('div');
            pipe.style.width = `${pipeWidth}px`;
            pipe.style.height = `${Math.random() * 400}px`;
            pipe.style.background = 'green';
            pipe.style.position = 'absolute';
            pipe.style.top = '0px';
            pipe.style.left = `${gameContainer.offsetWidth}px`;
            gameContainer.appendChild(pipe);
            pipes.push(pipe);
        }

        setInterval(generatePipe, 2000);

        function checkCollision(bird, pipe) {
            let birdRect = bird.getBoundingClientRect();
            let pipeRect = pipe.getBoundingClientRect();
            if (birdRect.left + birdRect.width > pipeRect.left &&
                birdRect.left < pipeRect.left + pipeRect.width &&
                birdRect.top + birdRect.height > pipeRect.top &&
                birdRect.top < pipeRect.top + pipeRect.height) {
                return true;
            }
            return false;
        }

        function update() {
            // Update bird position
            birdVelocity += gravity;
            bird.style.top = `${parseFloat(bird.style.top) + birdVelocity}px`;

            // Update pipe positions
            pipes.forEach(pipe => {
                pipe.style.left = `${parseFloat(pipe.style.left) - pipeSpeed}px`;
                if (parseFloat(pipe.style.left) < -pipeWidth) {
                    pipe.remove();
                    pipes.splice(pipes.indexOf(pipe), 1);
                }
            });

            // Check collisions
            pipes.forEach(pipe => {
                if (checkCollision(bird, pipe)) {
                    alert('Game Over!');
                    location.reload();
                }
            });

            // Update score
            score++;
            document.title = `Flappy Bird - Score: ${score}`;

            requestAnimationFrame(update);
        }
    