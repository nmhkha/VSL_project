# =============================================================================
# VSL Communicator - Word Suggester
# =============================================================================
# Xử lý gợi ý từ tiếng Việt dựa trên file từ điển.
# =============================================================================

import csv
import unicodedata
import os
import logging
from collections import defaultdict

class WordSuggester:
    """
    Class xử lý gợi ý từ tiếng Việt.
    Đọc từ file CSV và cung cấp gợi ý dựa trên input không dấu.
    """
    
    def __init__(self, csv_path: str):
        """
        Khởi tạo và load dữ liệu từ điển.
        
        Args:
            csv_path: Đường dẫn đến file words.csv
        """
        self.dictionary = defaultdict(list)
        self.csv_path = csv_path
        self._load_dictionary()
        
    def _remove_diacritics(self, text: str) -> str:
        """
        Loại bỏ dấu tiếng Việt để tạo key tra cứu.
        Ví dụ: "trường" -> "truong"
        """
        # Chuẩn hóa unicode tổ hợp
        text = unicodedata.normalize('NFD', text)
        # Loại bỏ các ký tự dấu (category 'Mn')
        text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
        # Thay thế Đ/đ thành D/d (vì unicodedata không đổi Đ thành D)
        text = text.replace('Đ', 'D').replace('đ', 'd')
        return text.lower()
        
    def _load_dictionary(self):
        """Đọc file CSV và xây dựng dictionary."""
        if not os.path.exists(self.csv_path):
            print(f"⚠ Không tìm thấy file từ điển: {self.csv_path}")
            logging.error(f"Dictionary file not found: {self.csv_path}")
            return

        print("Đang tải từ điển gợi ý...")
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                count = 0
                for row in reader:
                    if row:
                        word = row[0].strip()
                        if word:
                            # Key là từ không dấu viết thường
                            key = self._remove_diacritics(word)
                            self.dictionary[key].append(word)
                            count += 1
            
            print(f"✓ Đã tải {count} từ vào bộ nhớ.")
            logging.info(f"Loaded {count} words into dictionary")
            
        except Exception as e:
            print(f"✗ Lỗi khi đọc file từ điển: {e}")
            logging.error(f"Failed to load dictionary: {e}")

    def get_suggestions(self, query: str, limit: int = 5) -> list:
        """
        Lấy danh sách gợi ý cho từ đang gõ.
        
        Args:
            query: Chuỗi ký tự đang gõ (có thể không dấu)
            limit: Số lượng gợi ý tối đa
            
        Returns:
            List[str]: Danh sách các từ gợi ý
        """
        if not query:
            return []
            
        query_key = self._remove_diacritics(query)
        suggestions = []
        
        # 1. Ưu tiên khớp chính xác (Exact match key)
        # Ví dụ: gõ "truong" -> lấy list của key "truong"
        if query_key in self.dictionary:
            exact_matches = self.dictionary[query_key]
            # Lọc bớt các từ quá dài nếu cần, hoặc lấy hết
            suggestions.extend(exact_matches)
            
        # 2. Nếu chưa đủ limit, tìm kiếm prefix (Bắt đầu bằng...)
        # Lưu ý: Duyệt hết dict sẽ chậm, nên ở version đơn giản này ta chỉ dùng exact key match
        # Nếu muốn prefix search nhanh, cần dùng Trie structure.
        # Tuy nhiên, logic người dùng VSL thường gõ đủ ký tự của 1 từ rồi mới chọn
        # nên exact key match cho key không dấu là hợp lý nhất.
        
        # Chỉ trả về số lượng giới hạn
        return suggestions[:limit]
