import sys
import pygame

# --- Configuration ---
WIDTH, HEIGHT = 640, 480
FPS = 60

# Frame counts for each color
GREEN_FRAMES = 6
RED_FRAMES   = 8
BLUE_FRAMES  = 21

# Color definitions
BLACK = (  0,   0,   0)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)
BLUE  = (  0,   0, 255)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock  = pygame.time.Clock()

    state = 'idle'
    frame_counter = 0

    running = True
    while running:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # start sequence when spacebar pressed and we're idle
                if event.key == pygame.K_SPACE and state == 'idle':
                    state = 'green'
                    frame_counter = 0

        # --- State machine & rendering ---
        if state == 'green':
            screen.fill(GREEN)
            frame_counter += 1
            if frame_counter >= GREEN_FRAMES:
                state = 'red'
                frame_counter = 0

        elif state == 'red':
            screen.fill(RED)
            frame_counter += 1
            if frame_counter >= RED_FRAMES:
                state = 'blue'
                frame_counter = 0

        elif state == 'blue':
            screen.fill(BLUE)
            frame_counter += 1
            if frame_counter >= BLUE_FRAMES:
                state = 'idle'
                frame_counter = 0

        else:  # 'idle'
            screen.fill(BLACK)

        # --- Flip and tick ---
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
