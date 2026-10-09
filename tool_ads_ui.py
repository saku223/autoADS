import customtkinter as ctk
import requests
import time
import threading
import json
import os
import sys  
import re
import math
import random
import tempfile
import subprocess
import hashlib
import winreg 
import unicodedata 
import urllib.parse
import ddddocr
from PIL import Image, ImageDraw, ImageFont

_original_sleep = time.sleep

def _stoppable_sleep(secs):
    t = threading.current_thread()
    end_time = time.time() + secs
    while time.time() < end_time:
        if getattr(t, "stop_requested", False):
            raise Exception("Bị ngắt bởi người dùng (STOP)")
        _original_sleep(max(0.01, min(0.2, end_time - time.time())))

time.sleep = _stoppable_sleep

def create_hacker_icon():
    if not os.path.exists("hacker.ico"):
        try:
            img = Image.new('RGBA', (64, 64), color=(15, 16, 21, 255))
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("consola.ttf", 36)
            except:
                font = ImageFont.load_default()
            d.text((12, 12), "/>", fill=(0, 255, 65, 255), font=font)
            img.save("hacker.ico")
        except:
            pass

create_hacker_icon()

# CHUYỂN SANG GIAO DIỆN SÁNG (LIGHT MODE)
ctk.set_appearance_mode("Light")

CONFIG_FILE = "config_ads.json"
LICENSE_FILE = "license.txt"
CURRENT_VERSION = "6"
GITHUB_REPO = "saku223/autoADS"
API_URL = "https://script.google.com/macros/s/AKfycbydxSMlkK0vOp_QHcmSXjCJJ71MAYBO9Bhbq3nmtyaWXYNn-k8mZieHrb4JNdzSRXy4Dw/exec"

# ================= HÀM LẤY THÔNG TIN MÀN HÌNH CHỈNH (DYNAMIC MONITORS) =================
def get_target_monitor_rect(window_width, window_height):
    import ctypes
    monitors = []
    def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
        rect = lprcMonitor.contents
        monitors.append({
            "left": rect.left,
            "top": rect.top,
            "right": rect.right,
            "bottom": rect.bottom,
            "width": rect.right - rect.left,
            "height": rect.bottom - rect.top
        })
        return True

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long)
        ]

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(RECT),
        ctypes.c_void_p
    )

    try:
        proc = MonitorEnumProc(monitor_enum_proc)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, proc, 0)
    except:
        return {"left": 0, "top": 0, "right": 1920, "bottom": 1080, "width": 1920, "height": 1080}

    if len(monitors) >= 2:
        # Sắp xếp các màn hình từ trái qua phải theo tọa độ left
        monitors.sort(key=lambda m: m["left"])
        # Luôn chọn màn hình ngoài cùng bên PHẢI
        target = monitors[-1]
    else:
        # Chỉ có 1 màn hình
        target = monitors[0] if monitors else {"left": 0, "top": 0, "right": 1920, "bottom": 1080, "width": 1920, "height": 1080}

    return target

# ================= HÀM XỬ LÝ TIẾNG VIỆT KHÔNG DẤU =================
def remove_accents(input_str):
    if not input_str: return ""
    s = re.sub(r'[đĐ]', 'd', input_str)
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')

# ================= HÀM ĐỊNH DANH ĐƯỜNG DẪN THỰC VÀ ÂM THANH =================
def get_real_exe_path():
    """Lấy chính xác đường dẫn file exe thực sự của người dùng, KHÔNG lấy file tạm ONEFIL trong Temp."""
    # 1. Nuitka onefile environment variable (Chính xác 100% khi chạy EXE đóng gói bởi Nuitka)
    nuitka_bin = os.environ.get("NUITKA_ONEFILE_BINARY")
    if nuitka_bin and os.path.exists(nuitka_bin):
        return os.path.abspath(nuitka_bin)

    # 2. Nếu đang chạy bằng python script (.py) khi lập trình
    if not getattr(sys, "frozen", False):
        return sys.executable

    # 3. Khi chạy EXE đóng gói: tìm tool_ads_ui.exe thực tế trong thư mục làm việc
    for cand in [
        os.path.abspath("tool_ads_ui.exe"),
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0] if sys.argv else ".")), "tool_ads_ui.exe")
    ]:
        if os.path.exists(cand):
            return cand

    if sys.argv and sys.argv[0] and sys.argv[0].lower().endswith(".exe") and os.path.exists(sys.argv[0]):
        return os.path.abspath(sys.argv[0])

    if sys.executable:
        exe_low = sys.executable.lower()
        if "onefil" not in exe_low and "temp" not in exe_low and os.path.exists(sys.executable):
            return os.path.abspath(sys.executable)

    return sys.executable

def get_real_app_dir():
    """Lấy thư mục làm việc thực sự của tool (nơi chứa tool_ads_ui.exe hoặc tool_ads_ui.py)."""
    nuitka_bin = os.environ.get("NUITKA_ONEFILE_BINARY")
    if nuitka_bin and os.path.exists(nuitka_bin):
        return os.path.dirname(os.path.abspath(nuitka_bin))

    if not getattr(sys, "frozen", False):
        try:
            return os.path.dirname(os.path.abspath(__file__))
        except:
            return os.path.abspath(".")

    exe_p = get_real_exe_path()
    if exe_p and os.path.exists(exe_p) and exe_p.lower().endswith(".exe"):
        return os.path.dirname(os.path.abspath(exe_p))

    return os.path.abspath(".")

def play_money_ting_ting():
    """Phát âm thanh chuông 'ting ting' chuyển tiền nhận thông báo."""
    def _run():
        try:
            import winsound
            # Ting ting - 2 nốt ngân vang vui tai như chuông báo nhận tiền ngân hàng
            winsound.Beep(1760, 110) # Nốt Ting 1 (A6)
            time.sleep(0.04)
            winsound.Beep(2637, 280) # Nốt Ting 2 (E7)
        except Exception:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass
    threading.Thread(target=_run, daemon=True).start()

# ================= HÀM XỬ LÝ ĐƯỜNG DẪN ẢNH TRONG EXE =================
def resource_path(relative_path):
    """Tìm đường dẫn tài nguyên (ảnh, icon, config) trong mọi môi trường (Nuitka, PyInstaller, Python script)."""
    candidates = []

    # 1. Thư mục giải nén tạm thời của Nuitka onefile
    nuitka_dir = os.environ.get("NUITKA_ONEFILE_DIRECTORY")
    if nuitka_dir:
        candidates.append(os.path.join(nuitka_dir, relative_path))

    # 2. Thư mục giải nén tạm thời của PyInstaller
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(os.path.join(meipass, relative_path))

    # 3. Thư mục giải nén tạm của Python/Nuitka (Nơi Nuitka onefile giải nén img1.png, img2.png, img3.png)
    if sys.executable:
        candidates.append(os.path.join(os.path.dirname(sys.executable), relative_path))

    # 4. Thư mục thật của ứng dụng (nơi đặt file exe người dùng)
    try:
        app_dir = get_real_app_dir()
        if app_dir:
            candidates.append(os.path.join(app_dir, relative_path))
    except: pass

    # 5. Thư mục file mã nguồn hiện tại (__file__)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(script_dir, relative_path))
    except: pass

    # 6. Thư mục làm việc hiện tại (CWD)
    try:
        candidates.append(os.path.abspath(relative_path))
    except: pass

    for cand in candidates:
        if cand and os.path.exists(cand):
            return cand

    return relative_path

# ================= HỆ THỐNG BẢO MẬT (HWID) =================
def get_hwid():
    cache_file = "hwid_cache.dat"
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached = f.read().strip()
                if cached: return cached
        except: pass

    hwid_val = None
    # 1. Đọc MachineGuid từ Windows Registry (Chuẩn 100% trên Windows 10, 11)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            if guid:
                hwid_val = hashlib.sha256(guid.encode()).hexdigest()[:16].upper()
    except Exception:
        pass

    # 2. Fallback sang lệnh reg query nếu winreg bị hạn chế quyền
    if not hwid_val:
        try:
            cmd = 'reg query "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            for line in output.splitlines():
                if "MachineGuid" in line:
                    guid = line.split()[-1].strip()
                    hwid_val = hashlib.sha256(guid.encode()).hexdigest()[:16].upper()
                    break
        except Exception:
            pass

    # 3. Fallback sang UUID phần cứng
    if not hwid_val:
        try:
            import uuid
            hwid_val = hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:16].upper()
        except Exception:
            hwid_val = f"PC-{random.randint(100000, 999999)}"

    # Cố định HWID vào file để không bị thay đổi giữa các lần mở
    try:
        with open(cache_file, "w") as f:
            f.write(hwid_val)
    except: pass

    return hwid_val

# ================= CLASS QUẢN LÝ ẢNH NỀN TÙY CHỈNH =================
class DraggableBackground:
    def __init__(self, master, image_path, x, y, size=150):
        self.master = master
        self.image_path = image_path
        self.size = size
        self.x = x
        self.y = y
        self.angle = 0
        self.locked = False

        try:
            real_path = resource_path(image_path)
            if not os.path.exists(real_path):
                for folder in [
                    os.environ.get("NUITKA_ONEFILE_DIRECTORY", ""),
                    os.path.dirname(sys.executable) if sys.executable else "",
                    get_real_app_dir(),
                    os.path.abspath(".")
                ]:
                    cand = os.path.join(folder, image_path) if folder else ""
                    if cand and os.path.exists(cand):
                        real_path = cand
                        break
            self.original_image = Image.open(real_path)
            if self.original_image.mode != 'RGBA':
                self.original_image = self.original_image.convert('RGBA')
                
            self.ctk_image = ctk.CTkImage(light_image=self.original_image, size=(self.size, self.size))
            self.label = ctk.CTkLabel(master, image=self.ctk_image, text="")
            self.label.place(x=self.x, y=self.y)
            
            self.label.lower() 

            self.label.bind("<ButtonPress-1>", self.on_press)
            self.label.bind("<B1-Motion>", self.on_drag)
            self.label.bind("<MouseWheel>", self.on_scroll)
            self.label.bind("<Shift-MouseWheel>", self.on_shift_scroll)
        except Exception as e:
            pass

    def on_press(self, event):
        if self.locked: return
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        if self.locked: return
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.x += dx
        self.y += dy
        self.label.place(x=self.x, y=self.y)

    def on_scroll(self, event):
        if self.locked: return
        if event.delta > 0: self.size += 10
        else:
            self.size -= 10
            if self.size < 30: self.size = 30
        self.update_image()

    def on_shift_scroll(self, event):
        if self.locked: return
        if event.delta > 0: self.angle = (self.angle + 10) % 360
        else: self.angle = (self.angle - 10) % 360
        self.update_image()

    def update_image(self):
        if not hasattr(self, 'original_image') or self.original_image is None:
            return
        if not hasattr(self, 'ctk_image') or self.ctk_image is None:
            return
        if not hasattr(self, 'label') or self.label is None:
            return
        try:
            rotated = self.original_image.rotate(self.angle, expand=True, resample=Image.Resampling.BICUBIC)
        except AttributeError:
            rotated = self.original_image.rotate(self.angle, expand=True, resample=Image.BICUBIC)
        
        scale_factor = self.size / max(self.original_image.width, self.original_image.height)
        new_width = max(10, int(rotated.width * scale_factor))
        new_height = max(10, int(rotated.height * scale_factor))

        self.ctk_image.configure(light_image=rotated, size=(new_width, new_height))
        self.label.configure(image=self.ctk_image)

    def lock(self):
        self.locked = True

# ================= MÀN HÌNH ĐĂNG NHẬP =================
class LoginScreen(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("System Authentication")
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(fg_color="#0F1015")
        
        # Giấu cửa sổ đi ngay khi vừa khởi tạo để kiểm tra Auto-login ngầm
        self.withdraw()

        try: 
            icon_path = os.path.abspath("hacker.ico")
            self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass

        window_width = 400
        window_height = 320
        target = get_target_monitor_rect(window_width, window_height)
        x = int(target["left"] + (target["width"] / 2) - (window_width / 2))
        y = int(target["top"] + (target["height"] / 2) - (window_height / 2))
        self.geometry(f"+{x}+{y}")

        self.hwid = get_hwid()

        ctk.CTkLabel(self, text="💻 HỆ THỐNG XÁC THỰC", font=("Consolas", 22, "bold"), text_color="#00FF41").pack(pady=(20, 10))

        frame = ctk.CTkFrame(self, fg_color="#1A1C23", border_width=1, border_color="#00FF41")
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        ctk.CTkLabel(frame, text="MÃ NHẬN DIỆN PHẦN CỨNG:", font=("Consolas", 12, "bold"), text_color="#A0A0A0").pack(pady=(15, 0))
        self.hwid_entry = ctk.CTkEntry(frame, width=210, justify="center", font=("Consolas", 14, "bold"), fg_color="#000000", border_color="#005C18", text_color="#00FF41")
        self.hwid_entry.insert(0, self.hwid)
        self.hwid_entry.configure(state="readonly")
        self.hwid_entry.pack(pady=(5, 10))

        ctk.CTkLabel(frame, text="NHẬP LICENSE KEY:", font=("Consolas", 12, "bold"), text_color="#A0A0A0").pack(pady=(5, 0))
        self.key_entry = ctk.CTkEntry(frame, width=250, justify="center", show="*", font=("Consolas", 14), fg_color="#000000", border_color="#005C18", text_color="#00FF41")
        self.key_entry.pack(pady=(5, 15))

        self.btn_login = ctk.CTkButton(self, text="► KẾT NỐI", font=("Consolas", 14, "bold"), fg_color="#005C18", hover_color="#00FF41", text_color="#FFFFFF", border_width=1, border_color="#00FF41", command=self.check_login_thread)
        self.btn_login.pack(pady=(0, 20))

        self.after(50, self.load_saved_key)

    def load_saved_key(self):
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, "r") as f:
                    saved_key = f.read().strip()
                    if saved_key:
                        self.key_entry.insert(0, saved_key)
                        self.check_login_thread(auto_login=True)
                        return
            except: pass
        
        # Nếu không có file license hợp lệ thì hiện khung lên cho nhập
        self.deiconify()

    def check_login_thread(self, auto_login=False):
        key = self.key_entry.get().strip()
        if not key:
            self.btn_login.configure(text="❌ THIẾU LICENSE!", fg_color="#8B0000", hover_color="#CD5C5C")
            self.after(1500, lambda: self.btn_login.configure(text="► KẾT NỐI", fg_color="#005C18", hover_color="#00FF41"))
            return
            
        self.btn_login.configure(text="[ CONNECTING... ]", fg_color="#D68910", hover_color="#F39C12", state="disabled")
        threading.Thread(target=self.call_api, args=(key, auto_login), daemon=True).start()

    def call_api(self, key, auto_login):
        try:
            payload = {"key": key, "hwid": self.hwid}
            response = requests.post(API_URL, json=payload, timeout=10)
            data = response.json()
            
            if data.get("success"):
                if "app_config" in data:
                    self.master.app_config = data["app_config"]
                
                with open(LICENSE_FILE, "w") as f: 
                    f.write(key)
                
                self.after(0, self.success)
            else:
                msg = data.get("message", "Lỗi không xác định")
                self.after(0, lambda: self.show_error(msg))
                if auto_login:
                    self.after(0, lambda: self.key_entry.delete(0, 'end'))
                    self.after(0, self.deiconify)

        except Exception as e:
            err_str = str(e)
            if "JSONDecodeError" in str(type(e)) or "Expecting value" in err_str:
                self.after(0, lambda: self.show_error("Web App chưa mở quyền Anyone!"))
            elif API_URL == "" or "AKfycbxUNF3IXYubM" in API_URL:
                self.after(0, lambda: self.show_error("Chưa cấu hình API_URL!"))
            else:
                self.after(0, lambda: self.show_error("Lỗi kết nối Server!"))
            if auto_login:
                self.after(0, self.deiconify)

    def show_error(self, message):
        self.btn_login.configure(text=f"ACCESS DENIED: {message}", fg_color="#8B0000", hover_color="#CD5C5C", state="normal")
        self.after(2000, lambda: self.btn_login.configure(text="► THỬ LẠI", fg_color="#005C18", hover_color="#00FF41"))

    def success(self):
        self.withdraw()
        start_main_app(self.master)
        self.after(200, self.destroy)

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Loading...")
        width, height = 1450, 820 
        target = get_target_monitor_rect(width, height)
        x = int(target["left"] + (target["width"] / 2) - (width / 2))
        y = int(target["top"] + (target["height"] / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.overrideredirect(True)
        self.configure(fg_color='#00FF00')
        self.wm_attributes("-transparentcolor", '#00FF00')
        self.canvas = ctk.CTkCanvas(self, bg='#00FF00', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.cx = 725
        self.cy = 410

        self.base_heart_points = []
        initial_points = []
        for i in range(0, 360, 2): 
            t = math.radians(i)
            px = 16 * math.sin(t)**3
            py = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            self.base_heart_points.append((px, py))
            initial_points.extend([self.cx, self.cy])

        self.heart_id = self.canvas.create_polygon(initial_points, fill="#F5EBEF", outline="#DDBBC8", width=4, smooth=True, tags="core")
        self.canvas.create_text(self.cx, self.cy - 50, text="AUTO ADSPOWER V12", fill="#B85C7B", font=("Arial", 36, "bold"), tags="core")
        self.canvas.create_text(self.cx, self.cy + 30, text="~ Hello Kìn ~", fill="#D28F5A", font=("Candara", 28, "bold italic"), tags="core")

        self.heart_time = 0.0
        self.particles = []
        # Màu tone hồng/tím để đồng nhất với tool
        self.colors = [
            "#B85C7B", "#DDBBC8", "#FFB6C1", "#FF69B4", "#DB7093", "#C71585", "#FFFFFF"
        ]
        self.firework_colors = [
            "#9B59B6", "#2980B9", "#E67E22", "#16A085", "#F1C40F",
            "#C0392B", "#27AE60", "#D35400", "#8E44AD", "#1ABC9C"
        ]
        self.after(300, lambda: self.launch_firework(self.cx - 145, self.cy - 60))  
        self.after(1000, lambda: self.launch_firework(self.cx + 145, self.cy - 60)) 
        self.after(1800, lambda: self.launch_firework(self.cx, self.cy + 150)) 

        self.is_exploding = False
        self.homing_particles = []
        self.animate()
        self.after(3200, self.finale_explosion)

    def finale_explosion(self):
        self.is_exploding = True
        self.canvas.delete("core")
        # Xóa sạch các hạt pháo hoa nhiều màu còn sót lại trên màn hình
        for p in self.particles[:]:
            self.canvas.delete(p["id"])
        self.particles.clear()
        
        for _ in range(1200):
            color = random.choice(self.colors)
            if random.random() < 0.6:
                edge = random.randint(0, 3)
                if edge == 0:   tx, ty = random.randint(0, 1450), random.randint(0, 20)
                elif edge == 1: tx, ty = random.randint(0, 1450), random.randint(800, 820)
                elif edge == 2: tx, ty = random.randint(0, 20), random.randint(0, 820)
                else:           tx, ty = random.randint(1430, 1450), random.randint(0, 820)
            else:
                tx, ty = random.randint(50, 1400), random.randint(50, 770)
                
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(15, 50)         
            size = random.uniform(3, 8)          
            pid = self.canvas.create_oval(self.cx, self.cy, self.cx+size, self.cy+size, fill=color, outline="")
            
            self.homing_particles.append({
                "id": pid, 
                "x": self.cx, "y": self.cy,
                "vx": math.cos(angle)*speed, 
                "vy": math.sin(angle)*speed, 
                "target_x": tx, "target_y": ty,
                "size": size,
                "phase": 0, 
                "timer": random.randint(5, 20)
            })
            
        self.after(1700, self.prepare_ui)

    def launch_firework(self, cx, cy):
        color = random.choice(self.firework_colors)
        for _ in range(50):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(3, 9)         
            size = random.uniform(4, 9)          
            pid = self.canvas.create_oval(cx, cy, cx+size, cy+size, fill=color, outline="")
            self.particles.append({"id": pid, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "size": size})

    def animate(self):
        if not self.winfo_exists(): return 
        
        if not hasattr(self, "start_time"):
            self.start_time = time.time()
        self.heart_time = time.time() - self.start_time
        
        t = min(1.0, self.heart_time / 1.5)
        if t == 0:
            intro_scale = 0.0
        elif t == 1.0:
            intro_scale = 1.0
        else:
            c4 = (2 * math.pi) / 3
            intro_scale = math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1.0
            
        if not getattr(self, "is_exploding", False):
            beat_time = (self.heart_time * 1.2) % 1.0
            peak1 = math.exp(-math.pow((beat_time - 0.1) / 0.05, 2))
            peak2 = math.exp(-math.pow((beat_time - 0.3) / 0.05, 2))
            blend = min(1.0, max(0.0, self.heart_time - 1.0))
            
            pulse = 1.0 + (0.08 * peak1 + 0.04 * peak2) * blend
            final_scale = max(0, intro_scale * pulse)
                
            current_points = []
            for px, py in self.base_heart_points:
                px_new = self.cx + px * 22 * final_scale
                py_new = self.cy + py * 22 * final_scale
                current_points.extend([px_new, py_new])
            self.canvas.coords(self.heart_id, *current_points)
        
        for p in self.particles[:]:
            self.canvas.move(p["id"], p["vx"], p["vy"])
            p["vy"] += 0.1; p["size"] -= 0.08 
            if p["size"] <= 0:
                self.canvas.delete(p["id"])
                self.particles.remove(p)
            else:
                c = self.canvas.coords(p["id"])
                if c: self.canvas.coords(p["id"], c[0], c[1], c[0]+p["size"], c[1]+p["size"])
                
        for p in self.homing_particles:
            if p["phase"] == 0:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.8
                p["timer"] -= 1
                if p["timer"] <= 0:
                    p["phase"] = 1
            else:
                dx = p["target_x"] - p["x"]
                dy = p["target_y"] - p["y"]
                p["x"] += dx * 0.12 + random.uniform(-0.5, 0.5)
                p["y"] += dy * 0.12 + random.uniform(-0.5, 0.5)
            self.canvas.coords(p["id"], p["x"], p["y"], p["x"]+p["size"], p["y"]+p["size"])
            
        self.after(16, self.animate)

    def prepare_ui(self):
        self.parent.deiconify()
        self.attributes("-topmost", True)
        
        self._fade_progress = 0.0
        self.cross_fade()
        
    def cross_fade(self):
        self._fade_progress += 0.06
        if self._fade_progress >= 1.0:
            self._fade_progress = 1.0

        # Easing ease-out cubic: bắt đầu nhanh, kết thúc trôi nhẹ
        t = self._fade_progress
        eased = 1.0 - (1.0 - t) ** 3

        splash_alpha = 1.0 - eased
        main_alpha = eased

        try:
            self.attributes("-alpha", max(0.0, splash_alpha))
        except: pass
        self.parent.attributes("-alpha", min(1.0, main_alpha))

        if self._fade_progress >= 1.0:
            self.parent.attributes("-alpha", 1.0)
            self.withdraw()
            self.destroy()
        else:
            self.after(8, self.cross_fade)

# ================= HỆ THỐNG TỰ ĐỘNG CẬP NHẬT (AUTO-UPDATE) =================
def is_newer_version(latest_str, current_str):
    try:
        def parse_v(s):
            s = re.sub(r'^[^\d]*', '', str(s).strip())
            parts = re.split(r'[^\d]+', s)
            return [int(p) for p in parts if p.isdigit()]
        l_parts = parse_v(latest_str)
        c_parts = parse_v(current_str)
        if not l_parts or not c_parts:
            return False
        max_len = max(len(l_parts), len(c_parts))
        l_parts += [0] * (max_len - len(l_parts))
        c_parts += [0] * (max_len - len(c_parts))
        return l_parts > c_parts
    except Exception:
        return False

def get_direct_download_url(url):
    if not url: return ""
    url = url.strip()
    if "drive.google.com" in url:
        m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
        if not m:
            m = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
        if m:
            file_id = m.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    elif "dropbox.com" in url and "dl=0" in url:
        return url.replace("dl=0", "dl=1")
    return url

class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_version, update_info=None, on_check_again=None):
        super().__init__(parent)
        self.parent = parent
        self.current_version = current_version
        self.update_info = update_info or {}
        self.on_check_again = on_check_again
        self.downloading = False

        self.title("🔔 Trung Tâm Cập Nhật - Auto AdsPower")
        width, height = 560, 530
        target = get_target_monitor_rect(width, height)
        x = int(target["left"] + (target["width"] / 2) - (width / 2))
        y = int(target["top"] + (target["height"] / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(True, True)
        self.configure(fg_color="#F8F3F5")
        self.attributes("-topmost", True)

        try:
            self.iconbitmap(resource_path("chick.ico"))
        except: pass

        latest_ver = self.update_info.get("version") or self.update_info.get("latest_version") or self.current_version
        has_new = is_newer_version(latest_ver, self.current_version)
        self.has_new = has_new
        self.latest_ver = latest_ver

        # Nút bấm hành động (Neo chặt ở ĐÁY cửa sổ, luôn luôn hiển thị 100%)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="bottom", fill="x", padx=20, pady=(8, 15))

        if has_new:
            self.btn_action = ctk.CTkButton(
                self.btn_frame, text="🚀 TẢI & TỰ ĐỘNG CẬP NHẬT NGAY", height=40,
                font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
                fg_color="#27AE60", hover_color="#219653", text_color="#FFFFFF",
                command=self.start_download_update
            )
            self.btn_action.pack(side="left", expand=True, fill="x", padx=(0, 10))

            self.btn_cancel = ctk.CTkButton(
                self.btn_frame, text="Để sau", height=40, width=90,
                font=ctk.CTkFont(family="Arial", size=13),
                fg_color="#D5DBDB", hover_color="#BDC3C7", text_color="#333333",
                command=self.destroy
            )
            self.btn_cancel.pack(side="right")
        else:
            self.btn_action = ctk.CTkButton(
                self.btn_frame, text="🔄 Kiểm tra lại", height=40,
                font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
                fg_color="#B85C7B", hover_color="#9C4765", text_color="#FFFFFF",
                command=self.recheck_update
            )
            self.btn_action.pack(side="left", expand=True, fill="x", padx=(0, 10))

            self.btn_cancel = ctk.CTkButton(
                self.btn_frame, text="Đóng", height=40, width=90,
                font=ctk.CTkFont(family="Arial", size=13),
                fg_color="#D5DBDB", hover_color="#BDC3C7", text_color="#333333",
                command=self.destroy
            )
            self.btn_cancel.pack(side="right")

        # Khung Progress (Neo ngay trên nút bấm)
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 5))

        self.lbl_progress = ctk.CTkLabel(
            self.progress_frame, text="",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"), text_color="#555555"
        )
        self.lbl_progress.pack(anchor="w", pady=(0, 2))

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame, height=12, corner_radius=6,
            progress_color="#27AE60", fg_color="#E0E0E0"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")
        self.progress_bar.pack_forget()
        self.lbl_progress.pack_forget()

        # Header (Trên cùng)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(side="top", pady=(14, 6), fill="x", padx=20)

        ctk.CTkLabel(
            header_frame, text="🔔 TRUNG TÂM CẬP NHẬT PHẦN MỀM",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"), text_color="#B85C7B"
        ).pack()

        # Thẻ thông tin phiên bản
        info_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10, border_width=1, border_color="#E0C8D0")
        info_card.pack(side="top", fill="x", padx=20, pady=5)

        v_row = ctk.CTkFrame(info_card, fg_color="transparent")
        v_row.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            v_row, text=f"📌 Bản hiện tại: v{self.current_version}",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color="#555555"
        ).pack(side="left")

        if has_new:
            badge_text = "● ĐÃ CÓ BẢN MỚI"
            badge_color = "#E74C3C"
            status_text = f"🚀 Bản mới nhất trên Server: v{latest_ver}"
        else:
            badge_text = "● BẢN MỚI NHẤT"
            badge_color = "#27AE60"
            status_text = f"✅ Bạn đang dùng phiên bản mới nhất (v{latest_ver})"

        ctk.CTkLabel(
            v_row, text=badge_text,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"), text_color=badge_color
        ).pack(side="right")

        ctk.CTkLabel(
            info_card, text=status_text,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color="#B85C7B" if has_new else "#27AE60"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Khung Changelog (Giữa màn hình, tự động lấp đầy khoảng trống)
        ctk.CTkLabel(
            self, text="📝 Nội dung & tính năng mới:",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"), text_color="#4A4A4A"
        ).pack(side="top", anchor="w", padx=25, pady=(6, 2))

        changelog_text = self.update_info.get("changelog") or ""
        if not changelog_text:
            if has_new:
                changelog_text = "Bản cập nhật mới bổ sung các tính năng tự động và tối ưu hiệu suất."
            else:
                changelog_text = "Bạn đang sử dụng phiên bản phần mềm mới nhất!\nHệ thống luôn đảm bảo mọi tính năng hoạt động ổn định và mượt mà."

        self.txt_changelog = ctk.CTkTextbox(
            self, height=100, corner_radius=8, fg_color="#FFFFFF", text_color="#333333",
            border_width=1, border_color="#E0C8D0", font=ctk.CTkFont(family="Arial", size=12)
        )
        self.txt_changelog.pack(side="top", fill="both", expand=True, padx=20, pady=(2, 8))
        self.txt_changelog.insert("1.0", changelog_text)
        self.txt_changelog.configure(state="disabled")

    def recheck_update(self):
        self.btn_action.configure(state="disabled", text="⏳ Đang kiểm tra...")
        def _task():
            if self.on_check_again:
                upd = self.on_check_again()
                if upd:
                    self.update_info = upd
            self.after(500, self._refresh_ui)
        threading.Thread(target=_task, daemon=True).start()

    def _refresh_ui(self):
        self.destroy()
        if hasattr(self.parent, "open_update_dialog"):
            self.parent.open_update_dialog()

    def start_download_update(self):
        if self.downloading: return
        download_url = self.update_info.get("download_url") or self.update_info.get("url") or ""
        if not download_url:
            self.lbl_progress.pack(anchor="w", pady=(0, 2))
            self.lbl_progress.configure(text="❌ Chưa có link tải bản mới trên hệ thống!", text_color="#C0392B")
            return

        self.downloading = True
        self.btn_action.configure(state="disabled", text="⏳ Đang tải bản mới...")
        self.btn_cancel.configure(state="disabled")

        self.lbl_progress.pack(anchor="w", pady=(0, 2))
        self.progress_bar.pack(fill="x")
        self.lbl_progress.configure(text="Đang kết nối tới máy chủ...", text_color="#555555")
        self.progress_bar.set(0)

        threading.Thread(target=self._download_worker, args=(download_url,), daemon=True).start()

    def _download_worker(self, download_url):
        try:
            direct_url = get_direct_download_url(download_url)
            session = requests.Session()
            session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            
            res = session.get(direct_url, stream=True, timeout=30)
            for k, v in res.cookies.items():
                if k.startswith('download_warning'):
                    res = session.get(direct_url, params={'confirm': v}, stream=True, timeout=30)
                    break

            res.raise_for_status()
            total_bytes = int(res.headers.get("content-length", 0))

            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"tool_update_{int(time.time())}.exe")

            downloaded = 0
            start_t = time.time()
            with open(temp_file, "wb") as f:
                for chunk in res.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_bytes > 0:
                            pct = downloaded / total_bytes
                            speed_mb = (downloaded / (1024 * 1024)) / max(0.001, time.time() - start_t)
                            d_mb = downloaded / (1024 * 1024)
                            t_mb = total_bytes / (1024 * 1024)
                            self.after(0, lambda p=pct, d=d_mb, t=t_mb, s=speed_mb: self._update_progress(p, f"Đang tải: {int(p*100)}% ({d:.1f} MB / {t:.1f} MB) - {s:.1f} MB/s"))
                        else:
                            d_mb = downloaded / (1024 * 1024)
                            self.after(0, lambda d=d_mb: self._update_progress(0.5, f"Đang tải: {d:.1f} MB..."))

            is_hot_update = download_url.endswith(".py") or "tool_ads_ui.py" in download_url
            if is_hot_update:
                import shutil
                app_dir = get_real_app_dir()
                patch_path = os.path.join(app_dir, "app_update.py")
                try:
                    shutil.copy2(temp_file, patch_path)
                except Exception as e:
                    pass
                try:
                    shutil.copy2(temp_file, "app_update.py")
                except: pass
                try:
                    # Nếu file nguồn tool_ads_ui.py nằm ngay tại thư mục thì ghi đè luôn
                    src_f = os.path.join(app_dir, "tool_ads_ui.py")
                    if os.path.exists(src_f):
                        shutil.copy2(temp_file, src_f)
                except: pass

                # TỰ ĐỘNG THỰC HIỆN TẮT ADS VÀ KHỞI ĐỘNG LẠI NGAY (1-CLICK)!
                self.after(0, self._auto_apply_and_restart)
                return

            if os.path.getsize(temp_file) < 500000:
                with open(temp_file, "rb") as check_f:
                    head = check_f.read(200)
                    if b"<!DOCTYPE html" in head or b"<html" in head:
                        raise Exception("Link tải trả về trang HTML thay vì file exe! Vui lòng kiểm tra lại link.")

            # EXE UPDATE: TỰ ĐỘNG THỰC HIỆN TẮT ADS VÀ KHỞI ĐỘNG LẠI NGAY (1-CLICK)!
            self.after(0, lambda: self._execute_exe_updater(temp_file))

        except Exception as e:
            self.after(0, lambda err=str(e): self._download_failed(err))

    def _auto_apply_and_restart(self):
        """Tự động đóng AdsPower, thoát tool và khởi động lại với bản mới (1-Click, không cần bấm thêm nút)."""
        self.progress_bar.set(1.0)
        self.lbl_progress.configure(
            text="🎉 Đã tải và cài đặt xong! Đang tắt AdsPower & tự khởi động lại...",
            text_color="#27AE60"
        )
        self.btn_action.configure(
            text="⏳ Đang tự khởi động lại...",
            state="disabled",
            fg_color="#27AE60"
        )
        self.btn_cancel.configure(state="disabled")
        try:
            self.update_idletasks()
        except: pass

        def _do_restart():
            time.sleep(1.2)
            # 1. Tắt app AdsPower triệt để
            try:
                subprocess.call('taskkill /F /IM "AdsPower Global.exe" /IM "AdsPower Browser.exe" >nul 2>&1', shell=True)
            except: pass

            # 2. Lấy đường dẫn exe thật (KHÔNG lấy Temp python.exe của Nuitka)
            real_exe = get_real_exe_path()
            app_dir = get_real_app_dir()
            current_pid = os.getpid()

            restart_bat = os.path.join(tempfile.gettempdir(), f"restart_tool_{int(time.time())}.bat")
            
            if real_exe.lower().endswith(".exe"):
                launch_cmd = f'start "" "{real_exe}"'
            else:
                py_exe = sys.executable if not ("temp" in sys.executable.lower() or "onefil" in sys.executable.lower()) else "python"
                launch_cmd = f'start "" "{py_exe}" "tool_ads_ui.py"'

            bat_content = f"""@echo off
chcp 65001 >nul
:: Dong AdsPower
taskkill /F /IM "AdsPower Global.exe" /IM "AdsPower Browser.exe" >nul 2>&1
:: Doi tool cu thoat hoan toan
timeout /t 1 /nobreak >nul
taskkill /F /PID {current_pid} >nul 2>&1
:: Chuyen vao thu muc tool va khoi dong ban moi
cd /d "{app_dir}"
{launch_cmd}
timeout /t 2 /nobreak >nul
del "%~f0" >nul 2>&1
"""
            try:
                with open(restart_bat, "w", encoding="utf-8") as bf:
                    bf.write(bat_content)

                DETACHED_PROCESS = 0x00000008
                subprocess.Popen(
                    ["cmd.exe", "/c", restart_bat],
                    creationflags=DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    close_fds=True
                )
            except Exception:
                try:
                    subprocess.Popen([real_exe] if real_exe.lower().endswith(".exe") else [sys.executable, "tool_ads_ui.py"])
                except Exception:
                    pass

            time.sleep(0.3)
            os._exit(0)

        threading.Thread(target=_do_restart, daemon=True).start()

    def _update_progress(self, progress, text):
        try:
            self.progress_bar.set(progress)
            self.lbl_progress.configure(text=text, text_color="#555555")
        except: pass

    def _download_failed(self, err_msg):
        self.downloading = False
        self.btn_action.configure(state="normal", text="Thử lại")
        self.btn_cancel.configure(state="normal")
        self.lbl_progress.configure(text=f"❌ Lỗi tải bản mới: {err_msg[:60]}", text_color="#C0392B")

    def _execute_exe_updater(self, temp_file):
        """Tự động đóng AdsPower, thay thế file exe mới và bật lại (1-Click)."""
        self.progress_bar.set(1.0)
        self.lbl_progress.configure(
            text="🎉 Đã tải xong! Đang tắt AdsPower, thay thế bản mới & khởi động lại...",
            text_color="#27AE60"
        )
        self.btn_action.configure(state="disabled", text="⏳ Đang thay thế bản mới...")
        self.btn_cancel.configure(state="disabled")
        try:
            self.update_idletasks()
        except: pass

        def _do_exe_update():
            time.sleep(1.2)
            real_exe = get_real_exe_path()
            app_dir = get_real_app_dir()
            current_pid = os.getpid()

            # Tắt AdsPower trước
            try:
                subprocess.call('taskkill /F /IM "AdsPower Global.exe" /IM "AdsPower Browser.exe" >nul 2>&1', shell=True)
            except: pass

            updater_bat = os.path.join(tempfile.gettempdir(), f"updater_{int(time.time())}.bat")
            bat_content = f"""@echo off
chcp 65001 >nul
title Auto Updater - Dang cap nhat...
echo ========================================================
echo DANG CAP NHAT TOOL LEN PHIEN BAN MOI...
echo Vui long cho trong giay lat...
echo ========================================================
taskkill /F /IM "AdsPower Global.exe" /IM "AdsPower Browser.exe" >nul 2>&1
timeout /t 1 /nobreak >nul
taskkill /F /PID {current_pid} >nul 2>&1
timeout /t 1 /nobreak >nul

set "TARGET={real_exe}"
set "NEW={temp_file}"

:wait_loop
taskkill /f /im tool_ads_ui.exe >nul 2>&1
timeout /t 1 /nobreak >nul
del "%TARGET%" >nul 2>&1
if exist "%TARGET%" (
    goto wait_loop
)

move /y "%NEW%" "%TARGET%" >nul 2>&1
if not exist "%TARGET%" (
    copy /y "%NEW%" "%TARGET%" >nul 2>&1
)

cd /d "{app_dir}"
echo Khoi dong lai tool phien ban moi...
start "" "%TARGET%"
timeout /t 2 /nobreak >nul
del "%~f0" >nul 2>&1
"""
            try:
                with open(updater_bat, "w", encoding="utf-8") as bf:
                    bf.write(bat_content)

                DETACHED_PROCESS = 0x00000008
                subprocess.Popen(
                    ["cmd.exe", "/c", updater_bat],
                    creationflags=DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    close_fds=True
                )
                time.sleep(0.3)
                os._exit(0)
            except Exception as e:
                self.after(0, lambda err=str(e): self._download_failed(f"Lỗi khởi chạy updater: {err}"))

        threading.Thread(target=_do_exe_update, daemon=True).start()

# ================= GIAO DIỆN CHÍNH =================
class AutoAdsPowerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto AdsPower & FProxy - KINIUU")
        
        # Thêm khóa Lock để chống đè log 100%
        self.log_lock = threading.Lock()
        self.config_lock = threading.Lock()
        
        window_width = 1450
        window_height = 820
        target = get_target_monitor_rect(window_width, window_height)
        x = int(target["left"] + (target["width"] / 2) - (window_width / 2))
        y = int(target["top"] + (target["height"] / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#F2E6E8")

        try: self.root.iconbitmap(resource_path("chick.ico"))
        except: pass

        top_header_frame = ctk.CTkFrame(root, fg_color="transparent")
        top_header_frame.pack(pady=(10, 6), padx=(150, 25), fill="x")
        self.top_header_frame = top_header_frame
        

        title_lbl = ctk.CTkLabel(
            top_header_frame, text="🧸 AUTO TẠO PROFILE ADSPOWER (ĐA LUỒNG) 🧸",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"), text_color="#B85C7B"
        ) 
        title_lbl.pack(side="left", expand=True)

        self.btn_bell = ctk.CTkButton(
            top_header_frame, text="🔔 Cập nhật", width=125, height=36, corner_radius=18,
            fg_color="#FAFAFA", hover_color="#FADBD8", text_color="#B85C7B",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=13, weight="bold"),
            border_width=2, border_color="#E0C8D0",
            command=self.open_update_dialog
        )
        self.btn_bell.pack(side="right", padx=5)

        api_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="#FAFAFA", border_width=1, border_color="#E0C8D0")
        api_frame.pack(pady=5, padx=20, fill="x")
        api_frame.grid_columnconfigure(1, weight=1) 
        api_frame.grid_columnconfigure(3, weight=1) 

        ctk.CTkLabel(api_frame, text="🔗 Ads Local API:", font=ctk.CTkFont(weight="bold"), text_color="#4A4A4A").grid(row=0, column=0, padx=(15, 10), pady=(15, 5), sticky="e")
        self.ads_api_entry = ctk.CTkEntry(api_frame, fg_color="#FFFFFF", text_color="#333333", height=32)
        self.ads_api_entry.insert(0, "http://127.0.0.1:50325")
        self.ads_api_entry.grid(row=0, column=1, padx=(0, 20), pady=(15, 5), sticky="ew")

        ctk.CTkLabel(api_frame, text="🔐 Ads API Key:", font=ctk.CTkFont(weight="bold"), text_color="#4A4A4A").grid(row=0, column=2, padx=(10, 10), pady=(15, 5), sticky="e")
        self.ads_secret_entry = ctk.CTkEntry(api_frame, fg_color="#FFFFFF", text_color="#333333", height=32)
        self.ads_secret_entry.grid(row=0, column=3, padx=(0, 15), pady=(15, 5), sticky="ew")

        ctk.CTkLabel(api_frame, text="🚫 Tỉnh cần tránh:", font=ctk.CTkFont(weight="bold"), text_color="#4A4A4A").grid(row=1, column=0, padx=(15, 10), pady=(5, 15), sticky="e")
        self.blacklist_entry = ctk.CTkEntry(api_frame, fg_color="#FFFFFF", text_color="#333333", height=32) 
        self.blacklist_entry.insert(0, "Hanoi, Hà Nội, Hồ Chí Minh, Ho Chi Minh, Đà Nẵng, Huế, TT-Huế, Quảng Nam, Nghệ An, Hội An")
        self.blacklist_entry.grid(row=1, column=1, columnspan=3, padx=(0, 160), pady=(5, 15), sticky="ew")

        self.btn_tele_config = ctk.CTkButton(
            api_frame, text="🤖 Cấu hình Tele", width=130, height=32,
            fg_color="#8FCB8F", hover_color="#5AB583", text_color="#FFFFFF", font=ctk.CTkFont(weight="bold"), command=self.open_tele_config
        )
        self.btn_tele_config.grid(row=1, column=3, padx=(0, 15), pady=(5, 15), sticky="e")

        self.threads_data = [] 
        threads_frame = ctk.CTkFrame(root, corner_radius=10, fg_color="transparent")
        threads_frame.pack(pady=10, padx=20, fill="x")

        PREFIX_MODES = ["Tất cả", "14", "113", "14, 113", "27", "115", "116", "117", "27, 115, 116, 117"]

        for i in range(5):
            row_frame = ctk.CTkFrame(threads_frame, fg_color="#FAFAFA", corner_radius=8, border_width=2, border_color="#E0C8D0")
            row_frame.pack(pady=5, fill="x")

            ctk.CTkLabel(row_frame, text=f"🔑 Luồng {i+1}:", font=ctk.CTkFont(weight="bold"), text_color="#B85C7B").grid(row=0, column=0, padx=10, pady=10)
            
            key_entry = ctk.CTkEntry(row_frame, width=170, placeholder_text="Nhập FProxy Key...", fg_color="#FFFFFF", text_color="#333333")
            key_entry.grid(row=0, column=1, padx=(5, 5), pady=10)

            prefix_menu = ctk.CTkComboBox(row_frame, values=PREFIX_MODES, width=90, fg_color="#FFFFFF", border_color="#DBB6C4", button_color="#DBB6C4", button_hover_color="#CC9CAE", dropdown_fg_color="#FAFAFA", dropdown_hover_color="#E6CDD5", dropdown_text_color="#B85C7B", text_color="#333333", state="readonly", font=ctk.CTkFont(family="Arial", size=11, weight="bold"), dropdown_font=ctk.CTkFont(family="Arial", size=11, weight="bold"))
            prefix_menu.set("Tất cả")
            prefix_menu.grid(row=0, column=2, padx=5, pady=10)

            info_lbl = ctk.CTkLabel(row_frame, text="Proxy: Chờ...", width=160, anchor="w", text_color="#D28F5A", font=ctk.CTkFont(weight="bold"))
            info_lbl.grid(row=0, column=3, padx=(5, 5), pady=10)

            copy_btn = ctk.CTkButton(row_frame, text="📋 Copy", width=60, fg_color="#C79BC7", hover_color="#B68AB6", text_color="#FFFFFF", command=lambda idx=i: self.copy_ip(idx)) 
            copy_btn.grid(row=0, column=4, padx=5, pady=10)

            start_btn = ctk.CTkButton(row_frame, text="▶ Tạo profile ADS", width=120, fg_color="#228B22", hover_color="#006400", text_color="#FFFFFF", command=lambda idx=i: self.toggle_thread(idx, bypass_checks=False)) 
            start_btn.grid(row=0, column=5, padx=5, pady=10)

            one_profile_btn = ctk.CTkButton(row_frame, text="⚡ One Profile", width=100, fg_color="#8A2BE2", hover_color="#4B0082", text_color="#FFFFFF", command=lambda idx=i: self.toggle_thread(idx, bypass_checks=True)) 
            one_profile_btn.grid(row=0, column=6, padx=5, pady=10)

            toggle_browser_btn = ctk.CTkButton(row_frame, text="Đóng, mở profile", width=120, fg_color="#E6A868", hover_color="#D69858", text_color="#FFFFFF", command=lambda idx=i: self.toggle_browser(idx)) 
            toggle_browser_btn.grid(row=0, column=7, padx=5, pady=10)

            reg_btn = ctk.CTkButton(row_frame, text="🎮 Đăng ký Game", width=120, fg_color="#3498DB", hover_color="#2980B9", text_color="#FFFFFF", command=lambda idx=i: self.open_registration_window(idx)) 
            reg_btn.grid(row=0, column=8, padx=5, pady=10)

            del_btn = ctk.CTkButton(row_frame, text="🗑 Xóa", width=70, fg_color="#D96E66", hover_color="#C95E56", text_color="#FFFFFF", command=lambda idx=i: self.delete_profile(idx)) 
            del_btn.grid(row=0, column=9, padx=(5, 5), pady=10)

            countdown_lbl = ctk.CTkLabel(row_frame, text="", width=50, font=ctk.CTkFont(weight="bold"), text_color="#CD5C5C")
            countdown_lbl.grid(row=0, column=10, padx=(0, 10), pady=10)

            self.threads_data.append({
                "row_frame": row_frame, "entry": key_entry, "prefix_menu": prefix_menu,
                "lbl_info": info_lbl, "btn_start": start_btn, "btn_one_profile": one_profile_btn, 
                "btn_toggle_browser": toggle_browser_btn, "btn_reg": reg_btn, "btn_del": del_btn, 
                "countdown_lbl": countdown_lbl, "is_running": False, "profile_id": None, "current_ip": None, "is_browser_open": False 
            })

        log_font = ctk.CTkFont(family="Consolas", size=14, weight="bold")
        self.log_box = ctk.CTkTextbox(root, width=960, height=250, corner_radius=10, fg_color="transparent", text_color="#333333", border_width=2, border_color="#DDBBC8", font=log_font)
        self.log_box.pack(pady=5, padx=10)

        self.btn_toggle_app = ctk.CTkButton(root, text="Đóng App AdsPower", font=ctk.CTkFont(family="Arial", size=15, weight="bold"), fg_color="#F5B7B1", hover_color="#F1948A", text_color="#333333", corner_radius=20, height=38, width=220, command=self.toggle_main_adspower_app)
        self.btn_toggle_app.pack(pady=(0, 10))
        
        self.total_ips_checked = 0
        self.total_ips_used = 0 
        self.ip_counter_lock = threading.Lock()
        
        self.counter_frame = ctk.CTkFrame(self.root, fg_color="#FADBD8", corner_radius=15, border_width=2, border_color="#FFFFFF")
        self.counter_frame.place(x=1250, y=560) 
        
        self.counter_label = ctk.CTkLabel(self.counter_frame, text="Đã check: 0 IP\nĐã dùng: 0 IP", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), text_color="#B85C7B", justify="left")
        self.counter_label.pack(padx=15, pady=8)
        
        self.log_box.tag_config("time", foreground="#008080")
        self.log_box.tag_config("thread_1", foreground="#FF4500") 
        self.log_box.tag_config("thread_2", foreground="#1E90FF") 
        self.log_box.tag_config("thread_3", foreground="#32CD32") 
        self.log_box.tag_config("thread_4", foreground="#FF8C00") 
        self.log_box.tag_config("thread_5", foreground="#8A2BE2") 
        self.log_box.tag_config("thread_sys", foreground="#B85C7B")
        self.log_box.tag_config("ip", foreground="#B85C7B")
        self.log_box.tag_config("error", foreground="#B85C7B")
        self.log_box.tag_config("warning", foreground="#B85C7B")
        self.log_box.tag_config("success", foreground="#B85C7B")
        self.log_box.tag_config("highlight", foreground="#B85C7B")
        self.log_box.tag_config("info", foreground="#B85C7B")
        self.log_box.tag_config("separator", foreground="#B85C7B")
        
        self.tele_token = ""
        self.tele_chat_id = ""
        self.tele_msg_mapping = {}  
        self.last_update_id = 0
        self.tele_session = requests.Session()

        self.load_config()
        self.log_msg("HỆ THỐNG", "🌟 Đã kết nối với hệ thống Server API an toàn!")

        self.bg_images = []
        bg_config_file = resource_path("bg_coordinates.json")
        if not os.path.exists(bg_config_file):
            exe_dir = get_real_app_dir()
            cand = os.path.join(exe_dir, "bg_coordinates.json")
            if os.path.exists(cand):
                bg_config_file = cand
            elif os.path.exists("bg_coordinates.json"):
                bg_config_file = "bg_coordinates.json"

        if os.path.exists(bg_config_file):
            try:
                with open(bg_config_file, "r", encoding="utf-8") as f:
                    bg_data = json.load(f)
                for item in bg_data:
                    bg = DraggableBackground(self.root, item.get("file"), x=item.get("x"), y=item.get("y"), size=item.get("size"))
                    bg.angle = item.get("angle", 0)
                    bg.update_image()
                    bg.lock() 
                    if item.get("file") == "img2.png":
                        try:
                            bg.label.lift(top_header_frame)
                        except:
                            try: bg.label.lift()
                            except: pass
                    self.bg_images.append(bg)
                self.log_msg("HỆ THỐNG", "✨ Đã load thành công giao diện Custom từ file config!")
            except Exception as e:
                self._load_default_bgs()
        else:
            self._load_default_bgs()

        if not self.bg_images:
            self._load_default_bgs()
            
        threading.Thread(target=lambda: self.auto_start_adspower(is_auto=True), daemon=True).start()
        threading.Thread(target=self.poll_telegram_updates, daemon=True).start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._start_falling_hearts()

        # Khởi chạy kiểm tra cập nhật ngầm định kỳ (kể cả khi đang mở tool)
        self.update_info = None
        self._start_update_loop()

    def _start_update_loop(self):
        def _loop():
            # Chờ 1.5s sau khi mở app là kiểm tra ngay lập tức
            time.sleep(1.5)
            while getattr(self, "root", None) and self.root.winfo_exists():
                self.check_update_silent()
                # Kiểm tra định kỳ mỗi 15 giây để bắt ngay tức thì khi vừa có bản mới
                for _ in range(15):
                    if not (getattr(self, "root", None) and self.root.winfo_exists()):
                        return
                    time.sleep(1)
        threading.Thread(target=_loop, daemon=True).start()

    def check_update_silent(self):
        try:
            upd = self.fetch_update_live()
            if upd and isinstance(upd, dict):
                latest = upd.get("version") or upd.get("latest_version")
                if latest and is_newer_version(latest, CURRENT_VERSION):
                    self.update_info = upd
                    self.root.after(0, lambda l=latest: self._on_new_version_detected(l))
        except Exception:
            pass

    def _on_new_version_detected(self, latest_ver):
        # 1. Đổi nút chuông báo trên thanh công cụ sang màu đỏ
        self.show_update_badge(latest_ver)

        # 2. Phát âm thanh ting ting chuyển tiền đúng 1 lần cho bản mới này
        if getattr(self, "_last_sound_version", None) != latest_ver:
            self._last_sound_version = latest_ver
            play_money_ting_ting()
            
            # 3. Tự động hiển thị ngay cửa sổ thông báo cập nhật lên màn hình (nếu chưa mở)
            if not (hasattr(self, "_active_update_dialog") and self._active_update_dialog and self._active_update_dialog.winfo_exists()):
                self.open_update_dialog()

    def fetch_update_live(self):
        # 1. Kiểm tra trực tiếp từ GitHub Releases API (lấy release mới nhất vừa tạo ngay tức thì)
        try:
            if GITHUB_REPO:
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "AutoAdsPower-Updater",
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache"
                }
                gh_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases?per_page=1&_={int(time.time())}"
                gh_res = requests.get(gh_url, headers=headers, timeout=6)
                gh_data = None
                if gh_res.status_code == 200:
                    r_list = gh_res.json()
                    if isinstance(r_list, list) and len(r_list) > 0:
                        gh_data = r_list[0]
                elif gh_res.status_code != 403:
                    r2 = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest?_={int(time.time())}", headers=headers, timeout=6)
                    if r2.status_code == 200:
                        gh_data = r2.json()

                if gh_data:
                    tag = (gh_data.get("tag_name") or "").lstrip("v").strip()
                    changelog = (gh_data.get("body") or "").strip()
                    download_url = ""
                    for asset in gh_data.get("assets", []):
                        if asset.get("name", "").lower().endswith(".py"):
                            download_url = asset.get("browser_download_url")
                            break
                    if not download_url:
                        for asset in gh_data.get("assets", []):
                            if asset.get("name", "").lower().endswith(".exe"):
                                download_url = asset.get("browser_download_url")
                                break
                    if not download_url:
                        download_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/tool_ads_ui.py"

                    if tag:
                        upd = {
                            "version": tag,
                            "download_url": download_url,
                            "changelog": changelog
                        }
                        self.update_info = upd
                        return upd
        except Exception:
            pass

        # 2. Fallback nếu GitHub API bị rate-limit hoặc chưa index: đọc trực tiếp file nguồn trên GitHub Raw
        try:
            raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/tool_ads_ui.py?_={int(time.time())}"
            raw_res = requests.get(raw_url, timeout=6)
            if raw_res.status_code == 200:
                raw_text = raw_res.text
                m = re.search(r'CURRENT_VERSION\s*=\s*["\']([^"\']+)["\']', raw_text)
                if m:
                    ver = m.group(1).strip()
                    if is_newer_version(ver, CURRENT_VERSION):
                        upd = {
                            "version": ver,
                            "download_url": raw_url,
                            "changelog": f"Bản cập nhật nóng v{ver}"
                        }
                        self.update_info = upd
                        return upd
        except Exception:
            pass

        # 3. Fallback sang Google Apps Script API
        try:
            app_cfg = getattr(self.root, "app_config", {})
            if "update" in app_cfg and isinstance(app_cfg["update"], dict):
                upd = app_cfg["update"]
                self.update_info = upd
                return upd

            res = requests.get(f"{API_URL}?action=check_update", timeout=6)
            data = res.json()
            if data.get("success"):
                upd = data.get("update") or data
                self.update_info = upd
                return upd
        except Exception:
            pass
        return None

    def show_update_badge(self, latest_ver):
        try:
            self.btn_bell.configure(
                text=f"🔔 Có bản mới: v{latest_ver}!",
                fg_color="#E74C3C",
                hover_color="#C0392B",
                text_color="#FFFFFF",
                border_color="#922B21"
            )
        except Exception:
            pass

    def open_update_dialog(self):
        if hasattr(self, "_active_update_dialog") and self._active_update_dialog and self._active_update_dialog.winfo_exists():
            try:
                self._active_update_dialog.lift()
                self._active_update_dialog.focus_force()
                return
            except: pass
        self._active_update_dialog = UpdateDialog(self.root, CURRENT_VERSION, self.update_info, on_check_again=self.fetch_update_live)

    def _start_falling_hearts(self):
        """Hiệu ứng trái tim nhỏ rơi như tuyết phía sau ảnh nền."""
        import tkinter as tk
        W, H = 1450, 820
        self._heart_canvas = tk.Canvas(
            self.root, width=W, height=H,
            bg="#F2E6E8", highlightthickness=0
        )
        self._heart_canvas.place(x=0, y=0, width=W, height=H)
        self._heart_canvas.tk.call('lower', self._heart_canvas._w)

        # Đảm bảo tất cả các ảnh gấu luôn nằm trên canvas trái tim rơi (không bao giờ bị che)
        for bg in getattr(self, "bg_images", []):
            if hasattr(bg, "label") and bg.label:
                try: bg.label.lift(self._heart_canvas)
                except: pass
        # Riêng gấu img2 (thò đầu trên tiêu đề) luôn được nâng lên lớp cao nhất
        for bg in getattr(self, "bg_images", []):
            if getattr(bg, "image_path", "") == "img2.png" and hasattr(bg, "label") and bg.label:
                try: bg.label.lift()
                except: pass

        self._falling_hearts = []
        heart_colors = ["#F4B8C8", "#E88FAC", "#F9D0DA", "#D4799A", "#FADADD", "#C75B8A"]

        def make_heart_polygon(cx, cy, size):
            pts = []
            for i in range(0, 360, 8):
                t = math.radians(i)
                px = 16 * math.sin(t)**3
                py = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
                pts.extend([cx + px * size, cy + py * size])
            return pts

        def spawn_heart():
            x = random.randint(20, W - 20)
            size = random.uniform(0.5, 1.4)
            color = random.choice(heart_colors)
            pts = make_heart_polygon(x, -20, size)
            hid = self._heart_canvas.create_polygon(pts, fill=color, outline="", smooth=True)
            self._falling_hearts.append({
                "id": hid, "x": float(x), "y": -20.0,
                "size": size, "speed": random.uniform(0.6, 1.8),
                "drift": random.uniform(-0.3, 0.3),
                "sway": random.uniform(0, 2 * math.pi),
                "sway_speed": random.uniform(0.02, 0.06)
            })

        def animate_hearts():
            if not self.root.winfo_exists(): return
            for h in self._falling_hearts[:]:
                h["y"] += h["speed"]
                h["sway"] += h["sway_speed"]
                h["x"] += h["drift"] + math.sin(h["sway"]) * 0.4
                pts = make_heart_polygon(h["x"], h["y"], h["size"])
                self._heart_canvas.coords(h["id"], *pts)
                if h["y"] > H + 30:
                    self._heart_canvas.delete(h["id"])
                    self._falling_hearts.remove(h)
            if random.random() < 0.08:
                spawn_heart()
            self.root.after(30, animate_hearts)

        for _ in range(25):
            spawn_heart()
            h = self._falling_hearts[-1]
            h["y"] = float(random.randint(0, H))
            pts = make_heart_polygon(h["x"], h["y"], h["size"])
            self._heart_canvas.coords(h["id"], *pts)

        animate_hearts()

    # ================= BẢNG QUẢN LÝ GAME (MODERN GLASS / NO-CRASH EDITION) =================
    def open_registration_window(self, index):
        thread_info = self.threads_data[index]
        profile_id = thread_info["profile_id"]

        if not profile_id:
            self.log_msg(f"Luồng {index+1}", "⚠️ Phải tạo xong Profile thì mới mở bảng đăng ký được sếp nhé!")
            return

        # ── SINGLETON: Nếu cửa sổ đã tồn tại → chỉ hiện lại, không tạo mới ──
        existing_win = thread_info.get("reg_win")
        if existing_win is not None:
            try:
                if existing_win.winfo_exists():
                    existing_win.deiconify()
                    existing_win.lift()
                    existing_win.focus_force()
                    existing_win.attributes("-topmost", True)
                    # Fade in mượt khi hiện lại
                    existing_win.attributes("-alpha", 0.0)
                    def _fade_show(alpha=0.0, win=existing_win):
                        alpha = min(1.0, alpha + 0.10)
                        try: win.attributes("-alpha", alpha)
                        except: return
                        if alpha < 1.0:
                            win.after(12, lambda: _fade_show(alpha, win))
                    _fade_show()
                    return
            except Exception:
                pass  # Cửa sổ cũ đã bị destroy thật sự → tạo mới bên dưới

        if "reg_vars" not in thread_info:
            thread_info["reg_vars"] = {
                "Tên": ctk.StringVar(value=""),
                "SĐT": ctk.StringVar(value="Random"),
                "STK": ctk.StringVar(value=""),
                "TK": ctk.StringVar(value=""),
                "MK": ctk.StringVar(value=""),
                "Mã PIN": ctk.StringVar(value="")
            }
        else:
            reg_vars = thread_info["reg_vars"]
            aliases = {"T?n": "Tên", "S?T": "SĐT", "M? PIN": "Mã PIN", "Ten": "Tên", "SDT": "SĐT", "Ma PIN": "Mã PIN"}
            for old_key, new_key in aliases.items():
                if old_key in reg_vars and new_key not in reg_vars:
                    reg_vars[new_key] = reg_vars.pop(old_key)
            for key in ["Tên", "SĐT", "STK", "TK", "MK", "Mã PIN"]:
                if key not in reg_vars:
                    default_value = "Random" if key == "SĐT" else ""
                    reg_vars[key] = ctk.StringVar(value=default_value)
        if "game_states" not in thread_info:
            thread_info["game_states"] = {}
        if "game_notes" not in thread_info:
            thread_info["game_notes"] = {}
        if "ui_settings" not in thread_info:
            thread_info["ui_settings"] = {
                "auto_open": True,
                "delay_seconds": 0.5,
                "run_mode": "Smooth",
                "theme": "Pink Luxury",
            }

        reg_win = ctk.CTkToplevel(self.root)
        thread_info["reg_win"] = reg_win  # Lưu lại để dùng singleton lần sau
        reg_win.title(f"Quản trị Hệ thống - Luồng {index+1} | ID: {profile_id}")
        
        try:
            icon_p = resource_path("chick.ico")
            reg_win.iconbitmap(icon_p)
            reg_win.after(200, lambda: reg_win.iconbitmap(icon_p))
        except: pass
        
        window_width = 1320
        window_height = 700
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        # Căn giữa cửa sổ đăng ký game theo vị trí thực tế hiện tại của giao diện chính
        x = int(main_x + (main_width / 2) - (window_width / 2))
        y = int(main_y + (main_height / 2) - (window_height / 2))
        reg_win.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        reg_win.configure(fg_color="#F5EEF3")
        reg_win.attributes("-topmost", True)
        reg_win.attributes("-alpha", 0.0)

        def fade_in(alpha=0.0):
            alpha = min(1.0, alpha + 0.08)
            try: reg_win.attributes("-alpha", alpha)
            except: return
            if alpha < 1.0:
                reg_win.after(15, lambda: fade_in(alpha))

        def fade_out_and_hide(alpha=1.0):
            """Ẩn cửa sổ (withdraw) thay vì destroy → mở lại cực nhanh."""
            alpha = max(0.0, alpha - 0.10)
            try: reg_win.attributes("-alpha", alpha)
            except: return
            if alpha > 0.0:
                reg_win.after(15, lambda: fade_out_and_hide(alpha))
            else:
                try: reg_win.withdraw()
                except: pass

        reg_win.protocol("WM_DELETE_WINDOW", fade_out_and_hide)
        fade_in()


        try:
            # Fonts
            font_title = ctk.CTkFont(weight="bold", size=14)
            font_text = ctk.CTkFont(weight="bold", size=12)
            font_url = ctk.CTkFont(size=12)
            font_big = ctk.CTkFont(weight="bold", size=16)

            # Root layout
            outer = ctk.CTkFrame(reg_win, fg_color="#F5EEF3", corner_radius=0)
            outer.pack(fill="both", expand=True)

            hero = ctk.CTkFrame(outer, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7CBD7")
            hero.pack(fill="x", padx=18, pady=(8, 4))
            hero.pack_propagate(False)
            hero.configure(height=42)

            top = ctk.CTkFrame(hero, fg_color="transparent")
            top.pack(fill="both", expand=True, padx=14, pady=0)
            ctk.CTkLabel(top, text="BẢNG QUẢN LÝ GAME", font=font_title, text_color="#B84F78").pack(side="left")
            ctk.CTkLabel(top, text=f"Profile ID: {profile_id}", font=font_text, text_color="#C58A5A").pack(side="right")

            panel = ctk.CTkFrame(outer, fg_color="#FFFFFF", corner_radius=18, border_width=1, border_color="#E7CBD7")
            panel.pack(fill="both", expand=True, padx=18, pady=(0, 10))

            tab_view = ctk.CTkTabview(panel, fg_color="transparent", segmented_button_selected_color="#B84F78", text_color="#FFFFFF")
            tab_view.pack(fill="both", expand=True, padx=12, pady=(6, 10))
            tab_main = tab_view.add("Điều Khiển")
            tab_setting = tab_view.add("Cấu Hình")

            # Profile form
            data_card = ctk.CTkFrame(tab_main, fg_color="#FFFDFE", corner_radius=16, border_width=1, border_color="#ECD9E2")
            data_card.pack(fill="x", padx=6, pady=(2, 4))

            title_frame = ctk.CTkFrame(data_card, fg_color="transparent")
            title_frame.pack(fill="x", padx=18, pady=(6, 2))
            ctk.CTkLabel(title_frame, text="THÔNG TIN KHÁCH HÀNG / TÀI KHOẢN", font=font_title, text_color="#B84F78").pack(side="left")
            
            game_ui_elements = []
            ctk.CTkButton(
                title_frame,
                text="▶ MỞ TẤT CẢ CÁC GAME",
                width=180,
                height=32,
                corner_radius=16,
                fg_color="#EE7AA4",
                hover_color="#D95B8A",
                text_color="#FFFFFF",
                font=font_text,
                command=lambda: self.open_all_games(index, game_ui_elements),
            ).pack(side="right")

            form_frame = ctk.CTkFrame(data_card, fg_color="transparent")
            form_frame.pack(fill="x", padx=18, pady=(2, 4))

            columns = ["Tên", "SĐT", "STK", "TK", "MK", "Mã PIN"]
            placeholders = {"Tên": "VD: NGUYEN VAN A", "SĐT": "Random", "STK": "Số Tài Khoản", "TK": "Tên đăng nhập", "MK": "Mật khẩu", "Mã PIN": "PIN (6 số)"}

            entry_widgets = {}
            is_locked = ctk.BooleanVar(value=False)

            def make_copier(w, var):
                # Lưu màu gốc ngay lúc khởi tạo (không được lấy lúc click vì có thể đang hồng)
                _orig_color = w.cget("fg_color")
                _flash_timer_id = [None]  # dùng list để có thể mutate trong closure

                def copy_and_flash(event):
                    if is_locked.get():
                        val = var.get()
                        reg_win.clipboard_clear()
                        reg_win.clipboard_append(val)
                        w.configure(fg_color="#FFD1DC")
                        # Hủy timer cũ nếu đang chạy, rồi đặt timer mới 4 giây
                        if _flash_timer_id[0] is not None:
                            try: reg_win.after_cancel(_flash_timer_id[0])
                            except: pass
                        def _revert():
                            _flash_timer_id[0] = None
                            w.configure(fg_color=_orig_color)
                        _flash_timer_id[0] = reg_win.after(4000, _revert)
                if hasattr(w, "_entry"):
                    w._entry.bind("<Button-1>", copy_and_flash, add="+")
                if hasattr(w, "_canvas"):
                    w._canvas.bind("<Button-1>", copy_and_flash, add="+")
                w.bind("<Button-1>", copy_and_flash, add="+")

            for c, name in enumerate(columns):
                col = ctk.CTkFrame(form_frame, fg_color="transparent")
                col.grid(row=0, column=c, padx=8, sticky="n")
                ctk.CTkLabel(col, text=name.upper(), font=font_text, text_color="#B84F78").pack(anchor="w", pady=(0, 5))
                entry_width = 180 if name == "Tên" else (135 if name == "SĐT" else (90 if name == "Mã PIN" else 145))
                if name == "SĐT":
                    def on_sdt_select(choice, var=thread_info["reg_vars"][name]):
                        if choice == "Tự điền":
                            var.set("")
                    w = ctk.CTkComboBox(
                        col,
                        values=["Random", "Tự điền"],
                        width=entry_width,
                        height=36,
                        fg_color="#FFFFFF",
                        text_color="#2E2E2E",
                        border_color="#E3C1D0",
                        button_color="#DAB3C2",
                        button_hover_color="#C78DA4",
                        dropdown_fg_color="#FFFFFF",
                        dropdown_hover_color="#F5EEF3",
                        dropdown_text_color="#2E2E2E",
                        variable=thread_info["reg_vars"][name],
                        font=font_text,
                        dropdown_font=font_text,
                        command=on_sdt_select
                    )
                    w.pack(anchor="w")
                    entry_widgets[name] = w
                    make_copier(w, thread_info["reg_vars"][name])
                else:
                    w = ctk.CTkEntry(
                        col,
                        width=entry_width,
                        height=36,
                        fg_color="#FFFFFF",
                        text_color="#2E2E2E",
                        border_color="#E3C1D0",
                        placeholder_text=placeholders[name],
                        placeholder_text_color="#A98D97",
                        textvariable=thread_info["reg_vars"][name],
                        font=font_text,
                    )
                    w.pack(anchor="w")
                    entry_widgets[name] = w
                    make_copier(w, thread_info["reg_vars"][name])

            bank_col = ctk.CTkFrame(form_frame, fg_color="transparent")
            bank_col.grid(row=0, column=7, padx=8, sticky="n")
            ctk.CTkLabel(bank_col, text="NGÂN HÀNG", font=font_text, text_color="#B84F78").pack(anchor="w", pady=(0, 5))
            
            bank_inner = ctk.CTkFrame(bank_col, fg_color="transparent")
            bank_inner.pack(anchor="w")
            
            self.bank_var = ctk.StringVar(value="VIKKI BANK")
            w_bank = ctk.CTkOptionMenu(
                bank_inner,
                values=["VIKKI BANK", "TPBANK"],
                variable=self.bank_var,
                width=110,
                height=36,
                fg_color="#FFFFFF",
                button_color="#DAB3C2",
                button_hover_color="#C78DA4",
                text_color="#2E2E2E",
                font=font_text,
            )
            w_bank.pack(side="left")
            entry_widgets["Ngân Hàng"] = w_bank
            make_copier(w_bank, self.bank_var)
            
            def toggle_lock():
                locked = not is_locked.get()
                is_locked.set(locked)
                
                if locked:
                    btn_lock.configure(fg_color="#F39C12", hover_color="#D68910")
                else:
                    btn_lock.configure(fg_color="#E0E0E0", hover_color="#C0C0C0")
                    
                for n, w in entry_widgets.items():
                    if n == "SĐT" or n == "Ngân Hàng":
                        w.configure(state="disabled" if locked else "normal")
                    else:
                        w.configure(state="readonly" if locked else "normal")
                        
            btn_lock = ctk.CTkButton(
                bank_inner,
                text="🔒",
                width=36,
                height=36,
                fg_color="#E0E0E0",
                hover_color="#C0C0C0",
                text_color="#000000",
                font=ctk.CTkFont(size=16),
                command=toggle_lock
            )
            btn_lock.pack(side="left", padx=(4, 0))

            # Game list card
            table_card = ctk.CTkFrame(tab_main, fg_color="#FFFDFE", corner_radius=16, border_width=1, border_color="#ECD9E2")
            table_card.pack(fill="both", expand=True, padx=6, pady=(0, 6))

            header_wrap = ctk.CTkFrame(table_card, fg_color="transparent")
            header_wrap.pack(fill="x", padx=10, pady=(8, 0))

            header_frame = ctk.CTkFrame(header_wrap, fg_color="#B84F78", corner_radius=12, height=40)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            ctk.CTkLabel(header_frame, text="TÊN GAME", font=font_title, text_color="#FFFFFF", width=120, anchor="w").pack(side="left", padx=(18, 10))
            ctk.CTkLabel(header_frame, text="ĐỊA CHỈ LIÊN KẾT (URL)", font=font_title, text_color="#FFFFFF", width=320, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(header_frame, text="TRẠNG THÁI", font=font_title, text_color="#FFFFFF", width=100, anchor="center").pack(side="left", padx=10)
            ctk.CTkLabel(header_frame, text="ĐIỀU KHIỂN NHANH", font=font_title, text_color="#FFFFFF").pack(side="left", padx=(40, 10))

            table_container = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
            table_container.pack(padx=10, pady=10, fill="both", expand=True)

            default_games_list = [
                {"name": "mb66", "url": "https://m.tgreg51ad5a6wed.com/"},
                {"name": "78win", "url": "https://www.78winnf.love/"},
                {"name": "Open88", "url": "https://www.open88a2.com/m/register"},
                {"name": "789BET", "url": "https://m.78985.co/Account/Register?f=4840129&v=639093277678601407"},
                {"name": "Hi88", "url": "https://hi5599.com/?r=EDLGD6"},
                {"name": "u888", "url": "https://m.u888ejp.xyz/"},
                {"name": "new88", "url": "https://m.new8839.cc/Account/Register"},
                {"name": "shbet", "url": "https://m.shbetv8.top/Account/Register?f=7535048&v=639078753405738397"},
                {"name": "JUN88", "url": "https://sasa2.xn--8866-um1g.com/signup"},
                {"name": "QQ88", "url": "https://nziub.qq8893.com/m/register"},
                {"name": "rr88", "url": "https://rr88seo.rr8391.com/m/register"},
                {"name": "xx88", "url": "https://xx88seo.xx0188.com/m/register"},
                {"name": "gg88", "url": "https://www.gg8862.com/home/register"},
                {"name": "mm88", "url": "https://www.mm88p.com/m/register"},
                {"name": "88vv", "url": "https://m.88vv.my/"}
            ]
            if not os.path.exists("game_urls.json"):
                try:
                    with open("game_urls.json", "w", encoding="utf-8") as f:
                        json.dump(default_games_list, f, indent=4)
                except:
                    pass
            try:
                with open("game_urls.json", "r", encoding="utf-8") as f:
                    games_list = json.load(f)
            except:
                games_list = default_games_list

            thread_info["row_refs"] = []
            for r, game in enumerate(games_list):
                bg_color = "#FFFFFF" if r % 2 == 0 else "#FFF6FA"
                row_frame = ctk.CTkFrame(table_container, fg_color=bg_color, corner_radius=12, border_width=1, border_color="#E8D3DE")
                row_frame.pack(fill="x", pady=4, padx=2, ipady=4)
                row_frame._original_bg = bg_color

                accent = ctk.CTkFrame(row_frame, fg_color="#F3C4D2", corner_radius=999, width=8, height=44)
                accent.pack(side="left", padx=(10, 12), pady=4)
                accent.pack_propagate(False)

                font_game_name = ctk.CTkFont(weight="bold", size=15)
                game_name_lbl = ctk.CTkLabel(row_frame, text=game["name"].upper(), text_color="#1E8449", font=font_game_name, width=92, anchor="w")
                game_name_lbl.pack(side="left", padx=(0, 8))

                link_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                link_frame.pack(side="left", padx=10)
                link_entry = ctk.CTkEntry(link_frame, width=280, fg_color="#FBFBFB", text_color="#2E2E2E", border_width=1, border_color="#F0DCE5", font=font_url)
                link_entry.insert(0, game["url"])
                link_entry.pack(side="left")
                
                ctk.CTkButton(link_frame, text="💾", width=30, height=28, fg_color="#F39C12", hover_color="#D68910", font=ctk.CTkFont(size=14),
                              command=lambda g=game["name"], ent=link_entry: self.save_new_url(g, ent)).pack(side="left", padx=(4, 0))

                saved_status = thread_info["game_states"].get(game["name"], "Chưa mở")
                is_open = "Mở" in saved_status and "Chưa" not in saved_status
                is_close = "Đóng" in saved_status
                status_color = "#21A366" if is_open else ("#D64545" if is_close else "#8B8B8B")
                bg_badge = "#E8F8F1" if is_open else ("#FDECEC" if is_close else "#F1F3F5")

                badge_frame = ctk.CTkFrame(row_frame, fg_color=bg_badge, corner_radius=6, width=95, height=26)
                badge_frame.pack_propagate(False)
                badge_frame.pack(side="left", padx=10)
                
                font_status_mini = ctk.CTkFont(weight="bold", size=12)
                hien_thi_status = saved_status
                
                status_lbl = ctk.CTkLabel(badge_frame, text=hien_thi_status, text_color=status_color, font=font_status_mini)
                status_lbl.pack(expand=True)

                game_ui_elements.append({"game": game, "status_lbl": status_lbl, "badge_frame": badge_frame})
                thread_info["row_refs"].append({"frame": row_frame, "entry": link_entry, "name_lbl": game_name_lbl})

                action_btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                action_btn_frame.pack(side="left", padx=10) 

                inline_log_lbl = ctk.CTkLabel(row_frame, text="Đang đợi lệnh chạy...", text_color="#9C6A82", font=ctk.CTkFont(size=12, slant="italic"), anchor="w", justify="left")

                ctk.CTkButton(action_btn_frame, text="▶ Mở", width=60, height=28, corner_radius=14,
                              fg_color="#3498DB", hover_color="#2980B9", text_color="#FFFFFF", font=font_text,
                              command=lambda u=game["url"], n=game["name"], lbl=status_lbl, badge=badge_frame, inl=inline_log_lbl: self.manage_ads_tab(index, u, n, "open", lbl, badge, inl)).pack(side="left", padx=4)
                
                ctk.CTkButton(action_btn_frame, text="⏹ Đóng", width=65, height=28, corner_radius=14,
                              fg_color="#E74C3C", hover_color="#C0392B", text_color="#FFFFFF", font=font_text,
                              command=lambda u=game["url"], n=game["name"], lbl=status_lbl, badge=badge_frame, inl=inline_log_lbl: self.manage_ads_tab(index, u, n, "close", lbl, badge, inl)).pack(side="left", padx=4)
                
                ctk.CTkButton(action_btn_frame, text="⚡ Auto", width=65, height=28, corner_radius=14,
                              fg_color="#9B59B6", hover_color="#8E44AD", text_color="#FFFFFF", font=font_text,
                              command=lambda g=game["name"], lbl=status_lbl, badge=badge_frame, inl=inline_log_lbl: self.trigger_auto_fill(index, g, self.get_current_data(index), lbl, badge, inl)).pack(side="left", padx=(4, 4))
                              
                ctk.CTkButton(action_btn_frame, text="🛑 Stop", width=65, height=28, corner_radius=14,
                              fg_color="#F1C40F", hover_color="#F39C12", text_color="#FFFFFF", font=font_text,
                              command=lambda idx=index, g=game["name"]: self.stop_auto_thread(idx, g)).pack(side="left", padx=(0, 4))

                if game["name"] not in thread_info["game_notes"]:
                    thread_info["game_notes"][game["name"]] = ctk.StringVar(value="")
                
                # Lưu trạng thái màu chữ của note (False = đen bình thường, True = đỏ đậm)
                if "game_note_red" not in thread_info:
                    thread_info["game_note_red"] = {}
                if game["name"] not in thread_info["game_note_red"]:
                    thread_info["game_note_red"][game["name"]] = False

                note_font_normal = ctk.CTkFont(size=12)
                note_font_bold_red = ctk.CTkFont(size=12, weight="bold")

                note_entry = ctk.CTkEntry(
                    action_btn_frame, width=70, height=28,
                    fg_color="#FFFFFF",
                    text_color="#2E2E2E",
                    border_width=1, border_color="#E8D3DE",
                    placeholder_text="Ghi chú...",
                    textvariable=thread_info["game_notes"][game["name"]],
                    font=note_font_normal
                )
                note_entry.pack(side="left", padx=(4, 0))

                # Khôi phục trạng thái màu nếu đang là đỏ
                _init_red = thread_info["game_note_red"].get(game["name"], False)
                if _init_red:
                    note_entry.configure(text_color="#CC0000", font=note_font_bold_red)

                # Nút toggle màu: trái tim đỏ = đánh dấu / trái tim xám = bình thường
                note_color_btn = ctk.CTkButton(
                    action_btn_frame,
                    text="♥",
                    width=22, height=22,
                    corner_radius=11,
                    fg_color="#CC0000" if _init_red else "#BBBBBB",
                    hover_color="#AA0000" if _init_red else "#999999",
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(size=12),
                    border_width=0,
                )
                note_color_btn.pack(side="left", padx=(2, 4))

                def _make_note_toggle(ne=note_entry, btn=note_color_btn, gname=game["name"],
                                      tinfo=thread_info, fnorm=note_font_normal, fbold=note_font_bold_red,
                                      idx=index):
                    def _toggle():
                        is_red = tinfo["game_note_red"].get(gname, False)
                        if is_red:
                            ne.configure(text_color="#2E2E2E", font=fnorm)
                            btn.configure(fg_color="#BBBBBB", hover_color="#999999")
                            tinfo["game_note_red"][gname] = False
                            new_red = False
                        else:
                            ne.configure(text_color="#CC0000", font=fbold)
                            btn.configure(fg_color="#CC0000", hover_color="#AA0000")
                            tinfo["game_note_red"][gname] = True
                            new_red = True
                        # Sync lên Sheet ngay khi đổi màu
                        note_val = tinfo["game_notes"].get(gname, ctk.StringVar()).get().strip()
                        self.sync_note_to_sheet(idx, gname, note_val, new_red)
                    return _toggle

                note_color_btn.configure(command=_make_note_toggle())

                # Sync khi người dùng gõ xong và click ra ngoài (FocusOut)
                def _on_note_focus_out(event, gname=game["name"], tinfo=thread_info, idx=index):
                    note_val = tinfo["game_notes"].get(gname, ctk.StringVar()).get().strip()
                    is_red = tinfo["game_note_red"].get(gname, False)
                    if note_val:  # Chỉ sync khi có nội dung
                        self.sync_note_to_sheet(idx, gname, note_val, is_red)

                note_entry.bind("<FocusOut>", _on_note_focus_out, add="+")
                if hasattr(note_entry, "_entry"):
                    note_entry._entry.bind("<FocusOut>", _on_note_focus_out, add="+")

                inline_log_lbl.pack(side="left", padx=(10, 10), fill="x", expand=True)

                def on_enter(e, widget=row_frame):
                    widget.configure(fg_color="#FFEAF2", border_color="#F09CBC")
                def on_leave(e, widget=row_frame):
                    widget.configure(fg_color=widget._original_bg, border_color="#E8D3DE")

                row_frame.bind("<Enter>", on_enter)
                row_frame.bind("<Leave>", on_leave)
                game_name_lbl.bind("<Enter>", on_enter)
                game_name_lbl.bind("<Leave>", on_leave)
                action_btn_frame.bind("<Enter>", on_enter)
                action_btn_frame.bind("<Leave>", on_leave)

            thread_info["game_ui_elements"] = game_ui_elements
            settings_shell = ctk.CTkFrame(tab_setting, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#ECD9E2")
            settings_shell.pack(fill="both", expand=True, padx=6, pady=6)

            settings_header = ctk.CTkFrame(settings_shell, fg_color="#B84F78", corner_radius=14, height=52)
            settings_header.pack(fill="x", padx=12, pady=(12, 10))
            settings_header.pack_propagate(False)
            ctk.CTkLabel(settings_header, text="CẤU HÌNH LUỒNG NÂNG CAO", font=font_title, text_color="#FFFFFF").pack(side="left", padx=16)
            ctk.CTkLabel(settings_header, text="Preset riêng cho từng luồng, tối ưu thao tác đêm", font=font_text, text_color="#FFFFFF").pack(side="right", padx=16)

            settings_grid = ctk.CTkFrame(settings_shell, fg_color="transparent")
            settings_grid.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            settings_grid.grid_columnconfigure(0, weight=1)
            settings_grid.grid_columnconfigure(1, weight=1)

            card1 = ctk.CTkFrame(settings_grid, fg_color="#FAF7F9", corner_radius=14, border_width=1, border_color="#ECD9E2")
            card1.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="nsew")
            card2 = ctk.CTkFrame(settings_grid, fg_color="#FAF7F9", corner_radius=14, border_width=1, border_color="#ECD9E2")
            card2.grid(row=0, column=1, padx=(8, 0), pady=8, sticky="nsew")
            card3 = ctk.CTkFrame(settings_grid, fg_color="#FAF7F9", corner_radius=14, border_width=1, border_color="#ECD9E2")
            card3.grid(row=1, column=1, padx=(8, 0), pady=8, sticky="nsew")

            auto_open_switch = ctk.CTkSwitch(card1, text="Bật tự mở game", font=font_big, progress_color="#EE7AA4", button_color="#B84F78", button_hover_color="#D95B8A")
            auto_open_switch.pack(anchor="w", padx=16, pady=(10, 4))
            auto_open_switch.select() if thread_info["ui_settings"]["auto_open"] else auto_open_switch.deselect()
            ctk.CTkLabel(card1, text="Tự mở toàn bộ game sau khi vào luồng", font=font_big, text_color="#8A7B84").pack(anchor="w", padx=16, pady=(0, 10))

            ctk.CTkLabel(card2, text="Delay hành động", font=font_big, text_color="#B84F78").pack(anchor="w", padx=16, pady=(12, 4))
            delay_var = ctk.StringVar(value=str(thread_info["ui_settings"]["delay_seconds"]))
            ctk.CTkEntry(card2, textvariable=delay_var, width=110, height=34, fg_color="#FFFFFF", text_color="#2E2E2E", border_color="#E3C1D0", font=font_text).pack(anchor="w", padx=16)
            ctk.CTkLabel(card2, text="Độ trễ giữa các thao tác để ổn định hơn", font=font_big, text_color="#8A7B84").pack(anchor="w", padx=16, pady=(4, 10))

            ctk.CTkLabel(card3, text="Chế độ chạy", font=font_big, text_color="#B84F78").pack(anchor="w", padx=16, pady=(12, 4))
            run_mode_var = ctk.StringVar(value=thread_info["ui_settings"]["run_mode"])
            ctk.CTkOptionMenu(card3, values=["Smooth", "Fast", "Safe"], variable=run_mode_var, width=140, height=34, fg_color="#FFFFFF", button_color="#DAB3C2", button_hover_color="#C78DA4", text_color="#2E2E2E", font=font_text).pack(anchor="w", padx=16)
            ctk.CTkLabel(card3, text="Tối ưu cho máy yếu hoặc tool chạy đêm", font=font_big, text_color="#8A7B84").pack(anchor="w", padx=16, pady=(4, 10))

            # Card 4: Google Sheet Sync URL (trải full width ở row 2)
            card4 = ctk.CTkFrame(settings_grid, fg_color="#FAF7F9", corner_radius=14, border_width=1, border_color="#ECD9E2")
            card4.grid(row=2, column=0, columnspan=2, padx=(0, 0), pady=(0, 8), sticky="nsew")
            settings_grid.grid_columnconfigure(0, weight=1)
            settings_grid.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card4, text="📊 Google Sheet Sync URL", font=font_big, text_color="#B84F78").pack(anchor="w", padx=16, pady=(12, 4))

            sync_url_frame = ctk.CTkFrame(card4, fg_color="transparent")
            sync_url_frame.pack(fill="x", padx=16, pady=(0, 6))

            sync_url_entry = ctk.CTkEntry(
                sync_url_frame, height=34,
                fg_color="#FFFFFF", text_color="#2E2E2E",
                border_color="#E3C1D0", font=ctk.CTkFont(size=11),
                placeholder_text="Dán Apps Script URL vào đây (https://script.google.com/...)"
            )
            sync_url_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
            if getattr(self, 'sheet_sync_url', ''):
                sync_url_entry.insert(0, self.sheet_sync_url)

            def _save_sync_url(entry=sync_url_entry):
                url = entry.get().strip()
                self.sheet_sync_url = url
                self.save_config()
                if hasattr(self, "settings_status_lbl") and self.settings_status_lbl.winfo_exists():
                    self.settings_status_lbl.configure(text="✅ Đã lưu Sheet Sync URL!")

            ctk.CTkButton(
                sync_url_frame, text="💾 Lưu", width=70, height=34,
                fg_color="#3498DB", hover_color="#2980B9", text_color="#FFFFFF",
                font=font_text, command=_save_sync_url
            ).pack(side="left")

            ctk.CTkLabel(card4, text="Paste URL Apps Script từ Google Sheet Vikki vào đây để tự động sync ghi chú",
                         font=font_big, text_color="#8A7B84").pack(anchor="w", padx=16, pady=(0, 10))

            settings_actions = ctk.CTkFrame(settings_shell, fg_color="transparent")
            settings_actions.pack(fill="x", padx=12, pady=(0, 12))
            self.settings_status_lbl = ctk.CTkLabel(settings_actions, text="Sẵn sàng chỉnh cấu hình cho luồng này", font=font_text, text_color="#8A7B84")
            self.settings_status_lbl.pack(side="right", padx=8)

            def apply_theme_colors(theme_name):
                palettes = {
                    "Pink Luxury": {"bg": "#F5EEF3", "panel": "#FFFFFF", "border": "#E7CBD7", "card": "#FFFDFE", "card_border": "#ECD9E2", "header": "#B84F78", "row_even": "#FFFFFF", "row_odd": "#FFF6FA", "row_border": "#E8D3DE", "text": "#2E2E2E", "text_title": "#B84F78"},
                    "Midnight Rose": {"bg": "#1A1518", "panel": "#2D1F27", "border": "#5C3147", "card": "#36252F", "card_border": "#7A425E", "header": "#5C3147", "row_even": "#2A1C23", "row_odd": "#33222A", "row_border": "#5C3147", "text": "#E0E0E0", "text_title": "#DDBBC8"},
                    "Soft Rose": {"bg": "#FFF0F5", "panel": "#FFFFFF", "border": "#FFB6C1", "card": "#FFFAFA", "card_border": "#FFC0CB", "header": "#DB7093", "row_even": "#FFFFFF", "row_odd": "#FFF0F5", "row_border": "#FFB6C1", "text": "#2E2E2E", "text_title": "#DB7093"},
                    "Dark Hacker": {"bg": "#0D1117", "panel": "#161B22", "border": "#30363D", "card": "#21262D", "card_border": "#30363D", "header": "#238636", "row_even": "#161B22", "row_odd": "#0D1117", "row_border": "#30363D", "text": "#C9D1D9", "text_title": "#39D353"},
                    "Ocean Blue": {"bg": "#EBF5FB", "panel": "#FFFFFF", "border": "#AED6F1", "card": "#F4F6F7", "card_border": "#D6EAF8", "header": "#2874A6", "row_even": "#FFFFFF", "row_odd": "#EBF5FB", "row_border": "#D6EAF8", "text": "#1B4F72", "text_title": "#2874A6"}
                }
                p = palettes.get(theme_name, palettes["Pink Luxury"])

                try:
                    reg_win.configure(fg_color=p["bg"])
                    outer.configure(fg_color=p["bg"])
                    hero.configure(fg_color=p["panel"], border_color=p["border"])
                    panel.configure(fg_color=p["panel"], border_color=p["border"])
                    data_card.configure(fg_color=p["card"], border_color=p["card_border"])
                    table_card.configure(fg_color=p["card"], border_color=p["card_border"])
                    header_frame.configure(fg_color=p["header"])
                    settings_shell.configure(fg_color=p["card"], border_color=p["card_border"])
                    card1.configure(fg_color=p["card"], border_color=p["card_border"])
                    card2.configure(fg_color=p["card"], border_color=p["card_border"])
                    card3.configure(fg_color=p["card"], border_color=p["card_border"])

                    for r_idx, refs in enumerate(thread_info.get("row_refs", [])):
                        bg_color = p["row_even"] if r_idx % 2 == 0 else p["row_odd"]
                        refs["frame"].configure(fg_color=bg_color, border_color=p["row_border"])
                        refs["frame"]._original_bg = bg_color
                        refs["entry"].configure(fg_color=p["panel"], text_color=p["text"], border_color=p["row_border"])
                        refs["name_lbl"].configure(text_color="#1E8449")
                except Exception as e:
                    pass

            def save_settings():
                thread_info["ui_settings"]["auto_open"] = bool(auto_open_switch.get())
                try:
                    thread_info["ui_settings"]["delay_seconds"] = float(delay_var.get().strip())
                except Exception:
                    thread_info["ui_settings"]["delay_seconds"] = 0.5
                thread_info["ui_settings"]["run_mode"] = run_mode_var.get()
                if hasattr(self, "settings_status_lbl") and self.settings_status_lbl.winfo_exists():
                    self.settings_status_lbl.configure(text="Đã lưu preset cho luồng này")

            def apply_settings_to_flow():
                save_settings()
                self.log_msg(f"Luồng {index+1}", f"⚙️ Đã áp dụng cấu hình: {thread_info['ui_settings']}")
                apply_theme_colors(thread_info["ui_settings"]["theme"])
                if thread_info["ui_settings"]["auto_open"]:
                    self.open_all_games(index, thread_info.get("game_ui_elements", []))

            def reset_settings():
                auto_open_switch.deselect()
                delay_var.set("0.5")
                run_mode_var.set("Smooth")
                save_settings()
                apply_theme_colors("Pink Luxury")

            apply_theme_colors(thread_info["ui_settings"]["theme"])

            ctk.CTkButton(settings_actions, text="Lưu Preset", width=120, height=34, corner_radius=10,
                          fg_color="#EE7AA4", hover_color="#D95B8A", text_color="#FFFFFF", font=font_text,
                          command=save_settings).pack(side="left", padx=4)
            ctk.CTkButton(settings_actions, text="Áp Dụng Cho Luồng", width=150, height=34, corner_radius=10,
                          fg_color="#4A90E2", hover_color="#3B7FD0", text_color="#FFFFFF", font=font_text,
                          command=apply_settings_to_flow).pack(side="left", padx=4)
            ctk.CTkButton(settings_actions, text="Reset", width=90, height=34, corner_radius=10,
                          fg_color="#8E44AD", hover_color="#732D91", text_color="#FFFFFF", font=font_text,
                          command=reset_settings).pack(side="left", padx=4)

        except Exception:
            import traceback
            error_msg = traceback.format_exc()
            err_frame = ctk.CTkFrame(reg_win, fg_color="#FDEDEC", corner_radius=12, border_color="#E74C3C", border_width=2)
            err_frame.pack(padx=20, pady=20, fill="both", expand=True)
            ctk.CTkLabel(err_frame, text="L?I GIAO DI?N", font=("Arial", 20, "bold"), text_color="#C0392B").pack(pady=10)
            box = ctk.CTkTextbox(err_frame, width=1200, height=600, fg_color="#FFFFFF", text_color="#333333")
            box.pack(padx=10, pady=10)
            box.insert("0.0", error_msg)
            box.configure(state="disabled")

    def get_current_data(self, index):
        vars_dict = self.threads_data[index]["reg_vars"]
        data = {k: v.get().strip() for k, v in vars_dict.items()}
        sdt_input = data.get("SĐT", "")
        if sdt_input.lower() == "random" or sdt_input == "":
            data["SĐT_Thuc_Te"] = random.choice(['5', '9']) + "".join([str(random.randint(0, 9)) for _ in range(8)])
        else:
            data["SĐT_Thuc_Te"] = sdt_input.lstrip('0')
        return data

    def log_msg(self, thread_name, text):
        try:
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{thread_name}] {text}\n")
        except: pass
        
        try:
            curr_t = threading.current_thread()
            if hasattr(self, 'inline_log_map') and curr_t in self.inline_log_map:
                lbl = self.inline_log_map[curr_t]
                if lbl and lbl.winfo_exists():
                    clean_text = str(text).split('\n')[0]
                    clean_text = clean_text.replace("    + ", "↳ ").replace("  -> ", "➡ ").replace("▶ ", "")
                    self.root.after(0, lambda l=lbl, t=clean_text: l.configure(text=t))
        except: pass

        def write_log():
            with self.log_lock:
                msg_type = "info"
                if "❌" in text or "Lỗi" in text or "Blacklist" in text: msg_type = "error"
                elif "⚠️" in text or "Chưa có IP" in text or "Đang ngủ" in text or "Chờ" in text: msg_type = "warning"
                elif "✅" in text or "🎉" in text or "📋" in text: msg_type = "success"
                elif "🚀" in text or "⏳" in text or "⏭️" in text or "🔄" in text or "HỆ THỐNG" in thread_name: msg_type = "highlight"
                
                current_time = time.strftime("%H:%M:%S")
                self.log_box.insert("end", f"[{current_time}]", "time")
                
                thread_tag = "thread_sys"
                if "Luồng 1" in thread_name: thread_tag = "thread_1"
                elif "Luồng 2" in thread_name: thread_tag = "thread_2"
                elif "Luồng 3" in thread_name: thread_tag = "thread_3"
                elif "Luồng 4" in thread_name: thread_tag = "thread_4"
                elif "Luồng 5" in thread_name: thread_tag = "thread_5"
                
                self.log_box.insert("end", f" [{thread_name}] ", thread_tag)
                self.log_box.insert("end", "» ", "separator")
                
                parts = re.split(r'(\d+\.\d+\.\d+\.\d+)', text)
                for part in parts:
                    if re.match(r'\d+\.\d+\.\d+\.\d+', part): self.log_box.insert("end", part, "ip") 
                    else: self.log_box.insert("end", part, msg_type) 
                self.log_box.insert("end", "\n")
                
                try:
                    lines = int(self.log_box.index('end-1c').split('.')[0])
                    if lines > 500:
                        self.log_box.delete("1.0", f"{lines - 500}.0")
                except Exception: pass
                
                self.log_box.see("end")
        self.root.after(0, write_log)

    # ================= MỞ TẤT CẢ GAME (LÕI API GỐC - CHỐNG TRÀN RAM) =================
    def open_all_games(self, index, game_ui_elements):
        self.log_msg(f"Luồng {index+1}", "🚀 Đang nã đạn mở tab bằng API Lõi...")
        
        def run_opening_sequence():
            profile_id = self.threads_data[index]["profile_id"]
            ads_api = self.ads_api_entry.get().strip()
            t_name = f"Luồng {index+1}"
            try:
                res_active = requests.get(f"{ads_api}/api/v1/browser/active?user_id={profile_id}", timeout=5).json()
                if res_active.get("code") == 0 and res_active.get("data", {}).get("status") == "Active":
                    debug_addr = res_active["data"]["ws"]["selenium"]
                    
                    def get_tabs():
                        try:
                            return requests.get(f"http://{debug_addr}/json", timeout=5).json()
                        except:
                            return []
                    
                    for item in game_ui_elements:
                        tabs = get_tabs() 
                        game = item["game"]
                        lbl = item["status_lbl"]
                        
                        import urllib.parse
                        domain = urllib.parse.urlparse(game['url']).netloc
                        base_domain = domain.replace("m.", "").replace("www.", "")
                        
                        self.log_msg(t_name, f"🌐 Đang xử lý: {game['name']}")
                        self.root.after(0, lambda l=lbl: l.configure(text="Đang xử lý...", text_color="#3498DB"))
                        
                        target_tab_id = None
                        for tab in tabs:
                            curr_url = tab.get("url", "").lower()
                            curr_title = tab.get("title", "").lower()
                            if tab.get("type") == "page" and (base_domain in curr_url or game['name'].lower() in curr_url or game['name'].lower() in curr_title):
                                target_tab_id = tab['id']
                                break
                        
                        if target_tab_id:
                            try: requests.get(f"http://{debug_addr}/json/activate/{target_tab_id}", timeout=3)
                            except: pass
                        else:
                            safe_url = urllib.parse.quote(game['url'], safe=':/&?%=')
                            try: requests.put(f"http://{debug_addr}/json/new?{safe_url}", timeout=3)
                            except: pass
                        
                        self.threads_data[index]["game_states"][game['name']] = "✔ Đã Mở"
                        self.root.after(0, lambda l=lbl: l.configure(text="✔ Đã Mở", text_color="#32CD32"))
                        time.sleep(0.5)
                        
                    self.log_msg(t_name, "✅ Đã nã xong toàn bộ tab an toàn!")
                else:
                    self.log_msg(t_name, "⚠️ Trình duyệt chưa mở! Bấm 'Đóng, mở profile' trước nhé sếp.")
            except Exception as e:
                self.log_msg(t_name, f"⚠️ Lỗi kết nối: {e}")

        threading.Thread(target=run_opening_sequence, daemon=True).start()

    # ================= MỞ/ĐÓNG LẺ TỪNG TAB (BẢN KHÁNG TỬ HOÀN TOÀN) =================
    def manage_ads_tab(self, index, url, game_name, action="open", status_lbl=None, badge=None, inline_log_lbl=None):
        def task():
            if not hasattr(self, 'inline_log_map'): self.inline_log_map = {}
            if inline_log_lbl: self.inline_log_map[threading.current_thread()] = inline_log_lbl

            profile_id = self.threads_data[index]["profile_id"]
            ads_api = self.ads_api_entry.get().strip()
            t_name = f"Luồng {index+1}"
            
            try:
                res_active = requests.get(f"{ads_api}/api/v1/browser/active?user_id={profile_id}", timeout=5).json()
                
                if res_active.get("code") == 0 and res_active.get("data", {}).get("status") == "Active":
                    debug_addr = res_active["data"]["ws"]["selenium"]
                    import urllib.parse
                    domain = urllib.parse.urlparse(url).netloc
                    base_domain = domain.replace("m.", "").replace("www.", "")

                    def get_tabs():
                        try:
                            return requests.get(f"http://{debug_addr}/json", timeout=5).json()
                        except:
                            return []
                    
                    if action == "open":
                        self.log_msg(t_name, f"🌐 Đang kiểm tra tab game...")
                        if status_lbl and status_lbl.winfo_exists(): self.root.after(0, lambda: status_lbl.configure(text="Đang mở...", text_color="#3498DB"))
                        
                        tabs = get_tabs() 
                        target_tab_id = None
                        for tab in tabs:
                            curr_url = tab.get("url", "").lower()
                            curr_title = tab.get("title", "").lower()
                            if tab.get("type") == "page" and (base_domain in curr_url or game_name.lower() in curr_url or game_name.lower() in curr_title):
                                target_tab_id = tab['id']
                                break
                        
                        if target_tab_id:
                            self.log_msg(t_name, "    + Tab đã tồn tại, đang gọi nó lên trên cùng (Chống lag)...")
                            try: requests.get(f"http://{debug_addr}/json/activate/{target_tab_id}", timeout=3)
                            except: pass
                        else:
                            self.log_msg(t_name, "    + Đang mở tab mới...")
                            safe_url = urllib.parse.quote(url, safe=':/&?%=')
                            try: requests.put(f"http://{debug_addr}/json/new?{safe_url}", timeout=3)
                            except: pass
                        
                        self.threads_data[index]["game_states"][game_name] = "✔ Đã Mở"
                        self.log_msg(t_name, f"✅ Đã mở xong!")
                        if status_lbl and status_lbl.winfo_exists(): self.root.after(0, lambda: status_lbl.configure(text="✔ Đã Mở", text_color="#32CD32"))
                        
                    elif action == "close":
                        self.log_msg(t_name, f"✖ Đang tìm tab để đóng...")
                        if status_lbl and status_lbl.winfo_exists(): self.root.after(0, lambda: status_lbl.configure(text="Đang đóng...", text_color="#E74C3C"))
                        
                        tabs = get_tabs() 
                        page_tabs = [t for t in tabs if t.get("type") == "page"]
                        
                        has_anchor = any("newtab" in t.get("url", "") or "about:blank" in t.get("url", "") for t in page_tabs)
                        if not has_anchor:
                            self.log_msg(t_name, "    + Bơm tab trắng làm mỏ neo giữ mạng cho Profile...")
                            try: requests.put(f"http://{debug_addr}/json/new", timeout=3)
                            except: pass
                            time.sleep(1.5) 

                        closed = False
                        tabs_new = get_tabs() 
                        for tab in tabs_new:
                            curr_url = tab.get("url", "").lower()
                            curr_title = tab.get("title", "").lower()
                            
                            if tab.get("type") == "page" and (base_domain in curr_url or game_name.lower() in curr_url or game_name.lower() in curr_title):
                                self.log_msg(t_name, "    + Bóp cổ tab game...")
                                try: requests.get(f"http://{debug_addr}/json/close/{tab['id']}", timeout=3)
                                except: pass
                                closed = True
                                time.sleep(0.5) 
                                
                        if closed:
                            self.threads_data[index]["game_states"][game_name] = "✖ Đã Đóng"
                            self.log_msg(t_name, f"✅ Đã đóng tab thành công")
                            if status_lbl and status_lbl.winfo_exists(): self.root.after(0, lambda: status_lbl.configure(text="✖ Đã Đóng", text_color="#E74C3C"))
                        else:
                            self.log_msg(t_name, f"⚠️ Không tìm thấy tab để đóng")
                            if status_lbl and status_lbl.winfo_exists(): self.root.after(0, lambda: status_lbl.configure(text="Lỗi đóng", text_color="#D28F5A"))
                else:
                    self.log_msg(t_name, "⚠️ Trình duyệt chưa mở!")
            except Exception as e:
                self.log_msg(t_name, f"⚠️ Lỗi kết nối: {e}")
                
        threading.Thread(target=task, daemon=True).start()

    def save_new_url(self, game_name, entry_widget):
        import tkinter.messagebox
        new_url = entry_widget.get().strip()
        if not new_url: return
        
        top_win = entry_widget.winfo_toplevel()
        confirm = tkinter.messagebox.askyesno("Xác nhận đổi Link", f"Bạn có chắc chắn muốn đổi link mặc định của {game_name.upper()} thành:\n{new_url} ?", parent=top_win)
        
        if confirm:
            try:
                import json
                import os
                if os.path.exists("game_urls.json"):
                    with open("game_urls.json", "r", encoding="utf-8") as f:
                        urls = json.load(f)
                else:
                    urls = []
                for item in urls:
                    if item["name"] == game_name:
                        item["url"] = new_url
                        break
                with open("game_urls.json", "w", encoding="utf-8") as f:
                    json.dump(urls, f, indent=4)
                tkinter.messagebox.showinfo("Thành công", f"Đã cập nhật link cho {game_name.upper()}!", parent=top_win)
            except Exception as e:
                tkinter.messagebox.showerror("Lỗi", f"Không thể lưu link: {e}", parent=top_win)

    def stop_auto_thread(self, index, game_name):
        thread_key = f"{index}_{game_name}"
        if not hasattr(self, "running_auto_threads"): return
        t = self.running_auto_threads.get(thread_key)
        if t and t.is_alive():
            t.stop_requested = True
            self.log_msg(f"Luồng {index+1}", f"🛑 Đã gửi lệnh STOP cho {game_name.upper()}!")
            if hasattr(self, "inline_log_map") and t in self.inline_log_map:
                try:
                    self.inline_log_map[t].configure(text=f"Đã dừng Auto {game_name}", text_color="#E74C3C")
                except: pass

    # ================= ĐIỀU PHỐI AUTO FILL =================
    def trigger_auto_fill(self, index, game_name, data, status_lbl, badge, inline_log_lbl=None):
        def task():
            if not hasattr(self, 'inline_log_map'): self.inline_log_map = {}
            if inline_log_lbl: self.inline_log_map[threading.current_thread()] = inline_log_lbl

            t_name = f"Luồng {index+1}"
            driver = None 
            try:
                if status_lbl and status_lbl.winfo_exists():
                    self.root.after(0, lambda: status_lbl.configure(text="Đang Càn Quét...", text_color="#8A2BE2"))
                
                profile_id = self.threads_data[index]["profile_id"]
                ads_api = self.ads_api_entry.get().strip()
                sdt_da_xu_ly = data["SĐT_Thuc_Te"]

                try:
                    data["Ngân Hàng"] = self.bank_var.get()
                except:
                    data["Ngân Hàng"] = "VIKKI BANK"
                
                res_active = requests.get(f"{ads_api}/api/v1/browser/active?user_id={profile_id}", timeout=5).json()
                if res_active.get("code") != 0 or res_active.get("data", {}).get("status") != "Active":
                    self.log_msg(t_name, "⚠️ Trình duyệt chưa mở!")
                    if status_lbl and status_lbl.winfo_exists(): self.root.after(0, lambda: status_lbl.configure(text="Lỗi: Chưa mở", text_color="#D96E66"))
                    return

                debug_addr = res_active["data"]["ws"]["selenium"]
                driver_path = res_active["data"]["webdriver"]
                
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service

                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", debug_addr)
                
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                domain_map = {"mb66": "tgreg", "78win": "78win", "Open88": "open88", "789BET": "78985", "u888": "u888", "new88": "new88", "shbet": "shviet", "JUN88": "8866", "QQ88": "qq88", "rr88": "rr8391", "xx88": "xx0188", "gg88": "gg8862", "mm88": "mm88", "88vv": "88vv", "Hi88": "hi88"}
                target_keyword = domain_map.get(game_name, game_name.lower())

                found_tab = False
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    if target_keyword in driver.current_url.lower() or game_name.lower() in driver.title.lower():
                        found_tab = True
                        break

                if not found_tab:
                    self.log_msg(t_name, f"⚠️ Không tìm thấy tab {game_name}.")
                    return

                self.log_msg(t_name, f"⚡ Bắt đầu chuỗi Combo [{game_name}]...")

                success = False
                if game_name == "mb66":
                    success = self.auto_fill_mb66(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "78win":
                    success = self.auto_fill_78win(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "Open88":
                    success = self.auto_fill_open88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "789BET":
                    success = self.auto_fill_789bet(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "u888":
                    success = self.auto_fill_u888(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "new88":
                    success = self.auto_fill_new88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "shbet":
                    success = self.auto_fill_shbet(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "JUN88":
                    success = self.auto_fill_jun88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "QQ88":
                    success = self.auto_fill_qq88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "rr88":
                    success = self.auto_fill_rr88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "xx88":
                    success = self.auto_fill_xx88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "gg88":
                    success = self.auto_fill_gg88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "mm88":
                    success = self.auto_fill_mm88(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "88vv":
                    success = self.auto_fill_88vv(driver, data, sdt_da_xu_ly, t_name, index)
                elif game_name == "Hi88":
                    success = self.auto_fill_hi88(driver, data, sdt_da_xu_ly, t_name, index)

                if success and status_lbl and status_lbl.winfo_exists():
                    self.root.after(0, lambda: status_lbl.configure(text="✔ Hoàn Tất", text_color="#32CD32"))
                elif not success and status_lbl and status_lbl.winfo_exists():
                    self.root.after(0, lambda: status_lbl.configure(text="Lỗi Kẹt", text_color="#D96E66"))

            except Exception as e:
                self.log_msg(t_name, f"❌ Lỗi kẹt bất ngờ: {str(e)}")
            finally:
                try:
                    if driver and driver.service and driver.service.process:
                        import subprocess
                        pid = driver.service.process.pid
                        subprocess.call(f"taskkill /F /PID {pid} /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except:
                    pass

        import threading
        t = threading.Thread(target=task, daemon=True)
        if not hasattr(self, 'running_auto_threads'): self.running_auto_threads = {}
        self.running_auto_threads[f"{index}_{game_name}"] = t
        t.start()

    # [MODULE 1] - mb66
    def auto_fill_mb66(self, driver, data, sdt, t_name, index):
        import time
        import random
        try:
            def simulate_ctrl_v(selector, text, field_name):
                js_paste = f"""
                var el = document.querySelector('{selector}');
                if(el) {{ el.focus(); el.value = '{text}';
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    el.blur(); return true; }} return false;
                """
                if driver.execute_script(js_paste): self.log_msg(t_name, f"    + Đã điền: {field_name}")
                time.sleep(random.uniform(0.5, 1.2))

            def human_typing(selector, text):
                driver.execute_script(f"var el = document.querySelector('{selector}'); if(el) {{ el.focus(); el.value = ''; el.dispatchEvent(new Event('input')); }}")
                time.sleep(0.3)
                for char in str(text):
                    driver.execute_script(f"var el = document.querySelector('{selector}'); if(el) {{ el.value += '{char}'; el.dispatchEvent(new Event('input', {{bubbles: true}})); }}")
                    time.sleep(random.uniform(0.05, 0.15))

            self.log_msg(t_name, "▶ CHẶNG 1: Dọn rác và xử lý Đăng Ký...")
            driver.execute_script("document.querySelectorAll('.close, [alt=\"close\"], i.fa-times').forEach(el => { try{el.click();}catch(e){} });")
            driver.execute_script("""
                var btnDong = document.querySelector('button[translate="Common_Closed"]');
                if(btnDong) btnDong.click();
            """)
            time.sleep(1)
            driver.execute_script("var b = document.querySelector('a[href=\"/Account/Register\"]'); if(b) b.click();")
            time.sleep(2)

            simulate_ctrl_v('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            simulate_ctrl_v('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            simulate_ctrl_v('input[formcontrolname="name"]', data["Tên"], "Họ & tên")
            simulate_ctrl_v('input[formcontrolname="mobile"]', sdt, "Số điện thoại")
            
            driver.execute_script("var cb = document.querySelector('input[type=\"checkbox\"]'); if(cb && !cb.checked) cb.click();")
            time.sleep(1)

            driver.execute_script("var b = document.querySelector('span[translate=\"Register_Register\"]'); if(b) { b.click(); if(b.closest('button')) b.closest('button').click(); }")

            self.log_msg(t_name, "▶ CHẶNG 2: Rình bấm Lập Tức Nạp Tiền...")
            for _ in range(7):
                time.sleep(1)
                if driver.execute_script("var b = document.querySelector('button[translate=\"Register_DepositImmediately\"]'); if(b) { b.click(); return true; } return false;"):
                    self.log_msg(t_name, "  + Đã bấm Nạp Tiền!")
                    break

            self.log_msg(t_name, "▶ CHẶNG 3: Chuyển sang Tab Rút Tiền...")
            time.sleep(2)
            js_rut_tien = """
            var rt = Array.from(document.querySelectorAll('span')).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
            if(rt) { rt.click(); return true; } return false;
            """
            for _ in range(5):
                if driver.execute_script(js_rut_tien):
                    break
                time.sleep(1)

            self.log_msg(t_name, "▶ CHẶNG 4: Cài đặt Mã PIN...")
            time.sleep(2)
            js_alert_pin = """
            var alert = Array.from(document.querySelectorAll('span')).find(el => el.innerText.includes('Mật khẩu rút tiền chưa cài đặt'));
            if(alert) { alert.click(); return true; } return false;
            """
            if driver.execute_script(js_alert_pin):
                time.sleep(1.5)
                simulate_ctrl_v('input[formcontrolname="newPassword"]', data["Mã PIN"], "PIN 1")
                simulate_ctrl_v('input[formcontrolname="confirm"]', data["Mã PIN"], "PIN 2")
                driver.execute_script("Array.from(document.querySelectorAll('button')).find(el => el.innerText.trim().toLowerCase() === 'gửi đi')?.click();")
                time.sleep(2)

            self.log_msg(t_name, "▶ CHẶNG 5: Thêm Ngân Hàng (Múa phím)...")
            driver.execute_script("var el = document.querySelector('span.mat-select-placeholder'); if(el) el.click();")
            time.sleep(1.5)

            bank_name = data.get("Ngân Hàng", "VIKKI BANK").upper()
            human_typing('input[formcontrolname="filter"]', bank_name)
            time.sleep(1.5)

            driver.execute_script(f"Array.from(document.querySelectorAll('span.mat-option-text')).find(el => el.innerText.includes('{bank_name}'))?.click();")
            time.sleep(1)

            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Lấy Random Chi nhánh: {chi_nhanh}")
            human_typing('input[formcontrolname="city"]', chi_nhanh)

            simulate_ctrl_v('input[formcontrolname="account"]', data["STK"], "Số TK")

            driver.execute_script("var b = document.querySelector('button[type=\"submit\"] span[translate=\"Common_Submit\"]'); if(b) { b.click(); if(b.closest('button')) b.closest('button').click(); }")

            self.log_msg(t_name, "🎉 KẾT THÚC COMBO MB66 HOÀN HẢO!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module mb66: {e}")
            return False

    # [MODULE 2] - 78win
    def auto_fill_78win(self, driver, data, sdt, t_name, index):
        import time
        import random
        import ddddocr

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module VIP 78win (Fix React nuốt chữ Cài PIN)...")

            def react_typing(selector, text, field_name, is_append=False):
                self.log_msg(t_name, f"    + Đang lạch cạch gõ: {field_name}")
                if not is_append:
                    driver.execute_script(f"""
                        var el = document.querySelector('{selector}');
                        if(el) {{
                            el.focus();
                            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            if(setter) setter.call(el, '');
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    """)
                    time.sleep(0.3)

                for char in str(text):
                    driver.execute_script(f"""
                        var el = document.querySelector('{selector}');
                        if(el) {{
                            el.focus();
                            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            if(setter) setter.call(el, el.value + '{char}');
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    """)
                    time.sleep(random.uniform(0.05, 0.15))
                driver.execute_script(f"""var el = document.querySelector('{selector}'); if(el) el.blur();""")
                time.sleep(0.5)

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm thần tốc: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.8)

            max_retries = 5
            success_reg = False

            for attempt in range(max_retries):
                self.log_msg(t_name, f"▶ [Vòng {attempt + 1}] Bắt đầu quy trình Đăng ký...")
                
                driver.execute_script("""
                    var closeAd = document.querySelector('img[alt="modal-close-button"]');
                    if(closeAd) closeAd.click();
                    var dontShow = document.querySelector('div.dontshow');
                    if(dontShow) dontShow.click();
                """)
                time.sleep(1.5)
                
                driver.execute_script("""var btnReg = document.querySelector('span.is-signup'); if(btnReg) btnReg.click();""")
                time.sleep(2)

                react_typing('#playerid', data["TK"], "Tài khoản")
                react_typing('#password', data["MK"], "Mật khẩu")
                react_typing('#firstname', data["Tên"], "Họ & tên")
                
                driver.execute_script("""
                    var tel = document.querySelector('input[type="tel"]'); 
                    if(tel) tel.focus();
                """)
                time.sleep(0.3)
                react_typing('input[type="tel"]', sdt, "Số điện thoại", is_append=True)

                driver.execute_script("""
                    var cb = document.querySelector('input[type="checkbox"]'); 
                    if(cb && !cb.checked) cb.click();
                """)
                time.sleep(1)

                self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
                driver.execute_script("""var btnSubmit = document.querySelector('button.nrc-button'); if(btnSubmit) btnSubmit.click();""")
                time.sleep(3)

                is_verify = driver.execute_script("""
                    return document.body.innerText.includes('Trượt để hoàn thành') || 
                           document.body.innerText.includes('ghép hình') || 
                           document.querySelector('div[class*="captcha"]') !== null ||
                           document.querySelector('div[class*="slider"]') !== null;
                """)
                if is_verify:
                    self.log_msg(t_name, "🚨 BÁO ĐỘNG: 78WIN đòi trượt Captcha! Sếp mau thò tay kéo phát, em đứng chờ sếp đây!")
                    self.log_msg(t_name, "⏳ Bot đang nín thở... (Sếp có 60s để xử lý)")

                    passed = False
                    for _ in range(60): 
                        time.sleep(1)
                        still_there = driver.execute_script("""
                            return document.body.innerText.includes('Trượt để hoàn thành') || 
                                   document.body.innerText.includes('ghép hình');
                        """)
                        if not still_there:
                            passed = True
                            break 
                            
                    if passed:
                        self.log_msg(t_name, "🎉 TUYỆT VỜI SẾP ƠI! Đã qua ải Xác minh. Bot chuẩn bị chạy tiếp đây...")
                        time.sleep(4) 
                    else:
                        self.log_msg(t_name, "❌ Hết 60s sếp chưa thao tác xong. Tool xin phép hủy luồng!")
                        return False
                else:
                    self.log_msg(t_name, "✅ May quá web không đòi Xác minh, đi tiếp luôn!")
                    time.sleep(2)

                is_success = driver.execute_script("""
                    var btnHome = Array.from(document.querySelectorAll('button.sec-btn')).find(el => el.innerText.includes('Trang chủ'));
                    if(btnHome) { btnHome.click(); return true; } return false;
                """)
                if is_success:
                    self.log_msg(t_name, "✅ Đăng ký thành công! Đã bấm về Trang chủ.")
                    success_reg = True
                    break

                is_error = driver.execute_script("""
                    var btnClose = Array.from(document.querySelectorAll('button.pri-btn')).find(el => el.innerText.includes('Đóng'));
                    if(btnClose) { btnClose.click(); return true; } return false;
                """)
                if is_error:
                    self.log_msg(t_name, "❌ Web báo lỗi (Sai mã/Bận)! Đang F5 tải lại trang...")
                    driver.refresh()
                    time.sleep(4)
                    continue

                is_still_here = driver.execute_script("""return document.querySelector('input[placeholder="Mã xác minh"]') !== null;""")
                if is_still_here:
                    self.log_msg(t_name, "⚠️ Kẹt ở Form. Đang F5 tải lại trang...")
                    driver.refresh()
                    time.sleep(4)
                    continue

                success_reg = True
                break

            if not success_reg:
                self.log_msg(t_name, "⚠️ F5 5 lần vẫn xịt. Bỏ qua luồng này.")
                return False

            time.sleep(3)

            self.log_msg(t_name, "▶ CHẶNG 6: Dọn rác Trang chủ & Vào Rút Tiền...")
            driver.execute_script("""
                var closeAd = document.querySelector('img[alt="modal-close-button"]');
                if(closeAd) closeAd.click();
            """)
            time.sleep(1.5)
            
            driver.execute_script("""var wIcon = document.querySelector('img[src*="func-withdrawal"]'); if(wIcon) wIcon.click();""")
            time.sleep(2)
            driver.execute_script("""var btnRut = Array.from(document.querySelectorAll('div.btn')).find(el => el.innerText.includes('Rút tiền')); if(btnRut) btnRut.click();""")
            time.sleep(3)

            self.log_msg(t_name, "▶ CHẶNG 7: Cài đặt Mã PIN...")
            fast_react_fill('#pin', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('#confirmpin', data["Mã PIN"], "Mã PIN 2")
            
            self.log_msg(t_name, f"    + Đang mổ cò Mật khẩu Game để web xác nhận...")
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="password"]');
                var passInput = inputs[inputs.length - 1]; 
                if(passInput) {
                    passInput.focus();
                    let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    if(setter) setter.call(passInput, '');
                    passInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            """)
            time.sleep(0.3)
            
            for char in str(data["MK"]):
                driver.execute_script(f"""
                    var inputs = document.querySelectorAll('input[type="password"]');
                    var passInput = inputs[inputs.length - 1];
                    if(passInput) {{
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(passInput, passInput.value + '{char}');
                        passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                """)
                time.sleep(0.1)
                
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="password"]');
                var passInput = inputs[inputs.length - 1];
                if(passInput) {
                    passInput.dispatchEvent(new Event('change', { bubbles: true }));
                    passInput.blur();
                }
            """)
            time.sleep(1.5) 
            
            self.log_msg(t_name, "  -> Đang bấm Cập nhật PIN...")
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('button'));
                var btnCapNhat = btns.find(el => el.innerText.trim() === 'Cập nhật' && el.classList.contains('fill-player-info-btn'));
                if(!btnCapNhat) btnCapNhat = btns.find(el => el.innerText.trim() === 'Cập nhật');
                if(btnCapNhat) {
                    var rect = btnCapNhat.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 2 });
                    btnCapNhat.dispatchEvent(ev);
                }
            """)
            
            time.sleep(3)
            driver.execute_script("""var btnDong = Array.from(document.querySelectorAll('button.pri-btn')).find(el => el.innerText.includes('Đóng')); if(btnDong) btnDong.click();""")
            time.sleep(2)

            self.log_msg(t_name, "▶ CHẶNG 8: Liên kết Bank...")
            driver.execute_script("""var bId = document.querySelector('#bankid'); if(bId) bId.click();""")
            time.sleep(1.5)
            
            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "dong" if bank_choice == "VIKKI BANK" else "tp"
            target_alt = "DongA Bank" if bank_choice == "VIKKI BANK" else "TPBank"
            
            fast_react_fill('input.formik-input[placeholder="Nhập tên ngân hàng"]', search_keyword, f"Tìm kiếm bank: {search_keyword}")
            time.sleep(1.5)
            driver.execute_script(f"""var bLogo = document.querySelector('img[alt="{target_alt}"]'); if(bLogo) bLogo.click();""")
            time.sleep(1.5)
            
            fast_react_fill('#bankaccount', data["STK"], "Số Tài Khoản")
            
            self.log_msg(t_name, f"    + Đang mổ cò Mật khẩu Game (Lần 2)...")
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="password"]');
                var passInput = inputs[inputs.length - 1]; 
                if(passInput) {
                    passInput.focus();
                    let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    if(setter) setter.call(passInput, '');
                    passInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            """)
            time.sleep(0.3)
            
            for char in str(data["MK"]):
                driver.execute_script(f"""
                    var inputs = document.querySelectorAll('input[type="password"]');
                    var passInput = inputs[inputs.length - 1];
                    if(passInput) {{
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(passInput, passInput.value + '{char}');
                        passInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                """)
                time.sleep(0.1)
                
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="password"]');
                var passInput = inputs[inputs.length - 1];
                if(passInput) {
                    passInput.dispatchEvent(new Event('change', { bubbles: true }));
                    passInput.blur();
                }
            """)
            
            time.sleep(1.5)
            self.log_msg(t_name, "  -> Gửi thông Ngân hàng...")
            driver.execute_script("""
                var btnOK = Array.from(document.querySelectorAll('button.nrc-button')).find(el => el.innerText === 'OK'); 
                if(btnOK) {
                    var rect = btnOK.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + rect.width / 2, clientY: rect.top + rect.height / 2 });
                    btnOK.dispatchEvent(ev);
                }
            """)
            time.sleep(3.5)
            
            driver.execute_script("""var btnDongCuoi = Array.from(document.querySelectorAll('button.pri-btn')).find(el => el.innerText.includes('Đóng')); if(btnDongCuoi) btnDongCuoi.click();""")
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN 78WIN FULL COMBO KHÔNG LỖI LẦM!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module 78win: {e}")
            return False

    # [MODULE 3] - Open88
    def auto_fill_open88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module OPEN88 (Chế độ Bán Thủ Công)...")

            val_ten = list(data.values())[0]
            val_stk = list(data.values())[2]
            val_tk  = list(data.values())[3]
            val_mk  = list(data.values())[4]
            val_pin = list(data.values())[5]

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            self.log_msg(t_name, "▶ CHẶNG 1: Bơm form Đăng Ký...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1)
            
            fast_react_fill('input[name="username"]', val_tk, "Tài khoản")
            fast_react_fill('input[name="password"]', val_mk, "Mật khẩu")
            fast_react_fill('input[name="payeeName"]', val_ten, "Họ & tên")
            
            self.log_msg(t_name, "    + Đang bơm: Số điện thoại")
            driver.execute_script(f"""
                var sdtInput = document.querySelector('input[name="mobile"]') || 
                               document.querySelector('input[type="tel"]') ||
                               document.querySelector('input[name="phone"]');
                               
                if(!sdtInput) {{
                    var inputs = document.querySelectorAll('input');
                    for(var i=0; i<inputs.length; i++) {{
                        var ph = inputs[i].placeholder || '';
                        if(ph.indexOf('S') !== -1 && ph.indexOf('T') !== -1) {{
                            sdtInput = inputs[i]; break;
                        }}
                    }}
                }}
                
                if(sdtInput) {{
                    sdtInput.focus();
                    let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    if(setter) setter.call(sdtInput, '{sdt}');
                    sdtInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    sdtInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    sdtInput.blur();
                }}
            """)
            time.sleep(1)
            
            driver.execute_script("""var cb = document.querySelector('input[type="checkbox"]'); if(cb && !cb.checked) cb.click();""")
            time.sleep(0.5)

            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script("var btnReg = document.querySelector('button.submit-btn.register-btn'); if(btnReg) btnReg.click();")
            time.sleep(2.5)

            is_verify = driver.execute_script("""return document.querySelector('.botion_btn') !== null;""")
            if is_verify:
                self.log_msg(t_name, "🚨 BÁO ĐỘNG: Web đòi Xác minh! Sếp mau thò tay kéo phát, em đứng chờ sếp đây!")
                self.log_msg(t_name, "⏳ Bot đang nín thở... (Sếp có 60s để xử lý)")

                passed = False
                for _ in range(60): 
                    time.sleep(1)
                    still_there = driver.execute_script("""return document.querySelector('.botion_btn') !== null;""")
                    if not still_there:
                        passed = True
                        break 
                        
                if passed:
                    self.log_msg(t_name, "🎉 TUYỆT VỜI SẾP ƠI! Đã qua ải Xác minh. Bot chuẩn bị chạy tiếp đây...")
                    time.sleep(4) 
                else:
                    self.log_msg(t_name, "❌ Hết 60s sếp chưa thao tác xong. Tool xin phép hủy luồng!")
                    return False
            else:
                self.log_msg(t_name, "✅ May quá web không đòi Xác minh, đi tiếp luôn!")
                time.sleep(4) 

            self.log_msg(t_name, "▶ CHẶNG 3: Vận công dọn rác quảng cáo (Quét liên tục)...")
            
            for _ in range(5):
                driver.execute_script("""
                    try {
                        var btnDongY = document.querySelector('button.bottom-btn--agree'); 
                        if(btnDongY) btnDongY.click();
                        
                        var btns = Array.from(document.querySelectorAll('span, div, button'));
                        var btnHuy = btns.find(el => el.innerText.indexOf('H') !== -1 || el.innerText.indexOf('T') !== -1);
                        if(btnHuy) btnHuy.click();

                        var btn1 = document.querySelector('.am-navbar-title.close-btn-outside');
                        if(btn1) btn1.click();

                        var depositSvg = document.querySelector('.am-icon-deposit-close');
                        if (depositSvg) {
                            try { depositSvg.click(); } catch(e){}
                            try { if(depositSvg.parentElement) depositSvg.parentElement.click(); } catch(e){}
                            try {
                                var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                                depositSvg.dispatchEvent(ev);
                            } catch(e){}
                        }

                        var btn3 = document.querySelector('svg.a2hs-close, .a2hs-close');
                        if(btn3) {
                            try { btn3.click(); } catch(e){}
                            try { if(btn3.parentElement) btn3.parentElement.click(); } catch(e){}
                        }

                        var btn5 = document.querySelector('.am-icon-cross');
                        if(btn5) {
                            try { btn5.click(); } catch(e){}
                            try { if(btn5.parentElement) btn5.parentElement.click(); } catch(e){}
                        }
                        
                        var useEls = document.querySelectorAll('use');
                        useEls.forEach(function(use) {
                            var href = use.getAttribute('xlink:href');
                            if(href && (href.includes('close') || href.includes('cross'))) {
                                var svg = use.closest('svg');
                                if(svg) {
                                    try { svg.click(); } catch(e){}
                                    try { if(svg.parentElement) svg.parentElement.click(); } catch(e){}
                                }
                            }
                        });
                    } catch(e) {}
                """)
                time.sleep(1.5)

            self.log_msg(t_name, "  -> Đang tìm đường vào Rút Tiền...")
            driver.execute_script("""
                try {
                    var useRut = document.querySelector('use[*|href="#nav-withdraw_fa818281"]');
                    if(useRut) {
                        var target = useRut.closest('.am-tab-bar-item') || useRut.closest('svg') || useRut.parentNode;
                        if(target) {
                            var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                            target.dispatchEvent(ev);
                        }
                    }
                } catch(e) {}
            """)
            time.sleep(3) 

            driver.execute_script("""
                var btnAdd = document.querySelector('.withdraw-bkadd'); 
                if(btnAdd) {
                    btnAdd.click();
                }
            """)
            time.sleep(2)

            self.log_msg(t_name, "▶ CHẶNG 4: Bơm thông tin Bank & Mã PIN...")

            driver.execute_script("""
                var selBank = document.querySelector('div.inputBase'); 
                if(selBank) selBank.click();
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "VIKKI" if bank_choice == "VIKKI BANK" else "TPBank"
            target_text = "Vikki Digital Bank" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_react_fill('input.inputBase', search_keyword, f"Tìm {search_keyword}")
            time.sleep(1.5)

            driver.execute_script(f"""
                var items = document.querySelectorAll('.am-list-content');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            fast_react_fill('input[name="bankCard"]', val_stk, "Số tài khoản")

            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Lấy Random Chi nhánh: {chi_nhanh}")
            fast_react_fill('input[name="customBankBranch"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[name="withdraw"]', val_pin, "Mã PIN 1")
            fast_react_fill('input[name="withdrawT"]', val_pin, "Mã PIN 2")

            self.log_msg(t_name, "▶ CHẶNG 5: Chốt Xác nhận...")

            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('span.am-button.btn-gray, span.am-button'));
                var btnXN = btns.find(el => el.innerText.indexOf('X') !== -1 && el.innerText.indexOf('n') !== -1);
                if(btnXN) btnXN.click();
            """)
            time.sleep(2)

            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('a.am-modal-button'));
                var btnXN2 = btns.find(el => el.innerText.indexOf('X') !== -1 && el.innerText.indexOf('n') !== -1);
                if(btnXN2) btnXN2.click();
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN OPEN88 THÀNH CÔNG RỰC RỠ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module Open88: {e}")
            return False

    # [MODULE 4] - Code xử lý 789BET (BẢN VÒNG LẶP CLICK CHẬM & ÉP 4 SỐ)
    def auto_fill_789bet(self, driver, data, sdt, t_name, index):
        import time
        import random
        import ddddocr
        import re

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module 789BET (Chế độ Cẩn Thận Từng Giây)...")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            # ================= CHẶNG 1: ĐIỀN FORM (Chỉ điền 1 lần) =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bơm form Đăng Ký...")
            fast_react_fill('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            fast_react_fill('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[formcontrolname="name"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[formcontrolname="mobile"]', sdt, "Số điện thoại")

            # ================= CHẶNG 2: VÒNG LẶP CAPTCHA CẨN THẬN =================
            success_reg = False
            for attempt in range(5): # Tối đa thử nộp form 5 lần
                self.log_msg(t_name, f"▶ CHẶNG 2 [Vòng nộp Form {attempt+1}]: Xử lý Captcha...")
                
                captcha_text = ""
                # VÒNG LẶP NHỎ ÉP AI ĐỌC CHUẨN 4 SỐ (Tối đa 4 lần đổi ảnh)
                for ocr_retry in range(4):
                    self.log_msg(t_name, "    + Click chuột vào ô Captcha và chờ 2s load ảnh...")
                    # Giả lập click chuột vật lý cực chuẩn
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) {
                            el.focus();
                            var rect = el.getBoundingClientRect();
                            var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                            el.dispatchEvent(ev);
                        }
                    """)
                    
                    time.sleep(2) # Chờ 2s theo đúng ý sếp cho ảnh nét căng
                    
                    try:
                        img_element = driver.execute_script("""
                            var input = document.querySelector('input[formcontrolname="checkCode"]');
                            if(input) {
                                return input.parentElement.querySelector('img');
                            }
                            return null;
                        """)
                        
                        if img_element:
                            img_bytes = img_element.screenshot_as_png
                            ocr = ddddocr.DdddOcr(show_ad=False)
                            raw_text = ocr.classification(img_bytes)
                            
                            # Tẩy rửa thành số
                            clean_text = raw_text.lower()
                            clean_text = clean_text.replace('o', '0').replace('q', '0').replace('l', '1').replace('i', '1').replace('z', '2').replace('s', '5').replace('b', '8').replace('g', '9')
                            temp_captcha = re.sub(r'\D', '', clean_text)
                            
                            # KIỂM TRA ĐỦ 4 SỐ CHƯA
                            if len(temp_captcha) == 4:
                                captcha_text = temp_captcha
                                self.log_msg(t_name, f"    🤖 AI đọc CHUẨN 4 SỐ: '{captcha_text}'")
                                break # Đủ số thì thoát vòng lặp nhỏ đi nộp
                            else:
                                self.log_msg(t_name, f"    ⚠️ AI ẩu (đọc ra '{raw_text}' -> thành {len(temp_captcha)} số). Đổi ảnh khác!")
                                # Gõ phím Backspace xóa trắng ô để click lại không bị lỗi
                                driver.execute_script("""
                                    var el = document.querySelector('input[formcontrolname="checkCode"]');
                                    if(el) { el.value = ''; el.dispatchEvent(new Event('input')); }
                                """)
                                time.sleep(1)
                        else:
                            self.log_msg(t_name, "⚠️ Không tìm thấy ảnh Captcha!")
                            break
                    except Exception as e:
                        self.log_msg(t_name, f"❌ Lỗi AI đọc Captcha: {e}")
                        break

                if len(captcha_text) != 4:
                    self.log_msg(t_name, "❌ 4 lần AI đều đọc thiếu số. Xin phép hủy luồng để qua Acc khác.")
                    return False
                
                # Điền 4 số chuẩn vào ô
                fast_react_fill('input[formcontrolname="checkCode"]', captcha_text, "Mã Captcha")

                self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
                driver.execute_script("""
                    var btn = document.querySelector('span[translate="Login_RegisterBtn"]') || 
                              Array.from(document.querySelectorAll('button, a, div')).find(el => el.innerText && el.innerText.trim().toUpperCase() === 'ĐĂNG KÝ NGAY') ||
                              Array.from(document.querySelectorAll('button')).find(el => el.innerText && el.innerText.trim().toUpperCase() === 'ĐĂNG KÝ');
                    if(btn) btn.click();
                """)
                time.sleep(3.5)

                # KIỂM TRA BẢNG LỖI 
                is_error = driver.execute_script("""
                    var btnConfirm = document.querySelector('button[translate="Common_Confirm"]') ||
                                     Array.from(document.querySelectorAll('button, span, div.confirm-btn')).find(el => el.innerText && (el.innerText.trim() === 'Xác nhận' || el.innerText.trim() === 'Đồng ý' || el.innerText.trim() === 'OK'));
                    if(btnConfirm) {
                        btnConfirm.click();
                        return true;
                    }
                    // Thêm check toast error của Angular
                    var toast = document.querySelector('.toast-message, .ng-trigger-flyInOut');
                    if(toast) {
                        return true;
                    }
                    return false;
                """)

                if is_error:
                    self.log_msg(t_name, "❌ Web báo sai Captcha! Đã bấm xác nhận, làm lại chậm rãi...")
                    time.sleep(1.5)
                    # Xóa trắng ô input trước khi vòng lặp quay lại click
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) { el.value = ''; el.dispatchEvent(new Event('input', {bubbles: true})); }
                    """)
                    time.sleep(1)
                    continue 

                # KIỂM TRA THÀNH CÔNG LỌT VÀO TRONG
                is_success = driver.execute_script("""
                    var successBtn = document.querySelector('button[translate="Register_DepositImmediately"]') ||
                                     Array.from(document.querySelectorAll('button, a')).find(el => el.innerText && el.innerText.trim().toUpperCase().includes('NẠP TIỀN'));
                    return successBtn !== null || window.location.href.toLowerCase().includes('/home') || window.location.href.toLowerCase().includes('/user') || document.querySelector('i.icon.wallet') !== null;
                """)
                if is_success:
                    self.log_msg(t_name, "✅ Đăng ký thành công! Đã lọt vào trong.")
                    success_reg = True
                    break
                else:
                    time.sleep(2)
                    if driver.execute_script("""return document.querySelector('button[translate="Register_DepositImmediately"]') !== null;"""):
                        self.log_msg(t_name, "✅ Đăng ký thành công! Đã lọt vào trong.")
                        success_reg = True
                        break

            if not success_reg:
                self.log_msg(t_name, "❌ Đăng ký 5 lần đều xịt! Tool xin phép hủy luồng.")
                return False

            # ================= CHẶNG 3: DỌN QUẢNG CÁO =================
            self.log_msg(t_name, "▶ CHẶNG 3: Vào trang trong & Dọn quảng cáo...")
            driver.execute_script("""var btn = document.querySelector('button[translate="Register_DepositImmediately"]'); if(btn) btn.click();""")
            time.sleep(2.5)
            
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1.5)

            # ================= CHẶNG 4: VÀO RÚT TIỀN & CÀI PIN =================
            self.log_msg(t_name, "▶ CHẶNG 4: Chuyển sang Tab Rút Tiền...")
            driver.execute_script("""var iconWallet = document.querySelector('i.icon.wallet'); if(iconWallet) iconWallet.click();""")
            time.sleep(1.5)
            driver.execute_script("""var btnRut = document.querySelector('a[href="/Financial?type=withdraw"]') || document.querySelector('i.icon.withdraw'); if(btnRut) btnRut.click();""")
            time.sleep(2.5)

            self.log_msg(t_name, "▶ CHẶNG 5: Cài đặt Mã PIN (Rút tiền)...")
            driver.execute_script("""var btnCaiDat = document.querySelector('a[href="/Account/ChangeMoneyPassword"]'); if(btnCaiDat) btnCaiDat.click();""")
            time.sleep(1.5)
            
            fast_react_fill('input[formcontrolname="newPassword"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[formcontrolname="confirm"]', data["Mã PIN"], "Mã PIN 2")
            
            driver.execute_script("""var btnGui = document.querySelector('span[translate="Account_Submit"]'); if(btnGui) btnGui.click();""")
            time.sleep(2.5)

            # ================= CHẶNG 6: THÊM NGÂN HÀNG =================
            self.log_msg(t_name, "▶ CHẶNG 6: Thêm Ngân Hàng...")
            driver.execute_script("""var el = document.querySelector('span.mat-select-placeholder'); if(el) el.click();""")
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            target_text = "VIKKI BANK" if bank_choice == "VIKKI BANK" else "TPBANK"

            driver.execute_script(f"""
                var searchInput = document.querySelector('input[formcontrolname="filter"]') || document.querySelector('input.mat-input-element');
                if(searchInput) {{
                    searchInput.focus();
                    searchInput.value = '{target_text}';
                    searchInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            """)
            time.sleep(1)

            driver.execute_script(f"""
                var items = document.querySelectorAll('span.mat-option-text');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Chi nhánh Random: {chi_nhanh}")
            fast_react_fill('input[formcontrolname="city"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[formcontrolname="account"]', data["STK"], "Số TK")

            driver.execute_script("""var btnSubmit = document.querySelector('span[translate="Common_Submit"]'); if(btnSubmit) btnSubmit.click();""")
            time.sleep(2.5)

            self.log_msg(t_name, "  -> Cú click Rút Tiền chốt hạ...")
            driver.execute_script("""
                var items = document.querySelectorAll('li span.truncate');
                var target = Array.from(items).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
                if(target) target.parentElement.click();
            """)
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN 789BET NHANH NHƯ CHỚP!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module 789BET: {e}")
            return False
 
    # [MODULE 5] - Code xử lý u888 (BẢN CHẬM RÃI Y HỆT NGƯỜI THẬT)
    def auto_fill_u888(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module u888 (Chế độ Chậm rãi chắc cú)...")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            # ================= CHẶNG 1: DỌN RÁC & VÀO FORM =================
            self.log_msg(t_name, "▶ CHẶNG 1: Dọn quảng cáo & Vào form Đăng ký...")
            
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1)
            
            driver.execute_script("""var btnDong2 = document.querySelector('button[translate="Announcement_GotIt"]'); if(btnDong2) btnDong2.click();""")
            time.sleep(1)
            
            driver.execute_script("""var btnReg = document.querySelector('button[routerlink="/Account/Register"]'); if(btnReg) btnReg.click();""")
            time.sleep(2.5) # Nới thêm tí chờ load form

            # ================= CHẶNG 2: BƠM DỮ LIỆU ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 2: Bơm dữ liệu Form Đăng Ký...")
            fast_react_fill('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            fast_react_fill('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[formcontrolname="name"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[formcontrolname="mobile"]', sdt, "Số điện thoại")

            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script("""
                var btn = document.querySelector('span[translate="Login_RegisterBtn"]'); 
                if(btn) { btn.click(); if(btn.closest('button')) btn.closest('button').click(); }
            """)
            time.sleep(3.5)

            # ================= CHẶNG 3: VÀO TRANG TRONG & DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 3: Vào trang trong & Dọn quảng cáo...")
            driver.execute_script("""var btn = document.querySelector('button[translate="Register_DepositImmediately"]'); if(btn) btn.click();""")
            time.sleep(3.5) # CHỜ 3.5s CHO WEB RENDER XONG TRANG CHỦ
            
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(2) # CHỜ 2s CHO POPUP TẮT HẲN

            # ================= CHẶNG 4: VÀO RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 4: Từ từ bấm sang Tab Rút Tiền...")
            driver.execute_script("""
                var items = document.querySelectorAll('li span');
                var target = Array.from(items).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
                if(target) { 
                    var elToClick = target.closest('li') || target;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            self.log_msg(t_name, "    + Đang nhâm nhi ngụm trà chờ trang Rút tiền load...")
            time.sleep(4) # CHỜ HẲN 4s ĐỂ GIAO DIỆN CHUYỂN TRANG MƯỢT MÀ, KHÔNG BỊ SỐC

            # ================= CHẶNG 5: CÀI ĐẶT MÃ PIN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Click Cài đặt Mã PIN...")
            driver.execute_script("""
                var alert = Array.from(document.querySelectorAll('span')).find(el => el.innerText.includes('Mật khẩu rút tiền chưa cài đặt'));
                if(alert) { 
                    var elToClick = alert.closest('a') || alert;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            time.sleep(2.5) # CHỜ 2.5s CHO FORM ĐIỀN PIN NẢY LÊN TỪ TỪ
            
            fast_react_fill('input[formcontrolname="newPassword"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[formcontrolname="confirm"]', data["Mã PIN"], "Mã PIN 2")
            
            driver.execute_script("""
                var btnGui = document.querySelector('span[translate="Account_Submit"]'); 
                if(btnGui) { btnGui.click(); if(btnGui.closest('button')) btnGui.closest('button').click(); }
            """)
            time.sleep(3) # CHỜ 3s XÁC NHẬN PIN

            # ================= CHẶNG 6: THÊM NGÂN HÀNG =================
            self.log_msg(t_name, "▶ CHẶNG 6: Thêm Ngân Hàng...")
            driver.execute_script("""var el = document.querySelector('span.mat-select-placeholder'); if(el) el.click();""")
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            target_text = "VIKKI BANK" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_react_fill('input[formcontrolname="filter"]', target_text, f"Tìm {target_text}")
            time.sleep(1.5)

            driver.execute_script(f"""
                var items = document.querySelectorAll('span.mat-option-text');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Chi nhánh Random: {chi_nhanh}")
            fast_react_fill('input[formcontrolname="city"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[formcontrolname="account"]', data["STK"], "Số TK")

            self.log_msg(t_name, "  -> Cú click Gửi đi chốt hạ...")
            driver.execute_script("""
                var btnSubmit = document.querySelector('button.btn-submit span[translate="Common_Submit"]'); 
                if(btnSubmit) { btnSubmit.click(); if(btnSubmit.closest('button')) btnSubmit.closest('button').click(); }
            """)
            time.sleep(2.5)
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN U888 CHẬM RÃI MÀ CHẮC CÚ THÀNH CÔNG!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module u888: {e}")
            return False

    # [MODULE 6] - Code xử lý new88 (BẢN CHẬM RÃI CHẮC CÚ NHƯ U888)
    def auto_fill_new88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module new88 (Chế độ Slow Motion chống văng)...")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            # ================= CHẶNG 1: VÀO FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bơm dữ liệu Form Đăng Ký...")
            # Form của bọn này mở lên là vào luôn đăng ký, không có quảng cáo đầu
            
            fast_react_fill('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            fast_react_fill('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[formcontrolname="name"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[formcontrolname="mobile"]', sdt, "Số điện thoại")

            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script("""
                var btn = document.querySelector('span[translate="Register_Register"]'); 
                if(btn) { btn.click(); if(btn.closest('button')) btn.closest('button').click(); }
            """)
            time.sleep(3.5) # Chờ 3.5s cho nó gửi Data lên server

            # ================= CHẶNG 2: VÀO TRANG TRONG & DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 2: Vào trang trong & Dọn quảng cáo...")
            driver.execute_script("""var btn = document.querySelector('button[translate="Register_DepositImmediately"]'); if(btn) btn.click();""")
            time.sleep(3.5) # CHỜ 3.5s CHO WEB RENDER XONG TRANG CHỦ
            
            # Tắt quảng cáo 1
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1) 
            
            # Tắt quảng cáo 2
            driver.execute_script("""var btnDong2 = document.querySelector('button[translate="Announcement_GotIt"]'); if(btnDong2) btnDong2.click();""")
            time.sleep(2) # CHỜ 2s CHO POPUP TẮT HẲN

            # ================= CHẶNG 3: VÀO RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 3: Từ từ bấm sang Tab Rút Tiền...")
            driver.execute_script("""
                var items = document.querySelectorAll('span, div, p');
                var target = Array.from(items).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
                if(!target) target = document.querySelector('i.mb-1.block'); // Fallback icon của sếp
                
                if(target) { 
                    var elToClick = target.closest('li') || target.closest('a') || target;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            self.log_msg(t_name, "    + Đang nhâm nhi ngụm trà chờ trang Rút tiền load...")
            time.sleep(4) # CHỜ HẲN 4s ĐỂ GIAO DIỆN CHUYỂN TRANG MƯỢT MÀ

            # ================= CHẶNG 4: CÀI ĐẶT MÃ PIN =================
            self.log_msg(t_name, "▶ CHẶNG 4: Click Cài đặt Mã PIN...")
            driver.execute_script("""
                var alert = Array.from(document.querySelectorAll('span')).find(el => el.innerText.includes('Mật khẩu rút tiền chưa cài đặt'));
                if(alert) { 
                    var elToClick = alert.closest('a') || alert;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            time.sleep(2.5) # CHỜ 2.5s CHO FORM ĐIỀN PIN NẢY LÊN TỪ TỪ
            
            fast_react_fill('input[formcontrolname="newPassword"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[formcontrolname="confirm"]', data["Mã PIN"], "Mã PIN 2")
            
            driver.execute_script("""
                var btnGui = document.querySelector('span[translate="Account_Submit"]'); 
                if(btnGui) { btnGui.click(); if(btnGui.closest('button')) btnGui.closest('button').click(); }
            """)
            time.sleep(3) # CHỜ 3s XÁC NHẬN PIN

            # ================= CHẶNG 5: THÊM NGÂN HÀNG =================
            self.log_msg(t_name, "▶ CHẶNG 5: Thêm Ngân Hàng...")
            driver.execute_script("""var el = document.querySelector('span.mat-select-placeholder'); if(el) el.click();""")
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            target_text = "VIKKI BANK" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_react_fill('input[formcontrolname="filter"]', target_text, f"Tìm {target_text}")
            time.sleep(1.5)

            driver.execute_script(f"""
                var items = document.querySelectorAll('span.mat-option-text');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            # Lười thì để con Bot nó gánh vác sếp ơi =)))
            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Chi nhánh Random: {chi_nhanh}")
            fast_react_fill('input[formcontrolname="city"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[formcontrolname="account"]', data["STK"], "Số TK")

            self.log_msg(t_name, "  -> Cú click Gửi đi chốt hạ...")
            driver.execute_script("""
                var btnSubmit = document.querySelector('button.btn-submit span[translate="Common_Submit"]'); 
                if(btnSubmit) { btnSubmit.click(); if(btnSubmit.closest('button')) btnSubmit.closest('button').click(); }
            """)
            time.sleep(2.5)
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN NEW88 CHẬM RÃI MÀ CHẮC CÚ THÀNH CÔNG!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module new88: {e}")
            return False

    # [MODULE 7] - Code xử lý shbet (BẢN FINAL: CHỈ TẬP TRUNG OCR ĐỌC CAPTCHA CHUẨN)
    def auto_fill_shbet(self, driver, data, sdt, t_name, index):
        import time
        import random
        import ddddocr
        import re

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module shbet (Chế độ Slow Motion & Vượt Captcha AI)...")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            # ================= CHẶNG 1: DỌN RÁC & VÀO FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Dọn rác & Mở form Đăng Ký...")
            
            # Đóng quảng cáo 1
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1.5)
            
            # Đóng quảng cáo 2
            driver.execute_script("""var btnDong2 = document.querySelector('button[translate="Announcement_GotIt"]'); if(btnDong2) btnDong2.click();""")
            time.sleep(1.5)
            
            # Click nút Đăng ký mở form
            driver.execute_script("""
                var btnReg = document.querySelector('span[translate="Register_Register"]') || document.querySelector('a[routerlink="/Account/Register"]'); 
                if(btnReg) { btnReg.click(); if(btnReg.closest('button')) btnReg.closest('button').click(); }
            """)
            time.sleep(3) 

            # ================= CHẶNG 2: BƠM DỮ LIỆU ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 2: Bơm dữ liệu Form (Nửa trên)...")
            fast_react_fill('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            fast_react_fill('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[formcontrolname="name"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[formcontrolname="mobile"]', sdt, "Số điện thoại")

            # ================= CHẶNG 3: XỬ LÝ CAPTCHA BẰNG AI =================
            self.log_msg(t_name, "▶ CHẶNG 3: Cuộn trang & Vượt Captcha bằng AI...")
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            time.sleep(1.5)

            success_reg = False
            for attempt in range(5): 
                self.log_msg(t_name, f"    + [Vòng nộp Form {attempt+1}]: Xử lý Captcha...")
                
                captcha_text = ""
                for ocr_retry in range(4):
                    self.log_msg(t_name, "      - Click ô Captcha để load ảnh mới và chờ 3s...")
                    
                    # Bấm vào ô hoặc ảnh để làm mới Captcha
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) {
                            el.scrollIntoView({behavior: 'smooth', block: 'center'});
                            el.focus();
                            var img = el.parentElement.querySelector('img') || el.parentElement.parentElement.querySelector('img');
                            if(img) img.click();
                        }
                    """)
                    
                    time.sleep(3) 
                    
                    try:
                        img_element = driver.execute_script("""
                            var input = document.querySelector('input[formcontrolname="checkCode"]');
                            if(input) {
                                return input.parentElement.querySelector('img') || input.parentElement.parentElement.querySelector('img');
                            }
                            return null;
                        """)
                        
                        if img_element:
                            img_bytes = img_element.screenshot_as_png
                            ocr = ddddocr.DdddOcr(show_ad=False)
                            raw_text = ocr.classification(img_bytes)
                            
                            # Tẩy rửa các ký tự AI hay nhìn nhầm
                            clean_text = raw_text.lower().replace('o', '0').replace('q', '0').replace('l', '1').replace('i', '1').replace('z', '2').replace('s', '5').replace('b', '8').replace('g', '9')
                            temp_captcha = re.sub(r'\D', '', clean_text)
                            
                            if len(temp_captcha) == 4:
                                captcha_text = temp_captcha
                                self.log_msg(t_name, f"      🤖 AI đọc CHUẨN 4 SỐ: '{captcha_text}'")
                                break 
                            else:
                                self.log_msg(t_name, f"      ⚠️ AI đọc sai ('{raw_text}'). Đổi ảnh khác!")
                                driver.execute_script("""
                                    var el = document.querySelector('input[formcontrolname="checkCode"]');
                                    if(el) { el.value = ''; el.dispatchEvent(new Event('input')); }
                                """)
                                time.sleep(1)
                        else:
                            break
                    except Exception as e:
                        break

                if len(captcha_text) != 4:
                    self.log_msg(t_name, "❌ AI lú nặng. Xin phép hủy luồng để qua Acc khác.")
                    return False
                
                fast_react_fill('input[formcontrolname="checkCode"]', captcha_text, "Mã Captcha")

                self.log_msg(t_name, "  -> Bấm Đăng ký người dùng mới...")
                driver.execute_script("""
                    var btn = document.querySelector('span[translate="Login_RegisterBtn"]') || 
                              document.querySelector('span[translate="Register_Register"]') ||
                              Array.from(document.querySelectorAll('button')).find(el => el.innerText.trim().toUpperCase() === 'ĐĂNG KÝ NGAY');
                    if(btn) { btn.click(); if(btn.closest('button')) btn.closest('button').click(); }
                """)
                time.sleep(4)

                # Check xem nó có quăng lỗi sai Captcha không
                is_error = driver.execute_script("""
                    var btnConfirm = document.querySelector('button[translate="Common_Confirm"]');
                    if(btnConfirm) { btnConfirm.click(); return true; }
                    var toast = document.querySelector('.toast-message, .ng-trigger-flyInOut');
                    if(toast) return true;
                    return false;
                """)

                if is_error:
                    self.log_msg(t_name, "❌ Sai Captcha! Đã bấm xác nhận, làm lại chậm rãi...")
                    time.sleep(1.5)
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) { el.value = ''; el.dispatchEvent(new Event('input', {bubbles: true})); }
                    """)
                    time.sleep(1)
                    continue 

                # Check xem lọt vào trong chưa
                is_success = driver.execute_script("""
                    return document.querySelector('button[translate="Register_DepositImmediately"]') !== null || window.location.href.toLowerCase().includes('/home');
                """)
                if is_success:
                    self.log_msg(t_name, "✅ Đăng ký thành công! Đã lọt vào trong.")
                    success_reg = True
                    break

            if not success_reg:
                self.log_msg(t_name, "❌ Đăng ký 5 lần đều xịt! Tool xin phép hủy luồng.")
                return False

            # ================= CHẶNG 4: VÀO TRANG TRONG & DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 4: Vào trang trong & Dọn quảng cáo...")
            driver.execute_script("""var btn = document.querySelector('button[translate="Register_DepositImmediately"]'); if(btn) btn.click();""")
            time.sleep(4) 
            
            driver.execute_script("""
                var btnDong = document.querySelector('button[translate="Announcement_GotIt"]') || document.querySelector('button[translate="Common_Closed"]'); 
                if(btnDong) btnDong.click();
            """)
            time.sleep(2)

            # ================= CHẶNG 5: VÀO RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Từ từ bấm sang Tab Rút Tiền...")
            driver.execute_script("""
                var items = document.querySelectorAll('span, div, p');
                var target = Array.from(items).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
                if(target) { 
                    var elToClick = target.closest('li') || target.closest('a') || target;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            self.log_msg(t_name, "    + Đang nhâm nhi ngụm trà chờ trang Rút tiền load...")
            time.sleep(4.5) 

            # ================= CHẶNG 6: CÀI ĐẶT MÃ PIN =================
            self.log_msg(t_name, "▶ CHẶNG 6: Click Cài đặt Mã PIN...")
            driver.execute_script("""
                var alert = Array.from(document.querySelectorAll('span')).find(el => el.innerText.includes('Mật khẩu rút tiền chưa cài đặt'));
                if(alert) { 
                    var elToClick = alert.closest('a') || alert.closest('div') || alert;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            time.sleep(2.5) 
            
            fast_react_fill('input[formcontrolname="newPassword"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[formcontrolname="confirm"]', data["Mã PIN"], "Mã PIN 2")
            
            driver.execute_script("""
                var btnGui = document.querySelector('span[translate="Account_Submit"]'); 
                if(btnGui) { btnGui.click(); if(btnGui.closest('button')) btnGui.closest('button').click(); }
            """)
            time.sleep(3) 

            # ================= CHẶNG 7: THÊM NGÂN HÀNG =================
            self.log_msg(t_name, "▶ CHẶNG 7: Thêm Ngân Hàng...")
            driver.execute_script("""var el = document.querySelector('span.mat-select-placeholder'); if(el) el.click();""")
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            target_text = "VIKKI BANK" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_react_fill('input[formcontrolname="filter"]', target_text, f"Tìm {target_text}")
            time.sleep(1.5)

            driver.execute_script(f"""
                var items = document.querySelectorAll('span.mat-option-text');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Chi nhánh Random: {chi_nhanh}")
            fast_react_fill('input[formcontrolname="city"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[formcontrolname="account"]', data["STK"], "Số TK")

            self.log_msg(t_name, "  -> Cú click Gửi đi chốt hạ...")
            driver.execute_script("""
                var btnSubmit = document.querySelector('button.btn-submit span[translate="Common_Submit"]'); 
                if(btnSubmit) { btnSubmit.click(); if(btnSubmit.closest('button')) btnSubmit.closest('button').click(); }
            """)
            time.sleep(2.5)
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN SHBET MƯỢT MÀ THÀNH CÔNG!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module shbet: {e}")
            return False

    # [MODULE 8] - Code xử lý JUN88 (BẢN FULL OPTION - FIX NÚT THÊM NGÂN HÀNG)
    def auto_fill_jun88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module JUN88 (Bản Full - Dịch chuyển tức thời)...")

            # Tuyệt chiêu Click Dưỡng Sinh
            js_gentle_click = """
                function gentleClick(btn) {
                    if(btn) {
                        try { btn.scrollIntoView({behavior: 'smooth', block: 'center'}); } catch(e){}
                        setTimeout(function() {
                            try { btn.click(); } catch(e){}
                        }, 500); 
                    }
                }
            """

            # Khai báo hàm gõ phím chuẩn React + Kính Lúp
            def react_typing(selector, text, field_name, is_append=False):
                self.log_msg(t_name, f"    + Đang lạch cạch gõ: {field_name}")
                if not is_append:
                    driver.execute_script(f"""
                        var els = document.querySelectorAll('{selector}');
                        var el = Array.from(els).reverse().find(e => e.getBoundingClientRect().width > 0);
                        if(el) {{
                            el.focus();
                            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            if(setter) setter.call(el, '');
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    """)
                    time.sleep(0.3)

                for char in str(text):
                    driver.execute_script(f"""
                        var els = document.querySelectorAll('{selector}');
                        var el = Array.from(els).reverse().find(e => e.getBoundingClientRect().width > 0);
                        if(el) {{
                            el.focus();
                            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            if(setter) setter.call(el, el.value + '{char}');
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    """)
                    time.sleep(random.uniform(0.05, 0.15))
                
                driver.execute_script(f"""
                    var els = document.querySelectorAll('{selector}');
                    var el = Array.from(els).reverse().find(e => e.getBoundingClientRect().width > 0);
                    if(el) el.blur();
                """)
                time.sleep(0.5)

            # ================= CHẶNG 1: DỌN RÁC & FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Rình và Đóng Popup quảng cáo...")
            
            for _ in range(5):
                clicked = driver.execute_script("""
                    var btns = Array.from(document.querySelectorAll('button.nrc-button'));
                    var btnOK = btns.find(el => {
                        var txt = (el.innerText || el.textContent || "").trim().toUpperCase();
                        return txt === 'OK';
                    });
                    if(btnOK && btnOK.getBoundingClientRect().width > 0) {
                        btnOK.click();
                        return true;
                    }
                    return false;
                """)
                if clicked:
                    self.log_msg(t_name, "    + Đã đấm nút OK đóng Popup!")
                    time.sleep(1.5)
                    break
                time.sleep(1)

            self.log_msg(t_name, "▶ CHẶNG 2: Bơm dữ liệu Form Đăng Ký...")
            react_typing('#playerid', data["TK"], "Tài khoản")
            react_typing('#password', data["MK"], "Mật khẩu")
            react_typing('#firstname', data["Tên"], "Họ & tên")

            self.log_msg(t_name, "    + Đang bơm: Số điện thoại")
            driver.execute_script("""
                var els = document.querySelectorAll('input[type="tel"]'); 
                var tel = Array.from(els).reverse().find(e => e.getBoundingClientRect().width > 0);
                if(tel) tel.focus();
            """)
            time.sleep(0.3)
            react_typing('input[type="tel"]', sdt, "Số điện thoại", is_append=True)

            self.log_msg(t_name, "  -> Bấm Đăng Ký Phiên Bản 1...")
            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('button.nrc-button'));
                var btnReg = btns.find(el => (el.innerText || el.textContent).toUpperCase().includes('ĐĂNG KÝ PHIÊN BẢN'));
                if(btnReg) gentleClick(btnReg);
            """)
            time.sleep(3.5) 

            # ================= CHẶNG 3: CHỜ SẾP KÉO CAPTCHA & ĐĂNG NHẬP =================
            self.log_msg(t_name, "▶ CHẶNG 3: Chờ Sếp kéo Captcha và Load vào màn hình thành công...")
            self.log_msg(t_name, "🚨 Sếp thò tay kéo giùm em cái Captcha nhé! Có 60s...")
            
            passed = False
            for _ in range(60): 
                time.sleep(1)
                is_success = driver.execute_script("""
                    var txt = document.body.innerText || "";
                    if(txt.includes('Đăng Ký Thành Công') || txt.includes('Trang chủ')) return true;

                    var btns = Array.from(document.querySelectorAll('button, a, div'));
                    return btns.some(el => {
                        var t = (el.innerText || el.textContent || "").trim().toUpperCase();
                        return t === 'TRANG CHỦ' || t === 'TẢI XUỐNG';
                    });
                """)
                if is_success:
                    passed = True
                    break
                    
            if passed:
                self.log_msg(t_name, "🎉 TUYỆT VỜI SẾP ƠI! Đã qua ải. Bấm Trang Chủ vào thẳng Game...")
                driver.execute_script(js_gentle_click + """
                    var btns = Array.from(document.querySelectorAll('button, a, div, span'));
                    var btnTC = btns.find(el => {
                        var t = (el.innerText || el.textContent || "").trim().toUpperCase();
                        return t === 'TRANG CHỦ' && el.children.length === 0;
                    });
                    if(!btnTC) btnTC = document.querySelector('button.sec-btn'); 
                    if(btnTC) gentleClick(btnTC);
                """)
                time.sleep(4) 
            else:
                self.log_msg(t_name, "❌ Hết 60s chưa thấy nút Trang chủ. Tool xin phép hủy luồng!")
                return False

            # ================= CHẶNG 4: F5 DỌN RÁC & VÀO RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 4: F5 tẩy trần và Phi vào Rút tiền...")
            driver.refresh()
            self.log_msg(t_name, "    + Đang chờ web load lại sau khi F5...")
            time.sleep(5)

            driver.execute_script(js_gentle_click + """
                var btnRut = document.querySelector('img[src*="icon_withdrawal.png"]');
                gentleClick(btnRut);
            """)
            time.sleep(3)

            driver.execute_script(js_gentle_click + """
                var dontShow = document.querySelector('.dontshow');
                if(dontShow) gentleClick(dontShow);
            """)
            time.sleep(1.5)

            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('div.btn, button'));
                var btnXN = btns.find(el => (el.innerText || el.textContent).trim().toLowerCase() === 'rút tiền');
                if(btnXN) gentleClick(btnXN);
            """)
            time.sleep(2.5)

            # ================= CHẶNG 5: CÀI PIN RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Cài đặt Mã PIN rút tiền...")
            react_typing('#pin', data["Mã PIN"], "Mã PIN 1")
            react_typing('#confirmpin', data["Mã PIN"], "Mã PIN 2")
            react_typing('#password', data["MK"], "Mật khẩu game (để xác nhận)")
            
            self.log_msg(t_name, "  -> Bấm Xác Nhận Lưu PIN...")
            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('button.nrc-button.fill-player-info-btn'));
                var btnXN = btns.find(el => (el.innerText || el.textContent).includes('Xác Nhận'));
                if(btnXN) gentleClick(btnXN);
            """)
            time.sleep(3)

            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('button.pri-btn'));
                var btnDong = btns.find(el => (el.innerText || el.textContent).includes('Đóng') && el.getBoundingClientRect().width > 0);
                if(btnDong) gentleClick(btnDong);
            """)
            time.sleep(2)

            # ================= CHẶNG 6: DỊCH CHUYỂN TỨC THỜI VỀ ACCOUNT =================
            self.log_msg(t_name, "▶ CHẶNG 6: Dịch chuyển tức thời về trang Tài Khoản...")
            
            # Dùng JS chuyển thẳng URL sang /account
            driver.execute_script("window.location.href = '/account';")
            time.sleep(4) 

            self.log_msg(t_name, "    + Cuộn tìm và click 'Tài khoản rút tiền'...")
            driver.execute_script(js_gentle_click + """
                var items = document.querySelectorAll('span, div, p');
                var target = Array.from(items).find(el => el.innerText && el.innerText.trim().toLowerCase() === 'tài khoản rút tiền');
                if(!target) target = document.querySelector('div[data-item="withdrawalAccount"]');
                
                if(target) {
                    var clickTarget = target.closest('a') || target.closest('li') || target.closest('div.am-list-item') || target;
                    gentleClick(clickTarget);
                }
            """)
            time.sleep(3)

            # Check xem có thẻ cũ không (Acc đã add bank), nếu có thì bấm để nhảy vào trong
            driver.execute_script(js_gentle_click + """
                var card = document.querySelector('.card-img.DEBIT_CARD');
                if(card) gentleClick(card.closest('.card') || card);
            """)
            time.sleep(1.5)

            # ĐÃ FIX: Click Bạo Lực vào nút Thêm Ngân Hàng (+)
            self.log_msg(t_name, "    + Bấm Thêm Ngân Hàng (+)...")
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('button.nrc-button, button'));
                var btnThem = btns.find(el => (el.innerText || el.textContent).includes('Thêm ngân hàng'));
                if(btnThem) {
                    btnThem.click();
                    // Bồi thêm event click vật lý
                    btnThem.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                }
            """)
            time.sleep(2.5)

            # ================= CHẶNG 7: BƠM BANK VÀ CHỐT HẠ =================
            self.log_msg(t_name, "▶ CHẶNG 7: Bơm Form Ngân Hàng...")
            driver.execute_script(js_gentle_click + """
                var bankId = document.querySelector('#bankid');
                gentleClick(bankId);
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "Vikki" if bank_choice == "VIKKI BANK" else "TPBank"
            target_alt = "Vikki" if bank_choice == "VIKKI BANK" else "TPBank"

            react_typing('input.formik-input', search_keyword, "Tìm Ngân hàng")
            time.sleep(1.5)

            driver.execute_script(js_gentle_click + f"""
                var imgBank = document.querySelector('img[alt="{target_alt}"]');
                if(imgBank) gentleClick(imgBank.parentElement || imgBank);
            """)
            time.sleep(1.5)

            react_typing('#bankaccount', data["STK"], "Số tài khoản")
            react_typing('#password', data["MK"], "Mật khẩu game (Lần 2)")

            self.log_msg(t_name, "  -> Bấm OK Chốt Hạ...")
            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('button.nrc-button'));
                var btnOK = btns.find(el => (el.innerText || el.textContent).trim() === 'OK');
                if(btnOK) gentleClick(btnOK);
            """)
            time.sleep(3.5)

            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('button.pri-btn'));
                var btnDong = btns.find(el => (el.innerText || el.textContent).includes('Đóng') && el.getBoundingClientRect().width > 0);
                if(btnDong) gentleClick(btnDong);
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN JUN88 MƯỢT MÀ TỪ A TỚI Z!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module JUN88: {e}")
            return False

    # [MODULE 9] - Code xử lý QQ88 (BẢN CHẬM RÃI - FIX CLICK ĐÚP XÁC NHẬN)
    def auto_fill_qq88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module QQ88 (Chế độ Slow Motion ngâm nhi trà đá)...")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.8) # Bóp phanh chậm lại 0.8s mỗi nhịp gõ

            # ================= CHẶNG 1: DỌN RÁC & FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bấm Đồng Ý & Bơm form Đăng Ký...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)
            
            fast_react_fill('input[name="username"]', data["TK"], "Tài khoản")
            fast_react_fill('input[name="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[name="payeeName"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[name="mobileNum1"]', sdt, "Số điện thoại")
            
            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script("var btnReg = document.querySelector('button.submit-btn'); if(btnReg) btnReg.click();")
            time.sleep(4.5) # Chờ 4.5s cho web tạo tài khoản và chuyển trang

            # ================= CHẶNG 2: VÀO TRANG TRONG & DỌN 1 ĐỐNG RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 2: Vận công dọn rác quảng cáo Trang chủ...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)

            # Quét liên hoàn cước dọn sạch các thể loại Popup X
            for _ in range(3):
                driver.execute_script("""
                    try {
                        // Tắt nút X trên cùng
                        var btn1 = document.querySelector('.am-navbar-title.close-btn');
                        if(btn1) btn1.click();

                        // Tắt nút X dạng use SVG
                        var useEls = document.querySelectorAll('use');
                        useEls.forEach(function(use) {
                            var href = use.getAttribute('xlink:href');
                            if(href && (href.includes('close') || href.includes('cross'))) {
                                var svg = use.closest('svg');
                                if(svg) {
                                    try { svg.click(); } catch(e){}
                                    try { if(svg.parentElement) svg.parentElement.click(); } catch(e){}
                                }
                            }
                        });
                        
                        // Cứ thấy chữ Đóng hoặc Tắt là bấm
                        var btns = Array.from(document.querySelectorAll('span, div, button'));
                        var btnHuy = btns.find(el => el.innerText.trim() === 'Đóng' || el.innerText.trim() === 'Hủy');
                        if(btnHuy) btnHuy.click();
                    } catch(e) {}
                """)
                time.sleep(1.5)

            # ================= CHẶNG 3: VÀO RÚT TIỀN & THÊM BANK =================
            self.log_msg(t_name, "▶ CHẶNG 3: Tìm đường vào Rút Tiền...")
            driver.execute_script("""
                var btnRut = document.querySelector('img[src*="member-withdraw"]'); 
                if(btnRut) {
                    var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                    btnRut.dispatchEvent(ev);
                }
            """)
            time.sleep(3.5) # Chờ 3.5s load trang rút tiền

            self.log_msg(t_name, "▶ CHẶNG 4: Bấm Thêm Ngân Hàng (Dấu +)...")
            driver.execute_script("""
                var btnAdd = document.querySelector('svg.am-icon-bankadd_7c674007'); 
                if(!btnAdd) btnAdd = document.querySelector('.withdraw-bkadd'); // Fallback
                if(btnAdd) {
                    var target = btnAdd.closest('div') || btnAdd;
                    target.click();
                }
            """)
            time.sleep(2.5)

            # ================= CHẶNG 5: ĐIỀN THÔNG TIN BANK & PIN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Bơm thông tin Bank & Cài Mã PIN...")

            driver.execute_script("""
                var selBank = document.querySelector('div.inputBase'); 
                if(selBank) selBank.click();
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "VIKKI" if bank_choice == "VIKKI BANK" else "TPBank"
            target_text = "Vikki Digital Bank" if bank_choice == "VIKKI BANK" else "TPBANK"

            # Gõ vào ô tìm kiếm bank
            driver.execute_script(f"""
                var searchInput = document.querySelectorAll('input.inputBase')[0];
                if(searchInput) {{
                    searchInput.focus();
                    let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    if(setter) setter.call(searchInput, '{search_keyword}');
                    searchInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            """)
            time.sleep(1.5)

            # Click chọn Bank
            driver.execute_script(f"""
                var items = document.querySelectorAll('.am-list-content');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            fast_react_fill('input[name="bankCard"]', data["STK"], "Số tài khoản")

            # Mảng 12 tỉnh thành
            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Lấy Random Chi nhánh: {chi_nhanh}")
            fast_react_fill('input[name="customBankBranch"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[name="withdraw"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[name="withdrawT"]', data["Mã PIN"], "Mã PIN 2")
            
            self.log_msg(t_name, "    + Chờ 2s cho hệ thống nhận diện xong Mã PIN...")
            time.sleep(2) 

            # ================= CHẶNG 6: CHỐT XÁC NHẬN =================
            self.log_msg(t_name, "▶ CHẶNG 6: Bấm Xác Nhận chốt hạ (Mỗi nút ĐÚNG 1 HIT)...")

            # ĐÃ SỬA: Chỉ click ĐÚNG 1 LẦN duy nhất cho nút XÁC NHẬN MÀU XANH
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('span.am-button'));
                var btnXN = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận' || el.innerText.toLowerCase().includes('xác nhận'));
                if(btnXN) {
                    btnXN.click();
                }
            """)
            
            self.log_msg(t_name, "    + Chờ 3s cho popup xác nhận thứ 2 hiện lên...")
            time.sleep(3) 

            # ĐÃ SỬA: Chỉ click ĐÚNG 1 LẦN duy nhất cho nút XÁC NHẬN POPUP
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('a.am-modal-button'));
                var btnXN2 = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận' || el.innerText.toLowerCase().includes('xác nhận'));
                if(btnXN2) {
                    btnXN2.click();
                }
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN QQ88 CHẬM MÀ CHẮC THÀNH CÔNG RỰC RỠ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module QQ88: {e}")
            return False
    # [MODULE 10] - Code xử lý RR88 (BẢN CHẬM RÃI - CLONE CỦA QQ88/OPEN88)
    def auto_fill_rr88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module RR88 (Chế độ Slow Motion ngâm nhi trà đá)...")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.8) # Bóp phanh chậm lại 0.8s mỗi nhịp gõ

            # ================= CHẶNG 1: DỌN RÁC & FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bấm Đồng Ý & Bơm form Đăng Ký...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)
            
            fast_react_fill('input[name="username"]', data["TK"], "Tài khoản")
            fast_react_fill('input[name="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[name="payeeName"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[name="mobileNum1"]', sdt, "Số điện thoại")
            
            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script("var btnReg = document.querySelector('button.submit-btn'); if(btnReg) btnReg.click();")
            time.sleep(4.5) # Chờ 4.5s cho web tạo tài khoản và chuyển trang

            # ================= CHẶNG 2: VÀO TRANG TRONG & DỌN 1 ĐỐNG RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 2: Vận công dọn rác quảng cáo Trang chủ...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)

            # Quét liên hoàn cước dọn sạch các thể loại Popup X
            for _ in range(3):
                driver.execute_script("""
                    try {
                        // Tắt nút X trên cùng
                        var btn1 = document.querySelector('.am-navbar-title.close-btn');
                        if(btn1) btn1.click();

                        // Tắt nút X dạng use SVG
                        var useEls = document.querySelectorAll('use');
                        useEls.forEach(function(use) {
                            var href = use.getAttribute('xlink:href');
                            if(href && (href.includes('close') || href.includes('cross'))) {
                                var svg = use.closest('svg');
                                if(svg) {
                                    try { svg.click(); } catch(e){}
                                    try { if(svg.parentElement) svg.parentElement.click(); } catch(e){}
                                }
                            }
                        });
                        
                        // Cứ thấy chữ Đóng hoặc Tắt là bấm
                        var btns = Array.from(document.querySelectorAll('span, div, button'));
                        var btnHuy = btns.find(el => el.innerText.trim() === 'Đóng' || el.innerText.trim() === 'Hủy');
                        if(btnHuy) btnHuy.click();
                    } catch(e) {}
                """)
                time.sleep(1.5)

            # ================= CHẶNG 3: VÀO RÚT TIỀN & THÊM BANK =================
            self.log_msg(t_name, "▶ CHẶNG 3: Tìm đường vào Rút Tiền...")
            driver.execute_script("""
                var btnRut = document.querySelector('img[src*="withdraw"]'); // Đã gộp để nhận cả member-withdraw và mid-withdraw
                if(btnRut) {
                    var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                    btnRut.dispatchEvent(ev);
                }
            """)
            time.sleep(3.5) # Chờ 3.5s load trang rút tiền

            self.log_msg(t_name, "▶ CHẶNG 4: Bấm Thêm Ngân Hàng (Dấu +)...")
            driver.execute_script("""
                var btnAdd = document.querySelector('svg.am-icon-bankadd_7c674007'); 
                if(!btnAdd) btnAdd = document.querySelector('.withdraw-bkadd'); // Fallback
                if(btnAdd) {
                    var target = btnAdd.closest('div') || btnAdd;
                    target.click();
                }
            """)
            time.sleep(2.5)

            # ================= CHẶNG 5: ĐIỀN THÔNG TIN BANK & PIN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Bơm thông tin Bank & Cài Mã PIN...")

            driver.execute_script("""
                var selBank = document.querySelector('div.inputBase'); 
                if(selBank) selBank.click();
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "VIKKI" if bank_choice == "VIKKI BANK" else "TPBank"
            target_text = "Vikki Digital Bank" if bank_choice == "VIKKI BANK" else "TPBANK"

            # Gõ vào ô tìm kiếm bank
            driver.execute_script(f"""
                var searchInput = document.querySelectorAll('input.inputBase')[0];
                if(searchInput) {{
                    searchInput.focus();
                    let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    if(setter) setter.call(searchInput, '{search_keyword}');
                    searchInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            """)
            time.sleep(1.5)

            # Click chọn Bank
            driver.execute_script(f"""
                var items = document.querySelectorAll('.am-list-content');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            fast_react_fill('input[name="bankCard"]', data["STK"], "Số tài khoản")

            # Mảng 12 tỉnh thành cho sếp
            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Lấy Random Chi nhánh: {chi_nhanh}")
            fast_react_fill('input[name="customBankBranch"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[name="withdraw"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[name="withdrawT"]', data["Mã PIN"], "Mã PIN 2")
            
            self.log_msg(t_name, "    + Chờ 2s cho hệ thống nhận diện xong Mã PIN...")
            time.sleep(2) 

            # ================= CHẶNG 6: CHỐT XÁC NHẬN =================
            self.log_msg(t_name, "▶ CHẶNG 6: Bấm Xác Nhận chốt hạ (Mỗi nút ĐÚNG 1 HIT)...")

            # Lệnh Click duy nhất cho nút XÁC NHẬN (bất kể xanh đỏ tím vàng)
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('span.am-button'));
                var btnXN = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận' || el.innerText.toLowerCase().includes('xác nhận'));
                if(btnXN) {
                    btnXN.click();
                }
            """)
            
            self.log_msg(t_name, "    + Chờ 3s cho popup xác nhận thứ 2 hiện lên...")
            time.sleep(3) 

            # Lệnh Click duy nhất cho nút XÁC NHẬN POPUP
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('a.am-modal-button'));
                var btnXN2 = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận' || el.innerText.toLowerCase().includes('xác nhận'));
                if(btnXN2) {
                    btnXN2.click();
                }
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN RR88 CHẬM MÀ CHẮC THÀNH CÔNG RỰC RỠ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module RR88: {e}")
            return False

    # [MODULE 11] - Code xử lý XX88 (BẢN CHẬM RÃI - FIX SĐT 10 SỐ)
    def auto_fill_xx88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module XX88 (Chế độ Slow Motion ngâm nhi trà đá)...")

            # Tự động render SĐT đúng luật XX88 (Bắt đầu bằng 5 hoặc 9, tổng 10 số)
            sdt_xx88 = random.choice(['5', '9']) + "".join([str(random.randint(0, 9)) for _ in range(9)])
            self.log_msg(t_name, f"    + Tạo SĐT đúng luật XX88: {sdt_xx88}")

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.8) # Bóp phanh chậm lại 0.8s mỗi nhịp gõ

            # ================= CHẶNG 1: DỌN RÁC & FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bấm Đồng Ý & Bơm form Đăng Ký...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)
            
            fast_react_fill('input[name="username"]', data["TK"], "Tài khoản")
            fast_react_fill('input[name="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[name="payeeName"]', data["Tên"], "Họ & tên")
            # Bơm số điện thoại chuyên dụng của XX88
            fast_react_fill('input[name="mobileNum1"]', sdt_xx88, "Số điện thoại")
            
            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script("var btnReg = document.querySelector('button.submit-btn'); if(btnReg) btnReg.click();")
            
            # THEO LỆNH SẾP: Vào trang chủ đứng ngâm 6-7s cho popup hiện lên hết
            self.log_msg(t_name, "    + Chờ 6.5s cho web load xong hết 1 đống Popup...")
            time.sleep(6.5)

            # ================= CHẶNG 2: VÀO TRANG TRONG & DỌN 1 ĐỐNG RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 2: Vận công dọn rác quảng cáo Trang chủ...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)

            # Quét liên hoàn cước dọn sạch các thể loại Popup X
            for _ in range(3):
                driver.execute_script("""
                    try {
                        // Tắt nút X trên cùng
                        var btn1 = document.querySelector('.am-navbar-title.close-btn');
                        if(btn1) btn1.click();

                        // Tắt nút X dạng use SVG
                        var useEls = document.querySelectorAll('use');
                        useEls.forEach(function(use) {
                            var href = use.getAttribute('xlink:href');
                            if(href && (href.includes('close') || href.includes('cross'))) {
                                var svg = use.closest('svg');
                                if(svg) {
                                    try { svg.click(); } catch(e){}
                                    try { if(svg.parentElement) svg.parentElement.click(); } catch(e){}
                                }
                            }
                        });
                        
                        // Cứ thấy chữ Đóng hoặc Tắt là bấm
                        var btns = Array.from(document.querySelectorAll('span, div, button'));
                        var btnHuy = btns.find(el => el.innerText.trim() === 'Đóng' || el.innerText.trim() === 'Hủy');
                        if(btnHuy) btnHuy.click();
                    } catch(e) {}
                """)
                time.sleep(1.5)

            # ================= CHẶNG 3: VÀO RÚT TIỀN & THÊM BANK =================
            self.log_msg(t_name, "▶ CHẶNG 3: Tìm đường vào Rút Tiền...")
            driver.execute_script("""
                var btnRut = document.querySelector('img[src*="withdraw"]'); // Bao trọn các loại tên file ảnh Rút tiền
                if(btnRut) {
                    var ev = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                    btnRut.dispatchEvent(ev);
                }
            """)
            time.sleep(3.5) # Chờ 3.5s load trang rút tiền

            self.log_msg(t_name, "▶ CHẶNG 4: Bấm Thêm Ngân Hàng (Dấu +)...")
            driver.execute_script("""
                var btnAdd = document.querySelector('svg.am-icon-bankadd_7c674007'); 
                if(!btnAdd) btnAdd = document.querySelector('.withdraw-bkadd'); // Fallback
                if(btnAdd) {
                    var target = btnAdd.closest('div') || btnAdd;
                    target.click();
                }
            """)
            time.sleep(2.5)

            # ================= CHẶNG 5: ĐIỀN THÔNG TIN BANK & PIN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Bơm thông tin Bank & Cài Mã PIN...")

            driver.execute_script("""
                var selBank = document.querySelector('div.inputBase'); 
                if(selBank) selBank.click();
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "VIKKI" if bank_choice == "VIKKI BANK" else "TPBank"
            target_text = "Vikki Digital Bank" if bank_choice == "VIKKI BANK" else "TPBANK"

            # Gõ vào ô tìm kiếm bank
            driver.execute_script(f"""
                var searchInput = document.querySelectorAll('input.inputBase')[0];
                if(searchInput) {{
                    searchInput.focus();
                    let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    if(setter) setter.call(searchInput, '{search_keyword}');
                    searchInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            """)
            time.sleep(1.5)

            # Click chọn Bank
            driver.execute_script(f"""
                var items = document.querySelectorAll('.am-list-content');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            fast_react_fill('input[name="bankCard"]', data["STK"], "Số tài khoản")

            # Mảng 12 tỉnh thành cho sếp
            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Lấy Random Chi nhánh: {chi_nhanh}")
            fast_react_fill('input[name="customBankBranch"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[name="withdraw"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[name="withdrawT"]', data["Mã PIN"], "Mã PIN 2")
            
            self.log_msg(t_name, "    + Chờ 2s cho hệ thống nhận diện xong Mã PIN...")
            time.sleep(2) 

            # ================= CHẶNG 6: CHỐT XÁC NHẬN =================
            self.log_msg(t_name, "▶ CHẶNG 6: Bấm Xác Nhận chốt hạ (Mỗi nút ĐÚNG 1 HIT)...")

            # Lệnh Click duy nhất cho nút XÁC NHẬN
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('span.am-button'));
                var btnXN = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận' || el.innerText.toLowerCase().includes('xác nhận'));
                if(btnXN) {
                    btnXN.click();
                }
            """)
            
            self.log_msg(t_name, "    + Chờ 3.5s cho popup xác nhận thứ 2 hiện lên...")
            time.sleep(3.5) 

            # Lệnh Click duy nhất cho nút XÁC NHẬN POPUP
            driver.execute_script("""
                var btns = Array.from(document.querySelectorAll('a.am-modal-button'));
                var btnXN2 = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận' || el.innerText.toLowerCase().includes('xác nhận'));
                if(btnXN2) {
                    btnXN2.click();
                }
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN XX88 CHẬM MÀ CHẮC THÀNH CÔNG RỰC RỠ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module XX88: {e}")
            return False

    # [MODULE 12] - Code xử lý GG88 (BẢN FULL: FIX LỖI TÌM SAI CHỮ XÁC NHẬN)
    def auto_fill_gg88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module GG88 (Chế độ Phá giáp & Ưu tiên bàn phím mới)...")

            # Tuyệt chiêu vuốt chạm Mobile CẢI TIẾN
            js_touch_click = """
                function touchClick(btn) {
                    if(btn) {
                        try { btn.scrollIntoView({behavior: 'smooth', block: 'center'}); } catch(e){}
                        try { btn.click(); } catch(e){}
                        try { btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window })); } catch(e){}
                        try { btn.dispatchEvent(new Event('touchstart', { bubbles: true, cancelable: true })); } catch(e){}
                        try { btn.dispatchEvent(new Event('touchend', { bubbles: true, cancelable: true })); } catch(e){}
                    }
                }
            """

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang dán: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            def human_typing(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang gõ mổ cò: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{ el.focus(); el.value = ''; el.dispatchEvent(new Event('input')); }}
                """)
                time.sleep(0.3)
                for char in str(text):
                    driver.execute_script(f"""
                        var el = document.querySelector('{selector}');
                        if(el) {{ el.value += '{char}'; el.dispatchEvent(new Event('input', {{bubbles: true}})); }}
                    """)
                    time.sleep(random.uniform(0.05, 0.15)) 
                driver.execute_script(f"var el = document.querySelector('{selector}'); if(el) el.blur();")
                time.sleep(0.5)

            def go_ban_phim_ao_chuan(vong_lap):
                self.log_msg(t_name, f"    + Bắt đầu gõ mã PIN ảo ({vong_lap}): [1-1-2-2-1-1] ...")
                for digit in ['1', '1', '2', '2', '1', '1']:
                    driver.execute_script(js_touch_click + f"""
                        var keys = Array.from(document.querySelectorAll('.ui-number-keyboard-key'));
                        var targetKeys = keys.filter(k => k.innerText.trim() === '{digit}' && k.getBoundingClientRect().width > 0);
                        if(targetKeys.length > 0) {{
                            var keyBtn = targetKeys[targetKeys.length - 1];
                            touchClick(keyBtn);
                        }}
                    """)
                    time.sleep(0.8)

            # ================= CHẶNG 1: BƠM FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bơm form Đăng Ký...")
            
            fast_react_fill('input[data-input-name="account"]', data["TK"], "Tài khoản")
            fast_react_fill('input[data-input-name="userpass"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[data-input-name="phone"]', sdt, "Số điện thoại")
            human_typing('input[data-input-name="realName"]', data["Tên"], "Họ & tên (Gõ tay)")
            
            self.log_msg(t_name, "  -> Quét tìm và Vuốt Đăng Ký Ngay...")
            driver.execute_script(js_touch_click + """
                var els = Array.from(document.querySelectorAll('*'));
                var targets = els.filter(el => {
                    var txt = el.textContent || el.innerText;
                    return txt && txt.trim().toLowerCase() === 'đăng ký' && el.children.length === 0;
                });
                if(targets.length > 0) touchClick(targets[targets.length - 1]);
            """)
            
            self.log_msg(t_name, "    + Chờ 5s cho web load vào trang chủ...")
            time.sleep(5) 

            # ================= CHẶNG 2: DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 2: Vào trang trong & Dọn quảng cáo (Bấm X 3 lần)...")
            for _ in range(3):
                driver.execute_script(js_touch_click + """
                    var uses = document.querySelectorAll('use');
                    for(var i=0; i<uses.length; i++) {
                        var u = uses[i];
                        var href = u.getAttribute('xlink:href') || u.getAttribute('href');
                        if(href && href.includes('ui-close-059120')) {
                            var svg = u.closest('svg');
                            if(svg) {
                                touchClick(svg); 
                                if(svg.parentElement) touchClick(svg.parentElement); 
                            }
                        }
                    }
                """)
                time.sleep(2)

            # ================= CHẶNG 3: VÀO RÚT TIỀN & CÀI PIN ẢO =================
            self.log_msg(t_name, "▶ CHẶNG 3: Tìm đường vào Rút Tiền...")
            driver.execute_script(js_touch_click + """
                var btnRut = document.querySelector('img[alt="Rút Tiền"]') || document.querySelector('img[src*="icon_dt_1tx"]'); 
                touchClick(btnRut);
                if(btnRut && btnRut.parentElement) touchClick(btnRut.parentElement);
            """)
            time.sleep(3.5)

            self.log_msg(t_name, "▶ CHẶNG 4: Thiết lập Mã PIN (Virtual Keyboard)...")
            
            self.log_msg(t_name, "    + Bấm chọn hàng 1 (Cài đặt PIN)...")
            driver.execute_script(js_touch_click + """
                var items = document.querySelectorAll('li.ui-password-input__item');
                if(items.length > 0) touchClick(items[0]);
            """)
            self.log_msg(t_name, "    + Chờ 3s cho bàn phím ảo trồi lên...")
            time.sleep(3)
            go_ban_phim_ao_chuan("Cài đặt PIN")
            
            time.sleep(1.5) 
            
            self.log_msg(t_name, "    + Chuyển trỏ chuột bấm vào ô đầu tiên của Hàng 2 (Xác nhận PIN)...")
            driver.execute_script(js_touch_click + """
                var items = document.querySelectorAll('li.ui-password-input__item');
                if(items.length > 6) {
                    touchClick(items[6]); 
                } else {
                    var uls = document.querySelectorAll('ul.ui-password-input');
                    if(uls.length > 1) {
                        var firstBoxRow2 = uls[1].querySelector('li');
                        if(firstBoxRow2) touchClick(firstBoxRow2);
                    }
                }
            """)
            time.sleep(2)
            go_ban_phim_ao_chuan("Xác nhận PIN")

            # ĐÃ SỬA CHỮ NÀY: Tìm đúng chữ "XÁC NHẬN" thay vì "Tiếp theo"
            self.log_msg(t_name, "  -> Bấm nút Xác Nhận (Lưu mã PIN)...")
            driver.execute_script(js_touch_click + """
                var els = Array.from(document.querySelectorAll('*'));
                var targets = els.filter(el => {
                    var txt = el.textContent || el.innerText;
                    return txt && txt.trim().toLowerCase() === 'xác nhận' && el.children.length === 0;
                });
                if(targets.length > 0) touchClick(targets[targets.length - 1]);
            """)
            time.sleep(3.5)

            # ================= CHẶNG 5: THÊM NGÂN HÀNG & NHẬP PIN LẦN 2 =================
            self.log_msg(t_name, "▶ CHẶNG 5: Vào Menu Thêm Tài Khoản Ngân Hàng...")
            driver.execute_script(js_touch_click + """
                var btnAdd = document.querySelector('div[class*="addAccountInputBtn"]');
                touchClick(btnAdd);
            """)
            time.sleep(2.5)

            driver.execute_script(js_touch_click + """
                var btnThem = document.querySelector('span[class*="right-text"]');
                touchClick(btnThem);
                if(btnThem && btnThem.parentElement) touchClick(btnThem.parentElement);
            """)
            time.sleep(3.5)

            self.log_msg(t_name, "    + Yêu cầu Xác minh PIN: Gõ lại [1-1-2-2-1-1]...")
            driver.execute_script(js_touch_click + """
                var items = document.querySelectorAll('li.ui-password-input__item');
                if(items.length > 0) touchClick(items[0]);
            """)
            time.sleep(1.5)
            go_ban_phim_ao_chuan("Xác minh Add Bank")

            self.log_msg(t_name, "  -> Bấm nút Tiếp Theo (Vào Form Add Bank)...")
            driver.execute_script(js_touch_click + """
                var els = Array.from(document.querySelectorAll('*'));
                var targets = els.filter(el => {
                    var txt = el.textContent || el.innerText;
                    return txt && txt.trim().toLowerCase() === 'tiếp theo' && el.children.length === 0;
                });
                if(targets.length > 0) touchClick(targets[targets.length - 1]);
            """)
            time.sleep(3.5)

            # ================= CHẶNG 6: NHẬP THÔNG TIN BANK =================
            self.log_msg(t_name, "▶ CHẶNG 6: Bơm Số Tài Khoản và Chọn Bank...")
            
            fast_react_fill('input[placeholder*="số tài khoản ngân hàng"]', data["STK"], "Số TK Ngân hàng")

            driver.execute_script(js_touch_click + """
                var bankInput = document.querySelector('input[placeholder*="Chọn ngân hàng phát hành"]');
                touchClick(bankInput);
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "Vikki" if bank_choice == "VIKKI BANK" else "TPBank"

            fast_react_fill('input[placeholder*="Chọn ngân hàng phát hành"]', search_keyword, f"Tìm bank: {search_keyword}")
            time.sleep(1.5)

            driver.execute_script(js_touch_click + f"""
                var items = document.querySelectorAll('.ui-options__option-content');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{search_keyword.upper()}'));
                touchClick(target);
                if(target && target.parentElement) touchClick(target.parentElement);
            """)
            time.sleep(1.5)

            # ================= CHẶNG 7: XÁC NHẬN CHỐT HẠ =================
            self.log_msg(t_name, "  -> Bấm XÁC NHẬN chốt hạ Add Bank...")
            driver.execute_script(js_touch_click + """
                var els = Array.from(document.querySelectorAll('*'));
                var targets = els.filter(el => {
                    var txt = el.textContent || el.innerText;
                    return txt && txt.trim().toLowerCase() === 'xác nhận' && el.children.length === 0;
                });
                if(targets.length > 0) touchClick(targets[targets.length - 1]);
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN GG88 HOÀN HẢO TỪ A TỚI Z!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module GG88: {e}")
            return False

    # [MODULE 13] - Code xử lý MM88 (BẢN FINAL: FIX NÚT THÊM BANK RÚT TIỀN)
    def auto_fill_mm88(self, driver, data, sdt, t_name, index):
        import time
        import random

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module MM88 (Chế độ Người cao tuổi từ tốn)...")

            # Tuyệt chiêu Click Dưỡng Sinh
            js_gentle_click = """
                function gentleClick(btn) {
                    if(btn) {
                        try { btn.scrollIntoView({behavior: 'smooth', block: 'center'}); } catch(e){}
                        setTimeout(function() {
                            try { btn.click(); } catch(e){}
                        }, 500); 
                    }
                }
            """

            def fast_react_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang dán: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.8)

            # ================= CHẶNG 1: BƠM FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Bơm form Đăng Ký MM88...")
            
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(1.5)
            
            fast_react_fill('input[name="username"]', data["TK"], "Tài khoản")
            fast_react_fill('input[name="password"]', data["MK"], "Mật khẩu")
            fast_react_fill('input[name="payeeName"]', data["Tên"], "Họ & tên")
            fast_react_fill('input[name="mobileNum1"]', sdt, "Số điện thoại")
            
            self.log_msg(t_name, "  -> Bấm Đăng Ký Ngay...")
            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('button, span, div'));
                var btnReg = btns.find(el => el.innerText.trim().toLowerCase() === 'đăng ký' && el.children.length === 0);
                if(btnReg) gentleClick(btnReg);
                else {
                    var submitBtn = document.querySelector('button.submit-btn');
                    gentleClick(submitBtn);
                }
            """)
            
            self.log_msg(t_name, "    + Chờ 10s cho web load vào trang chủ...")
            time.sleep(10) 

            # ================= CHẶNG 2: DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 2: Dọn rác quảng cáo...")
            driver.execute_script("var btn = document.querySelector('button.bottom-btn--agree'); if(btn) btn.click();")
            time.sleep(2)

            for _ in range(2):
                driver.execute_script(js_gentle_click + """
                    var btnClose = document.querySelector('.am-navbar-title.close-btn');
                    if(btnClose) gentleClick(btnClose);

                    var uses = document.querySelectorAll('use');
                    for(var i=0; i<uses.length; i++) {
                        var href = uses[i].getAttribute('xlink:href') || '';
                        if(href.includes('deposit-close') || href.includes('close')) {
                            gentleClick(uses[i].closest('svg')); 
                        }
                    }
                """)
                time.sleep(2)

            # ================= CHẶNG 3: VÀO TÀI KHOẢN VÀ THÊM EMAIL =================
            self.log_msg(t_name, "▶ CHẶNG 3: Vào Tài Khoản -> Bảo Mật...")
            
            driver.execute_script(js_gentle_click + """
                var btnTk = document.querySelector('img[src*="footer-member"]');
                gentleClick(btnTk);
            """)
            time.sleep(3.5)

            self.log_msg(t_name, "    + Bấm nút: Bảo mật tài khoản...")
            driver.execute_script(js_gentle_click + """
                var btnBaoMat = document.querySelector('a.SECPRIV');
                if(!btnBaoMat) {
                    var spans = Array.from(document.querySelectorAll('span.main-text'));
                    var targetSpan = spans.find(s => s.innerText.trim().includes('Bảo mật tài khoản'));
                    if(targetSpan) btnBaoMat = targetSpan.closest('a');
                }
                gentleClick(btnBaoMat);
            """)
            time.sleep(2.5)

            self.log_msg(t_name, "  -> Vào mục Cá nhân...")
            driver.execute_script(js_gentle_click + """
                var els = Array.from(document.querySelectorAll('span.flex-list-text, p, div'));
                var target = els.find(el => el.innerText && el.innerText.trim() === 'Thông tin cá nhân');
                if(target) {
                    var rowContainer = target.closest('.am-list-content') || target;
                    gentleClick(rowContainer);
                }
            """)
            time.sleep(3)

            email_val = data["TK"] + "@gmail.com"
            fast_react_fill('input[name="email"]', email_val, f"Email ({email_val})")
            time.sleep(1)

            driver.execute_script(js_gentle_click + """
                var btnXN = document.querySelector('a.btn-success.am-button');
                gentleClick(btnXN);
            """)
            time.sleep(3)

            self.log_msg(t_name, "  -> Bấm Back 2 lần ra Trang Chủ...")
            for _ in range(2):
                driver.execute_script(js_gentle_click + """
                    var spans = Array.from(document.querySelectorAll('span.return_icon, .am-navbar-left'));
                    var visibleSpans = spans.filter(s => s.getBoundingClientRect().width > 0);
                    
                    if(visibleSpans.length > 0) {
                        gentleClick(visibleSpans[visibleSpans.length - 1]);
                    } else {
                        var uses = Array.from(document.querySelectorAll('use'));
                        var leftUses = uses.filter(u => (u.getAttribute('xlink:href') || '').includes('left') && u.getBoundingClientRect().width > 0);
                        if(leftUses.length > 0) {
                            var svg = leftUses[leftUses.length - 1].closest('svg');
                            if(svg) {
                                gentleClick(svg);
                                if(svg.parentElement) gentleClick(svg.parentElement);
                            }
                        }
                    }
                """)
                time.sleep(2.5)

            driver.execute_script(js_gentle_click + "var btn1 = document.querySelector('.am-navbar-title.close-btn'); if(btn1) gentleClick(btn1);")
            time.sleep(1.5)

            # ================= CHẶNG 4: VÀO RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 4: Vào Rút Tiền...")
            driver.execute_script(js_gentle_click + """
                var btnRut = document.querySelector('img[src*="withdraw"]');
                gentleClick(btnRut);
            """)
            time.sleep(4)

            # ĐÃ SỬA: Click chuẩn vào khung bọc nút Thêm Ngân Hàng (Dấu cộng)
            self.log_msg(t_name, "  -> Bấm dấu (+) Thêm Ngân Hàng...")
            driver.execute_script(js_gentle_click + """
                var btnAddDiv = document.querySelector('.withdraw-bkadd');
                if(btnAddDiv) {
                    gentleClick(btnAddDiv);
                } else {
                    // Dự phòng rủi ro nếu web đổi class
                    var uses = Array.from(document.querySelectorAll('use'));
                    var targetUses = uses.filter(u => (u.getAttribute('xlink:href') || '').includes('bankadd_7c674007') && u.getBoundingClientRect().width > 0);
                    if(targetUses.length > 0) {
                        var svg = targetUses[targetUses.length - 1].closest('svg');
                        if(svg && svg.parentElement) gentleClick(svg.parentElement);
                        else gentleClick(svg);
                    }
                }
            """)
            time.sleep(3.5)

            # ================= CHẶNG 5: THÊM BANK & MÃ PIN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Bơm Bank & PIN...")

            driver.execute_script(js_gentle_click + """
                var selBank = document.querySelector('div.inputBase'); 
                gentleClick(selBank);
            """)
            time.sleep(2)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            search_keyword = "Vikki" if bank_choice == "VIKKI BANK" else "TPBank"
            target_text = "Vikki Digital Bank" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_react_fill('input[placeholder="Tìm kiếm"]', search_keyword, f"Tìm bank: {search_keyword}")
            time.sleep(2)

            driver.execute_script(js_gentle_click + f"""
                var items = document.querySelectorAll('.am-list-content');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                gentleClick(target);
            """)
            time.sleep(2)

            fast_react_fill('input[name="bankCard"]', data["STK"], "Số TK")

            danh_sach_tinh = ["Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", "Hải Dương", "Nam Định"]
            chi_nhanh = random.choice(danh_sach_tinh)
            fast_react_fill('input[name="customBankBranch"]', chi_nhanh, "Chi nhánh")

            fast_react_fill('input[name="withdraw"]', data["Mã PIN"], "Mã PIN 1")
            fast_react_fill('input[name="withdrawT"]', data["Mã PIN"], "Mã PIN 2")
            time.sleep(2)

            # ================= CHẶNG 6: XÁC NHẬN CHỐT HẠ =================
            self.log_msg(t_name, "▶ CHẶNG 6: Bấm Xác Nhận chốt đơn...")

            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('span.am-button'));
                var btnXN = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận');
                gentleClick(btnXN);
            """)
            time.sleep(4) 

            driver.execute_script(js_gentle_click + """
                var btns = Array.from(document.querySelectorAll('a.am-modal-button'));
                var btnXN2 = btns.find(el => el.innerText.trim().toLowerCase() === 'xác nhận');
                gentleClick(btnXN2);
            """)

            self.log_msg(t_name, "🎉 TỔNG KẾT: MM88 ĐÃ CHỐT ĐƠN THÀNH CÔNG RỰC RỠ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module MM88: {e}")
            return False
    # [MODULE 14] - Code xử lý 88vv (BẢN KÉO FORM & VƯỢT CAPTCHA ANGULAR - FIX SPEED & THU LẠI 2 LẦN)
    def auto_fill_88vv(self, driver, data, sdt, t_name, index):
        import time
        import random
        import ddddocr
        import re

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module 88vv (Chế độ cuộn trang & Vượt Captcha)...")

            def fast_angular_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            # ================= CHẶNG 1: DỌN RÁC & VÀO FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Dọn rác & Mở form Đăng Ký...")
            
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1.5)
            
            driver.execute_script("""var btnDong2 = document.querySelector('button[translate="Announcement_GotIt"]'); if(btnDong2) btnDong2.click();""")
            time.sleep(1.5)
            
            driver.execute_script("""
                var btnReg = document.querySelector('a[routerlink="/Account/Register"]'); 
                if(btnReg) { btnReg.click(); } else {
                    var spanReg = document.querySelector('span[translate="Register_Register"]');
                    if(spanReg) spanReg.click();
                }
            """)
            time.sleep(3) 

            # ================= CHẶNG 2: BƠM DỮ LIỆU ĐĂNG KÝ NỬA TRÊN =================
            self.log_msg(t_name, "▶ CHẶNG 2: Bơm dữ liệu Form (Nửa trên)...")
            fast_angular_fill('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            fast_angular_fill('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            fast_angular_fill('input[formcontrolname="confirmPassword"]', data["MK"], "Xác nhận Mật khẩu")
            fast_angular_fill('input[formcontrolname="moneyPassword"]', data["Mã PIN"], "Mật khẩu rút tiền (PIN)")
            fast_angular_fill('input[formcontrolname="name"]', data["Tên"], "Họ & tên")

            # ================= CHẶNG 3: CUỘN TRANG & XỬ LÝ CAPTCHA =================
            self.log_msg(t_name, "▶ CHẶNG 3: Cuộn trang & Vượt Captcha...")
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            time.sleep(1.5)

            success_reg = False
            for attempt in range(5): 
                self.log_msg(t_name, f"    + [Vòng nộp Form {attempt+1}]: Xử lý Captcha...")
                
                captcha_text = ""
                for ocr_retry in range(4):
                    self.log_msg(t_name, "      - Click ô Captcha để load ảnh mới và chờ 4s...")
                    
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) {
                            el.scrollIntoView({behavior: 'smooth', block: 'center'});
                            el.click();
                            el.focus();
                            var img = el.parentElement.querySelector('img');
                            if(img) img.click();
                        }
                    """)
                    
                    time.sleep(4) 
                    
                    try:
                        img_element = driver.execute_script("""
                            var input = document.querySelector('input[formcontrolname="checkCode"]');
                            if(input) {
                                return input.parentElement.querySelector('img');
                            }
                            return null;
                        """)
                        
                        if img_element:
                            img_bytes = img_element.screenshot_as_png
                            ocr = ddddocr.DdddOcr(show_ad=False)
                            raw_text = ocr.classification(img_bytes)
                            
                            clean_text = raw_text.lower().replace('o', '0').replace('q', '0').replace('l', '1').replace('i', '1').replace('z', '2').replace('s', '5').replace('b', '8').replace('g', '9')
                            temp_captcha = re.sub(r'\D', '', clean_text)
                            
                            if len(temp_captcha) == 4:
                                captcha_text = temp_captcha
                                self.log_msg(t_name, f"      🤖 AI đọc CHUẨN 4 SỐ: '{captcha_text}'")
                                break 
                            else:
                                self.log_msg(t_name, f"      ⚠️ AI đọc sai ('{raw_text}'). Đổi ảnh khác!")
                                driver.execute_script("""
                                    var el = document.querySelector('input[formcontrolname="checkCode"]');
                                    if(el) { el.value = ''; el.dispatchEvent(new Event('input')); }
                                """)
                                time.sleep(1)
                        else:
                            break
                    except Exception as e:
                        break

                if len(captcha_text) != 4:
                    self.log_msg(t_name, "❌ AI lú nặng. Xin phép hủy luồng để qua Acc khác.")
                    return False
                
                fast_angular_fill('input[formcontrolname="checkCode"]', captcha_text, "Mã Captcha")

                self.log_msg(t_name, "  -> Bấm Đăng ký người dùng mới...")
                driver.execute_script("""
                    var btn = document.querySelector('span[translate="Login_RegisterBtn"]');
                    if(btn) { btn.click(); if(btn.closest('button')) btn.closest('button').click(); }
                """)
                time.sleep(4)

                is_error = driver.execute_script("""
                    var btnConfirm = document.querySelector('button[translate="Common_Confirm"]');
                    if(btnConfirm) { btnConfirm.click(); return true; }
                    var toast = document.querySelector('.toast-message, .ng-trigger-flyInOut');
                    if(toast) return true;
                    return false;
                """)

                if is_error:
                    self.log_msg(t_name, "❌ Sai Captcha! Đã bấm xác nhận, làm lại chậm rãi...")
                    time.sleep(1.5)
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) { el.value = ''; el.dispatchEvent(new Event('input', {bubbles: true})); }
                    """)
                    time.sleep(1)
                    continue 

                is_success = driver.execute_script("""
                    return document.querySelector('button[translate="Register_DepositImmediately"]') !== null;
                """)
                if is_success:
                    self.log_msg(t_name, "✅ Đăng ký thành công! Đã lọt vào trong.")
                    success_reg = True
                    break

            if not success_reg:
                self.log_msg(t_name, "❌ Đăng ký 5 lần đều xịt! Tool xin phép hủy luồng.")
                return False

            # ================= CHẶNG 4: VÀO TRANG TRONG & DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 4: Vào trang chủ & Dọn quảng cáo...")
            driver.execute_script("""var btn = document.querySelector('button[translate="Register_DepositImmediately"]'); if(btn) btn.click();""")
            time.sleep(4) 
            
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1.5) 
            
            driver.execute_script("""var btnDong2 = document.querySelector('button[translate="Announcement_GotIt"]'); if(btnDong2) btnDong2.click();""")
            time.sleep(1.5)

            # ================= CHẶNG 5: VÀO RÚT TIỀN & THU LẠI 2 LẦN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Bấm sang Tab Rút Tiền...")
            driver.execute_script("""
                var btnRut = document.querySelector('span[translate="Shared_Withdraw"]');
                if(btnRut) { 
                    var target = btnRut.closest('div') || btnRut;
                    target.click(); 
                }
            """)
            # ĐÃ GIẢM TỐC ĐỘ THEO LỆNH SẾP: Từ 4s xuống 2.5s
            time.sleep(2.5)

            self.log_msg(t_name, "    + Bấm Thu lại màn hình nhỏ (Lần 1)...")
            driver.execute_script("""
                var btnThu = document.querySelector('span[translate="Shared_Collapse"]');
                if(btnThu) {
                    var target = btnThu.closest('div') || btnThu.closest('.switch') || btnThu;
                    target.click();
                }
            """)
            time.sleep(1.5)

            self.log_msg(t_name, "    + Bấm Rút Tiền lần 2 (Menu ngang)...")
            driver.execute_script("""
                var spans = document.querySelectorAll('li span');
                var target = Array.from(spans).find(el => el.innerText && el.innerText.trim().toLowerCase() === 'rút tiền');
                if(target) {
                    var li = target.closest('li') || target;
                    li.click();
                }
            """)
            time.sleep(2)

            # ĐÃ THÊM: Click nút Thu Lại Lần 2 trước khi qua Add Bank
            self.log_msg(t_name, "    + Bấm Thu lại màn hình nhỏ (Lần 2)...")
            driver.execute_script("""
                var btnThu = document.querySelector('span[translate="Shared_Collapse"]');
                if(btnThu) {
                    var target = btnThu.closest('div') || btnThu.closest('.switch') || btnThu;
                    target.click();
                }
            """)
            time.sleep(1.5)

            # ================= CHẶNG 6: THÊM NGÂN HÀNG =================
            self.log_msg(t_name, "▶ CHẶNG 6: Thêm Ngân Hàng...")
            driver.execute_script("""
                var el = document.querySelector('span.mat-select-placeholder'); 
                if(el) el.click();
            """)
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            target_text = "VIKKI BANK" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_angular_fill('input[formcontrolname="filter"]', target_text, f"Tìm {target_text}")
            time.sleep(1.5)

            driver.execute_script(f"""
                var items = document.querySelectorAll('span.mat-option-text');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Chi nhánh Random: {chi_nhanh}")
            fast_angular_fill('input[formcontrolname="city"]', chi_nhanh, "Chi nhánh")

            fast_angular_fill('input[formcontrolname="account"]', data["STK"], "Số TK")

            self.log_msg(t_name, "  -> Cú click Gửi đi chốt hạ...")
            driver.execute_script("""
                var btnSubmit = document.querySelector('button.btn-submit span[translate="Common_Submit"]'); 
                if(btnSubmit) { btnSubmit.click(); if(btnSubmit.closest('button')) btnSubmit.closest('button').click(); }
            """)
            time.sleep(2.5)
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN 88vv THÀNH CÔNG RỰC RỠ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module 88vv: {e}")
            return False

    # [MODULE 15] - Code xử lý Hi88 (BẢN DIRECT LINK - BỎ CHECK PING, VÀO THẲNG VIỆC)
    def auto_fill_hi88(self, driver, data, sdt, t_name, index):
        import time
        import random
        import ddddocr
        import re

        try:
            self.log_msg(t_name, "🎯 Đang chạy Module Hi88 (Bản Direct Link & Vượt Captcha)...")

            def fast_angular_fill(selector, text, field_name):
                self.log_msg(t_name, f"    + Đang bơm: {field_name}")
                driver.execute_script(f"""
                    var el = document.querySelector('{selector}');
                    if(el) {{
                        el.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        if(setter) setter.call(el, '{text}');
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        el.blur();
                    }}
                """)
                time.sleep(0.5)

            # ĐÃ BỎ CHẶNG 0 CHỜ PING VÀ NHẢY TAB. PHI THẲNG VÀO CHẶNG 1!

            # ================= CHẶNG 1: DỌN RÁC & VÀO FORM ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 1: Dọn rác & Mở form Đăng Ký...")
            
            driver.execute_script("""var btnDong = document.querySelector('button[translate="Common_Closed"]'); if(btnDong) btnDong.click();""")
            time.sleep(1.5)
            
            driver.execute_script("""var btnDong2 = document.querySelector('button[translate="Announcement_GotIt"]'); if(btnDong2) btnDong2.click();""")
            time.sleep(1.5)
            
            driver.execute_script("""
                var btnReg = document.querySelector('a[translate="Register_Register"]') || document.querySelector('a[routerlink="/Account/Register"]'); 
                if(btnReg) { btnReg.click(); if(btnReg.closest('button')) btnReg.closest('button').click(); }
            """)
            time.sleep(3) 

            # ================= CHẶNG 2: BƠM DỮ LIỆU ĐĂNG KÝ =================
            self.log_msg(t_name, "▶ CHẶNG 2: Bơm dữ liệu Form Đăng Ký (Nửa trên)...")
            fast_angular_fill('input[formcontrolname="account"]', data["TK"], "Tài khoản")
            fast_angular_fill('input[formcontrolname="password"]', data["MK"], "Mật khẩu")
            fast_angular_fill('input[formcontrolname="name"]', data["Tên"], "Họ & tên")
            fast_angular_fill('input[formcontrolname="mobile"]', sdt, "Số điện thoại")

            # ================= CHẶNG 3: XỬ LÝ CAPTCHA BẰNG AI =================
            self.log_msg(t_name, "▶ CHẶNG 3: Cuộn trang & Vượt Captcha bằng AI...")
            driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            time.sleep(1.5)

            success_reg = False
            for attempt in range(5): 
                self.log_msg(t_name, f"    + [Vòng nộp Form {attempt+1}]: Xử lý Captcha...")
                
                captcha_text = ""
                for ocr_retry in range(4):
                    self.log_msg(t_name, "      - Click ô Captcha để load ảnh mới và chờ 3s...")
                    
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) {
                            el.scrollIntoView({behavior: 'smooth', block: 'center'});
                            el.focus();
                            var img = el.parentElement.querySelector('img') || el.parentElement.parentElement.querySelector('img');
                            if(img) img.click();
                        }
                    """)
                    time.sleep(3) 
                    
                    try:
                        img_element = driver.execute_script("""
                            var input = document.querySelector('input[formcontrolname="checkCode"]');
                            if(input) {
                                return input.parentElement.querySelector('img') || input.parentElement.parentElement.querySelector('img');
                            }
                            return null;
                        """)
                        
                        if img_element:
                            img_bytes = img_element.screenshot_as_png
                            ocr = ddddocr.DdddOcr(show_ad=False)
                            raw_text = ocr.classification(img_bytes)
                            
                            clean_text = raw_text.lower().replace('o', '0').replace('q', '0').replace('l', '1').replace('i', '1').replace('z', '2').replace('s', '5').replace('b', '8').replace('g', '9')
                            temp_captcha = re.sub(r'\D', '', clean_text)
                            
                            if len(temp_captcha) == 4:
                                captcha_text = temp_captcha
                                self.log_msg(t_name, f"      🤖 AI đọc CHUẨN 4 SỐ: '{captcha_text}'")
                                break 
                            else:
                                self.log_msg(t_name, f"      ⚠️ AI đọc sai ('{raw_text}'). Đổi ảnh khác!")
                                driver.execute_script("""
                                    var el = document.querySelector('input[formcontrolname="checkCode"]');
                                    if(el) { el.value = ''; el.dispatchEvent(new Event('input')); }
                                """)
                                time.sleep(1)
                        else:
                            break
                    except Exception as e:
                        break

                if len(captcha_text) != 4:
                    self.log_msg(t_name, "❌ AI lú nặng. Xin phép hủy luồng để qua Acc khác.")
                    return False
                
                fast_angular_fill('input[formcontrolname="checkCode"]', captcha_text, "Mã Captcha")

                self.log_msg(t_name, "  -> Bấm Đăng ký người dùng mới...")
                driver.execute_script("""
                    var btn = document.querySelector('span[translate="Login_RegisterBtn"]'); 
                    if(btn) { btn.click(); if(btn.closest('button')) btn.closest('button').click(); }
                """)
                time.sleep(4)

                is_error = driver.execute_script("""
                    var btnConfirm = document.querySelector('button[translate="Common_Confirm"]');
                    if(btnConfirm) { btnConfirm.click(); return true; }
                    var toast = document.querySelector('.toast-message, .ng-trigger-flyInOut');
                    if(toast) return true;
                    return false;
                """)

                if is_error:
                    self.log_msg(t_name, "❌ Sai Captcha! Đã bấm xác nhận, làm lại chậm rãi...")
                    time.sleep(1.5)
                    driver.execute_script("""
                        var el = document.querySelector('input[formcontrolname="checkCode"]');
                        if(el) { el.value = ''; el.dispatchEvent(new Event('input', {bubbles: true})); }
                    """)
                    time.sleep(1)
                    continue 

                is_success = driver.execute_script("""
                    return document.querySelector('button[translate="Register_DepositImmediately"]') !== null || window.location.href.toLowerCase().includes('/home');
                """)
                if is_success:
                    self.log_msg(t_name, "✅ Đăng ký thành công! Đã lọt vào trong.")
                    success_reg = True
                    break

            if not success_reg:
                self.log_msg(t_name, "❌ Đăng ký 5 lần đều xịt! Tool xin phép hủy luồng.")
                return False

            # ================= CHẶNG 4: VÀO TRANG TRONG & DỌN RÁC =================
            self.log_msg(t_name, "▶ CHẶNG 4: Vào trang trong & Dọn quảng cáo...")
            driver.execute_script("""var btn = document.querySelector('button[translate="Register_DepositImmediately"]'); if(btn) btn.click();""")
            time.sleep(4) 
            
            driver.execute_script("""
                var btnDong = document.querySelector('button[translate="Announcement_GotIt"]') || document.querySelector('button[translate="Common_Closed"]'); 
                if(btnDong) btnDong.click();
            """)
            time.sleep(2)

            # ================= CHẶNG 5: VÀO RÚT TIỀN =================
            self.log_msg(t_name, "▶ CHẶNG 5: Từ từ bấm sang Tab Rút Tiền...")
            driver.execute_script("""
                var items = document.querySelectorAll('span.truncate, span.block');
                var target = Array.from(items).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
                if(target) { 
                    var elToClick = target.closest('li') || target.closest('a') || target;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            self.log_msg(t_name, "    + Đang nhâm nhi ngụm trà chờ trang Rút tiền load...")
            time.sleep(4.5) 

            # ================= CHẶNG 6: CÀI ĐẶT MÃ PIN =================
            self.log_msg(t_name, "▶ CHẶNG 6: Click Cài đặt Mã PIN...")
            driver.execute_script("""
                var alert = Array.from(document.querySelectorAll('span')).find(el => el.innerText.includes('Mật khẩu rút tiền chưa cài đặt'));
                if(alert) { 
                    var elToClick = alert.closest('a') || alert.closest('div') || alert;
                    var rect = elToClick.getBoundingClientRect();
                    var ev = new MouseEvent('click', { bubbles: true, cancelable: true, view: window, clientX: rect.left + 5, clientY: rect.top + 5 });
                    elToClick.dispatchEvent(ev);
                }
            """)
            time.sleep(2.5) 
            
            fast_angular_fill('input[formcontrolname="newPassword"]', data["Mã PIN"], "Mã PIN 1")
            fast_angular_fill('input[formcontrolname="confirm"]', data["Mã PIN"], "Mã PIN 2")
            
            driver.execute_script("""
                var btnGui = document.querySelector('span[translate="Account_Submit"]'); 
                if(btnGui) { btnGui.click(); if(btnGui.closest('button')) btnGui.closest('button').click(); }
            """)
            time.sleep(3) 

            # ================= CHẶNG 7: THÊM NGÂN HÀNG =================
            self.log_msg(t_name, "▶ CHẶNG 7: Thêm Ngân Hàng...")
            driver.execute_script("""var el = document.querySelector('span.mat-select-placeholder'); if(el) el.click();""")
            time.sleep(1.5)

            bank_choice = data.get("Ngân Hàng", "VIKKI BANK")
            target_text = "VIKKI BANK" if bank_choice == "VIKKI BANK" else "TPBANK"

            fast_angular_fill('input[formcontrolname="filter"]', target_text, f"Tìm {target_text}")
            time.sleep(1.5)

            driver.execute_script(f"""
                var items = document.querySelectorAll('span.mat-option-text');
                var target = Array.from(items).find(el => el.innerText.trim().toUpperCase().includes('{target_text.upper()}'));
                if(target) target.click();
            """)
            time.sleep(1.5)

            # Lấy list tỉnh thành
            danh_sach_tinh = [
                "Lai Châu", "Long An", "Thanh Hóa", "Hà Giang", "Yên Bái", 
                "Hải Dương", "Nam Định", "Hưng Yên", "Cao Bằng", "Đồng Nai", 
                "Hải Phòng", "Thái Nguyên"
            ]
            chi_nhanh = random.choice(danh_sach_tinh)
            self.log_msg(t_name, f"  + Chi nhánh Random: {chi_nhanh}")
            fast_angular_fill('input[formcontrolname="city"]', chi_nhanh, "Chi nhánh")

            fast_angular_fill('input[formcontrolname="account"]', data["STK"], "Số TK")

            self.log_msg(t_name, "  -> Cú click Gửi đi chốt hạ...")
            driver.execute_script("""
                var btnSubmit = document.querySelector('button.btn-submit span[translate="Common_Submit"]'); 
                if(btnSubmit) { btnSubmit.click(); if(btnSubmit.closest('button')) btnSubmit.closest('button').click(); }
            """)
            time.sleep(2.5)

            # Lệnh bồi thêm phát cuối của sếp
            self.log_msg(t_name, "  -> Bấm Rút Tiền lần nữa để hoàn thành quy trình...")
            driver.execute_script("""
                var items = document.querySelectorAll('li span.truncate, li span.block');
                var target = Array.from(items).find(el => el.innerText.trim().toLowerCase() === 'rút tiền');
                if(target) { 
                    var elToClick = target.closest('li') || target.closest('a') || target;
                    elToClick.click();
                }
            """)
            
            self.log_msg(t_name, "🎉 TỔNG KẾT: CHỐT ĐƠN HI88 SIÊU MƯỢT MÀ!")
            return True

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi Module Hi88: {e}")
            return False
            
    def update_counter_ui(self):
        txt = f"Đã check: {self.total_ips_checked} IP\nĐã dùng: {self.total_ips_used} IP"
        self.root.after(0, lambda: self.counter_label.configure(text=txt))

    def _load_default_bgs(self):
        default_items = [
            {"file": "img1.png", "x": -21, "y": 480, "size": 310, "angle": 0},
            {"file": "img2.png", "x": -29, "y": -19, "size": 130, "angle": 30},
            {"file": "img3.png", "x": 1100, "y": 616, "size": 350, "angle": 0}
        ]
        for item in default_items:
            try:
                bg = DraggableBackground(self.root, item["file"], x=item["x"], y=item["y"], size=item["size"])
                bg.angle = item.get("angle", 0)
                bg.update_image()
                bg.lock()
                if item["file"] == "img2.png":
                    try:
                        bg.label.lift(getattr(self, 'top_header_frame', None))
                    except:
                        try: bg.label.lift()
                        except: pass
                self.bg_images.append(bg)
            except: pass

    def toggle_main_adspower_app(self):
        try:
            CREATE_NO_WINDOW = 0x08000000
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq AdsPower*"', shell=True, creationflags=CREATE_NO_WINDOW).decode('utf-8', errors='ignore')
            is_running = "AdsPower" in output
            if is_running:
                self.log_msg("HỆ THỐNG", "Đang gửi lệnh ĐÓNG hoàn toàn app AdsPower...")
                subprocess.call('taskkill /F /IM "AdsPower Browser.exe" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                subprocess.call('taskkill /F /IM "AdsPower Global.exe" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
                self.btn_toggle_app.configure(text="🌸 Mở App AdsPower", fg_color="#A9DFBF", hover_color="#7DCEA0", text_color="#333333")
                self.log_msg("HỆ THỐNG", "✅ Đã đóng app AdsPower!")
            else:
                self.log_msg("HỆ THỐNG", "🚀 Đang gọi lệnh MỞ app AdsPower...")
                self.auto_start_adspower(is_auto=False)
                self.btn_toggle_app.configure(text="Đóng App AdsPower", fg_color="#F5B7B1", hover_color="#F1948A", text_color="#333333")
        except Exception as e:
            self.log_msg("HỆ THỐNG", f"⚠️ Lỗi nút Đóng/Mở app: {str(e)}")

    def auto_start_adspower(self, is_auto=True):
        try:
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            ads_paths = [
                os.path.join(local_appdata, r"Programs\AdsPower Global\AdsPower Global.exe"),
                os.path.join(local_appdata, r"Programs\AdsPower Browser\AdsPower Browser.exe"),
                r"C:\Program Files (x86)\AdsPower Global\AdsPower Global.exe",
                r"C:\Program Files\AdsPower Global\AdsPower Global.exe",
                r"C:\Program Files (x86)\AdsPower Browser\AdsPower Browser.exe",
                r"C:\Program Files\AdsPower Browser\AdsPower Browser.exe",
                os.path.join(os.environ.get('APPDATA', ''), r"AdsPower Global\AdsPower Global.exe")
            ]
            opened = False
            for path in ads_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    if is_auto: self.log_msg("HỆ THỐNG", f"🚀 Đã tự động kích hoạt AdsPower Browser!")
                    else: self.log_msg("HỆ THỐNG", f"🚀 Đã mở AdsPower Browser thủ công!")
                    opened = True
                    break
            if not opened: self.log_msg("HỆ THỐNG", "⚠️ Không tìm thấy file chạy AdsPower. Vui lòng mở thủ công!")
        except Exception as e: self.log_msg("HỆ THỐNG", f"⚠️ Lỗi khởi động AdsPower: {str(e)}")

    def load_config(self):
        self.sheet_sync_url = ""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("ads_api"): self.ads_api_entry.delete(0, 'end'); self.ads_api_entry.insert(0, data["ads_api"])
                    if data.get("ads_secret"): self.ads_secret_entry.insert(0, data["ads_secret"])
                    if data.get("blacklist"): self.blacklist_entry.delete(0, 'end'); self.blacklist_entry.insert(0, data["blacklist"])
                    
                    self.tele_token = data.get("tele_token", "")
                    self.tele_chat_id = data.get("tele_chat_id", "")
                    self.sheet_sync_url = data.get("sheet_sync_url", "")

                    if data.get("fproxy_keys"):
                        for i, key in enumerate(data["fproxy_keys"]):
                            if i < 5: self.threads_data[i]["entry"].insert(0, key)
                    if data.get("fproxy_prefixes"):
                        for i, prefix in enumerate(data["fproxy_prefixes"]):
                            if i < 5: self.threads_data[i]["prefix_menu"].set(prefix)
                            
                    if data.get("saved_profiles"):
                        for i, prof in enumerate(data["saved_profiles"]):
                            if i < 5 and prof.get("profile_id"):
                                self.threads_data[i]["profile_id"] = prof["profile_id"]
                                self.threads_data[i]["current_ip"] = prof["ip"]
                                self.set_thread_state(i, "DONE")
                                self.update_info(i, f"{prof['ip']} | Đã lưu", "#3CB371")
            except Exception as e:
                self.log_msg("HỆ THỐNG", f"⚠️ Lỗi đọc config: {e}")

    def on_closing(self):
        self.log_msg("HỆ THỐNG", "🛑 Đang dọn dẹp các tiến trình ngầm trước khi thoát...")
        for thread in self.threads_data:
            thread["is_running"] = False
        self.root.after(1000, self.root.destroy)

    def save_config(self):
        with self.config_lock:
            keys = [thread["entry"].get().strip() for thread in self.threads_data]
            prefixes = [thread["prefix_menu"].get() for thread in self.threads_data]
            
            saved_profiles = []
            for thread in self.threads_data:
                saved_profiles.append({
                    "profile_id": thread["profile_id"],
                    "ip": thread["current_ip"]
                })
                
            data = {
                "ads_api": self.ads_api_entry.get().strip(),
                "ads_secret": self.ads_secret_entry.get().strip(),
                "blacklist": self.blacklist_entry.get().strip(),
                "tele_token": self.tele_token,
                "tele_chat_id": self.tele_chat_id,
                "sheet_sync_url": getattr(self, 'sheet_sync_url', ''),
                "fproxy_keys": keys, 
                "fproxy_prefixes": prefixes,
                "saved_profiles": saved_profiles 
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

    # =========================================================
    # SYNC GHI CHÚ → GOOGLE SHEET
    # =========================================================
    def sync_note_to_sheet(self, index, game_name, note_text, is_red):
        """Gửi dữ liệu note lên Google Sheet (chạy nền, không chặn UI)."""
        sync_url = getattr(self, 'sheet_sync_url', '').strip()
        if not sync_url:
            return  # Chưa cài URL thì bỏ qua

        thread_info = self.threads_data[index]
        ten = thread_info["reg_vars"].get("Tên", ctk.StringVar()).get().strip().upper()
        stk = thread_info["reg_vars"].get("STK", ctk.StringVar()).get().strip()

        if not ten or not stk:
            return  # Thiếu thông tin không sync

        payload = {
            "ten": ten,
            "stk": stk,
            "game": game_name.lower(),
            "note": note_text,
            "is_red": is_red,
            "gid": 330563007
        }

        def _do_sync():
            try:
                resp = requests.post(sync_url, json=payload, timeout=12)
                data = resp.json()
                if data.get("success"):
                    self.log_msg("Ụ THỐNG",
                        f"✅ Sheet sync OK: {ten} / {game_name} → dòng {data.get('row','?')} cột {data.get('col','?')}")
                else:
                    self.log_msg("Ụ THỐNG",
                        f"⚠️ Sheet sync: {data.get('message', 'Lỗi không xác định')}")
            except Exception as ex:
                self.log_msg("Ụ THỐNG", f"❌ Sheet sync lỗi kết nối: {ex}")

        threading.Thread(target=_do_sync, daemon=True).start()

    def open_tele_config(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Cấu hình Telegram Bot")
        dialog.geometry("450x260")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#F2E6E8")
        dialog.attributes("-topmost", True)
        dialog.grab_set() 
        try: dialog.iconbitmap(resource_path("chick.ico"))
        except: pass

        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (450 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (260 // 2)
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text="🤖 CẤU HÌNH NHẬN THÔNG BÁO", font=ctk.CTkFont(size=16, weight="bold"), text_color="#B85C7B").pack(pady=(20, 10))

        frame = ctk.CTkFrame(dialog, fg_color="#FAFAFA", border_width=1, border_color="#E0C8D0")
        frame.pack(padx=20, pady=5, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Bot Token:", text_color="#4A4A4A", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        token_entry = ctk.CTkEntry(frame, width=280, fg_color="#FFFFFF", text_color="#333333", placeholder_text="Ví dụ: 123456:ABC-DEF...")
        token_entry.grid(row=0, column=1, padx=(0, 10), pady=15)
        token_entry.insert(0, self.tele_token)

        ctk.CTkLabel(frame, text="Chat ID:", text_color="#4A4A4A", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=(0, 15), sticky="e")
        chatid_entry = ctk.CTkEntry(frame, width=280, fg_color="#FFFFFF", text_color="#333333", placeholder_text="Ví dụ: 123456789")
        chatid_entry.grid(row=1, column=1, padx=(0, 10), pady=(0, 15))
        chatid_entry.insert(0, self.tele_chat_id)

        def save_and_close():
            self.tele_token = token_entry.get().strip()
            self.tele_chat_id = chatid_entry.get().strip()
            self.save_config()
            dialog.destroy()
            self.log_msg("HỆ THỐNG", "✅ Đã lưu cấu hình thông báo Telegram!")

        btn_save = ctk.CTkButton(dialog, text="💾 Lưu Cấu Hình", fg_color="#32CD32", hover_color="#228B22", command=save_and_close)
        btn_save.pack(pady=15)

    def send_telegram_notification(self, index, prefix, check_count, elapsed_time, ip_profile, location, ads_location, profile_id, screenshot_path=None, lat=None, lon=None, error_msg=None):
        self.log_msg("HỆ THỐNG", f"🔄 Đang chuẩn bị gửi Telegram... Token len: {len(self.tele_token)}, ChatID len: {len(self.tele_chat_id)}")
        token = self.tele_token
        chat_id = self.tele_chat_id
        if not token or not chat_id:
            self.log_msg("HỆ THỐNG", "⚠️ Lỗi: Chưa cấu hình Telegram Token hoặc Chat ID!")
            return
        
        import html
        safe_location = html.escape(str(location)) if location else "Không xác định"
        safe_ip = html.escape(str(ip_profile)) if ip_profile else "Không xác định"
        safe_prefix = html.escape(str(prefix)) if prefix else "Không xác định"

        if error_msg:
            status_text = f"❌ <b>TẠO PROFILE THẤT BẠI!</b>\n⚠️ <i>{html.escape(str(error_msg))}</i>"
            header_icon = "⚠️"
        else:
            status_text = "✅ <b>TẠO PROFILE THÀNH CÔNG!</b>"
            header_icon = "🎉"

        msg = (
            f"{header_icon} <b>[AUTO ADSPOWER - KINIUU]</b> {header_icon}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{status_text}\n\n"
            f"🌐 <b>IP Chốt:</b> <code>{safe_ip}</code>\n"
            f"📍 <b>Khu vực trên web check:</b> <b>{safe_location}</b>\n\n"
            f"🎯 <b>Đầu IP Yêu Cầu:</b> <code>{safe_prefix}</code>\n"
            f"🔍 <b>Số IP Đã Quét:</b> <code>{check_count}</code> vòng\n"
            f"⏱ <b>Thời Gian Hoàn Thành:</b> <code>{elapsed_time}s</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧸 <i>System by Van Huy Studio</i>"
        )
        
        # Tạo nút bấm vào Google Maps nếu có tọa độ
        inline_btns = []
        if lat and lon:
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            inline_btns.append([{"text": "🗺 Xem trên Google Maps", "url": google_maps_url}])
            
        if not error_msg:
            inline_btns.append([{"text": "🗑 Xóa Profile", "callback_data": "ask_delete_profile"}])

        keyboard = {
            "inline_keyboard": inline_btns
        }
        
        try:
            if screenshot_path and os.path.exists(screenshot_path):
                url = f"https://api.telegram.org/bot{token}/sendPhoto"
                payload = {"chat_id": chat_id, "caption": msg, "parse_mode": "HTML", "reply_markup": json.dumps(keyboard)}
                with open(screenshot_path, "rb") as f:
                    res = self.tele_session.post(url, data=payload, files={"photo": f}, timeout=15).json()
                
                # FALLBACK: Nếu sendPhoto lỗi, tự động chuyển về sendMessage
                if not res.get("ok"):
                    self.log_msg("HỆ THỐNG", f"⚠️ Gửi ảnh lỗi ({res.get('description')}), đang thử gửi lại dạng Text...")
                    url_text = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload_text = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "reply_markup": keyboard}
                    res = self.tele_session.post(url_text, json=payload_text, timeout=5).json()
            else:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML", "reply_markup": keyboard}
                res = self.tele_session.post(url, json=payload, timeout=5).json()
            
            if res.get("ok"):
                msg_id = res["result"]["message_id"]
                if not error_msg and profile_id is not None:
                    self.tele_msg_mapping[msg_id] = {"profile_id": profile_id, "index": index}
                
                # --- CODE MỚI: GỬI BẢN ĐỒ TỌA ĐỘ VÀO TELEGRAM ---
                if lat and lon:
                    try:
                        loc_url = f"https://api.telegram.org/bot{token}/sendLocation"
                        loc_payload = {
                            "chat_id": chat_id,
                            "latitude": lat,
                            "longitude": lon,
                            "reply_to_message_id": msg_id # Reply trực tiếp vào tin nhắn báo cáo cho đẹp
                        }
                        self.tele_session.post(loc_url, json=loc_payload, timeout=5)
                    except Exception as e:
                        self.log_msg("HỆ THỐNG", f"⚠️ Không gửi được bản đồ: {e}")
                
                self.log_msg("HỆ THỐNG", f"✈️ Đã bắn thông báo lên Bot Telegram thành công!")
            else:
                self.log_msg("HỆ THỐNG", f"⚠️ Lỗi Telegram: {res.get('description', res)}")
        except Exception as e:
            self.log_msg("HỆ THỐNG", f"⚠️ Lỗi kết nối Telegram: {e}")

    def poll_telegram_updates(self):
        while True:
            token = self.tele_token
            if not token: 
                time.sleep(3)
                continue
            
            # Khởi tạo update_id lần đầu tiên bằng offset=-1 để bỏ qua tin nhắn/nút bấm cũ khi tool ngoại tuyến
            if self.last_update_id == 0:
                try:
                    url = f"https://api.telegram.org/bot{token}/getUpdates?offset=-1&limit=1&timeout=0"
                    res = self.tele_session.get(url, timeout=5).json()
                    if res.get("ok") and res.get("result"):
                        self.last_update_id = res["result"][0]["update_id"]
                except Exception as e:
                    self.log_msg("HỆ THỐNG", f"⚠️ Không thể khởi tạo Telegram Update ID (Bỏ qua tin cũ): {e}")

            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates?offset={self.last_update_id + 1}&timeout=10"
                res = self.tele_session.get(url, timeout=15).json()
                
                if res.get("ok") and res.get("result"):
                    for item in res["result"]:
                        self.last_update_id = item["update_id"]
                        
                        try:
                            if "callback_query" in item:
                                cb = item["callback_query"]
                                cb_id = cb["id"]
                                data = cb.get("data", "")
                                chat_id = cb["message"]["chat"]["id"]
                                msg_id = cb["message"]["message_id"]
                                
                                # Trả lời Callback Query ngay lập tức để tránh nút bị xoay tròn liên tục
                                def _answer_cb():
                                    try: self.tele_session.get(f"https://api.telegram.org/bot{token}/answerCallbackQuery?callback_query_id={cb_id}", timeout=5)
                                    except Exception as cb_err: self.log_msg("HỆ THỐNG", f"⚠️ Lỗi answerCallbackQuery: {cb_err}")
                                threading.Thread(target=_answer_cb, daemon=True).start()
                                
                                if data.startswith("start_std_") or data.startswith("start_one_"):
                                    parts = data.split("_")
                                    mode = parts[1]
                                    idx = int(parts[2])
                                    
                                    if mode == "std":
                                        self.log_msg("HỆ THỐNG", f"📲 Nhận lệnh TẠO PROFILE THƯỜNG từ xa cho Luồng {idx+1}")
                                        self.root.after(0, self.toggle_thread, idx, False)
                                    elif mode == "one":
                                        self.log_msg("HỆ THỐNG", f"📲 Nhận lệnh TẠO ONE PROFILE từ xa cho Luồng {idx+1}")
                                        self.root.after(0, self.toggle_thread, idx, True)
                                    
                                    mode_name = "Tạo profile ADS (Chuẩn)" if mode == "std" else "One Profile"
                                    edit_url = f"https://api.telegram.org/bot{token}/editMessageText"
                                    edit_payload = {
                                        "chat_id": chat_id, "message_id": msg_id,
                                        "text": f"✅ Đã nhận lệnh khởi động lại <b>Luồng {idx+1}</b> ở chế độ: <b>{mode_name}</b>!",
                                        "parse_mode": "HTML"
                                    }
                                    def _edit_msg():
                                        try: self.tele_session.post(edit_url, json=edit_payload, timeout=5)
                                        except Exception as e: self.log_msg("HỆ THỐNG", f"⚠️ Lỗi sửa tin nhắn: {e}")
                                    threading.Thread(target=_edit_msg, daemon=True).start()
                                    
                                elif data == "ask_delete_profile":
                                    edit_url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
                                    payload = {
                                        "chat_id": chat_id, "message_id": msg_id,
                                        "reply_markup": {
                                            "inline_keyboard": [
                                                [{"text": "⚠️ XÁC NHẬN XÓA?", "callback_data": "do_delete_profile"}],
                                                [{"text": "❌ KHÔNG, QUAY LẠI", "callback_data": "cancel_delete_profile"}]
                                            ]
                                        }
                                    }
                                    def _edit_msg():
                                        try: self.tele_session.post(edit_url, json=payload, timeout=5)
                                        except Exception as e: self.log_msg("HỆ THỐNG", f"⚠️ Lỗi sửa tin nhắn: {e}")
                                    threading.Thread(target=_edit_msg, daemon=True).start()
                                    
                                elif data == "cancel_delete_profile":
                                    edit_url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
                                    payload = {
                                        "chat_id": chat_id, "message_id": msg_id,
                                        "reply_markup": {
                                            "inline_keyboard": [
                                                [{"text": "🗑 Xóa Profile", "callback_data": "ask_delete_profile"}]
                                            ]
                                        }
                                    }
                                    def _edit_msg():
                                        try: self.tele_session.post(edit_url, json=payload, timeout=5)
                                        except Exception as e: self.log_msg("HỆ THỐNG", f"⚠️ Lỗi sửa tin nhắn: {e}")
                                    threading.Thread(target=_edit_msg, daemon=True).start()
                                    
                                elif data == "do_delete_profile":
                                    if msg_id in self.tele_msg_mapping:
                                        mapped_data = self.tele_msg_mapping[msg_id]
                                        profile_id = mapped_data["profile_id"]
                                        idx = mapped_data["index"]
                                        
                                        edit_url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
                                        def _edit_msg():
                                            try: self.tele_session.post(edit_url, json={"chat_id": chat_id, "message_id": msg_id, "reply_markup": {"inline_keyboard": []}}, timeout=5)
                                            except Exception as e: self.log_msg("HỆ THỐNG", f"⚠️ Lỗi sửa tin nhắn: {e}")
                                        threading.Thread(target=_edit_msg, daemon=True).start()
                                        
                                        self.log_msg("HỆ THỐNG", f"📲 Nhận lệnh XÓA TỪ XA qua nút bấm Telegram cho Profile: {profile_id}")
                                        threading.Thread(target=self._remote_delete_worker, args=(idx, profile_id, chat_id, msg_id), daemon=True).start()
                                        del self.tele_msg_mapping[msg_id]
                                continue

                            msg = item.get("message")
                            if not msg: continue
                            
                            text = msg.get("text", "").strip().lower()
                            reply_to = msg.get("reply_to_message")
                            chat_id = msg.get("chat", {}).get("id")
                        except Exception as item_err:
                            self.log_msg("HỆ THỐNG", f"⚠️ Lỗi xử lý sự kiện Telegram: {item_err}")
            except Exception as e:
                time.sleep(2)

    def _remote_delete_worker(self, index, profile_id, chat_id, reply_msg_id):
        self.start_delete_countdown(index)
        ads_api = self.ads_api_entry.get().strip()
        ads_secret = self.ads_secret_entry.get().strip()
        headers = {"Content-Type": "application/json"}
        if ads_secret: headers["api-key"] = ads_secret

        try:
            self.root.after(0, self.update_info, index, "🛑 [██░░░░░░] Đang đóng...", "#D96E66")
            self.log_msg("HỆ THỐNG", f"🚪 Đang ép đóng profile {profile_id} trước khi xóa...")
            
            if self.threads_data[index].get("is_browser_open", False):
                try: requests.get(f"{ads_api}/api/v1/browser/stop?user_id={profile_id}", timeout=2)
                except: pass
                self.root.after(0, self.update_info, index, "⏳ [█████░░░] Đang chờ...", "#D96E66")
                time.sleep(1) 
            
            self.root.after(0, self.update_info, index, "🗑️ [███████░] Đang xóa...", "#D96E66")
            res = requests.post(f"{ads_api}/api/v1/user/delete", headers=headers, json={"user_ids": [profile_id]}, timeout=10).json()
            if res.get("code") == 0:
                self.log_msg("HỆ THỐNG", f"✅ Đã dọn dẹp vĩnh viễn profile {profile_id} theo lệnh từ điện thoại!")
                self.root.after(0, self.update_info, index, "✅ Đã xóa!", "#3CB371")
            else:
                self.log_msg("HỆ THỐNG", f"⚠️ AdsPower báo lỗi: {res.get('msg')} -> Đã ÉP XÓA bóng ma khỏi Tool từ xa!")
                self.root.after(0, self.update_info, index, "⚠️ Lỗi API!", "#CD5C5C")
                
            if self.threads_data[index]["profile_id"] == profile_id:
                self.threads_data[index]["profile_id"] = None
                self.threads_data[index]["is_running"] = False
                self.threads_data[index]["current_ip"] = None
                self.threads_data[index]["is_browser_open"] = False

                def _do_clear_ui():
                    self.threads_data[index]["game_states"] = {} 
                    if "game_ui_elements" in self.threads_data[index]:
                        for item in self.threads_data[index]["game_ui_elements"]:
                            try: item["status_lbl"].configure(text="Chưa mở", text_color="#888888")
                            except: pass

                    # Xóa thông tin đã điền khi xóa từ xa qua Telegram
                    if "reg_vars" in self.threads_data[index]:
                        defaults = {"Tên": "", "SĐT": "Random", "STK": "", "TK": "", "MK": "", "Mã PIN": ""}
                        for key, var in self.threads_data[index]["reg_vars"].items():
                            try: var.set(defaults.get(key, ""))
                            except: pass

                    if "game_notes" in self.threads_data[index]:
                        for var in self.threads_data[index]["game_notes"].values():
                            try: var.set("")
                            except: pass

                    if "game_note_red" in self.threads_data[index]:
                        self.threads_data[index]["game_note_red"] = {}

                    # Đóng và hủy cửa sổ đăng ký nếu đang mở
                    old_win = self.threads_data[index].get("reg_win")
                    if old_win is not None:
                        try:
                            if old_win.winfo_exists(): old_win.destroy()
                        except: pass
                        self.threads_data[index]["reg_win"] = None

                    self.set_thread_state(index, "READY")
                    self.root.after(1500, lambda: self.update_info(index, "Proxy: Chờ...", "#D28F5A") if self.threads_data[index]["profile_id"] is None else None)

                self.root.after(0, _do_clear_ui)
                self.save_config()

            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "▶ Tạo profile ADS", "callback_data": f"start_std_{index}"},
                        {"text": "⚡ One Profile", "callback_data": f"start_one_{index}"}
                    ]
                ]
            }
            url = f"https://api.telegram.org/bot{self.tele_token}/sendMessage"
            
            if res.get("code") == 0:
                bot_text = f"✅ Báo cáo sếp: Đã chém đẹp Profile <code>{profile_id}</code>!\nSếp muốn <b>Luồng {index + 1}</b> chạy tiếp chế độ nào?"
            else:
                bot_text = f"⚠️ Lỗi AdsPower: {res.get('msg')} -> Đã ÉP XÓA khỏi Tool!\nSếp muốn <b>Luồng {index + 1}</b> chạy tiếp chế độ nào?"

            payload = {
                "chat_id": chat_id, 
                "text": bot_text, 
                "parse_mode": "HTML", 
                "reply_to_message_id": reply_msg_id,
                "reply_markup": keyboard
            }
            self.tele_session.post(url, json=payload, timeout=5)
                
        except Exception as e:
            self.log_msg("HỆ THỐNG", f"❌ Lỗi API AdsPower (Xóa từ xa): {e} -> Ép dọn bộ nhớ!")
            if self.threads_data[index]["profile_id"] == profile_id:
                self.threads_data[index]["profile_id"] = None
                self.threads_data[index]["is_running"] = False
                self.threads_data[index]["current_ip"] = None
                self.threads_data[index]["is_browser_open"] = False
                
                def _do_clear_err_ui():
                    if "reg_vars" in self.threads_data[index]:
                        defaults = {"Tên": "", "SĐT": "Random", "STK": "", "TK": "", "MK": "", "Mã PIN": ""}
                        for key, var in self.threads_data[index]["reg_vars"].items():
                            try: var.set(defaults.get(key, ""))
                            except: pass
                            
                    if "game_notes" in self.threads_data[index]:
                        for var in self.threads_data[index]["game_notes"].values():
                            try: var.set("")
                            except: pass
                            
                    if "game_note_red" in self.threads_data[index]:
                        self.threads_data[index]["game_note_red"] = {}

                    old_win = self.threads_data[index].get("reg_win")
                    if old_win is not None:
                        try:
                            if old_win.winfo_exists(): old_win.destroy()
                        except: pass
                        self.threads_data[index]["reg_win"] = None

                    self.set_thread_state(index, "READY")
                    self.root.after(1500, lambda: self.update_info(index, "Proxy: Chờ...", "#D28F5A") if self.threads_data[index]["profile_id"] is None else None)

                self.root.after(0, _do_clear_err_ui)
                self.save_config()
            
            self.tele_session.post(f"https://api.telegram.org/bot{self.tele_token}/sendMessage", json={"chat_id": chat_id, "text": f"❌ Lỗi kết nối API: {str(e)} -> Đã ép dọn tool!", "reply_to_message_id": reply_msg_id}, timeout=5)

    def copy_ip(self, index):
        ip = self.threads_data[index]["current_ip"]
        if ip:
            self.root.clipboard_clear(); self.root.clipboard_append(ip)
            self.log_msg(f"Luồng {index+1}", f"📋 Đã Copy IP thành công: {ip}")
        else: self.log_msg(f"Luồng {index+1}", "⚠️ Chưa có IP để copy!")

    def set_thread_state(self, index, state):
        btn = self.threads_data[index]["btn_start"]
        btn_one = self.threads_data[index]["btn_one_profile"]
        row_frame = self.threads_data[index]["row_frame"]
        btn_toggle = self.threads_data[index]["btn_toggle_browser"]
        btn_del = self.threads_data[index]["btn_del"]

        if state == "READY":
            btn.configure(text="▶ Tạo profile ADS", fg_color="#228B22", hover_color="#006400", text_color="#FFFFFF", state="normal")
            btn_one.configure(fg_color="#8A2BE2", hover_color="#4B0082", text_color="#FFFFFF", state="normal")
            row_frame.configure(border_color="#E0C8D0")
            btn_toggle.configure(fg_color="#E6A868", hover_color="#D69858") 
            btn_del.configure(fg_color="#D96E66", hover_color="#C95E56")
            if self.threads_data[index]["profile_id"] is None: btn_toggle.configure(text="Đóng, mở profile")
        elif state == "RUNNING":
            btn.configure(fg_color="#D96E66", hover_color="#C95E56", text_color="#FFFFFF", state="normal") 
            btn_one.configure(fg_color="#D3D3D3", hover_color="#C0C0C0", text_color="#555555", state="disabled") 
            btn_toggle.configure(fg_color="#E6A868", hover_color="#D69858") 
            btn_del.configure(fg_color="#D96E66", hover_color="#C95E56")   
        elif state == "DONE":
            btn.configure(text="✔ Đã tạo profile", fg_color="#C79BC7", hover_color="#C79BC7", text_color="#FFFFFF", state="disabled") 
            btn_one.configure(fg_color="#D3D3D3", hover_color="#C0C0C0", text_color="#555555", state="disabled") 
            row_frame.configure(border_color="#32CD32")
            btn_toggle.configure(fg_color="#E67E22", hover_color="#D35400") 
            btn_del.configure(fg_color="#E74C3C", hover_color="#C0392B")

    def update_info(self, index, text, color="#D28F5A"): self.threads_data[index]["lbl_info"].configure(text=text, text_color=color)
    def _update_countdown_ui(self, index, text): self.threads_data[index]["countdown_lbl"].configure(text=text)

    def start_delete_countdown(self, index):
        def _run():
            steps = [
                "🗑️ [█████] 5s",
                "🗑️ [████░] 4s",
                "🗑️ [███░░] 3s",
                "🗑️ [██░░░] 2s",
                "🗑️ [█░░░░] 1s",
            ]
            for step in steps:
                self.root.after(0, self._update_countdown_ui, index, step)
                time.sleep(1)
            self.root.after(0, self._update_countdown_ui, index, "")
        
        threading.Thread(target=_run, daemon=True).start()

    def animate_row(self, index, step=0):
        thread_info = self.threads_data[index]
        if not thread_info["is_running"]: return
        spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        thread_info["btn_start"].configure(text=f"⏳ Đang xử lý {spinners[step % len(spinners)]}")
        pulse_colors = ["#E0C8D0", "#DE96AF", "#FF69B4", "#DE96AF"]
        thread_info["row_frame"].configure(border_color=pulse_colors[step % len(pulse_colors)])
        self.root.after(120, self.animate_row, index, step + 1)

    def toggle_thread(self, index, bypass_checks=False):
        thread_info = self.threads_data[index]
        if thread_info["is_running"]:
            thread_info["is_running"] = False
            self.log_msg(f"Luồng {index+1}", "⚠️ Đã nhận lệnh DỪNG từ người dùng!")
            self.set_thread_state(index, "READY")
            self.update_info(index, "Đã dừng", "#CD5C5C")
            self._update_countdown_ui(index, "") 
        else:
            fproxy_key = thread_info["entry"].get().strip()
            if not fproxy_key: self.log_msg(f"Luồng {index+1}", "❌ API Key trống, không thể chạy!"); return
            
            self.save_config()
            thread_info["is_running"] = True
            thread_info["current_ip"] = None 
            self.set_thread_state(index, "RUNNING")

            thread_info["game_states"] = {} 
            if "game_ui_elements" in thread_info:
                for item in thread_info["game_ui_elements"]:
                    try: item["status_lbl"].configure(text="Chưa mở", text_color="#888888")
                    except: pass
            
            if bypass_checks: self.update_info(index, "Đang lấy IP nhanh...", "#8A2BE2")
            else: self.update_info(index, "Đang rình IP...", "#D28F5A")
                
            self.animate_row(index)
            threading.Thread(target=self.run_worker, args=(index, fproxy_key, bypass_checks), daemon=True).start()

    def toggle_browser(self, index): threading.Thread(target=self._toggle_browser_worker, args=(index,), daemon=True).start()

    def _toggle_browser_worker(self, index):
        thread_info = self.threads_data[index]
        profile_id = thread_info["profile_id"]
        t_name = f"Luồng {index+1}"
        if not profile_id:
            self.log_msg(t_name, "⚠️ Luồng này chưa tạo profile, không có trình duyệt để mở/đóng!"); return

        ads_api = self.ads_api_entry.get().strip()
        
        try:
            res_active = requests.get(f"{ads_api}/api/v1/browser/active?user_id={profile_id}", timeout=5).json()
            is_really_open = False
            
            if res_active.get("code") == 0 and res_active.get("data", {}).get("status") == "Active":
                is_really_open = True

            if is_really_open:
                self.log_msg(t_name, f"🚪 Đang gửi lệnh ĐÓNG cửa sổ trình duyệt...")
                try:
                    res = requests.get(f"{ads_api}/api/v1/browser/stop?user_id={profile_id}", timeout=3).json()
                    if res.get("code") == 0 or "not open" in str(res):
                        self.log_msg(t_name, "✅ Đã đóng cửa sổ trình duyệt thành công!")
                        thread_info["is_browser_open"] = False
                        self.root.after(0, lambda: thread_info["btn_toggle_browser"].configure(text="Mở profile"))
                    else:
                        self.log_msg(t_name, f"⚠️ Lỗi (Có thể cửa sổ đã tắt): {res.get('msg')}")
                        thread_info["is_browser_open"] = False
                        self.root.after(0, lambda: thread_info["btn_toggle_browser"].configure(text="Mở profile"))
                except requests.exceptions.ReadTimeout:
                    self.log_msg(t_name, "✅ Đã đóng cửa sổ trình duyệt thành công (Bỏ qua Timeout)!")
                    thread_info["is_browser_open"] = False
                    self.root.after(0, lambda: thread_info["btn_toggle_browser"].configure(text="Mở profile"))
            else:
                self.log_msg(t_name, f"🌐 Đang gửi lệnh MỞ cửa sổ trình duyệt...")
                res = requests.get(f"{ads_api}/api/v1/browser/start?user_id={profile_id}", timeout=10).json()
                if res.get("code") == 0:
                    self.log_msg(t_name, "✅ Đã mở trình duyệt thành công!")
                    thread_info["is_browser_open"] = True
                    self.root.after(0, lambda: thread_info["btn_toggle_browser"].configure(text="Đóng profile"))
                else:
                    self.log_msg(t_name, f"⚠️ Lỗi khởi động: {res.get('msg')}")

        except Exception as e:
            self.log_msg(t_name, f"❌ Lỗi API AdsPower: {str(e)}")

    def delete_profile(self, index): threading.Thread(target=self._delete_profile_worker, args=(index,), daemon=True).start()
    
    def _delete_profile_worker(self, index):
        profile_id = self.threads_data[index]["profile_id"]
        t_name = f"Luồng {index+1}"
        if not profile_id: 
            self.log_msg(t_name, "⚠️ Luồng này chưa tạo profile nào!")
            return

        self.start_delete_countdown(index)
        ads_api = self.ads_api_entry.get().strip()
        ads_secret = self.ads_secret_entry.get().strip()
        headers = {"Content-Type": "application/json"}
        if ads_secret: headers["api-key"] = ads_secret

        try:
            self.root.after(0, self.update_info, index, "🛑 [██░░░░░░] Đang đóng...", "#D96E66")
            self.log_msg(t_name, f"🗑️ Đang gửi lệnh xóa Profile ID: {profile_id}...")
            
            # Chỉ đóng trình duyệt và sleep nếu thực sự đang mở trình duyệt
            if self.threads_data[index].get("is_browser_open", False):
                try: requests.get(f"{ads_api}/api/v1/browser/stop?user_id={profile_id}", timeout=2)
                except: pass
                self.root.after(0, self.update_info, index, "⏳ [█████░░░] Đang chờ...", "#D96E66")
                time.sleep(1)

            self.root.after(0, self.update_info, index, "🗑️ [███████░] Đang xóa...", "#D96E66")
            res = requests.post(f"{ads_api}/api/v1/user/delete", headers=headers, json={"user_ids": [profile_id]}, timeout=10).json()
            
            if res.get("code") == 0:
                self.log_msg(t_name, "✅ Đã xóa vĩnh viễn profile trên AdsPower!")
                self.root.after(0, self.update_info, index, "✅ Đã xóa!", "#3CB371")
            else: 
                self.log_msg(t_name, f"⚠️ AdsPower báo lỗi: {res.get('msg')} -> Đã ÉP XÓA bóng ma khỏi Tool!")
                self.root.after(0, self.update_info, index, "⚠️ Lỗi API!", "#CD5C5C")

            self.threads_data[index]["profile_id"] = None
            self.threads_data[index]["is_running"] = False 
            self.threads_data[index]["current_ip"] = None
            self.threads_data[index]["is_browser_open"] = False 
            
            self.threads_data[index]["game_states"] = {} 
            if "game_ui_elements" in self.threads_data[index]:
                for item in self.threads_data[index]["game_ui_elements"]:
                    try: item["status_lbl"].configure(text="Chưa mở", text_color="#888888")
                    except: pass

            # Xóa thông tin đã điền khi profile bị xóa
            if "reg_vars" in self.threads_data[index]:
                defaults = {"Tên": "", "SĐT": "Random", "STK": "", "TK": "", "MK": "", "Mã PIN": ""}
                for key, var in self.threads_data[index]["reg_vars"].items():
                    try: var.set(defaults.get(key, ""))
                    except: pass

            # Xóa tất cả ô ghi chú game
            if "game_notes" in self.threads_data[index]:
                for var in self.threads_data[index]["game_notes"].values():
                    try: var.set("")
                    except: pass

            # Reset trạng thái màu ghi chú
            if "game_note_red" in self.threads_data[index]:
                self.threads_data[index]["game_note_red"] = {}

            # Đóng và hủy cửa sổ đăng ký để lần sau tạo profile mới sẽ tạo cửa sổ mới
            old_win = self.threads_data[index].get("reg_win")
            if old_win is not None:
                try:
                    if old_win.winfo_exists(): old_win.destroy()
                except: pass
                self.threads_data[index]["reg_win"] = None

            self.save_config()
            self.set_thread_state(index, "READY") 
            self.root.after(1500, lambda: self.update_info(index, "Proxy: Chờ...", "#D28F5A") if self.threads_data[index]["profile_id"] is None else None)
        except Exception as e: 
            self.log_msg(t_name, f"❌ Lỗi kết nối API: {str(e)} -> Ép dọn bộ nhớ!")
            self.threads_data[index]["profile_id"] = None
            self.threads_data[index]["is_running"] = False 
            self.threads_data[index]["current_ip"] = None
            self.threads_data[index]["is_browser_open"] = False 

            # Xóa thông tin đã điền khi profile bị ép xóa
            if "reg_vars" in self.threads_data[index]:
                defaults = {"Tên": "", "SĐT": "Random", "STK": "", "TK": "", "MK": "", "Mã PIN": ""}
                for key, var in self.threads_data[index]["reg_vars"].items():
                    try: var.set(defaults.get(key, ""))
                    except: pass

            if "game_notes" in self.threads_data[index]:
                for var in self.threads_data[index]["game_notes"].values():
                    try: var.set("")
                    except: pass

            if "game_note_red" in self.threads_data[index]:
                self.threads_data[index]["game_note_red"] = {}

            # Đóng cửa sổ đăng ký nếu đang mở
            old_win = self.threads_data[index].get("reg_win")
            if old_win is not None:
                try:
                    if old_win.winfo_exists(): old_win.destroy()
                except: pass
                self.threads_data[index]["reg_win"] = None

            self.save_config()
            self.set_thread_state(index, "READY")
            self.root.after(1500, lambda: self.update_info(index, "Proxy: Chờ...", "#D28F5A") if self.threads_data[index]["profile_id"] is None else None)

    def run_worker(self, index, fproxy_key, bypass_checks=False):
        t_name = f"Luồng {index+1}"
        ads_api = self.ads_api_entry.get().strip()
        ads_secret = self.ads_secret_entry.get().strip()
        
        raw_blacklist = self.blacklist_entry.get().split(',')
        blacklist = [remove_accents(t.strip().lower()) for t in raw_blacklist if t.strip()]

        if bypass_checks: self.log_msg(t_name, "⚡ CHẾ ĐỘ ONE PROFILE: Bắt đầu lấy IP trực tiếp...")
        else: self.log_msg(t_name, "⚙️ Bắt đầu tiến trình rình IP và tạo hồ sơ...")
            
        start_time = time.time()
        proxy_data = self.tim_ip_dep(index, t_name, fproxy_key, blacklist, bypass_checks)
        
        if proxy_data and self.threads_data[index]["is_running"]:
            browser_data = self.tao_va_mo_adspower(index, t_name, proxy_data, ads_api, ads_secret)
            if browser_data:
                ads_loc = self.check_location_via_proxy(t_name, proxy_data)
                
                # --- CHỤP ẢNH MÀN HÌNH MÀU XANH ---
                screenshot_path = None
                if isinstance(browser_data, dict):
                    try:
                        from selenium import webdriver
                        from selenium.webdriver.chrome.options import Options
                        from selenium.webdriver.chrome.service import Service
                        from PIL import Image
                        
                        driver_path = browser_data.get("webdriver")
                        ws_info = browser_data.get("ws", {})
                        debug_addr = ws_info.get("selenium")
                        
                        if driver_path and debug_addr:
                            chrome_options = Options()
                            chrome_options.add_experimental_option("debuggerAddress", debug_addr)
                            service = Service(executable_path=driver_path)
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                            
                            for handle in driver.window_handles:
                                driver.switch_to.window(handle)
                                if "start.adspower.net" in driver.current_url:
                                    break
                                    
                            # Đợi banner tải xong
                            time.sleep(1.5)
                            ss_file = f"temp_screenshot_{index}.png"
                            driver.save_screenshot(ss_file)
                            
                            try:
                                img = Image.open(ss_file)
                                # Cắt phần banner màu xanh (khoảng 350px từ trên xuống)
                                cropped = img.crop((0, 0, img.width, min(img.height, 350)))
                                cropped.save(ss_file)
                                screenshot_path = ss_file
                            except:
                                pass
                    except Exception as e:
                        self.log_msg(t_name, f"⚠️ Lỗi cắt ảnh: {e}")
                
                elapsed_time = int(time.time() - start_time)
                prefix_setup = self.threads_data[index]["prefix_menu"].get()
                
                self.send_telegram_notification(
                    index=index,
                    prefix=prefix_setup, 
                    check_count=proxy_data.get("check_count", 0), 
                    elapsed_time=elapsed_time,
                    ip_profile=proxy_data["ip"],
                    location=proxy_data.get("location", "Không xác định"),
                    ads_location=ads_loc,
                    profile_id=self.threads_data[index]["profile_id"],
                    screenshot_path=screenshot_path,
                    lat=proxy_data.get("lat"), # THÊM DÒNG NÀY
                    lon=proxy_data.get("lon")  # THÊM DÒNG NÀY
                )
                
                # Xóa ảnh tạm sau khi gửi
                if screenshot_path and os.path.exists(screenshot_path):
                    try: os.remove(screenshot_path)
                    except: pass
                
                self.threads_data[index]["is_running"] = False
                self.set_thread_state(index, "DONE")
            else:
                elapsed_time = int(time.time() - start_time)
                prefix_setup = self.threads_data[index]["prefix_menu"].get()
                self.send_telegram_notification(
                    index=index,
                    prefix=prefix_setup, 
                    check_count=proxy_data.get("check_count", 0), 
                    elapsed_time=elapsed_time,
                    ip_profile=proxy_data["ip"],
                    location=proxy_data.get("location", "Không xác định"),
                    ads_location="Không xác định",
                    profile_id=self.threads_data[index]["profile_id"],
                    screenshot_path=None,
                    lat=proxy_data.get("lat"),
                    lon=proxy_data.get("lon"),
                    error_msg="Lỗi AdsPower (thiếu quyền, lỗi mạng, hoặc lỗi API)"
                )
                self.threads_data[index]["is_running"] = False
                self.set_thread_state(index, "READY")
        else:
            self.threads_data[index]["is_running"] = False
            self.set_thread_state(index, "READY")

    def check_location_checkip(self, ip):
        lat, lon = None, None
        loc_str = "Không xác định"

        try:
            # 1. Cào tên Thành phố / Khu vực từ checkip.com.vn
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://checkip.com.vn/"}
            res = requests.get(f"https://checkip.com.vn/locator?host={ip}", headers=headers, timeout=10)
            if res.status_code == 200:
                html = res.text
                clean_html = re.sub(r'\s+', ' ', html)

                match_khu_vuc = re.search(r'<td[^>]*>\s*Khu vực\s*</td>\s*<td[^>]*>\s*([^<]+?)\s*</td>', clean_html, re.IGNORECASE)
                if match_khu_vuc:
                    loc = match_khu_vuc.group(1).strip()
                    if loc and loc not in ["-", "Unknown"]: loc_str = loc

                match_city = re.search(r'<td[^>]*>\s*Thành phố\s*</td>\s*<td[^>]*>\s*([^<]+?)\s*</td>', clean_html, re.IGNORECASE)
                if match_city:
                    loc_city = match_city.group(1).strip()
                    if loc_city and loc_city not in ["-", "Unknown"]: loc_str = loc_city

                # Cố gắng quét tọa độ trực tiếp trong HTML (nếu có)
                c_match = re.search(r'(2[0-4]|1[0-9]|[8-9])\.(\d{2,10})[^0-9a-zA-Z]+(10[2-9]|110)\.(\d{2,10})', html)
                if c_match:
                    lat = float(f"{c_match.group(1)}.{c_match.group(2)}")
                    lon = float(f"{c_match.group(3)}.{c_match.group(4)}")
        except: pass

        # 2. TUYỆT CHIÊU: Nếu có tên Thành phố mà không tìm thấy Tọa độ -> Tự động tra cứu Tọa độ chuẩn!
        if loc_str != "Không xác định" and (lat is None or lon is None):
            try:
                import urllib.parse
                safe_loc = urllib.parse.quote(loc_str)
                # Dùng API Bản đồ thế giới để lấy tọa độ chính xác của Thành phố đó
                geo_url = f"https://nominatim.openstreetmap.org/search?q={safe_loc}+Vietnam&format=json&limit=1"
                geo_headers = {"User-Agent": "KiniuuTool/1.0"}
                geo_res = requests.get(geo_url, headers=geo_headers, timeout=5).json()
                if geo_res and len(geo_res) > 0:
                    lat = float(geo_res[0]["lat"])
                    lon = float(geo_res[0]["lon"])
            except: pass

        # 3. Fallback dự phòng cuối cùng nếu mạng lỗi hoặc checkip sập
        if loc_str == "Không xác định" or lat is None or lon is None:
            try:
                res_api = requests.get(f"http://ip-api.com/json/{ip}?lang=vi", timeout=5).json()
                if res_api.get("status") == "success":
                    if lat is None: lat = res_api.get("lat")
                    if lon is None: lon = res_api.get("lon")
                    if loc_str == "Không xác định":
                        city = res_api.get("city", "")
                        region = res_api.get("regionName", "")
                        if city and region and city != region: loc_str = f"{city}, {region}".strip(", ")
                        else: loc_str = city or region or loc_str
            except: pass
            
        return loc_str, lat, lon

    def check_location_via_proxy(self, t_name, proxy_data):
        self.log_msg(t_name, "🔍 Đang đồng bộ vị trí hiển thị với server AdsPower...")
        try:
            proxy_url = f"http://{proxy_data['user']}:{proxy_data['pass']}@{proxy_data['ip']}:{proxy_data['port']}"
            proxies = {"http": proxy_url, "https": proxy_url}
            
            try:
                res = requests.get("http://ip-api.com/json/?lang=en", proxies=proxies, timeout=6).json()
                if res.get("status") == "success":
                    country = res.get("country", "")
                    region = remove_accents(res.get("regionName", "")).lower()
                    region = region.replace(" province", "").replace(" city", "").strip()
                    city = remove_accents(res.get("city", "")).lower()
                    city = city.replace(" city", "").replace(" province", "").strip()
                    return f"{country} / {region} / {city}"
            except: pass

            try:
                res = requests.get("http://ipwho.is/", proxies=proxies, timeout=6).json()
                if res.get("success"):
                    country = res.get("country", "")
                    region = remove_accents(res.get("region", "")).lower().replace(" province", "").replace(" city", "").strip()
                    city = remove_accents(res.get("city", "")).lower().replace(" city", "").replace(" province", "").strip()
                    return f"{country} / {region} / {city}"
            except: pass
            
        except Exception as e:
            pass
        return "Không load được thông tin"

    def tim_ip_dep(self, index, t_name, fproxy_key, blacklist, bypass_checks=False):
        last_known_ip = None 
        stuck_count = 0 
        local_check_count = 0
        
        while self.threads_data[index]["is_running"]:
            try:
                res_current = requests.get(f"https://fproxy.me/api/getcurrent?api_key={fproxy_key}", timeout=10).json()
                
                if res_current.get("success") == True:
                    ip = res_current["data"].get("ip")
                    port = res_current["data"].get("port")
                    
                    if not ip:
                        self.update_info(index, "Đang chờ IP mới...", "#D28F5A")
                        self.doi_ip_fproxy(index, t_name, fproxy_key, last_known_ip)
                        continue
                    
                    if ip == last_known_ip:
                        stuck_count += 1
                        if stuck_count > 10: 
                            self.log_msg(t_name, f"⚠️ IP kẹt quá lâu, ép tool tự gửi lại lệnh đổi mới!")
                            self.doi_ip_fproxy(index, t_name, fproxy_key, last_known_ip)
                            stuck_count = 0
                        else:
                            self.update_info(index, "Đang chờ FProxy xoay...", "#D28F5A")
                            time.sleep(3)
                        continue

                    last_known_ip = ip
                    stuck_count = 0 
                    local_check_count += 1
                    self.log_msg(t_name, f"⚡ Phát hiện IP FProxy: {ip}")

                    with self.ip_counter_lock:
                        self.total_ips_checked += 1
                        self.update_counter_ui()

                    real_loc, lat, lon = self.check_location_checkip(ip)
                    real_loc_norm = remove_accents(real_loc.lower())

                    if bypass_checks:
                        self.log_msg(t_name, f"✅ Đã lấy thẳng IP ({real_loc}) bỏ qua bộ lọc!")
                        self.update_info(index, f"{ip} | {real_loc}", "#8A2BE2")
                        self.threads_data[index]["current_ip"] = ip
                        with self.ip_counter_lock:
                            self.total_ips_used += 1
                            self.update_counter_ui()
                        return {"ip": ip, "port": port, "user": res_current["data"].get("user", ""), "pass": res_current["data"].get("pass", ""), "check_count": local_check_count, "location": real_loc, "lat": lat, "lon": lon}

                    selected_prefix = self.threads_data[index]["prefix_menu"].get()
                    if selected_prefix != "Tất cả":
                        valid_prefixes = [p.strip() for p in selected_prefix.split(",")]
                        if not any(ip.startswith(f"{p}.") for p in valid_prefixes):
                            self.update_info(index, f"Sai đầu IP, bỏ qua...", "#D28F5A")
                            self.log_msg(t_name, f"⚠️ Sai đầu IP (Cần {selected_prefix}) -> Bỏ qua")
                            self.doi_ip_fproxy(index, t_name, fproxy_key, ip)
                            continue
                    
                    self.update_info(index, f"Soi: {ip}...", "#D28F5A")
                    
                    if any(tinh in real_loc_norm for tinh in blacklist):
                        self.log_msg(t_name, f"❌ Dính Blacklist ({real_loc}) -> Bỏ qua")
                        self.doi_ip_fproxy(index, t_name, fproxy_key, ip)
                        continue
                    
                    if not self.check_smsbet(t_name, ip):
                        self.doi_ip_fproxy(index, t_name, fproxy_key, ip)
                        continue

                    self.log_msg(t_name, f"✅ CHỐT IP NGON Ở: {real_loc} - IP: {ip}")
                    self.update_info(index, f"{ip} | {real_loc}", "#3CB371")
                    self.threads_data[index]["current_ip"] = ip
                    
                    with self.ip_counter_lock:
                        self.total_ips_used += 1
                        self.update_counter_ui()
                        
                    return {"ip": ip, "port": port, "user": res_current["data"].get("user", ""), "pass": res_current["data"].get("pass", ""), "check_count": local_check_count, "location": real_loc, "lat": lat, "lon": lon}
                else: 
                    self.update_info(index, "Proxy đang xoay...", "#CD5C5C")
                    time.sleep(5)
            except Exception:
                 self.update_info(index, "Lỗi API FProxy...", "#CD5C5C")
                 time.sleep(5)
        return None

    def doi_ip_fproxy(self, index, t_name, fproxy_key, old_ip):
        while self.threads_data[index]["is_running"]:
            try:
                res_new = requests.get(f"https://fproxy.me/api/getnew?api_key={fproxy_key}", timeout=10).json()
                
                if res_new.get("success") == True:
                    wait_time = int(res_new["data"].get("waiting_time", 40))
                    self.log_msg(t_name, f"🔄 Đã gửi lệnh đổi IP. Chờ hệ thống xoay...")
                    
                    end_time = time.time() + wait_time
                    last_check_time = time.time()

                    while self.threads_data[index]["is_running"]:
                        current_time = time.time()
                        remaining = int(end_time - current_time)

                        if remaining <= 0:
                            break 

                        self.root.after(0, self._update_countdown_ui, index, f"🔄 {remaining}s")
                        self.root.after(0, self.update_info, index, "Đang xoay IP...", "#D28F5A")

                        if current_time - last_check_time >= 3 and old_ip is not None:
                            last_check_time = current_time
                            try:
                                check_res = requests.get(f"https://fproxy.me/api/getcurrent?api_key={fproxy_key}", timeout=2).json()
                                if check_res.get("success") == True:
                                    new_ip = check_res["data"].get("ip")
                                    if new_ip and new_ip != old_ip:
                                        self.root.after(0, self._update_countdown_ui, index, "")
                                        return 
                            except: pass
                        time.sleep(0.5) 
                    
                    self.root.after(0, self._update_countdown_ui, index, "")
                    return 
                    
                else:
                    msg = res_new.get("message", "")
                    wait_time = 15 
                    match = re.search(r'\d+', msg)
                    if match:
                        wait_time = int(match.group(0))
                    self.log_msg(t_name, f"⏳ Chờ chút nhé. Hệ thống đang làm mới và sẽ tự gửi lại lệnh sau {wait_time}s...")

                    end_time = time.time() + wait_time
                    while self.threads_data[index]["is_running"]:
                        current_time = time.time()
                        remaining = int(end_time - current_time)

                        if remaining <= 0:
                            break 

                        self.root.after(0, self._update_countdown_ui, index, f"⏳ {remaining}s")
                        self.root.after(0, self.update_info, index, "Đang làm mới...", "#CD5C5C")
                        time.sleep(0.5) 
                    
                    self.root.after(0, self._update_countdown_ui, index, "")
                    continue
                    
            except Exception as e: 
                time.sleep(3) 
        self.root.after(0, self._update_countdown_ui, index, "")

    def check_smsbet(self, t_name, ip):
        try:
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://bet.smsbet.top/"}
            check_url = f"https://bet.smsbet.top/check_ip.php?ip={ip}"
            res = requests.get(check_url, headers=headers, timeout=10)
            try: data = res.json()
            except ValueError: return True 
            
            status = data.get("status")
            if status == "exists":
                self.log_msg(t_name, f"🟢 SMSBet: BÁO XANH (Đã dùng) -> Bỏ qua")
                return False
            elif status == "not_exists":
                add_url = f"https://bet.smsbet.top/add_ip.php?ip={ip}"
                requests.get(add_url, headers=headers, timeout=5)
                return True
            else: return True
        except Exception: return True

    def tao_va_mo_adspower(self, index, t_name, proxy_data, ads_api, ads_secret):
        ip = proxy_data["ip"]
        self.log_msg(t_name, f"🚀 Bắn API AdsPower tạo hồ sơ với Proxy: {ip}...")
        
        headers = {"Content-Type": "application/json"}
        if ads_secret: headers["api-key"] = ads_secret

        payload = {
            "name": f"Profile_{ip}",
            "group_id": "0", 
            "user_proxy_config": {
                "proxy_soft": "other", "proxy_type": "http",
                "proxy_host": str(ip), "proxy_port": str(proxy_data["port"]),
                "proxy_user": str(proxy_data["user"]), "proxy_password": str(proxy_data["pass"])
            },
            "fingerprint_config": {
                "os": "android", "os_version": "12",
                "browser_kernel_config": {"version": "134", "type": "chrome"},
                "user_agent": "Mozilla/5.0 (Linux; Android 12; SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
                "ua_browser_version": "110", "resolution_type": "0",
                "resolution": "750x1334", "window_size_type": "0", "window_size": "750x1334",
                "webrtc": "forward", "canvas": "0", "webgl_image": "0"
            }
        }
        
        try:
            res_create = requests.post(f"{ads_api}/api/v1/user/create", headers=headers, json=payload, timeout=10).json()
            if res_create.get("code") == 0:
                profile_id = res_create["data"]["id"]
                self.threads_data[index]["profile_id"] = profile_id 
                
                self.save_config() 
                
                self.log_msg(t_name, f"✅ Đã tạo hồ sơ HOÀN HẢO! (ID: {profile_id})")
                self.log_msg(t_name, "🌐 Đang tự động bật trình duyệt...")
                res_start = requests.get(f"{ads_api}/api/v1/browser/start?user_id={profile_id}", headers=headers, timeout=10).json()
                if res_start.get("code") == 0:
                    self.log_msg(t_name, "🎉 Trình duyệt ĐÃ MỞ trên màn hình!")
                    self.threads_data[index]["is_browser_open"] = True 
                    self.threads_data[index]["btn_toggle_browser"].configure(text="Đóng profile") 
                    return res_start.get("data", True)
                else: 
                    self.log_msg(t_name, f"⚠️ Lỗi tự bật trình duyệt: {res_start.get('msg')}")
                    return True 
            else:
                self.log_msg(t_name, f"❌ Lỗi AdsPower: {res_create.get('msg')}")
                return False
        except Exception as e:
            self.log_msg(t_name, f"❌ Không kết nối được AdsPower: {str(e)}")
            return False

import importlib.util

def load_patched_gui():
    import shutil
    base_dir = get_real_app_dir()
    
    # Đảm bảo các file ảnh và config luôn có sẵn ở thư mục chạy
    for fname in ["img1.png", "img2.png", "img3.png", "bg_coordinates.json", "chick.ico"]:
        target_f = os.path.join(base_dir, fname)
        if not os.path.exists(target_f):
            src_f = resource_path(fname)
            if os.path.exists(src_f) and os.path.abspath(src_f) != os.path.abspath(target_f):
                try: shutil.copy2(src_f, target_f)
                except: pass

    patch_file = os.path.join(base_dir, "app_update.py")
    if not os.path.exists(patch_file) and os.path.exists("app_update.py"):
        patch_file = "app_update.py"
    if os.path.exists(patch_file):
        try:
            spec = importlib.util.spec_from_file_location("app_update", patch_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            patch_ver = getattr(mod, "CURRENT_VERSION", "0")
            # CHỈ NẠP BẢN PATCH NẾU NÓ THỰC SỰ MỚI HƠN BẢN HIỆN TẠI!
            if is_newer_version(patch_ver, CURRENT_VERSION):
                if hasattr(mod, "AutoAdsPowerGUI"):
                    return mod.AutoAdsPowerGUI
            else:
                # File patch cũ hơn hoặc bằng bản hiện tại -> Xóa bỏ để chạy code mới nhất của tool
                try: os.remove(patch_file)
                except: pass
        except Exception as e:
            print(f"[!] Lỗi nạp bản vá hot-update: {e}")
            try: os.remove(patch_file)
            except: pass
    return None

def start_main_app(app):
    app.attributes("-alpha", 0.0)
    PatchedGUI = load_patched_gui()
    if PatchedGUI:
        PatchedGUI(app)
    else:
        AutoAdsPowerGUI(app)
    SplashScreen(app)

if __name__ == "__main__":
    app = ctk.CTk()
    app.withdraw()
    login = LoginScreen(app)
    app.mainloop()