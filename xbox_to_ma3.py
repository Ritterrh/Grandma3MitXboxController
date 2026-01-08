import pygame
import time
from pythonosc import udp_client
import sys
import json
import os
from pathlib import Path

# Standard Konfiguration (Fallback)
DEFAULT_CONFIG = {
    "osc": {
        "host": "127.0.0.1",
        "port": 8000,
        "target_page": 1,
        "fader_pan": 201,
        "fader_tilt": 202,
        "fader_dimmer": 203,
        "fader_fine_pan": 204,
        "fader_fine_tilt": 205
    },
    "controller": {
        "deadzone": 0.15,
        "sensitivity": 1.0,
        "fine_sensitivity": 0.3,
        "update_rate": 50,
        "smoothing": 0.3
    },
    "features": {
        "use_right_stick_fine_control": True,
        "show_debug_info": False,
        "auto_reconnect": True
    },
    "ui": {
        "window_width": 800,
        "window_height": 600,
        "theme": "dark"
    }
}

# Lade Konfiguration
def load_config():
    """Lädt config.json oder verwendet Default-Werte"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                loaded = json.load(f)
                # Merge mit Default (falls Keys fehlen)
                config = DEFAULT_CONFIG.copy()
                for key in loaded:
                    if isinstance(loaded[key], dict):
                        config[key].update(loaded[key])
                    else:
                        config[key] = loaded[key]
                print(f"✓ Config geladen: {config_path}")
                return config
        except Exception as e:
            print(f"⚠ Fehler beim Laden der Config: {e}")
            print("  Verwende Default-Konfiguration")
    else:
        print(f"ℹ config.json nicht gefunden, verwende Defaults")
    return DEFAULT_CONFIG

CONFIG = load_config()

# UI Konfiguration
WINDOW_WIDTH = CONFIG['ui']['window_width']
WINDOW_HEIGHT = CONFIG['ui']['window_height']
BG_COLOR = (20, 20, 30)
TEXT_COLOR = (200, 200, 220)
ACCENT_COLOR = (100, 150, 255)
SUCCESS_COLOR = (100, 255, 150)
WARNING_COLOR = (255, 200, 100)
ERROR_COLOR = (255, 100, 100)

# Controller-Typen Erkennung
KNOWN_CONTROLLERS = {
    'xbox': ['xbox', 'xinput'],
    'playstation': ['playstation', 'ps4', 'ps5', 'dualshock', 'dualsense', 'sony'],
}

def detect_controller_type(name):
    """Erkennt den Controller-Typ basierend auf dem Namen"""
    name_lower = name.lower()
    for controller_type, keywords in KNOWN_CONTROLLERS.items():
        if any(keyword in name_lower for keyword in keywords):
            return controller_type
    return 'generic'

def get_button_mapping(controller_type):
    """Gibt das Button-Mapping für verschiedene Controller zurück"""
    mappings = {
        'xbox': {
            'name': 'Xbox Controller',
            'buttons': {0: 'A', 1: 'B', 2: 'X', 3: 'Y', 6: 'Back', 7: 'Start'},
            'rt_axis': 5,
            'lt_axis': 2,
        },
        'playstation': { 
            'name': 'PlayStation Controller',
            'buttons': {0: 'X', 1: 'O', 2: '□', 3: '△', 8: 'Share', 9: 'Options'},
            'rt_axis': 5,
            'lt_axis': 2,
        },
        'generic': {
            'name': 'Generic Controller',
            'buttons': {0: 'Btn 0', 1: 'Btn 1', 2: 'Btn 2', 3: 'Btn 3'},
            'rt_axis': 5,
            'lt_axis': 2,
        }
    }
    return mappings.get(controller_type, mappings['generic'])

def apply_deadzone(value, deadzone):
    """
    Wendet eine Deadzone auf einen Achsenwert an.
    value: -1.0 bis 1.0
    deadzone: Schwellwert (z.B. 0.15 = 15%)
    """
    if abs(value) < deadzone:
        return 0.0
    # Skaliere den Wert außerhalb der Deadzone zurück auf den vollen Bereich
    sign = 1 if value > 0 else -1
    scaled = (abs(value) - deadzone) / (1.0 - deadzone)
    return sign * scaled

def smooth_value(current, target, smoothing):
    """
    Glättet Werte mittels linearer Interpolation.
    smoothing: 0.0 = keine Glättung, 1.0 = maximale Glättung
    """
    return current + (target - current) * (1.0 - smoothing)

class MA3ControllerUI:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("MA3 Controller Bridge v2.0")
        
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # OSC Client
        osc_config = CONFIG['osc']
        self.client = udp_client.SimpleUDPClient(osc_config['host'], osc_config['port'])
        self.osc_host = osc_config['host']
        self.osc_port = osc_config['port']
        self.osc_connected = True
        
        self.joystick = None
        self.controller_type = None
        self.button_mapping = None
        self.running = True
        
        # Werte-Speicher (smoothed values)
        self.pan_val = 0.0
        self.tilt_val = 0.0
        self.pan_fine_val = 0.0
        self.tilt_fine_val = 0.0
        self.trigger_val = 0.0
        self.button_states = {}
        
        # Raw values (vor smoothing)
        self.pan_raw = 0.0
        self.tilt_raw = 0.0
        self.pan_fine_raw = 0.0
        self.tilt_fine_raw = 0.0
        
        # Statistiken
        self.osc_message_count = 0
        self.start_time = time.time()
        
    def wait_for_controller(self):
        """Wartet auf Controller-Verbindung mit UI-Feedback"""
        waiting = True
        dots = 0
        last_check = time.time()
        
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
            
            # Prüfe alle 0.5 Sekunden auf neue Controller
            if time.time() - last_check > 0.5:
                pygame.joystick.quit()
                pygame.joystick.init()
                
                if pygame.joystick.get_count() > 0:
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
                    
                    # Erkenne Controller-Typ
                    controller_name = self.joystick.get_name()
                    self.controller_type = detect_controller_type(controller_name)
                    self.button_mapping = get_button_mapping(self.controller_type)
                    
                    waiting = False
                else:
                    dots = (dots + 1) % 4
                    last_check = time.time()
            
            # Zeichne Wartebildschirm
            self.screen.fill(BG_COLOR)
            
            title = self.font_large.render("MA3 Controller Bridge v2.0", True, ACCENT_COLOR)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
            
            wait_text = f"Warte auf Controller{'.' * dots}   "
            wait_surface = self.font_medium.render(wait_text, True, WARNING_COLOR)
            self.screen.blit(wait_surface, (WINDOW_WIDTH // 2 - wait_surface.get_width() // 2, 250))
            
            info_lines = [
                "Verbinde deinen Xbox oder PlayStation Controller",
                "ESC = Beenden"
            ]
            y = 350
            for line in info_lines:
                text = self.font_small.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, y))
                y += 30
            
            # Config Info
            config_info = f"Config: {self.osc_host}:{self.osc_port} | DZ: {int(CONFIG['controller']['deadzone']*100)}% | Smooth: {int(CONFIG['controller']['smoothing']*100)}%"
            text = self.font_tiny.render(config_info, True, (100, 100, 120))
            self.screen.blit(text, (20, WINDOW_HEIGHT - 30))
            
            pygame.display.flip()
            self.clock.tick(30)
        
        return self.running
    
    def draw_stick_indicator(self, x, y, value_x, value_y, raw_x, raw_y, label):
        """Zeichnet einen Joystick-Indikator mit Deadzone-Visualisierung"""
        size = 100
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Hintergrund
        pygame.draw.circle(self.screen, (40, 40, 50), (center_x, center_y), size // 2)
        
        # Deadzone Circle
        deadzone_radius = int((size // 2) * CONFIG['controller']['deadzone'])
        pygame.draw.circle(self.screen, (60, 60, 70), (center_x, center_y), deadzone_radius, 1)
        
        # Outer circle
        pygame.draw.circle(self.screen, ACCENT_COLOR, (center_x, center_y), size // 2, 2)
        
        # Crosshair
        pygame.draw.line(self.screen, (60, 60, 70), (center_x - size // 2, center_y), 
                        (center_x + size // 2, center_y), 1)
        pygame.draw.line(self.screen, (60, 60, 70), (center_x, center_y - size // 2), 
                        (center_x, center_y + size // 2), 1)
        
        # Raw Position (grau)
        raw_pos_x = center_x + int(raw_x * (size // 2 - 5))
        raw_pos_y = center_y + int(raw_y * (size // 2 - 5))
        pygame.draw.circle(self.screen, (100, 100, 120), (raw_pos_x, raw_pos_y), 4)
        
        # Smoothed Position (grün)
        pos_x = center_x + int(value_x * (size // 2 - 5))
        pos_y = center_y + int(value_y * (size // 2 - 5))
        pygame.draw.circle(self.screen, SUCCESS_COLOR, (pos_x, pos_y), 8)
        
        # Label
        label_surface = self.font_small.render(label, True, TEXT_COLOR)
        self.screen.blit(label_surface, (x, y - 25))
        
        # Werte
        value_text = f"X: {value_x:+.2f}  Y: {value_y:+.2f}"
        value_surface = self.font_tiny.render(value_text, True, TEXT_COLOR)
        self.screen.blit(value_surface, (x, y + size + 5))
    
    def draw_bar(self, x, y, width, height, value, label, max_val=100):
        """Zeichnet einen horizontalen Balken"""
        # Hintergrund
        pygame.draw.rect(self.screen, (40, 40, 50), (x, y, width, height))
        pygame.draw.rect(self.screen, ACCENT_COLOR, (x, y, width, height), 2)
        
        # Füllung
        fill_width = int(width * (value / max_val))
        if fill_width > 0:
            pygame.draw.rect(self.screen, SUCCESS_COLOR, (x, y, fill_width, height))
        
        # Label und Wert
        label_surface = self.font_small.render(label, True, TEXT_COLOR)
        self.screen.blit(label_surface, (x, y - 25))
        
        value_text = f"{value:.1f}"
        value_surface = self.font_small.render(value_text, True, TEXT_COLOR)
        self.screen.blit(value_surface, (x + width + 10, y + height // 2 - value_surface.get_height() // 2))
    
    def draw_button_states(self, x, y):
        """Zeichnet Button-Status"""
        title = self.font_small.render("Buttons:", True, TEXT_COLOR)
        self.screen.blit(title, (x, y))
        
        y += 30
        for btn_id, btn_name in self.button_mapping['buttons'].items():
            is_pressed = self.button_states.get(btn_id, False)
            color = SUCCESS_COLOR if is_pressed else (60, 60, 70)
            
            pygame.draw.circle(self.screen, color, (x + 15, y + 12), 8)
            text = self.font_small.render(btn_name, True, TEXT_COLOR)
            self.screen.blit(text, (x + 30, y))
            y += 30
    
    def update_values(self):
        """Liest Controller-Werte und sendet OSC"""
        pygame.event.pump()
        
        deadzone = CONFIG['controller']['deadzone']
        smoothing = CONFIG['controller']['smoothing']
        sensitivity = CONFIG['controller']['sensitivity']
        fine_sensitivity = CONFIG['controller']['fine_sensitivity']
        
        # Linker Stick (Pan/Tilt) - Raw lesen
        pan_input = self.joystick.get_axis(0)
        tilt_input = self.joystick.get_axis(1)
        
        # Deadzone anwenden
        pan_deadzone = apply_deadzone(pan_input, deadzone)
        tilt_deadzone = apply_deadzone(tilt_input, deadzone)
        
        # Mit Sensitivity multiplizieren
        self.pan_raw = pan_deadzone * sensitivity
        self.tilt_raw = tilt_deadzone * sensitivity
        
        # Smoothing
        self.pan_val = smooth_value(self.pan_val, self.pan_raw, smoothing)
        self.tilt_val = smooth_value(self.tilt_val, self.tilt_raw, smoothing)
        
        # Rechter Stick (Fine Control) - optional
        if CONFIG['features']['use_right_stick_fine_control']:
            pan_fine_input = self.joystick.get_axis(2)  # Right stick X
            tilt_fine_input = self.joystick.get_axis(3)  # Right stick Y
            
            pan_fine_deadzone = apply_deadzone(pan_fine_input, deadzone)
            tilt_fine_deadzone = apply_deadzone(tilt_fine_input, deadzone)
            
            self.pan_fine_raw = pan_fine_deadzone * fine_sensitivity
            self.tilt_fine_raw = tilt_fine_deadzone * fine_sensitivity
            
            self.pan_fine_val = smooth_value(self.pan_fine_val, self.pan_fine_raw, smoothing)
            self.tilt_fine_val = smooth_value(self.tilt_fine_val, self.tilt_fine_raw, smoothing)
        
        # Skaliere auf 0-100 für MA3
        osc_config = CONFIG['osc']
        pan_ma3 = (self.pan_val + 1) * 50
        tilt_ma3 = (self.tilt_val + 1) * 50
        
        # Sende Hauptwerte
        self.client.send_message(f"/Page{osc_config['target_page']}/Fader{osc_config['fader_pan']}", pan_ma3)
        self.client.send_message(f"/Page{osc_config['target_page']}/Fader{osc_config['fader_tilt']}", tilt_ma3)
        self.osc_message_count += 2
        
        # Sende Fine-Control Werte (wenn aktiv)
        if CONFIG['features']['use_right_stick_fine_control']:
            pan_fine_ma3 = (self.pan_fine_val + 1) * 50
            tilt_fine_ma3 = (self.tilt_fine_val + 1) * 50
            
            self.client.send_message(f"/Page{osc_config['target_page']}/Fader{osc_config['fader_fine_pan']}", pan_fine_ma3)
            self.client.send_message(f"/Page{osc_config['target_page']}/Fader{osc_config['fader_fine_tilt']}", tilt_fine_ma3)
            self.osc_message_count += 2
        
        # Trigger (RT)
        try:
            trigger_raw = self.joystick.get_axis(self.button_mapping['rt_axis'])
            if trigger_raw > -1:
                trigger_processed = (trigger_raw + 1) * 50
                self.trigger_val = smooth_value(self.trigger_val, trigger_processed, smoothing)
                self.client.send_message(f"/Page{osc_config['target_page']}/Fader{osc_config['fader_dimmer']}", self.trigger_val)
                self.osc_message_count += 1
        except:
            pass
        
        # Buttons
        for btn_id in self.button_mapping['buttons'].keys():
            try:
                is_pressed = self.joystick.get_button(btn_id)
                self.button_states[btn_id] = is_pressed
                
                # Button A/X für Flash
                if btn_id == 0:
                    self.client.send_message(f"/Page{osc_config['target_page']}/Key{osc_config['fader_pan']}", 1 if is_pressed else 0)
                    if is_pressed:
                        self.osc_message_count += 1
            except:
                pass
    
    def draw_ui(self):
        """Zeichnet die Haupt-UI"""
        self.screen.fill(BG_COLOR)
        
        # Header
        title = self.font_large.render("MA3 Controller Bridge v2.0", True, ACCENT_COLOR)
        self.screen.blit(title, (20, 20))
        
        # Controller Info
        controller_info = f"{self.button_mapping['name']}: {self.joystick.get_name()}"
        info_surface = self.font_small.render(controller_info, True, SUCCESS_COLOR)
        self.screen.blit(info_surface, (20, 80))
        
        # OSC Info
        osc_info = f"OSC → {self.osc_host}:{self.osc_port}"
        osc_surface = self.font_small.render(osc_info, True, SUCCESS_COLOR if self.osc_connected else ERROR_COLOR)
        self.screen.blit(osc_surface, (20, 105))
        
        # Linker Stick (Pan/Tilt)
        self.draw_stick_indicator(50, 180, self.pan_val, self.tilt_val, self.pan_raw, self.tilt_raw, "Left: Pan/Tilt")
        
        # Rechter Stick (Fine Control) - wenn aktiv
        if CONFIG['features']['use_right_stick_fine_control']:
            self.draw_stick_indicator(250, 180, self.pan_fine_val, self.tilt_fine_val, 
                                     self.pan_fine_raw, self.tilt_fine_raw, "Right: Fine")
        
        # Trigger Bar
        self.draw_bar(50, 420, 200, 30, self.trigger_val, "RT (Dimmer)")
        
        # Button Status
        self.draw_button_states(500, 180)
        
        # OSC Werte
        y = 420
        osc_config = CONFIG['osc']
        osc_title = self.font_small.render(f"OSC (Page {osc_config['target_page']}):", True, TEXT_COLOR)
        self.screen.blit(osc_title, (500, y))
        y += 30
        
        osc_values = [
            f"F{osc_config['fader_pan']} Pan:   {(self.pan_val + 1) * 50:.1f}",
            f"F{osc_config['fader_tilt']} Tilt:  {(self.tilt_val + 1) * 50:.1f}",
            f"F{osc_config['fader_dimmer']} Dim: {self.trigger_val:.1f}",
        ]
        
        if CONFIG['features']['use_right_stick_fine_control']:
            osc_values.extend([
                f"F{osc_config['fader_fine_pan']} PanF: {(self.pan_fine_val + 1) * 50:.1f}",
                f"F{osc_config['fader_fine_tilt']} TiltF: {(self.tilt_fine_val + 1) * 50:.1f}",
            ])
        
        for value_line in osc_values:
            text = self.font_tiny.render(value_line, True, TEXT_COLOR)
            self.screen.blit(text, (500, y))
            y += 22
        
        # Statistiken
        runtime = time.time() - self.start_time
        stats_text = f"Runtime: {int(runtime)}s | OSC Msgs: {self.osc_message_count} | FPS: {int(self.clock.get_fps())}"
        stats_surface = self.font_tiny.render(stats_text, True, (100, 100, 120))
        self.screen.blit(stats_surface, (20, WINDOW_HEIGHT - 50))
        
        # Config Info
        config_text = f"DZ: {int(CONFIG['controller']['deadzone']*100)}% | Smooth: {int(CONFIG['controller']['smoothing']*100)}% | Sens: {CONFIG['controller']['sensitivity']:.1f}x"
        config_surface = self.font_tiny.render(config_text, True, (100, 100, 120))
        self.screen.blit(config_surface, (20, WINDOW_HEIGHT - 30))
        
        # Footer
        help_text = "ESC = Beenden  |  Update: {}Hz  |  Deadzone (grau) | Smoothed (grün)".format(CONFIG['controller']['update_rate'])
        help_surface = self.font_tiny.render(help_text, True, (100, 100, 110))
        self.screen.blit(help_surface, (20, WINDOW_HEIGHT - 10))
        
        pygame.display.flip()
    
    def run(self):
        """Hauptschleife"""
        if not self.wait_for_controller():
            return
        
        print(f"\n✓ Controller verbunden: {self.joystick.get_name()}")
        print(f"✓ Typ erkannt als: {self.controller_type}")
        print(f"✓ Sende OSC an MA3 @ {self.osc_host}:{self.osc_port}")
        print(f"✓ Deadzone: {int(CONFIG['controller']['deadzone']*100)}%")
        print(f"✓ Smoothing: {int(CONFIG['controller']['smoothing']*100)}%")
        print(f"✓ Fine Control: {'Aktiv (Rechter Stick)' if CONFIG['features']['use_right_stick_fine_control'] else 'Deaktiviert'}")
        print(f"\n🎮 Bereit! UI läuft mit {CONFIG['controller']['update_rate']} Hz\n")
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
            
            self.update_values()
            self.draw_ui()
            self.clock.tick(CONFIG['controller']['update_rate'])
        
        pygame.quit()
        print("\n✓ Beendet.")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  MA3 Controller Bridge v2.0")
    print("="*60 + "\n")
    app = MA3ControllerUI()
    app.run()