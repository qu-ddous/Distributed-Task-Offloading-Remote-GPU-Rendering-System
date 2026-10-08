"""
Global Fast MouseWheel Scroll Engine for CustomTkinter
Patches CTkScrollableFrame._mouse_wheel_all to:
1. Only scroll the currently mapped/visible page.
2. Allow scrolling anywhere the mouse is physically positioned over the frame
   (including over buttons, cards, text, images, and child canvases).
3. Accelerate scroll speed (85-100 pixels per notch instead of 20 pixels),
   allowing users to quickly and naturally glide to the bottom of the page.
"""
import sys
import customtkinter as ctk

_PATCHED = False

def install_fast_scroll_engine():
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    def _fast_mouse_wheel_all(self, event):
        try:
            # Only scroll if this scrollable frame is currently visible on screen
            if not self.winfo_ismapped():
                return

            # Check if mouse pointer is physically positioned over this frame
            try:
                mx, my = self.winfo_pointerxy()
                rx, ry = self.winfo_rootx(), self.winfo_rooty()
                rw, rh = self.winfo_width(), self.winfo_height()
                if not (rx <= mx <= rx + rw and ry <= my <= ry + rh):
                    return
            except Exception:
                pass

            # Fast smooth scroll
            if sys.platform.startswith("win"):
                delta = getattr(event, "delta", 0)
                if delta:
                    # 85 pixels per notch for quick, responsive scrolling
                    units = -int((delta / 120) * 85)
                    if getattr(self, "_shift_pressed", False):
                        if self._parent_canvas.xview() != (0.0, 1.0):
                            self._parent_canvas.xview("scroll", units, "units")
                    else:
                        if self._parent_canvas.yview() != (0.0, 1.0):
                            self._parent_canvas.yview("scroll", units, "units")
            elif sys.platform == "darwin":
                delta = getattr(event, "delta", 0)
                if delta:
                    units = -int(delta * 4)
                    if getattr(self, "_shift_pressed", False):
                        if self._parent_canvas.xview() != (0.0, 1.0):
                            self._parent_canvas.xview("scroll", units, "units")
                    else:
                        if self._parent_canvas.yview() != (0.0, 1.0):
                            self._parent_canvas.yview("scroll", units, "units")
            else:
                num = getattr(event, "num", None)
                step = -4 if num == 4 else 4
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview_scroll(step, "units")
        except Exception:
            pass

    ctk.CTkScrollableFrame._mouse_wheel_all = _fast_mouse_wheel_all

def enable_fast_smooth_scroll(scrollable_frame=None, scroll_factor: int = 2):
    install_fast_scroll_engine()

# Auto-install on module import
install_fast_scroll_engine()
