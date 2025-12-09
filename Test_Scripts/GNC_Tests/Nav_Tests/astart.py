import heapq
import cv2
import numpy as np
from typing import List, Tuple, Set, Dict, Optional
import time

class AStarPathfinder:
    """A* pathfinding algorithm with cost map and priority queue"""
    
    def __init__(self, grid: np.ndarray, cost_map: Optional[np.ndarray] = None):
        """
        Initialize pathfinder with a grid and optional cost map.
        Grid values: 0 = walkable, 1 = obstacle
        Cost map: additional traversal costs (default = 1.0 for all cells)
        """
        self.grid = grid
        self.rows, self.cols = grid.shape
        
        # Cost map: higher values = more expensive to traverse
        if cost_map is None:
            self.cost_map = np.ones_like(grid, dtype=float)
        else:
            self.cost_map = cost_map
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring cells (8-directional movement)"""
        row, col = pos
        neighbors = []
        # 8-directional: right, down, left, up, and diagonals
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # cardinal
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # diagonal
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.rows and 
                0 <= new_col < self.cols and 
                self.grid[new_row][new_col] == 0):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_move_cost(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        """Calculate movement cost considering terrain cost and diagonal movement"""
        # Base cost: 1.0 for cardinal, ~1.414 for diagonal
        dr = abs(to_pos[0] - from_pos[0])
        dc = abs(to_pos[1] - from_pos[1])
        base_cost = 1.414 if (dr + dc) == 2 else 1.0
        
        # Apply terrain cost from cost map
        terrain_cost = self.cost_map[to_pos[0], to_pos[1]]
        
        return base_cost * terrain_cost
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  visualizer=None) -> Optional[List[Tuple[int, int]]]:
        """
        Find shortest path using A* with priority queue.
        Returns list of coordinates from start to goal, or None if no path exists.
        """
        # Priority queue: (f_score, counter, position)
        counter = 0
        open_set = [(0, counter, start)]
        counter += 1
        
        # Track visited nodes
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        closed_set: Set[Tuple[int, int]] = set()
        
        # Cost from start to each node
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        
        # Estimated total cost (g + h)
        f_score: Dict[Tuple[int, int], float] = {start: self.heuristic(start, goal)}
        
        # Track nodes in open set
        open_set_hash: Set[Tuple[int, int]] = {start}
        
        while open_set:
            # Pop node with lowest f-score from priority queue
            _, _, current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            # Visualize exploration
            if visualizer:
                visualizer.update(current, open_set_hash, closed_set, came_from, goal)
            
            # Goal reached
            if current == goal:
                path = self._reconstruct_path(came_from, current)
                if visualizer:
                    visualizer.draw_final_path(path)
                return path
            
            closed_set.add(current)
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g_score with terrain cost
                tentative_g = g_score[current] + self.get_move_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    
                    if neighbor not in open_set_hash:
                        # Push to priority queue with f_score as priority
                        heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                        counter += 1
                        open_set_hash.add(neighbor)
        
        return None  # No path found
    
    def _reconstruct_path(self, came_from: Dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from dictionary"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


class PathVisualizer:
    """OpenCV-based visualization for A* pathfinding"""
    
    def __init__(self, grid: np.ndarray, cost_map: np.ndarray, cell_size: int = 20):
        self.grid = grid
        self.cost_map = cost_map
        self.rows, self.cols = grid.shape
        self.cell_size = cell_size
        self.width = self.cols * cell_size
        self.height = self.rows * cell_size
        self.delay = 50  # ms delay for visualization
        
    def create_base_image(self) -> np.ndarray:
        """Create base image with grid and cost map"""
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        for i in range(self.rows):
            for j in range(self.cols):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if self.grid[i, j] == 1:  # Obstacle
                    cv2.rectangle(img, (x1, y1), (x2, y2), (50, 50, 50), -1)
                else:
                    # Color based on cost (higher cost = more red)
                    cost = self.cost_map[i, j]
                    intensity = int(255 - min(cost * 25, 200))
                    cv2.rectangle(img, (x1, y1), (x2, y2), (intensity, intensity, 255), -1)
                
                # Grid lines
                cv2.rectangle(img, (x1, y1), (x2, y2), (200, 200, 200), 1)
        
        return img
    
    def draw_cell(self, img: np.ndarray, pos: Tuple[int, int], color: Tuple[int, int, int]):
        """Draw a colored cell at position"""
        i, j = pos
        x1, y1 = j * self.cell_size, i * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        cv2.rectangle(img, (x1 + 2, y1 + 2), (x2 - 2, y2 - 2), color, -1)
    
    def update(self, current: Tuple[int, int], open_set: Set, closed_set: Set,
               came_from: Dict, goal: Tuple[int, int]):
        """Update visualization during pathfinding"""
        img = self.create_base_image()
        
        # Draw closed set (explored nodes) - blue
        for pos in closed_set:
            self.draw_cell(img, pos, (200, 150, 100))
        
        # Draw open set (frontier) - cyan
        for pos in open_set:
            self.draw_cell(img, pos, (255, 255, 100))
        
        # Draw current node - yellow
        self.draw_cell(img, current, (0, 255, 255))
        
        # Add legend
        cv2.putText(img, "Priority Queue (Open Set)", (10, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 100), 2)
        cv2.putText(img, "Explored (Closed Set)", (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 150, 100), 2)
        cv2.putText(img, "Current Node", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        cv2.imshow("A* Pathfinding", img)
        cv2.waitKey(self.delay)
    
    def draw_final_path(self, path: List[Tuple[int, int]]):
        """Draw the final path"""
        img = self.create_base_image()
        
        # Draw path - green
        for i, pos in enumerate(path):
            if i == 0:  # Start - blue
                self.draw_cell(img, pos, (255, 0, 0))
            elif i == len(path) - 1:  # Goal - red
                self.draw_cell(img, pos, (0, 0, 255))
            else:  # Path - green
                self.draw_cell(img, pos, (0, 255, 0))
        
        # Draw arrows along path
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            pt1 = (c1 * self.cell_size + self.cell_size // 2,
                   r1 * self.cell_size + self.cell_size // 2)
            pt2 = (c2 * self.cell_size + self.cell_size // 2,
                   r2 * self.cell_size + self.cell_size // 2)
            cv2.arrowedLine(img, pt1, pt2, (0, 200, 0), 2, tipLength=0.3)
        
        # Add text
        cv2.putText(img, f"Path Length: {len(path)} steps", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, "Press any key to continue...", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.imshow("A* Pathfinding", img)
        cv2.waitKey(0)


def create_test_map(size: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """Create a test map with obstacles and varied terrain costs"""
    grid = np.zeros((size, size), dtype=int)
    cost_map = np.ones((size, size), dtype=float)
    
    # Add obstacles (walls)
    # Vertical walls
    grid[10:40, 15] = 1
    grid[10:40, 35] = 1
    
    # Horizontal walls with gaps
    grid[20, 5:15] = 1
    grid[20, 35:45] = 1
    
    # Random obstacles
    np.random.seed(42)
    for _ in range(30):
        i, j = np.random.randint(0, size, 2)
        if (i, j) not in [(0, 0), (size-1, size-1)]:
            grid[i, j] = 1
    
    # Add terrain cost variations (higher cost = harder to traverse)
    # Rough terrain zones
    cost_map[5:15, 20:30] = 3.0  # High cost zone
    cost_map[30:40, 5:15] = 2.0  # Medium cost zone
    cost_map[35:45, 35:45] = 2.5  # Another medium-high zone
    
    # Low cost "roads"
    cost_map[24, :] = 0.5
    cost_map[:, 25] = 0.5
    
    return grid, cost_map


def main():
    """Demo A* with OpenCV visualization"""
    print("=" * 60)
    print("A* PATHFINDING WITH COST MAP AND PRIORITY QUEUE")
    print("=" * 60)
    print("\nFeatures:")
    print("- 50x50 grid map")
    print("- Cost map for varied terrain")
    print("- Priority queue (heap) for efficient node selection")
    print("- Real-time OpenCV visualization")
    print("\nColor Legend:")
    print("- Red background = High cost terrain")
    print("- Light background = Low cost terrain")
    print("- Gray = Obstacles")
    print("- Cyan = Open set (priority queue)")
    print("- Brown = Closed set (explored)")
    print("- Green = Final path")
    print("\nStarting visualization...\n")
    
    # Create map
    grid, cost_map = create_test_map(size=50)
    
    # Test cases
    test_cases = [
        ((0, 0), (49, 49)),
        ((5, 5), (45, 45)),
        ((10, 45), (40, 5))
    ]
    
    for start, goal in test_cases:
        print(f"\n📍 Finding path from {start} to {goal}")
        
        pathfinder = AStarPathfinder(grid, cost_map)
        visualizer = PathVisualizer(grid, cost_map, cell_size=15)
        
        path = pathfinder.find_path(start, goal, visualizer)
        
        if path:
            total_cost = sum(pathfinder.get_move_cost(path[i], path[i+1]) 
                           for i in range(len(path)-1))
            print(f"✓ Path found! Length: {len(path)} steps, Total cost: {total_cost:.2f}")
        else:
            print("❌ No path found!")
    
    cv2.destroyAllWindows()
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    main()