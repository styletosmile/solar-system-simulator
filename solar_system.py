import tkinter as tk
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Planet:
    """Represents a planet in the solar system."""
    name: str
    distance: float  # Distance from sun in million km
    size: float      # Radius in pixels
    color: str       # Color for drawing
    orbital_speed: float  # Degrees per frame
    angle: float = 0.0  # Current angle in orbital path
    
    def update(self) -> None:
        """Update planet's position in its orbit."""
        self.angle = (self.angle + self.orbital_speed) % 360
    
    def get_position(self, center_x: float, center_y: float, scale: float) -> Tuple[float, float]:
        """Calculate planet's x, y position on screen."""
        # Convert angle to radians
        rad = math.radians(self.angle)
        
        # Calculate orbital position
        x = center_x + self.distance * scale * math.cos(rad)
        y = center_y + self.distance * scale * math.sin(rad)
        
        return x, y


@dataclass
class Meteorite:
    """Represents a meteorite flying toward the sun."""
    x: float
    y: float
    start_x: float
    start_y: float
    target_x: float
    target_y: float
    speed: float = 5.0
    size: float = 3
    explosion_frames: int = 0  # Frames left for explosion animation
    
    def update(self) -> None:
        """Update meteorite position."""
        if self.explosion_frames > 0:
            # In explosion phase
            self.explosion_frames -= 1
        else:
            # Moving toward sun
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > self.speed:
                # Move toward target
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                # Reached target - start explosion
                self.explosion_frames = 15  # 15 frames of explosion
    
    def is_alive(self) -> bool:
        """Check if meteorite is still active."""
        return self.explosion_frames > 0 or self._distance_to_target() > self.speed
    
    def _distance_to_target(self) -> float:
        """Calculate distance to target."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        return math.sqrt(dx**2 + dy**2)
    
    def is_exploding(self) -> bool:
        """Check if meteorite is currently exploding."""
        return self.explosion_frames > 0


class SolarSystemSimulator:
    """Main simulation class for the solar system."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Solar System Simulator")
        self.root.geometry("1400x900")
        
        # Canvas for drawing
        self.canvas = tk.Canvas(
            root,
            width=1400,
            height=850,
            bg="black"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Center of the solar system on canvas
        self.center_x = 700
        self.center_y = 425
        
        # Scale factor: pixels per million km (increased for more spacing)
        self.base_scale = 0.05
        self.scale = self.base_scale
        self.zoom_multiplier = 1.0
        
        # Initialize planets
        self.planets = self._create_planets()
        
        # Meteorites list
        self.meteorites: List[Meteorite] = []
        
        # Sun parameters
        self.sun_radius = 20
        self.sun_color = "yellow"
        
        # Control variables
        self.is_running = True
        self.speed_multiplier = 1.0
        
        # Create control frame
        self._create_controls()
        
        # Start animation
        self.animate()
    
    def _create_planets(self) -> List[Planet]:
        """Create all planets with their properties."""
        planets = [
            Planet(
                name="Mercury",
                distance=57.9,
                size=3,
                color="gray",
                orbital_speed=6.15  # Increased by 50% (4.1 * 1.5)
            ),
            Planet(
                name="Venus",
                distance=108.2,
                size=7,
                color="yellow",
                orbital_speed=2.4  # Increased by 50% (1.6 * 1.5)
            ),
            Planet(
                name="Earth",
                distance=149.6,
                size=7,
                color="blue",
                orbital_speed=1.5  # Increased by 50% (1.0 * 1.5)
            ),
            Planet(
                name="Mars",
                distance=227.9,
                size=4,
                color="red",
                orbital_speed=0.795  # Increased by 50% (0.53 * 1.5)
            ),
            Planet(
                name="Jupiter",
                distance=778.5,
                size=16,
                color="orange",
                orbital_speed=0.126  # Increased by 50% (0.084 * 1.5)
            ),
            Planet(
                name="Saturn",
                distance=1434.0,
                size=14,
                color="goldenrod",
                orbital_speed=0.051  # Increased by 50% (0.034 * 1.5)
            ),
            Planet(
                name="Uranus",
                distance=2871.0,
                size=8,
                color="cyan",
                orbital_speed=0.018  # Increased by 50% (0.012 * 1.5)
            ),
            Planet(
                name="Neptune",
                distance=4495.0,
                size=8,
                color="blue",
                orbital_speed=0.00915  # Increased by 50% (0.0061 * 1.5)
            ),
        ]
        return planets
    
    def _create_controls(self) -> None:
        """Create control panel."""
        control_frame = tk.Frame(self.root, bg="gray20", height=50)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Pause/Resume button
        self.pause_button = tk.Button(
            control_frame,
            text="Pause",
            command=self.toggle_pause,
            bg="gray40",
            fg="white",
            padx=10,
            pady=5
        )
        self.pause_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Speed control
        tk.Label(
            control_frame,
            text="Speed:",
            bg="gray20",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        self.speed_scale = tk.Scale(
            control_frame,
            from_=0.1,
            to=5.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            command=self.set_speed,
            bg="gray40",
            fg="white",
            length=200
        )
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
        # Zoom control
        tk.Label(
            control_frame,
            text="Zoom:",
            bg="gray20",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        self.zoom_scale = tk.Scale(
            control_frame,
            from_=0.2,
            to=20.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            command=self.set_zoom,
            bg="gray40",
            fg="white",
            length=200
        )
        self.zoom_scale.set(1.0)
        self.zoom_scale.pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = tk.Label(
            control_frame,
            text="Solar System Simulator - Click to add meteorites",
            bg="gray20",
            fg="white"
        )
        self.info_label.pack(side=tk.LEFT, padx=20)
        
        # Reset button
        reset_button = tk.Button(
            control_frame,
            text="Reset",
            command=self.reset,
            bg="gray40",
            fg="white",
            padx=10,
            pady=5
        )
        reset_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def on_canvas_click(self, event) -> None:
        """Handle canvas click to create meteorite."""
        # Only create meteorite if click is not on control panel
        if event.y < 850:
            meteorite = Meteorite(
                x=float(event.x),
                y=float(event.y),
                start_x=float(event.x),
                start_y=float(event.y),
                target_x=float(self.center_x),
                target_y=float(self.center_y),
                speed=5.0,
                size=3
            )
            self.meteorites.append(meteorite)
    
    def toggle_pause(self) -> None:
        """Toggle simulation pause/resume."""
        self.is_running = not self.is_running
        self.pause_button.config(text="Resume" if not self.is_running else "Pause")
    
    def set_speed(self, value: str) -> None:
        """Set simulation speed multiplier."""
        self.speed_multiplier = float(value)
    
    def set_zoom(self, value: str) -> None:
        """Set zoom multiplier."""
        self.zoom_multiplier = float(value)
        self.scale = self.base_scale * self.zoom_multiplier
    
    def reset(self) -> None:
        """Reset all planets to starting positions."""
        for planet in self.planets:
            planet.angle = 0.0
        self.meteorites = []
    
    def update_simulation(self) -> None:
        """Update planet positions and meteorites."""
        if self.is_running:
            # Update planets
            for planet in self.planets:
                # Apply speed multiplier
                original_speed = planet.orbital_speed
                planet.orbital_speed = original_speed * self.speed_multiplier
                planet.update()
                planet.orbital_speed = original_speed
            
            # Update meteorites
            for meteorite in self.meteorites[:]:
                meteorite.update()
                if not meteorite.is_alive():
                    self.meteorites.remove(meteorite)
    
    def draw(self) -> None:
        """Draw the solar system."""
        self.canvas.delete("all")
        
        # Draw background
        self.canvas.create_rectangle(0, 0, 1400, 850, fill="black", outline="black")
        
        # Draw orbital paths
        for planet in self.planets:
            self.canvas.create_oval(
                self.center_x - planet.distance * self.scale,
                self.center_y - planet.distance * self.scale,
                self.center_x + planet.distance * self.scale,
                self.center_y + planet.distance * self.scale,
                outline="gray30",
                width=1
            )
        
        # Draw Sun
        self.canvas.create_oval(
            self.center_x - self.sun_radius,
            self.center_y - self.sun_radius,
            self.center_x + self.sun_radius,
            self.center_y + self.sun_radius,
            fill=self.sun_color,
            outline="orange",
            width=2
        )
        
        # Draw planets
        for planet in self.planets:
            x, y = planet.get_position(self.center_x, self.center_y, self.scale)
            
            self.canvas.create_oval(
                x - planet.size,
                y - planet.size,
                x + planet.size,
                y + planet.size,
                fill=planet.color,
                outline="white",
                width=1
            )
            
            # Draw planet name (only for larger planets to avoid clutter)
            if planet.size >= 7:
                self.canvas.create_text(
                    x,
                    y + planet.size + 15,
                    text=planet.name,
                    fill="white",
                    font=("Arial", 8)
                )
        
        # Draw meteorites
        for meteorite in self.meteorites:
            if meteorite.is_exploding():
                # Draw explosion (orange expanding circles)
                explosion_radius = (15 - meteorite.explosion_frames) * 2
                self.canvas.create_oval(
                    meteorite.x - explosion_radius,
                    meteorite.y - explosion_radius,
                    meteorite.x + explosion_radius,
                    meteorite.y + explosion_radius,
                    fill="orange",
                    outline="red",
                    width=2
                )
            else:
                # Draw meteorite (brown/gray color)
                self.canvas.create_oval(
                    meteorite.x - meteorite.size,
                    meteorite.y - meteorite.size,
                    meteorite.x + meteorite.size,
                    meteorite.y + meteorite.size,
                    fill="brown",
                    outline="gray",
                    width=1
                )
    
    def animate(self) -> None:
        """Main animation loop."""
        self.update_simulation()
        self.draw()
        
        # Schedule next frame (30 FPS)
        self.root.after(33, self.animate)


def main():
    """Main entry point."""
    root = tk.Tk()
    simulator = SolarSystemSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
