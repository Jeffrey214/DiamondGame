# DiamondGame

DiamondGame is a Python-based Tkinter application where players navigate a dynamic board filled with walls and diamonds. Choose from multiple game modes and challenge yourself to collect diamonds on the shortest path from Start to Finish!

## Features

### Multi-Mode Gameplay
- **Volný Mode:**  
  Automatically finds the shortest path from Start to Finish. Among all equal-length paths, it selects the route with the most diamonds collected.
- **Všechny Mode:**  
  Computes a minimal-step path that collects *all* diamonds on the board before finishing.
- **Cíl Mode:**  
  Allows players to specify an exact target number of diamonds to collect. The game computes the shortest route that collects exactly that many diamonds.

### Dynamic Board Generation
- Increased wall density for added challenge, ensuring a valid path exists from Start to Finish while keeping all diamonds reachable.
- Random placement of walls and diamonds guarantees a unique experience on every play.

### Graphical Enhancements
- Custom graphics for walls, diamonds, and the player integrated using Pillow.
- Start and Finish cells are clearly highlighted and labeled ("Start" and "Konec").
- Animated player movement shows the computed path and diamond collection progress.

### User Interface Improvements
- Intuitive Tkinter-based GUI with clearly labeled buttons and status messages.
- Options for selecting game modes and setting the target diamond count in Cíl mode.
- The Start button is disabled after a single use per board to prevent multiple runs, with a dedicated Reset button to generate a new board.

### Executable Packaging
- Can be packaged as a standalone Windows executable (`DiamondGame.exe`) using PyInstaller.
- Custom icon support: the final executable displays a diamond-themed icon.
- No command prompt window appears on launch—only the Tkinter GUI is displayed.

## Bug Fixes & Enhancements
- **Pathing Corrections:**  
  - Resolved issues where the Všechny mode path would backtrack unnecessarily.
  - Ensured that in Cíl mode the game collects exactly the specified number of diamonds.
  - Re-enabled the Start button if no valid path is found so users can try again without resetting the board.
- **Robust Board Validation:**  
  - Improved board generation to guarantee each diamond is reachable and the Finish cell remains accessible, preventing dead ends.

## Future Plans
- Explore additional board sizes and difficulty settings.
- Implement customizable themes and additional graphics options.
- Enhance path-finding efficiency for larger or more complex boards.
