import pygame
import constants
import sys
from pygame.locals import *
import pygame.freetype

pygame.init()
SIMULATE_EVENT = pygame.USEREVENT + 1
FONT = pygame.freetype.Font('fonts/Arial.ttf', constants.FONT_SIZE)
pygame.display.set_caption('Game of Life Simulation')

class Game():
  def __init__(self):
    # initialize display
    self.display = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    self.display.fill(constants.COLORS['black'])
    self.set_initial_states()

    # create an array of cells on the screen
    self.cells = []
    self.draw_cells()

    # add text
    self.update_text(0, 0)
  
  def run(self):
    """
      Handle events and run simulation
    """
    while True:
      for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        if event.type == QUIT:
          pygame.quit()
          sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP and (not self.game_started or self.game_over) and pos[0] < constants.WORLD_SIZE:
          # mark initially selected cells as live (selected by mouse click)
          self.num_of_ticks = 0
          for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
              old_cell = self.cells[i][j]
              if old_cell.rect_square.collidepoint(pos):
                new_state = 0 if self.cells[i][j].state else 1
                self.update_cell_state(new_state, i, j, old_cell.pos)
          self.population = self.get_population()
          self.update_text(self.num_of_ticks, self.population)
        elif event.type == pygame.MOUSEBUTTONUP:
          # handle button clicks
          if self.run_btn.rect_button.collidepoint(pos) and (not self.game_started or self.game_paused):
            self.run_simulation() 
          elif self.pause_btn.rect_button.collidepoint(pos) and self.game_started and not self.game_paused:
            pygame.time.set_timer(SIMULATE_EVENT, 0) # disable timer
            self.game_paused = True
          elif self.reset_btn.rect_button.collidepoint(pos):
            self.reset()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and not self.game_started:
          self.run_simulation()
        elif event.type == SIMULATE_EVENT and not self.game_over:
          self.run_tick()
          self.num_of_ticks += 1
          self.population = self.get_population()
          self.update_text(self.num_of_ticks, self.population)
          if self.population == 0:
            self.game_over = True
            self.game_started = False
            pygame.time.set_timer(SIMULATE_EVENT, 0) # disable timer
            self.game_over_txt()
      pygame.display.update()
  
  def set_initial_states(self):
    self.num_of_ticks = 0
    self.population = 0
    self.game_started = False
    self.game_over = False
    self.game_paused = False

  def reset(self):
    """
      Reset game to the intial state
    """
    pygame.time.set_timer(SIMULATE_EVENT, 0) # disable timer
    self.display.fill(constants.COLORS['black'])
    self.set_initial_states()
    self.cells = []
    self.draw_cells()
    self.update_text(0, 0)

  def draw_cells(self):
    """
      Add cells to the world; make sure there are cells outside the visible world so that objects can go outside
    """
    for i in range(-10, int(constants.WORLD_SIZE / constants.SQUARE_SIZE) + 10):
      row = []
      for j in range(-10, int(constants.WORLD_SIZE / constants.SQUARE_SIZE) + 10):
        square = Cell(self.display, 0)
        square.draw(constants.COLORS['black'], (i * constants.SQUARE_SIZE, j * constants.SQUARE_SIZE))
        row.append(square)
      self.cells.append(row)

  def run_simulation(self):
    pygame.time.set_timer(SIMULATE_EVENT, constants.SPEED)
    self.game_started = True
    self.game_over = False
    self.game_paused = False

  def game_over_txt(self):
    """
      Display game over text
    """
    # text align center inside right box
    txt, rect = FONT.render('Generation died!', constants.COLORS['white'])
    center_padding = (constants.BOX_WIDTH - rect.size[0]) / 2
    self.display.blit(txt, (constants.WORLD_SIZE + center_padding, constants.BOX_HEIGHT / 2))
  
  def get_population(self):
    """
      Returns the number of live cells
    """
    population = 0
    for row in self.cells:
      for cell in row:
        if cell.state == 1:
          population += 1
    return population

  def update_text(self, ticks, population):
    """
      Update the texts displaying the number of ticks and current population
    """
    right_box = pygame.Rect(constants.WORLD_SIZE, 0, constants.BOX_WIDTH, constants.BOX_HEIGHT)
    pygame.draw.rect(self.display, constants.COLORS['white'], right_box, 1) 
    black_box = pygame.Rect(constants.WORLD_SIZE + 1, 0, constants.BOX_WIDTH - 1, constants.BOX_HEIGHT)
    pygame.draw.rect(self.display, constants.COLORS['black'], black_box) 
    self.ticks_text, self.ticks_rect = FONT.render('Generation: ' + str(ticks), constants.COLORS['white'])
    self.display.blit(self.ticks_text, (constants.WORLD_SIZE + constants.PADDING, constants.PADDING))
    self.population_text, self.population_rect = FONT.render('Population: ' + str(population), constants.COLORS['white'])
    self.display.blit(self.population_text, (constants.WORLD_SIZE + constants.PADDING, constants.PADDING * 3))
    self.ticks_text.fill(constants.COLORS['white'], rect=self.ticks_rect)
    self.run_btn = Button(self.display, 'Run', constants.BOX_HEIGHT / 1.5, FONT, 'navy', constants.COLORS['white'])
    self.pause_btn = Button(self.display, 'Pause', constants.BOX_HEIGHT / 1.5 + 50, FONT, 'navy', constants.COLORS['white'])
    self.reset_btn = Button(self.display, 'Reset', constants.BOX_HEIGHT / 1.5 + 100, FONT, 'navy', constants.COLORS['white'])
    self.run_btn.draw()
    self.pause_btn.draw()
    self.reset_btn.draw()

  def update_cell_state(self, new_state, i, j, pos):
    """
      Update the state of a cell to live/dead
    """
    new_color = 'white' if new_state else 'black'
    new_square = Cell(self.display, new_state)
    new_square.draw(constants.COLORS[new_color], pos)
    self.cells[i][j] = new_square

  def run_tick(self):
    """
      Advance the state of the world by 1 tick
    """
    for i in range(len(self.cells)):
      for j in range(len(self.cells[i])):
        # get the states of the 8 neighbors
        nb1 = self.get_state(i - 1, j - 1)
        nb2 = self.get_state(i - 1, j)
        nb3 = self.get_state(i - 1, j + 1)
        nb4 = self.get_state(i, j - 1)
        nb5 = self.get_state(i, j + 1)
        nb6 = self.get_state(i + 1, j - 1)
        nb7 = self.get_state(i + 1, j)
        nb8 = self.get_state(i + 1, j + 1)
        nbors = [nb1, nb2, nb3, nb4, nb5, nb6, nb7, nb8]
        live_cells = nbors.count(1)
        dead_cells = 8 - live_cells
        # any live cell with 2 or 3 live neighbors survive
        # any live cell with 3 live neighbors becomes a live cell
        if (self.cells[i][j].state == 1 and (live_cells == 2 or live_cells == 3)
          or (self.cells[i][j].state == 0 and live_cells == 3)):
          self.cells[i][j].next_state = 1
        # any other cell dies or remains dead
        else:
          self.cells[i][j].next_state = 0

    for i in range(len(self.cells)):
      for j in range(len(self.cells[i])):
        self.update_cell_state(self.cells[i][j].next_state, i, j, self.cells[i][j].pos)

  def get_state(self, i, j):
    """
      Get the state of a cell (live or dead) at a certain position
      If the cell given is out of the world it's considered to be a dead cell
    """
    try:
      nb = self.cells[i][j]
      return nb.state
    except IndexError:
      return 0

class Button():
  def __init__(self, display, text, y_pos, font, bg, txt_color):
    self.font = font
    self.text = text
    self.bg = bg
    self.txt_color = txt_color
    self.width, self.height = (int(constants.BOX_WIDTH / 2.5), constants.FONT_SIZE + 10)
    self.display = display
    self.y = y_pos
    self.x = int(constants.WORLD_SIZE + (constants.BOX_WIDTH - self.width) / 2)

  def draw(self):
    # horizontally center button inside the right box
    self.rect_button = pygame.Rect(self.x, self.y, self.width, self.height) 
    textsurf, rect = self.font.render(self.text, self.txt_color)
    pygame.draw.rect(self.display, self.bg, self.rect_button)

    # text align center inside button
    x_pos = self.x + int((self.width - rect.size[0]) / 2)
    y_pos = self.y + 5
    self.display.blit(textsurf, (x_pos, y_pos))

class Cell():
  """
    Represents a single cell in the world
  """
  def __init__(self, display, state):
    # state 0 = dead cell, state 1 = live cell
    self.state = state 
    self.next_state = 0
    self.display = display
    self.rect_square = None
    self.pos = None

  def draw(self, color, pos):
    self.pos = pos
    self.rect_square = pygame.Rect(pos[0], pos[1], constants.SQUARE_SIZE, constants.SQUARE_SIZE)
    pygame.draw.rect(self.display, color, self.rect_square) 

def run_game():
  game = Game()
  game.run()  

if __name__ == '__main__':
  run_game()
