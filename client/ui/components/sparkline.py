import tkinter as tk
from typing import List, Optional
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
        secondary_color: Optional[str] = None,
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

    def update_data(self, new_val1: float, new_val2: Optional[float] = None):
        self.series1.append(float(new_val1))
        if len(self.series1) > 20:
            self.series1.pop(0)

        if self.s_color and new_val2 is not None:
            self.series2.append(float(new_val2))
            if len(self.series2) > 20:
                self.series2.pop(0)

        self.draw()

    def set_points(self, s1: List[float], s2: Optional[List[float]] = None):
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

        # Baseline & grid
        self.canvas.create_line(pad_x, self.h - pad_y, self.w - pad_x, self.h - pad_y, fill="#F1F5F9", width=1)
        self.canvas.create_line(pad_x, self.h / 2, self.w - pad_x, self.h / 2, fill="#F8FAFC", width=1)

        # Series 2
        if self.s_color and len(self.series2) >= 2:
            pts2 = self._calc_coords(self.series2, pad_x, pad_y, eff_w, eff_h)
            if len(pts2) >= 4:
                self.canvas.create_line(pts2, fill=self.s_color, width=2, smooth=True)

        # Series 1
        if len(self.series1) >= 2:
            pts1 = self._calc_coords(self.series1, pad_x, pad_y, eff_w, eff_h)
            if len(pts1) >= 4:
                poly_pts = [pts1[0], self.h - pad_y] + pts1 + [pts1[-2], self.h - pad_y]
                fill_tint = "#EFF6FF" if self.p_color == "#3B82F6" else ("#ECFDF5" if self.p_color == "#10B981" else "#F5F3FF")
                try:
                    self.canvas.create_polygon(poly_pts, fill=fill_tint, outline="")
                except Exception:
                    pass
                self.canvas.create_line(pts1, fill=self.p_color, width=2, smooth=True)

    def _calc_coords(self, data: List[float], px: int, py: int, ew: int, eh: int) -> List[float]:
        max_val = max(100.0, max(data) if data else 100.0)
        min_val = 0.0
        val_range = max(1.0, max_val - min_val)

        coords = []
        n = len(data)
        step = ew / max(1, n - 1)
        for i, val in enumerate(data):
            x = px + (i * step)
            norm = (val - min_val) / val_range
            y = (self.h - py) - (norm * eh)
            coords.extend([x, y])
        return coords


class BenchmarkBarCanvas(ctk.CTkFrame):
    """
    Renders an interactive horizontal/vertical comparison bar chart
    comparing Local Laptop CPU rendering duration against Remote GPU Offloading.
    """
    def __init__(self, master, width: int = 180, height: int = 70, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.w = width
        self.h = height

        self.canvas = tk.Canvas(
            self,
            width=self.w,
            height=self.h,
            bg="#F8FAFC",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.update_bars(0.0, 0.0)

    def update_bars(self, local_sec: float, remote_total_sec: float):
        self.canvas.delete("all")
        pad_x = 10
        pad_y = 10
        eff_w = self.w - (pad_x * 2)

        if local_sec <= 0 and remote_total_sec <= 0:
            self.canvas.create_text(self.w / 2, self.h / 2, text="Awaiting Benchmark Data", fill="#94A3B8", font=("Segoe UI", 9, "bold"))
            return

        max_val = max(0.1, max(local_sec, remote_total_sec))
        bar_h = 16

        # Bar 1: Local CPU (Amber / Red)
        y1 = pad_y
        w1 = max(12, int((local_sec / max_val) * eff_w))
        self.canvas.create_rectangle(pad_x, y1, pad_x + w1, y1 + bar_h, fill="#EF4444", outline="")
        self.canvas.create_text(pad_x + 6, y1 + bar_h / 2, text=f"Local CPU: {local_sec:.2f}s", anchor="w", fill="#FFFFFF", font=("Segoe UI", 8, "bold"))

        # Bar 2: Remote GPU (Mint Emerald)
        y2 = y1 + bar_h + 8
        w2 = max(12, int((remote_total_sec / max_val) * eff_w))
        self.canvas.create_rectangle(pad_x, y2, pad_x + w2, y2 + bar_h, fill="#10B981", outline="")
        self.canvas.create_text(pad_x + 6, y2 + bar_h / 2, text=f"Remote GPU: {remote_total_sec:.2f}s", anchor="w", fill="#FFFFFF", font=("Segoe UI", 8, "bold"))


class CloudGraphicCanvas(ctk.CTkFrame):
    """
    Draws a stylized 3D Cloud + Remote GPU Node graphic directly on Canvas
    for the Dashboard Hero Card.
    """
    def __init__(self, master, width: int = 160, height: int = 120, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.w = width
        self.h = height

        self.canvas = tk.Canvas(
            self,
            width=self.w,
            height=self.h,
            bg="#FFFFFF",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        cx = self.w // 2
        cy = self.h // 2 - 10

        # Draw Cloud bubbles (Blue shades)
        self.canvas.create_oval(cx - 45, cy - 25, cx + 5, cy + 25, fill="#60A5FA", outline="")
        self.canvas.create_oval(cx - 20, cy - 40, cx + 35, cy + 15, fill="#3B82F6", outline="")
        self.canvas.create_oval(cx + 10, cy - 25, cx + 55, cy + 20, fill="#93C5FD", outline="")
        self.canvas.create_oval(cx - 40, cy - 10, cx + 50, cy + 30, fill="#2563EB", outline="")

        # Play/stream triangle inside cloud
        self.canvas.create_polygon(
            [cx - 5, cy - 15, cx - 5, cy + 15, cx + 18, cy],
            fill="#FFFFFF",
            outline=""
        )

        # Draw Rack Server Box below cloud
        sy = cy + 28
        self.canvas.create_rectangle(cx - 45, sy, cx + 45, sy + 24, fill="#1E293B", outline="#334155", width=1)
        self.canvas.create_rectangle(cx - 45, sy + 12, cx + 45, sy + 24, fill="#0F172A", outline="")

        # Drive lights and NVIDIA green indicator
        self.canvas.create_rectangle(cx - 38, sy + 4, cx - 15, sy + 8, fill="#10B981", outline="")
        self.canvas.create_oval(cx + 25, sy + 4, cx + 31, sy + 10, fill="#34D399", outline="")
        self.canvas.create_oval(cx + 34, sy + 4, cx + 40, sy + 10, fill="#60A5FA", outline="")
        self.canvas.create_line(cx - 38, sy + 17, cx + 38, sy + 17, fill="#334155", width=1)

