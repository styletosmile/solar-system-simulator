import tkinter as tk
import math
import random
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
    destroyed: bool = False  # Whether planet is destroyed
    destruction_frames: int = 0  # Frames left for destruction animation
    debris: List['Debris'] = None  # Debris particles from destruction
    
    def __post_init__(self):
        if self.debris is None:
            self.debris = []
    
    def update(self) -> None:
        """Update planet's position in its orbit."""
        if not self.destroyed:
            self.angle = (self.angle + self.orbital_speed) % 360
        else:
            # Update debris during destruction
            self.destruction_frames -= 1
            for particle in self.debris:
                particle.update()
    
    def get_position(self, center_x: float, center_y: float, scale: float) -> Tuple[float, float]:
        """Calculate planet's x, y position on screen."""
        # Convert angle to radians
        rad = math.radians(self.angle)
        
        # Calculate orbital position
        x = center_x + self.distance * scale * math.cos(rad)
        y = center_y + self.distance * scale * math.sin(rad)
        
        return x, y
    
    def destroy(self) -> None:
        """Start planet destruction animation."""
        self.destroyed = True
        self.destruction_frames = 30  # 30 frames of destruction
        self.create_debris()
    
    def create_debris(self) -> None:
        """Create debris particles for destruction animation."""
        num_particles = 12
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            velocity_x = math.cos(angle) * random.uniform(3, 8)
            velocity_y = math.sin(angle) * random.uniform(3, 8)
            
            # Use current position if we have it
            particle = Debris(
                x=0,
                y=0,
                vx=velocity_x,
                vy=velocity_y,
                color=self.color,
                size=random.uniform(2, 6),
                lifetime=30
            )
            self.debris.append(particle)


@dataclass
class Debris:
    """Represents a piece of debris from destroyed planet or meteorite."""
    x: float
    y: float
    vx: float
    vy: float
    color: str
    size: float
    lifetime: int  # Frames until disappears
    
    def update(self) -> None:
        """Update debris position and lifetime."""
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        # Apply gravity-like effect toward center
        self.vy += 0.3
    
    def is_alive(self) -> bool:
        """Check if debris is still visible."""
        return self.lifetime > 0
    
    def get_alpha(self) -> float:
        """Get opacity based on remaining lifetime (0-1)."""
        return self.lifetime / 30.0


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
    debris: List[Debris] = None
    burning: bool = False  # Whether meteorite is burning after collision
    
    def __post_init__(self):
        if self.debris is None:
            self.debris = []
    
    def update(self) -> None:
        """Update meteorite position."""
        if self.explosion_frames > 0:
            # In explosion phase
            self.explosion_frames -= 1
            # Update debris
            for particle in self.debris:
                particle.update()
        elif self.burning:
            # Meteorite is burning - just decrementing already handled
            pass
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
                self.create_explosion()
                self.explosion_frames = 20  # 20 frames of explosion
                self.burning = True
    
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
    
    def create_explosion(self) -> None:
        """Create explosion particles."""
        num_particles = 20
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            velocity_x = math.cos(angle) * random.uniform(4, 10)
            velocity_y = math.sin(angle) * random.uniform(4, 10)
            
            # Mix of colors for nice explosion effect
            colors = ["red", "orange", "yellow", "white"]
            particle = Debris(
                x=self.x,
                y=self.y,
                vx=velocity_x,
                vy=velocity_y,
                color=random.choice(colors),
                size=random.uniform(2, 5),
                lifetime=25
            )
            self.debris.append(particle)


@dataclass
class Star:
    """Represents a fast-moving star through the solar system."""
    x: float
    y: float
    vx: float
    vy: float
    speed: float = 8.0  # Faster than meteorites
    size: float = 2
    explosion_frames: int = 0  # Frames left for explosion animation
    debris: List[Debris] = None
    trail: List[Tuple[float, float]] = None  # Trail positions
    
    def __post_init__(self):
        if self.debris is None:
            self.debris = []
        if self.trail is None:
            self.trail = []
    
    def update(self) -> None:
        """Update star position."""
        if self.explosion_frames > 0:
            # In explosion phase
            self.explosion_frames -= 1
            # Update debris
            for particle in self.debris:
                particle.update()
        else:
            # Add current position to trail
            self.trail.append((self.x, self.y))
            # Keep trail to last 10 positions
            if len(self.trail) > 10:
                self.trail.pop(0)
            
            # Moving across the screen
            self.x += self.vx
            self.y += self.vy
    
    def is_alive(self) -> bool:
        """Check if star is still active."""
        # Star is alive if still exploding or still on screen
        if self.explosion_frames > 0:
            return True
        # Check if off screen
        if self.x < -100 or self.x > 1500 or self.y < -100 or self.y > 950:
            return False
        return True
    
    def is_exploding(self) -> bool:
        """Check if star is currently exploding."""
        return self.explosion_frames > 0
    
    def create_explosion(self) -> None:
        """Create explosion particles."""
        num_particles = 12
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            velocity_x = math.cos(angle) * random.uniform(2, 6)
            velocity_y = math.sin(angle) * random.uniform(2, 6)
            
            # White and yellow colors for star explosion
            colors = ["white", "yellow", "cyan"]
            particle = Debris(
                x=self.x,
                y=self.y,
                vx=velocity_x,
                vy=velocity_y,
                color=random.choice(colors),
                size=random.uniform(1, 3),
                lifetime=20
            )
            self.debris.append(particle)


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
        
        # Stars list
        self.stars: List[Star] = []
        
        # Star spawning
        self.star_spawn_timer = 0
        self.star_spawn_interval = random.randint(30, 150)  # 1-5 seconds at 30 FPS
        
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
                orbital_speed=6.15,
                debris=[]
            ),
            Planet(
                name="Venus",
                distance=108.2,
                size=7,
                color="yellow",
                orbital_speed=2.4,
                debris=[]
            ),
            Planet(
                name="Earth",
                distance=149.6,
                size=7,
                color="blue",
                orbital_speed=1.5,
                debris=[]
            ),
            Planet(
                name="Mars",
                distance=227.9,
                size=4,
                color="red",
                orbital_speed=0.795,
                debris=[]
            ),
            Planet(
                name="Jupiter",
                distance=778.5,
                size=16,
                color="orange",
                orbital_speed=0.126,
                debris=[]
            ),
            Planet(
                name="Saturn",
                distance=1434.0,
                size=14,
                color="goldenrod",
                orbital_speed=0.051,
                debris=[]
            ),
            Planet(
                name="Uranus",
                distance=2871.0,
                size=8,
                color="cyan",
                orbital_speed=0.018,
                debris=[]
            ),
            Planet(
                name="Neptune",
                distance=4495.0,
                size=8,
                color="blue",
                orbital_speed=0.00915,
                debris=[]
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
                size=3,
                debris=[]
            )
            self.meteorites.append(meteorite)
    
    def spawn_stars(self) -> None:
        """Spawn random stars flying across the solar system."""
        self.star_spawn_timer += 1
        
        if self.star_spawn_timer >= self.star_spawn_interval:
            # Time to spawn new stars
            num_stars = random.randint(3, 7)
            
            for _ in range(num_stars):
                # Random starting position (from edges)
                edge = random.choice(['left', 'right', 'top', 'bottom'])
                
                if edge == 'left':
                    x = -20
                    y = random.uniform(0, 850)
                    vx = random.uniform(6, 10)
                    vy = random.uniform(-2, 2)
                elif edge == 'right':
                    x = 1420
                    y = random.uniform(0, 850)
                    vx = random.uniform(-10, -6)
                    vy = random.uniform(-2, 2)
                elif edge == 'top':
                    x = random.uniform(0, 1400)
                    y = -20
                    vx = random.uniform(-2, 2)
                    vy = random.uniform(6, 10)
                else:  # bottom
                    x = random.uniform(0, 1400)
                    y = 870
                    vx = random.uniform(-2, 2)
                    vy = random.uniform(-10, -6)
                
                star = Star(
                    x=x,
                    y=y,
                    vx=vx,
                    vy=vy,
                    speed=8.0,
                    size=2,
                    debris=[],
                    trail=[]
                )
                self.stars.append(star)
            
            # Reset timer for next spawn
            self.star_spawn_timer = 0
            self.star_spawn_interval = random.randint(30, 150)  # 1-5 seconds
    
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
        self.planets = self._create_planets()
        self.meteorites = []
        self.stars = []
    
    def check_meteorite_planet_collision(self) -> None:
        """Check if meteorites collide with planets."""
        for meteorite in self.meteorites[:]:
            if meteorite.is_exploding() or meteorite.burning:
                continue
            
            for planet in self.planets[:]:
                if planet.destroyed:
                    continue
                
                planet_x, planet_y = planet.get_position(self.center_x, self.center_y, self.scale)
                
                dx = meteorite.x - planet_x
                dy = meteorite.y - planet_y
                distance = math.sqrt(dx**2 + dy**2)
                
                # Check collision
                if distance < planet.size + meteorite.size:
                    # Collision! Destroy planet and meteorite
                    planet.destroy()
                    # Transfer meteorite position to planet debris
                    for particle in planet.debris:
                        particle.x = planet_x
                        particle.y = planet_y
                    
                    # Remove meteorite immediately after planet collision
                    self.meteorites.remove(meteorite)
                    break
    
    def check_meteorite_sun_collision(self) -> None:
        """Check if meteorites reach the sun."""
        sun_radius_with_margin = self.sun_radius + 5
        
        for meteorite in self.meteorites[:]:
            if meteorite.is_exploding() or meteorite.burning:
                continue
            
            dx = meteorite.x - self.center_x
            dy = meteorite.y - self.center_y
            distance = math.sqrt(dx**2 + dy**2)
            
            # Check if reached sun
            if distance < sun_radius_with_margin:
                # Meteorite hits sun - create burning effect
                meteorite.create_explosion()
                meteorite.explosion_frames = 20  # 20 frames of burning animation
                meteorite.burning = True
    
    def check_star_collisions(self) -> None:
        """Check if stars collide with planets, meteorites, or sun."""
        for star in self.stars[:]:
            if star.is_exploding():
                continue
            
            # Check collision with planets
            for planet in self.planets[:]:
                if planet.destroyed:
                    continue
                
                planet_x, planet_y = planet.get_position(self.center_x, self.center_y, self.scale)
                
                dx = star.x - planet_x
                dy = star.y - planet_y
                distance = math.sqrt(dx**2 + dy**2)
                
                # Check collision
                if distance < planet.size + star.size:
                    # Star hits planet
                    star.create_explosion()
                    star.explosion_frames = 15
                    return
            
            # Check collision with meteorites
            for meteorite in self.meteorites[:]:
                if meteorite.is_exploding() or meteorite.burning:
                    continue
                
                dx = star.x - meteorite.x
                dy = star.y - meteorite.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < star.size + meteorite.size:
                    # Star hits meteorite
                    star.create_explosion()
                    star.explosion_frames = 15
                    return
            
            # Check collision with sun
            dx = star.x - self.center_x
            dy = star.y - self.center_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.sun_radius + star.size:
                # Star hits sun - create explosion once and remove
                star.create_explosion()
                star.explosion_frames = 15
    
    def update_simulation(self) -> None:
        """Update planet positions, meteorites, and stars."""
        if self.is_running:
            # Update planets
            for planet in self.planets[:]:
                planet.update()
                if planet.destroyed and planet.destruction_frames <= 0:
                    # Remove completely destroyed planet
                    self.planets.remove(planet)
            
            # Update meteorites
            for meteorite in self.meteorites[:]:
                meteorite.update()
                if not meteorite.is_alive():
                    self.meteorites.remove(meteorite)
            
            # Update stars
            for star in self.stars[:]:
                star.update()
                if not star.is_alive():
                    self.stars.remove(star)
            
            # Spawn new stars
            self.spawn_stars()
            
            # Check collisions
            self.check_meteorite_planet_collision()
            self.check_meteorite_sun_collision()
            self.check_star_collisions()
    
    def draw(self) -> None:
        """Draw the solar system."""
        self.canvas.delete("all")
        
        # Draw background
        self.canvas.create_rectangle(0, 0, 1400, 850, fill="black", outline="black")
        
        # Draw orbital paths
        for planet in self.planets:
            if not planet.destroyed:
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
            if planet.destroyed:
                # Draw destruction debris
                for particle in planet.debris:
                    if particle.is_alive():
                        alpha = int(255 * particle.get_alpha())
                        # Create bright glowing debris
                        self.canvas.create_oval(
                            particle.x - particle.size,
                            particle.y - particle.size,
                            particle.x + particle.size,
                            particle.y + particle.size,
                            fill=particle.color,
                            outline="white",
                            width=2
                        )
            else:
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
                # Draw burning/explosion effect at sun
                frames_left = meteorite.explosion_frames
                max_frames = 20
                
                # Draw debris particles with bright colors
                for particle in meteorite.debris:
                    if particle.is_alive():
                        self.canvas.create_oval(
                            particle.x - particle.size,
                            particle.y - particle.size,
                            particle.x + particle.size,
                            particle.y + particle.size,
                            fill=particle.color,
                            outline="white",
                            width=2
                        )
                
                # Draw intense flaring effect at sun
                progress = 1 - (frames_left / max_frames)
                
                # Multiple expanding rings for intense effect
                for ring in range(4):
                    ring_radius = (progress + ring * 0.2) * 60
                    if ring_radius > 0:
                        opacity = max(0, 1 - progress - ring * 0.15)
                        ring_width = max(1, int(4 * opacity))
                        if ring_width > 0:
                            colors = ["yellow", "orange", "red", "white"]
                            color = colors[min(ring, len(colors) - 1)]
                            self.canvas.create_oval(
                                self.center_x - ring_radius,
                                self.center_y - ring_radius,
                                self.center_x + ring_radius,
                                self.center_y + ring_radius,
                                outline=color,
                                width=ring_width
                            )
                
                # Draw inner bright flash
                flash_radius = progress * 50
                if flash_radius > 0:
                    flash_opacity = max(0, 1 - progress * 1.5)
                    if flash_opacity > 0:
                        self.canvas.create_oval(
                            self.center_x - flash_radius,
                            self.center_y - flash_radius,
                            self.center_x + flash_radius,
                            self.center_y + flash_radius,
                            fill="white",
                            outline="yellow"
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
        
        # Draw stars
        for star in self.stars:
            if star.is_exploding():
                # Draw explosion
                for particle in star.debris:
                    if particle.is_alive():
                        self.canvas.create_oval(
                            particle.x - particle.size,
                            particle.y - particle.size,
                            particle.x + particle.size,
                            particle.y + particle.size,
                            fill=particle.color,
                            outline="white",
                            width=1
                        )
            else:
                # Draw star trail
                if len(star.trail) > 1:
                    for i, (trail_x, trail_y) in enumerate(star.trail):
                        # Fade trail from dark to bright
                        opacity = int(255 * (i / len(star.trail)))
                        trail_size = max(0.5, star.size * (i / len(star.trail)))
                        self.canvas.create_oval(
                            trail_x - trail_size,
                            trail_y - trail_size,
                            trail_x + trail_size,
                            trail_y + trail_size,
                            fill="cyan",
                            outline="blue"
                        )
                
                # Draw star as bright white point
                self.canvas.create_oval(
                    star.x - star.size,
                    star.y - star.size,
                    star.x + star.size,
                    star.y + star.size,
                    fill="white",
                    outline="cyan",
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
