from typing import Optional
import customtkinter as ctk

from client.ui.theme import *
from shared.docs_content import DOCS_DATA

class DocsView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, is_server: bool = False):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller
        self.is_server = is_server
        self.current_lang = "en" # "en" or "ur"

        self._build_header_card()
        self._build_content_container()
        self._render_documentation()

    def on_page_shown(self):
        """Called when user navigates to Docs tab."""
        pass

    def _build_header_card(self):
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        header.pack(fill="x", padx=10, pady=(0, 16))

        box = ctk.CTkFrame(header, fg_color="transparent")
        box.pack(fill="x", padx=22, pady=18)
        box.grid_columnconfigure(0, weight=1)

        # Left titles
        left = ctk.CTkFrame(box, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        badge_txt = "SERVER NODE GUIDE" if self.is_server else "STUDIO MANUAL & GUIDE"
        badge = ctk.CTkLabel(
            left,
            text=badge_txt,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_PURPLE,
            corner_radius=6,
            padx=10,
            pady=3
        )
        badge.pack(anchor="w", pady=(0, 6))

        self.lbl_title = ctk.CTkLabel(
            left,
            text=DOCS_DATA["en"]["title"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            left,
            text=DOCS_DATA["en"]["subtitle"],
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.lbl_subtitle.pack(anchor="w", pady=(2, 0))

        # Right Language Switcher Card
        lang_card = ctk.CTkFrame(box, fg_color=BG_CARD_ALT, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        lang_card.grid(row=0, column=1, sticky="e", padx=(14, 0))

        ctk.CTkLabel(
            lang_card,
            text="🌐 Language / Zaban:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY
        ).pack(side="left", padx=(12, 8), pady=8)

        self.btn_lang_en = ctk.CTkButton(
            lang_card,
            text="🇬🇧 English",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=90,
            height=30,
            corner_radius=8,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            command=lambda: self._set_language("en")
        )
        self.btn_lang_en.pack(side="left", padx=(0, 6), pady=6)

        self.btn_lang_ur = ctk.CTkButton(
            lang_card,
            text="🇵🇰 Roman Urdu",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=115,
            height=30,
            corner_radius=8,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=TEXT_SECONDARY,
            command=lambda: self._set_language("ur")
        )
        self.btn_lang_ur.pack(side="left", padx=(0, 8), pady=6)

    def _set_language(self, lang: str):
        if self.current_lang == lang:
            return
        self.current_lang = lang

        if lang == "en":
            self.btn_lang_en.configure(fg_color=ACCENT_BLUE, text_color="#FFFFFF")
            self.btn_lang_ur.configure(fg_color="#E2E8F0", text_color=TEXT_SECONDARY)
        else:
            self.btn_lang_ur.configure(fg_color=ACCENT_BLUE, text_color="#FFFFFF")
            self.btn_lang_en.configure(fg_color="#E2E8F0", text_color=TEXT_SECONDARY)

        data = DOCS_DATA[lang]
        self.lbl_title.configure(text=data["title"])
        self.lbl_subtitle.configure(text=data["subtitle"])

        self._render_documentation()

    def _build_content_container(self):
        self.sections_container = ctk.CTkFrame(self, fg_color="transparent")
        self.sections_container.pack(fill="x", padx=10, pady=(0, 20))

    def _render_documentation(self):
        # Clear previous cards
        for widget in self.sections_container.winfo_children():
            widget.destroy()

        data = DOCS_DATA[self.current_lang]

        for sec in data["sections"]:
            card = ctk.CTkFrame(self.sections_container, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=(0, 16))

            # Header row in card
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=22, pady=(18, 10))

            badge = ctk.CTkLabel(
                top_row,
                text=sec["tag"],
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#FFFFFF",
                fg_color=sec["tag_color"],
                corner_radius=6,
                padx=10,
                pady=2
            )
            badge.pack(anchor="w", pady=(0, 4))

            title_row = ctk.CTkFrame(top_row, fg_color="transparent")
            title_row.pack(fill="x")

            ctk.CTkLabel(
                title_row,
                text=sec["icon"],
                font=ctk.CTkFont(size=20),
                width=30
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                title_row,
                text=sec["title"],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=TEXT_PRIMARY
            ).pack(side="left")

            ctk.CTkLabel(
                card,
                text=sec["summary"],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                justify="left"
            ).pack(anchor="w", padx=22, pady=(0, 14))

            # Points inside card
            for p_title, p_desc in sec["points"]:
                p_box = ctk.CTkFrame(card, fg_color=BG_CARD_ALT, corner_radius=10, border_width=1, border_color="#E2E8F0")
                p_box.pack(fill="x", padx=22, pady=(0, 10))

                content_box = ctk.CTkFrame(p_box, fg_color="transparent")
                content_box.pack(fill="x", padx=14, pady=10)

                ctk.CTkLabel(
                    content_box,
                    text=p_title,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=TEXT_PRIMARY,
                    justify="left"
                ).pack(anchor="w")

                ctk.CTkLabel(
                    content_box,
                    text=p_desc,
                    font=ctk.CTkFont(size=11),
                    text_color=TEXT_SECONDARY,
                    justify="left",
                    wraplength=760
                ).pack(anchor="w", pady=(4, 0))

                # Add quick copy button if mentioning commands or IPs
                if "192.168.99.1" in p_desc or "DIRECT_CABLE_PAIRING.bat" in p_desc:
                    bar = ctk.CTkFrame(content_box, fg_color="#FFFFFF", corner_radius=6, border_width=1, border_color=BORDER_COLOR)
                    bar.pack(anchor="w", pady=(8, 0))

                    sample_txt = "192.168.99.1" if "192.168.99.1" in p_desc else "dist/DIRECT_CABLE_PAIRING.bat"
                    ctk.CTkLabel(bar, text=f"⚡ {sample_txt}", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color=ACCENT_BLUE).pack(side="left", padx=8)

                    def make_copy_fn(t=sample_txt):
                        def fn():
                            try:
                                self.clipboard_clear()
                                self.clipboard_append(t)
                            except Exception:
                                pass
                        return fn

                    btn_c = ctk.CTkButton(
                        bar,
                        text="Copy",
                        width=50,
                        height=22,
                        font=ctk.CTkFont(size=9, weight="bold"),
                        fg_color="#F1F5F9",
                        hover_color="#E2E8F0",
                        text_color=TEXT_PRIMARY,
                        corner_radius=4,
                        command=make_copy_fn()
                    )
                    btn_c.pack(side="left", padx=(0, 4), pady=2)

