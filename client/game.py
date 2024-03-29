import pygame
import os
import math
import sys
import recording

class Game:
    def __init__(self, ghostfile, username):
        # Lietotājvārds priekš ieraksta
        self.username = username
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.script_dir, "..", "assets")
        self.BG_COLOR = (6, 56, 0)
        
        
        
        pygame.init()
        pygame.display.set_caption("Drifter")
        screen_sizes = pygame.display.get_desktop_sizes()
        self.screen_width = screen_sizes[0][0]-100
        self.screen_height = screen_sizes[0][1]-100
        #self.screen_width = 800
        #self.screen_height = 600
    
        
        self.canvas = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.canvas.convert_alpha()
        self.canvas.fill(self.BG_COLOR)

        self.track = pygame.image.load(os.path.join(self.assets_dir, "track2.png")).convert_alpha()
        self.car = pygame.image.load(os.path.join(self.assets_dir, "car.png")).convert_alpha()
        self.car = pygame.transform.scale(self.car, (40, 80))
        
        self.simplemask = pygame.mask.Mask((40, 40))
        self.simplemask.fill()
        
        self.track_mask = pygame.mask.from_threshold(self.track, (0, 0, 0,255), (1, 1, 1, 255))
        
        # Create an image from track mask for debugging
        #self.mask_image = self.track_mask.to_surface(setcolor=(255, 0, 0, 100), unsetcolor=(0, 0, 0, 0))
        
        self.collided = False
        self.checkpoint_reached = False
        self.last_col = 0
        self.ticks = 0        

        # Auto pozicija izmantojot formulu tiek atrasta pie starta linijas
        # Mainoties ekrana izmeram mainas auto sakotneja vieta
        self.x = self.screen_width/2 - 2900
        self.y = self.screen_height/2 - 1100
        
        self.startline_coords = [(self.x -40, self.y+300), (self.x-200, self.y-300)]
        
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
        
        self.raceticks = 0
        self.succesful_finish = False
        
        self.ghost = False
        if ghostfile:
            playbackRecorder = recording.Recorder()
            self.ghost_car = pygame.image.load(os.path.join(self.assets_dir, "car.png")).convert_alpha()
            self.ghost_car = pygame.transform.scale(self.ghost_car, (40, 80))
            self.ghost_car.set_alpha(128)
            self.ghost = True
            self.ghoststates = playbackRecorder.load_recording(ghostfile)
            #print(self.ghoststates)


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
            self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)
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
    
    def mainMenu(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return True
            
        
    def angle_between_vectors(self, velocity_x, velocity_y, orientation):
        # Convert orientation from degrees to radians
        orientation_radians = orientation*(math.pi/180)

        # Calculate the components of the orientation vector
        orientation_x = math.cos(orientation_radians)
        orientation_y = math.sin(orientation_radians)

        # Calculate the dot product of the velocity and orientation vectors
        dot_product = velocity_x * orientation_x + velocity_y * orientation_y

        # Calculate the magnitudes of the vectors
        magnitude_velocity = math.sqrt(velocity_x**2 + velocity_y**2)
        magnitude_orientation = math.sqrt(orientation_x**2 + orientation_y**2)

        # Check if either magnitude is zero to avoid division by zero
        if magnitude_velocity == 0 or magnitude_orientation == 0:
            return 0  # You can handle this case as needed

        # Calculate the angle in radians
        angle_radians = math.acos(dot_product / (magnitude_velocity * magnitude_orientation))

        # Convert the angle from radians to degrees
        angle_degrees = (math.degrees(angle_radians))
        print(angle_degrees)

        return angle_degrees


    def move(self):
        """
        Te tiek darita masinas kustibas fizika
        """
        #Car specs
        POWER = 0.3 #0.3
        STEERING = 1.05
        TOP_SPEED = 30
        DRAG = 0.02 #0.02
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

        # if keys[pygame.K_a] and abs(math.atan2(self.velocity_y, self.velocity_x)-(self.orientation*pidiv180))<math.pi:
        #     self.angular_velocity += min((speed/TOP_SPEED)*STEERING, 1)
        # elif keys[pygame.K_a] and abs(math.atan2(self.velocity_y, self.velocity_x)-(self.orientation*pidiv180))>math.pi:
        #     self.angular_velocity -= min((speed/TOP_SPEED)*STEERING, 1)
        # if keys[pygame.K_d] and abs(math.atan2(self.velocity_y, self.velocity_x)-(self.orientation*pidiv180))<math.pi:
        #     self.angular_velocity -= min((speed/TOP_SPEED)*STEERING, 1)
        # elif keys[pygame.K_d] and abs(math.atan2(self.velocity_y, self.velocity_x)-(self.orientation*pidiv180))>math.pi:
        #     self.angular_velocity = min((speed/TOP_SPEED)*STEERING, 1)
            

        #Car slows down faster when drifting
        #self.angle = self.angle_between_vectors(self.velocity_x, self.velocity_y, self.orientation)
        #print(self.velocity_x, self.velocity_y, self.orientation)
        # self.drifting_drag = abs(self.angle-90)
        # self.correct_angle = (self.orientation-90)%360
        # self.angle = (math.atan2(self.velocity_y, self.velocity_x)-(self.correct_angle*pidiv180))
        # self.angle = math.degrees(self.angle)
        #print(math.atan2(self.velocity_y, self.velocity_x), self.correct_angle*pidiv180)
        #Car has natural drag
        self.velocity_x *= (1-DRAG)
        self.velocity_y *= (1-DRAG)

        self.angular_velocity *= (1-STEERING_DRAG)
        
        self.orientation += self.angular_velocity
        self.orientation %= 360

        self.x = self.x + self.velocity_x
        self.y = self.y + self.velocity_y
        self.position = (self.x, self.y)


    def detect_collision(self):
        """
        Funkcija pārbauda vai ir notikusi sadursme ar malu.
        Tas tiek darīts izmantojot pygame.mask objektus ar 
        auto hitbox un melnas malas masku
        """
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
            
            # Ja ir sadursme, tad atspogulojam masinas virziena vektoru
            if self.ticks - self.last_col > 10:
                self.bounce()
                self.last_col = self.ticks
            return True
        else:
            self.collided = False

            return False
    
    # Lai nekraptos, parbaudam vai ir sasniegts checkpoints
    def check_checkpoint(self):
        checkpoint_coords = (-750,-3000)
        offset = 1000
        if self.x > checkpoint_coords[0] - offset and self.x < checkpoint_coords[0] + offset and self.y > checkpoint_coords[1] - offset and self.y < checkpoint_coords[1] + offset:
            if not self.checkpoint_reached:
                print("Checkpoint reached")
            self.checkpoint_reached = True
            return True

    def check_startline(self):
        if self.x < self.startline_coords[0][0] and self.x > self.startline_coords[1][0] and self.y < self.startline_coords[0][1] and self.y > self.startline_coords[1][1]:
            return True
    
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

    # def sectors(self):
    #     if self.x < 4000 / 2 and self.y < 4000 / 2:
    #         print("Player in Sector 1")
    #     if self.x >= 4000 / 2 and self.y < 4000 / 2:
    #         print("Player in Sector 2")
    #     if self.x < 4000 / 2 and self.y >= 4000 / 2:
    #         print("Player in Sector 3")
    #     if self.x >= 4000 / 2 and self.y >= 4000 / 2:
    #         print("Player in Sector 4")



    def run(self):
        """
        Ta teikt main speles izpildes funkcija
        """
        gamerecorder = recording.Recorder()
        gamerecorder.clear_recording()
        #self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)
        self.show_countdown()
        exit = False
        
        if self.ghost:
            ghost_offset_x = (self.ghoststates[0].x+2900)
            ghost_offset_y = (self.ghoststates[0].y+1100)
        
        while not exit:

            
            self.ticks += 1
            self.background()
            self.move()
            self.blitRotate(self.canvas, self.car, (self.screen_width/2, self.screen_height/2), (20, 40), self.orientation)
            self.check_checkpoint()
            self.mainMenu()
            #self.sectors()
            
            #print(self.x, self.y)
            
            if self.ghost:
                if len(self.ghoststates) > 0:
                    ghoststate = self.ghoststates.pop(0)
                    self.blitRotate(self.canvas, self.ghost_car, (self.x - ghoststate.x + ghost_offset_x, self.y - ghoststate.y + ghost_offset_y), (20, 40), ghoststate.angle)
                else:
                    self.ghost = False
            
            if self.mainMenu():
                exit = True
            
            
            self.detect_collision()
            
            
            gamerecorder.record_state(self.ticks, self.x, self.y, self.orientation)
            
            #gamerecorder.record_state(self.ticks, self.x, self.y, self.orientation)
            #self.canvas.blit(self.mask_image, dest=self.position)
            if self.checkpoint_reached and self.check_startline():
                
                print("Finish")
                self.raceticks = self.ticks
                self.succesful_finish = True
                filename = gamerecorder.save_to_file(self.username, self.ticks)
                gamerecorder.upload_recording(filename)
                exit = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    exit = True

            pygame.display.update()
            pygame.time.Clock().tick(45)


if __name__ == "__main__":
    # Padot argumenta recording filename!
    game = Game(None,'eduardsosh')
    game.run()
