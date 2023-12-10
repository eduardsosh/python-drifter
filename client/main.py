import pygame
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 600
        self.canvas = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("My Board")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "..", "assets")

        self.track = pygame.image.load(os.path.join(assets_dir, "track.png"))
        self.car = pygame.image.load(os.path.join(assets_dir, "car.png"))
        self.car = pygame.transform.scale(self.car, (40, 80))

        self.color = (255, 255, 255)
        self.x = 0
        self.y = 0
        self.position = (self.x, self.y)

    def background(self):
        self.canvas.fill(self.color)
        self.canvas.blit(self.track, dest=self.position)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.y -= 5
        if keys[pygame.K_w]:
            self.y += 5
        if keys[pygame.K_a]:
            self.x += 5
        if keys[pygame.K_d]:
            self.x -= 5
        self.position = (self.x, self.y)

    def run(self):
        exit = False
        while not exit:
            self.background()
            self.move()
            self.canvas.blit(self.car, (self.screen_width/2, self.screen_height/2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True

            pygame.display.update()
            pygame.time.Clock().tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
