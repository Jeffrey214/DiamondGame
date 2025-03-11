import tkinter as tk
import random
import os
from PIL import Image, ImageTk
from collections import deque

# Board dimensions and cell size
M, N = 8, 8
CELL_SIZE = 60

def find_simple_bfs_path(board, start, end):
    """Quick BFS to check connectivity (used in board validation)."""
    m, n = len(board), len(board[0])
    queue = deque([(start, [])])
    visited = set()
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == end:
            return path + [(x, y)]
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and board[nx][ny] != "#" and (nx, ny) not in visited:
                queue.append(((nx, ny), path + [(x, y)]))
    return []

def generate_raw_board(m, n, wall_chance=0.25, treasure_chance=0.2):
    """Generate a board with random walls/diamonds, not guaranteed valid."""
    board = [
        [" " if random.random() > wall_chance else "#" for _ in range(n)]
        for _ in range(m)
    ]
    diamonds = []
    for i in range(m):
        for j in range(n):
            if random.random() < treasure_chance and board[i][j] != "#":
                board[i][j] = "💎"
                diamonds.append((i, j))
    # Ensure start/finish are free
    board[0][0] = 0
    board[m-1][n-1] = 0
    return board, diamonds

def generate_valid_board(m, n, wall_chance=0.25, treasure_chance=0.2, max_tries=500):
    """
    Generate a board that:
      - Has a path from start to finish.
      - Every diamond is reachable from start and from that diamond to finish.
    """
    for _ in range(max_tries):
        board, diamonds = generate_raw_board(m, n, wall_chance, treasure_chance)
        path_sf = find_simple_bfs_path(board, (0,0), (m-1,n-1))
        if not path_sf:
            continue
        
        # Check diamond connectivity
        all_reachable = True
        for d in diamonds:
            if (not find_simple_bfs_path(board, (0,0), d)
                or not find_simple_bfs_path(board, d, (m-1,n-1))):
                all_reachable = False
                break
        
        if all_reachable:
            return board, diamonds
    
    # Fallback: trivial board
    board = [[0]*n for _ in range(m)]
    board[0][0] = 0
    board[m-1][n-1] = 0
    return board, []

def find_shortest_path_with_most_diamonds(board, diamonds):
    """
    Volný mode BFS:
    1) Among all shortest paths from (0,0) to (M-1,N-1),
    2) Pick the one that collects the most diamonds as a tiebreak.
    """
    m, n = len(board), len(board[0])
    diamond_to_idx = {d: i for i, d in enumerate(diamonds)}
    
    start_state = (0, 0, 0)  # (row, col, bitmask)
    queue = deque([start_state])
    dist = {start_state: 0}
    pred = {start_state: None}
    
    finish_distance = None
    finish_states_same_layer = []
    
    while queue:
        x, y, mask = queue.popleft()
        d = dist[(x, y, mask)]
        
        # If we have a known finish distance, skip states beyond that distance
        if finish_distance is not None and d > finish_distance:
            break
        
        if (x, y) == (m-1, n-1):
            # Found a shortest path
            if finish_distance is None:
                finish_distance = d
            if d == finish_distance:
                finish_states_same_layer.append((x, y, mask))
            continue
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and board[nx][ny] != "#":
                new_mask = mask
                if board[nx][ny] == "💎":
                    bit_index = diamond_to_idx[(nx, ny)]
                    if not (mask & (1 << bit_index)):
                        new_mask = mask | (1 << bit_index)
                new_state = (nx, ny, new_mask)
                if new_state not in dist:
                    dist[new_state] = d + 1
                    pred[new_state] = (x, y, mask)
                    queue.append(new_state)
    
    if finish_distance is None:
        return []
    
    # Among states in finish_states_same_layer, pick the one with the most diamonds
    best_state = None
    best_diamond_count = -1
    for (fx, fy, fmask) in finish_states_same_layer:
        diamond_count = bin(fmask).count("1")
        if diamond_count > best_diamond_count:
            best_diamond_count = diamond_count
            best_state = (fx, fy, fmask)
    
    # Reconstruct path
    path = []
    cur = best_state
    while cur is not None:
        x, y, mask = cur
        path.append((x, y))
        cur = pred[cur]
    path.reverse()
    return path

def find_path_exactly_t_diamonds(board, diamonds, T):
    """
    BFS for 'Cíl' or 'Všechny' mode:
    - Collect *exactly* T diamonds in as few steps as possible.
    - If T == len(diamonds), that means "collect all."
    
    State: (x, y, mask)
    where mask is a bitmask of which diamonds have been collected.
    """
    if T < 0:
        return []
    if T > len(diamonds):
        return []
    
    m, n = len(board), len(board[0])
    diamond_to_idx = {d: i for i, d in enumerate(diamonds)}
    
    start_state = (0, 0, 0)  # row, col, mask=0
    dist = {start_state: 0}
    pred = {start_state: None}
    queue = deque([start_state])
    
    while queue:
        x, y, mask = queue.popleft()
        d = dist[(x, y, mask)]
        
        # Check if we have T diamonds *and* are at the finish
        if bin(mask).count("1") == T and (x, y) == (m-1, n-1):
            # Reconstruct
            path = []
            cur = (x, y, mask)
            while cur is not None:
                cx, cy, cmask = cur
                path.append((cx, cy))
                cur = pred[cur]
            path.reverse()
            return path
        
        # Otherwise expand neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and board[nx][ny] != "#":
                new_mask = mask
                # If there's a diamond here, try to collect it
                if board[nx][ny] == "💎":
                    bit_index = diamond_to_idx[(nx, ny)]
                    if not (mask & (1 << bit_index)):
                        new_mask = mask | (1 << bit_index)
                        # If collecting pushes us above T, skip
                        if bin(new_mask).count("1") > T:
                            continue
                new_state = (nx, ny, new_mask)
                if new_state not in dist:
                    dist[new_state] = d + 1
                    pred[new_state] = (x, y, mask)
                    queue.append(new_state)
    
    # No path found that collects exactly T diamonds
    return []

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diamatová hra")
        self.root.resizable(False, False)
        self.animation_after_id = None
        
        # Control frame
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="Volný")
        self.mode_options = ["Volný", "Všechny", "Cíl"]
        self.mode_menu = tk.OptionMenu(self.control_frame, self.mode_var, *self.mode_options, command=self.toggle_mode)
        self.mode_menu.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.target_label = tk.Label(self.control_frame, text="Cíl diamantů:")
        self.target_entry = tk.Entry(self.control_frame)
        
        self.canvas = tk.Canvas(root, width=N*CELL_SIZE, height=M*CELL_SIZE)
        self.canvas.pack()
        
        self.status_label = tk.Label(root, text="Nasbírané diamanty: 0", font=("Arial", 14))
        self.status_label.pack(pady=10)
        
        # Load images
        script_dir = os.path.dirname(os.path.abspath(__file__))
        diamond_path = os.path.join(script_dir, "dependancies", "images", "diamond.png")
        wall_path    = os.path.join(script_dir, "dependancies", "images", "wall.png")
        person_path  = os.path.join(script_dir, "dependancies", "images", "person.png")
        image_size = 50
        
        diamond_img = Image.open(diamond_path).resize((image_size, image_size), Image.Resampling.LANCZOS)
        wall_img    = Image.open(wall_path).resize((image_size, image_size), Image.Resampling.LANCZOS)
        person_img  = Image.open(person_path).resize((image_size, image_size), Image.Resampling.LANCZOS)
        
        self.img_diamond = ImageTk.PhotoImage(diamond_img)
        self.img_wall    = ImageTk.PhotoImage(wall_img)
        self.img_person  = ImageTk.PhotoImage(person_img)
        
        # Initial board
        self.reset_game(init=True)

    def toggle_mode(self, mode):
        if mode == "Cíl":
            self.target_label.pack(side=tk.LEFT, padx=10, pady=5)
            self.target_entry.pack(side=tk.LEFT, padx=10, pady=5)
        else:
            self.target_label.pack_forget()
            self.target_entry.pack_forget()

    def reset_game(self, init=False):
        if self.animation_after_id is not None:
            self.root.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        
        self.board, self.diamonds = generate_valid_board(M, N, wall_chance=0.25, treasure_chance=0.2)
        self.current_step = 0
        self.collected_diamonds = 0
        self.start_button.config(state=tk.NORMAL)
        self.draw_board()
        
        if not init:
            self.status_label.config(text="Hra resetována. Klikněte na Start pro spuštění.")

    def start_game(self):
        # Disable the start button so it can't be clicked twice
        self.start_button.config(state=tk.DISABLED)
        
        self.current_step = 0
        self.collected_diamonds = 0
        
        mode = self.mode_var.get()
        if mode == "Cíl":
            try:
                target_diamonds = int(self.target_entry.get())
            except ValueError:
                self.status_label.config(text="Zadej platné číslo pro cíl diamantů!")
                self.start_button.config(state=tk.NORMAL)  # re-enable
                return
            
            self.path = find_path_exactly_t_diamonds(self.board, self.diamonds, target_diamonds)
        
        elif mode == "Všechny":
            # BFS path for exactly all diamonds
            self.path = find_path_exactly_t_diamonds(self.board, self.diamonds, len(self.diamonds))
        
        else:  # Volný
            self.path = find_shortest_path_with_most_diamonds(self.board, self.diamonds)
        
        if not self.path:
            # If BFS fails to find a path, re-enable Start so user can try again
            self.status_label.config(text="Nelze najít žádnou cestu do cíle!")
            self.start_button.config(state=tk.NORMAL)
            return
        
        self.draw_board()
        self.animate_step()

    def draw_board(self, player_pos=None, traversed_squares=None):
        self.canvas.delete("all")
        for i in range(M):
            for j in range(N):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                # Cell color
                if (i, j) == (0, 0) or (i, j) == (M - 1, N - 1):
                    fill_color = "lightblue"
                else:
                    if traversed_squares and (i, j) in traversed_squares:
                        fill_color = "lightblue"
                    elif self.board[i][j] == "#":
                        fill_color = "darkred"
                    elif self.board[i][j] == "💎":
                        fill_color = "lightgreen"
                    else:
                        fill_color = "white"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                
                # Image
                if self.board[i][j] == "#":
                    self.canvas.create_image(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, image=self.img_wall)
                elif self.board[i][j] == "💎":
                    self.canvas.create_image(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, image=self.img_diamond)
        
        # Player
        if player_pos:
            i, j = player_pos
            px1 = j * CELL_SIZE
            py1 = i * CELL_SIZE
            self.canvas.create_image(px1 + CELL_SIZE/2, py1 + CELL_SIZE/2, image=self.img_person)
        
        # Labels
        self.canvas.create_text(CELL_SIZE/2, CELL_SIZE/2,
                                text="Start", font=("Arial", 12, "bold"), fill="blue")
        self.canvas.create_text((N-1)*CELL_SIZE + CELL_SIZE/2, (M-1)*CELL_SIZE + CELL_SIZE/2,
                                text="Konec", font=("Arial", 12, "bold"), fill="blue")
        
        self.status_label.config(text=f"Nasbírané diamanty: {self.collected_diamonds}")
    
    def animate_step(self):
        if self.current_step >= len(self.path):
            self.status_label.config(
                text=f"🎉 Cíl dosažen! Nasbíral jsi {self.collected_diamonds} diamantů! 🎉"
            )
            return
        
        i, j = self.path[self.current_step]
        
        if self.board[i][j] == "💎":
            self.collected_diamonds += 1
            self.board[i][j] = 0
        
        if (i, j) == (M-1, N-1):
            self.draw_board(player_pos=(i, j), traversed_squares=self.path[:self.current_step+1])
            self.status_label.config(
                text=f"🎉 Cíl dosažen! Nasbíral jsi {self.collected_diamonds} diamantů! 🎉"
            )
            return
        
        traversed_squares = self.path[: self.current_step + 1]
        self.draw_board(player_pos=(i, j), traversed_squares=traversed_squares)
        
        self.current_step += 1
        self.animation_after_id = self.root.after(300, self.animate_step)

def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
