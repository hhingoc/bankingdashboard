# ==============================================
# File: dashboard_portfolio.py
# Module: Cơ cấu Danh mục (2 TABS)
# Màu sắc: CHUẨN NGÂN HÀNG theo PDF
# ==============================================


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BẢNG MÀU CHUẨN NGÂN HÀNG (TỪ PDF)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# 1️⃣ PRIMARY COLORS (60% - Màu chủ đạo)
PRIMARY = '#003366'  # Navy Blue - Tin cậy, ổn định
PRIMARY_LIGHT = '#3b82f6'  # Blue - Thân thiện
PRIMARY_BG = '#dbeafe'  # Light Blue - Background


# 2️⃣ SEMANTIC COLORS (30% - Màu ngữ nghĩa)
POSITIVE = '#10b981'  # Xanh lá - Tích cực, tăng trưởng
POSITIVE_DARK = '#22c55e'  # Xanh đậm
NEGATIVE = '#ef4444'  # Đỏ - Rủi ro, tiêu cực
NEGATIVE_DARK = '#dc2626'  # Đỏ đậm
WARNING = '#f59e0b'  # Vàng/Cam - Cảnh báo
WARNING_DARK = '#fb923c'  # Cam đậm
INFO = '#3b82f6'  # Xanh dương - Thông tin


# 3️⃣ GRAYSCALE (10% - Xám chuyên nghiệp)
SLATE_800 = '#1e293b'  # Text chính
SLATE_600 = '#475569'  # Text phụ
SLATE_400 = '#94a3b8'  # Border, icon
SLATE_200 = '#e2e8f0'  # Background card
SLATE_50 = '#f8fafc'  # Background page


# 4️⃣ CATEGORICAL COLORS (6 màu phân biệt)
CATEGORICAL = [
   '#3b82f6',  # Blue - Nhóm 1
   '#10b981',  # Green - Nhóm 2
   '#f59e0b',  # Amber - Nhóm 3
   '#8b5cf6',  # Purple - Nhóm 4
   '#ec4899',  # Pink - Nhóm 5
   '#14b8a6',  # Teal - Nhóm 6
]


# 5️⃣ SCALE COLORS (Thang màu tuần tự)
GREEN_SCALE = ['#f0fdf4', '#dcfce7', '#bbf7d0', '#86efac',
              '#4ade80', '#22c55e', '#16a34a', '#15803d']


RED_SCALE = ['#fef2f2', '#fee2e2', '#fecaca', '#fca5a5',
            '#f87171', '#ef4444', '#dc2626', '#b91c1c']




def show_portfolio_composition(df):
   """📦 Module Cơ cấu Danh mục"""


   st.header("📦 Cơ cấu Danh mục")
   st.caption(f"📊 Phân tích {len(df):,} hợp đồng | Dữ liệu đến 06/08/2025")


   tab_a, tab_b  = st.tabs([
       "📊 A. PHÂN BỔ SẢN PHẨM",
       "🌍 B. PHÂN BỐ ĐỊA LÝ",


   ])


   with tab_a:
       show_product_allocation(df)


   with tab_b:
       show_geographic_distribution(df)






# ═════════════════════════════════════════════════════════════════════
def show_product_allocation(df):
   """Tab A: Phân bổ Sản phẩm - BỐ CỤC GRID CHUYÊN NGHIỆP"""


   st.markdown("### 📊 Phần A: Phân bổ Sản phẩm")
   st.markdown("---")


   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'


   # ═══════════════════════════════════════════════════════════════
   # TÍNH TOÁN CƠ BẢN
   # ═══════════════════════════════════════════════════════════════
   if 'Sub_productTen_san_pham' not in df.columns:
       st.error("⚠️ Không có cột Sub_productTen_san_pham")
       return


   # STATS theo SẢN PHẨM
   product_stats = df.groupby('Sub_productTen_san_pham').agg({
       outstanding_col: 'sum',
       'Ma_khach_hang': 'count'
   }).reset_index()


   product_stats.columns = ['Product', 'Debt', 'Count']
   product_stats['Pct'] = (product_stats['Debt'] / product_stats['Debt'].sum() * 100)
   product_stats['Debt_Ty'] = product_stats['Debt'] / 1e9
   product_stats['Avg_Per_Contract'] = product_stats['Debt'] / product_stats['Count']
   product_stats = product_stats.sort_values('Debt', ascending=False)


   # TỔNG QUAN
   total_debt = df[outstanding_col].sum()
   total_contracts = len(df)
   num_products = len(product_stats)
   top3_concentration = product_stats.head(3)['Pct'].sum()
   avg_per_contract = total_debt / total_contracts


   # ═══════════════════════════════════════════════════════════════
   # 4 KPI CARDS - HÀNG ĐẦU
   # ═══════════════════════════════════════════════════════════════
   col1, col2, col3, col4 = st.columns(4)


   with col1:
       st.metric("💰 Tổng Dư nợ", f"{total_debt / 1e9:.2f} tỷ", f"{total_contracts:,} HĐ")


   with col2:
       st.metric("🎯 Số SP", f"{num_products}", f"{num_products} loại")


   with col3:
       concentration_status = "Tập trung" if top3_concentration > 75 else "Cân bằng" if top3_concentration > 50 else "Phân tán"
       st.metric("📊 Top 3", f"{top3_concentration:.1f}%", concentration_status)


   with col4:
       st.metric("📈 TB/HĐ", f"{avg_per_contract / 1e6:.1f}M", f"{avg_per_contract / 1e9:.3f} tỷ")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # GRID LAYOUT: 2 HÀNG × 3 CỘT (GIỐNG HÌNH MẪU)
   # ═══════════════════════════════════════════════════════════════


   # ─── HÀNG 1: 2 CHARTS LỚN + 1 TABLE ───
   col_row1_a, col_row1_b = st.columns([1, 1])


   with col_row1_a:
       st.markdown("#### 🌳 Treemap: Phân bổ SP")


       top10_tree = product_stats.head(10)


       fig_tree = go.Figure(go.Treemap(
           labels=top10_tree['Product'].str[:30],
           parents=[""] * len(top10_tree),
           values=top10_tree['Debt'],
           text=[f"{x:.1f}T" for x in top10_tree['Debt_Ty']],
           textposition="middle center",
           marker=dict(
               colors=top10_tree['Debt_Ty'],
               colorscale=[[0, PRIMARY_BG], [0.5, PRIMARY_LIGHT], [1, PRIMARY]],
               showscale=False
           ),
           hovertemplate='<b>%{label}</b><br>%{value:,.0f} VNĐ<extra></extra>'
       ))


       fig_tree.update_layout(
           height=400,
           margin=dict(l=10, r=10, t=30, b=10),
           paper_bgcolor=SLATE_50
       )


       st.plotly_chart(fig_tree, use_container_width=True)


   with col_row1_b:
       st.markdown("#### 💎 Bubble: Dư nợ × Số HĐ")


       top15 = product_stats.head(15).copy()


       fig_bubble = go.Figure(
           go.Scatter(
               x=top15['Count'],
               y=top15['Debt_Ty'],
               mode='markers+text',
               marker=dict(
                   size=top15['Pct'] * 3,  # Tăng size
                   color=top15['Debt_Ty'],
                   colorscale=[[0, PRIMARY_BG], [0.5, POSITIVE], [1, PRIMARY]],
                   showscale=False,
                   line=dict(width=2, color='white')
               ),
               text=top15['Product'].str[:8],
               textposition='top center',
               textfont=dict(size=8, color=SLATE_800),
               hovertemplate='<b>%{text}</b><br>Số HĐ: %{x:,}<br>Dư nợ: %{y:.2f} tỷ<extra></extra>'
           )
       )


       fig_bubble.update_layout(
           xaxis=dict(title="Số HĐ", showgrid=True, gridcolor=SLATE_200, tickfont=dict(size=10)),
           yaxis=dict(title="Dư nợ (tỷ)", showgrid=True, gridcolor=SLATE_200, tickfont=dict(size=10)),
           height=400,
           plot_bgcolor='white',
           paper_bgcolor=SLATE_50,
           margin=dict(l=50, r=20, t=30, b=50)
       )


       st.plotly_chart(fig_bubble, use_container_width=True)


   # ─── TABLE BREAKDOWN (DƯỚI TREEMAP) ───
   st.markdown("#### 📋 Breakdown Top 10")


   table_display = product_stats.head(10)[['Product', 'Count', 'Debt_Ty', 'Pct']].copy()
   table_display['Product'] = table_display['Product'].str[:40]
   table_display.columns = ['Sản phẩm', 'Số HĐ', 'Dư nợ (tỷ)', 'Tỷ trọng (%)']


   st.dataframe(
       table_display.style.format({
           'Số HĐ': '{:,}',
           'Dư nợ (tỷ)': '{:.2f}',
           'Tỷ trọng (%)': '{:.1f}%'
       }).background_gradient(cmap='Blues', subset=['Dư nợ (tỷ)', 'Tỷ trọng (%)']),
       use_container_width=True,
       height=350
   )


   st.markdown("---")


   # ─── HÀNG 2: 3 CHARTS NHỎ ───
   col_row2_a, col_row2_b, col_row2_c = st.columns(3)


   with col_row2_a:
       st.markdown("#### 📊 Top 5 Dư nợ")


       top5_bar = product_stats.head(5).sort_values('Debt_Ty', ascending=True)


       fig_top5 = go.Figure(go.Bar(
           y=top5_bar['Product'].str[:20],
           x=top5_bar['Debt_Ty'],
           orientation='h',
           marker_color=PRIMARY,
           text=[f"{x:.1f}T" for x in top5_bar['Debt_Ty']],
           textposition='outside',
           textfont=dict(size=10, color=SLATE_800),
           hovertemplate='<b>%{y}</b><br>%{x:.2f} tỷ<extra></extra>'
       ))


       fig_top5.update_layout(
           xaxis=dict(title="", showgrid=False, showticklabels=False),
           yaxis=dict(tickfont=dict(size=9)),
           height=350,
           showlegend=False,
           plot_bgcolor='white',
           paper_bgcolor=SLATE_50,
           margin=dict(l=10, r=60, t=10, b=30)
       )


       st.plotly_chart(fig_top5, use_container_width=True)


   with col_row2_b:
       st.markdown("#### 📈 Xu hướng Top 3")


       if 'Year' in df.columns:
           top3_products = product_stats.head(3)['Product'].tolist()


           trend_data = df[df['Sub_productTen_san_pham'].isin(top3_products)].groupby(
               ['Year', 'Sub_productTen_san_pham']
           )[outstanding_col].sum().reset_index()


           trend_data['Debt_Ty'] = trend_data[outstanding_col] / 1e9


           fig_trend = go.Figure()


           for i, product in enumerate(top3_products):
               product_data = trend_data[trend_data['Sub_productTen_san_pham'] == product]


               fig_trend.add_trace(go.Scatter(
                   name=product[:15],
                   x=product_data['Year'],
                   y=product_data['Debt_Ty'],
                   mode='lines+markers',
                   line=dict(color=CATEGORICAL[i], width=2),
                   marker=dict(size=6),
                   hovertemplate='<b>%{fullData.name}</b><br>%{y:.1f}T<extra></extra>'
               ))


           fig_trend.update_layout(
               xaxis=dict(tickmode='linear', dtick=1, tickfont=dict(size=9)),
               yaxis=dict(showgrid=True, gridcolor=SLATE_200, tickfont=dict(size=9)),
               showlegend=True,
               legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(size=8)),
               height=350,
               plot_bgcolor='white',
               paper_bgcolor=SLATE_50,
               margin=dict(l=40, r=10, t=10, b=80)
           )


           st.plotly_chart(fig_trend, use_container_width=True)


   with col_row2_c:
       st.markdown("#### 🍩 Top 5 Tỷ trọng")


       top5_donut = product_stats.head(5)
       other = product_stats.iloc[5:]['Debt'].sum() if len(product_stats) > 5 else 0


       if other > 0:
           donut_data = pd.concat([
               top5_donut,
               pd.DataFrame([{'Product': 'Khác', 'Debt': other}])
           ], ignore_index=True)
       else:
           donut_data = top5_donut.copy()


       color_map = {k: CATEGORICAL[i % len(CATEGORICAL)] for i, k in enumerate(donut_data['Product'])}


       fig_donut = go.Figure(go.Pie(
           labels=donut_data['Product'].str[:15],
           values=donut_data['Debt'],
           hole=0.5,
           marker=dict(colors=[color_map[p] for p in donut_data['Product']]),
           textinfo='percent',
           textfont=dict(size=10),
           hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
       ))


       fig_donut.update_layout(
           height=350,
           showlegend=True,
           legend=dict(orientation="h", yanchor="bottom", y=-0.2, font=dict(size=7)),
           paper_bgcolor=SLATE_50,
           margin=dict(l=10, r=10, t=10, b=60)
       )


       st.plotly_chart(fig_donut, use_container_width=True)




# ═════════════════════════════════════════════════════════════════════
def show_geographic_distribution(df):
   """Tab B: Phân bố Địa lý - GRID LAYOUT"""


   st.markdown("### 🌍 Phần B: Phân bố Địa lý")
   st.markdown("---")


   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'


   # ═══════════════════════════════════════════════════════════════
   # 4 KPI CARDS - ĐỊA LÝ
   # ═══════════════════════════════════════════════════════════════
   col1, col2, col3, col4 = st.columns(4)


   if 'Vung' in df.columns:
       total_regions = df['Vung'].nunique()
       total_branches = df['Ma_chi_nhanh'].nunique()
       total_geo_debt = df[outstanding_col].sum()


       # Top vùng
       top_region = df.groupby('Vung')[outstanding_col].sum().idxmax()
       top_region_debt = df.groupby('Vung')[outstanding_col].sum().max()


       with col1:
           st.metric("🌏 Số Vùng", f"{total_regions}", "Phủ sóng")


       with col2:
           st.metric("🏢 Số Chi nhánh", f"{total_branches}", f"{total_regions} vùng")


       with col3:
           st.metric("🥇 Vùng dẫn đầu", top_region, f"{top_region_debt / 1e9:.1f}T")


       with col4:
           avg_per_branch = total_geo_debt / total_branches
           st.metric("📊 TB/Chi nhánh", f"{avg_per_branch / 1e9:.2f}T", f"~{avg_per_branch / 1e6:.0f}M")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 1: TREEMAP LỚN (FULL WIDTH)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🌳 Treemap: Vùng → Khu vực → Chi nhánh")


   if 'Vung' in df.columns and 'Khu_vuc' in df.columns:
       treemap_data = df.groupby(['Vung', 'Khu_vuc', 'Ma_chi_nhanh'])[outstanding_col].sum().reset_index()
       treemap_data.columns = ['Vung', 'Khu_vuc', 'Chi_nhanh', 'Debt']


       fig_treemap = px.treemap(
           treemap_data,
           path=['Vung', 'Khu_vuc', 'Chi_nhanh'],
           values='Debt',
           color='Debt',
           color_continuous_scale='Greens',
           hover_data={'Debt': ':,.0f'}
       )


       fig_treemap.update_layout(
           height=500,
           margin=dict(l=10, r=10, t=30, b=10),
           paper_bgcolor=SLATE_50
       )


       st.plotly_chart(fig_treemap, use_container_width=True)
   else:
       st.warning("⚠️ Không có đầy đủ dữ liệu Vùng/Khu vực")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 2: 3 CHARTS (VÙNG | KHU VỰC | CHI NHÁNH)
   # ═══════════════════════════════════════════════════════════════
   col_row2_a, col_row2_b, col_row2_c = st.columns(3)


   with col_row2_a:
       st.markdown("#### 📊 Dư nợ theo Vùng")


       if 'Vung' in df.columns:
           vung_stats = df.groupby('Vung')[outstanding_col].sum().reset_index()
           vung_stats.columns = ['Vung', 'Debt']
           vung_stats = vung_stats.sort_values('Debt', ascending=True)


           fig_vung = go.Figure(go.Bar(
               y=vung_stats['Vung'],
               x=vung_stats['Debt'] / 1e9,
               orientation='h',
               marker_color=POSITIVE,
               text=[f"{x:.1f}T" for x in vung_stats['Debt'] / 1e9],
               textposition='outside',
               textfont=dict(size=10, color=SLATE_800),
               hovertemplate='<b>%{y}</b><br>%{x:.2f} tỷ<extra></extra>'
           ))


           fig_vung.update_layout(
               xaxis=dict(title="", showgrid=False, showticklabels=False),
               yaxis=dict(tickfont=dict(size=10)),
               height=350,
               showlegend=False,
               plot_bgcolor='white',
               paper_bgcolor=SLATE_50,
               margin=dict(l=10, r=60, t=10, b=30)
           )


           st.plotly_chart(fig_vung, use_container_width=True)


   with col_row2_b:
       st.markdown("#### 🏙️ Top 10 Khu vực")


       if 'Khu_vuc' in df.columns:
           kv_stats = df.groupby('Khu_vuc')[outstanding_col].sum().reset_index()
           kv_stats.columns = ['Khu_vuc', 'Debt']
           kv_stats = kv_stats.nlargest(10, 'Debt').sort_values('Debt', ascending=True)


           fig_kv = go.Figure(go.Bar(
               y=kv_stats['Khu_vuc'],
               x=kv_stats['Debt'] / 1e9,
               orientation='h',
               marker_color=PRIMARY_LIGHT,
               text=[f"{x:.1f}T" for x in kv_stats['Debt'] / 1e9],
               textposition='outside',
               textfont=dict(size=9, color=SLATE_800),
               hovertemplate='<b>%{y}</b><br>%{x:.2f} tỷ<extra></extra>'
           ))


           fig_kv.update_layout(
               xaxis=dict(title="", showgrid=False, showticklabels=False),
               yaxis=dict(tickfont=dict(size=8)),
               height=350,
               showlegend=False,
               plot_bgcolor='white',
               paper_bgcolor=SLATE_50,
               margin=dict(l=10, r=50, t=10, b=30)
           )


           st.plotly_chart(fig_kv, use_container_width=True)


   with col_row2_c:
       st.markdown("#### 🏢 Top 10 Chi nhánh")


       if 'Ma_chi_nhanh' in df.columns:
           branch_stats = df.groupby('Ma_chi_nhanh')[outstanding_col].sum().reset_index()
           branch_stats.columns = ['Branch', 'Debt']
           branch_stats = branch_stats.nlargest(10, 'Debt').sort_values('Debt', ascending=True)


           fig_branch = go.Figure(go.Bar(
               y=branch_stats['Branch'],
               x=branch_stats['Debt'] / 1e9,
               orientation='h',
               marker_color=PRIMARY,
               text=[f"{x:.1f}T" for x in branch_stats['Debt'] / 1e9],
               textposition='outside',
               textfont=dict(size=9, color=SLATE_800),
               hovertemplate='<b>%{y}</b><br>%{x:.2f} tỷ<extra></extra>'
           ))


           fig_branch.update_layout(
               xaxis=dict(title="", showgrid=False, showticklabels=False),
               yaxis=dict(tickfont=dict(size=8)),
               height=350,
               showlegend=False,
               plot_bgcolor='white',
               paper_bgcolor=SLATE_50,
               margin=dict(l=10, r=50, t=10, b=30)
           )


           st.plotly_chart(fig_branch, use_container_width=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 3: TABLE CHI TIẾT (FULL WIDTH)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📋 Chi tiết Top 15 Chi nhánh")


   if 'Vung' in df.columns:
       geo_table = df.groupby(['Vung', 'Khu_vuc', 'Ma_chi_nhanh']).agg({
           outstanding_col: 'sum',
           'Ma_khach_hang': 'count'
       }).reset_index()


       geo_table.columns = ['Vùng', 'Khu vực', 'Chi nhánh', 'Dư nợ (VNĐ)', 'Số HĐ']
       geo_table['Dư nợ (tỷ)'] = (geo_table['Dư nợ (VNĐ)'] / 1e9).round(2)
       geo_table['Tỷ trọng (%)'] = (geo_table['Dư nợ (VNĐ)'] / geo_table['Dư nợ (VNĐ)'].sum() * 100).round(2)
       geo_table = geo_table.sort_values('Dư nợ (VNĐ)', ascending=False).head(15)


       st.dataframe(
           geo_table[['Vùng', 'Khu vực', 'Chi nhánh', 'Số HĐ', 'Dư nợ (tỷ)', 'Tỷ trọng (%)']].style.format({
               'Số HĐ': '{:,}',
               'Dư nợ (tỷ)': '{:.2f}',
               'Tỷ trọng (%)': '{:.1f}%'
           }).background_gradient(cmap='Greens', subset=['Dư nợ (tỷ)', 'Tỷ trọng (%)']),
           use_container_width=True,
           height=400
       )


       st.caption("📊 Top 15 Chi nhánh theo Dư nợ")






