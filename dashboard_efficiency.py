# ==============================================
# File: dashboard_efficiency.py
# Module: Hiệu quả Hoạt động (3 TABS)
# ==============================================


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from colors_config import *




# ═════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═════════════════════════════════════════════════════════════════════


def show_efficiency_section(df):
   """Main function cho module Hiệu quả Hoạt động"""


   st.title("⚡ Hiệu quả Hoạt động")


   # 2 TABS
   tab1, tab2  = st.tabs([
       "📊 A. Hiệu suất Chi nhánh",
       "📈 B. Phân tích Năng suất",
   ])


   with tab1:
       show_branch_performance(df)


   with tab2:
       show_productivity_analysis(df)






def show_branch_performance(df):
   """Tab A: Hiệu suất Chi nhánh - Bố cục Professional"""


   st.markdown("### 📊 Phần A: Hiệu suất Chi nhánh")
   st.markdown("---")


   # CHUẨN HÓA DỮ LIỆU
   df_temp = df.copy()
   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'
   interest_col = 'Lai_thong_thuong_Da_tra'


   df_temp[outstanding_col] = pd.to_numeric(df_temp[outstanding_col], errors='coerce').fillna(0)
   df_temp[interest_col] = pd.to_numeric(df_temp[interest_col], errors='coerce').fillna(0)


   # Tính toán theo chi nhánh
   branch_perf = df_temp.groupby('Ma_chi_nhanh').agg({
       outstanding_col: 'sum',
       interest_col: 'sum',
       'Ma_khach_hang': 'count'
   }).reset_index()


   branch_perf.columns = ['Chi_nhanh', 'Du_no', 'Thu_lai', 'So_HD']
   branch_perf['Du_no_per_HD'] = branch_perf['Du_no'] / branch_perf['So_HD']
   branch_perf['Thu_lai_per_HD'] = branch_perf['Thu_lai'] / branch_perf['So_HD']
   branch_perf['Efficiency_Ratio'] = (branch_perf['Thu_lai'] / branch_perf['Du_no'] * 100)


   total_debt = branch_perf['Du_no'].sum()
   total_income = branch_perf['Thu_lai'].sum()
   total_contracts = branch_perf['So_HD'].sum()
   avg_efficiency = (total_income / total_debt * 100) if total_debt > 0 else 0


   # ═══════════════════════════════════════════════════════════════
   # ═══════════════════════════════════════════════════════════════
   # HÀNG 1: 4 KPI CARDS (PURPLE-BLUE GRADIENT)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 💎 Chỉ số Hiệu quả Hoạt động")


   col1, col2, col3, col4 = st.columns(4)


   avg_debt_per_hd = total_debt / total_contracts if total_contracts > 0 else 0
   avg_income_per_hd = total_income / total_contracts if total_contracts > 0 else 0


   # Card 1: Dư nợ TB/HĐ (Gradient: Tím → Tím đậm)
   with col1:
       st.markdown(f"""
       <div style='background: linear-gradient(135deg, #8b5cf6, #7c3aed); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💰 Dư nợ TB/HĐ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{avg_debt_per_hd / 1e9:.2f} tỷ</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Trung bình mỗi hợp đồng</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 2: Thu lãi TB/HĐ (Gradient: Xanh dương → Xanh đậm)
   with col2:
       st.markdown(f"""
       <div style='background: linear-gradient(135deg, #3b82f6, #2563eb); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💸 Thu lãi TB/HĐ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{avg_income_per_hd / 1e6:.1f} triệu</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Thu nhập trung bình/HĐ</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 3: Efficiency Ratio (Gradient thay đổi theo giá trị)
   with col3:
       if avg_efficiency >= 7:
           gradient = "linear-gradient(135deg, #10b981, #059669)"  # Xanh lá - Excellent
           status = "✨ Xuất sắc"
       elif avg_efficiency >= 5:
           gradient = "linear-gradient(135deg, #06b6d4, #0891b2)"  # Cyan - Good
           status = "✅ Tốt"
       elif avg_efficiency >= 3:
           gradient = "linear-gradient(135deg, #f59e0b, #d97706)"  # Cam - Average
           status = "⚠️ Trung bình"
       else:
           gradient = "linear-gradient(135deg, #ef4444, #dc2626)"  # Đỏ - Poor
           status = "❌ Cần cải thiện"


       st.markdown(f"""
       <div style='background: {gradient}; border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📊 Efficiency Ratio</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{avg_efficiency:.2f}%</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>{status}</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 4: Số Chi nhánh (Gradient: Indigo)
   with col4:
       st.markdown(f"""
       <div style='background: linear-gradient(135deg, #6366f1, #4f46e5); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>🏢 Số Chi nhánh</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{len(branch_perf)}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Chi nhánh hoạt động</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 2: TREEMAP (TRÁI) × SCATTER (PHẢI) - PURPLE-BLUE THEME
   # ═══════════════════════════════════════════════════════════════
   col_left, col_right = st.columns([1, 1])


   # DARK THEME COLORS
   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   with col_left:
       st.markdown("#### 🌳 Treemap: Cơ cấu Dư nợ theo Chi nhánh")
       st.caption("📍 Top 20 chi nhánh có dư nợ lớn nhất")


       # Treemap
       top20_tree = branch_perf.nlargest(20, 'Du_no')


       fig_treemap = go.Figure(go.Treemap(
           labels=top20_tree['Chi_nhanh'],
           parents=[''] * len(top20_tree),
           values=top20_tree['Du_no'],
           text=[f"{x / 1e9:.1f} tỷ" for x in top20_tree['Du_no']],
           textposition='middle center',
           textfont=dict(size=12, color='white', weight=600),
           marker=dict(
               # Purple-Blue gradient colorscale
               colorscale=[
                   [0, '#8b5cf6'],  # Purple light
                   [0.3, '#7c3aed'],  # Purple
                   [0.6, '#6366f1'],  # Indigo
                   [1, '#3b82f6']  # Blue
               ],
               line=dict(width=2, color=DARK_COLORS['bg_card'])
           ),
           hovertemplate="<b>%{label}</b><br>" +
                         "Dư nợ: <b>%{value:,.0f} VNĐ</b><br>" +
                         "<extra></extra>"
       ))


       fig_treemap.update_layout(
           height=450,
           margin=dict(l=10, r=10, t=10, b=10),
           paper_bgcolor='rgba(0,0,0,0)',
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_treemap, use_container_width=True, key="eff_treemap_branch")


   with col_right:
       st.markdown("#### 📊 Scatter: Ma trận Hiệu suất")
       st.caption("📍 Kích thước bong bóng = Số hợp đồng | Màu sắc = Efficiency Ratio")


       # Scatter Plot
       fig_scatter = go.Figure()


       fig_scatter.add_trace(go.Scatter(
           x=branch_perf['Du_no_per_HD'] / 1e9,
           y=branch_perf['Thu_lai_per_HD'] / 1e6,
           mode='markers',
           marker=dict(
               size=branch_perf['So_HD'] / 10,
               color=branch_perf['Efficiency_Ratio'],
               # Purple-Blue-Green gradient cho efficiency
               colorscale=[
                   [0, '#ef4444'],  # Đỏ - Poor (<3%)
                   [0.3, '#f59e0b'],  # Cam - Average (3-5%)
                   [0.6, '#06b6d4'],  # Cyan - Good (5-7%)
                   [1, '#10b981']  # Xanh lá - Excellent (>7%)
               ],
               showscale=True,
               colorbar=dict(
                   title=dict(
                       text="Efficiency (%)",
                       font=dict(size=11, color=DARK_COLORS['text_white'])
                   ),
                   tickfont=dict(size=10, color=DARK_COLORS['text_white']),
                   x=1.02,
                   bgcolor='rgba(15, 23, 42, 0.8)',
                   bordercolor=DARK_COLORS['grid'],
                   borderwidth=1
               ),
               line=dict(width=2, color=DARK_COLORS['bg_card'])
           ),
           text=branch_perf['Chi_nhanh'],
           hovertemplate="<b>%{text}</b><br>" +
                         "Dư nợ/HĐ: <b>%{x:.2f} tỷ</b><br>" +
                         "Thu lãi/HĐ: <b>%{y:.1f} triệu</b><br>" +
                         "Số HĐ: <b>" + branch_perf['So_HD'].astype(str) + "</b><br>" +
                         "<extra></extra>"
       ))


       # Đường median
       median_debt = branch_perf['Du_no_per_HD'].median() / 1e9
       median_income = branch_perf['Thu_lai_per_HD'].median() / 1e6


       fig_scatter.add_vline(
           x=median_debt,
           line_dash="dash",
           line_color='#8b5cf6',
           line_width=2,
           annotation_text="Median Dư nợ",
           annotation_position="top",
           annotation=dict(font=dict(size=10, color='#8b5cf6'))
       )


       fig_scatter.add_hline(
           y=median_income,
           line_dash="dash",
           line_color='#3b82f6',
           line_width=2,
           annotation_text="Median Thu lãi",
           annotation_position="right",
           annotation=dict(font=dict(size=10, color='#3b82f6'))
       )


       fig_scatter.update_layout(
           height=450,
           xaxis=dict(
               title=dict(
                   text="<b>Dư nợ TB/HĐ (Tỷ VNĐ)</b>",
                   font=dict(size=11, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               showgrid=True,
               gridcolor=DARK_COLORS['grid'],
               gridwidth=1,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           yaxis=dict(
               title=dict(
                   text="<b>Thu lãi TB/HĐ (Triệu VNĐ)</b>",
                   font=dict(size=11, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               showgrid=True,
               gridcolor=DARK_COLORS['grid'],
               gridwidth=1,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=60, r=100, t=20, b=60),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_scatter, use_container_width=True, key="eff_scatter_performance")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 3: TOP 10 BAR (TRÁI) × HEATMAP (PHẢI) - PURPLE-BLUE THEME
   # ═══════════════════════════════════════════════════════════════
   col_left2, col_right2 = st.columns([1, 1])


   with col_left2:
       st.markdown("#### 🏆 Top 10 Chi nhánh - Efficiency cao nhất")
       st.caption("📍 Xếp hạng theo tỷ lệ Thu lãi/Dư nợ")


       top10 = branch_perf.nlargest(10, 'Efficiency_Ratio')


       # Dynamic colors theo efficiency
       colors_bar = []
       for x in top10['Efficiency_Ratio']:
           if x >= 7:
               colors_bar.append('#10b981')  # Xanh lá - Excellent
           elif x >= 5:
               colors_bar.append('#06b6d4')  # Cyan - Good
           elif x >= 3:
               colors_bar.append('#f59e0b')  # Cam - Average
           else:
               colors_bar.append('#ef4444')  # Đỏ - Poor


       fig_top10 = go.Figure()


       fig_top10.add_trace(go.Bar(
           x=top10['Chi_nhanh'],
           y=top10['Efficiency_Ratio'],
           marker=dict(
               color=colors_bar,
               line=dict(color=DARK_COLORS['bg_card'], width=2)
           ),
           text=[f"{x:.2f}%" for x in top10['Efficiency_Ratio']],
           textposition='outside',
           textfont=dict(size=11, color=DARK_COLORS['text_white'], weight=600),
           hovertemplate='<b>%{x}</b><br>Efficiency: <b>%{y:.2f}%</b><extra></extra>'
       ))


       # Threshold lines
       fig_top10.add_hline(
           y=7,
           line_dash="dash",
           line_color='#10b981',
           line_width=2,
           annotation_text="Excellent (7%)",
           annotation_position="right",
           annotation=dict(font=dict(size=10, color='#10b981'))
       )


       fig_top10.add_hline(
           y=5,
           line_dash="dot",
           line_color='#06b6d4',
           line_width=2,
           annotation_text="Good (5%)",
           annotation_position="right",
           annotation=dict(font=dict(size=10, color='#06b6d4'))
       )


       fig_top10.update_layout(
           height=450,
           xaxis=dict(
               title="",
               tickangle=-45,
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               showgrid=False,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           yaxis=dict(
               title=dict(
                   text="<b>Efficiency Ratio (%)</b>",
                   font=dict(size=11, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               showgrid=True,
               gridcolor=DARK_COLORS['grid'],
               gridwidth=1,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=60, r=30, t=20, b=110),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_top10, use_container_width=True, key="eff_bar_top10_efficiency")


   with col_right2:
       st.markdown("#### 🔥 Heatmap: Dư nợ Chi nhánh × Nhóm nợ")
       st.caption("📍 Top 10 chi nhánh có tổng dư nợ cao nhất")


       # Heatmap
       df_temp['Nhom_no_KH'] = pd.to_numeric(df_temp['Nhom_no_KH'], errors='coerce').fillna(1).astype(int)
       heatmap_data = df_temp.groupby(['Ma_chi_nhanh', 'Nhom_no_KH'])[outstanding_col].sum().reset_index()


       heatmap_pivot = heatmap_data.pivot(
           index='Ma_chi_nhanh',
           columns='Nhom_no_KH',
           values=outstanding_col
       ).fillna(0) / 1e9


       heatmap_pivot['Total'] = heatmap_pivot.sum(axis=1)
       heatmap_pivot = heatmap_pivot.nlargest(10, 'Total').drop('Total', axis=1)
       heatmap_pivot.columns = [f'N{int(col)}' for col in heatmap_pivot.columns]


       fig_heatmap = go.Figure(data=go.Heatmap(
           z=heatmap_pivot.values,
           x=heatmap_pivot.columns,
           y=heatmap_pivot.index,
           # Purple-Blue gradient cho heatmap
           colorscale=[
               [0, '#1e293b'],  # Navy dark (0)
               [0.2, '#8b5cf6'],  # Purple (low)
               [0.5, '#6366f1'],  # Indigo (medium)
               [0.8, '#3b82f6'],  # Blue (high)
               [1, '#06b6d4']  # Cyan (highest)
           ],
           text=[[f"{val:.1f}" if val > 0 else "" for val in row] for row in heatmap_pivot.values],
           texttemplate="%{text}",
           textfont=dict(size=10, color='white', weight=600),
           colorbar=dict(
               title=dict(
                   text="Dư nợ (Tỷ)",
                   font=dict(size=11, color=DARK_COLORS['text_white'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               x=1.02,
               bgcolor='rgba(15, 23, 42, 0.8)',
               bordercolor=DARK_COLORS['grid'],
               borderwidth=1
           ),
           hovertemplate='<b>%{y}</b><br>Nhóm nợ: <b>%{x}</b><br>Dư nợ: <b>%{z:.1f} tỷ</b><extra></extra>'
       ))


       fig_heatmap.update_layout(
           height=450,
           xaxis=dict(
               title=dict(
                   text="<b>Nhóm nợ</b>",
                   font=dict(size=11, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               side='top',
               showgrid=False
           ),
           yaxis=dict(
               title="",
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               autorange='reversed',
               showgrid=False
           ),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=90, r=80, t=60, b=30),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_heatmap, use_container_width=True, key="eff_heatmap_debt")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 4: WATERFALL (TRÁI) × COMBO (PHẢI) - PURPLE-BLUE THEME
   # ═══════════════════════════════════════════════════════════════
   col_left3, col_right3 = st.columns([1, 1])


   with col_left3:
       st.markdown("#### 💧 Waterfall: Phân rã Thu lãi (Top 10)")
       st.caption("📍 Đóng góp của từng chi nhánh vào tổng thu lãi")


       top10_income = branch_perf.nlargest(10, 'Thu_lai')
       other_income = total_income - top10_income['Thu_lai'].sum()


       waterfall_values = [0] + (top10_income['Thu_lai'] / 1e9).tolist() + [other_income / 1e9, total_income / 1e9]
       waterfall_labels = ['Bắt đầu'] + top10_income['Chi_nhanh'].tolist() + ['Còn lại', 'Tổng']
       waterfall_measures = ['total'] + ['relative'] * 11 + ['total']


       fig_waterfall = go.Figure(go.Waterfall(
           x=waterfall_labels,
           y=waterfall_values,
           measure=waterfall_measures,
           text=[f"{v:.1f}" if v != 0 else "" for v in waterfall_values],
           textposition='outside',
           textfont=dict(size=10, color=DARK_COLORS['text_white'], weight=600),
           connector=dict(line=dict(color=DARK_COLORS['grid'], width=2)),
           # Purple-Blue gradient cho waterfall
           increasing=dict(marker=dict(color='#8b5cf6')),  # Purple cho các bar tăng
           decreasing=dict(marker=dict(color='#ef4444')),  # Đỏ nếu có giảm
           totals=dict(marker=dict(color='#3b82f6'))  # Blue cho tổng
       ))


       fig_waterfall.update_layout(
           height=450,
           xaxis=dict(
               title="",
               tickangle=-45,
               tickfont=dict(size=9, color=DARK_COLORS['text_white']),
               showgrid=False,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           yaxis=dict(
               title=dict(
                   text="<b>Thu lãi (Tỷ VNĐ)</b>",
                   font=dict(size=11, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               showgrid=True,
               gridcolor=DARK_COLORS['grid'],
               gridwidth=1,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           showlegend=False,
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=60, r=20, t=20, b=110),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_waterfall, use_container_width=True)


   with col_right3:
       st.markdown("#### 📊 Combo: Số HĐ × Dư nợ TB/HĐ (Top 15)")
       st.caption("📍 Quy mô vs Giá trị trung bình mỗi hợp đồng")


       top15 = branch_perf.nlargest(15, 'So_HD')


       fig_combo = make_subplots(specs=[[{"secondary_y": True}]])


       # Bar: Số HĐ (Indigo)
       fig_combo.add_trace(
           go.Bar(
               name='Số HĐ',
               x=top15['Chi_nhanh'],
               y=top15['So_HD'],
               marker=dict(
                   color='#6366f1',  # Indigo
                   line=dict(color=DARK_COLORS['bg_card'], width=2)
               ),
               text=top15['So_HD'],
               textposition='outside',
               textfont=dict(size=9, color=DARK_COLORS['text_white'], weight=600),
               hovertemplate='<b>%{x}</b><br>Số HĐ: <b>%{y}</b><extra></extra>'
           ),
           secondary_y=False
       )


       # Line: Dư nợ TB/HĐ (Cyan)
       fig_combo.add_trace(
           go.Scatter(
               name='Dư nợ TB/HĐ',
               x=top15['Chi_nhanh'],
               y=top15['Du_no_per_HD'] / 1e9,
               line=dict(color='#06b6d4', width=4),  # Cyan
               mode='lines+markers',
               marker=dict(
                   size=10,
                   color='#06b6d4',
                   line=dict(color=DARK_COLORS['bg_card'], width=2)
               ),
               text=[f"{x / 1e9:.2f}T" for x in top15['Du_no_per_HD']],
               textposition='top center',
               textfont=dict(size=9, color='#06b6d4', weight=600),
               hovertemplate='<b>%{x}</b><br>Dư nợ TB: <b>%{y:.2f} tỷ</b><extra></extra>'
           ),
           secondary_y=True
       )


       fig_combo.update_xaxes(
           title="",
           tickangle=-45,
           tickfont=dict(size=9, color=DARK_COLORS['text_white']),
           showgrid=False,
           showline=True,
           linecolor=DARK_COLORS['grid'],
           linewidth=1
       )


       fig_combo.update_yaxes(
           title=dict(
               text="<b>Số HĐ</b>",
               font=dict(size=11, color=DARK_COLORS['text_light'])
           ),
           secondary_y=False,
           tickfont=dict(size=10, color=DARK_COLORS['text_white']),
           showgrid=True,
           gridcolor=DARK_COLORS['grid'],
           gridwidth=1,
           showline=True,
           linecolor=DARK_COLORS['grid'],
           linewidth=1
       )


       fig_combo.update_yaxes(
           title=dict(
               text="<b>Dư nợ TB/HĐ (Tỷ)</b>",
               font=dict(size=11, color='#06b6d4')
           ),
           secondary_y=True,
           tickfont=dict(size=10, color=DARK_COLORS['text_white']),
           showgrid=True,
           gridcolor=DARK_COLORS['grid'],
           gridwidth=1,
           showline=True,
           linecolor=DARK_COLORS['grid'],
           linewidth=1
       )


       fig_combo.update_layout(
           height=450,
           hovermode='x unified',
           legend=dict(
               orientation="h",
               yanchor="bottom",
               y=1.02,
               xanchor="center",
               x=0.5,
               bgcolor='rgba(15, 23, 42, 0.8)',
               bordercolor=DARK_COLORS['grid'],
               borderwidth=1,
               font=dict(size=10, color=DARK_COLORS['text_white'])
           ),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=60, r=70, t=60, b=110),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_combo, use_container_width=True)




def show_productivity_analysis(df):
   """Tab B: Phân tích Năng suất - Professional Layout"""


   st.markdown("### 📈 Phần B: Phân tích Năng suất")
   st.markdown("---")


   # CHUẨN HÓA DỮ LIỆU
   df_temp = df.copy()
   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'
   interest_col = 'Lai_thong_thuong_Da_tra'


   df_temp[outstanding_col] = pd.to_numeric(df_temp[outstanding_col], errors='coerce').fillna(0)
   df_temp[interest_col] = pd.to_numeric(df_temp[interest_col], errors='coerce').fillna(0)


   # Tính toán theo chi nhánh
   branch_perf = df_temp.groupby('Ma_chi_nhanh').agg({
       outstanding_col: 'sum',
       interest_col: 'sum',
       'Ma_khach_hang': 'count'
   }).reset_index()


   branch_perf.columns = ['Chi_nhanh', 'Du_no', 'Thu_lai', 'So_HD']
   branch_perf['Du_no_per_HD'] = branch_perf['Du_no'] / branch_perf['So_HD']
   branch_perf['Thu_lai_per_HD'] = branch_perf['Thu_lai'] / branch_perf['So_HD']
   branch_perf['Efficiency_Ratio'] = (branch_perf['Thu_lai'] / branch_perf['Du_no'] * 100)


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 1: 4 KPI CARDS - NĂNG SUẤT (PURPLE-BLUE GRADIENT)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📈 Chỉ số Năng suất Hoạt động")


   col1, col2, col3, col4 = st.columns(4)


   # Tính productivity metrics
   avg_contracts_per_branch = branch_perf['So_HD'].mean()
   top_performer = branch_perf.nlargest(1, 'Efficiency_Ratio').iloc[0]
   high_performers = len(branch_perf[branch_perf['Efficiency_Ratio'] >= 7])
   avg_income_per_branch = branch_perf['Thu_lai'].mean()


   # Card 1: Số HĐ TB/Chi nhánh (Cyan gradient)
   with col1:
       st.markdown(f"""
       <div style='background: linear-gradient(135deg, #06b6d4, #0891b2); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📊 Số HĐ TB/Chi nhánh</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{avg_contracts_per_branch:.0f}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Hợp đồng/CN</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 2: Chi nhánh xuất sắc nhất (Gold gradient - nổi bật)
   with col2:
       st.markdown(f"""
       <div style='background: linear-gradient(135deg, #fbbf24, #f59e0b); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>🏆 Chi nhánh xuất sắc</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{top_performer['Efficiency_Ratio']:.2f}%</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>{top_performer['Chi_nhanh']}</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 3: Số CN đạt chuẩn (Green gradient - success)
   with col3:
       achievement_rate = high_performers / len(branch_perf) * 100


       if achievement_rate >= 70:
           gradient = "linear-gradient(135deg, #10b981, #059669)"
           emoji = "✨"
       elif achievement_rate >= 50:
           gradient = "linear-gradient(135deg, #06b6d4, #0891b2)"
           emoji = "✅"
       else:
           gradient = "linear-gradient(135deg, #f59e0b, #d97706)"
           emoji = "⚠️"


       st.markdown(f"""
       <div style='background: {gradient}; border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>{emoji} CN đạt chuẩn (≥7%)</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{high_performers}/{len(branch_perf)}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>{achievement_rate:.1f}% đạt mục tiêu</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 4: Thu lãi TB/Chi nhánh (Indigo gradient)
   with col4:
       st.markdown(f"""
       <div style='background: linear-gradient(135deg, #6366f1, #4f46e5); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);'>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💰 Thu lãi TB/CN</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{avg_income_per_branch / 1e9:.2f} tỷ</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Trung bình mỗi CN</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 2: HEATMAP - CHI NHÁNH × SẢN PHẨM (PURPLE-BLUE THEME)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🔥 Heatmap: Hiệu suất Chi nhánh × Sản phẩm")
   st.caption("📍 Top 15 Chi nhánh × Top 5 Sản phẩm theo dư nợ")


   # DARK THEME COLORS
   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   if 'Sub_productTen_san_pham' in df_temp.columns:
       # Tính dư nợ theo Chi nhánh × Sản phẩm
       heatmap_data = df_temp.groupby(['Ma_chi_nhanh', 'Sub_productTen_san_pham'])[outstanding_col].sum().reset_index()


       pivot = heatmap_data.pivot(
           index='Ma_chi_nhanh',
           columns='Sub_productTen_san_pham',
           values=outstanding_col
       ).fillna(0) / 1e9


       # Lấy Top 15 chi nhánh
       pivot['Total'] = pivot.sum(axis=1)
       pivot = pivot.nlargest(15, 'Total').drop('Total', axis=1)


       # Lấy Top 5 sản phẩm
       top5_products = pivot.sum(axis=0).nlargest(5).index
       pivot = pivot[top5_products]


       fig_heatmap = go.Figure(data=go.Heatmap(
           z=pivot.values,
           x=pivot.columns,
           y=pivot.index,
           # Purple-Blue-Cyan gradient cho productivity
           colorscale=[
               [0, '#1e293b'],  # Navy dark (0)
               [0.2, '#6366f1'],  # Indigo (low)
               [0.5, '#8b5cf6'],  # Purple (medium)
               [0.8, '#06b6d4'],  # Cyan (high)
               [1, '#fbbf24']  # Gold (highest)
           ],
           text=[[f"{val:.1f}T" if val > 0.5 else "" for val in row] for row in pivot.values],
           texttemplate="%{text}",
           textfont=dict(size=10, color='white', weight=600),
           hovertemplate="<b>%{y}</b><br>" +
                         "%{x}<br>" +
                         "Dư nợ: <b>%{z:.2f} tỷ</b><br>" +
                         "<extra></extra>",
           colorbar=dict(
               title=dict(
                   text="Dư nợ (Tỷ)",
                   font=dict(size=12, color=DARK_COLORS['text_white'])
               ),
               tickfont=dict(size=11, color=DARK_COLORS['text_white']),
               x=1.02,
               bgcolor='rgba(15, 23, 42, 0.8)',
               bordercolor=DARK_COLORS['grid'],
               borderwidth=1
           )
       ))


       fig_heatmap.update_layout(
           height=550,
           xaxis=dict(
               title=dict(
                   text="<b>Sản phẩm</b>",
                   font=dict(size=12, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               tickangle=-45,
               side='top',
               showgrid=False
           ),
           yaxis=dict(
               title=dict(
                   text="<b>Chi nhánh</b>",
                   font=dict(size=12, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               autorange='reversed',
               showgrid=False
           ),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=110, r=80, t=110, b=60),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_heatmap, use_container_width=True, key="eff_heatmap_branch_product")


       # INSIGHT BOX (DARK THEME)
       top_combo = heatmap_data.nlargest(1, outstanding_col).iloc[0]
       concentration_pct = pivot.sum().sum() / df_temp[outstanding_col].sum() * 100


       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
           border-left: 5px solid #06b6d4;
           border-radius: 12px;
           padding: 1.5rem;
           margin: 1.5rem 0;
           box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
       '>
           <div style='color: #06b6d4; font-size: 16px; font-weight: 700; margin-bottom: 1rem;'>
               💡 Phân tích Productivity:
           </div>
           <div style='color: #f8fafc; line-height: 2;'>
               • <b style='color: #fbbf24;'>Tổ hợp mạnh nhất:</b> <b>{top_combo['Ma_chi_nhanh']}</b> × <b>{top_combo['Sub_productTen_san_pham']}</b> = <b>{top_combo[outstanding_col] / 1e9:.2f} tỷ</b><br>
               • <b style='color: #8b5cf6;'>Tập trung:</b> Top 15 chi nhánh chiếm <b>{concentration_pct:.1f}%</b> tổng dư nợ<br>
               • <b style='color: #06b6d4;'>Sản phẩm chủ lực:</b> {', '.join([f'<b>{p}</b>' for p in top5_products[:3]])}
           </div>
       </div>
       """, unsafe_allow_html=True)
   else:
       st.warning("⚠️ Không có dữ liệu Sản phẩm trong file")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HÀNG 3: GROUPED BAR (TRÁI) × STACKED BAR (PHẢI) - PURPLE-BLUE
   # ═══════════════════════════════════════════════════════════════
   col_left, col_right = st.columns([1, 1])


   # DARK THEME COLORS
   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   with col_left:
       st.markdown("#### 📊 So sánh theo Vùng")
       st.caption("📍 Dư nợ vs Thu lãi theo khu vực địa lý")


       if 'Vung' in df_temp.columns:
           vung_stats = df_temp.groupby('Vung').agg({
               outstanding_col: 'sum',
               interest_col: 'sum',
               'Ma_khach_hang': 'count'
           }).reset_index()
           vung_stats.columns = ['Vung', 'Du_no', 'Thu_lai', 'So_HD']


           fig_grouped = go.Figure()


           # Bar 1: Dư nợ (Indigo)
           fig_grouped.add_trace(go.Bar(
               name='Dư nợ (tỷ)',
               x=vung_stats['Vung'],
               y=vung_stats['Du_no'] / 1e9,
               marker=dict(
                   color='#6366f1',
                   line=dict(color=DARK_COLORS['bg_card'], width=2)
               ),
               text=[f"{x:.1f}" for x in vung_stats['Du_no'] / 1e9],
               textposition='outside',
               textfont=dict(size=11, color=DARK_COLORS['text_white'], weight=600),
               hovertemplate='<b>%{x}</b><br>Dư nợ: <b>%{y:.1f} tỷ</b><extra></extra>'
           ))


           # Bar 2: Thu lãi (Cyan)
           fig_grouped.add_trace(go.Bar(
               name='Thu lãi (tỷ)',
               x=vung_stats['Vung'],
               y=vung_stats['Thu_lai'] / 1e9,
               marker=dict(
                   color='#06b6d4',
                   line=dict(color=DARK_COLORS['bg_card'], width=2)
               ),
               text=[f"{x:.1f}" for x in vung_stats['Thu_lai'] / 1e9],
               textposition='outside',
               textfont=dict(size=11, color=DARK_COLORS['text_white'], weight=600),
               hovertemplate='<b>%{x}</b><br>Thu lãi: <b>%{y:.1f} tỷ</b><extra></extra>'
           ))


           fig_grouped.update_layout(
               barmode='group',
               height=450,
               xaxis=dict(
                   title="",
                   tickfont=dict(size=11, color=DARK_COLORS['text_white']),
                   showgrid=False,
                   showline=True,
                   linecolor=DARK_COLORS['grid'],
                   linewidth=1
               ),
               yaxis=dict(
                   title=dict(
                       text="<b>Giá trị (Tỷ VNĐ)</b>",
                       font=dict(size=11, color=DARK_COLORS['text_light'])
                   ),
                   tickfont=dict(size=11, color=DARK_COLORS['text_white']),
                   showgrid=True,
                   gridcolor=DARK_COLORS['grid'],
                   gridwidth=1,
                   showline=True,
                   linecolor=DARK_COLORS['grid'],
                   linewidth=1
               ),
               legend=dict(
                   orientation="h",
                   y=1.08,
                   x=0.5,
                   xanchor="center",
                   bgcolor='rgba(15, 23, 42, 0.8)',
                   bordercolor=DARK_COLORS['grid'],
                   borderwidth=1,
                   font=dict(size=11, color=DARK_COLORS['text_white'])
               ),
               paper_bgcolor='rgba(0,0,0,0)',
               plot_bgcolor=DARK_COLORS['bg_card'],
               margin=dict(l=60, r=30, t=70, b=60),
               font=dict(family='Inter, sans-serif')
           )


           st.plotly_chart(fig_grouped, use_container_width=True, key="eff_grouped_region")
       else:
           st.warning("⚠️ Không có dữ liệu Vùng")


   with col_right:
       st.markdown("#### 📊 Stacked Bar: Thu lãi Chi nhánh × Nhóm nợ")
       st.caption("📍 Top 10 chi nhánh, phân tích cơ cấu theo chất lượng nợ")


       # Tính thu lãi theo Chi nhánh × Nhóm nợ
       df_temp['Nhom_no_KH'] = pd.to_numeric(df_temp['Nhom_no_KH'], errors='coerce').fillna(1).astype(int)


       stacked_data = df_temp.groupby(['Ma_chi_nhanh', 'Nhom_no_KH'])[interest_col].sum().reset_index()


       # Pivot
       stacked_pivot = stacked_data.pivot(
           index='Ma_chi_nhanh',
           columns='Nhom_no_KH',
           values=interest_col
       ).fillna(0) / 1e9


       # Lấy top 10 chi nhánh
       stacked_pivot['Total'] = stacked_pivot.sum(axis=1)
       stacked_pivot = stacked_pivot.nlargest(10, 'Total').drop('Total', axis=1)


       fig_stacked = go.Figure()


       # Purple-Blue-Green gradient cho nhóm nợ
       colors_stacked = {
           1: '#10b981',  # Xanh lá - Good
           2: '#06b6d4',  # Cyan - Watch
           3: '#f59e0b',  # Cam - Substandard
           4: '#ef4444',  # Đỏ - Doubtful
           5: '#dc2626'  # Đỏ đậm - Loss
       }


       for col in sorted(stacked_pivot.columns):
           fig_stacked.add_trace(go.Bar(
               name=f'Nhóm {int(col)}',
               x=stacked_pivot.index,
               y=stacked_pivot[col],
               marker=dict(
                   color=colors_stacked.get(int(col), '#6366f1'),
                   line=dict(color=DARK_COLORS['bg_card'], width=1)
               ),
               hovertemplate="<b>%{x}</b><br>" +
                             f"Nhóm {int(col)}<br>" +
                             "Thu lãi: <b>%{y:.2f} tỷ</b><br>" +
                             "<extra></extra>"
           ))


       fig_stacked.update_layout(
           barmode='stack',
           height=450,
           xaxis=dict(
               title="",
               tickangle=-45,
               tickfont=dict(size=10, color=DARK_COLORS['text_white']),
               showgrid=False,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           yaxis=dict(
               title=dict(
                   text="<b>Thu lãi (Tỷ VNĐ)</b>",
                   font=dict(size=11, color=DARK_COLORS['text_light'])
               ),
               tickfont=dict(size=11, color=DARK_COLORS['text_white']),
               showgrid=True,
               gridcolor=DARK_COLORS['grid'],
               gridwidth=1,
               showline=True,
               linecolor=DARK_COLORS['grid'],
               linewidth=1
           ),
           legend=dict(
               orientation="h",
               yanchor="bottom",
               y=1.02,
               xanchor="center",
               x=0.5,
               bgcolor='rgba(15, 23, 42, 0.8)',
               bordercolor=DARK_COLORS['grid'],
               borderwidth=1,
               font=dict(size=10, color=DARK_COLORS['text_white'])
           ),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor=DARK_COLORS['bg_card'],
           margin=dict(l=60, r=30, t=60, b=110),
           font=dict(family='Inter, sans-serif')
       )


       st.plotly_chart(fig_stacked, use_container_width=True, key="eff_stacked_branch_debt")


       # Caption with percentage
       contribution_pct = stacked_pivot.sum().sum() / (df_temp[interest_col].sum() / 1e9) * 100
       st.markdown(f"""
       <div style='color: #06b6d4; font-size: 13px; margin-top: 0.5rem;'>
           💡 Top 10 đóng góp <b>{contribution_pct:.1f}%</b> tổng thu lãi
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")
   # ═══════════════════════════════════════════════════════════════
   # HÀNG 4: BẢNG XẾP HẠNG CHI NHÁNH - DARK THEME
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📋 Bảng xếp hạng Chi nhánh (Top 20)")
   st.caption("📍 Đánh giá toàn diện theo 5 tiêu chí")


   # Tính toán ranking
   ranking_df = branch_perf.copy()
   ranking_df['Dư nợ (tỷ)'] = (ranking_df['Du_no'] / 1e9).round(2)
   ranking_df['Thu lãi (tỷ)'] = (ranking_df['Thu_lai'] / 1e9).round(2)
   ranking_df['Dư nợ TB/HĐ (tỷ)'] = (ranking_df['Du_no_per_HD'] / 1e9).round(2)
   ranking_df['Thu lãi TB/HĐ (tr)'] = (ranking_df['Thu_lai_per_HD'] / 1e6).round(1)
   ranking_df['Efficiency (%)'] = ranking_df['Efficiency_Ratio'].round(2)


   # Sắp xếp theo Efficiency
   ranking_df = ranking_df.nlargest(20, 'Efficiency (%)')


   # Hiển thị bảng với gradient styling
   st.dataframe(
       ranking_df[['Chi_nhanh', 'So_HD', 'Dư nợ (tỷ)', 'Thu lãi (tỷ)',
                   'Dư nợ TB/HĐ (tỷ)', 'Thu lãi TB/HĐ (tr)', 'Efficiency (%)']].style.background_gradient(
           cmap='viridis',  # Purple-Blue-Green gradient
           subset=['Efficiency (%)']
       ).format({
           'So_HD': '{:,.0f}',
           'Dư nợ (tỷ)': '{:.2f}',
           'Thu lãi (tỷ)': '{:.2f}',
           'Dư nợ TB/HĐ (tỷ)': '{:.2f}',
           'Thu lãi TB/HĐ (tr)': '{:.1f}',
           'Efficiency (%)': '{:.2f}%'
       }).set_properties(**{
           'background-color': '#0f172a',
           'color': '#f8fafc',
           'border-color': '#334155'
       }),
       use_container_width=True,
       height=500
   )


   # INFO BOX (DARK THEME)
   st.markdown("""
   <div style='
       background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
       border-left: 5px solid #8b5cf6;
       border-radius: 12px;
       padding: 1.5rem;
       margin: 1.5rem 0;
       box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
   '>
       <div style='color: #8b5cf6; font-size: 16px; font-weight: 700; margin-bottom: 1rem;'>
           📊 Chú giải:
       </div>
       <div style='color: #f8fafc; line-height: 2;'>
           • <b style='color: #fbbf24;'>Efficiency (%):</b> Thu lãi / Dư nợ × 100% - Chỉ số hiệu quả sử dụng vốn<br>
           • <b style='color: #06b6d4;'>Dư nợ TB/HĐ:</b> Quy mô cho vay trung bình mỗi hợp đồng<br>
           • <b style='color: #10b981;'>Thu lãi TB/HĐ:</b> Thu nhập trung bình mỗi hợp đồng<br>
           • <b style='color: #8b5cf6;'>Mục tiêu:</b> Efficiency ≥ 7% - Đạt chuẩn hiệu quả
       </div>
       <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #334155;'>
           <div style='color: #06b6d4; font-size: 15px; font-weight: 700; margin-bottom: 0.5rem;'>
               🎯 Đánh giá cấp độ:
           </div>
           <div style='color: #f8fafc; line-height: 2;'>
               • <span style='color: #10b981;'>Xuất sắc (≥7%):</span> Top performers<br>
               • <span style='color: #06b6d4;'>Tốt (5-7%):</span> Đạt tiêu chuẩn<br>
               • <span style='color: #f59e0b;'>Trung bình (3-5%):</span> Cần cải thiện<br>
               • <span style='color: #ef4444;'>Yếu (<3%):</span> Cần hành động khẩn cấp
           </div>
       </div>
   </div>
   """, unsafe_allow_html=True)





