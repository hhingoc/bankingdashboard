

# ==============================================
# File: dashboard_profitability.py
# Module: Lợi nhuận & Doanh thu (3 TABS)
# ==============================================


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots




def show_profitability_section(df):
   """
   💰 Module Lợi nhuận & Doanh thu
   3 Tabs: A) Tổng quan | B) Cấu trúc | C) Hiệu suất
   """


   st.header("💰 Lợi nhuận & Doanh thu")
   st.caption(f"📊 Phân tích {len(df):,} hợp đồng | Dữ liệu đến 06/08/2025")


   # =====================================================================
   # TABS NGANG (Streamlit native tabs)
   # =====================================================================
   tab_a, tab_b, tab_c = st.tabs([
       "📊 A. TỔNG QUAN LỢI NHUẬN",
       "🏗️ B. CẤU TRÚC THU NHẬP",
       "📈 C. HIỆU SUẤT LÃI SUẤT"
   ])


   # ─────────────────────────────────────────────────────────────────
   # TAB A: TỔNG QUAN LỢI NHUẬN
   # ─────────────────────────────────────────────────────────────────
   with tab_a:
       show_profitability_overview(df)


   # ─────────────────────────────────────────────────────────────────
   # TAB B: CẤU TRÚC THU NHẬP
   # ─────────────────────────────────────────────────────────────────
   with tab_b:
       show_income_structure(df)


   # ─────────────────────────────────────────────────────────────────
   # TAB C: HIỆU SUẤT LÃI SUẤT
   # ─────────────────────────────────────────────────────────────────
   with tab_c:
       show_interest_performance(df)




# ═════════════════════════════════════════════════════════════════════
# TAB A: TỔNG QUAN LỢI NHUẬN
# ═════════════════════════════════════════════════════════════════════


def show_profitability_overview(df):
   """Tab A: Tổng quan Lợi nhuận"""


   st.markdown("### 📊 Phần A: Tổng quan Lợi nhuận")
   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # 4 KPI CARDS
   # ─────────────────────────────────────────────────────────────────
   lai_phai_thu = df['Lai_thong_thuong_Phai_tra'].sum()
   lai_da_thu = df['Lai_thong_thuong_Da_tra'].sum()
   lai_con_lai = lai_phai_thu - lai_da_thu
   ty_le_thu_hoi = (lai_da_thu / lai_phai_thu * 100) if lai_phai_thu > 0 else 0


   col1, col2, col3, col4 = st.columns(4)


   with col1:
       st.metric(
           "💰 Tổng lãi phải thu",
           f"{lai_phai_thu / 1e9:.2f} tỷ",
           help="Tổng lãi thông thường phải thu"
       )


   with col2:
       st.metric(
           "✅ Lãi đã thu",
           f"{lai_da_thu / 1e9:.2f} tỷ",
           help="Lãi đã thu được"
       )


   with col3:
       st.metric(
           "⏳ Lãi còn lại",
           f"{lai_con_lai / 1e9:.2f} tỷ",
           help="Lãi chưa thu"
       )


   with col4:
       delta_color = "normal" if ty_le_thu_hoi >= 95 else "inverse"
       st.metric(
           "📊 Tỷ lệ thu hồi",
           f"{ty_le_thu_hoi:.2f}%",
           delta="Xuất sắc" if ty_le_thu_hoi >= 95 else "Cần cải thiện",
           delta_color=delta_color,
           help="Tỷ lệ thu hồi lãi"
       )


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════════
   # ═══════════════════════════════════════════════════════════════════
   # WATERFALL CHART: Thu nhập Lãi (ĐÚNG LOGIC) - START = 0
   # ═══════════════════════════════════════════════════════════════════


   st.markdown("#### 💧 Waterfall: Phân tích Thu nhập Lãi (Đầy đủ)")


   # ─── TÍNH TOÁN ───
   lai_phat_goc = df['Lai_phat_tren_goc_Phai_tra'].sum()
   lai_phat_lai = df['Lai_phat_tren_lai_Phai_tra'].sum()
   total_income = lai_da_thu + lai_con_lai + lai_phat_goc + lai_phat_lai


   # ─── BẢNG MÀU ───
   BANK_COLORS = {
       'positive': '#10b981',
       'negative': '#ef4444',
       'total': '#3b82f6',
       'text': '#1e293b',
       'border': '#94a3b8',
       'grid': '#e5e7eb',
   }


   # ─── TẠO WATERFALL (START = 0) ───
   fig_waterfall = go.Figure(go.Waterfall(
       name="Dòng tiền",
       orientation="v",
       measure=["relative", "relative", "relative", "relative", "total"],
       x=[
           "✅ Lãi đã thu",
           "⏳ Lãi chưa thu",
           "🔴 Phạt Gốc",
           "🟠 Phạt Lãi",
           "🎯 Tổng thu nhập"
       ],
       y=[
           lai_da_thu / 1e9,  # +674.4T
           lai_con_lai / 1e9,  # +23.3T
           lai_phat_goc / 1e9,  # +0.774T
           lai_phat_lai / 1e9,  # +0.601T
           0  # Total (auto)
       ],
       text=[
           f"+{lai_da_thu / 1e9:.1f}T",
           f"+{lai_con_lai / 1e9:.1f}T",
           f"+{lai_phat_goc / 1e6:.0f}M" if lai_phat_goc > 0 else "0",
           f"+{lai_phat_lai / 1e6:.0f}M" if lai_phat_lai > 0 else "0",
           f"{total_income / 1e9:.2f}T"
       ],
       textposition="outside",
       textfont=dict(size=12, color=BANK_COLORS['text']),
       connector={"line": {"color": BANK_COLORS['border'], "width": 2, "dash": "dot"}},
       decreasing={"marker": {"color": BANK_COLORS['negative']}},
       increasing={"marker": {"color": BANK_COLORS['positive']}},
       totals={"marker": {"color": BANK_COLORS['total']}}
   ))


   fig_waterfall.update_layout(
       title={
           'text': 'Thu nhập Lãi: Cơ cấu đầy đủ (tại 06/08/2025)',
           'font': {'size': 16, 'color': BANK_COLORS['text']},
           'x': 0.5,
           'xanchor': 'center'
       },
       xaxis=dict(
           title='',
           showgrid=False,
           tickfont=dict(size=11, color=BANK_COLORS['text']),
           tickangle=-12
       ),
       yaxis=dict(
           title=dict(
               text='Giá trị (Tỷ VNĐ)',
               font=dict(size=12, color=BANK_COLORS['text'])
           ),
           showgrid=True,
           gridcolor=BANK_COLORS['grid'],
           zeroline=True,
           zerolinecolor=BANK_COLORS['border'],
           zerolinewidth=2,
           tickfont=dict(size=10, color=BANK_COLORS['text'])
       ),
       height=500,
       showlegend=False,
       plot_bgcolor='white',
       paper_bgcolor='#f8fafc',
       margin=dict(l=60, r=40, t=80, b=80)
   )


   st.plotly_chart(fig_waterfall, use_container_width=True)


   # ═══════════════════════════════════════════════════════════════════
   # CHÚ GIẢI
   # ═══════════════════════════════════════════════════════════════════


   st.info("""
   **📌 Giải thích Waterfall (tại 06/08/2025):**


   **CƠ CẤU THU NHẬP:**
   - ✅ **Lãi đã thu (674.4T):** Lãi thường đã thu được thực tế
   - ⏳ **Lãi chưa thu (23.3T):** Lãi thường chưa đến hạn/chưa thu
   - 🔴 **Phạt Gốc (774M):** Phạt do gốc quá hạn (thu bổ sung)
   - 🟠 **Phạt Lãi (601M):** Phạt do lãi quá hạn (thu bổ sung)


   **TỔNG THU NHẬP DỰ KIẾN:**
   - 🎯 **698.48T** = 674.4 + 23.3 + 0.774 + 0.601 (nếu thu đủ)


   ⚠️ **Lưu ý:**
   - Lãi phải thu = Đã thu + Chưa thu = 697.7T (không tính phạt)
   - Tổng thu nhập > Lãi phải thu vì có thêm lãi phạt!
   """)


   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # LINE CHART: Xu hướng thu lãi theo NĂM 2014-2024
   # ─────────────────────────────────────────────────────────────────
   st.markdown("#### 📈 Xu hướng Thu lãi theo Năm (2014-2024)")


   if 'Nam_giai_ngan' in df.columns:
       # Filter dữ liệu
       df_temp = df[(df['Nam_giai_ngan'] >= 2014) & (df['Nam_giai_ngan'] <= 2024)].copy()


       if len(df_temp) > 0:
           # Group theo năm
           trend_income = df_temp.groupby('Nam_giai_ngan').agg({
               'Lai_thong_thuong_Da_tra': 'sum',
               'Lai_thong_thuong_Phai_tra': 'sum',
               'Ma_khach_hang': 'count'
           }).reset_index()


           trend_income.columns = ['Nam', 'Lai_da_thu', 'Lai_phai_tra', 'So_HD']


           # Tính % thu hồi
           trend_income['Collection_Rate'] = (trend_income['Lai_da_thu'] / trend_income['Lai_phai_tra'] * 100)


           # Convert to tỷ
           trend_income['Lai_da_thu_ty'] = trend_income['Lai_da_thu'] / 1e9
           trend_income['Lai_phai_tra_ty'] = trend_income['Lai_phai_tra'] / 1e9


           # Sort theo năm
           trend_income = trend_income.sort_values('Nam')


           # ─── CREATE DUAL-AXIS LINE CHART ───
           from plotly.subplots import make_subplots


           fig_trend = make_subplots(specs=[[{"secondary_y": True}]])


           # Line 1: Lãi đã thu
           fig_trend.add_trace(
               go.Scatter(
                   x=trend_income['Nam'],
                   y=trend_income['Lai_da_thu_ty'],
                   name='Lãi đã thu',
                   line=dict(color='#10b981', width=3),
                   mode='lines+markers',
                   marker=dict(size=10, line=dict(color='white', width=2)),
                   hovertemplate='<b>Năm %{x}</b><br>Lãi đã thu: %{y:.2f} tỷ<extra></extra>'
               ),
               secondary_y=False
           )


           # Line 2: Lãi phải trả
           fig_trend.add_trace(
               go.Scatter(
                   x=trend_income['Nam'],
                   y=trend_income['Lai_phai_tra_ty'],
                   name='Lãi phải trả',
                   line=dict(color='#3b82f6', width=3, dash='dash'),
                   mode='lines+markers',
                   marker=dict(size=10, line=dict(color='white', width=2)),
                   hovertemplate='<b>Năm %{x}</b><br>Lãi phải trả: %{y:.2f} tỷ<extra></extra>'
               ),
               secondary_y=False
           )


           # Line 3: Collection Rate (secondary axis)
           fig_trend.add_trace(
               go.Scatter(
                   x=trend_income['Nam'],
                   y=trend_income['Collection_Rate'],
                   name='Collection Rate',
                   line=dict(color='#f59e0b', width=2),
                   mode='lines+markers',
                   marker=dict(size=8),
                   hovertemplate='<b>Năm %{x}</b><br>Collection Rate: %{y:.1f}%<extra></extra>'
               ),
               secondary_y=True
           )


           # Update axes
           fig_trend.update_xaxes(
               title_text='Năm',
               showgrid=True,
               gridcolor='#e5e7eb',
               tickmode='linear',
               dtick=1
           )


           fig_trend.update_yaxes(
               title_text='Thu nhập Lãi (Tỷ VNĐ)',
               showgrid=True,
               gridcolor='#e5e7eb',
               secondary_y=False
           )


           fig_trend.update_yaxes(
               title_text='Collection Rate (%)',
               showgrid=False,
               secondary_y=True,
               range=[0, 100]
           )


           # Layout
           fig_trend.update_layout(
               title='Xu hướng Thu lãi & Collection Rate theo Năm',
               height=450,
               plot_bgcolor='white',
               paper_bgcolor='white',
               hovermode='x unified',
               legend=dict(
                   orientation='h',
                   yanchor='bottom',
                   y=1.02,
                   xanchor='right',
                   x=1
               )
           )


           st.plotly_chart(fig_trend, use_container_width=True)


           # ─── INSIGHTS ───
           col_ins1, col_ins2, col_ins3 = st.columns(3)


           with col_ins1:
               total_collected = trend_income['Lai_da_thu_ty'].sum()
               st.metric("💰 Tổng thu lãi 2014-2024", f"{total_collected:.1f} tỷ")


           with col_ins2:
               avg_collection = trend_income['Collection_Rate'].mean()
               delta_color = "normal" if avg_collection >= 90 else "inverse"
               st.metric(
                   "📊 Collection Rate TB",
                   f"{avg_collection:.1f}%",
                   delta="Tốt" if avg_collection >= 90 else "Cần cải thiện",
                   delta_color=delta_color
               )


           with col_ins3:
               # CAGR
               first_val = trend_income.iloc[0]['Lai_da_thu_ty']
               last_val = trend_income.iloc[-1]['Lai_da_thu_ty']
               num_years = trend_income.iloc[-1]['Nam'] - trend_income.iloc[0]['Nam']


               if first_val > 0 and num_years > 0:
                   cagr = ((last_val / first_val) ** (1 / num_years) - 1) * 100
               else:
                   cagr = 0


               delta_color_cagr = "normal" if cagr > 0 else "inverse"
               st.metric(
                   "📈 CAGR Thu lãi",
                   f"{cagr:+.1f}%/năm",
                   delta="Tăng trưởng" if cagr > 0 else "Giảm",
                   delta_color=delta_color_cagr
               )


       else:
           st.warning("⚠️ Không có dữ liệu thu lãi từ 2014-2024")


   else:
       st.warning("⚠️ Không có cột 'Nam_giai_ngan' trong dữ liệu")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════════
   # ═══════════════════════════════════════════════════════════════════
   # COMBO CHART: Top 10 Chi nhánh (ĐỠN GIẢN - BỎ YIELD)
   # ═══════════════════════════════════════════════════════════════════


   st.markdown("### 📊 Top 10 Chi nhánh: Dư nợ × Thu lãi")


   # ─── TÍNH TOÁN ───
   branch_profit = df.groupby('Ma_chi_nhanh').agg({
       'Goc_vay_con_lai_no_trong_han_no_qua_han': 'sum',
       'Lai_thong_thuong_Da_tra': 'sum'
   }).reset_index()


   branch_profit.columns = ['Ma_chi_nhanh', 'Du_no', 'Thu_lai']


   # Lấy Top 10 theo thu lãi
   top10 = branch_profit.nlargest(10, 'Thu_lai').sort_values('Thu_lai', ascending=True)


   # ─── BẢNG MÀU THEO RANKING ───
   def get_color_by_rank(rank):
       if rank <= 3:
           return '#059669'  # Top 3: Xanh đậm
       elif rank <= 7:
           return '#10b981'  # Top 4-7: Xanh
       else:
           return '#f59e0b'  # Top 8-10: Vàng


   top10['Rank'] = range(10, 0, -1)
   top10['Color'] = top10['Rank'].apply(get_color_by_rank)


   # ─── TẠO COMBO CHART ───
   fig = go.Figure()


   # Bar: Dư nợ
   fig.add_trace(go.Bar(
       x=top10['Ma_chi_nhanh'],
       y=top10['Du_no'] / 1e9,
       name='Dư nợ',
       marker=dict(color=top10['Color']),
       textposition='none',
       yaxis='y',
       hovertemplate='<b>%{x}</b><br>Dư nợ: %{y:.2f}T<extra></extra>'
   ))


   # Line: Thu lãi
   fig.add_trace(go.Scatter(
       x=top10['Ma_chi_nhanh'],
       y=top10['Thu_lai'] / 1e9,
       name='Thu lãi',
       mode='lines+markers',
       line=dict(color='#ef4444', width=3),
       marker=dict(size=10, color='#ef4444'),
       yaxis='y2',
       hovertemplate='<b>%{x}</b><br>Thu lãi: %{y:.2f}T<extra></extra>'
   ))


   # ─── CẤU HÌNH LAYOUT ───
   fig.update_layout(
       title={
           'text': 'Top 10 Chi nhánh theo Thu lãi',
           'font': {'size': 16, 'color': '#1e293b'},
           'x': 0.5,
           'xanchor': 'center'
       },
       xaxis=dict(
           title='Chi nhánh',
           showgrid=False,
           tickfont=dict(size=10, color='#1e293b'),
           tickangle=-45
       ),
       yaxis=dict(
           title=dict(
               text='Dư nợ (Tỷ VNĐ)',
               font=dict(size=12, color='#10b981')
           ),
           showgrid=True,
           gridcolor='#e5e7eb',
           tickfont=dict(size=10, color='#10b981')
       ),
       yaxis2=dict(
           title=dict(
               text='Thu lãi (Tỷ VNĐ)',
               font=dict(size=12, color='#ef4444')
           ),
           overlaying='y',
           side='right',
           showgrid=False,
           tickfont=dict(size=10, color='#ef4444')
       ),
       legend=dict(
           orientation='h',
           yanchor='bottom',
           y=1.02,
           xanchor='right',
           x=1
       ),
       height=450,
       plot_bgcolor='white',
       paper_bgcolor='#f8fafc',
       margin=dict(l=60, r=60, t=100, b=120),
       hovermode='x unified'
   )


   st.plotly_chart(fig, use_container_width=True)


   # ═══════════════════════════════════════════════════════════════════
   # INSIGHT CARDS (ĐƠN GIẢN - BỎ YIELD)
   # ═══════════════════════════════════════════════════════════════════


   col1, col2, col3, col4 = st.columns(4)


   # Top 1
   top1 = top10.iloc[-1]
   with col1:
       st.success(f"""
       🥇 **Top 1: {top1['Ma_chi_nhanh']}**


       Dư nợ: {top1['Du_no'] / 1e9:.1f}T


       Thu lãi: {top1['Thu_lai'] / 1e9:.1f}T
       """)


   # Tổng Top 10
   with col2:
       st.info(f"""
       📊 **Tổng Top 10**


       Dư nợ: {top10['Du_no'].sum() / 1e9:.1f}T


       Thu lãi: {top10['Thu_lai'].sum() / 1e9:.1f}T
       """)


   # % của Top 10
   pct_du_no = (top10['Du_no'].sum() / df['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum() * 100)
   pct_thu_lai = (top10['Thu_lai'].sum() / df['Lai_thong_thuong_Da_tra'].sum() * 100)


   with col3:
       st.info(f"""
       📈 **% Đóng góp**


       Dư nợ: {pct_du_no:.1f}%


       Thu lãi: {pct_thu_lai:.1f}%
       """)


   # Chi nhánh kém nhất
   bottom = top10.iloc[0]
   with col4:
       st.warning(f"""
       ⚠️ **Thấp nhất: {bottom['Ma_chi_nhanh']}**


       Dư nợ: {bottom['Du_no'] / 1e9:.1f}T


       Thu lãi: {bottom['Thu_lai'] / 1e9:.1f}T
       """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════════
   # CHÚ GIẢI (ĐƠN GIẢN)
   # ═══════════════════════════════════════════════════════════════════


   st.info("""
   **📌 Cách đọc biểu đồ:**


   - **Cột (Dư nợ):** Quy mô tín dụng của chi nhánh
     - 🟢 Xanh đậm: Top 3 (Xuất sắc)
     - 🟢 Xanh nhạt: Top 4-7 (Tốt)
     - 🟡 Vàng: Top 8-10 (Trung bình)


   - **Đường đỏ (Thu lãi):** Thu nhập thực tế đã thu được


   **💡 Insight:**
   - **Xếp hạng:** Theo thu lãi (doanh thu thực tế)
   - **Top 10** chiếm phần lớn dư nợ và thu nhập của toàn hệ thống
   - Chi nhánh có **thu lãi cao** = Hiệu quả tốt
   """)




# ═════════════════════════════════════════════════════════════════════
# TAB B: CẤU TRÚC THU NHẬP
# ═════════════════════════════════════════════════════════════════════


def show_income_structure(df):
   """Tab B: Cấu trúc Thu nhập"""


   st.markdown("### 🏗️ Phần B: Cấu trúc Thu nhập")
   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════════
   # BAR CHART NGANG: Cấu trúc Thu nhập theo Sản phẩm (ÁP DỤNG FILTER)
   # ═══════════════════════════════════════════════════════════════════


   st.markdown("### 🌟 Cấu trúc Thu nhập theo Sản phẩm")


   # ─── TÌM CỘT SẢN PHẨM (ƯU TIÊN Sub_productTen_san_pham) ───
   product_col = None


   # Thử tìm cột con trước
   if 'Sub_productTen_san_pham' in df.columns:
       product_col = 'Sub_productTen_san_pham'
   # Nếu không có, tìm cột cha
   elif 'ProductTen_san_pham' in df.columns:
       product_col = 'ProductTen_san_pham'
   # Fallback: Tìm cột khác
   else:
       for col in df.columns:
           if ('product' in col.lower() or 'san_pham' in col.lower()) and 'ten' in col.lower():
               product_col = col
               break


   # ─── TÍNH TOÁN ───
   if product_col and product_col in df.columns:
       # ✅ KIỂM TRA SỐ LƯỢNG SẢN PHẨM
       n_products = df[product_col].nunique()


       if n_products > 1:
           # Tính thu nhập theo sản phẩm (đã filter)
           product_income = df.groupby(product_col).agg({
               'Lai_thong_thuong_Da_tra': 'sum'
           }).reset_index()


           product_income.columns = ['San_pham', 'Thu_nhap']


           # Loại bỏ giá trị null hoặc 0
           product_income = product_income[
               (product_income['San_pham'].notna()) &
               (product_income['Thu_nhap'] > 0)
               ]


           # Kiểm tra lại sau khi lọc
           if len(product_income) > 0:
               # Tính % đóng góp
               total_income = product_income['Thu_nhap'].sum()
               product_income['Pct'] = (product_income['Thu_nhap'] / total_income * 100).round(2)


               # Sắp xếp theo thu nhập giảm dần
               product_income = product_income.sort_values('Thu_nhap', ascending=True)


               # ─── BẢNG MÀU GRADIENT ───
               n = len(product_income)
               colors = []
               for i in range(n):
                   intensity = i / (n - 1) if n > 1 else 0
                   r = int(219 - (219 - 30) * intensity)
                   g = int(234 - (234 - 64) * intensity)
                   b = int(254 - (254 - 175) * intensity)
                   colors.append(f'rgb({r},{g},{b})')


               # ─── TẠO BAR CHART NGANG ───
               fig = go.Figure(go.Bar(
                   x=product_income['Thu_nhap'] / 1e9,
                   y=product_income['San_pham'],
                   orientation='h',
                   marker=dict(
                       color=colors,
                       line=dict(color='white', width=1)
                   ),
                   text=[f"{val / 1e9:.1f}T ({pct:.1f}%)"
                         for val, pct in zip(product_income['Thu_nhap'], product_income['Pct'])],
                   textposition='outside',
                   textfont=dict(size=11, color='#1e293b'),
                   hovertemplate='<b>%{y}</b><br>Thu nhập: %{x:.2f}T<extra></extra>'
               ))


               # ─── CẤU HÌNH LAYOUT ───
               fig.update_layout(
                   title={
                       'text': f'Thu nhập Lãi theo Sản phẩm ({n} loại)',
                       'font': {'size': 16, 'color': '#1e293b'},
                       'x': 0.5,
                       'xanchor': 'center'
                   },
                   xaxis=dict(
                       title='Thu nhập (Tỷ VNĐ)',
                       showgrid=True,
                       gridcolor='#e5e7eb',
                       tickfont=dict(size=10, color='#1e293b')
                   ),
                   yaxis=dict(
                       title='',
                       showgrid=False,
                       tickfont=dict(size=11, color='#1e293b')
                   ),
                   height=max(400, n * 40),  # Động theo số sản phẩm
                   plot_bgcolor='white',
                   paper_bgcolor='#f8fafc',
                   margin=dict(l=250, r=120, t=80, b=60),
                   showlegend=False
               )


               st.plotly_chart(fig, use_container_width=True)


               # ═══════════════════════════════════════════════════════════
               # INSIGHT CARDS
               # ═══════════════════════════════════════════════════════════


               col1, col2, col3, col4 = st.columns(4)


               # Top 1
               top1 = product_income.iloc[-1]
               with col1:
                   st.success(f"""
                   🥇 **Top 1**


                   {top1['San_pham'][:30]}


                   Thu: {top1['Thu_nhap'] / 1e9:.1f}T


                   Đóng góp: {top1['Pct']:.1f}%
                   """)


               # Top 3
               if n >= 3:
                   top3_pct = product_income.nlargest(3, 'Thu_nhap')['Pct'].sum()
                   with col2:
                       st.info(f"""
                       📊 **Top 3**


                       Đóng góp: **{top3_pct:.1f}%**


                       {"Tập trung cao" if top3_pct > 60 else "Đa dạng"}
                       """)
               else:
                   with col2:
                       st.info(f"""
                       📊 **Tổng số**


                       **{n}** sản phẩm


                       Hạn chế
                       """)


               # Số lượng
               with col3:
                   st.info(f"""
                   🔢 **Đa dạng**


                   **{n}** sản phẩm


                   {"Tốt" if n >= 5 else "Cần mở rộng"}
                   """)


               # Thấp nhất
               bottom = product_income.iloc[0]
               with col4:
                   st.warning(f"""
                   ⚠️ **Thấp nhất**


                   {bottom['San_pham'][:30]}


                   Thu: {bottom['Thu_nhap'] / 1e9:.1f}T


                   Đóng góp: {bottom['Pct']:.1f}%
                   """)


               st.markdown("---")


               # CHÚ GIẢI
               st.info("""
               **📌 Cách đọc biểu đồ:**
               Dựa trên LÃI ĐÃ THU (thực tế)  
               Cho biết mỗi sản phẩm đóng góp bao nhiêu doanh thu THỰC
               Đúng logic cho phân tích lợi nhuận!
               - **Cột dài hơn** = Thu nhập cao hơn
               - **Màu đậm hơn** = Đóng góp lớn hơn
               - **Số bên ngoài** = Giá trị (Tỷ) và % đóng góp


               **💡 Insight:**
               - Sản phẩm **đóng góp > 30%** = Trụ cột
               - Top 3 chiếm **> 60%** = Tập trung cao → Rủi ro
               - Sản phẩm **< 5%** = Xem xét tối ưu
               """)


           else:
               st.warning("⚠️ Không có dữ liệu thu nhập sau khi lọc!")


       else:
           # Chỉ có 1 sản phẩm hoặc tất cả giống nhau
           st.warning(f"""
           ⚠️ **Chỉ có 1 loại sản phẩm**: {df[product_col].iloc[0] if len(df) > 0 else 'N/A'}


           Không thể phân tích cấu trúc. Hãy điều chỉnh bộ lọc hoặc dùng cột khác!
           """)


           # Gợi ý
           st.info("""
           💡 **Gợi ý phân tích thay thế:**
           - Theo **Mục đích vay** (Ten_muc_dich_vay)
           - Theo **Sector** (Ma_Sector)
           - Thay đổi bộ lọc để xem nhiều sản phẩm hơn
           """)


   else:
       st.error(f"""
       ⚠️ **Không tìm thấy cột sản phẩm hợp lệ!**


       Các cột hiện có: {', '.join(df.columns.tolist()[:15])}...
       """)


   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # STACKED BAR: Thu lãi theo Chi nhánh Top 10
   # ─────────────────────────────────────────────────────────────────
   st.markdown("#### 📊 Thu lãi theo Chi nhánh (Top 10)")


   branch_income = df.groupby('Ma_chi_nhanh').agg({
       'Lai_thong_thuong_Da_tra': 'sum',
       'Lai_phat_tren_goc_Phai_tra': 'sum',
       'Lai_phat_tren_lai_Phai_tra': 'sum'
   }).reset_index()


   branch_income.columns = ['Chi_nhanh', 'Lai_thuong', 'Lai_phat_goc', 'Lai_phat_lai']
   branch_income['Total'] = branch_income[['Lai_thuong', 'Lai_phat_goc', 'Lai_phat_lai']].sum(axis=1)
   branch_income = branch_income.sort_values('Total', ascending=False).head(10)


   fig_stacked = go.Figure()


   fig_stacked.add_trace(go.Bar(
       name='Lãi thông thường',
       x=branch_income['Chi_nhanh'],
       y=branch_income['Lai_thuong'] / 1e9,
       marker_color='#10b981'
   ))


   fig_stacked.add_trace(go.Bar(
       name='Lãi phạt gốc',
       x=branch_income['Chi_nhanh'],
       y=branch_income['Lai_phat_goc'] / 1e9,
       marker_color='#f59e0b'
   ))


   fig_stacked.add_trace(go.Bar(
       name='Lãi phạt lãi',
       x=branch_income['Chi_nhanh'],
       y=branch_income['Lai_phat_lai'] / 1e9,
       marker_color='#ef4444'
   ))


   fig_stacked.update_layout(
       barmode='stack',
       title='Thu nhập Lãi theo Chi nhánh - Top 10',
       xaxis_title='Chi nhánh',
       yaxis_title='Thu nhập (Tỷ VNĐ)',
       height=450
   )


   st.plotly_chart(fig_stacked, use_container_width=True)


   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # PIE CHART: Cơ cấu Lãi thường + Lãi phạt
   # ─────────────────────────────────────────────────────────────────
   st.markdown("#### 🥧 Cơ cấu Thu nhập Lãi")


   lai_thuong_total = df['Lai_thong_thuong_Da_tra'].sum()
   lai_phat_total = df['Lai_phat_tren_goc_Phai_tra'].sum() + df['Lai_phat_tren_lai_Phai_tra'].sum()


   fig_pie = go.Figure(data=[go.Pie(
       labels=['Lãi thông thường', 'Lãi phạt'],
       values=[lai_thuong_total, lai_phat_total],
       hole=0.4,
       marker=dict(colors=['#10b981', '#ef4444'])
   )])


   fig_pie.update_layout(
       title='Cơ cấu Thu nhập: Lãi thường vs Lãi phạt',
       height=400
   )


   st.plotly_chart(fig_pie, use_container_width=True)




# ═════════════════════════════════════════════════════════════════════
# TAB C: HIỆU SUẤT LÃI SUẤT
# ═════════════════════════════════════════════════════════════════════


def show_interest_performance(df):
   """Tab C: Hiệu suất Lãi suất"""


   st.markdown("### 📈 Phần C: Hiệu suất Lãi suất")
   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # HISTOGRAM: Phân bổ Lãi suất (6%-18%)
   # ─────────────────────────────────────────────────────────────────
   st.markdown("#### 📊 Histogram: Phân bổ Lãi suất")


   df_temp = df[df['Lai_Suat'] > 0].copy()


   fig_hist = px.histogram(
       df_temp,
       x='Lai_Suat',
       nbins=30,
       title='Phân bổ Lãi suất trong danh mục',
       labels={'Lai_Suat': 'Lãi suất (%)', 'count': 'Số lượng HĐ'},
       color_discrete_sequence=['#3b82f6']
   )


   fig_hist.update_layout(
       height=400,
       xaxis_title='Lãi suất (%)',
       yaxis_title='Số lượng HĐ'
   )


   st.plotly_chart(fig_hist, use_container_width=True)


   st.markdown("---")


#def show_interest_rate_analysis(df):
   st.markdown("## 📈 Phân tích lãi suất – Interest Rate Dynamics")


   # Bảo đảm kiểu float để tính trung bình an toàn
   if "Lai_Suat" in df.columns:
       df["Lai_Suat"] = pd.to_numeric(df["Lai_Suat"], errors="coerce")


   # ✅ SỬA: Xu hướng lãi suất theo NĂM (thay vì tháng)
   date_col = "Ngay_giai_ngan_ban_dau_cua_khoan_vay_orig_val_date"


   if date_col in df.columns and "Lai_Suat" in df.columns:
       # Lọc dữ liệu hợp lệ
       df_year = df.dropna(subset=[date_col, "Lai_Suat"]).copy()


       # ✅ Tạo cột NĂM (thay vì tháng)
       df_year["Nam"] = pd.to_datetime(df_year[date_col], errors='coerce').dt.year


       # Lọc bỏ năm NaN
       df_year = df_year.dropna(subset=["Nam"])
       df_year["Nam"] = df_year["Nam"].astype(int)


       # Tính trung bình theo năm
       trend = df_year.groupby("Nam")["Lai_Suat"].mean().reset_index()


       # Sắp xếp theo năm
       trend = trend.sort_values("Nam")


       # Vẽ chart
       st.markdown("#### 📉 1. Xu hướng lãi suất trung bình theo năm")


       fig_trend = px.line(
           trend,
           x="Nam",
           y="Lai_Suat",
           markers=True,
           line_shape="spline",
           color_discrete_sequence=["#1565C0"],
           labels={"Nam": "Năm", "Lai_Suat": "Lãi suất trung bình (%)"}
       )


       fig_trend.update_traces(
           mode="lines+markers",
           marker=dict(size=10, symbol='circle'),
           line=dict(width=3)
       )


       fig_trend.update_layout(
           plot_bgcolor="#F3F7FF",
           yaxis=dict(
               showgrid=True,
               gridcolor="LightGray",
               title="Lãi suất (%)"
           ),
           xaxis=dict(
               showgrid=False,
               title="Năm",
               dtick=1  # ✅ Hiển thị mỗi năm 1 tick
           ),
           height=450
       )


       st.plotly_chart(fig_trend, use_container_width=True)


       # ✅ THÊM: Hiển thị số liệu
       col1, col2, col3 = st.columns(3)


       with col1:
           st.metric(
               "📊 Lãi suất TB toàn kỳ",
               f"{trend['Lai_Suat'].mean():.2f}%"
           )


       with col2:
           if len(trend) > 0:
               last_year = trend.iloc[-1]
               st.metric(
                   f"📈 Năm {int(last_year['Nam'])}",
                   f"{last_year['Lai_Suat']:.2f}%"
               )


       with col3:
           if len(trend) > 1:
               change = trend['Lai_Suat'].iloc[-1] - trend['Lai_Suat'].iloc[-2]
               st.metric(
                   "📊 Thay đổi",
                   f"{change:+.2f}%",
                   delta=f"{change:+.2f}%"
               )


       st.markdown("---")


   else:
       st.warning("⚠️ Không tìm thấy cột ngày giải ngân hoặc lãi suất!")




   # ─────────────────────────────────────────────────────────────────
   # BAR CHART: Lãi suất TB theo sản phẩm - chi nhánh (Top N)
   # ─────────────────────────────────────────────────────────────────
   st.markdown("#### 📊 Lãi suất Trung bình theo Chi nhánh (Top 10)")


   branch_rate = df.groupby('Ma_chi_nhanh').agg({
       'Lai_Suat': 'mean',
       'Goc_vay_con_lai_no_trong_han_no_qua_han': 'sum'
   }).reset_index()


   branch_rate.columns = ['Chi_nhanh', 'Lai_suat_TB', 'Du_no']
   branch_rate = branch_rate.sort_values('Du_no', ascending=False).head(10)


   fig_rate = go.Figure()


   fig_rate.add_trace(go.Bar(
       x=branch_rate['Chi_nhanh'],
       y=branch_rate['Lai_suat_TB'],
       marker_color='#8b5cf6',
       text=branch_rate['Lai_suat_TB'].round(2),
       textposition='outside'
   ))


   fig_rate.update_layout(
       title='Lãi suất Trung bình theo Chi nhánh - Top 10',
       xaxis_title='Chi nhánh',
       yaxis_title='Lãi suất TB (%)',
       height=450
   )


   st.plotly_chart(fig_rate, use_container_width=True)




