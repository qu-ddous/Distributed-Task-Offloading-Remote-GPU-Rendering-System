import tkinter as tk
from typing import List, Tuple
import customtkinter as ctk

class MiniGraphCanvas(ctk.CTkFrame):
    """
    Ultra-lightweight vector Sparkline/Wave graph widget built directly on Tkinter Canvas.
    Supports single or dual curves with gradients, smooth Bézier interpolation, and zero flicker.
    """
    def __init__(
        self,
        master,
        width: int = 180,
        height: int = 65,
        bg_color: str = "#FFFFFF",
        primary_color: str = "#3B82F6",
        secondary_color: str = None,
        fill_alpha: bool = True,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.w = width
        self.h = height
        self.bg_color = bg_color
        self.p_color = primary_color
        self.s_color = secondary_color
        self.fill_alpha = fill_alpha

        self.canvas = tk.Canvas(
            self,
            width=self.w,
            height=self.h,
            bg=self.bg_color,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.series1: List[float] = [20, 35, 45, 30, 65, 50, 70, 68, 85, 60, 75, 68]
        self.series2: List[float] = [15, 25, 30, 45, 40, 55, 48, 60, 50, 45, 52, 48] if secondary_color else []
        self.draw()

    def update_data(self, new_val1: float, new_val2: float = None):
        self.series1.append(float(new_val1))
        if len(self.series1) > 20:
            self.series1.pop(0)

        if self.s_color and new_val2 is not None:
            self.series2.append(float(new_val2))
            if len(self.series2) > 20:
                self.series2.pop(0)

        self.draw()

    def set_points(self, s1: List[float], s2: List[float] = None):
        self.series1 = list(s1)
        if s2:
            self.series2 = list(s2)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        pad_x = 4
        pad_y = 6
        eff_w = self.w - (pad_x * 2)
        eff_h = self.h - (pad_y * 2)

        # Draw grid line (subtle baseline)
        self.canvas.create_line(pad_x, self.h - pad_y, self.w - pad_x, self.h - pad_y, fill="#F1F5F9", width=1)
        self.canvas.create_line(pad_x, self.h / 2, self.w - pad_x, self.h / 2, fill="#F8FAFC", width=1)

        # Draw series 2 if present
        if self.s_color and len(self.series2) >= 2:
            pts2 = self._calc_coords(self.series2, pad_x, pad_y, eff_w, eff_h)
            if len(pts2) >= 4:
                self.canvas.create_line(pts2, fill=self.s_color, width=2, smooth=True)

        # Draw series 1
        if len(self.series1) >= 2:
            pts1 = self._calc_coords(self.series1, pad_x, pad_y, eff_w, eff_h)
            if len(pts1) >= 4:
                # Shaded area under curve
                poly_pts = [pts1[0], self.h - pad_y] + pts1 + [pts1[-2], self.h - pad_y]
                # Subtle fill
                fill_tint = "#EFF6FF" if self.p_color == "#3B82F6" else ("#ECFDF5" if self.p_color == "#10B981" else "#F5F3FF")
                try:
                    self.canvas.create_polygon(poly_pts, fill=fill_tint, outline="")
                except Exception:
                    pass
                # Stroke line
                self.canvas.create_line(pts1, fill=self.p_color, width=2, smooth=True)

    def _calc_coords(self, data: List[float], px: int, py: int, ew: int, eh: int) -> List[float]:
        max_val = max(100.0, max(data) if data else 100.0)
        min_val = 0.0
        val_range = max(1.0, max_val - min_val)

        coords = []
        n = len(data)
        step = ew / max(1, n - 1)

        for i, v in enumerate(data):
            x = px + (i * step)
            norm = (v - min_val) / val_range
            y = (self.h - py) - (norm * eh)
            coords.extend([x, y])

        return coords

