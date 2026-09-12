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


class SolarSystemSimulator:
    """Main simulation class for the solar system."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Solar System Simulator")
        self.root.geometry("1200x800")
        
        # Canvas for drawing
        self.canvas = tk.Canvas(
            root,
            width=1200,
            height=800,
            bg="black"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Center of the solar system on canvas
        self.center_x = 600
        self.center_y = 400
        
        # Scale factor: pixels per million km
        self.scale = 0.008
        
        # Initialize planets
        self.planets = self._create_planets()
        
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
                orbital_speed=4.1
            ),
            Planet(
                name="Venus",
                distance=108.2,
                size=7,
                color="yellow",
                orbital_speed=1.6
            ),
            Planet(
                name="Earth",
                distance=149.6,
                size=7,
                color="blue",
                orbital_speed=1.0
            ),
            Planet(
                name="Mars",
                distance=227.9,
                size=4,
                color="red",
                orbital_speed=0.53
            ),
            Planet(
                name="Jupiter",
                distance=778.5,
                size=16,
                color="orange",
                orbital_speed=0.084
            ),
            Planet(
                name="Saturn",
                distance=1434.0,
                size=14,
                color="goldenrod",
                orbital_speed=0.034
            ),
            Planet(
                name="Uranus",
                distance=2871.0,
                size=8,
                color="cyan",
                orbital_speed=0.012
            ),
            Planet(
                name="Neptune",
                distance=4495.0,
                size=8,
                color="blue",
                orbital_speed=0.0061
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
        
        # Info label
        self.info_label = tk.Label(
            control_frame,
            text="Solar System Simulator - 8 Planets",
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
    
    def toggle_pause(self) -> None:
        """Toggle simulation pause/resume."""
        self.is_running = not self.is_running
        self.pause_button.config(text="Resume" if not self.is_running else "Pause")
    
    def set_speed(self, value: str) -> None:
        """Set simulation speed multiplier."""
        self.speed_multiplier = float(value)
    
    def reset(self) -> None:
        """Reset all planets to starting positions."""
        for planet in self.planets:
            planet.angle = 0.0
    
    def update_simulation(self) -> None:
        """Update planet positions."""
        if self.is_running:
            for planet in self.planets:
                # Apply speed multiplier
                original_speed = planet.orbital_speed
                planet.orbital_speed = original_speed * self.speed_multiplier
                planet.update()
                planet.orbital_speed = original_speed
    
    def draw(self) -> None:
        """Draw the solar system."""
        self.canvas.delete("all")
        
        # Draw background
        self.canvas.create_rectangle(0, 0, 1200, 800, fill="black", outline="black")
        
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
