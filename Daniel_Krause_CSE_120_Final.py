import pygame
from datetime import datetime
import random

"""
    Debug Settings

    For testing. Set enable_log to true to have the engine log its actions during each frame
"""
# Set this global variable to true to enable log messages. Set to false to disable logging
enable_log = True

# Get the current date and time formatted as <Month Day, Year @ Hour:Min:Sec>
def get_date_and_time():
    return f"{datetime.now().strftime('%b %d, %Y @ %H:%M:%S')}"

# Log a message to the console
# message is a string that you want to log
# level selects the color of the log text: 0->Green, 1->Yellow, 2->Red
def log(message, level):
    if level == 0:
        print(f"<{get_date_and_time()}>\x1b[32m [LEVEL - 0] {message}\x1b[0m")
    elif level == 1:
        print( f"<{get_date_and_time()}>\x1b[33m [LEVEL - 1] {message}\x1b[0m" )
    else:
        print(f"<{get_date_and_time()}>\x1b[31m [LEVEL - {level}] {message}\x1b[0m")

"""
    Object Class
    
    This class will hold all of the information for game objects
"""
class GameObject:
    # ix and iy are the initial object x and y location in the board
    def __init__(self, ix, iy):
        self.x = ix
        self.y = iy

"""
    Player Class - Extends GameObject

    This class will hold all of the information needed to define a player inside of the game
"""
class Player(GameObject):
    # ix and iy are the initial player x and y location in the board
    def __init__(self, ix, iy):
        super().__init__(ix, iy)
        self.color = (   0,   0, 255 )
        if enable_log:
            log(f"Player initialized at [ {self.x}, {self.y} ]", 0)

"""
    Key Class - Extends GameObject

    This class will hold all of the information needed to define a key inside of the game
"""
class Key(GameObject):
    # ix and iy are the initial player x and y location in the board
    def __init__(self, ix, iy):
        super().__init__(ix, iy)
        if enable_log:
            log(f"Key initialized at [ {self.x}, {self.y} ]", 0)

"""
    Door Class - Extends GameObject

    This class will hold all of the information needed to define a door inside of the game
"""
class Door(GameObject):
    # ix and iy are the initial player x and y location in the board
    def __init__(self, ix, iy):
        super().__init__(ix, iy)
        self.locked = True
        if enable_log:
            log(f"Key initialized at [ {self.x}, {self.y} ]", 0)

"""
    Room
    
    This class defines a map room
"""
class Room:
    def __init__(self, ix, iy, iw, ih):
        self.x = ix
        self.y = iy
        self.w = iw
        self.h = ih
        self.cx = ix + int(iw / 2)
        self.cy = iy + int(ih / 2)

"""
    Board Class
    
    This class defines a game board. The board is a 2D array 
"""
class Board:
    def __init__(self, iwidth):
        self.width = iwidth

        # define colors
        self.colors = {
            "WALL":     (   0,   0,   0 ),     # Walls
            "FLOOR":    ( 120,  28, 109 ),     # Floor
            "KEY":      ( 244, 247,  84 ),     # Key
            "LOCKED":   ( 191,   9,  47 ),     # Locked Door
            "UNLOCKED": ( 132, 153,  79 ),     # Open Door
        }

        # Define an empty list for map
        self.board = []

        # Define an empty list for rooms
        self.rooms = []

        # Make a number of rows equal to the board width
        for row in range(self.width):
            r = []
            # Make a number of cols equal to the board width
            for col in range(self.width):
                r.append("")
            # Add the row to the board
            self.board.append(r)

        # Define key and door
        self.key = Key(-1, -1)
        # Define key and door
        self.door = Door(-1, -1)

        if enable_log:
            log(f"Board initialized as {self.width} by {self.width} 2D list", 0)

        # Define a player and place it outside of map bounds
        # Engine.setup will place the player after the board has been generated
        self.player = Player(-1, -1)

    def board_clear( self ):
        # Set every cell in the board to be a WALL
        for r in range(self.width):
            for c in range(self.width):
                self.board[r][c] = "WALL"

        # Set object locations to just outside of map
        self.player.x = -1
        self.player.y = -1
        self.key.x = -1
        self.key.y = -1
        self.door.x = -1
        self.door.y = -1

        if enable_log:
            log(f"Board cleared to walls and player location set to [ {self.player.x}, {self.player.y} ]", 0)

    # Return true if level complete
    def player_interaction( self ):
        # Check for key
        if [self.key.x, self.key.y] == [self.player.x, self.player.y]:
            # Move key off-screen
            self.board[self.key.x][self.key.y] = "FLOOR"
            self.key.x = -1
            self.key.y = -1
            # Unlock the door
            self.door.locked = False
            self.board[self.door.x][self.door.y] = "UNLOCKED"
            if enable_log:
                log( f"Unlocked the door at [ {self.door.x}, {self.door.y} ]", 1)
            return False

        # Check for door
        if [self.door.x, self.door.y] == [self.player.x, self.player.y]:
            # Check for locked door
            if self.door.locked:
                if enable_log:
                    log( f"The door is still locked, find the key", 2 )
                return False
            if enable_log:
                log( f"You found the exit!", 2)
            return True

        if enable_log:
            log( f"Nothing to interact with!", 1)
        return False

    def new_level( self ):

        # Generate rooms in a random order
        block_loc = [
            [ 0, 0 ], [ 0, 1 ], [ 0, 2 ],
            [ 1, 0 ], [ 1, 1 ], [ 1, 2 ],
            [ 2, 0 ], [ 2, 1 ], [ 2, 2 ]
        ]
        random.shuffle( block_loc )

        # Clear old rooms
        self.rooms = []

        while block_loc:
            this_block = block_loc.pop()
            rw = random.randint( 5, 19 )
            rh = random.randint( 5, 19 )
            rx = this_block[0]*20 + 1
            ry = this_block[1]*20 + 1

            self.place_room(rx, ry, rh, rw)


        for r in range( len( self.rooms ) - 1 ):
            self.connect_rooms( self.rooms[ r ], self.rooms[ r + 1 ] )


        # Put the player in the middle of the first room
        self.place_player( self.rooms[0].cx, self.rooms[0].cy )
        # Put the door in the middle of the second room
        rand_room = random.choice( self.rooms[1:len(self.rooms)-1] )
        self.place_door( rand_room.cx, rand_room.cy )
        # Put the key in the middle of the last room
        self.place_key( self.rooms[-1].cx, self.rooms[-1].cy )

        self.door.locked = True

    def place_room( self, x, y, h, w ):
        for r in range( x, x + w ):
            for c in range( y, y + h ):
                self.board[ r ][ c ] = "FLOOR"

        self.rooms.append( Room( x, y, w, h ) )

    def place_player( self, x, y ):
        self.player.x = x
        self.player.y = y

    def place_door( self, x, y ):
        self.door.x = x
        self.door.y = y
        self.board[x][y] = "LOCKED"

    def place_key( self, x, y ):
        self.key.x = x
        self.key.y = y
        self.board[x][y] = "KEY"

    def connect_rooms(self, rm1, rm2):
        for x in range( min( rm1.cx, rm2.cx ), max( rm1.cx, rm2.cx ) + 1 ):
            self.board[ x ][ rm1.cy ] = "FLOOR"
        for y in range( min( rm1.cy, rm2.cy ), max( rm1.cy, rm2.cy ) + 1 ):
            self.board[ rm2.cx ][ y ] = "FLOOR"

    """
        Attempt to move the player
        
        dx -> requested change in x
        dy -> requested change in y
    
        return True if move was successful
        return False if move failed
    """
    def move( self, dx, dy ):
        # Check upper bound
        if self.player.y + dy < 0:
            if enable_log:
                log(f"Player at upper bound of map!", 1)
            return False
        # Check lower bound
        if self.player.y + dy >= self.width:
            if enable_log:
                log(f"Player at lower bound of map!", 1)
            return False
        # Check left bound
        if self.player.x + dx < 0:
            if enable_log:
                log(f"Player at left bound of map!", 1)
            return False
        # Check right bound
        if self.player.x + dx >= self.width:
            if enable_log:
                log(f"Player at right bound of map!", 1)
            return False

        # Check for collision with wall
        if self.board[self.player.x + dx][self.player.y + dy] == "WALL":
            if enable_log:
                log( f"Player hit a wall at [ {self.player.x + dx}, {self.player.y + dy} ]", 1 )
        else:
            self.player.x += dx
            self.player.y += dy
            if enable_log:
                log( f"Player moved to [ {self.player.x}, {self.player.y} ]", 0 )

        return True

"""
    Game Engine Class

    This class will handle the core game logic. It will be in charge of setting up
        the game-loop, loading assets, user input, and rendering
"""
class Engine:
    def __init__(self):
        """
            Screen Settings

            Screen will be a rectangle of dimmentions:
                width  : screen_width
                height : screen_width + the height of the menu
        """
        self.screen_width  = 900
        self.menu_height   = 125
        self.screen_height = ( self.screen_width + self.menu_height )
        if enable_log:
            log(f"Screen will be {self.screen_width} pixels by {self.screen_height} pixels", 0)

        """
            Engine Settings
            
            running    : bool -> use this to handle when the game exits
            map_width  : int  -> define the width / height of the game map ( int tiles )
            viewscreen : int  -> define the width / height of the player "camera" ( int tiles )
            new_frame  : bool -> set this to true to render a new frame to the screen
        """
        # Game starts in its exited state. Engine.setup() will start the game
        self.running = False
        # This is how many tiles wide and tall to make the game map
        self.map_width = 61
        # This is how many tiles the game will render to the screen at one time
        # Use an odd number to ensure the player will be rendered in the center of the screen
        self.viewscreen_options = [5,9,15,25,45]
        self.viewscreen_index = 1
        # Set to false. First fram will be rendered during Engine.setup()
        self.new_frame = False
        if enable_log:
            log(f"Board will be {self.map_width} tiles square and the viewscreen will be {self.viewscreen_options[self.viewscreen_index]} tiles square", 0)

        """
            Map Settings
            
            tile_width : int    -> Calculate how many pixels wide each tile should be
            board      : Board  -> Define an instance of the game board
        """
        # To calculate tile width, divide the screen_width by the number of tiles in the viewscreen
        # If the screen is 880 pixels wide, and the game will render 11 tiles in the viewscreen,
        #   each tile will be 80 pixels wide
        self.tile_width = int( self.screen_width / self.viewscreen_options[self.viewscreen_index] )
        # Define board
        self.board = Board( self.map_width )
        if enable_log:
            log(f"Each tile will be {self.tile_width} pixels square", 0)

        """
            Pygame Settings
            
            Setup rendering pipeline
        """
        # Start pygame functionality
        pygame.init()
        # Define a pygame display object
        self.display = pygame.display.set_mode( ( self.screen_width, self.screen_height ) )
        # Set window title
        pygame.display.set_caption( "Maze Runner" )
        # Set display font
        self.font = pygame.font.SysFont("Courier New", 16)
        if enable_log:
            log(f"PyGame initialized", 0)

    """
        Game Loop Functions
    """
    # This function will be called once before the game starts, and then once again each time
    #   a new level is requested
    def setup( self ):
        if enable_log:
            log(f"Generating a new level...", 0)

        # Clear the board
        self.board.board_clear()

        # Generate a new level
        self.board.new_level()

        # Render new frame
        self.new_frame = True

        # Start the game engine
        self.running = True

    # This function will be called each frame, and will parse user input
    def input( self ):
        # Get keyboard events, one at a time
        for event in pygame.event.get():
            # If the user clicks the close button
            if event.type == pygame.QUIT:
                if enable_log:
                    log(f"Exiting the game", 1)
                # Stop the game engine
                self.running = False
            # If player pressed a key
            elif event.type == pygame.KEYDOWN:
                # Render new frame any time the user presses a key
                self.new_frame = True
                # If the ESC key was pressed
                if event.key == pygame.K_ESCAPE:
                    if enable_log:
                        log(f"Exiting the game", 1)
                    # End game
                    self.running = False
                elif event.key == pygame.K_q:
                    if self.viewscreen_index > 0:
                        self.viewscreen_index -= 1
                        self.tile_width = int( self.screen_width / self.viewscreen_options[self.viewscreen_index] )
                        if enable_log:
                            log(f"Viewport width {self.viewscreen_options[self.viewscreen_index]} | Tile Width {self.tile_width}", 0)
                elif event.key == pygame.K_e:
                    if self.viewscreen_index < len(self.viewscreen_options) - 1:
                        self.viewscreen_index += 1
                        self.tile_width = int( self.screen_width / self.viewscreen_options[self.viewscreen_index] )
                        if enable_log:
                            log(f"Viewport width {self.viewscreen_options[self.viewscreen_index]} | Tile Width {self.tile_width}", 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.board.move( 1, 0 )
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.board.move( -1, 0 )
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.board.move( 0, -1 )
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.board.move( 0, 1 )
                elif event.key == pygame.K_SPACE:
                    if self.board.player_interaction():
                        self.setup()
                elif event.key == pygame.K_r:
                    self.setup()

    def render_menu( self ):
        text = self.font.render( "+-----------------Controls-----------------+", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = 5
        text_rect.y = self.screen_height - self.menu_height + 2
        self.display.blit( text, text_rect )

        text = self.font.render( "| [ q: Zoom    In   ] [ e: Zoom      Out ] |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = 5
        text_rect.y = self.screen_height - self.menu_height + 22
        self.display.blit( text, text_rect )

        text = self.font.render( "| [ w: Move    Up   ] [ s: Move     Down ] |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = 5
        text_rect.y = self.screen_height - self.menu_height + 42
        self.display.blit( text, text_rect )

        text = self.font.render( "| [ a: Move    Left ] [ d: Move    Right ] |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = 5
        text_rect.y = self.screen_height - self.menu_height + 62
        self.display.blit( text, text_rect )

        text = self.font.render( "| [ Space: Interact ] [ r: New     Level ] |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = 5
        text_rect.y = self.screen_height - self.menu_height + 82
        self.display.blit( text, text_rect )

        text = self.font.render( "+------------------------------------------+", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = 5
        text_rect.y = self.screen_height - self.menu_height + 102
        self.display.blit( text, text_rect )

        text = self.font.render( "+------------Current  Objective------------+", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = self.screen_width - text_rect.width - 5
        text_rect.y = self.screen_height - self.menu_height + 2
        self.display.blit( text, text_rect )

        if self.board.door.locked:
            text = self.font.render(     "|               Find the key               |", True, (0, 0, 0) )
        else:
            text = self.font.render(     "|             Find the Way Out             |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = self.screen_width - text_rect.width - 5
        text_rect.y = self.screen_height - self.menu_height + 22
        self.display.blit( text, text_rect )

        text = self.font.render( "|                                          |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = self.screen_width - text_rect.width - 5
        text_rect.y = self.screen_height - self.menu_height + 42
        self.display.blit( text, text_rect )

        text = self.font.render( "|                                          |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = self.screen_width - text_rect.width - 5
        text_rect.y = self.screen_height - self.menu_height + 62
        self.display.blit( text, text_rect )

        text = self.font.render( "|                                          |", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = self.screen_width - text_rect.width - 5
        text_rect.y = self.screen_height - self.menu_height + 82
        self.display.blit( text, text_rect )

        text = self.font.render( "+------------------------------------------+", True, (0, 0, 0) )
        text_rect = text.get_rect()
        text_rect.x = self.screen_width - text_rect.width - 5
        text_rect.y = self.screen_height - self.menu_height + 102
        self.display.blit( text, text_rect )

        cell_rect = pygame.Rect(
            text_rect.x + int( text_rect.w / 2 ) - 5 - 30,
            self.screen_height - 80,
            60, 60
        )
        if self.board.door.locked:
            pygame.draw.rect( self.display, self.board.colors["KEY"], cell_rect )
        else:
            pygame.draw.rect( self.display, self.board.colors["UNLOCKED"], cell_rect )

    # Render the tiles in current viewscreen
    def render( self ):
        # Only render new frame when a change has been made to game state
        if not self.new_frame:
            return

        # Clear new frame flag
        self.new_frame = False

        if enable_log:
            log(f"Rendering new frame...", 0)


        # Clear previous frame
        self.display.fill( (255, 255, 255) )

        """
            Calculate Viewscreen Offset
            
            If the player is away from the walls of the map, render player in the middle of the viewscreen
            Otherwise, lock viewscreen to bounds of the map and calculate where the player should be rendered
        """
        vs_offset = int( self.viewscreen_options[self.viewscreen_index] / 2 )
        sx = 0  # x coordinate of top left viewscreen tile
        sy = 0  # y coordinate of top left viewscreen tile
        """ Calculate x coordinate of first viewscreen tile """
        # If the player is too close to left wall
        if self.board.player.x - vs_offset < 0:
            # Viewscreen will start in column zero
            sx = 0
        # If the player is too close to right wall
        elif self.board.player.x + vs_offset > self.map_width - 1:
            # Viewscreen will start at right wall - viewscreen width
            sx = self.map_width - self.viewscreen_options[self.viewscreen_index]
        # If the player is far enough away from the wall
        else:
            # The viewscreen will render the player in the center of the viewscreen
            sx = self.board.player.x - vs_offset

        """ Calculate y coordinate of first viewscreen tile """
        # If the player is too close to top wall
        if self.board.player.y - vs_offset < 0:
            # Viewscreen will start at row zero
            sy = 0
        # If the player is too close to bottom wall
        elif self.board.player.y + vs_offset > self.map_width - 1:
            # Viewscreen will start at bottom wall - viewscreen width
            sy = self.map_width - self.viewscreen_options[self.viewscreen_index]
        # If the player is far enough away from the wall
        else:
            # The viewscreen will render the player in the center of the viewscreen
            sy = self.board.player.y - vs_offset

        if enable_log:
            log(f"The viewscreen will render map tiles [ {sx}, {sy} ] -> [ {sx + self.viewscreen_options[self.viewscreen_index] - 1}, {sy + self.viewscreen_options[self.viewscreen_index] - 1} ] ", 0)

        # Render board
        cell_rect = pygame.Rect( 0, 0, self.tile_width, self.tile_width )
        for x in range( self.viewscreen_options[self.viewscreen_index] ):
            cell_rect.x = x * cell_rect.width
            for y in range( self.viewscreen_options[self.viewscreen_index] ):
                cell_rect.y = y * cell_rect.width
                # Get cell type
                cell_type = self.board.board[sx+x][sy+y]
                # Check for door
                if cell_type == "DOOR":
                    if self.board.door.locked:
                        pygame.draw.rect( self.display, self.board.colors["LOCKED"], cell_rect )
                    else:
                        pygame.draw.rect( self.display, self.board.colors["UNLOCKED"], cell_rect )
                else:
                    pygame.draw.rect( self.display, self.board.colors[cell_type], cell_rect )

        # Render on top of map
        # calculate center of player cell in relation to viewscreen
        px = ( ( self.board.player.x - sx ) * self.tile_width ) + int( 0.5 * self.tile_width )
        py = ( ( self.board.player.y - sy ) * self.tile_width ) + int( 0.5 * self.tile_width )
        # make the radius of the player 3/4 the size of the cell
        r = int( 0.75 * self.tile_width / 2 )
        pygame.draw.circle( self.display, self.board.player.color, (px, py), r )

        # Draw grid
        for x in range( 1, self.viewscreen_options[self.viewscreen_index] ):
            for y in range( self.viewscreen_options[self.viewscreen_index] + 1 ):
                pygame.draw.line( self.display, ( 25, 25, 25 ), ( x, y * self.tile_width ), ( self.screen_width, y * self.tile_width ), 1 )
                pygame.draw.line( self.display, ( 25, 25, 25 ), ( x * self.tile_width, y ), ( x * self.tile_width, self.screen_width ), 1 )

        # Render Menu
        self.render_menu()

        # Push new frame to display
        pygame.display.update()

    def exit_game( self ):
        pygame.quit()
        log(f"Thank you for playing my Maze Runner!", 0)

    # Handle main game loop
    def run(self):
        # Call the setup function
        self.setup()

        # Enter game loop
        while self.running:
            # Render screen
            self.render()
            # Parse user input
            self.input()

        # Once game is over, clear memory
        self.exit_game()


# Program execution begins here
if __name__ == '__main__':
    if enable_log:
        log(f"To disable logs, set enable log ( at the top of this file ) to False", 2)
    else:
        log(f"To enable logs, set enable log ( at the top of this file ) to True", 2)
    game = Engine()
    game.run()