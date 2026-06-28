# ==============================================
# File: dashboard_risk.py
# Module: Rủi ro & Chất lượng Tín dụng (3 TABS)
# ==============================================


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ✅ IMPORT BẢNG MÀU
from colors_config import (
   PRIMARY, PRIMARY_LIGHT,
   POSITIVE, POSITIVE_LIGHT,
   NEGATIVE, NEGATIVE_DARK,
   WARNING,
   SLATE_50, SLATE_200, SLATE_400,
   NPL_GROUP_COLORS,
   RED_SCALE,
   get_npl_color
)




def show_risk_section(df):
   """
   ⚠️ Module Rủi ro & Chất lượng Tín dụng
   3 Tabs: A) Chỉ số Rủi ro | B) Phân tích Nợ xấu | C) Dự báo & Cảnh báo
   """


   st.header("⚠️ Rủi ro & Chất lượng Tín dụng")
   st.caption(f"📊 Phân tích {len(df):,} hợp đồng | Dữ liệu đến 06/08/2025")


   tab_a, tab_b, tab_c = st.tabs([
       "📊 A. CHỈ SỐ RỦI RO",
       "🔥 B. PHÂN TÍCH NỢ XẤU",
       "🔮 C. DỰ BÁO & CẢNH BÁO"
   ])


   with tab_a:
       show_risk_overview(df)


   with tab_b:
       show_npl_analysis(df)


   with tab_c:
       show_forecast_alerts(df)




# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# TAB A: CHỈ SỐ RỦI RO TỔNG QUAN - PHIÊN BẢN ĐẦY ĐỦ
# ═════════════════════════════════════════════════════════════════════


def show_risk_overview(df):
   """Tab A: Chỉ số rủi ro tổng quan - 5 phần phân tích"""


   st.markdown("### 📊 Phần A: Chỉ số Rủi ro Tổng quan")
   st.markdown("---")


   # CHUẨN HÓA DỮ LIỆU
   df_temp = df.copy()
   df_temp['Nhom_no_KH'] = pd.to_numeric(df_temp['Nhom_no_KH'], errors='coerce').fillna(1).astype(int)


   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'
   overdue_col = 'Goc_qua_han'


   df_temp[outstanding_col] = pd.to_numeric(df_temp[outstanding_col], errors='coerce').fillna(0)
   df_temp[overdue_col] = pd.to_numeric(df_temp[overdue_col], errors='coerce').fillna(0)


   total_outstanding = df_temp[outstanding_col].sum()
   total_overdue = df_temp[overdue_col].sum()


   # Tính các chỉ số
   npl_df = df_temp[df_temp['Nhom_no_KH'].isin([3, 4, 5])].copy()
   npl_amount = npl_df[outstanding_col].sum()
   npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else 0


   watchlist_df = df_temp[df_temp['Nhom_no_KH'] == 2].copy()
   watchlist_amount = watchlist_df[outstanding_col].sum()
   watchlist_ratio = (watchlist_amount / total_outstanding * 100) if total_outstanding > 0 else 0


   overdue_ratio = (total_overdue / total_outstanding * 100) if total_outstanding > 0 else 0


   # ═══════════════════════════════════════════════════════════════
   # PHẦN 1: 4 KPI CARDS
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### ⚡ Chỉ số Rủi ro Chính")


   col1, col2, col3, col4 = st.columns(4)


   with col1:
       st.metric(
           label="⚠️ NPL Ratio",
           value=f"{npl_ratio:.2f}%",
           delta="Cảnh báo" if npl_ratio >= 3 else "Tốt",
           delta_color="inverse" if npl_ratio >= 3 else "normal",
           help="NPL = (Nhóm 3+4+5) / Tổng dư nợ"
       )


   with col2:
       st.metric(
           label="📊 Dư nợ Xấu",
           value=f"{npl_amount / 1e9:.2f} tỷ",
           delta=f"{len(npl_df)} HĐ",
           delta_color="off",
           help="Tổng dư nợ nhóm 3, 4, 5"
       )


   with col3:
       st.metric(
           label="👀 Nợ Cần chú ý",
           value=f"{watchlist_ratio:.2f}%",
           delta=f"{watchlist_amount / 1e9:.2f} tỷ",
           delta_color="off",
           help="Nhóm 2 - Tiềm năng trở thành NPL"
       )


   with col4:
       st.metric(
           label="💰 Tỷ lệ Quá hạn",
           value=f"{overdue_ratio:.2f}%",
           delta=f"{total_overdue / 1e9:.2f} tỷ",
           delta_color="inverse" if overdue_ratio > 5 else "off",
           help="Tổng gốc quá hạn / Tổng dư nợ"
       )


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # PHẦN 2: TỔNG QUAN NHÓM NỢ (2 CỘT)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🎯 Tổng quan Nhóm nợ")


   col_left, col_right = st.columns(2)


   # Tính toán nhóm nợ
   nhom_stats = []
   for nhom in [1, 2, 3, 4, 5]:
       debt = df_temp[df_temp['Nhom_no_KH'] == nhom][outstanding_col].sum()
       count = len(df_temp[df_temp['Nhom_no_KH'] == nhom])
       ratio = (debt / total_outstanding * 100) if total_outstanding > 0 else 0
       nhom_stats.append({
           'Nhóm': f'Nhóm {nhom}',
           'Dư nợ': debt,
           'Tỷ lệ': ratio,
           'Số HĐ': count
       })


   nhom_df = pd.DataFrame(nhom_stats)
   colors_donut = [POSITIVE, WARNING, RED_SCALE[4], RED_SCALE[6], RED_SCALE[7]]


   # ─────────────────────────────────────────────────────────────
   # BIỂU ĐỒ 1: DONUT CHART
   # ─────────────────────────────────────────────────────────────
   with col_left:
       st.markdown("##### 🥧 Tổng quan Nhóm nợ")
       st.caption("📍 Phân bố dư nợ theo 5 nhóm")


       fig_donut = go.Figure(data=[go.Pie(
           labels=nhom_df['Nhóm'],
           values=nhom_df['Dư nợ'],
           hole=0.5,
           marker=dict(colors=colors_donut),
           textinfo='label+percent',
           textposition='outside',
           textfont=dict(size=12),
           hovertemplate="<b>%{label}</b><br>" +
                         "Dư nợ: %{value:,.0f} VNĐ<br>" +
                         "Tỷ lệ: %{percent}<br>" +
                         "<extra></extra>"
       )])


       total_contracts = len(df_temp)
       fig_donut.add_annotation(
           text=f"<b>{total_outstanding / 1e9:.1f} tỷ</b><br>{total_contracts} HĐ",
           x=0.5, y=0.5,
           font=dict(size=16, color=PRIMARY, family='Arial Black'),
           showarrow=False
       )


       fig_donut.update_layout(
           height=400,
           showlegend=True,
           legend=dict(
               orientation="v",
               yanchor="middle",
               y=0.5,
               xanchor="left",
               x=1.05,
               font=dict(size=11)
           ),
           margin=dict(l=20, r=120, t=40, b=20),
           paper_bgcolor='rgba(0,0,0,0)'
       )


       st.plotly_chart(fig_donut, use_container_width=True)


       st.info(f"""
**📖 Phân bố Dư nợ:**
- **Nhóm 1**: {nhom_df.iloc[0]['Tỷ lệ']:.2f}% ({nhom_df.iloc[0]['Dư nợ'] / 1e9:.2f} tỷ)
- **Nhóm 2**: {nhom_df.iloc[1]['Tỷ lệ']:.2f}% ({nhom_df.iloc[1]['Dư nợ'] / 1e9:.2f} tỷ)
- **NPL**: {npl_ratio:.2f}% ({npl_amount / 1e9:.2f} tỷ)
       """)


   # ─────────────────────────────────────────────────────────────
   # BIỂU ĐỒ 2: HORIZONTAL BAR
   # ─────────────────────────────────────────────────────────────
   with col_right:
       st.markdown("##### 📊 Chi tiết Dư nợ")
       st.caption("📍 Dư nợ và số HĐ từng nhóm")


       fig_bar = go.Figure()


       for idx, row in nhom_df.iterrows():
           fig_bar.add_trace(go.Bar(
               name=row['Nhóm'],
               y=[row['Nhóm']],
               x=[row['Dư nợ'] / 1e9],
               orientation='h',
               marker_color=colors_donut[idx],
               text=f"{row['Tỷ lệ']:.2f}% ({row['Số HĐ']} HĐ)",
               textposition='inside',
               textfont=dict(size=11, color='white'),
               hovertemplate=f"<b>{row['Nhóm']}</b><br>" +
                             f"Dư nợ: {row['Dư nợ'] / 1e9:.2f} tỷ<br>" +
                             f"Tỷ lệ: {row['Tỷ lệ']:.2f}%<br>" +
                             f"Số HĐ: {row['Số HĐ']}<br>" +
                             "<extra></extra>"
           ))


       fig_bar.update_layout(
           title=dict(text="Dư nợ theo Nhóm (tỷ VNĐ)", font=dict(size=13, color=PRIMARY)),
           height=400,
           xaxis=dict(
               title=dict(text="Dư nợ (tỷ VNĐ)", font=dict(size=12)),
               tickfont=dict(size=11)
           ),
           yaxis=dict(title="", tickfont=dict(size=12)),
           showlegend=False,
           margin=dict(l=80, r=20, t=60, b=60),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor='rgba(248,250,252,0.8)'
       )


       st.plotly_chart(fig_bar, use_container_width=True)


       if npl_ratio >= 3:
           st.error(f"""
**🔴 NPL > 3%**
- NPL: {npl_ratio:.2f}%
- {len(npl_df)} HĐ cần xử lý
           """)
       else:
           st.success(f"""
**✅ NPL < 3%**
- NPL: {npl_ratio:.2f}%
- {len(npl_df)} HĐ NPL
           """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # PHẦN 3: NPL THEO CHI NHÁNH (TOP 10)
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🏢 NPL theo Chi nhánh (Top 10)")
   st.caption("📍 10 Chi nhánh có NPL Ratio cao nhất")


   branch_npl = df_temp.groupby('Ma_chi_nhanh').apply(
       lambda x: pd.Series({
           'Total_Debt': x[outstanding_col].sum(),
           'NPL_Debt': x[x['Nhom_no_KH'].isin([3, 4, 5])][outstanding_col].sum(),
           'NPL_Count': len(x[x['Nhom_no_KH'].isin([3, 4, 5])]),
           'NPL_Ratio': (x[x['Nhom_no_KH'].isin([3, 4, 5])][outstanding_col].sum() / x[outstanding_col].sum() * 100) if
           x[outstanding_col].sum() > 0 else 0
       }), include_groups=False
   ).reset_index()


   branch_npl = branch_npl[branch_npl['Total_Debt'] > 1e9].copy()
   top10_npl = branch_npl.nlargest(10, 'NPL_Ratio')


   colors_branch = [
       RED_SCALE[7] if x > 10 else
       RED_SCALE[5] if x > 5 else
       WARNING if x > 3 else
       POSITIVE_LIGHT
       for x in top10_npl['NPL_Ratio']
   ]


   fig_branch_npl = go.Figure()


   fig_branch_npl.add_trace(go.Bar(
       x=top10_npl['Ma_chi_nhanh'],
       y=top10_npl['NPL_Ratio'],
       marker_color=colors_branch,
       text=[f"{x:.2f}%" for x in top10_npl['NPL_Ratio']],
       textposition='outside',
       textfont=dict(size=12),
       hovertemplate="<b>%{x}</b><br>" +
                     "NPL: %{y:.2f}%<br>" +
                     "<extra></extra>"
   ))


   fig_branch_npl.add_hline(
       y=3, line_dash="dash", line_color=WARNING, line_width=2,
       annotation_text="Ngưỡng 3%",
       annotation_position="right"
   )


   fig_branch_npl.update_layout(
       title=dict(text="NPL Ratio - Top 10 Chi nhánh", font=dict(size=14, color=PRIMARY)),
       height=450,
       xaxis=dict(
           title=dict(text="Chi nhánh", font=dict(size=12)),
           tickangle=-45,
           tickfont=dict(size=11)
       ),
       yaxis=dict(
           title=dict(text="NPL Ratio (%)", font=dict(size=12)),
           tickfont=dict(size=11),
           range=[0, max(top10_npl['NPL_Ratio']) * 1.2]
       ),
       margin=dict(l=60, r=60, t=80, b=100),
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(248,250,252,0.8)'
   )


   st.plotly_chart(fig_branch_npl, use_container_width=True)


   high_risk_branches = branch_npl[branch_npl['NPL_Ratio'] > 5].sort_values('NPL_Ratio', ascending=False)


   if len(high_risk_branches) > 0:
       st.error(f"""
**🔴 {len(high_risk_branches)} chi nhánh NPL > 5%**
- NPL: {high_risk_branches['NPL_Debt'].sum() / 1e9:.2f} tỷ
- HĐ: {high_risk_branches['NPL_Count'].sum():.0f}
       """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # ═══════════════════════════════════════════════════════════════
   # PHẦN 4: SO SÁNH DƯ NỢ XẤU VS GỐC QUÁ HẠN
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📉 So sánh: Dư nợ vs Gốc quá hạn (Nhóm 2-5)")
   st.caption("📍 Phân tích mối quan hệ giữa dư nợ và gốc quá hạn")


   # Tính toán cho nhóm 2-5
   group_comparison = []
   for nhom in [2, 3, 4, 5]:
       nhom_data = df_temp[df_temp['Nhom_no_KH'] == nhom]
       group_comparison.append({
           'Nhóm': f'Nhóm {nhom}',
           'Dư nợ': nhom_data[outstanding_col].sum() / 1e9,
           'Gốc quá hạn': nhom_data[overdue_col].sum() / 1e9,
           'Số HĐ': len(nhom_data),
           'Tỷ lệ QH': (nhom_data[overdue_col].sum() / nhom_data[outstanding_col].sum() * 100) if nhom_data[
                                                                                                      outstanding_col].sum() > 0 else 0
       })


   comparison_df = pd.DataFrame(group_comparison)


   # Grouped Bar Chart
   fig_comparison = go.Figure()


   fig_comparison.add_trace(go.Bar(
       name='Dư nợ (tỷ)',
       x=comparison_df['Nhóm'],
       y=comparison_df['Dư nợ'],
       marker_color=SLATE_400,
       text=[f"{x:.2f} tỷ" for x in comparison_df['Dư nợ']],
       textposition='outside',
       textfont=dict(size=11)
   ))


   fig_comparison.add_trace(go.Bar(
       name='Gốc quá hạn (tỷ)',
       x=comparison_df['Nhóm'],
       y=comparison_df['Gốc quá hạn'],
       marker_color=NEGATIVE,
       text=[f"{x:.2f} tỷ" for x in comparison_df['Gốc quá hạn']],
       textposition='outside',
       textfont=dict(size=11)
   ))


   fig_comparison.update_layout(
       title=dict(text="Dư nợ vs Gốc quá hạn (Nhóm 2-5)", font=dict(size=14, color=PRIMARY)),
       barmode='group',
       height=450,
       xaxis=dict(
           title=dict(text="Nhóm nợ", font=dict(size=12)),
           tickfont=dict(size=12)
       ),
       yaxis=dict(
           title=dict(text="Số tiền (tỷ VNĐ)", font=dict(size=12)),
           tickfont=dict(size=11)
       ),
       legend=dict(
           orientation="h",
           yanchor="bottom",
           y=1.02,
           xanchor="center",
           x=0.5,
           font=dict(size=12)
       ),
       margin=dict(l=60, r=60, t=100, b=70),
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(248,250,252,0.8)'
   )


   st.plotly_chart(fig_comparison, use_container_width=True)


   # ═══════════════════════════════════════════════════════════════
   # INSIGHTS - 4 CARDS
   # ═══════════════════════════════════════════════════════════════
   col_cp1, col_cp2, col_cp3, col_cp4 = st.columns(4)


   for idx, col in enumerate([col_cp1, col_cp2, col_cp3, col_cp4]):
       row = comparison_df.iloc[idx]
       with col:
           if idx == 0:
               st.warning(f"""
   **{row['Nhóm']}**
   - Dư nợ: {row['Dư nợ']:.2f} tỷ
   - Quá hạn: {row['Gốc quá hạn']:.2f} tỷ
   - Tỷ lệ QH: {row['Tỷ lệ QH']:.2f}%
                   """)
           else:
               st.error(f"""
   **{row['Nhóm']}**
   - Dư nợ: {row['Dư nợ']:.2f} tỷ
   - Quá hạn: {row['Gốc quá hạn']:.2f} tỷ
   - Tỷ lệ QH: {row['Tỷ lệ QH']:.2f}%
                   """)


   # ═══════════════════════════════════════════════════════════════
   # CHÚ THÍCH CHI TIẾT
   # ═══════════════════════════════════════════════════════════════
   st.info("""
   **📖 Cách đọc biểu đồ:**
   - **Cột xám (Dư nợ)**: Tổng tiền khách hàng còn nợ → Quy mô rủi ro
   - **Cột đỏ (Gốc quá hạn)**: Phần gốc đã quá hạn → Tính chất rủi ro
   - **Tỷ lệ QH = (Gốc quá hạn / Dư nợ) × 100%**


   💡 **Công thức:** Tỷ lệ càng cao = Rủi ro càng nghiêm trọng
       """)


   # Phân tích chi tiết
   st.markdown("##### 🔍 Phân tích Chi tiết")


   nhom2 = comparison_df.iloc[0]
   nhom4 = comparison_df.iloc[2]
   nhom5 = comparison_df.iloc[3]


   # Nhóm 2
   if nhom2['Tỷ lệ QH'] > 3:
       st.error(f"""
   **🔴 Nhóm 2 - RỦI RO CAO:**
   - Dư nợ {nhom2['Dư nợ']:.2f} tỷ chiếm {(nhom2['Dư nợ'] / total_outstanding * 1e9 * 100):.1f}% tổng dư nợ
   - Gốc quá hạn {nhom2['Gốc quá hạn']:.2f} tỷ = {nhom2['Tỷ lệ QH']:.2f}% (vượt ngưỡng 3%)
   - **Nguy cơ:** Nếu 10% trượt xuống NPL = thêm {nhom2['Dư nợ'] * 0.1:.2f} tỷ NPL
   - **Hành động:** Cần theo dõi sát {int(nhom2['Số HĐ'])} HĐ
           """)


   # Nhóm 4
   if nhom4['Tỷ lệ QH'] > 5:
       st.error(f"""
   **🔴 Nhóm 4 - TỶ LỆ QH CAO NHẤT:**
   - Tỷ lệ QH {nhom4['Tỷ lệ QH']:.2f}% (cao nhất trong 4 nhóm)
   - Gốc quá hạn {nhom4['Gốc quá hạn']:.2f} tỷ / {nhom4['Dư nợ']:.2f} tỷ dư nợ
   - **Đánh giá:** NPL nặng, khó thu hồi
           """)


   # Nhóm 5
   if nhom5['Tỷ lệ QH'] < 1:
       st.warning(f"""
   **⚠️ Nhóm 5 - BẤT THƯỜNG (Tỷ lệ QH quá thấp):**
   - Tỷ lệ QH chỉ {nhom5['Tỷ lệ QH']:.2f}% (lẽ ra phải >80%)
   - **Giải thích:** Đã xóa nợ, tái cơ cấu hoặc sai dữ liệu
   - Dư nợ {nhom5['Dư nợ']:.2f} tỷ chủ yếu là "nợ zombie"
           """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # LEGEND
   # ═══════════════════════════════════════════════════════════════
   st.markdown("---")


   with st.expander("ℹ️ Giải thích Nhóm nợ theo NHNN", expanded=False):
       st.markdown(f"""
       **Phân loại nợ theo Thông tư 11/2021/TT-NHNN:**


       - <span style="color:{NPL_GROUP_COLORS[1]}">**●**</span> **Nhóm 1 - Nợ chuẩn**: Đầy đủ khả năng thanh toán
       - <span style="color:{NPL_GROUP_COLORS[2]}">**●**</span> **Nhóm 2 - Nợ cần chú ý**: Quá hạn 11-90 ngày
       - <span style="color:{NPL_GROUP_COLORS[3]}">**●**</span> **Nhóm 3 - Nợ dưới chuẩn**: Quá hạn 91-180 ngày ⚠️ **NPL**
       - <span style="color:{NPL_GROUP_COLORS[4]}">**●**</span> **Nhóm 4 - Nợ nghi ngờ**: Quá hạn 181-360 ngày 🚨 **NPL**
       - <span style="color:{NPL_GROUP_COLORS[5]}">**●**</span> **Nhóm 5 - Nợ xấu**: Quá hạn > 360 ngày 💀 **NPL**


       📌 **NPL (Non-Performing Loan)** = Nhóm 3 + 4 + 5
       """, unsafe_allow_html=True)




# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# TAB B: PHÂN TÍCH NỢ XẤU
# ═════════════════════════════════════════════════════════════════════


def show_npl_analysis(df):
   """Tab B: Phân tích Nợ xấu"""


   st.markdown("### 🔥 Phần B: Phân tích Nợ xấu Chi tiết")
   st.markdown("---")


   # CHUẨN HÓA DỮ LIỆU
   df_temp = df.copy()
   df_temp['Nhom_no_KH'] = pd.to_numeric(df_temp['Nhom_no_KH'], errors='coerce').fillna(1).astype(int)


   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'
   overdue_col = 'Goc_qua_han'
   df_temp[outstanding_col] = pd.to_numeric(df_temp[outstanding_col], errors='coerce').fillna(0)
   df_temp[overdue_col] = pd.to_numeric(df_temp[overdue_col], errors='coerce').fillna(0)


   # TÍNH NPL
   total_outstanding = df_temp[outstanding_col].sum()
   npl_df = df_temp[df_temp['Nhom_no_KH'].isin([3, 4, 5])].copy()
   npl_amount = npl_df[outstanding_col].sum()
   npl_ratio = (npl_amount / total_outstanding * 100) if total_outstanding > 0 else 0


   # KPI CARDS
   col1, col2, col3, col4 = st.columns(4)


   with col1:
       st.metric("💰 Tổng dư nợ NPL", f"{npl_amount / 1e9:.2f} tỷ", help="Tổng dư nợ Nhóm 3+4+5")


   with col2:
       st.metric("📊 NPL Ratio", f"{npl_ratio:.2f}%", help="NPL / Tổng dư nợ × 100%")


   with col3:
       st.metric("📋 Số HĐ NPL", f"{len(npl_df):,}", help="Số hợp đồng thuộc nhóm 3+4+5")


   with col4:
       unique_customers = npl_df['Ma_khach_hang'].nunique() if 'Ma_khach_hang' in npl_df.columns else 0
       st.metric("👥 Số KH có NPL", f"{unique_customers:,}", help=f"Từ {len(npl_df)} HĐ")


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # BIỂU ĐỒ 1: NPL SEVERITY MATRIX - CẢI TIẾN
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🎯 Ma trận Phân loại Hợp đồng NPL")


   # ✅ CHÚ THÍCH CHI TIẾT
   with st.expander("💡 Hướng dẫn đọc biểu đồ", expanded=False):
       st.markdown("""
**📊 Mục đích:** Phân loại HĐ NPL theo **2 chiều rủi ro**


**Trục tọa độ:**
- **Trục X (Gốc quá hạn)**: Tính chất rủi ro - Số tiền thực tế đã quá hạn
- **Trục Y (Dư nợ NPL)**: Quy mô rủi ro - Tổng số nợ còn lại


**Phân vùng rủi ro:**


🔴 **VÙNG ĐỎ - Phải Trên** (Dư nợ cao + Quá hạn cao)
  - Rủi ro cực kỳ nghiêm trọng
  - Cần xử lý NGAY LẬP TỨC
  - Ưu tiên cao nhất cho đội thu hồi nợ


🟡 **VÙNG VÀNG - Trái Trên** (Dư nợ cao + Quá hạn = 0)
  - Rủi ro tiềm ẩn
  - KH đã cơ cấu lại nợ hoặc có lịch sử xấu
  - Cần THEO DÕI SÁT để tránh trượt xuống vùng đỏ
  - Ví dụ: KH 10857126 (11.44 tỷ, Nhóm 4, nhưng gốc quá hạn = 0)


🟢 **VÙNG XANH - Trái Dưới** (Dư nợ thấp + Quá hạn thấp)
  - Rủi ro thấp nhất trong NPL
  - Ưu tiên xử lý sau cùng


**Màu sắc bong bóng:**
- 🟠 Cam: Nhóm 3 (Dưới chuẩn)
- 🔴 Đỏ: Nhóm 4 (Nghi ngờ)
- ⚫ Đỏ đậm: Nhóm 5 (Xấu)


**Kích thước bong bóng:** Tỷ lệ với dư nợ (càng lớn = dư nợ càng cao)
       """)


   st.caption("📍 Hover chuột vào bong bóng để xem chi tiết Mã KH, Chi nhánh, Dư nợ")


   # Nhóm theo mức độ rủi ro
   npl_df['Risk_Label'] = npl_df['Nhom_no_KH'].map({
       3: 'Nhóm 3 (Dưới chuẩn)',
       4: 'Nhóm 4 (Nghi ngờ)',
       5: 'Nhóm 5 (Xấu)'
   })


   # SCATTER PLOT
   fig_severity = px.scatter(
       npl_df,
       x=overdue_col,
       y=outstanding_col,
       color='Risk_Label',
       size=outstanding_col,
       color_discrete_map={
           'Nhóm 3 (Dưới chuẩn)': NPL_GROUP_COLORS[3],
           'Nhóm 4 (Nghi ngờ)': NPL_GROUP_COLORS[4],
           'Nhóm 5 (Xấu)': NPL_GROUP_COLORS[5]
       },
       hover_data={
           'Ma_khach_hang': True,
           'Ma_chi_nhanh': True,
           outstanding_col: ':,.0f',
           overdue_col: ':,.0f'
       } if 'Ma_khach_hang' in npl_df.columns else None,
       labels={
           overdue_col: 'Gốc Quá hạn (VNĐ)',
           outstanding_col: 'Dư nợ NPL (VNĐ)',
           'Risk_Label': 'Nhóm nợ'
       }
   )


   # Median lines
   median_overdue = npl_df[overdue_col].median()
   median_debt = npl_df[outstanding_col].median()


   fig_severity.add_vline(
       x=median_overdue,
       line_dash="dash",
       line_color=SLATE_400,
       annotation_text="Median quá hạn",
       annotation_position="top"
   )


   fig_severity.add_hline(
       y=median_debt,
       line_dash="dash",
       line_color=SLATE_400,
       annotation_text="Median dư nợ",
       annotation_position="right"
   )


   # ✅ ANNOTATIONS CẢI TIẾN - 3 vùng rõ ràng
   # Vùng Đỏ
   fig_severity.add_annotation(
       x=npl_df[overdue_col].quantile(0.75),
       y=npl_df[outstanding_col].quantile(0.75),
       text="🔴 VÙNG ĐỎ<br>Ưu tiên cao nhất<br>(Dư nợ cao + Quá hạn cao)",
       showarrow=True,
       arrowhead=2,
       arrowcolor=NEGATIVE,
       ax=-60,
       ay=-60,
       font=dict(size=10, color=NEGATIVE_DARK, family='Arial Black'),
       bgcolor='rgba(239,68,68,0.15)',
       bordercolor=NEGATIVE,
       borderwidth=2
   )


   # Vùng Vàng
   fig_severity.add_annotation(
       x=npl_df[overdue_col].quantile(0.1),
       y=npl_df[outstanding_col].quantile(0.75),
       text="🟡 VÙNG VÀNG<br>Rủi ro tiềm ẩn<br>(Dư nợ cao + Chưa quá hạn)",
       showarrow=True,
       arrowhead=2,
       arrowcolor=WARNING,
       ax=60,
       ay=-40,
       font=dict(size=10, color='#d97706', family='Arial Black'),
       bgcolor='rgba(245,158,11,0.15)',
       bordercolor=WARNING,
       borderwidth=2
   )


   # Vùng Xanh
   fig_severity.add_annotation(
       x=npl_df[overdue_col].quantile(0.1),
       y=npl_df[outstanding_col].quantile(0.25),
       text="🟢 VÙNG XANH<br>Rủi ro thấp nhất<br>(Dư nợ thấp)",
       showarrow=True,
       arrowhead=2,
       arrowcolor=POSITIVE_LIGHT,
       ax=50,
       ay=40,
       font=dict(size=10, color='#15803d', family='Arial Black'),
       bgcolor='rgba(34,197,94,0.15)',
       bordercolor=POSITIVE_LIGHT,
       borderwidth=2
   )


   fig_severity.update_layout(
       title={
           'text': "Ma trận Rủi ro: Phân loại HĐ NPL theo 2 chiều",
           'font': {'size': 14, 'color': PRIMARY}
       },
       xaxis=dict(
           title="Gốc Quá hạn (VNĐ)",
           type='log',
           showgrid=True,
           gridcolor='rgba(0,0,0,0.05)'
       ),
       yaxis=dict(
           title="Dư nợ NPL (VNĐ)",
           type='log',
           showgrid=True,
           gridcolor='rgba(0,0,0,0.05)'
       ),
       height=600,
       legend=dict(
           orientation="h",
           yanchor="top",
           y=-0.12,
           xanchor="center",
           x=0.5
       ),
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(248,250,252,0.8)',
       margin=dict(l=60, r=60, t=60, b=100)
   )


   st.plotly_chart(fig_severity, use_container_width=True)


   # Insights
   high_priority = npl_df[
       (npl_df[overdue_col] > median_overdue) &
       (npl_df[outstanding_col] > median_debt)
       ]


   col_i1, col_i2 = st.columns(2)


   with col_i1:
       st.error(f"""
**🔴 VÙNG ĐỎ - Ưu tiên cao:**
- Số lượng: **{len(high_priority)}** hợp đồng
- Tổng dư nợ: **{high_priority[outstanding_col].sum() / 1e9:.2f}** tỷ
- Gốc quá hạn: **{high_priority[overdue_col].sum() / 1e9:.2f}** tỷ
       """)


   with col_i2:
       st.info(f"""
**📊 Phân bố NPL:**
- Nhóm 3: {len(npl_df[npl_df['Nhom_no_KH'] == 3])} HĐ ({npl_df[npl_df['Nhom_no_KH'] == 3][outstanding_col].sum() / 1e9:.2f} tỷ)
- Nhóm 4: {len(npl_df[npl_df['Nhom_no_KH'] == 4])} HĐ ({npl_df[npl_df['Nhom_no_KH'] == 4][outstanding_col].sum() / 1e9:.2f} tỷ)
- Nhóm 5: {len(npl_df[npl_df['Nhom_no_KH'] == 5])} HĐ ({npl_df[npl_df['Nhom_no_KH'] == 5][outstanding_col].sum() / 1e9:.2f} tỷ)
       """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # BIỂU ĐỒ 2: PARETO CHART - CẢI TIẾN
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📊 Pareto: Tập trung NPL theo Khách hàng")
   st.caption(f"📍 Quy tắc 80/20: {len(npl_df)} HĐ NPL thuộc {npl_df['Ma_khach_hang'].nunique()} khách hàng")


   if 'Ma_khach_hang' in npl_df.columns:
       # ✅ Tổng hợp theo KHÁCH HÀNG (đúng logic)
       customer_npl = npl_df.groupby('Ma_khach_hang').agg({
           outstanding_col: 'sum',
           'Nhom_no_KH': 'count'  # Số HĐ của KH
       }).reset_index()
       customer_npl.columns = ['Customer', 'NPL_Amount', 'Contract_Count']
       customer_npl = customer_npl.sort_values('NPL_Amount', ascending=False).reset_index(drop=True)


       # Tính % trong NPL
       customer_npl['NPL_Pct'] = (customer_npl['NPL_Amount'] / npl_amount * 100)
       customer_npl['Cumulative_NPL'] = customer_npl['NPL_Amount'].cumsum()
       customer_npl['Cumulative_Pct'] = (customer_npl['Cumulative_NPL'] / npl_amount * 100)
       customer_npl['Rank'] = range(1, len(customer_npl) + 1)


       top30 = customer_npl.head(30).copy()


       # PARETO CHART
       fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])


       fig_pareto.add_trace(
           go.Bar(
               x=top30['Rank'],
               y=top30['NPL_Amount'],
               name='Dư nợ NPL',
               marker=dict(
                   color=top30['NPL_Pct'],
                   colorscale=[[0, RED_SCALE[2]], [0.5, RED_SCALE[5]], [1, RED_SCALE[7]]],
                   showscale=True,
                   colorbar=dict(title="% NPL", x=1.15)
               ),
               # ✅ HIỂN THỊ ĐẦY ĐỦ: Dư nợ + Số HĐ
               text=[f"{x / 1e9:.2f}B<br>({int(c)} HĐ)" for x, c in zip(top30['NPL_Amount'], top30['Contract_Count'])],
               textposition='outside',
               textfont=dict(size=9, color=PRIMARY),
               # ✅ HOVER CHI TIẾT: Mã KH + Số HĐ
               hovertemplate='<b>Rank #%{x}</b><br>' +
                             '<b>Mã KH:</b> %{customdata[0]}<br>' +
                             '<b>Dư nợ NPL:</b> %{y:,.0f} VNĐ (%{customdata[2]:.2f}%)<br>' +
                             '<b>Số HĐ:</b> %{customdata[1]} hợp đồng<br>' +
                             '<extra></extra>',
               customdata=top30[['Customer', 'Contract_Count', 'NPL_Pct']]
           ),
           secondary_y=False
       )


       fig_pareto.add_trace(
           go.Scatter(
               x=top30['Rank'],
               y=top30['Cumulative_Pct'],
               name='% Tích lũy',
               line=dict(color=PRIMARY, width=3),
               mode='lines+markers',
               marker=dict(size=8),
               hovertemplate='<b>Top %{x} KH</b><br>Chiếm: <b>%{y:.1f}%</b> NPL<br><extra></extra>'
           ),
           secondary_y=True
       )


       fig_pareto.add_hline(y=80, line_dash="dash", line_color=NEGATIVE, line_width=2,
                            annotation_text="Ngưỡng 80% NPL", annotation_position="right", secondary_y=True)


       customers_80 = (customer_npl['Cumulative_Pct'] <= 80).sum()


       # ✅ ANNOTATION CHỈ SỐ KH CHIẾM 80%
       if customers_80 > 0 and customers_80 <= 30:
           fig_pareto.add_annotation(
               x=customers_80,
               y=80,
               text=f"<b>Top {customers_80} KH</b><br>= 80% NPL",
               showarrow=True,
               arrowhead=2,
               arrowcolor=NEGATIVE,
               ax=-60,
               ay=-50,
               font=dict(size=12, color=NEGATIVE_DARK, family='Arial Black'),
               bgcolor='rgba(239,68,68,0.1)',
               bordercolor=NEGATIVE,
               borderwidth=2,
               yref='y2'
           )


       fig_pareto.update_xaxes(title_text='Ranking Khách hàng (Theo NPL giảm dần)')
       fig_pareto.update_yaxes(title_text='Dư nợ NPL (VNĐ)', secondary_y=False, tickformat='.2s')
       fig_pareto.update_yaxes(title_text='% Tích lũy trong NPL', secondary_y=True, range=[0, 105])


       fig_pareto.update_layout(
           title={'text': f"Pareto NPL: Top 30/{len(customer_npl)} Khách hàng",
                  'font': {'size': 14, 'color': PRIMARY}},
           height=500,
           hovermode='x unified',
           legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
           paper_bgcolor='rgba(0,0,0,0)',
           plot_bgcolor='rgba(248,250,252,0.8)',
           margin=dict(l=60, r=120, t=60, b=100)
       )


       st.plotly_chart(fig_pareto, use_container_width=True)


       # ✅ BẢNG CHI TIẾT TOP 10 KH
       st.markdown("##### 📋 Chi tiết Top 10 Khách hàng")


       top10_detail = customer_npl.head(10).copy()
       top10_detail['NPL (tỷ)'] = (top10_detail['NPL_Amount'] / 1e9).round(3)
       top10_detail['% NPL'] = top10_detail['NPL_Pct'].round(2)
       top10_detail['% Tích lũy'] = top10_detail['Cumulative_Pct'].round(2)


       display_df = top10_detail[['Rank', 'Customer', 'Contract_Count', 'NPL (tỷ)', '% NPL', '% Tích lũy']].copy()
       display_df.columns = ['#', 'Mã KH', 'Số HĐ', 'Dư nợ (tỷ)', '% NPL', '% Tích lũy']


       st.dataframe(
           display_df.style.background_gradient(subset=['Dư nợ (tỷ)', '% NPL'], cmap='Reds')
           .format({'Dư nợ (tỷ)': '{:.3f}', '% NPL': '{:.2f}', '% Tích lũy': '{:.2f}'}),
           hide_index=True,
           use_container_width=True,
           height=400
       )


       # Insights
       top10_amount = customer_npl.head(10)['NPL_Amount'].sum()
       top10_pct = (top10_amount / npl_amount * 100)


       col_p1, col_p2, col_p3 = st.columns(3)


       with col_p1:
           st.metric("🎯 Top 10 KH chiếm", f"{top10_pct:.1f}%", delta=f"{top10_amount / 1e9:.2f} tỷ NPL")


       with col_p2:
           st.metric("📊 80% NPL tập trung ở", f"Top {customers_80} KH",
                     delta=f"{customers_80 / len(customer_npl) * 100:.1f}% tổng KH")


       with col_p3:
           total_contracts = customer_npl['Contract_Count'].sum()
           st.metric("📋 Tổng", f"{len(customer_npl)} KH", delta=f"{total_contracts} HĐ")


       st.warning(f"""
**💡 Khuyến nghị (Dựa trên quy tắc 80/20):**
- 🎯 Tập trung xử lý **Top {customers_80} khách hàng** để giảm 80% dư nợ NPL
- 👥 Top 10 KH chiếm **{top10_pct:.1f}%** NPL → Thiết lập đội xử lý nợ riêng
- 📊 Rủi ro tập trung: {"🔴 Cao - Cần phân tán" if customers_80 < 20 else "🟡 Trung bình - Chấp nhận được"}
- 📞 Liên hệ: Top 10 KH có **{top10_detail['Contract_Count'].sum()} hợp đồng** cần giám sát
       """)


   st.markdown("---")
   # ═══════════════════════════════════════════════════════════════
   # ✅ BẢNG TOP 15 - SẮP XẾP ĐÚNG
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📋 Top 15 Hợp đồng NPL có Dư nợ cao nhất")


   # ✅ SỬA: Sắp xếp giảm dần + reset index
   npl_top = npl_df.nlargest(15, outstanding_col).reset_index(drop=True)
   npl_top.index = npl_top.index + 1  # Bắt đầu từ 1


   display_cols = {
       'Ma_chi_nhanh': 'Chi nhánh',
       'Ma_khach_hang': 'Mã KH',
       'Nhom_no_KH': 'Nhóm',
       outstanding_col: 'Dư nợ NPL (tỷ)',
       overdue_col: 'Gốc quá hạn (tỷ)'
   }


   available_cols = [col for col in display_cols.keys() if col in npl_top.columns]
   npl_display = npl_top[available_cols].copy()
   npl_display.columns = [display_cols.get(col, col) for col in available_cols]


   # Format
   npl_display['Dư nợ NPL (tỷ)'] = (npl_display['Dư nợ NPL (tỷ)'] / 1e9).round(3)
   npl_display['Gốc quá hạn (tỷ)'] = (npl_display['Gốc quá hạn (tỷ)'] / 1e9).round(3)


   # Style
   def highlight_npl_table(row):
       if 'Nhóm' in row.index:
           if row['Nhóm'] == 5:
               return ['background-color: #fecaca'] * len(row)
           elif row['Nhóm'] == 4:
               return ['background-color: #fed7aa'] * len(row)
           else:
               return ['background-color: #fef3c7'] * len(row)
       return [''] * len(row)


   st.dataframe(
       npl_display.style.apply(highlight_npl_table, axis=1)
       .format({'Dư nợ NPL (tỷ)': '{:.3f}', 'Gốc quá hạn (tỷ)': '{:.3f}'}),
       use_container_width=True,
       height=500
   )


   st.caption("💡 **Ghi chú**: Màu đỏ = Nhóm 5 | Màu cam = Nhóm 4 | Màu vàng = Nhóm 3 | ✅ Đã sắp xếp từ cao → thấp")




# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# TAB C: CẢNH BÁO SỚM & DỰ BÁO
# ═════════════════════════════════════════════════════════════════════


def show_forecast_alerts(df):
   """Tab C: Cảnh báo sớm & Dự báo"""


   st.markdown("### 🔮 Phần C: Dự báo & Cảnh báo Rủi ro")
   st.markdown("---")


   # CHUẨN HÓA DỮ LIỆU
   df_temp = df.copy()
   df_temp['Nhom_no_KH'] = pd.to_numeric(df_temp['Nhom_no_KH'], errors='coerce').fillna(1).astype(int)


   outstanding_col = 'Goc_vay_con_lai_no_trong_han_no_qua_han'
   df_temp[outstanding_col] = pd.to_numeric(df_temp[outstanding_col], errors='coerce').fillna(0)


   total_outstanding = df_temp[outstanding_col].sum()


   # Tính toán các chỉ số cảnh báo
   watchlist_df = df_temp[df_temp['Nhom_no_KH'] == 2].copy()
   watchlist_debt = watchlist_df[outstanding_col].sum()
   watchlist_ratio = (watchlist_debt / total_outstanding * 100)


   npl_df = df_temp[df_temp['Nhom_no_KH'].isin([3, 4, 5])].copy()
   npl_amount = npl_df[outstanding_col].sum()
   npl_ratio = (npl_amount / total_outstanding * 100)


   # Tính toán chi tiết theo nhóm
   nhom3_debt = df_temp[df_temp['Nhom_no_KH'] == 3][outstanding_col].sum()
   nhom4_debt = df_temp[df_temp['Nhom_no_KH'] == 4][outstanding_col].sum()
   nhom5_debt = df_temp[df_temp['Nhom_no_KH'] == 5][outstanding_col].sum()


   # ═══════════════════════════════════════════════════════════════
   # KPI CARDS
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### ⚡ Chỉ báo Cảnh báo Sớm")


   col1, col2, col3, col4 = st.columns(4)


   with col1:
       st.metric(
           label="👀 Watchlist (Nhóm 2)",
           value=f"{watchlist_ratio:.2f}%",
           delta=f"{len(watchlist_df)} HĐ",
           delta_color="off"
       )


   with col2:
       st.metric(
           label="📊 NPL hiện tại",
           value=f"{npl_ratio:.2f}%",
           delta="Normal" if npl_ratio < 3 else "High",
           delta_color="normal" if npl_ratio < 3 else "inverse"
       )


   # Slider để điều chỉnh % migration
   with col3:
       migration_pct = st.slider(
           "🎚️ % Nhóm 2 trượt xuống NPL",
           min_value=10,
           max_value=100,
           value=30,
           step=10,
           help="Di chuyển thanh để xem kịch bản khác nhau"
       )


   with col4:
       potential_npl = watchlist_debt * (migration_pct / 100)
       forecast_npl_ratio = ((npl_amount + potential_npl) / total_outstanding * 100)
       st.metric(
           label=f"🔮 NPL dự báo ({migration_pct}%)",
           value=f"{forecast_npl_ratio:.2f}%",
           delta=f"+{potential_npl / 1e9:.2f} tỷ",
           delta_color="inverse"
       )


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # BIỂU ĐỒ 1: WATERFALL ĐỘNG
   # ═══════════════════════════════════════════════════════════════
   st.markdown(f"#### 📊 Kịch bản Migration: {migration_pct}% Nhóm 2 → NPL")
   st.caption(
       f"📍 Dự báo: Nếu {migration_pct}% Nhóm 2 trượt xuống NPL → NPL tăng từ {npl_ratio:.2f}% lên {forecast_npl_ratio:.2f}%")


   migration_amount = watchlist_debt * (migration_pct / 100)


   # Chuyển sang đơn vị tỷ TRƯỚC KHI VẼ
   nhom3_ty = nhom3_debt / 1e9
   nhom4_ty = nhom4_debt / 1e9
   nhom5_ty = nhom5_debt / 1e9
   migration_ty = migration_amount / 1e9
   npl_total_ty = (npl_amount + migration_amount) / 1e9


   fig_waterfall = go.Figure(go.Waterfall(
       orientation="v",
       measure=["absolute", "absolute", "absolute", "relative", "total"],
       x=["Nhóm 3", "Nhóm 4", "Nhóm 5", f"+{migration_pct}% Nhóm 2", "NPL Dự báo"],
       y=[nhom3_ty, nhom4_ty, nhom5_ty, migration_ty, npl_total_ty],
       text=[
           f"{nhom3_ty:.2f} tỷ",
           f"{nhom4_ty:.2f} tỷ",
           f"{nhom5_ty:.2f} tỷ",
           f"+{migration_ty:.2f} tỷ",
           f"{npl_total_ty:.2f} tỷ"
       ],
       textposition="outside",
       textfont=dict(size=13, color=PRIMARY, family='Arial'),
       connector={"line": {"color": SLATE_400, "width": 2}},
       increasing={"marker": {"color": NEGATIVE}},
       totals={"marker": {"color": RED_SCALE[7]}}
   ))


   fig_waterfall.update_layout(
       title={
           'text': f"NPL: {npl_ratio:.2f}% → {forecast_npl_ratio:.2f}% (Tăng {forecast_npl_ratio - npl_ratio:.2f} điểm %)",
           'font': {'size': 15, 'color': PRIMARY, 'family': 'Arial'}
       },
       height=500,
       yaxis=dict(
           title=dict(text="Dư nợ (tỷ VNĐ)", font=dict(size=14, color=PRIMARY)),
           tickfont=dict(size=13),
           tickformat='.1f',
           ticksuffix=' tỷ'
       ),
       xaxis=dict(
           title="",
           tickfont=dict(size=13)
       ),
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(248,250,252,0.5)',
       margin=dict(l=70, r=70, t=90, b=70),
       showlegend=False
   )


   st.plotly_chart(fig_waterfall, use_container_width=True)


   # Insights
   col_wf1, col_wf2, col_wf3 = st.columns(3)


   with col_wf1:
       st.metric("📊 NPL hiện tại", f"{npl_amount / 1e9:.2f} tỷ", f"{npl_ratio:.2f}%")


   with col_wf2:
       st.metric("⚠️ Tiềm năng trượt", f"{migration_amount / 1e9:.2f} tỷ", f"{migration_pct}% Nhóm 2")


   with col_wf3:
       st.metric("🔮 NPL dự báo", f"{(npl_amount + migration_amount) / 1e9:.2f} tỷ", f"{forecast_npl_ratio:.2f}%")


   st.info(f"""
**📖 Cách đọc biểu đồ Waterfall:**
- **3 cột đỏ đầu**: NPL hiện tại (Nhóm 3: {nhom3_ty:.2f} tỷ | Nhóm 4: {nhom4_ty:.2f} tỷ | Nhóm 5: {nhom5_ty:.2f} tỷ)
- **Cột +{migration_pct}% Nhóm 2**: Phần TĂNG THÊM = +{migration_ty:.2f} tỷ
- **Cột cuối (đỏ đậm)**: Tổng NPL sau khi trượt = {npl_total_ty:.2f} tỷ ({forecast_npl_ratio:.2f}%)


💡 **Điều chỉnh thanh trượt ở trên để xem kịch bản khác (10%-100%)**
   """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # BIỂU ĐỒ 2: TOP 10 CHI NHÁNH
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🎯 Top 10 Chi nhánh có Nhóm 2 cao nhất")
   st.caption("📍 Xác định chi nhánh cần ưu tiên can thiệp")


   # Tính toán theo chi nhánh
   branch_stats = df_temp.groupby('Ma_chi_nhanh').apply(
       lambda x: pd.Series({
           'Total_Debt': x[outstanding_col].sum(),
           'Nhom2_Debt': x[x['Nhom_no_KH'] == 2][outstanding_col].sum(),
           'NPL_Debt': x[x['Nhom_no_KH'].isin([3, 4, 5])][outstanding_col].sum(),
           'Nhom2_Ratio': (x[x['Nhom_no_KH'] == 2][outstanding_col].sum() / x[outstanding_col].sum() * 100) if x[
                                                                                                                   outstanding_col].sum() > 0 else 0,
           'NPL_Ratio': (x[x['Nhom_no_KH'].isin([3, 4, 5])][outstanding_col].sum() / x[outstanding_col].sum() * 100) if
           x[outstanding_col].sum() > 0 else 0,
           'Nhom2_Count': len(x[x['Nhom_no_KH'] == 2])
       }), include_groups=False
   ).reset_index()


   branch_stats = branch_stats[branch_stats['Total_Debt'] > 1e9].copy()
   top10_branches = branch_stats.nlargest(10, 'Nhom2_Ratio')


   # Grouped Bar Chart
   fig_branches = go.Figure()


   fig_branches.add_trace(go.Bar(
       name='% Nhóm 2 (Cảnh báo)',
       x=top10_branches['Ma_chi_nhanh'],
       y=top10_branches['Nhom2_Ratio'],
       marker_color=WARNING,
       text=[f"{x:.1f}%" for x in top10_branches['Nhom2_Ratio']],
       textposition='outside',
       textfont=dict(size=12, color=WARNING, family='Arial')
   ))


   fig_branches.add_trace(go.Bar(
       name='% NPL (Hiện tại)',
       x=top10_branches['Ma_chi_nhanh'],
       y=top10_branches['NPL_Ratio'],
       marker_color=NEGATIVE,
       text=[f"{x:.1f}%" for x in top10_branches['NPL_Ratio']],
       textposition='inside',
       textfont=dict(size=12, color='white', family='Arial')
   ))


   fig_branches.update_layout(
       title={
           'text': "Top 10 Chi nhánh: Nhóm 2 (Tiềm năng) vs NPL (Hiện tại)",
           'font': {'size': 15, 'color': PRIMARY, 'family': 'Arial'}
       },
       barmode='group',
       height=520,
       xaxis=dict(
           title=dict(text='Chi nhánh', font=dict(size=14, color=PRIMARY)),
           tickangle=-45,
           tickfont=dict(size=12)
       ),
       yaxis=dict(
           title=dict(text='Tỷ lệ (%)', font=dict(size=14, color=PRIMARY)),
           tickfont=dict(size=13),
           range=[0, max(top10_branches['Nhom2_Ratio']) * 1.2]
       ),
       legend=dict(
           orientation="h",
           yanchor="bottom",
           y=1.02,
           xanchor="center",
           x=0.5,
           font=dict(size=12)
       ),
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(248,250,252,0.8)',
       margin=dict(l=70, r=70, t=110, b=110)
   )


   st.plotly_chart(fig_branches, use_container_width=True)


   # Insights
   high_watch = branch_stats[branch_stats['Nhom2_Ratio'] > 10].sort_values('Nhom2_Ratio', ascending=False)


   if len(high_watch) > 0:
       st.error(f"""
**🔴 CẢNH BÁO: {len(high_watch)} chi nhánh có Nhóm 2 > 10%**
- Tổng dư nợ Nhóm 2: {high_watch['Nhom2_Debt'].sum() / 1e9:.2f} tỷ
- Tổng HĐ: {high_watch['Nhom2_Count'].sum():.0f} hợp đồng
       """)


   st.info("""
**📖 Cách đọc biểu đồ Chi nhánh:**
- **Cột Vàng**: % Nhóm 2 - Rủi ro TƯƠNG LAI
- **Cột Đỏ**: % NPL - Rủi ro HIỆN TẠI
- **Cột Vàng cao**: Cần can thiệp NGAY
- **Cả 2 cột cao**: VẤN ĐỀ NGHIÊM TRỌNG
   """)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # BIỂU ĐỒ 3: SO SÁNH 4 KỊCH BẢN
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📈 Phân tích Stress Test: 4 Kịch bản")
   st.caption("📍 NPL tăng bao nhiêu nếu 0%, 30%, 50%, 100% Nhóm 2 trượt xuống?")


   # Tính 4 kịch bản
   scenarios = []
   for pct in [0, 30, 50, 100]:
       migration = watchlist_debt * (pct / 100)
       npl_new = npl_amount + migration
       npl_ratio_new = (npl_new / total_outstanding * 100)


       scenarios.append({
           'Kịch bản': f"{pct}%",
           'Phan_tram': pct,
           'NPL_Amount_ty': npl_new / 1e9,
           'NPL_Ratio': npl_ratio_new
       })


   scenarios_df = pd.DataFrame(scenarios)


   # Dual Axis Chart
   fig_scenario = make_subplots(
       rows=1, cols=1,
       specs=[[{"secondary_y": True}]]
   )


   # Bar: NPL Amount
   fig_scenario.add_trace(
       go.Bar(
           name='Tổng NPL (tỷ VNĐ)',
           x=scenarios_df['Kịch bản'],
           y=scenarios_df['NPL_Amount_ty'],
           marker_color=[POSITIVE_LIGHT, WARNING, RED_SCALE[5], RED_SCALE[7]],
           text=[f"{x:.1f} tỷ" for x in scenarios_df['NPL_Amount_ty']],
           textposition='outside',
           textfont=dict(size=13, family='Arial'),
           width=0.5
       ),
       secondary_y=False
   )


   # Line: NPL Ratio
   fig_scenario.add_trace(
       go.Scatter(
           name='NPL Ratio (%)',
           x=scenarios_df['Kịch bản'],
           y=scenarios_df['NPL_Ratio'],
           line=dict(color=NEGATIVE_DARK, width=4),
           mode='lines+markers+text',
           marker=dict(size=14, symbol='diamond'),
           text=[f"{x:.2f}%" for x in scenarios_df['NPL_Ratio']],
           textposition='top center',
           textfont=dict(size=13, color=NEGATIVE_DARK, family='Arial Black')
       ),
       secondary_y=True
   )


   # Ngưỡng cảnh báo
   fig_scenario.add_hline(
       y=3, line_dash="dot", line_color=WARNING, line_width=3,
       annotation_text="⚠️ Ngưỡng 3%",
       annotation_position="right",
       annotation=dict(font=dict(size=12, color=WARNING)),
       secondary_y=True
   )
   fig_scenario.add_hline(
       y=5, line_dash="dot", line_color=NEGATIVE, line_width=3,
       annotation_text="🔴 Ngưỡng 5%",
       annotation_position="right",
       annotation=dict(font=dict(size=12, color=NEGATIVE)),
       secondary_y=True
   )


   fig_scenario.update_xaxes(
       title_text='% Nhóm 2 trượt xuống NPL',
       title_font=dict(size=14, color=PRIMARY),
       tickfont=dict(size=13)
   )
   fig_scenario.update_yaxes(
       title_text='Tổng NPL (tỷ VNĐ)',
       secondary_y=False,
       range=[0, max(scenarios_df['NPL_Amount_ty']) * 1.3],
       tickformat='.1f',
       ticksuffix=' tỷ',
       title_font=dict(size=14, color=PRIMARY),
       tickfont=dict(size=13)
   )
   fig_scenario.update_yaxes(
       title_text='NPL Ratio (%)',
       secondary_y=True,
       range=[0, max(scenarios_df['NPL_Ratio']) * 1.3],
       title_font=dict(size=14, color=NEGATIVE_DARK),
       tickfont=dict(size=13)
   )


   fig_scenario.update_layout(
       title={
           'text': "NPL tăng như thế nào khi Nhóm 2 trượt?",
           'font': {'size': 15, 'color': PRIMARY, 'family': 'Arial'}
       },
       height=560,
       legend=dict(
           orientation="h",
           yanchor="bottom",
           y=1.08,
           xanchor="center",
           x=0.5,
           font=dict(size=13),
           bgcolor='rgba(255,255,255,0.9)',
           bordercolor=SLATE_400,
           borderwidth=1
       ),
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(248,250,252,0.8)',
       margin=dict(l=80, r=80, t=120, b=80)
   )


   st.plotly_chart(fig_scenario, use_container_width=True)


   # Insights - BẢNG SO SÁNH
   st.markdown("##### 📊 So sánh Chi tiết")


   col_sc1, col_sc2, col_sc3, col_sc4 = st.columns(4)


   for idx, col in enumerate([col_sc1, col_sc2, col_sc3, col_sc4]):
       scenario = scenarios_df.iloc[idx]
       pct = scenario['Phan_tram']


       with col:
           if pct == 0:
               st.success(f"""
**📊 Hiện tại ({pct}%)**
- NPL: {scenario['NPL_Amount_ty']:.2f} tỷ
- Ratio: {scenario['NPL_Ratio']:.2f}%
               """)
           elif pct == 30:
               st.warning(f"""
**⚠️ Kịch bản {pct}%**
- NPL: {scenario['NPL_Amount_ty']:.2f} tỷ
- Ratio: {scenario['NPL_Ratio']:.2f}%
               """)
           else:
               st.error(f"""
**🔴 Kịch bản {pct}%**
- NPL: {scenario['NPL_Amount_ty']:.2f} tỷ
- Ratio: {scenario['NPL_Ratio']:.2f}%
               """)


   st.info(f"""
**📖 Cách đọc Stress Test:**
- **Cột màu**: Tổng NPL (tỷ VNĐ)
- **Đường đỏ**: NPL Ratio (%)
- **Đường nét đứt**: Ngưỡng 3% và 5%


**Kết luận**: Cần can thiệp NGAY {len(watchlist_df)} HĐ Nhóm 2 để tránh NPL vượt 3%
   """)






