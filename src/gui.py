# =============================================================================
# VSL Communicator - GUI (Frontend)
# =============================================================================
# Giao diện Tkinter với layout split-view (Video trên, Text dưới).
# Tích hợp tính năng gợi ý từ tiếng Việt.
# =============================================================================

import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import cv2

from . import config
from .word_suggester import WordSuggester

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
    - Phần dưới (35%): Panel điều khiển (Status, Buffer, Suggestions, Text Area, Buttons)
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
        
        # Biến cho tính năng gợi ý từ
        self.current_buffer = ""  # Chuỗi ký tự đang gõ dở (vd: 'hoc')
        self.suggester = WordSuggester(config.WORDS_CSV_PATH)
        
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
        # Row 0: Control Panel (35%), Row 1: Video (65%)
        self.root.grid_rowconfigure(0, weight=config.TEXT_PANEL_WEIGHT, minsize=200)
        self.root.grid_rowconfigure(1, weight=config.VIDEO_PANEL_WEIGHT, minsize=400)
        self.root.grid_columnconfigure(0, weight=1)
        
        # =====================================================================
        # PHẦN DƯỚI: Video Panel (65%)
        # =====================================================================
        # DEBUG: Đổi màu nền thành đỏ để kiểm tra
        self.video_frame = tk.Frame(self.root, bg='red')
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Label hiển thị video
        self.video_label = tk.Label(self.video_frame, bg=config.BG_DARK)
        self.video_label.pack(expand=True, fill=tk.BOTH)
        
        # =====================================================================
        # PHẦN TRÊN: Control Panel (35%)
        # =====================================================================
        self.control_frame = tk.Frame(self.root, bg=config.BG_PANEL)
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Chia control panel:
        # Row 0: Status + Progress + Buffer
        # Row 1: Suggestion Buttons
        # Row 2: Text Area
        # Col 1: Function Buttons (Right side)
        
        self.control_frame.grid_rowconfigure(0, weight=0)  # Status Bar
        self.control_frame.grid_rowconfigure(1, weight=0)  # Suggestions
        self.control_frame.grid_rowconfigure(2, weight=1)  # Text Area
        self.control_frame.grid_columnconfigure(0, weight=1) # Main content
        self.control_frame.grid_columnconfigure(1, weight=0) # Side buttons
        
        # ----- Row 0: Status Bar & Buffer -----
        self.status_frame = tk.Frame(self.control_frame, bg=config.BG_PANEL)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Progress label
        self.status_label = tk.Label(
            self.status_frame,
            text="Giữ 3s: ...",
            bg=config.BG_PANEL,
            fg=config.TEXT_SECONDARY,
            font=(config.STATUS_FONT_FAMILY, config.STATUS_FONT_SIZE, config.STATUS_FONT_WEIGHT)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_canvas = tk.Canvas(
            self.status_frame,
            width=200,
            height=20,
            bg=config.BG_DARK,
            highlightthickness=1,
            highlightbackground=config.TEXT_SECONDARY
        )
        self.progress_canvas.pack(side=tk.LEFT, padx=20)
        
        # Buffer Label (Hiển thị ký tự đang gõ dở)
        self.buffer_label = tk.Label(
            self.status_frame,
            text="Buffer: ",
            bg=config.BG_PANEL,
            fg=config.TEXT_ACCENT,
            font=(config.STATUS_FONT_FAMILY, config.STATUS_FONT_SIZE, "bold")
        )
        self.buffer_label.pack(side=tk.RIGHT, padx=10)
        
        # ----- Row 1: Suggestion Buttons -----
        self.suggestion_frame = tk.Frame(self.control_frame, bg=config.BG_PANEL)
        self.suggestion_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.suggestion_buttons = []
        for i in range(5):
            btn = tk.Button(
                self.suggestion_frame,
                text="",
                font=(config.BUTTON_FONT_FAMILY, 14),
                bg=config.BUTTON_BG,
                fg=config.BUTTON_FG,
                command=lambda idx=i: self._on_suggestion_click(idx),
                width=15
            )
            # Mặc định ẩn nút
            btn.pack_forget() 
            self.suggestion_buttons.append(btn)
            
        # ----- Row 2: Text Area -----
        self.text_frame = tk.Frame(self.control_frame, bg=config.BG_TEXT)
        self.text_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.text_scrollbar = tk.Scrollbar(self.text_frame)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(
            self.text_frame,
            bg=config.BG_TEXT,
            fg=config.TEXT_PRIMARY,
            font=(config.TEXT_AREA_FONT_FAMILY, config.TEXT_AREA_FONT_SIZE, config.TEXT_AREA_FONT_WEIGHT),
            wrap=tk.WORD,
            insertbackground=config.TEXT_PRIMARY,
            selectbackground=config.TEXT_SECONDARY,
            selectforeground=config.BG_DARK,
            padx=15,
            pady=15,
            yscrollcommand=self.text_scrollbar.set
        )
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.text_scrollbar.config(command=self.text_area.yview)
        
        # ----- Side Buttons Panel -----
        self.buttons_frame = tk.Frame(self.control_frame, bg=config.BG_PANEL)
        self.buttons_frame.grid(row=2, column=1, sticky="ns", padx=10, pady=10)
        
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
        
        self.clear_button = tk.Button(self.buttons_frame, text="🗑️ Xóa", command=self._on_clear, **button_config)
        self.clear_button.pack(pady=5, fill=tk.X)
        
        self.speak_button = tk.Button(self.buttons_frame, text="🔊 Đọc", command=self._on_speak, **button_config)
        self.speak_button.pack(pady=5, fill=tk.X)
        
        self.space_button = tk.Button(self.buttons_frame, text="⎵ Space", command=self._on_space, **button_config)
        self.space_button.pack(pady=5, fill=tk.X)
        
        self.backspace_button = tk.Button(self.buttons_frame, text="⌫ Xóa ký tự", command=self._on_backspace, **button_config)
        self.backspace_button.pack(pady=5, fill=tk.X)
        
        # Nút cài đặt (placeholder)
        tk.Frame(self.buttons_frame, height=20, bg=config.BG_PANEL).pack()
        self.settings_button = tk.Button(self.buttons_frame, text="⚙️ Cài đặt", command=self._on_settings, **button_config)
        self.settings_button.pack(pady=5, fill=tk.X)
    
    def _bind_shortcuts(self):
        self.root.bind('q', lambda e: self.on_closing())
        self.root.bind('Q', lambda e: self.on_closing())
        self.root.bind('<Escape>', lambda e: self.on_closing())

    def _on_suggestion_click(self, index):
        """Xử lý khi click vào nút gợi ý."""
        if 0 <= index < len(self.suggestion_buttons):
            text = self.suggestion_buttons[index].cget("text")
            if text:
                # 1. Thêm từ đã chọn vào câu
                self.text_area.insert(tk.END, text + " ")
                self.sentence_tokens.append(text)
                self.sentence_tokens.append(" ")
                
                # 2. Xóa buffer và reset gợi ý
                self.current_buffer = ""
                self._update_suggestions_ui([])
                self._update_buffer_ui()

    def _update_suggestions_ui(self, suggestions):
        """Cập nhật hiển thị các nút gợi ý."""
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(suggestions):
                btn.configure(text=suggestions[i])
                btn.pack(side=tk.LEFT, padx=5) # Hiện nút
            else:
                btn.configure(text="")
                btn.pack_forget() # Ẩn nút

    def _update_buffer_ui(self):
        """Cập nhật hiển thị buffer label."""
        self.buffer_label.configure(text=f"Buffer: {self.current_buffer}")

    def _on_clear(self):
        self.text_area.delete("1.0", tk.END)
        self.sentence_tokens = []
        self.current_buffer = ""
        self.last_appended_token = ""
        self._update_suggestions_ui([])
        self._update_buffer_ui()
    
    def _on_speak(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text: return
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Lỗi TTS: {e}")
        else:
            print(f"TTS không khả dụng. Text: {text}")
    
    def _on_space(self):
        """
        Nút Space:
        - Nếu có buffer: chốt buffer vào câu -> thêm space -> xóa buffer
        - Nếu không buffer: thêm space bình thường
        """
        if self.current_buffer:
            # Chốt buffer hiện tại
            self.text_area.insert(tk.END, self.current_buffer + " ")
            self.sentence_tokens.append(self.current_buffer)
            self.sentence_tokens.append(" ")
            
            # Reset buffer
            self.current_buffer = ""
            self._update_suggestions_ui([])
            self._update_buffer_ui()
        else:
            # Thêm khoảng trắng thường
            self.text_area.insert(tk.END, " ")
            self.sentence_tokens.append(" ")
            self.last_appended_token = " "
    
    def _on_backspace(self):
        """
        Nút Backspace:
        - Ưu tiên xóa ký tự trong buffer trước.
        - Nếu buffer rỗng thì xóa ký tự trong text area.
        """
        if self.current_buffer:
            self.current_buffer = self.current_buffer[:-1]
            self._update_buffer_ui()
            # Cập nhật gợi ý mới sau khi xóa bớt
            suggestions = self.suggester.get_suggestions(self.current_buffer)
            self._update_suggestions_ui(suggestions)
        else:
            # Logic cũ: Xóa trong text area
            content = self.text_area.get("1.0", tk.END)
            if len(content) > 1:
                self.text_area.delete("end-2c", "end-1c")
                if self.sentence_tokens:
                    self.sentence_tokens.pop()
    
    def _on_settings(self):
        pass # Placeholder

    def _update_progress_bar(self, progress: float):
        self.progress_canvas.delete("all")
        width = 200
        height = 20
        fill_width = int(width * progress)
        color = config.TEXT_SECONDARY if progress < 1.0 else config.TEXT_ACCENT
        if fill_width > 0:
            self.progress_canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")
    
    def update_frame(self):
        if not self.running: return
        
        frame, current_pred, confirmed_pred, hold_progress = self.backend.process_frame()
        
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            panel_height = self.video_label.winfo_height()
            panel_width = self.video_label.winfo_width()
            
            # Resize frame để fit vào panel
            if panel_height > 10 and panel_width > 10:
                aspect_ratio = frame.shape[1] / frame.shape[0]
                new_height = panel_height - 10
                new_width = int(new_height * aspect_ratio)
                if new_width > panel_width - 10:
                    new_width = panel_width - 10
                    new_height = int(new_width / aspect_ratio)
                frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
            else:
                # Nếu panel chưa có kích thước, dùng kích thước mặc định
                frame_resized = cv2.resize(frame_rgb, (640, 480))
                
            image = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=image)
            self.video_label.configure(image=photo)
            self.video_label.image = photo

        status_text = f"Giữ 3s: {current_pred}" if current_pred else "Giữ 3s: ..."
        self.status_label.configure(text=status_text)
        self._update_progress_bar(hold_progress)
        
        # LOGIC MỚI: Xử lý ký tự xác nhận
        if confirmed_pred and confirmed_pred != self.last_appended_token:
            # Thay vì thêm ngay vào câu, thêm vào Buffer
            self.current_buffer += confirmed_pred
            self.last_appended_token = confirmed_pred
            self.backend.confirmed_prediction = "" # Reset backend
            
            # Cập nhật UI Buffer
            self._update_buffer_ui()
            
            # Lấy gợi ý từ Backend
            suggestions = self.suggester.get_suggestions(self.current_buffer)
            self._update_suggestions_ui(suggestions)
            
        self.root.after(config.FRAME_UPDATE_INTERVAL, self.update_frame)
    
    def on_closing(self):
        self.running = False
        self.backend.release()
        self.root.destroy()
