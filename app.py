"""
Beam Analysis - Nominal Moment Strength Calculator
Native Desktop Application using CustomTkinter
Based on ACI 318 Example 4-1 and 4-1M
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import numpy as np
from calculator import RectangularBeam

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color Scheme
COLORS = {
    "concrete": "#E0E0DC",
    "outline": "#4D4D4D",
    "compression": "#D98C8C",
    "compression_line": "#B33333",
    "tension": "#336699",
    "steel": "#404050",
    "neutral": "#666666",
    "dimension": "#3380B3",
    "strain": "#B3D9F2",
    "strain_edge": "#336699",
    "moment_arm": "#339933",
    "result": "#1A4D99",
    "ok": "#2ECC71",
    "ng": "#E74C3C",
    "bg_dark": "#1a1a2e",
    "panel_bg": "#16213e",
    "accent": "#0f3460",
    "text": "#eaeaea",
    "text_dim": "#a0a0a0",
}


class BeamAnalysisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Beam Analysis - Nominal Moment Strength (ACI 318)")
        self.geometry("1400x850")
        self.minsize(1200, 700)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Variables
        self.unit_system = ctk.StringVar(value="Imperial")
        self.input_vars = {}
        
        # Create UI
        self._create_input_panel()
        self._create_main_panel()
        
        # Initialize with default values
        self._set_defaults()
        self._update_calculations()
    
    def _create_input_panel(self):
        """Create the left input panel."""
        self.input_frame = ctk.CTkScrollableFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=COLORS["panel_bg"]
        )
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Title
        title_label = ctk.CTkLabel(
            self.input_frame,
            text="INPUT PARAMETERS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        )
        title_label.pack(pady=(20, 15), padx=20)
        
        # Unit System Toggle
        unit_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        unit_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            unit_frame,
            text="Unit System",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")
        
        self.unit_toggle = ctk.CTkSegmentedButton(
            unit_frame,
            values=["Imperial", "SI"],
            variable=self.unit_system,
            command=self._on_unit_change,
            font=ctk.CTkFont(size=12)
        )
        self.unit_toggle.pack(fill="x", pady=(5, 0))
        
        # Separator
        self._add_separator()
        
        # Materials Section
        self._add_section_header("MATERIALS")
        self._create_input_field("fc", "fc' (Concrete)", "psi")
        self._create_input_field("fy", "fy (Steel Yield)", "psi")
        self._create_input_field("Es", "Es (Modulus)", "psi")
        self._create_input_field("beta1", "Beta1", "")
        self._create_input_field("epsilon_cu", "ecu (Ult. Strain)", "")
        
        self._add_separator()
        
        # Geometry Section
        self._add_section_header("GEOMETRY")
        self._create_input_field("b", "b (Width)", "in")
        self._create_input_field("h", "h (Total Depth)", "in")
        self._create_input_field("d", "d (Eff. Depth)", "in")
        
        self._add_separator()
        
        # Reinforcement Section
        self._add_section_header("REINFORCEMENT")
        self._create_input_field("n_bars", "Number of Bars", "")
        self._create_input_field("bar_area", "Bar Area (each)", "in2")
    
    def _add_separator(self):
        """Add a subtle separator line."""
        sep = ctk.CTkFrame(self.input_frame, height=1, fg_color=COLORS["accent"])
        sep.pack(fill="x", padx=20, pady=15)
    
    def _add_section_header(self, text):
        """Add a section header."""
        label = ctk.CTkLabel(
            self.input_frame,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["dimension"]
        )
        label.pack(anchor="w", padx=20, pady=(5, 10))
    
    def _create_input_field(self, key, label_text, unit):
        """Create an input field with label."""
        frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=3)
        
        # Label
        display_label = f"{label_text}" if not unit else f"{label_text} [{unit}]"
        label = ctk.CTkLabel(
            frame,
            text=display_label,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"]
        )
        label.pack(anchor="w")
        
        # Store label reference for unit updates
        if not hasattr(self, '_unit_labels'):
            self._unit_labels = {}
        self._unit_labels[key] = (label, label_text, unit)
        
        # Entry
        var = ctk.StringVar()
        self.input_vars[key] = var
        
        entry = ctk.CTkEntry(
            frame,
            textvariable=var,
            font=ctk.CTkFont(size=12),
            height=32,
            corner_radius=6
        )
        entry.pack(fill="x", pady=(2, 0))
        entry.bind("<KeyRelease>", lambda e: self._update_calculations())
        entry.bind("<FocusOut>", lambda e: self._update_calculations())
    
    def _create_main_panel(self):
        """Create the main content area."""
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.main_frame.grid_columnconfigure(3, weight=0, minsize=200)
        self.main_frame.grid_rowconfigure(0, weight=3)
        self.main_frame.grid_rowconfigure(1, weight=2)
        
        # Create diagram frames
        self._create_diagram_frame("Cross Section", 0)
        self._create_diagram_frame("Strain Distribution", 1)
        self._create_diagram_frame("Stress Block & Forces", 2)
        self._create_results_panel()
        self._create_equations_panel()
    
    def _create_diagram_frame(self, title, col):
        """Create a diagram frame with matplotlib canvas."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["panel_bg"], corner_radius=8)
        frame.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)
        
        # Title
        label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"]
        )
        label.pack(pady=(10, 5))
        
        # Figure
        fig, ax = plt.subplots(figsize=(4, 3.5), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_dark"])
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store references
        if col == 0:
            self.fig_section, self.ax_section, self.canvas_section = fig, ax, canvas
        elif col == 1:
            self.fig_strain, self.ax_strain, self.canvas_strain = fig, ax, canvas
        else:
            self.fig_stress, self.ax_stress, self.canvas_stress = fig, ax, canvas
    
    def _create_results_panel(self):
        """Create the results summary panel."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["panel_bg"], corner_radius=8)
        frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
        
        # Title
        ctk.CTkLabel(
            frame,
            text="Results",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"]
        ).pack(pady=(10, 5))
        
        # Results text
        self.results_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["text"],
            corner_radius=6,
            wrap="word"
        )
        self.results_text.pack(fill="both", expand=True, padx=8, pady=8)
    
    def _create_equations_panel(self):
        """Create the equations panel."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["panel_bg"], corner_radius=8)
        frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
        
        # Title
        ctk.CTkLabel(
            frame,
            text="Calculation Procedure (ACI 318)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"]
        ).pack(pady=(10, 5), anchor="w", padx=15)
        
        # Equations text
        self.equations_text = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["text"],
            corner_radius=6,
            height=150
        )
        self.equations_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def _set_defaults(self):
        """Set default values based on unit system."""
        if self.unit_system.get() == "Imperial":
            defaults = {
                "fc": "4000", "fy": "60000", "Es": "29000000",
                "beta1": "0.85", "epsilon_cu": "0.003",
                "b": "12", "h": "20", "d": "17.5",
                "n_bars": "4", "bar_area": "0.79"
            }
            units = {"fc": "psi", "fy": "psi", "Es": "psi", "b": "in", "h": "in", "d": "in", "bar_area": "in2"}
        else:
            defaults = {
                "fc": "20", "fy": "420", "Es": "200000",
                "beta1": "0.85", "epsilon_cu": "0.003",
                "b": "250", "h": "565", "d": "500",
                "n_bars": "3", "bar_area": "510"
            }
            units = {"fc": "MPa", "fy": "MPa", "Es": "MPa", "b": "mm", "h": "mm", "d": "mm", "bar_area": "mm2"}
        
        for key, val in defaults.items():
            self.input_vars[key].set(val)
        
        # Update labels
        for key, (label, text, _) in self._unit_labels.items():
            unit = units.get(key, "")
            display = f"{text}" if not unit else f"{text} [{unit}]"
            label.configure(text=display)
    
    def _on_unit_change(self, value):
        """Handle unit system change."""
        self._set_defaults()
        self._update_calculations()
    
    def _get_input_value(self, key, default=0.0):
        """Get input value as float."""
        try:
            return float(self.input_vars[key].get())
        except (ValueError, KeyError):
            return default
    
    def _update_calculations(self):
        """Update all calculations and displays."""
        try:
            # Get values
            fc = self._get_input_value("fc", 4000)
            fy = self._get_input_value("fy", 60000)
            Es = self._get_input_value("Es", 29000000)
            beta1 = self._get_input_value("beta1", 0.85)
            epsilon_cu = self._get_input_value("epsilon_cu", 0.003)
            b = self._get_input_value("b", 12)
            h = self._get_input_value("h", 20)
            d = self._get_input_value("d", 17.5)
            n_bars = int(self._get_input_value("n_bars", 4))
            bar_area = self._get_input_value("bar_area", 0.79)
            
            if any(v <= 0 for v in [fc, fy, Es, b, h, d, n_bars, bar_area]):
                return
            
            # Create beam and calculate
            beam = RectangularBeam(
                b=b, h=h, d=d, fc=fc, fy=fy,
                n_bars=n_bars, bar_area=bar_area,
                Es=Es, beta1=beta1, epsilon_cu=epsilon_cu,
                unit_system=self.unit_system.get().lower()
            )
            results = beam.calculate_mn()
            units = beam.get_units()
            
            # Update diagrams
            self._draw_cross_section(b, h, d, results["a"], results["c"], n_bars, bar_area)
            self._draw_strain_diagram(h, d, results["c"], epsilon_cu, results["epsilon_s"])
            self._draw_stress_diagram(h, d, results["a"], results["c"], results["T_display"], units)
            
            # Update results
            self._update_results_text(results, units)
            self._update_equations_text(results, units, n_bars, bar_area, fc, fy, Es, beta1, epsilon_cu, b, d)
            
        except Exception as e:
            pass  # Silently handle errors during typing
    
    def _draw_cross_section(self, b, h, d, a, c, n_bars, bar_area):
        """Draw the beam cross section."""
        ax = self.ax_section
        ax.clear()
        ax.set_facecolor(COLORS["bg_dark"])
        
        # Concrete beam
        rect = patches.Rectangle((0, 0), b, h, facecolor=COLORS["concrete"],
                                   edgecolor=COLORS["outline"], linewidth=1.5)
        ax.add_patch(rect)
        
        # Compression zone
        comp = patches.Rectangle((0, h - a), b, a, facecolor=COLORS["compression"],
                                   edgecolor="none", alpha=0.6)
        ax.add_patch(comp)
        
        # Neutral axis
        ax.plot([0, b], [h - c, h - c], '--', color=COLORS["neutral"], linewidth=1.2)
        
        # Steel bars
        bar_r = np.sqrt(bar_area / np.pi) * 0.7
        steel_y = h - d
        cx = [b / 2] if n_bars == 1 else np.linspace(b * 0.12, b * 0.88, n_bars)
        
        for x in cx:
            circle = patches.Circle((x, steel_y), bar_r, facecolor=COLORS["steel"],
                                      edgecolor="#1A1A1A", linewidth=0.5)
            ax.add_patch(circle)
        
        # Dimensions
        ax.text(b / 2, -h * 0.06, f'b={b:.1f}', ha='center', fontsize=8, color=COLORS["text"])
        ax.text(b + b * 0.1, h / 2, f'h={h:.1f}', fontsize=8, color=COLORS["text"])
        ax.text(-b * 0.12, h - a / 2, f'a={a:.2f}', fontsize=8, color=COLORS["compression_line"])
        ax.text(b + b * 0.04, h - c, f'c={c:.2f}', fontsize=7, color=COLORS["neutral"])
        
        ax.set_xlim(-b * 0.2, b * 1.3)
        ax.set_ylim(-h * 0.1, h * 1.05)
        ax.set_aspect('equal')
        ax.axis('off')
        
        self.canvas_section.draw()
    
    def _draw_strain_diagram(self, h, d, c, epsilon_cu, epsilon_s):
        """Draw the strain distribution."""
        ax = self.ax_strain
        ax.clear()
        ax.set_facecolor(COLORS["bg_dark"])
        
        steel_y = h - d
        strain_w = 0.4
        
        # Beam outline
        ax.plot([0, 0], [0, h], color='#555', linewidth=1)
        
        # Strain profile
        x_top = epsilon_cu * strain_w / 0.003
        x_bot = epsilon_s * strain_w / 0.003
        
        ax.fill([0, x_top, x_bot, 0], [h, h, steel_y, steel_y],
                facecolor=COLORS["strain"], edgecolor=COLORS["strain_edge"],
                linewidth=1.2, alpha=0.5)
        
        # Neutral axis
        ax.plot([-0.05, strain_w * 1.2], [h - c, h - c], '--', color=COLORS["neutral"], linewidth=1)
        ax.text(-0.03, h - c, f'c={c:.2f}', fontsize=7, ha='right', color=COLORS["neutral"])
        
        # Labels
        ax.text(x_top + 0.02, h, f'ecu={epsilon_cu:.4f}', fontsize=8, color=COLORS["text"])
        ax.text(x_bot + 0.02, steel_y, f'es={epsilon_s:.5f}', fontsize=8, color=COLORS["text"])
        
        ax.set_xlim(-0.1, strain_w * 1.5)
        ax.set_ylim(-h * 0.1, h * 1.05)
        ax.axis('off')
        
        self.canvas_strain.draw()
    
    def _draw_stress_diagram(self, h, d, a, c, T_display, units):
        """Draw the stress block and forces."""
        ax = self.ax_stress
        ax.clear()
        ax.set_facecolor(COLORS["bg_dark"])
        
        steel_y = h - d
        stress_w = 0.5
        
        # Compression block
        comp = patches.Rectangle((0, h - a), stress_w, a, facecolor=COLORS["compression"],
                                   edgecolor=COLORS["compression_line"], linewidth=1.2, alpha=0.7)
        ax.add_patch(comp)
        ax.text(stress_w / 2, h - a / 2, "0.85fc'", ha='center', fontsize=8, color=COLORS["text"])
        
        # Force arrows
        ax.annotate('', xy=(stress_w + 0.2, h - a / 2), xytext=(stress_w + 0.05, h - a / 2),
                    arrowprops=dict(arrowstyle='->', color=COLORS["compression_line"], lw=2))
        ax.text(stress_w + 0.22, h - a / 2, f'C={T_display:.0f} {units["force_k"]}',
                fontsize=8, color=COLORS["compression_line"])
        
        # Steel and tension
        ax.plot([0, stress_w * 0.3], [steel_y, steel_y], color=COLORS["steel"], linewidth=2)
        ax.annotate('', xy=(0.2, steel_y), xytext=(0, steel_y),
                    arrowprops=dict(arrowstyle='->', color=COLORS["tension"], lw=2))
        ax.text(0.22, steel_y, f'T={T_display:.0f} {units["force_k"]}',
                fontsize=8, color=COLORS["tension"])
        
        # Neutral axis
        ax.plot([-0.05, stress_w + 0.25], [h - c, h - c], '--', color=COLORS["neutral"], linewidth=1)
        
        # Moment arm
        xa = stress_w + 0.35
        ax.plot([xa, xa], [h - a / 2, steel_y], color=COLORS["moment_arm"], linewidth=1.5)
        ax.text(xa + 0.02, (h - a / 2 + steel_y) / 2, 'd-a/2', fontsize=7, color=COLORS["moment_arm"])
        
        ax.set_xlim(-0.1, stress_w + 0.55)
        ax.set_ylim(-h * 0.1, h * 1.05)
        ax.set_aspect('equal')
        ax.axis('off')
        
        self.canvas_stress.draw()
    
    def _update_results_text(self, results, units):
        """Update the results text panel."""
        yield_str = "Yes (Yields)" if results["yield_check"] else "No (Elastic)"
        as_str = "OK" if results["as_check"] else "NOT OK"
        
        text = f"""RESULTS SUMMARY
================

Steel Area:
  As = {results['As']:.4f} {units['area']}

Forces:
  T = C = {results['T_display']:.2f} {units['force_k']}

Geometry:
  a = {results['a']:.4f} {units['length']}
  c = {results['c']:.4f} {units['length']}

Strain Check:
  ey = {results['epsilon_y']:.6f}
  es = {results['epsilon_s']:.6f}
  Yield: {yield_str}

NOMINAL MOMENT:
  Mn = {results['Mn_display']:.1f} {units['moment_display']}

Min Steel Check:
  As,min = {results['As_min']:.4f} {units['area']}
  Status: {as_str}
"""
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
    
    def _update_equations_text(self, results, units, n_bars, bar_area, fc, fy, Es, beta1, epsilon_cu, b, d):
        """Update the equations panel."""
        yield_ok = "[OK]" if results["yield_check"] else "[NG]"
        as_ok = "[OK]" if results["as_check"] else "[NG]"
        
        text = f"""STEP-BY-STEP CALCULATIONS

Step 1: Steel Area and Tension Force
  As = n x A_bar = {n_bars} x {bar_area:.3f} = {results['As']:.3f} {units['area']}
  T = As x fy = {results['As']:.3f} x {fy:.0f} = {results['T']:.0f} {units['force']}  ({results['T_display']:.1f} {units['force_k']})

Step 2: Stress Block Depth
  a = (As x fy) / (0.85 x fc' x b) = {results['T']:.0f} / (0.85 x {fc:.0f} x {b:.1f}) = {results['a']:.4f} {units['length']}
  c = a / beta1 = {results['a']:.4f} / {beta1:.3f} = {results['c']:.4f} {units['length']}

Step 3: Strain Check  {yield_ok}
  ey = fy / Es = {fy:.0f} / {Es:.0f} = {results['epsilon_y']:.6f}
  es = ((d - c) / c) x ecu = (({d:.2f} - {results['c']:.2f}) / {results['c']:.2f}) x {epsilon_cu:.4f} = {results['epsilon_s']:.6f}

Step 4: Nominal Moment
  Mn = As x fy x (d - a/2) = {results['T']:.0f} x ({d:.2f} - {results['a']:.4f}/2) = {results['Mn_k']:.0f} {units['moment_k']}
  
  >>> Mn = {results['Mn_display']:.1f} {units['moment_display']} <<<

Step 5: Minimum Steel Check  {as_ok}
  As,min = {results['As_min']:.4f} {units['area']}
  As {'>' if results['as_check'] else '<'} As,min
"""
        self.equations_text.delete("1.0", "end")
        self.equations_text.insert("1.0", text)


if __name__ == "__main__":
    app = BeamAnalysisApp()
    app.mainloop()
