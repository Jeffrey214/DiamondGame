import tkinter as tk
import random
import os
from PIL import Image, ImageTk
from collections import deque

# Board dimensions and cell size
M, N = 8, 8
CELL_SIZE = 60

def find_simple_bfs_path(board, start, end):
    """Simple BFS to check if there's a path from start to end (for board validation)."""
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
    """Generate a board with given probabilities for walls and diamonds."""
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
    # Ensure start and finish are free
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
        path_sf = find_simple_bfs_path(board, (0, 0), (m - 1, n - 1))
        if not path_sf:
            continue
        
        # Check diamond connectivity
        all_reachable = True
        for d in diamonds:
            if not find_simple_bfs_path(board, (0, 0), d) or not find_simple_bfs_path(board, d, (m-1, n-1)):
                all_reachable = False
                break
        
        if all_reachable:
            return board, diamonds
    
    # Fallback: trivial board with no walls/diamonds
    board = [[0]*n for _ in range(m)]
    board[0][0] = 0
    board[m-1][n-1] = 0
    return board, []

def find_shortest_path_basic(board, start, end):
    """A plain BFS to get a single shortest path from start to end."""
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

def find_shortest_path_with_most_diamonds(board, diamonds):
    """
    Volný mode BFS:
    1) Among all shortest paths from (0,0) to (M-1,N-1),
    2) Pick the one that collects the most diamonds (as a tiebreak).
    """
    m, n = len(board), len(board[0])
    diamond_to_idx = {d: i for i, d in enumerate(diamonds)}
    
    start_state = (0, 0, 0)  # (row, col, bitmask_of_collected_diamonds)
    queue = deque([start_state])
    dist = {start_state: 0}
    pred = {start_state: None}
    
    finish_distance = None
    finish_states_same_layer = []
    
    while queue:
        x, y, mask = queue.popleft()
        d = dist[(x, y, mask)]
        
        # If we've already found a finish distance, and this state's distance is beyond that, stop exploring
        if finish_distance is not None and d > finish_distance:
            break
        
        # If this is a finish cell, record it
        if (x, y) == (m-1, n-1):
            if finish_distance is None:
                finish_distance = d  # first time => minimal distance
            if d == finish_distance:
                finish_states_same_layer.append((x, y, mask))
            continue
        
        # Expand neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and board[nx][ny] != "#":
                new_mask = mask
                if board[nx][ny] == "💎" and (nx, ny) in diamond_to_idx:
                    new_mask = mask | (1 << diamond_to_idx[(nx, ny)] )
                
                new_state = (nx, ny, new_mask)
                if new_state not in dist:
                    dist[new_state] = d + 1
                    pred[new_state] = (x, y, mask)
                    queue.append(new_state)
    
    # If we never found the finish
    if finish_distance is None:
        return []
    
    # Among all states at finish_distance, pick the one with the most diamonds
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
        cx, cy, cmask = cur
        path.append((cx, cy))
        cur = pred[cur]
    path.reverse()
    return path

def create_greedy_path(board, diamonds, target_diamonds=None):
    """
    For 'Všechny' or 'Cíl' mode:
    Greedy approach: go to the nearest diamond until target/all collected, then to finish.
    """
    current_pos = (0, 0)
    full_path = []
    diamonds_copy = diamonds[:]
    collected = 0
    
    while diamonds_copy and (target_diamonds is None or collected < target_diamonds):
        # Sort diamonds by Manhattan distance
        diamonds_copy.sort(key=lambda d: abs(d[0] - current_pos[0]) + abs(d[1] - current_pos[1]))
        best_diamond = diamonds_copy.pop(0)
        
        path_to_diamond = find_shortest_path_basic(board, current_pos, best_diamond)
        if not path_to_diamond:
            continue
        
        # If the path to the diamond includes finish, truncate
        if (M - 1, N - 1) in path_to_diamond:
            idx = path_to_diamond.index((M-1, N-1))
            full_path.extend(path_to_diamond[1:idx+1])
            return full_path
        
        full_path.extend(path_to_diamond[1:])
        current_pos = best_diamond
        collected += 1
    
    # Finally, path to finish
    path_to_finish = find_shortest_path_basic(board, current_pos, (M-1, N-1))
    if path_to_finish:
        full_path.extend(path_to_finish[1:])
    return full_path

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diamond Collector")
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
        self.start_button.config(state=tk.NORMAL)  # Re-enable on reset only
        self.draw_board()
        
        if not init:
            self.status_label.config(text="Hra resetována. Klikněte na Start pro spuštění.")

    def start_game(self):
        # Disable immediately, so it can't be clicked twice
        self.start_button.config(state=tk.DISABLED)
        
        self.current_step = 0
        self.collected_diamonds = 0
        
        mode = self.mode_var.get()
        if mode == "Cíl":
            try:
                target_diamonds = int(self.target_entry.get())
            except ValueError:
                # Re-enable because the user never truly started a game
                self.status_label.config(text="Zadej platné číslo pro cíl diamantů!")
                self.start_button.config(state=tk.NORMAL)
                return
            
            if target_diamonds > len(self.diamonds):
                self.status_label.config(text="Není dostatek diamantů!")
                self.start_button.config(state=tk.NORMAL)
                return
            
            self.path = create_greedy_path(self.board, self.diamonds, target_diamonds)
        
        elif mode == "Všechny":
            self.path = create_greedy_path(self.board, self.diamonds, len(self.diamonds))
        
        else:  # Volný
            self.path = find_shortest_path_with_most_diamonds(self.board, self.diamonds)
        
        if not self.path:
            # No valid path => user must reset
            self.status_label.config(text="Nelze najít žádnou cestu do cíle!")
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
                
                if self.board[i][j] == "#":
                    self.canvas.create_image(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, image=self.img_wall)
                elif self.board[i][j] == "💎":
                    self.canvas.create_image(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, image=self.img_diamond)
        
        if player_pos:
            i, j = player_pos
            px1 = j * CELL_SIZE
            py1 = i * CELL_SIZE
            self.canvas.create_image(px1 + CELL_SIZE/2, py1 + CELL_SIZE/2, image=self.img_person)
        
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
            # Do NOT re-enable the Start button here
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
            # Do NOT re-enable the Start button here
            return
        
        traversed_squares = self.path[:self.current_step + 1]
        self.draw_board(player_pos=(i, j), traversed_squares=traversed_squares)
        
        self.current_step += 1
        self.animation_after_id = self.root.after(300, self.animate_step)

def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
