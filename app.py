# ==============================================
# File: app.py
# ==============================================


import streamlit as st
import pandas as pd
from data_preprocess import load_and_clean_data
from dashboard_overview import show_overview_section
from dashboard_filters import apply_filters
from dashboard_portfolio import show_portfolio_composition


# Import màu từ colors_config
from colors_config import THEME, POSITIVE, NEGATIVE, WARNING

# === 1. CẤU HÌNH STREAMLIT ===
st.set_page_config(
    page_title="🏦 Bank Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 2. CSS HOÀN CHỈNH VỚI MÀU SẮC ĐỒNG NHẤT ===
st.markdown(f"""
   <style>
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');


   /* ═══════════════════════════════════════════════════════════════ */
   /* GLOBAL THEME */
   /* ═══════════════════════════════════════════════════════════════ */
   * {{
       font-family: 'Inter', sans-serif;
   }}


   .main .block-container {{
       background-color: {THEME['BACKGROUND_PRIMARY']};
       color: {THEME['TEXT_SECONDARY']};
       padding-top: 2rem;
       padding-bottom: 2rem;
   }}


   .stApp {{
       background-color: {THEME['BACKGROUND_PRIMARY']};
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* SIDEBAR STYLING */
   /* ═══════════════════════════════════════════════════════════════ */
   [data-testid="stSidebar"] {{
       background: linear-gradient(180deg, {THEME['BACKGROUND_SECONDARY']} 0%, #1a1447 100%);
       padding-top: 1rem;
       border-right: 1px solid {THEME['BORDER']};
   }}


   [data-testid="stSidebar"] > div:first-child {{
       padding-top: 0;
   }}


   /* ✅ FIX: Title trong sidebar - MÀU TRẮNG SÁNG */
   [data-testid="stSidebar"] h1 {{
       color: #FFFFFF !important;
       font-size: 24px !important;
       font-weight: 700 !important;
       margin-bottom: 1rem !important;
   }}


   /* ✅ FIX: Subheader (h2, h3) - MÀU VÀNG/CAM SÁNG ĐỂ NỔI BẬT */
   [data-testid="stSidebar"] h2 {{
       color: #FCD34D !important;
       font-size: 15px !important;
       font-weight: 700 !important;
       text-transform: uppercase;
       letter-spacing: 0.5px;
       margin-top: 1.5rem !important;
       margin-bottom: 1rem !important;
       padding-left: 0.5rem;
       border-left: 3px solid #FCD34D;
   }}


   [data-testid="stSidebar"] h3 {{
       color: #FCD34D !important;
       font-size: 15px !important;
       font-weight: 700 !important;
       text-transform: uppercase;
       letter-spacing: 0.5px;
       margin-top: 1.5rem !important;
       margin-bottom: 1rem !important;
       padding-left: 0.5rem;
       border-left: 3px solid #FCD34D;
   }}


   /* Paragraph text trong sidebar */
   [data-testid="stSidebar"] p {{
       color: {THEME['TEXT_SECONDARY']} !important;
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* RADIO BUTTONS - MENU STYLE */
   /* ═══════════════════════════════════════════════════════════════ */


   .stRadio {{
       background: transparent;
   }}


   .stRadio > label {{
       display: none;
   }}


   .stRadio > div {{
       gap: 0.5rem;
   }}


   .stRadio > div > label {{
       background: rgba(255, 255, 255, 0.05);
       border: 1px solid rgba(255, 255, 255, 0.1);
       border-radius: 12px;
       padding: 1rem 1.2rem;
       margin-bottom: 0.5rem;
       cursor: pointer;
       transition: all 0.3s ease;
       display: flex;
       align-items: center;
       gap: 12px;
       font-size: 16px !important;
       font-weight: 500 !important;
       color: {THEME['TEXT_SECONDARY']} !important;
   }}


   .stRadio > div > label:hover {{
       background: rgba(255, 255, 255, 0.08);
       border-color: {THEME['ACCENT']};
       transform: translateX(5px);
       box-shadow: 0 4px 12px rgba(96, 51, 191, 0.3);
   }}


   .stRadio > div > label:has(input:checked) {{
       background: linear-gradient(135deg, {THEME['ACCENT']}, {THEME['DATA_SECONDARY']});
       border-color: {THEME['ACCENT']};
       color: white !important;
       font-weight: 600 !important;
       box-shadow: 0 4px 16px rgba(96, 51, 191, 0.4);
   }}


   .stRadio > div > label > div:first-child {{
       display: none;
   }}


   .stRadio > div > label > div:last-child {{
       font-size: 16px !important;
       font-weight: inherit !important;
       color: inherit !important;
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* EXPANDER STYLING */
   /* ═══════════════════════════════════════════════════════════════ */


   /* Expander header */
   .streamlit-expanderHeader {{
       font-weight: 600;
       font-size: 15px;
       background: rgba(255, 255, 255, 0.05) !important;
       border: 1px solid {THEME['BORDER']} !important;
       border-radius: 10px;
       color: #FFFFFF !important;
       padding: 0.8rem 1rem;
       transition: all 0.3s ease;
   }}


   .streamlit-expanderHeader:hover {{
       background: rgba(255, 255, 255, 0.08) !important;
       border-color: {THEME['ACCENT']} !important;
   }}


   /* ✅ FIX: Expander content - NỀN TỐI VÀ STYLING ĐẦY ĐỦ */
   .streamlit-expanderContent {{
       background: rgba(0, 0, 0, 0.3) !important;
       border: 1px solid {THEME['BORDER']};
       border-top: none;
       border-radius: 0 0 10px 10px;
       padding: 1rem;
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* MULTISELECT STYLING - FIX MÀU SẮC BÊN TRONG EXPANDER */
   /* ═══════════════════════════════════════════════════════════════ */


   /* ✅ Label của multiselect */
   .stMultiSelect > label {{
       font-size: 14px !important;
       font-weight: 600 !important;
       color: #FFFFFF !important;
       margin-bottom: 0.5rem !important;
   }}


   /* ✅ Container của multiselect */
   .stMultiSelect > div {{
       background: rgba(0, 0, 0, 0.4) !important;
       border: 1px solid {THEME['BORDER']} !important;
       border-radius: 8px;
   }}


   /* ✅ Input field bên trong multiselect */
   .stMultiSelect input {{
       color: white !important;
       background: transparent !important;
   }}


   /* ✅ Placeholder text */
   .stMultiSelect input::placeholder {{
       color: rgba(255, 255, 255, 0.5) !important;
   }}


   /* ✅ Dropdown menu */
   [data-baseweb="popover"] {{
       background: {THEME['BACKGROUND_SECONDARY']} !important;
       border: 1px solid {THEME['BORDER']} !important;
   }}


   /* ✅ Options trong dropdown */
   [role="option"] {{
       background: {THEME['BACKGROUND_SECONDARY']} !important;
       color: white !important;
   }}


   [role="option"]:hover {{
       background: {THEME['ACCENT']} !important;
       color: white !important;
   }}


   /* ✅ Selected tags (chips) - MÀU VÀNG/CAM */
   [data-baseweb="tag"] {{
       background: linear-gradient(135deg, #F59E0B, #FCD34D) !important;
       color: #1B134D !important;  /* Chữ màu tím đậm để tương phản */
       border: none !important;
       font-weight: 600 !important;
       padding: 0.4rem 0.8rem !important;
       border-radius: 8px !important;
       box-shadow: 0 2px 6px rgba(252, 211, 77, 0.3);
   }}

   /* Close button (X) trên tag */
   [data-baseweb="tag"] svg {{
       color: #1B134D !important;  /* Icon X màu tím đậm */
       opacity: 0.8;
   }}

   [data-baseweb="tag"] svg:hover {{
       opacity: 1;
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* BUTTON STYLING */
   /* ═══════════════════════════════════════════════════════════════ */
   .stButton > button {{
       width: 100%;
       background: linear-gradient(135deg, {THEME['ACCENT']}, {THEME['DATA_SECONDARY']});
       color: white !important;
       border: none;
       border-radius: 10px;
       font-weight: 600;
       font-size: 15px;
       padding: 0.75rem 1rem;
       transition: all 0.3s ease;
       box-shadow: 0 4px 12px rgba(96, 51, 191, 0.3);
   }}


   .stButton > button:hover {{
       background: linear-gradient(135deg, {THEME['DATA_SECONDARY']}, {THEME['ACCENT']});
       transform: translateY(-2px);
       box-shadow: 0 6px 16px rgba(96, 51, 191, 0.4);
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* INFO BOX (st.info) */
   /* ═══════════════════════════════════════════════════════════════ */
   .stAlert {{
       background: rgba(96, 51, 191, 0.2) !important;
       border: 1px solid {THEME['ACCENT']} !important;
       border-radius: 10px;
       color: white !important;
   }}


   .stAlert p {{
       color: white !important;
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* CONTENT AREA STYLING */
   /* ═══════════════════════════════════════════════════════════════ */
   h1, h2, h3 {{
       color: {THEME['TEXT_PRIMARY']} !important;
   }}


   p {{
       color: {THEME['TEXT_SECONDARY']};
   }}


   [data-testid="stMetricValue"] {{
       font-size: 28px;
       font-weight: 700;
       color: {THEME['TEXT_PRIMARY']} !important;
   }}


   [data-testid="stMetricLabel"] {{
       color: {THEME['TEXT_SECONDARY']} !important;
       font-weight: 500;
   }}


   [data-testid="metric-container"] {{
       background-color: {THEME['BACKGROUND_SECONDARY']};
       border: 1px solid {THEME['BORDER']};
       border-radius: 12px;
       padding: 1rem;
   }}


   hr {{
       border-color: {THEME['BORDER']};
       opacity: 0.3;
   }}


   .stDataFrame {{
       border: 1px solid {THEME['BORDER']};
       border-radius: 10px;
   }}


   /* ═══════════════════════════════════════════════════════════════ */
   /* HIDE STREAMLIT BRANDING */
   /* ═══════════════════════════════════════════════════════════════ */
   #MainMenu {{visibility: hidden;}}
   footer {{visibility: hidden;}}
   .stDeployButton {{display: none;}}
   button[kind="header"] {{display: none;}}
   </style>
""", unsafe_allow_html=True)

# === 3. NẠP DỮ LIỆU ===
DATA_PATH = "DSKH_BANK_ABCDEF.csv"


@st.cache_data
def load_data():
    return load_and_clean_data(DATA_PATH)


with st.spinner("⏳ Đang tải dữ liệu..."):
    df = load_data()

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION MENU 3 TẦNG
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=ABCDEF+Bank", width=200)

    st.title("🎯 Dashboard Control")
    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: CHỌN TẦNG
    # ═══════════════════════════════════════════════════════════════
    st.markdown("### 📊 Chọn Tầng Phân Tích")

    tang_main = st.radio(
        "layer_selection",
        [
            "📊 Tầng 1: Tổng quan (Strategic)",
            "🔍 Tầng 2: Phân tích Chuyên sâu (Tactical)",
            "⚙️ Tầng 3: Vận hành Chi tiết (Operational)"
        ],
        index=0,
        key="tang_selector",
        label_visibility="collapsed"
    )

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: BỘ LỌC
    # ═══════════════════════════════════════════════════════════════
    if "Chuyên sâu" in tang_main:
        st.markdown("### 🎛️ Bộ lọc dữ liệu")

        # 📍 ĐỊA LÝ
        with st.expander("📍 Địa lý", expanded=False):
            all_vung = sorted(df['Vung'].dropna().unique()) if 'Vung' in df else []
            vung_selected = st.multiselect(
                "Vùng",
                options=all_vung,
                default=all_vung,
                key="vung_filter"
            )

            all_khu_vuc = sorted(df['Khu_vuc'].dropna().unique()) if 'Khu_vuc' in df else []
            khu_vuc_selected = st.multiselect(
                "Khu vực",
                options=all_khu_vuc,
                default=all_khu_vuc,
                key="khuvuc_filter"
            )

            all_branch = sorted(df['Ma_chi_nhanh'].dropna().unique())
            branch_selected = st.multiselect(
                "Chi nhánh",
                options=all_branch,
                default=all_branch,
                key="branch_filter"
            )

        # 📦 SẢN PHẨM
        with st.expander("📦 Sản phẩm", expanded=False):
            all_product = sorted(
                df['Sub_productTen_san_pham'].dropna().unique()
            ) if 'Sub_productTen_san_pham' in df else []
            product_selected = st.multiselect(
                "Loại sản phẩm",
                options=all_product,
                default=all_product,
                key="product_filter"
            )

            all_term = sorted(
                df['Phan_theo_ky_han_NHTDDH'].dropna().unique()
            ) if 'Phan_theo_ky_han_NHTDDH' in df else []
            term_selected = st.multiselect(
                "Kỳ hạn vay",
                options=all_term,
                default=all_term,
                key="term_filter"
            )

        # ⏱️ THỜI GIAN
        with st.expander("⏱️ Thời gian", expanded=False):
            time_col = 'Ngay_giai_ngan_ban_dau_cua_khoan_vay_orig_val_date'
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df['Year'] = df[time_col].dt.year
            df['Quarter'] = df[time_col].dt.to_period('Q').astype(str)

            all_years = sorted(df['Year'].dropna().unique())
            year_selected = st.multiselect(
                "Năm giải ngân",
                options=all_years,
                default=all_years,
                key="year_filter"
            )

            all_quarters = sorted(df['Quarter'].dropna().unique())
            quarter_selected = st.multiselect(
                "Quý giải ngân",
                options=all_quarters,
                default=all_quarters,
                key="quarter_filter"
            )

        # ⚠️ RỦI RO
        with st.expander("⚠️ Rủi ro", expanded=False):
            if 'Nhom_no_KH' in df.columns:
                df['Nhom_no_KH'] = df['Nhom_no_KH'].astype('Int64')
                all_risk = sorted(df['Nhom_no_KH'].dropna().unique().tolist())
                for i in range(1, 6):
                    if i not in all_risk:
                        all_risk.append(i)
                all_risk = sorted(all_risk)
            else:
                all_risk = [1, 2, 3, 4, 5]

            risk_selected = st.multiselect(
                "Nhóm nợ",
                options=all_risk,
                default=all_risk,
                key="risk_filter",
                help="1: Chuẩn | 2: Chú ý | 3: Dưới chuẩn | 4: Nghi ngờ | 5: Xấu"
            )

        st.markdown("---")

        if st.button("🔄 Reset filters", use_container_width=True):
            st.rerun()

        df_filtered = apply_filters(
            df,
            vung_selected, khu_vuc_selected, branch_selected,
            product_selected, term_selected,
            year_selected, quarter_selected, risk_selected
        )

        st.info(f"📊 **{len(df_filtered):,}** / {len(df):,} hợp đồng")

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # SECTION 3: MENU CHỦ ĐỀ
        # ═══════════════════════════════════════════════════════════
        st.markdown("### 📑 Chọn Chủ đề phân tích")

        selected_tab = st.radio(
            "topic_selection",
            [
                "💰 Lợi nhuận & Doanh thu",
                "⚠️ Rủi ro & Chất lượng",
                "⚡ Hiệu quả Hoạt động",
                "📦 Cơ cấu Danh mục"
            ],
            index=0,
            key="topic_selector",
            label_visibility="collapsed"
        )


    else:
        df_filtered = df
        selected_tab = None

# ═══════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════
st.title("🏦 Dashboard Quản trị Tín dụng Ngân hàng")
st.caption("📅 Dữ liệu đến ngày: 06/08/2025")
st.markdown("---")

# TẦNG 1
if "Tổng quan" in tang_main:
    show_overview_section(df)


# TẦNG 2
elif "Chuyên sâu" in tang_main:
    with st.expander("ℹ️ Tóm tắt Bộ lọc", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Vùng", f"{len(vung_selected)}/{len(all_vung)}")
        with col2:
            st.metric("Chi nhánh", f"{len(branch_selected)}/{len(all_branch)}")
        with col3:
            st.metric("Sản phẩm", f"{len(product_selected)}/{len(all_product)}")
        with col4:
            st.metric("Năm", f"{len(year_selected)}/{len(all_years)}")

    st.markdown("---")

    if "Lợi nhuận" in selected_tab:
        from dashboard_profitability import show_profitability_section

        show_profitability_section(df_filtered)
    elif "Rủi ro" in selected_tab:
        from dashboard_risk import show_risk_section

        show_risk_section(df_filtered)
    elif "Hiệu quả" in selected_tab:
        from dashboard_efficiency import show_efficiency_section

        show_efficiency_section(df_filtered)
    elif "Cơ cấu" in selected_tab:
        show_portfolio_composition(df_filtered)


# TẦNG 3
elif "Vận hành" in tang_main:
    from dashboard_operational import show_operational_dashboard

    show_operational_dashboard(df)

# FOOTER
st.markdown("---")
st.markdown(
    "📘 **Nguồn:** DSKH_BANK_ABCDEF.csv | "
    "🧮 **Tổng hợp:** KPI, Dư nợ, Lợi nhuận, NPL | "
    "📊 **Tech Stack:** Python + Streamlit + Plotly"
)

