import time
import random
import threading
import customtkinter as ctk
from pynput.mouse import Controller, Button, Listener as MouseListener
from pynput.keyboard import Listener as KeyListener
import pygetwindow as gw

# Configuración de apariencia
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

mouse = Controller()

# --- Variables de Estado del Cliente ---
gui_visible = False
ac_enabled = False
aa_enabled = False

# Opciones avanzadas
hold_mode_enabled = True
break_block_protection = True
random_mode_enabled = True  # Toggle para activar/desactivar la aleatoriedad de los clics

# Parámetros de CPS
min_cps = 10
max_cps = 14
smoothing_val = 5.0

# Monitoreo de inputs físicos
is_left_pressed = False
is_right_pressed = False
left_press_time = 0

class GeovanissV4Panel(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Geovaniss Client v4.4")
        self.geometry("320x500")
        
        # Estética de Panel Flotante In-Game
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#141414")

        # --- Cabecera ---
        self.header_frame = ctk.CTkFrame(self, fg_color="#1c1c1c", corner_radius=0, height=35)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="⚡ Geovaniss Client v4.4 [ . ]", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color="#3498db"
        )
        self.title_label.pack(side="left", padx=10, pady=6)

        # --- Contenedor ---
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#333333")
        self.main_container.pack(fill="both", expand=True, padx=8, pady=8)

        # --- MÓDULO: AUTOCLICKER ---
        self.create_module_header("Combat", "AutoClicker")
        
        self.ac_switch = ctk.CTkSwitch(self.main_container, text="Enable AutoClicker", command=self.toggle_ac, progress_color="#3498db")
        self.ac_switch.pack(anchor="w", padx=10, pady=4)

        # Visualizador de CPS (De cual a cual)
        self.cps_label = ctk.CTkLabel(self.main_container, text=f"CPS Range: {min_cps} to {max_cps}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#3498db")
        self.cps_label.pack(anchor="w", padx=10, pady=(5,0))
        
        # Slider de Min CPS
        self.min_cps_title = ctk.CTkLabel(self.main_container, text=f"Min CPS: {min_cps}", font=ctk.CTkFont(size=10))
        self.min_cps_title.pack(anchor="w", padx=10)
        self.min_cps_slider = ctk.CTkSlider(self.main_container, from_=5, to=20, number_of_steps=15, command=self.update_min_cps)
        self.min_cps_slider.set(min_cps)
        self.min_cps_slider.pack(fill="x", padx=10, pady=2)

        # Slider de Max CPS
        self.max_cps_title = ctk.CTkLabel(self.main_container, text=f"Max CPS: {max_cps}", font=ctk.CTkFont(size=10))
        self.max_cps_title.pack(anchor="w", padx=10)
        self.max_cps_slider = ctk.CTkSlider(self.main_container, from_=5, to=25, number_of_steps=20, command=self.update_max_cps)
        self.max_cps_slider.set(max_cps)
        self.max_cps_slider.pack(fill="x", padx=10, pady=2)

        # Opciones avanzadas de AutoClicker
        self.random_checkbox = ctk.CTkCheckBox(self.main_container, text="Random Mode (Jitter Humanizado)", command=self.toggle_random_mode, font=ctk.CTkFont(size=11))
        self.random_checkbox.select() if random_mode_enabled else self.random_checkbox.deselect()
        self.random_checkbox.pack(anchor="w", padx=10, pady=6)

        self.hold_checkbox = ctk.CTkCheckBox(self.main_container, text="Hold Mode (Solo al mantener click)", command=self.toggle_hold_mode, font=ctk.CTkFont(size=11))
        self.hold_checkbox.select() if hold_mode_enabled else self.hold_checkbox.deselect()
        self.hold_checkbox.pack(anchor="w", padx=10, pady=4)

        self.break_check_box = ctk.CTkCheckBox(self.main_container, text="Smart Break Block Check", command=self.toggle_break_check, font=ctk.CTkFont(size=11))
        self.break_check_box.select() if break_block_protection else self.break_check_box.deselect()
        self.break_check_box.pack(anchor="w", padx=10, pady=4)

        # --- MÓDULO: AIM ASSIST ---
        self.create_module_header("Combat", "Aim Assist")

        self.aa_switch = ctk.CTkSwitch(self.main_container, text="Enable Aim Assist", command=self.toggle_aa, progress_color="#3498db")
        self.aa_switch.pack(anchor="w", padx=10, pady=4)

        self.smooth_label = ctk.CTkLabel(self.main_container, text=f"Smoothing: {smoothing_val}", font=ctk.CTkFont(size=11))
        self.smooth_label.pack(anchor="w", padx=10)

        self.smooth_slider = ctk.CTkSlider(self.main_container, from_=1, to=15, number_of_steps=14, command=self.update_smooth)
        self.smooth_slider.set(smoothing_val)
        self.smooth_slider.pack(fill="x", padx=10, pady=4)

        # --- Pie de Página ---
        self.footer_label = ctk.CTkLabel(self, text="Press [ . ] in-game to toggle GUI", font=ctk.CTkFont(size=10), text_color="gray")
        self.footer_label.pack(pady=6)

        self.withdraw()

    def create_module_header(self, category, name):
        lbl = ctk.CTkLabel(self.main_container, text=f"[{category}] {name}", font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaaaaa")
        lbl.pack(anchor="w", padx=5, pady=(10, 2))

    def toggle_visibility(self):
        global gui_visible
        gui_visible = not gui_visible
        if gui_visible:
            self.deiconify()
            self.lift()
            self.attributes("-topmost", True)
            self.focus_force()
        else:
            self.withdraw()

    def toggle_ac(self):
        global ac_enabled
        ac_enabled = bool(self.ac_switch.get())

    def toggle_aa(self):
        global aa_enabled
        aa_enabled = bool(self.aa_switch.get())

    def toggle_random_mode(self):
        global random_mode_enabled
        random_mode_enabled = bool(self.random_checkbox.get())

    def toggle_hold_mode(self):
        global hold_mode_enabled
        hold_mode_enabled = bool(self.hold_checkbox.get())

    def toggle_break_check(self):
        global break_block_protection
        break_block_protection = bool(self.break_check_box.get())

    def update_min_cps(self, value):
        global min_cps, max_cps
        min_cps = int(value)
        if min_cps > max_cps:
            max_cps = min_cps
            self.max_cps_slider.set(max_cps)
            self.max_cps_title.configure(text=f"Max CPS: {max_cps}")
        self.min_cps_title.configure(text=f"Min CPS: {min_cps}")
        self.cps_label.configure(text=f"CPS Range: {min_cps} to {max_cps}")

    def update_max_cps(self, value):
        global min_cps, max_cps
        max_cps = int(value)
        if max_cps < min_cps:
            min_cps = max_cps
            self.min_cps_slider.set(min_cps)
            self.min_cps_title.configure(text=f"Min CPS: {min_cps}")
        self.max_cps_title.configure(text=f"Max CPS: {max_cps}")
        self.cps_label.configure(text=f"CPS Range: {min_cps} to {max_cps}")

    def update_smooth(self, value):
        global smoothing_val
        smoothing_val = round(value, 1)
        self.smooth_label.configure(text=f"Smoothing: {smoothing_val}")


# --- Detección de Minecraft ---
def is_minecraft_active():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            title = active_window.title.lower()
            if any(k in title for k in ["minecraft", "lunar", "badlion", "forge", "feather", "fabric"]):
                return True
    except Exception:
        pass
    return False


# --- Lógica de Fondo (Hilos) ---

def auto_clicker_loop():
    global ac_enabled, gui_visible, is_left_pressed, is_right_pressed, left_press_time, min_cps, max_cps, hold_mode_enabled, break_block_protection, random_mode_enabled
    while True:
        if gui_visible or not ac_enabled:
            time.sleep(0.1)
            continue

        if not is_minecraft_active():
            time.sleep(0.3)
            continue

        if hold_mode_enabled and not is_left_pressed:
            time.sleep(0.01)
            continue

        if is_right_pressed:
            time.sleep(0.05)
            continue

        if break_block_protection and is_left_pressed:
            if time.time() - left_press_time > 0.35:
                time.sleep(0.05)
                continue

        mouse.press(Button.left)
        mouse.release(Button.left)
        
        # Lógica de Random Mode (Activado vs Desactivado)
        if random_mode_enabled:
            # Variación aleatoria entre el CPS mínimo y máximo configurado
            delay = random.uniform(1.0 / max_cps, 1.0 / min_cps)
        else:
            # Velocidad fija exacta basada en el Min CPS
            delay = 1.0 / min_cps
            
        time.sleep(delay)

def aim_assist_loop():
    global aa_enabled, gui_visible, is_left_pressed, smoothing_val
    while True:
        if aa_enabled and not gui_visible and is_left_pressed:
            if is_minecraft_active():
                pass
        time.sleep(0.01)

def on_click(x, y, button, pressed):
    global is_left_pressed, is_right_pressed, left_press_time
    if button == Button.left:
        is_left_pressed = pressed
        if pressed:
            left_press_time = time.time()
    elif button == Button.right:
        is_right_pressed = pressed


if __name__ == "__main__":
    threading.Thread(target=auto_clicker_loop, daemon=True).start()
    threading.Thread(target=aim_assist_loop, daemon=True).start()
    
    mouse_listener = MouseListener(on_click=on_click)
    mouse_listener.start()

    app = GeovanissV4Panel()

    def on_key_press(key):
        try:
            if hasattr(key, 'char') and key.char == '.':
                app.after(0, app.toggle_visibility)
        except Exception:
            pass

    key_listener = KeyListener(on_press=on_key_press)
    key_listener.start()

    print("[+] Geovaniss Client v4.4 inyectado correctamente.")
    print("[+] Presiona [ . ] dentro del juego para abrir/cerrar el menú.")

    app.mainloop()