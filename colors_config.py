# ==============================================
# File: colors_config.py
# Bảng màu chuẩn cho Dashboard Ngân hàng
# ==============================================


"""
Bảng màu tuân thủ chuẩn Banking Dashboard (60-30-10 Rule)
Nguồn: BANG-MAU-DASHBOARD-NGAN-HANG-CHUYEN-NGHIEP.pdf
"""


# ═══════════════════════════════════════════════════════════════════
# 1. CORE COLORS (60%) - Màu chủ đạo
# ═══════════════════════════════════════════════════════════════════
PRIMARY = '#003366'  # Navy Blue - Đại diện ngân hàng
PRIMARY_LIGHT = '#3b82f6'  # Blue - Thân thiện
PRIMARY_LIGHTER = '#dbeafe'  # Light Blue - Background


# ═══════════════════════════════════════════════════════════════════
# 2. ANALYTICAL COLORS (30%) - Màu phân tích
# ═══════════════════════════════════════════════════════════════════


# A. Màu Ý nghĩa Tài chính
POSITIVE = '#10b981'  # Xanh lá - Lợi nhuận, tăng trưởng, NPL thấp
POSITIVE_LIGHT = '#22c55e'  # Xanh lá nhạt - Tích cực


NEGATIVE = '#ef4444'  # Đỏ - Thua lỗ, nợ xấu, rủi ro cao
NEGATIVE_DARK = '#dc2626'  # Đỏ đậm - Rất nghiêm trọng


WARNING = '#f59e0b'  # Vàng/Cam - NPL trung bình, cần chú ý
WARNING_LIGHT = '#fb923c'  # Cam nhạt


NEUTRAL = '#6b7280'  # Xám - Dữ liệu tham khảo
NEUTRAL_LIGHT = '#9ca3af'  # Xám nhạt


# B. Grayscale - Chuyên nghiệp
SLATE_800 = '#1e293b'  # Text chính
SLATE_600 = '#475569'  # Text phụ
SLATE_400 = '#94a3b8'  # Border, icon
SLATE_200 = '#e2e8f0'  # Background card
SLATE_50 = '#f8fafc'  # Background page


# ═══════════════════════════════════════════════════════════════════
# 3. ACCENT COLORS (10%) - Màu nhấn mạnh
# ═══════════════════════════════════════════════════════════════════


# Red Scale (cho NPL, Rủi ro)
RED_SCALE = [
   '#fef2f2',  # Red 50  - NPL rất thấp
   '#fee2e2',  # Red 100
   '#fecaca',  # Red 200
   '#fca5a5',  # Red 300
   '#f87171',  # Red 400 - NPL trung bình
   '#ef4444',  # Red 500 - NPL cao
   '#dc2626',  # Red 600 - NPL rất cao
   '#b91c1c',  # Red 700 - NPL nghiêm trọng
   '#991b1b'  # Red 800 - NPL nguy cấp
]


# Green Scale (cho Lợi nhuận, Hiệu quả)
GREEN_SCALE = [
   '#f0fdf4',  # Green 50
   '#dcfce7',  # Green 100
   '#bbf7d0',  # Green 200
   '#86efac',  # Green 300
   '#4ade80',  # Green 400
   '#22c55e',  # Green 500
   '#16a34a',  # Green 600
   '#15803d',  # Green 700
   '#166534'  # Green 800
]


# Yellow/Amber Scale (cho Cảnh báo)
AMBER_SCALE = [
   '#fffbeb',  # Amber 50
   '#fef3c7',  # Amber 100
   '#fde68a',  # Amber 200
   '#fcd34d',  # Amber 300
   '#fbbf24',  # Amber 400
   '#f59e0b',  # Amber 500
   '#d97706',  # Amber 600
   '#b45309'  # Amber 700
]


# ═══════════════════════════════════════════════════════════════════
# 4. NPL LOGIC COLORS - Màu theo nhóm nợ
# ═══════════════════════════════════════════════════════════════════
NPL_GROUP_COLORS = {
   1: '#22c55e',  # Nhóm 1: Xanh lá - Nợ chuẩn
   2: '#eab308',  # Nhóm 2: Vàng - Nợ cần chú ý
   3: '#f97316',  # Nhóm 3: Cam - Nợ dưới chuẩn (NPL)
   4: '#ef4444',  # Nhóm 4: Đỏ - Nợ nghi ngờ (NPL)
   5: '#dc2626'  # Nhóm 5: Đỏ đậm - Nợ xấu (NPL)
}




# ═══════════════════════════════════════════════════════════════════
# 5. HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════


def get_npl_color(npl_ratio):
   """
   Trả về màu phù hợp dựa trên NPL ratio


   Args:
       npl_ratio (float): Tỷ lệ NPL (%)


   Returns:
       str: Mã màu hex
   """
   if npl_ratio < 2:
       return POSITIVE_LIGHT  # Xanh lá - Tốt
   elif npl_ratio < 3:
       return WARNING  # Vàng - Cảnh báo
   elif npl_ratio < 5:
       return RED_SCALE[4]  # Đỏ nhạt
   elif npl_ratio < 10:
       return RED_SCALE[5]  # Đỏ
   else:
       return RED_SCALE[7]  # Đỏ đậm - Nghiêm trọng




def get_risk_level_color(level):
   """
   Trả về màu theo mức độ rủi ro


   Args:
       level (str): 'low', 'medium', 'high', 'critical'


   Returns:
       str: Mã màu hex
   """
   colors = {
       'low': POSITIVE_LIGHT,
       'medium': WARNING,
       'high': NEGATIVE,
       'critical': NEGATIVE_DARK
   }
   return colors.get(level.lower(), NEUTRAL)




def get_performance_color(value, threshold_good, threshold_bad):
   """
   Trả về màu dựa trên hiệu suất (giá trị càng cao càng tốt)


   Args:
       value (float): Giá trị cần đánh giá
       threshold_good (float): Ngưỡng tốt
       threshold_bad (float): Ngưỡng xấu


   Returns:
       str: Mã màu hex
   """
   if value >= threshold_good:
       return POSITIVE_LIGHT
   elif value >= threshold_bad:
       return WARNING
   else:
       return NEGATIVE


# --- DEFINITION CỦA CÁC THEME ---


dark_theme = {
   "NAME": "Dark",
   # Nền & Giao diện
   "BACKGROUND_PRIMARY": "#150925",    # Nền chính của trang
   "BACKGROUND_SECONDARY": "#492d70", # Nền cho card, sidebar
   "ACCENT": "#5a3780",             # Màu nhấn
   "BORDER": "#3e328a",             # Màu viền cho card


   # Màu Dữ liệu Biểu đồ
   "DATA_PRIMARY": "#63A5C3",
   "DATA_SECONDARY": "#C13C91",


   # Màu Văn bản
   "TEXT_PRIMARY": "#FFFFFF",
   "TEXT_SECONDARY": "#E2E8F0",
   "TEXT_TERTIARY": "#94A3B8"
}


light_theme = {
   "NAME": "Light",
   # Nền & Giao diện
   "BACKGROUND_PRIMARY": "#f8fafc",    # SLATE_50
   "BACKGROUND_SECONDARY": "#ffffff", # Màu trắng
   "ACCENT": "#003366",             # PRIMARY
   "BORDER": "#e2e8f0",             # SLATE_200


   # Màu Dữ liệu Biểu đồ
   "DATA_PRIMARY": "#3b82f6",       # PRIMARY_LIGHT
   "DATA_SECONDARY": "#8b5cf6",     # Một màu tím cho theme sáng


   # Màu Văn bản
   "TEXT_PRIMARY": "#1e293b",       # SLATE_800
   "TEXT_SECONDARY": "#475569",     # SLATE_600
   "TEXT_TERTIARY": "#9ca3af"       # NEUTRAL_LIGHT
}
# --- CHỌN THEME ĐỂ SỬ DỤNG TRONG TOÀN BỘ APP ---
THEME = dark_theme  # <-- Chỉ cần thay đổi ở đây để chuyển đổi toàn bộ giao diện


# =======================================================================
# CÁC HÀM TIỆN ÍCH (HELPER FUNCTIONS) - Sử dụng màu từ THEME được chọn
# =======================================================================


def get_npl_color_by_ratio(npl_ratio):
   """Trả về màu ngữ nghĩa dựa trên tỷ lệ NPL."""
   if npl_ratio < 2: return POSITIVE
   if npl_ratio < 3: return WARNING
   return NEGATIVE


def apply_theme_to_fig(fig):
   """Áp dụng màu nền và font của theme hiện tại cho biểu đồ Plotly."""
   fig.update_layout(
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(0,0,0,0)',
       font_color=THEME["TEXT_SECONDARY"],
       title_font_color=THEME["TEXT_PRIMARY"],
       xaxis=dict(gridcolor=THEME["BORDER"]),
       yaxis=dict(gridcolor=THEME["BORDER"])
   )
   return fig

