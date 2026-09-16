import time
import random
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from flask_server import get_computer_move  # Import Flask server

# LED matrix initialization
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=2, block_orientation=0)

# Game variables
player_paddle = [3, 4, 5]     # Player paddle (left side)
computer_paddle = [3, 4, 5]   # Computer paddle (right side)
ball_position = [8, 4]        # Ball's initial position (center)
ball_direction = [-1, random.choice([-1, 1])]  # Ball movement direction
player_score = 0
computer_score = 0

def move_paddle(paddle, direction):
    """Move a paddle up or down."""
    if direction == "up" and paddle[0] > 0:
        return [p - 1 for p in paddle]
    elif direction == "down" and paddle[-1] < 7:
        return [p + 1 for p in paddle]
    return paddle

def move_ball():
    """Move the ball and handle collisions."""
    global ball_position, ball_direction, player_score, computer_score
    next_x = ball_position[0] + ball_direction[0]
    next_y = ball_position[1] + ball_direction[1]

    # Check wall collision (top and bottom)
    if next_y < 0 or next_y > 7:
        ball_direction[1] *= -1

    # Check paddle collision
    if next_x == 1 and next_y in player_paddle:      # Player paddle
        ball_direction[0] *= -1
    elif next_x == 14 and next_y in computer_paddle:  # Computer paddle
        ball_direction[0] *= -1

    # Check scoring
    if next_x < 0:      # Player misses
        computer_score += 1
        reset_ball()
    elif next_x > 15:   # Computer misses
        player_score += 1
        reset_ball()

    # Update ball position
    ball_position[0] += ball_direction[0]
    ball_position[1] += ball_direction[1]

def reset_ball():
    """Reset the ball to the center."""
    global ball_position, ball_direction
    ball_position = [8, 4]
    ball_direction = [-1, random.choice([-1, 1])]

def display_game():
    """Display the game on the LED matrix."""
    with canvas(device) as draw:
        # Draw paddles
        for p in player_paddle:
            draw.point((0, p), fill="white")   # Player paddle
        for p in computer_paddle:
            draw.point((15, p), fill="white")  # Computer paddle
        # Draw ball
        draw.point((ball_position[0], ball_position[1]), fill="white")

def play_game():
    """Run the Pong game loop."""
    global player_paddle, computer_paddle, ball_position, ball_direction
    global player_score, computer_score

    while True:
        # Simulate player paddle movement
        player_paddle = move_paddle(player_paddle, "up" if random.random() > 0.5 else "down")

        # Get computer paddle movement from Flask server
        move = get_computer_move()
        computer_paddle = move_paddle(computer_paddle, move)

        # Move the ball
        move_ball()

        # Display the game
        display_game()

        # Check for game over
        if player_score == 5 or computer_score == 5:
            break

        # Delay for smooth gameplay
        time.sleep(0.2)

    # Game Over
    print(f"Game Over! {'Player Wins!' if player_score == 5 else 'Computer Wins!'}")

def main():
    """Main function to run the game and ask to play again."""
    while True:
        # Reset scores and positions
        global player_score, computer_score
        player_score = 0
        computer_score = 0

        # Play the game
        play_game()

        # Ask to play again
        play_again = input("Play again? (y/n): ").strip().lower()
        if play_again != "y":
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
