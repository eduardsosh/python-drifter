import pygame
import os
import math
import sys
import recording

class Game:
    def __init__(self):
        self.BG_COLOR = (6, 56, 0)
        
        pygame.init()
        pygame.display.set_caption("Drifter")
        screen_sizes = pygame.display.get_desktop_sizes()
        self.screen_width = screen_sizes[0][0]-100
        self.screen_height = screen_sizes[0][1]-100
    
        
        self.canvas = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.canvas.convert_alpha()
        self.canvas.fill(self.BG_COLOR)
        
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.script_dir, "..", "assets")

        self.track = pygame.image.load(os.path.join(self.assets_dir, "track2.png")).convert_alpha()
        self.car = pygame.image.load(os.path.join(self.assets_dir, "car.png")).convert_alpha()
        self.car = pygame.transform.scale(self.car, (40, 80))
        
        self.simplemask = pygame.mask.Mask((40, 40))
        self.simplemask.fill()
        
        self.track_mask = pygame.mask.from_threshold(self.track, (0, 0, 0,255), (1, 1, 1, 255))
        
        # Create an image from track mask for debugging
        #self.mask_image = self.track_mask.to_surface(setcolor=(255, 0, 0, 100), unsetcolor=(0, 0, 0, 0))
        
        self.collided = False
        self.last_col = 0
        self.ticks = 0        

        # Auto pozicija izmantojot formulu tiek atrasta pie starta linijas
        # Mainoties ekrana izmeram mainas auto sakotneja vieta
        self.x = self.screen_width/2 - 2900
        self.y = self.screen_height/2 - 1100
        self.position = (self.x, self.y)
        
        self.velocity_x = 0
        self.velocity_y = 0
        
        #orientation in degrees 0-360
        # Skatamies pa labi sakumaa
        self.orientation = 270
        self.angular_velocity = 0
        
        # Sadursmes vektors
        self.dx = 0
        self.dy = 0
        
        
        


        #countdown second count
        self.countdown_seconds = 3
    def show_countdown(self):
        font = pygame.font.Font(None, 36)
        countdown_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for seconds in range(self.countdown_seconds, 0, -1):
            countdown_surface.fill((0, 0, 0, 0))  # Clear the surface
            text = font.render(str(seconds), True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            countdown_surface.blit(text, text_rect)
            self.canvas.fill((255, 255, 255))  # Clear the canvas
            self.canvas.blit(self.track, dest=self.position)  # Draw game elements
            self.canvas.blit(self.car, (self.screen_width / 2 - 20, self.screen_height / 2 - 40))
            self.canvas.blit(countdown_surface, (0, 0))  # Overlay countdown surface
            pygame.display.flip()
            pygame.time.delay(1000)  # Delay for 1 second


    def background(self):
        self.canvas.fill(self.BG_COLOR)
        self.canvas.blit(self.track, dest=self.position)

    #Funkcija uzzime objektu nemot vera vina rotaciju
    def blitRotate(self, surf, image, pos, originPos, angle):
        image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
        offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

        rotated_offset = offset_center_to_pivot.rotate(-angle)

        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

        #draw the rect
        #pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image_rect.size),2)
        surf.blit(rotated_image, rotated_image_rect)
        
        
    

    def move(self):
        """
        Te tiek darita masinas kustibas fizika
        """
        #Car specs
        POWER = 0.3
        STEERING = 1.05
        TOP_SPEED = 30
        DRAG = 0.02
        STEERING_DRAG = 0.05
        
        pidiv180 = math.pi/180
        keys = pygame.key.get_pressed()
        
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        
        if keys[pygame.K_s]:
            self.velocity_x += math.sin(self.orientation*pidiv180)*POWER*-1
            self.velocity_y += math.cos(self.orientation*pidiv180)*POWER*-1
            pass
        if keys[pygame.K_w] and speed < TOP_SPEED:
            self.velocity_x += math.sin(self.orientation*pidiv180)*POWER
            self.velocity_y += math.cos(self.orientation*pidiv180)*POWER
        if keys[pygame.K_a]:
            self.angular_velocity += min((speed/TOP_SPEED)*STEERING, 1)
        if keys[pygame.K_d]:
            self.angular_velocity -= min((speed/TOP_SPEED)*STEERING, 1)
                    
        #Car has natural drag
        self.velocity_x *= (1-DRAG)
        self.velocity_y *= (1-DRAG)
        
        self.angular_velocity *= (1-STEERING_DRAG)
        
        self.orientation += self.angular_velocity
        
        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        self.position = (self.x, self.y)


    def detect_collision(self):
        OFFSET_X = -20
        OFFSET_Y = -20
        car_mask = self.simplemask
        #Get the offset between the car and the track
        offset = (-self.x + self.screen_width/2 + OFFSET_X, -self.y + self.screen_height/2 + OFFSET_Y)
        #Check if the car is colliding with the track
        overlap = self.track_mask.overlap(car_mask, offset)
        overlap_area = self.track_mask.overlap_area(car_mask, offset)
        
        
        #If there is an overlap, return True
        if overlap:
            # Kkada formula lai dabutu sadursmes virzienu
            self.dx = self.track_mask.overlap_area(car_mask, (offset[0] + 1, offset[1])) - self.track_mask.overlap_area(car_mask, (offset[0] - 1, offset[1]))
            self.dy = self.track_mask.overlap_area(car_mask, (offset[0], offset[1] + 1)) - self.track_mask.overlap_area(car_mask, (offset[0], offset[1] - 1))
            print("Collision")
            print(self.dx, self.dy)
            print(math.degrees(math.atan2(self.dx, self.dy)))
            self.collided = True
            if self.ticks - self.last_col > 10:
                self.bounce()
                self.last_col = self.ticks
            return True
        else:
            self.collided = False

            return False
    
    def bounce(self):
        """
        dx un dy ir vektors uz sadursmes punktu
        velocity_x un velocity_y ir musu vektors
        Jaunais velocity tiek aprekinats padarot sadursmes vektoru perpendikularu 
        (varam iedomaties ka tas tiek pagriezts lai attelotu sienu)
        un atspogulojot velocity vektoru pret to
        
        """
        length = math.sqrt(self.dx**2 + self.dy**2)
        if length == 0:
            return
        self.dx /= length
        self.dy /= length

        self.dx, self.dy = -self.dy, self.dx

        dot = self.dx * self.velocity_x + self.dy * self.velocity_y

        self.velocity_x = 1.5 * self.dx * dot - self.velocity_x
        self.velocity_y = 1.5 * self.dy * dot - self.velocity_y


    def run(self):
        """
        Ta teikt main speles izpildes funkcija
        """
        gamerecorder = recording.Recorder()
        gamerecorder.clear_recording()
        self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)
        self.show_countdown()
        exit = False
        
        while not exit:
            self.ticks += 1
            self.background()
            self.move()
            self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)
            self.detect_collision()
            
            gamerecorder.record_state(self.ticks, self.x, self.y, self.orientation)
            #self.canvas.blit(self.mask_image, dest=self.position)
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gamerecorder.save_to_file()
                    exit = True

            pygame.display.update()
            pygame.time.Clock().tick(45)


if __name__ == "__main__":
    game = Game()
    game.run()
