
// Step 2: Write game logic

// Get canvas element
var canvas = document.getElementById("gameCanvas");
var ctx = canvas.getContext("2d");

// Game variables
var gravity = 0.5;
var jumpForce = -10;
var score = 0;

// Bird object
var bird = {
    x: 50,
    y: canvas.height / 2,
    width: 40,
    height: 30,
    velocityY: 0,

    // Function to draw bird on canvas
    drawBird: function() {
        ctx.fillStyle = "#FF0000";
        ctx.fillRect(this.x, this.y, this.width, this.height);
    },

    // Function to update bird's position based on gravity and velocity
    updateBirdPosition: function() {
        this.velocityY += gravity;
        this.y += this.velocityY;
        
        if (this.y >= canvas.height - this.height) {
            gameOver();
        }
        
        if (this.y <= 0) {
            gameOver();
        }
        
         requestAnimationFrame(updateGameArea);
     },
     
     // Function to make bird jump when spacebar is pressed or screen is touched/clicked
     jumpBird : function(event){
          if(event.keyCode ===32 || event.type === 'touchstart'){
              console.log('Jump');
              this.velocityY=jumpForce;  
          }   
      },    
};

document.addEventListener('keydown',bird.jumpBird);
document.addEventListener('touchstart',bird.jumpBird);

function startGame(){
   ...
}

function updateGameArea(){
   ...
}

function clearCanvas(){
   ...
}

function gameOver(){
   ...
}
