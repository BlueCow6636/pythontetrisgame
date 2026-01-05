import wx
import random
import time

# =================================================
# GAME CONSTANTS
# =================================================
BLOCK_SIZE = 30
ROWS = 20
COLS = 10

INFO_HEIGHT = 90
WIDTH = COLS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE + INFO_HEIGHT

DIFFICULTY_SPEED = {
    "Easy": 700,
    "Medium": 400,
    "Hard": 200
}

BACKGROUND = wx.Colour(18, 18, 18)
GRID_LINE = wx.Colour(40, 40, 40)
TEXT_COLOR = wx.Colour(230, 230, 230)

COLORS = [
    wx.Colour(255, 85, 85),
    wx.Colour(85, 255, 85),
    wx.Colour(85, 85, 255),
    wx.Colour(255, 255, 85),
    wx.Colour(85, 255, 255),
    wx.Colour(200, 100, 255)
]

# =================================================
# SHAPES
# =================================================
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1],
     [1, 1]],
    [[0, 1, 0],
     [1, 1, 1]],
    [[1, 0, 0],
     [1, 1, 1]],
    [[0, 0, 1],
     [1, 1, 1]]
]

# =================================================
# PIECE CLASS
# =================================================
class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

# =================================================
# MAIN GAME PANEL
# =================================================
class TetrisPanel(wx.Panel):
    def __init__(self, parent, difficulty):
        super().__init__(parent)
        self.SetMinSize((WIDTH, HEIGHT))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.difficulty = difficulty
        self.speed = DIFFICULTY_SPEED[difficulty]
        self.timer = wx.Timer(self)

        self.grid = [[BACKGROUND for _ in range(COLS)] for _ in range(ROWS)]

        self.current_piece = Piece()
        self.next_piece = Piece()

        self.score = 0
        self.start_time = time.time()   # start timer

        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.timer.Start(self.speed)
        self.SetFocus()

    # -------------------------------------------------
    # GAME LOOP
    # -------------------------------------------------
    def on_timer(self, event):
        self.current_piece.y += 1

        if not self.valid_position():
            self.current_piece.y -= 1
            self.lock_piece()
            self.check_completed_rows()

            self.current_piece = self.next_piece
            self.next_piece = Piece()

            if not self.valid_position():
                self.timer.Stop()
                self.show_game_over()
                return

        self.Refresh()
        self.Update()

    # -------------------------------------------------
    # KEY HANDLING
    # -------------------------------------------------
    def on_key(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_LEFT:
            self.current_piece.x -= 1
            if not self.valid_position():
                self.current_piece.x += 1

        elif key == wx.WXK_RIGHT:
            self.current_piece.x += 1
            if not self.valid_position():
                self.current_piece.x -= 1

        elif key == wx.WXK_DOWN:
            self.current_piece.y += 1
            if not self.valid_position():
                self.current_piece.y -= 1

        elif key == wx.WXK_UP:
            old_shape = self.current_piece.shape
            self.current_piece.rotate()
            if not self.valid_position():
                self.current_piece.shape = old_shape

        self.Refresh()
        self.Update()

    # -------------------------------------------------
    # GAME LOGIC
    # -------------------------------------------------
    def valid_position(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = self.current_piece.x + x
                    ny = self.current_piece.y + y

                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return False

                    if ny >= 0 and self.grid[ny][nx] != BACKGROUND:
                        return False
        return True

    def lock_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color

    # -------------------------------------------------
    # SCORE UPDATE WITHOUT CLEARING ROWS
    # -------------------------------------------------
    def check_completed_rows(self):
        for row in self.grid:
            if BACKGROUND not in row:
                self.score += 100   # row stays, score increases

    # -------------------------------------------------
    # GAME OVER MESSAGE
    # -------------------------------------------------
    def show_game_over(self):
        time_spent = int(time.time() - self.start_time)

        if self.score > 0:
            message = "Congratulations!"
        else:
            message = "Better luck next time!"

        wx.MessageBox(
            f"{message}\n\n"
            f"Final Score: {self.score}\n"
            f"Time Spent: {time_spent} seconds",
            "Game Over"
        )

    # -------------------------------------------------
    # DRAWING
    # -------------------------------------------------
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(BACKGROUND))
        dc.Clear()

        dc.SetTextForeground(TEXT_COLOR)
        dc.DrawText(f"Score: {self.score}", 10, 10)
        dc.DrawText(f"Speed: {self.difficulty}", 10, 30)
        dc.DrawText("Next:", WIDTH - 120, 10)

        # Next piece preview
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    dc.SetBrush(wx.Brush(self.next_piece.color))
                    dc.DrawRectangle(
                        WIDTH - 100 + x * 20,
                        40 + y * 20,
                        20,
                        20
                    )

        # Grid
        for y in range(ROWS):
            for x in range(COLS):
                dc.SetBrush(wx.Brush(self.grid[y][x]))
                dc.SetPen(wx.Pen(GRID_LINE))
                dc.DrawRectangle(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE + INFO_HEIGHT,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )

        # Current piece
        dc.SetBrush(wx.Brush(self.current_piece.color))
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    dc.DrawRectangle(
                        (self.current_piece.x + x) * BLOCK_SIZE,
                        (self.current_piece.y + y) * BLOCK_SIZE + INFO_HEIGHT,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )

# =================================================
# START SCREEN
# =================================================
class StartFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxPython Tetris")
        panel = wx.Panel(self)
        panel.SetBackgroundColour(BACKGROUND)

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="TETRIS")
        title.SetForegroundColour(TEXT_COLOR)
        title.SetFont(wx.Font(28, wx.FONTFAMILY_SWISS,
                              wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD))

        vbox.AddStretchSpacer()
        vbox.Add(title, 0, wx.CENTER)
        vbox.AddSpacer(30)

        for level in ["Easy", "Medium", "Hard"]:
            btn = wx.Button(panel, label=level, size=(200, 45))
            btn.SetBackgroundColour(wx.Colour(40, 40, 40))
            btn.SetForegroundColour(TEXT_COLOR)
            btn.Bind(wx.EVT_BUTTON, self.start_game)
            vbox.Add(btn, 0, wx.CENTER | wx.ALL, 8)

        vbox.AddStretchSpacer()
        panel.SetSizer(vbox)

        self.SetClientSize((WIDTH, HEIGHT))
        self.Centre()

    def start_game(self, event):
        difficulty = event.GetEventObject().GetLabel()
        self.Destroy()

        frame = wx.Frame(
            None,
            title="wxPython Tetris",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER
        )
        frame.SetClientSize((WIDTH, HEIGHT))
        frame.Centre()

        panel = TetrisPanel(frame, difficulty)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        frame.SetSizer(sizer)

        frame.Show()

# =================================================
# RUN APPLICATION
# =================================================
app = wx.App()
StartFrame().Show()
app.MainLoop()