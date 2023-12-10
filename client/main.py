import pygame
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 600
        self.canvas = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pygame.display.set_caption("My Board")

        self.canvas.convert_alpha()
        self.canvas.fill((0, 0, 0, 0))
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, "..", "assets")

        self.track = pygame.image.load(os.path.join(assets_dir, "track.png"))
        self.car = pygame.image.load(os.path.join(assets_dir, "car.png")).convert_alpha()
        
        
        self.car = pygame.transform.scale(self.car, (40, 80))

        self.color = (255, 255, 255)
        self.x = 0
        self.y = 0
        self.position = (self.x, self.y)
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        #orientation in degrees 0-360
        self.orientation = 0
        self.angular_velocity = 0

    def background(self):
        self.canvas.fill(self.color)
        self.canvas.blit(self.track, dest=self.position)

    def blitRotate(self, surf, image, pos, originPos, angle):

        # offset from pivot to center
        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
        
        # roatated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # roatetd image center
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

        # get a rotated image
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        # rotate and blit the images
        surf.blit(rotated_image, rotated_image_rect)
    


    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.y -= 5
        if keys[pygame.K_w]:
            self.y += 5
        if keys[pygame.K_a]:
            self.orientation += 1
        if keys[pygame.K_d]:
            self.orientation -= 1
        self.position = (self.x, self.y)

    def run(self):
        exit = False
        while not exit:
            self.background()
            self.move()
            
            self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True

            pygame.display.update()
            pygame.time.Clock().tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
