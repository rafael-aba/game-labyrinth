import constants
import pygame
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def TupleAddition(A, B, lowerbound = 0, upperbound = constants.LENGTH):
    result = tuple(map(lambda i, j: i + j, A, B))
    if result[0] < lowerbound:
        result = (lowerbound,result[1])
    if result[1] < lowerbound:
        result = (result[0],lowerbound)
    if result[0] > upperbound:
        result = (upperbound,result[1])
    if result[1] > upperbound:
        result = (result[0],upperbound)
    return result

def TupleNegative(T):
    return (-T[0], -T[1])

def TupleDivideBy2(T):
    return (T[0]//2, T[1]//2)

class Maze:
    def __init__(self):
        self.img = {}
        self.FetchMaze()
        self.overlay_img = self.Overlay_maze()
    
    # Fetch map from mazegenerator.net
    def FetchMaze(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options)
        try:
            driver.get(constants.URL)
            driver.find_element(By.ID, constants.GENERATE_BUTTON).click()
            img_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, constants.MAZE_IMG)))
            img_url = img_element.get_attribute('src')

            driver.get(img_url)
            svg = driver.find_element(By.TAG_NAME, "svg")
            driver.save_screenshot("./images/maze.png")
            self.img = pygame.image.load("./images/maze.png")
            self.img = self.img.subsurface((0, 0, 2*svg.size["width"], 2*svg.size["height"]))
            self.img = pygame.transform.scale(self.img, constants.RESOLUTION)
        finally:
            driver.close()
        
        # Mark entrance and exit
        rectSize = 22
        pygame.draw.rect(self.img, constants.RED, (constants.RESOLUTION[0]//2 - rectSize - 1, 0, rectSize, rectSize + 5))
        pygame.draw.rect(self.img, constants.BLUE, (constants.RESOLUTION[0]//2 + 2, constants.RESOLUTION[1] - rectSize - 5, rectSize, rectSize + 5))

    def Overlay_maze(self):
        wall_img = pygame.image.load("./images/wall.png")
        wall_img.set_colorkey((255,255,255))
        wall_img = pygame.transform.scale(wall_img, (7,7))

        house = pygame.image.load("./images/house.png")
        house.set_colorkey((255,255,255))
        house = pygame.transform.scale(house, (15,15))

        width, height = self.img.get_size()
        overlay = pygame.Surface((width, height))
        overlay.fill(constants.LIGHT_GREEN)

        for y in range(height):
            for x in range(width):
                if self.img.get_at((x,y)) == (constants.WALL):
                    overlay.set_at((x, y), constants.DARK_GREEN)
        
        overlay.blit(house,(constants.RESOLUTION[0]//2 + 8, constants.RESOLUTION[1]-15))

        return overlay

    def Draw(self, image, game, hero, wolf):
        maze_with_wolf = self.overlay_img.copy()
        
        if game.wolf:
            wolf.Update(self, hero)
            wolf.Draw(maze_with_wolf)
        
        if game.difficulty == constants.NORMAL:
            width, height = maze_with_wolf.get_size()
            visionImage = pygame.Surface((width, height))

            visionPosition = TupleAddition(hero.position,TupleNegative(TupleDivideBy2(hero.vision)), 0, constants.LENGTH - hero.vision[0])
            visionImage = maze_with_wolf.subsurface((visionPosition, hero.vision))
            
            image.fill(constants.BLACK)
            image.blit(visionImage, visionPosition)
        else:
            image.blit(maze_with_wolf, constants.ORIGIN)


class Hero:
    length = 118
    sprite_idle = (0,0,length,177)
    sprite_idle = (length,0,length,177)
    sprite_idle = (2*length,0,length,177)
    sprite_idle = (3*length,0,length,177)
    sprite_idle = (0,0,length,177)
    sprite_idle = (0,0,length,177)
    sprite_idle = (3*length,0,length,177)
    sprite_move = (20,20,100,100)
    def __init__(self):
        self.size = 15
        self.position = (constants.LENGTH//2 - self.size - 5, 0)

        self.img = pygame.image.load('images/hero_2.jfif')
        dimensions = self.img.get_size()
        self.sprite = {}
        self.sprites = []
        for j in range(0,dimensions[1]-dimensions[1]//4,dimensions[1]//4):
            for i in range(0,dimensions[0]-dimensions[0]//4,dimensions[0]//4):
                rect = (i,j,dimensions[0]//4,dimensions[1]//4)
                sprite = self.img.subsurface(rect)
                sprite = pygame.transform.scale(sprite, (self.size,self.size))
                sprite.set_colorkey((254,254,254))
                self.sprites.append(sprite)
        
        self.tick = 0
        self.frame = 0
        self.state = constants.IDLE
        self.direction = constants.DOWN
        self.moving = False
        self.speed = 1

        self.vision = (50,50)
    
    def Draw(self, screen):
        screen.blit(self.sprite, self.position)
    
    def Update(self, maze):
        self.tick = (self.tick + 1) % 60
        self.UpdateParameters()
        self.RotateSprite()
        self.Move(maze)
    
    def UpdateParameters(self):
        if self.moving:
            self.state = constants.IDLE
        else:
            self.state = constants.WALK

    def RotateSprite(self):
        offset = 0

        if self.moving:
            self.frame = (self.tick//15)  % 4
        else: 
            self.frame = 0
        if self.direction == constants.UP:
            offset = 4
        if self.direction == constants.DOWN:
            offset = 0
        if self.direction == constants.RIGHT:
            offset = 12
        if self.direction == constants.LEFT:
            offset = 8
        self.sprite = self.sprites[self.frame + offset]

    def Move(self, maze):
        if self.moving:
            movement = (0,0)
            if self.direction == constants.RIGHT:
                movement = TupleAddition(movement,(self.speed,0),-self.speed, self.speed)
            elif self.direction == constants.LEFT:
                movement = TupleAddition(movement,(-self.speed,0),-self.speed, self.speed)
            elif self.direction == constants.UP:
                movement = TupleAddition(movement,(0,-self.speed),-self.speed, self.speed)
            elif self.direction == constants.DOWN:
                movement = TupleAddition(movement,(0,self.speed),-self.speed, self.speed)

            newPosition = TupleAddition(self.position, movement)
            if not self.ProcessColision(maze,newPosition):
                self.position = newPosition

    def ProcessColision(self, maze, newPosition):
        result = False
        if self.direction == constants.RIGHT:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (self.size, i))
                result = self.CalculateColision(maze, nextPosition, result)
        if self.direction == constants.LEFT:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (0, i))
                result = self.CalculateColision(maze, nextPosition, result)
        if self.direction == constants.DOWN:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (i, self.size))
                result = self.CalculateColision(maze, nextPosition, result)
        if self.direction == constants.UP:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (i, 0))
                result = self.CalculateColision(maze, nextPosition, result)
        return result
    
    def CalculateColision(self, maze, position, currentResult):
        try:
            pixel = maze.img.get_at(position)
            return currentResult or pixel == constants.WALL
        except:
            return True
        
    def ProcessInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.moving = True
                self.direction = constants.RIGHT
            if event.key == pygame.K_LEFT:
                self.moving = True
                self.direction = constants.LEFT
            if event.key == pygame.K_UP:
                self.moving = True
                self.direction = constants.UP
            if event.key == pygame.K_DOWN:
                self.moving = True
                self.direction = constants.DOWN
            if event.key == pygame.K_ESCAPE:
                return False
        if event.type == pygame.KEYUP:
            self.moving = False
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_RIGHT]:
                self.moving = True
                self.direction = constants.RIGHT
            if keys_pressed[pygame.K_LEFT]:
                self.moving = True
                self.direction = constants.LEFT
            if keys_pressed[pygame.K_UP]:
                self.moving = True
                self.direction = constants.UP
            if keys_pressed[pygame.K_DOWN]:
                self.moving = True
                self.direction = constants.DOWN
        return True
        
    def HasWon(self, maze):
        return maze.img.get_at(self.position) == constants.EXIT

class Wolf:
    length = 118
    sprite_idle = (0,0,length,177)
    sprite_idle = (length,0,length,177)
    sprite_idle = (2*length,0,length,177)
    sprite_idle = (3*length,0,length,177)
    sprite_idle = (0,0,length,177)
    sprite_idle = (0,0,length,177)
    sprite_idle = (3*length,0,length,177)
    sprite_move = (20,20,100,100)
    def __init__(self):
        self.size = 15
        self.position = (constants.LENGTH//2 - self.size - 5, 0)

        self.img = pygame.image.load('images/wolf.jpg')
        dimensions = self.img.get_size()
        self.sprite = {}
        self.sprites = []

        for j in range(0,dimensions[1],dimensions[1]//4):
            for i in range(0,dimensions[0],dimensions[0]//4):
                rect = (i,j,dimensions[0]//4,dimensions[1]//4)
                sprite = self.img.subsurface(rect)
                sprite = pygame.transform.scale(sprite, (self.size,self.size))
                sprite.set_colorkey((255,255,255))
                self.sprites.append(sprite)
        
        self.tick = 0
        self.frame = 0
        self.direction = constants.DOWN
        self.speed = 1

        self.vision = (50,50)
    
    def Draw(self, screen):
        screen.blit(self.sprite, self.position)
    
    def Update(self, maze, hero):
        self.tick = (self.tick + 1) % 60
        self.RotateSprite()
        self.Move(maze, hero)

    def RotateSprite(self):
        offset = 0

        self.frame = (self.tick//15) % 4
        if self.direction == constants.UP:
            offset = 12
        if self.direction == constants.DOWN:
            offset = 0
        if self.direction == constants.RIGHT:
            offset = 8
        if self.direction == constants.LEFT:
            offset = 4

        self.sprite = self.sprites[self.frame + offset]

    def ProcessInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.direction = constants.RIGHT
            if event.key == pygame.K_LEFT:
                self.direction = constants.LEFT
            if event.key == pygame.K_UP:
                self.direction = constants.UP
            if event.key == pygame.K_DOWN:
                self.direction = constants.DOWN
            if event.key == pygame.K_ESCAPE:
                return False
        if event.type == pygame.KEYUP:
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_RIGHT]:
                self.direction = constants.RIGHT
            if keys_pressed[pygame.K_LEFT]:
                self.direction = constants.LEFT
            if keys_pressed[pygame.K_UP]:
                self.direction = constants.UP
            if keys_pressed[pygame.K_DOWN]:
                self.direction = constants.DOWN
        return True
    def Move(self, maze, hero):
        movement = (0,0)
        if self.direction == constants.RIGHT:
            movement = TupleAddition(movement,(self.speed,0),-self.speed, self.speed)
        elif self.direction == constants.LEFT:
            movement = TupleAddition(movement,(-self.speed,0),-self.speed, self.speed)
        elif self.direction == constants.UP:
            movement = TupleAddition(movement,(0,-self.speed),-self.speed, self.speed)
        elif self.direction == constants.DOWN:
            movement = TupleAddition(movement,(0,self.speed),-self.speed, self.speed)

        newPosition = TupleAddition(self.position, movement)
        if not self.ProcessColision(maze,newPosition):
            self.position = newPosition

    def ProcessColision(self, maze, newPosition):
        result = False
        if self.direction == constants.RIGHT:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (self.size, i))
                result = self.CalculateColision(maze, nextPosition, result)
        if self.direction == constants.LEFT:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (0, i))
                result = self.CalculateColision(maze, nextPosition, result)
        if self.direction == constants.DOWN:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (i, self.size))
                result = self.CalculateColision(maze, nextPosition, result)
        if self.direction == constants.UP:
            for i in range(0, self.size):
                nextPosition = TupleAddition(newPosition, (i, 0))
                result = self.CalculateColision(maze, nextPosition, result)
        return result
    
    def CalculateColision(self, maze, position, currentResult):
        try:
            pixel = maze.img.get_at(position)
            return currentResult or pixel == constants.WALL
        except:
            return True
    def Eats(self,hero):
        hero_rect = pygame.Rect(hero.position, (hero.size, hero.size))
        wolf_rect = pygame.Rect(self.position, (self.size, self.size))
        
        if (wolf_rect.colliderect(hero_rect)):
            return True
        return False
        
class Game:
    def __init__(self):
        self.difficulty = constants.EASY
        self.selection = constants.EASY
        self.state = constants.LOADING
        self.timerValue = None
        self.finalTimerValue = None
        self.playerName = ''
        self.rankingFile = 'ranking.json'
        self.ranking = self.loadRanking()
        self.font_size = 60
        self.font_size_small = 15
        self.font = pygame.font.Font(None, self.font_size)
        self.font_small = pygame.font.Font(None, self.font_size_small)
        self.wolf_time = 5
        self.wolf = False

    def GetTimer(self, currentTimer):
        return '{:.2f}'.format(currentTimer - self.timerValue)
    
    def ProcessInput(self, event):
        if self.state == constants.MENU:
            self.ProcessMenuInput(event)
        if self.state == constants.RANKING:
            self.ProcessRankingInput(event)
        if self.state == constants.WIN:
            self.ProcessEndgameInput(event)
    
    def ProcessMenuInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.selection == constants.RANKING:
                    self.selection = constants.HARD
                elif self.selection == constants.EASY:
                    self.selection = constants.RANKING
                elif self.selection == constants.NORMAL:
                    self.selection = constants.EASY
                elif self.selection == constants.HARD:
                    self.selection = constants.NORMAL
            if event.key == pygame.K_DOWN:
                if self.selection == constants.EASY:
                    self.selection = constants.NORMAL
                elif self.selection == constants.NORMAL:
                    self.selection = constants.HARD
                elif self.selection == constants.HARD:
                    self.selection = constants.RANKING
                elif self.selection == constants.RANKING:
                    self.selection = constants.EASY
            if event.key == pygame.K_RETURN:
                self.difficulty = self.selection
                self.state = constants.RUNNING

    def ProcessEndgameInput(self, event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.playerName = self.playerName[:-1]
            elif event.key == pygame.K_RETURN:
                self.state = constants.LOADING        
            else:
                if len(self.playerName) < 8:
                    self.playerName += event.unicode

    def ProcessRankingInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = constants.LOADING        

    def StartGame(self):
        self.state = constants.MENU
        self.difficulty = constants.EASY
        self.selection = constants.EASY
        self.timerValue = None
        self.finalTimerValue = None
        self.ranking = self.loadRanking()
        self.wolf = False

    def loadRanking(self):
        try:
            with open(self.rankingFile, 'r') as file:
                ranking = json.load(file)
        except FileNotFoundError:
            with open(self.rankingFile, 'w') as file:
                ranking = []
                json.dump(ranking, file)
        return ranking
    
    def saveRanking(self):
        with open(self.rankingFile, 'w') as file:
            json.dump(self.ranking, file)
    
    def updateRanking(self):
        self.ranking.append({"player": self.playerName, "score": self.finalTimerValue, "difficulty": self.difficulty})
        self.saveRanking()

def game_loop():
    pygame.init()
    
    screen = pygame.display.set_mode([constants.RESOLUTION[0], constants.RESOLUTION[1]])
    pygame.display.set_caption("Maze")
    clock = pygame.time.Clock()

    game = Game()
    hero = None
    wolf = None
    maze = None
    
    running = True
    image = pygame.Surface(constants.RESOLUTION)

    while running:
        clock.tick(60)

        if game.state == constants.LOADING:
            if game.finalTimerValue:
                game.updateRanking()

            text_surface = game.font.render("LOADING MAZE...", True, constants.BLACK)
            text_width, text_height = text_surface.get_size()
            x_pos = (constants.LENGTH - text_width) // 2
            y_pos = (constants.LENGTH - text_height) // 2
            maze = None
            wolf = None
            hero = None
            game.StartGame()

            image.fill(constants.LIGHT_GREEN)
            image.blit(text_surface, (x_pos, y_pos))

        elif game.state == constants.MENU:
            if maze == None:
                maze = Maze()
            if hero == None:
                hero = Hero()

            easyColor = None
            normalColor = None
            hardColor = None
            rankingColor = None
            if game.selection == constants.EASY:
                easyColor = constants.RED
                normalColor = constants.BLACK
                hardColor = constants.BLACK
                rankingColor = constants.BLACK
            if game.selection == constants.NORMAL:
                easyColor = constants.BLACK
                normalColor = constants.RED
                hardColor = constants.BLACK
                rankingColor = constants.BLACK
            if game.selection == constants.HARD:
                easyColor = constants.BLACK
                normalColor = constants.BLACK
                hardColor = constants.RED
                rankingColor = constants.BLACK
            if game.selection == constants.RANKING:
                easyColor = constants.BLACK
                normalColor = constants.BLACK
                hardColor = constants.BLACK
                rankingColor = constants.RED
            
            easy_text = game.font.render("  EASY", True, easyColor)
            easy_width, easy_height = easy_text.get_size()
            easy_pos = ((constants.LENGTH - easy_width) // 2, (constants.LENGTH - easy_height) // 2 - 3*game.font_size//2)

            normal_text = game.font.render("  NORMAL", True, normalColor)
            normal_width, normal_height = normal_text.get_size()
            normal_pos = ((constants.LENGTH - normal_width) // 2, (constants.LENGTH - normal_height) // 2 - game.font_size//2)

            hard_text = game.font.render("  HARD", True, hardColor)
            hard_width, hard_height = hard_text.get_size()
            hard_pos = ((constants.LENGTH - hard_width) // 2, (constants.LENGTH - hard_height) // 2 + game.font_size//2)

            ranking_text = game.font.render("  RANKING", True, rankingColor)
            ranking_width, ranking_height = ranking_text.get_size()
            ranking_pos = ((constants.LENGTH - ranking_width) // 2, (constants.LENGTH - ranking_height) // 2 + 3*game.font_size//2)

            arrow_text = game.font.render(">", True, constants.RED)
            arrow_pos = None
            if game.selection == constants.EASY:
                arrow_pos = TupleAddition(easy_pos, (0,-easy_height//6))
            if game.selection == constants.NORMAL:
                arrow_pos = TupleAddition(normal_pos, (0,-normal_height//6))
            if game.selection == constants.HARD:
                arrow_pos = TupleAddition(hard_pos, (0,-hard_height//6))
            if game.selection == constants.RANKING:
                arrow_pos = TupleAddition(ranking_pos, (0,-ranking_height//6))
            
            image.fill(constants.LIGHT_GREEN)
            image.blit(easy_text, easy_pos)
            image.blit(normal_text, normal_pos)
            image.blit(hard_text, hard_pos)
            image.blit(ranking_text, ranking_pos)
            image.blit(arrow_text, arrow_pos)

        elif game.state == constants.RUNNING:
            if game.difficulty == constants.RANKING:
                ranking_easy = game.font.render("EASY", True, constants.BLACK)
                ranking_normal = game.font.render("MEDIUM", True, constants.BLACK)
                ranking_hard = game.font.render("HARD", True, constants.BLACK)

                scoresEasy = sorted([x for x in game.ranking if x['difficulty'] == constants.EASY], key=lambda x: float(x['score']))
                scoresNormal = sorted([x for x in game.ranking if x['difficulty'] == constants.NORMAL], key=lambda x: float(x['score']))
                scoresHard = sorted([x for x in game.ranking if x['difficulty'] == constants.HARD], key=lambda x: float(x['score']))

                easyColumn = 16
                normalColumn = constants.RESOLUTION[1]//2 - ranking_normal.get_size()[0]//2
                hardColumn = constants.RESOLUTION[1] - ranking_hard.get_size()[0] - 16
                              
                image.fill(constants.LIGHT_GREEN)
                image.blit(ranking_easy, (easyColumn,16))
                image.blit(ranking_normal, (normalColumn, 16))
                image.blit(ranking_hard, (hardColumn, 16))

                for i in range(0,20):
                    if i < len(scoresEasy):
                        rankerEasy = game.font_small.render(scoresEasy[i]['player'] + ": " + str(scoresEasy[i]['score']), True, constants.BLACK)
                    else:
                        rankerEasy = game.font_small.render("-", True, constants.BLACK)

                    if i < len(scoresNormal):
                        rankerNormal = game.font_small.render(scoresNormal[i]['player'] + ": " + str(scoresNormal[i]['score']), True, constants.BLACK)
                    else:
                        rankerNormal = game.font_small.render("-", True, constants.BLACK)

                    if i < len(scoresHard):
                        rankerHard = game.font_small.render(scoresHard[i]['player'] + ": " + str(scoresHard[i]['score']), True, constants.BLACK)
                    else:
                        rankerHard = game.font_small.render("-", True, constants.BLACK)

                    image.blit(rankerEasy, (easyColumn,game.font_size+i*game.font_size_small))
                    image.blit(rankerNormal, (normalColumn,game.font_size+i*game.font_size_small))
                    image.blit(rankerHard, (hardColumn,game.font_size+i*game.font_size_small))
            else:
                if game.timerValue == None:
                    game.timerValue = time.time()

                hero.Update(maze)
                if game.wolf:
                    wolf.Update(maze, hero)
                    if wolf.Eats(hero):
                        game.state = constants.LOSE
                
                maze.Draw(image, game, hero, wolf)
                hero.Draw(image)


                if game.difficulty == constants.HARD:
                    visionPosition = TupleAddition(hero.position,TupleNegative(TupleDivideBy2(hero.vision)), 0, constants.LENGTH - hero.vision[0])
                    visionImage = image.subsurface((visionPosition, hero.vision))
                    image = pygame.transform.scale(visionImage, constants.RESOLUTION)

                if float(game.GetTimer(time.time())) > game.wolf_time :
                    if wolf == None:
                        wolf = Wolf()
                        game.wolf = True

                timerSurface = game.font.render(str(game.GetTimer(time.time())), True, constants.BLUE)
                timer_pos = (16, 16)
                image.blit(timerSurface, timer_pos)

                if hero.HasWon(maze):
                    game.state = constants.WIN

        elif game.state == constants.WIN:
            congrats = game.font.render("Congrats! Your time:", True, constants.BLACK)
            if game.finalTimerValue == None:
                game.finalTimerValue = game.GetTimer(time.time())
            finalTimer = game.font.render(str(game.finalTimerValue) + " sec", True, constants.RED)

            getplayerNameSurface = game.font.render("Enter your name:", True, constants.BLACK)
            playerNameSurface = game.font.render(game.playerName, True, constants.BLACK)

            spacing = 50
            congratsPos = ((constants.RESOLUTION[1]//2 - congrats.get_size()[0]//2, spacing))
            finalTimerPos = ((constants.RESOLUTION[1]//2 - finalTimer.get_size()[0]//2, congratsPos[1] + congrats.get_size()[1]))
            geplayerNamePos = ((constants.RESOLUTION[1]//2 - getplayerNameSurface.get_size()[0]//2, finalTimerPos[1] + finalTimer.get_size()[1] + spacing))
            playerNamePos = ((constants.RESOLUTION[1]//2 - playerNameSurface.get_size()[0]//2, geplayerNamePos[1] + getplayerNameSurface.get_size()[1]))

            image.fill(constants.LIGHT_GREEN)
            image.blit(congrats, congratsPos)
            image.blit(finalTimer, finalTimerPos)
            image.blit(getplayerNameSurface, geplayerNamePos)
            image.blit(playerNameSurface, playerNamePos)

        elif game.state == constants.LOSE:
            if game.finalTimerValue:
                game.updateRanking()

            text_surface = game.font.render("THE WOLF EAT YOU!", True, constants.BLACK)
            text_width, text_height = text_surface.get_size()
            x_pos = (constants.LENGTH - text_width) // 2
            y_pos = (constants.LENGTH - text_height) // 2

            image.fill(constants.LIGHT_GREEN)
            image.blit(text_surface, (x_pos, y_pos))
        screen.blit(image, constants.ORIGIN)
        pygame.display.update()
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if hero != None:
                if not hero.ProcessInput(event):
                    game.state = constants.LOADING
            if wolf != None:
                wolf.ProcessInput(event)
            game.ProcessInput(event)

    pygame.quit()

if __name__ == '__main__':
    game_loop()
    