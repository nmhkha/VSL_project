# =============================================================================
# VSL Communicator - GUI (Frontend)
# =============================================================================
# Giao diện Tkinter với layout split-view (Video trên, Text dưới).
# Không chứa logic xử lý ảnh - chỉ hiển thị.
# =============================================================================

import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import cv2

from . import config

# Thử import pyttsx3 cho Text-to-Speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠ pyttsx3 chưa được cài đặt. Chức năng Đọc sẽ không hoạt động.")
    print("  Cài đặt: pip install pyttsx3")


class VSLGUI:
    """
    Giao diện người dùng cho VSL Communicator.
    
    Layout:
    - Phần trên (65%): Video feed với skeleton và prediction box
    - Phần dưới (35%): Text area lớn + các nút chức năng
    """
    
    def __init__(self, root: tk.Tk, backend):
        """
        Khởi tạo GUI.
        
        Args:
            root: Tkinter root window
            backend: VSLBackend instance
        """
        self.root = root
        self.backend = backend
        
        # Cấu hình cửa sổ
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.BG_DARK)
        self.root.minsize(800, 600)
        
        # Biến quản lý
        self.running = True
        self.sentence_tokens = []
        self.last_appended_token = ""
        
        # Text-to-Speech engine
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # Cấu hình giọng nói tiếng Việt nếu có
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'vi' in voice.id.lower() or 'vietnam' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            except Exception as e:
                print(f"⚠ Không thể khởi tạo TTS: {e}")
                self.tts_engine = None
        
        # Tạo giao diện
        self._create_ui()
        
        # Bind phím tắt
        self._bind_shortcuts()
        
        # Bắt đầu vòng lặp cập nhật
        self.update_frame()
    
    def _create_ui(self):
        """Tạo các thành phần giao diện."""
        # Sử dụng Grid layout cho toàn bộ window
        self.root.grid_rowconfigure(0, weight=config.VIDEO_PANEL_WEIGHT)
        self.root.grid_rowconfigure(1, weight=config.TEXT_PANEL_WEIGHT)
        self.root.grid_columnconfigure(0, weight=1)
        
        # =====================================================================
        # PHẦN TRÊN: Video Panel (65%)
        # =====================================================================
        self.video_frame = tk.Frame(self.root, bg=config.BG_DARK)
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Label hiển thị video
        self.video_label = tk.Label(self.video_frame, bg=config.BG_DARK)
        self.video_label.pack(expand=True, fill=tk.BOTH)
        
        # =====================================================================
        # PHẦN DƯỚI: Control Panel (35%)
        # =====================================================================
        self.control_frame = tk.Frame(self.root, bg=config.BG_PANEL)
        self.control_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Chia control panel thành 2 phần: Status + Text Area | Buttons
        self.control_frame.grid_rowconfigure(0, weight=0)  # Status bar
        self.control_frame.grid_rowconfigure(1, weight=1)  # Text area
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(1, weight=0)  # Buttons column
        
        # ----- Status Bar -----
        self.status_frame = tk.Frame(self.control_frame, bg=config.BG_PANEL)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Progress label
        self.status_label = tk.Label(
            self.status_frame,
            text="Giữ 3s: Chờ tay...",
            bg=config.BG_PANEL,
            fg=config.TEXT_SECONDARY,
            font=(config.STATUS_FONT_FAMILY, config.STATUS_FONT_SIZE, config.STATUS_FONT_WEIGHT)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar (canvas)
        self.progress_canvas = tk.Canvas(
            self.status_frame,
            width=200,
            height=20,
            bg=config.BG_DARK,
            highlightthickness=1,
            highlightbackground=config.TEXT_SECONDARY
        )
        self.progress_canvas.pack(side=tk.LEFT, padx=20)
        
        # ----- Text Area (Khung soạn thảo lớn) -----
        self.text_frame = tk.Frame(self.control_frame, bg=config.BG_TEXT)
        self.text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Scrollbar
        self.text_scrollbar = tk.Scrollbar(self.text_frame)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.text_area = tk.Text(
            self.text_frame,
            bg=config.BG_TEXT,
            fg=config.TEXT_PRIMARY,
            font=(config.TEXT_AREA_FONT_FAMILY, config.TEXT_AREA_FONT_SIZE, config.TEXT_AREA_FONT_WEIGHT),
            wrap=tk.WORD,
            insertbackground=config.TEXT_PRIMARY,  # Màu con trỏ
            selectbackground=config.TEXT_SECONDARY,
            selectforeground=config.BG_DARK,
            padx=15,
            pady=15,
            yscrollcommand=self.text_scrollbar.set
        )
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.text_scrollbar.config(command=self.text_area.yview)
        
        # ----- Buttons Panel -----
        self.buttons_frame = tk.Frame(self.control_frame, bg=config.BG_PANEL)
        self.buttons_frame.grid(row=1, column=1, sticky="ns", padx=10, pady=10)
        
        # Style cho buttons
        button_font = (config.BUTTON_FONT_FAMILY, config.BUTTON_FONT_SIZE, config.BUTTON_FONT_WEIGHT)
        button_config = {
            'width': config.BUTTON_WIDTH,
            'font': button_font,
            'bg': config.BUTTON_BG,
            'fg': config.BUTTON_FG,
            'activebackground': config.BUTTON_ACTIVE,
            'activeforeground': config.BUTTON_FG,
            'relief': tk.FLAT,
            'cursor': 'hand2'
        }
        
        # Nút Xóa
        self.clear_button = tk.Button(
            self.buttons_frame,
            text="🗑️ Xóa",
            command=self._on_clear,
            **button_config
        )
        self.clear_button.pack(pady=5, fill=tk.X)
        
        # Nút Đọc
        self.speak_button = tk.Button(
            self.buttons_frame,
            text="🔊 Đọc",
            command=self._on_speak,
            **button_config
        )
        self.speak_button.pack(pady=5, fill=tk.X)
        
        # Nút Khoảng trắng
        self.space_button = tk.Button(
            self.buttons_frame,
            text="⎵ Space",
            command=self._on_space,
            **button_config
        )
        self.space_button.pack(pady=5, fill=tk.X)
        
        # Nút Backspace
        self.backspace_button = tk.Button(
            self.buttons_frame,
            text="⌫ Xóa ký tự",
            command=self._on_backspace,
            **button_config
        )
        self.backspace_button.pack(pady=5, fill=tk.X)
        
        # Separator
        tk.Frame(self.buttons_frame, height=20, bg=config.BG_PANEL).pack()
        
        # Nút Cài đặt (placeholder)
        self.settings_button = tk.Button(
            self.buttons_frame,
            text="⚙️ Cài đặt",
            command=self._on_settings,
            **button_config
        )
        self.settings_button.pack(pady=5, fill=tk.X)
    
    def _bind_shortcuts(self):
        """Bind các phím tắt."""
        self.root.bind('q', lambda e: self.on_closing())
        self.root.bind('Q', lambda e: self.on_closing())
        self.root.bind('<Escape>', lambda e: self.on_closing())
        
        # Phím cách - thêm khoảng trắng (chỉ khi focus không ở text area)
        # self.root.bind('<space>', lambda e: self._on_space() if e.widget != self.text_area else None)
    
    def _on_clear(self):
        """Xử lý nút Xóa - xóa toàn bộ text."""
        self.text_area.delete("1.0", tk.END)
        self.sentence_tokens = []
        self.last_appended_token = ""
    
    def _on_speak(self):
        """Xử lý nút Đọc - đọc text trong text area."""
        text = self.text_area.get("1.0", tk.END).strip()
        
        if not text:
            return
        
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Lỗi TTS: {e}")
        else:
            print(f"TTS không khả dụng. Text: {text}")
    
    def _on_space(self):
        """Thêm khoảng trắng vào text area."""
        self.text_area.insert(tk.END, " ")
        self.sentence_tokens.append(" ")
        self.last_appended_token = " "
    
    def _on_backspace(self):
        """Xóa ký tự cuối cùng."""
        content = self.text_area.get("1.0", tk.END)
        if len(content) > 1:  # Có ký tự để xóa (không tính newline cuối)
            self.text_area.delete("end-2c", "end-1c")
            if self.sentence_tokens:
                self.sentence_tokens.pop()
    
    def _on_settings(self):
        """Mở cửa sổ cài đặt (placeholder)."""
        # Tạo dialog đơn giản
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Cài đặt")
        settings_window.geometry("400x300")
        settings_window.configure(bg=config.BG_PANEL)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        tk.Label(
            settings_window,
            text="⚙️ Cài đặt\n\n(Tính năng đang phát triển)",
            bg=config.BG_PANEL,
            fg=config.TEXT_PRIMARY,
            font=(config.STATUS_FONT_FAMILY, 16)
        ).pack(expand=True)
        
        tk.Button(
            settings_window,
            text="Đóng",
            command=settings_window.destroy,
            bg=config.BUTTON_BG,
            fg=config.BUTTON_FG,
            font=(config.BUTTON_FONT_FAMILY, 12)
        ).pack(pady=20)
    
    def _update_progress_bar(self, progress: float):
        """
        Cập nhật thanh tiến độ.
        
        Args:
            progress: Giá trị từ 0.0 đến 1.0
        """
        self.progress_canvas.delete("all")
        
        width = 200
        height = 20
        fill_width = int(width * progress)
        
        # Màu gradient từ vàng sang xanh lá khi đầy
        if progress < 1.0:
            color = config.TEXT_SECONDARY  # Vàng
        else:
            color = config.TEXT_ACCENT  # Xanh lá
        
        # Vẽ thanh tiến độ
        if fill_width > 0:
            self.progress_canvas.create_rectangle(
                0, 0, fill_width, height,
                fill=color, outline=""
            )
    
    def update_frame(self):
        """Cập nhật frame video và prediction."""
        if not self.running:
            return
        
        # Lấy frame từ backend
        frame, current_pred, confirmed_pred, hold_progress = self.backend.process_frame()
        
        if frame is not None:
            # Chuyển BGR sang RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Tính kích thước phù hợp với panel
            panel_height = self.video_label.winfo_height()
            panel_width = self.video_label.winfo_width()
            
            if panel_height > 10 and panel_width > 10:
                # Tính tỷ lệ khung hình
                aspect_ratio = frame.shape[1] / frame.shape[0]
                
                # Tính kích thước mới
                new_height = panel_height - 10
                new_width = int(new_height * aspect_ratio)
                
                if new_width > panel_width - 10:
                    new_width = panel_width - 10
                    new_height = int(new_width / aspect_ratio)
                
                frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            else:
                frame_resized = frame_rgb
            
            # Chuyển sang ImageTk
            image = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=image)
            
            self.video_label.configure(image=photo)
            self.video_label.image = photo  # Giữ reference
        
        # Cập nhật status label
        if current_pred:
            status_text = f"Giữ 3s: {current_pred}"
        else:
            status_text = "Giữ 3s: Chờ tay..."
        self.status_label.configure(text=status_text)
        
        # Cập nhật progress bar
        self._update_progress_bar(hold_progress)
        
        # Nếu có ký tự xác nhận mới, thêm vào text area
        if confirmed_pred and confirmed_pred != self.last_appended_token:
            self.text_area.insert(tk.END, confirmed_pred)
            self.sentence_tokens.append(confirmed_pred)
            self.last_appended_token = confirmed_pred
            
            # Reset confirmed trong backend để tránh thêm trùng
            self.backend.confirmed_prediction = ""
        
        # Lên lịch cập nhật tiếp theo
        self.root.after(config.FRAME_UPDATE_INTERVAL, self.update_frame)
    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ."""
        self.running = False
        self.backend.release()
        self.root.destroy()
