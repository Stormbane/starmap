import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
import subprocess
import ctypes
from pathlib import Path
import yaml
from utils.resource_utils import resource_path, ensure_directory_exists

class StarMapUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Sky Map Generator")
        self.window.geometry("800x1000")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main frame with scrollbar
        self.main_frame = ctk.CTkScrollableFrame(self.window)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Sky Map Generator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        # Constellation Settings
        self.constellation_frame = ctk.CTkFrame(self.main_frame)
        self.constellation_frame.pack(padx=20, pady=10, fill="x")
        
        self.constellation_label = ctk.CTkLabel(
            self.constellation_frame,
            text="Constellation Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.constellation_label.pack(pady=5)
        
        # Max constellations input
        self.max_constellations_frame = ctk.CTkFrame(self.constellation_frame)
        self.max_constellations_frame.pack(padx=10, pady=5, fill="x")
        
        self.max_constellations_label = ctk.CTkLabel(
            self.max_constellations_frame,
            text="Max Constellations to Plot:"
        )
        self.max_constellations_label.pack(side="left", padx=5)
        
        self.max_constellations_var = tk.StringVar(value="20")
        self.max_constellations_entry = ctk.CTkEntry(
            self.max_constellations_frame,
            textvariable=self.max_constellations_var,
            width=100
        )
        self.max_constellations_entry.pack(side="left", padx=5)
        
        # Constellation selection
        self.constellation_list_frame = ctk.CTkFrame(self.constellation_frame)
        self.constellation_list_frame.pack(padx=10, pady=5, fill="x")
        
        self.constellation_list_label = ctk.CTkLabel(
            self.constellation_list_frame,
            text="Constellations to Show:"
        )
        self.constellation_list_label.pack(pady=5)
        
        self.constellation_vars = {}
        constellations = ["Ari", "Tau", "Gem", "Cnc", "Leo", "Vir", "Lib", "Sco", 
                         "Sgr", "Cap", "Aqr", "Psc", "Cen", "Cru", "Car", "Boo", 
                         "Crv", "Ori", "CMa", "Lup"]
        
        for const in constellations:
            var = tk.BooleanVar(value=True)
            self.constellation_vars[const] = var
            ctk.CTkCheckBox(
                self.constellation_list_frame,
                text=const,
                variable=var
            ).pack(pady=2)
        
        # Star Settings
        self.star_frame = ctk.CTkFrame(self.main_frame)
        self.star_frame.pack(padx=20, pady=10, fill="x")
        
        self.star_label = ctk.CTkLabel(
            self.star_frame,
            text="Star Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.star_label.pack(pady=5)
        
        # Star settings inputs
        star_settings = [
            ("Naked Eye Magnitude Limit", "6.5"),
            ("Label Magnitude Limit", "2.5"),
            ("Max Stars to Plot", "9000"),
            ("Batch Size", "500")
        ]
        
        self.star_vars = {}
        for label, default in star_settings:
            frame = ctk.CTkFrame(self.star_frame)
            frame.pack(padx=10, pady=5, fill="x")
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            var = tk.StringVar(value=default)
            self.star_vars[label] = var
            ctk.CTkEntry(frame, textvariable=var, width=100).pack(side="left", padx=5)
        
        # Show magnitude checkbox
        self.show_magnitude_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.star_frame,
            text="Show Magnitude in Star Labels",
            variable=self.show_magnitude_var
        ).pack(pady=5)
        
        # Planet Settings
        self.planet_frame = ctk.CTkFrame(self.main_frame)
        self.planet_frame.pack(padx=20, pady=10, fill="x")
        
        self.planet_label = ctk.CTkLabel(
            self.planet_frame,
            text="Planet Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.planet_label.pack(pady=5)
        
        # Planet appearance settings
        planets = {
            "Mercury": {"color": "#1A873A", "symbol": "☿", "text_color": "#105223"},
            "Venus": {"color": "#FFFFE3", "symbol": "♀", "text_color": "#C4C4AE"},
            "Mars": {"color": "#700101", "symbol": "♂", "text_color": "#2B0007"},
            "Jupiter": {"color": "#FFDD40", "symbol": "♃", "text_color": "#A8922A"},
            "Saturn": {"color": "#042682", "symbol": "♄", "text_color": "#021547"},
            "Uranus": {"color": "#5B8FB9", "symbol": "⛢", "text_color": "#021547"},
            "Neptune": {"color": "#3E66F9", "symbol": "♆", "text_color": "#021547"},
            "Pluto": {"color": "#8B4513", "symbol": "♇", "text_color": "#021547"},
            "Moon": {"color": "#CCCCCC", "symbol": "☽", "text_color": "#7F7F7F"}
        }
        
        self.planet_vars = {}
        for planet, settings in planets.items():
            planet_frame = ctk.CTkFrame(self.planet_frame)
            planet_frame.pack(padx=10, pady=5, fill="x")
            
            ctk.CTkLabel(planet_frame, text=planet).pack(side="left", padx=5)
            
            self.planet_vars[planet] = {}
            for setting, value in settings.items():
                var = tk.StringVar(value=value)
                self.planet_vars[planet][setting] = var
                ctk.CTkEntry(planet_frame, textvariable=var, width=100).pack(side="left", padx=5)
        
        # Generate button
        self.generate_button = ctk.CTkButton(
            self.main_frame,
            text="Generate Image",
            command=self.generate_image,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.generate_button.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=10)
    
    def generate_image(self):
        # Create config dictionary
        config = {
            "max_constellations_to_plot": int(self.max_constellations_var.get()),
            "show_only_constellations": [
                const for const, var in self.constellation_vars.items()
                if var.get()
            ],
            "planets": {
                planet: {
                    setting: var.get()
                    for setting, var in settings.items()
                }
                for planet, settings in self.planet_vars.items()
            },
            "stars": {
                "naked_eye_mag_limit": float(self.star_vars["Naked Eye Magnitude Limit"].get()),
                "label_mag_limit": float(self.star_vars["Label Magnitude Limit"].get()),
                "max_stars_to_plot": int(self.star_vars["Max Stars to Plot"].get()),
                "batch_size": int(self.star_vars["Batch Size"].get()),
                "show_magnitude": self.show_magnitude_var.get()
            }
        }
        
        # Save config
        with open("config.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Create output directory if it doesn't exist
        output_dir = ensure_directory_exists("generated_images")
        
        # Generate image (placeholder for now)
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='white')
        
        # Save the image
        output_path = os.path.join(output_dir, "generated_skymap.png")
        img.save(output_path)
        
        # Open the image
        os.startfile(output_path)
        
        self.status_label.configure(text=f"Image generated successfully: {output_path}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = StarMapUI()
    app.run() 