import pygame
import os
import math

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

        self.track = pygame.image.load(os.path.join(assets_dir, "track.png")).convert_alpha()
        self.car = pygame.image.load(os.path.join(assets_dir, "car.png")).convert_alpha()
        
        #Create a collision mask for the track
        self.track_mask = pygame.mask.from_threshold(self.track, (0, 0, 0,255), (1, 1, 1, 255))
        self.car_mask = pygame.mask.from_surface(self.car, 127)
        

        #Create a surface from track mask
        self.mask_image = self.track_mask.to_surface(setcolor=(255, 0, 0, 100), unsetcolor=(0, 0, 0, 0))
        self.car_mask_image = self.car_mask.to_surface(setcolor=(0, 255, 0, 100), unsetcolor=(0, 0, 0, 0))
        

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

    #https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
    #Funkcija uzzime objektu nemot vera vina rotaciju
    def blitRotate(self, surf, image, pos, originPos, angle):
        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

        rotated_offset = offset_center_to_pivot.rotate(-angle)

        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        surf.blit(rotated_image, rotated_image_rect)
    

    def move(self):
        #Car specs
        POWER = 0.3
        STEERING = 0.3
        TOP_SPEED = 30
        DRAG = 0.02
        STEERING_DRAG = 0.05
        
        pidiv180 = math.pi/180
        keys = pygame.key.get_pressed()
        
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        
        if keys[pygame.K_s]:
            #self.y -= 5
            pass
        if keys[pygame.K_w] and speed < TOP_SPEED:
            self.velocity_x += math.sin(self.orientation*pidiv180)*POWER
            self.velocity_y += math.cos(self.orientation*pidiv180)*POWER
        if keys[pygame.K_a]:
            self.angular_velocity += STEERING
        if keys[pygame.K_d]:
            self.angular_velocity -= STEERING
        
        #Car has natural drag
        self.velocity_x *= (1-DRAG)
        self.velocity_y *= (1-DRAG)
        
        self.angular_velocity *= (1-STEERING_DRAG)
        
        self.orientation += self.angular_velocity
        
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        self.position = (self.x, self.y)

    def check_collision(self):
        if self.track_mask.overlap(self.car_mask, (int(self.x), int(self.y))):
            print("Collision")
            return True
        
        
    def invert_mask(self , original_mask):
        """Inverts a given Pygame mask."""
        inverted_mask = pygame.mask.Mask(original_mask.get_size())
        for x in range(original_mask.get_size()[0]):
            for y in range(original_mask.get_size()[1]):
                if not original_mask.get_at((x, y)):
                    inverted_mask.set_at((x, y), 1)
        return inverted_mask


        
    def run(self):
        exit = False
        while not exit:
            self.background()
            self.move()
            self.check_collision()
            self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)
            
            self.canvas.blit(self.mask_image, dest=self.position)
            self.canvas.blit(self.car_mask_image, dest=self.position)
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True

            pygame.display.update()
            pygame.time.Clock().tick(30)


if __name__ == "__main__":
    game = Game()
    game.run()
