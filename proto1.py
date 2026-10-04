import pygame
import sqlite3
pygame.init()
#make the game window
screenDimentions = (1920,1080) #needs to be a tuple
screen = pygame.display.set_mode(screenDimentions)
clock = pygame.time.Clock() # frame rate

#makes the saved data file
data = sqlite3.connect("user.db")
data.execute("""
    CREATE TABLE IF NOT EXISTS users (
    username    TEXT PRIMARY KEY,
    win         INTEGER DEFAULT 0,
    loss        INTEGER DEFAULT 0,
    gamesPlayed INTEGER DEFAULT 0
    )
""") #creates the table if it isnt there, username is a primary key with each line after being a subsequent column relating to that username

#game variables
loginPressed: bool = False
signupPressed: bool = False
loginActive: bool = False
signupActive: bool = False
username: str = ''
usernameConfirm: str = ''
textColour: tuple[int,int,int] = (255,255,255)
inputColour: tuple[int,int,int] = (0,0,0)
welcomeFont: pygame.font.Font = pygame.font.SysFont("arialblack", 40)
normalFont: pygame.font.Font = pygame.font.SysFont("arial", 20)
userEntered : bool = False
newUser: bool = False
added = None
searchResult = None

#button images
loginButton = pygame.image.load("loginButton.png").convert_alpha()
signupButton = pygame.image.load("signupButton.png").convert_alpha()
confirmImg = pygame.image.load("confirmButton.png").convert_alpha()

#class for buttons
class Button():
    """
    an image based button to be used in this project
    it detects when left click is used on it and only registers one event per click

    """
    def __init__(self, x:int, y:int, image, scale):
        """
        makes a button

        Args:
            x (int): The x coordinate of the buttons top left corner
            y (int): The y coordinate of the buttons top left corner
            image(pygame.Surface): The button's image from a local png converted before hand ( e.g pygame.image.Load(image.png).convert_alpha() )
            scale(float): Factor by which to scale the image e.g 0.5 to half and 2 to double
        """
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height*scale))) #scales the image
        self.rect = self.image.get_rect() #gets a rectangle from the image
        self.rect.topleft = (x,y)
        self.clicked = False
    
    def draw(self):
        """
        draws the button on screen and checks if it was clicked

        should be called once per frame, checks the mouse position and its left click state, it then blits the button onto the global surface "screen"

        Returns:
            bool: True if the button is clicked, false if not
        """


        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        
        #check if mouse is over and clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        #reset trigger
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draws the button on screen
        screen.blit(self.image, (self.rect.x,self.rect.y))
        
        return action


def userAdd(username: str):
    """
    Adds a new username to the database.

    Args:
        username (str): A string that was entered by the user on the login screen.

    Returns:
        bool: True if the username is added, false if it wasnt added because it wasnt unique
    """
    try:
        with data: #reverts back if theres an error
            data.execute(
                "INSERT INTO users (username) VALUES (?)", #? is just a place holder, thats why the (username,) is there after
                (username,), #the comma is needed since .execute is expecting a tuple in this case
            )
        return True
    except sqlite3.IntegrityError:
        return False # in this case the username already exists 
    
def userSearch(username: str):
    """
    searches for the username entered by the user

    Args:
        username (str): A string that was entered by the user
    Returns:
        bool: True if the username is found, False if not
    """
    row = data.execute("SELECT 1 FROM users WHERE username = ?", (username,),).fetchone() # searchs for a row with the username the user entered on the login screen
    return row is not None # if a row with the username isnt found then row = None, if something was found row is not none and hence returns true

#instances for the buttons      
buttonLogin = Button(640, 500, loginButton,0.5)
buttonSignup = Button(1092,500, signupButton,0.5)
confirmButton = Button(780, 800, confirmImg, 1)

#menu rectangles
rect_login = pygame.Rect(640, 10, 640, 1920)
loginTextRect = pygame.Rect(640,550, 500,50)
signupTextRect = pygame.Rect(640,630, 500,50)
menuWhiteRect = pygame.Rect(0,0,1920,1080)

#naming game window
pygame.display.set_caption("login/setup screen")

#display text
def textDraw(text: str, font: pygame.font.Font , textColour: tuple[int,int,int], x: int ,y :int):
    """
    Display text by drawing it onto the global screen.

    Args:
        text: The string to be displayed.
        font: The pygame Font object used to render the text.
        textColour: The RGB colour of the text, e.g. (255, 255, 255).
        x: The x-coordinate of the top-left corner of the text.
        y: The y-coordinate of the top-left corner of the text.

    Returns:
        None
    """
    img = font.render(text, True, textColour)
    screen.blit(img, (x,y))







#game loop
run = True
while run:
    #checks for game window being crossed off / closing without using a quit button in menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        #checks for clicking the boxes
        if event.type == pygame.MOUSEBUTTONDOWN:
            if loginTextRect.collidepoint(event.pos):
                loginActive = True
            else:
                loginActive = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if signupTextRect.collidepoint(event.pos):
                signupActive = True
            else:
                signupActive = False 
        # checks if either the setup or login button has been pressed
        if signupActive == True or loginActive == True:
            if event.type == pygame.KEYDOWN: #checks for keyboard input
                if event.key == pygame.K_RETURN and loginActive == True:
                    loginActive = False #once enter is pressed you cannot type again
                    userEntered = True
                elif loginActive == True:
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]                    
                    else:
                        username = username + event.unicode # adds to the username str

                if signupActive == True and loginActive == False: #if the user selected sign up this makes sure they can type in the second box
                    if event.key == pygame.K_RETURN:
                        signupActive = False
                        if username == usernameConfirm: #checks if the username and confirm username are the same
                            newUser = True #if it is then it registers that it is able to be entered
                            userEntered = False
                        elif username != usernameConfirm:
                            signupActive = True #if not it lets the user retry to match them up
                    else:
                        if event.key == pygame.K_BACKSPACE and loginActive == False:
                            usernameConfirm = usernameConfirm[:-1]                        
                        else:
                            usernameConfirm = usernameConfirm + event.unicode






    pygame.display.update()
    clock.tick(60) #sets fps to 60
    screen.fill((255,255,255))

    pygame.draw.rect(screen,(173, 216, 230), rect_login) # makes the login part blue
    textDraw("Welcome!", welcomeFont, textColour, 850, 120)



    

    if buttonLogin.draw() == True:
        loginPressed = True
    if buttonSignup.draw() == True:
        signupPressed = True
    
    if loginPressed == True:
        pygame.draw.rect(screen,(255,255,255), loginTextRect)
        textDraw("Enter username:", normalFont, textColour, 640, 525)
    
    if signupPressed == True:
        pygame.draw.rect(screen,(255,255,255), loginTextRect)
        pygame.draw.rect(screen,(255,255,255), signupTextRect)
        textDraw("Enter username:", normalFont, textColour, 640, 525)
        textDraw("Confirm username:", normalFont, textColour, 640, 610)

    if username != usernameConfirm and signupActive == True:
        textDraw("The usernames you have entered dont match, please try again.", normalFont, (255,0,0), 640, 700) #checks if the username is the same from both times it was entered
    
    textDraw( username, normalFont, inputColour, 640, 560)
    textDraw( usernameConfirm, normalFont, inputColour, 640, 640)

    if newUser == True:
        if confirmButton.draw() == True:
            added = userAdd(username) #attempts to add the name to the databse

    if added == True:
        pygame.draw.rect(screen,(255,255,255), menuWhiteRect) # if the name is added the screen is blanked and black texted is displayed
        textDraw("You have successfully made your new account!", welcomeFont, (0,0,0), 640,600)
    elif added == False:
        textDraw("The username you entered is already being used please try again.", normalFont, textColour, 640, 1000) #if the username is not unique it lets the user re enter a username
        signupActive = True
        loginActive = True

    if userEntered == True:
        if confirmButton.draw() == True:
                searchResult = userSearch(username)
    if searchResult == True:
        pygame.draw.rect(screen,(255,255,255), menuWhiteRect) # if the name is found the screen goes white and shows they have logged in
        textDraw("You have successfully loged into your account", welcomeFont, (0,0,0), 640,600)
    elif searchResult == False:
        textDraw("The username you entered is already being used please try again.", normalFont, textColour, 640, 1000) #if the username is not found this lets the user re-enter the username
        loginActive = True