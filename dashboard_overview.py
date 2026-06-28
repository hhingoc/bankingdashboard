import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_preprocess import load_and_clean_data
from colors_config import THEME, POSITIVE, NEGATIVE, WARNING, NPL_GROUP_COLORS


@st.cache_data
def load_data():
   try:
       df = load_and_clean_data("DSKH_BANK_ABCDEF.csv")
       return df
   except Exception as e:
       st.error(f"Lỗi: {e}")
       return pd.DataFrame()




def calculate_kpis(df):
   # 1. Dư nợ hiện tại
   total_debt = df.get("Goc_vay_con_lai_no_trong_han_no_qua_han", pd.Series([0])).fillna(0).sum()


   # 2. Tổng giải ngân
   total_disbursement = df.get("Goc_vay_giai_ngan", pd.Series([0])).fillna(0).sum()
   if total_disbursement == 0:
       goc_da_tra = 0
       for col in df.columns:
           if col.strip() == "Gốc - Đã trả" or "Principal Paid" in col:
               goc_da_tra = df[col].fillna(0).sum()
               break
       total_disbursement = total_debt + goc_da_tra


   total_contracts = len(df)


   # 3. Lợi suất
   avg_rate = df.get("Lai_Suat", pd.Series([0])).replace(0, np.nan).mean()


   # 4. Thu nhập lãi
   lai_phai_tra = df.get("Lai_thong_thuong_Phai_tra", pd.Series([0])).fillna(0).sum()
   lai_da_tra = df.get("Lai_thong_thuong_Da_tra", pd.Series([0])).fillna(0).sum()
   interest_income_forecast = lai_phai_tra - lai_da_tra


   # 5. NPL và Portfolio Quality
   if 'Nhom_no_KH' in df.columns:
       df['Nhom_no_KH'] = pd.to_numeric(df['Nhom_no_KH'], errors='coerce')


       # NPL = nhóm 3+4+5
       npl_debt = df[df['Nhom_no_KH'].isin([3, 4, 5])]['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum()
       npl_ratio = (npl_debt / total_debt * 100) if total_debt > 0 else 0


       # Portfolio Quality = % hợp đồng nhóm 1+2 (chất lượng tốt)
       good_contracts = len(df[df['Nhom_no_KH'].isin([1, 2])])
       portfolio_quality = (good_contracts / len(df) * 100) if len(df) > 0 else 0
   else:
       npl_ratio = 0
       portfolio_quality = 0


   # 6. Lãi phạt
   penalty_goc = df.get("Lai_phat_tren_goc_Phai_tra", pd.Series([0])).fillna(0).sum()
   penalty_lai = df.get("Lai_phat_tren_lai_Phai_tra", pd.Series([0])).fillna(0).sum()
   total_penalty = penalty_goc + penalty_lai


   # 7. Collection Rate
   collection_rate = (lai_da_tra / lai_phai_tra * 100) if lai_phai_tra > 0 else 0


   return {
       "Tổng Dư nợ (Tỷ VNĐ)": float(total_debt / 1e9),
       "Tổng Giải ngân (Tỷ VNĐ)": float(total_disbursement / 1e9),
       "Số lượng HĐ": int(total_contracts),
       "Lợi suất TB (%)": float(avg_rate) if not np.isnan(avg_rate) else 0.0,
       "Thu nhập Lãi dự kiến (Tỷ VNĐ)": float(interest_income_forecast / 1e9),
       "Tỷ lệ NPL (%)": float(npl_ratio),
       "Lãi phạt phải thu (Triệu VNĐ)": float(total_penalty / 1e6),
       "Collection Rate (%)": float(collection_rate),
       "Portfolio Quality (%)": float(portfolio_quality)
   }




def create_gauge_chart(value, title, min_val=0, max_val=100,
                      threshold_good=80, threshold_warning=50,
                      reverse=False):
   """
   Tạo Gauge Chart (100% từ dữ liệu thực)
   """


   # Xác định màu
   if reverse:
       # NPL: thấp = tốt
       if value < threshold_warning:
           color = "#10b981"
       elif value < threshold_good:
           color = "#f59e0b"
       else:
           color = "#ef4444"
   else:
       # Collection, Quality: cao = tốt
       if value >= threshold_good:
           color = "#10b981"
       elif value >= threshold_warning:
           color = "#f59e0b"
       else:
           color = "#ef4444"


   fig = go.Figure(go.Indicator(
       mode="gauge+number",
       value=value,
       title={'text': title, 'font': {'size': 16, 'color': '#2c3e50', 'family': 'Arial'}},
       number={'suffix': "%", 'font': {'size': 36, 'color': color, 'family': 'Arial'}},
       gauge={
           'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': '#64748b'},
           'bar': {'color': color, 'thickness': 0.7},
           'bgcolor': "white",
           'borderwidth': 2,
           'bordercolor': "#e5e7eb",
           'steps': [
               {'range': [min_val, threshold_warning], 'color': '#fee2e2' if not reverse else '#d1fae5'},
               {'range': [threshold_warning, threshold_good], 'color': '#fef3c7'},
               {'range': [threshold_good, max_val], 'color': '#d1fae5' if not reverse else '#fee2e2'}
           ],
           'threshold': {
               'line': {'color': color, 'width': 4},
               'thickness': 0.8,
               'value': value
           }
       }
   ))


   fig.update_layout(
       height=250,
       margin=dict(l=10, r=10, t=50, b=10),
       paper_bgcolor="rgba(0,0,0,0)",
       font={'family': "Arial, sans-serif"}
   )


   return fig




def create_debt_structure_chart(df):
   """
   Tạo biểu đồ kết hợp Donut Chart + Bar Chart về cấu trúc tài sản
   Tối ưu cho Dark Theme với gradient và màu sắc nổi bật
   """
   from colors_config import THEME, POSITIVE, WARNING, NEGATIVE
   import numpy as np


   # ✅ FIX: Tính toán dữ liệu với xử lý an toàn
   def safe_sum(series):
       """Chuyển về numeric và tính tổng an toàn"""
       return pd.to_numeric(series, errors='coerce').fillna(0).sum()


   goc_trong_han = safe_sum(df.get('Goc_trong_han', pd.Series(0)))
   goc_qua_han = safe_sum(df.get('Goc_qua_han', pd.Series(0)))
   lai_phai_tra = safe_sum(df.get('Lai_thong_thuong_Phai_tra', pd.Series(0)))
   lai_da_tra = safe_sum(df.get('Lai_thong_thuong_Da_tra', pd.Series(0)))
   lai_con_lai = lai_phai_tra - lai_da_tra


   # ✅ Đảm bảo tất cả là float
   goc_trong_han = float(goc_trong_han)
   goc_qua_han = float(goc_qua_han)
   lai_con_lai = float(lai_con_lai)


   # ═══════════════════════════════════════════════════════════════
   # SUBPLOT: DONUT (TRÁI) + BAR (PHẢI)
   # ═══════════════════════════════════════════════════════════════
   from plotly.subplots import make_subplots
   import plotly.graph_objects as go


   fig = make_subplots(
       rows=1, cols=2,
       specs=[[{'type': 'domain'}, {'type': 'bar'}]],
       column_widths=[0.4, 0.6],
       subplot_titles=['Cấu trúc Tài sản', 'Chi tiết (Tỷ VNĐ)']
   )


   # ─────────────────────────────────────────────────────────────
   # 1. DONUT CHART - BÊN TRÁI
   # ─────────────────────────────────────────────────────────────
   labels = ['Gốc trong hạn', 'Gốc quá hạn', 'Lãi phải thu']
   values = [goc_trong_han / 1e9, goc_qua_han / 1e9, lai_con_lai / 1e9]


   # ✅ Màu gradient cho donut
   colors = ['#10B981', '#F59E0B', '#8B5CF6']


   fig.add_trace(go.Pie(
       labels=labels,
       values=values,
       hole=0.6,
       marker=dict(
           colors=colors,
           line=dict(color='#1B134D', width=3)
       ),
       textinfo='label+percent',
       textfont=dict(size=14, color='white', family='Inter, sans-serif'),
       hovertemplate='<b>%{label}</b><br>' +
                     'Giá trị: %{value:.2f} tỷ<br>' +
                     'Tỷ lệ: %{percent}<br>' +
                     '<extra></extra>',
       showlegend=False
   ), row=1, col=1)


   # ─────────────────────────────────────────────────────────────
   # 2. BAR CHART - BÊN PHẢI
   # ─────────────────────────────────────────────────────────────
   fig.add_trace(go.Bar(
       x=[goc_trong_han / 1e9, goc_qua_han / 1e9, lai_con_lai / 1e9],
       y=['Gốc trong hạn', 'Gốc quá hạn', 'Lãi phải thu'],
       orientation='h',
       marker=dict(
           color=colors,
           line=dict(color='rgba(255,255,255,0.2)', width=1)
       ),
       text=[
           f"{goc_trong_han / 1e9:.1f}",
           f"{goc_qua_han / 1e9:.1f}",
           f"{lai_con_lai / 1e9:.1f}"
       ],
       textposition='outside',
       textfont=dict(size=14, color='white', family='Inter, sans-serif'),
       hovertemplate='<b>%{y}</b><br>' +
                     'Giá trị: %{x:.2f} tỷ VNĐ<br>' +
                     '<extra></extra>',
       showlegend=False
   ), row=1, col=2)


   # ═══════════════════════════════════════════════════════════════
   # LAYOUT - DARK THEME
   # ═══════════════════════════════════════════════════════════════
   fig.update_layout(
       height=400,
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(0,0,0,0)',
       font=dict(color='white', family='Inter, sans-serif', size=13),
       margin=dict(l=50, r=50, t=80, b=50),


       hoverlabel=dict(
           bgcolor='rgba(27, 19, 77, 0.95)',
           font_size=13,
           font_family='Inter, sans-serif',
           font_color='white',
           bordercolor='#6033BF'
       ),


       annotations=[
           dict(
               text='Cấu trúc Tài sản',
               x=0.15,
               y=1.1,
               xref='paper',
               yref='paper',
               showarrow=False,
               font=dict(size=16, color='white', family='Inter, sans-serif')
           ),
           dict(
               text='Chi tiết (Tỷ VNĐ)',
               x=0.7,
               y=1.1,
               xref='paper',
               yref='paper',
               showarrow=False,
               font=dict(size=16, color='white', family='Inter, sans-serif')
           )
       ]
   )


   # X-axis styling
   fig.update_xaxes(
       showgrid=True,
       gridcolor='rgba(255,255,255,0.1)',
       gridwidth=1,
       zeroline=True,
       zerolinecolor='rgba(255,255,255,0.2)',
       tickfont=dict(color='white', size=12),
       title_font=dict(color='white'),
       row=1, col=2
   )


   # Y-axis styling
   fig.update_yaxes(
       showgrid=False,
       tickfont=dict(color='white', size=13),
       title_font=dict(color='white'),
       row=1, col=2
   )


   return fig




def create_npl_heatmap(df):
   """
   Heatmap Ma trận Rủi ro: Nhóm nợ × Chi nhánh
   Tối ưu cho Dark Theme với gradient nổi bật
   """
   from colors_config import THEME


   df_temp = df.copy()
   df_temp['Nhom_no_KH'] = pd.to_numeric(df_temp['Nhom_no_KH'], errors='coerce')


   # Tạo dữ liệu heatmap
   heatmap_data = df_temp.groupby(['Ma_chi_nhanh', 'Nhom_no_KH']).size().reset_index(name='So_luong')
   pivot = heatmap_data.pivot(index='Ma_chi_nhanh', columns='Nhom_no_KH', values='So_luong').fillna(0)


   # Đảm bảo có đủ 5 nhóm
   for nhom in [1, 2, 3, 4, 5]:
       if nhom not in pivot.columns:
           pivot[nhom] = 0


   pivot = pivot[[1, 2, 3, 4, 5]]
   pivot.columns = [f'Nhóm {int(x)}' for x in pivot.columns]


   # Sắp xếp theo tổng (giảm dần)
   pivot['Tong'] = pivot.sum(axis=1)
   pivot = pivot.sort_values('Tong', ascending=False)
   num_branches = len(pivot)
   pivot = pivot.drop('Tong', axis=1)


   # Transform data cho colorscale
   z_custom = pivot.copy()
   for i, col in enumerate(pivot.columns):
       col_values = pivot[col].values
       col_max = col_values.max()
       if col_max > 0:
           normalized = col_values / col_max
           z_custom[col] = (i * 1.0) + (normalized * 0.9)
       else:
           z_custom[col] = i * 1.0


   # ✅ COLORSCALE GRADIENT CHO DARK THEME
   colorscale = [
       # Nhóm 1: Xanh lá
       [0.0, 'rgba(16, 185, 129, 0.1)'], [0.05, 'rgba(16, 185, 129, 0.3)'],
       [0.10, 'rgba(16, 185, 129, 0.5)'], [0.15, 'rgba(16, 185, 129, 0.7)'],
       [0.18, 'rgba(16, 185, 129, 0.9)'],


       # Nhóm 2: Xanh dương
       [0.20, 'rgba(59, 130, 246, 0.1)'], [0.25, 'rgba(59, 130, 246, 0.4)'],
       [0.30, 'rgba(59, 130, 246, 0.6)'], [0.36, 'rgba(59, 130, 246, 0.8)'],


       # Nhóm 3: Vàng/Cam
       [0.40, 'rgba(245, 158, 11, 0.2)'], [0.45, 'rgba(245, 158, 11, 0.5)'],
       [0.50, 'rgba(245, 158, 11, 0.7)'], [0.54, 'rgba(245, 158, 11, 0.9)'],


       # Nhóm 4: Cam đỏ
       [0.60, 'rgba(251, 146, 60, 0.3)'], [0.65, 'rgba(251, 146, 60, 0.6)'],
       [0.70, 'rgba(251, 146, 60, 0.8)'], [0.72, 'rgba(251, 146, 60, 1.0)'],


       # Nhóm 5: Đỏ
       [0.80, 'rgba(239, 68, 68, 0.4)'], [0.85, 'rgba(239, 68, 68, 0.6)'],
       [0.90, 'rgba(239, 68, 68, 0.8)'], [0.95, 'rgba(239, 68, 68, 0.95)'],
       [1.0, 'rgba(220, 38, 38, 1.0)']
   ]


   # Text matrix
   text_matrix = pivot.values.astype(int).astype(str)
   text_matrix = [['' if v == '0' else v for v in row] for row in text_matrix]


   # Chiều cao động
   dynamic_height = max(500, num_branches * 30 + 150)


   # ═══════════════════════════════════════════════════════════════
   # TẠO HEATMAP
   # ═══════════════════════════════════════════════════════════════
   fig = go.Figure(data=go.Heatmap(
       z=z_custom.values,
       x=pivot.columns,
       y=pivot.index,
       colorscale=colorscale,
       showscale=False,
       text=text_matrix,
       texttemplate='%{text}',
       textfont={"size": 11, "color": "white", "family": "Inter, sans-serif"},
       hovertemplate='<b>Chi nhánh: %{y}</b><br>%{x}: %{customdata} HĐ<extra></extra>',
       customdata=pivot.values.astype(int),
       xgap=3,
       ygap=2,
       zmin=0,
       zmax=5
   ))


   # ═══════════════════════════════════════════════════════════════
   # LAYOUT - DARK THEME (CÚ PHÁP MỚI)
   # ═══════════════════════════════════════════════════════════════
   fig.update_layout(
       title={
           'text': f'🔥 Ma trận Rủi ro: Nhóm nợ × Chi nhánh ({num_branches} CN)',
           'font': {'size': 20, 'color': 'white', 'family': 'Inter, sans-serif'},
           'x': 0.5,
           'xanchor': 'center'
       },
       height=dynamic_height,
       plot_bgcolor='rgba(0,0,0,0)',
       paper_bgcolor='rgba(0,0,0,0)',
       font=dict(color='white', family='Inter, sans-serif'),
       margin=dict(l=120, r=40, t=100, b=80),


       hoverlabel=dict(
           bgcolor='rgba(27, 19, 77, 0.95)',
           font_size=13,
           font_family='Inter, sans-serif',
           font_color='white',
           bordercolor='#6033BF'
       )
   )


   # ✅ FIX: Cú pháp mới cho xaxis (dùng title dict thay vì titlefont)
   fig.update_xaxes(
       title=dict(
           text='Phân loại Nhóm nợ',
           font=dict(color='white', size=14, family='Inter, sans-serif')
       ),
       side='bottom',
       showgrid=False,
       tickfont=dict(color='white', size=12)
   )


   # ✅ FIX: Cú pháp mới cho yaxis
   fig.update_yaxes(
       title=dict(
           text='Mã Chi nhánh',
           font=dict(color='white', size=14, family='Inter, sans-serif')
       ),
       showgrid=False,
       tickfont=dict(color='white', size=10)
   )


   return fig




def create_term_distribution_chart(df):
   """
   Stacked Bar: Phân bổ Kỳ hạn theo Chi nhánh - Top 10
   OCEAN WAVE Gradient - Hiện đại và chuyên nghiệp
   """
   from colors_config import THEME


   # Tìm cột kỳ hạn
   term_col = None
   for col in df.columns:
       if any(x in str(col).lower() for x in ['ky_han', 'kỳ hạn', 'ky han']):
           term_col = col
           break


   if not term_col:
       return None


   # Phân loại kỳ hạn
   def classify_term(value):
       try:
           if isinstance(value, str):
               value = value.replace('M', '').strip()
           months = float(value)


           if months <= 12:
               return 'Ngắn hạn (≤12T)'
           elif months <= 60:
               return 'Trung hạn (1-5N)'
           else:
               return 'Dài hạn (>5N)'
       except:
           return 'Không xác định'


   df_temp = df.copy()
   df_temp['Loai_KH'] = df_temp[term_col].apply(classify_term)


   # Group by chi nhánh và kỳ hạn
   branch_term = df_temp.groupby(['Ma_chi_nhanh', 'Loai_KH']).agg({
       'Goc_vay_con_lai_no_trong_han_no_qua_han': 'sum'
   }).reset_index()


   branch_term.columns = ['Chi_nhanh', 'Loai_KH', 'Du_no']
   branch_term['Du_no_ty'] = branch_term['Du_no'] / 1e9


   # Pivot để tạo stacked bar
   pivot = branch_term.pivot(index='Chi_nhanh', columns='Loai_KH', values='Du_no_ty').fillna(0)


   # Lấy Top 10 chi nhánh
   pivot['Tong'] = pivot.sum(axis=1)
   pivot = pivot.sort_values('Tong', ascending=False).head(10)
   pivot = pivot.drop('Tong', axis=1)


   # Đảm bảo thứ tự cột
   expected_cols = ['Ngắn hạn (≤12T)', 'Trung hạn (1-5N)', 'Dài hạn (>5N)', 'Không xác định']
   for col in expected_cols:
       if col not in pivot.columns:
           pivot[col] = 0


   pivot = pivot[expected_cols]


   # ✅ OCEAN WAVE GRADIENT - Cyan → Blue → Navy
   colors = {
       'Ngắn hạn (≤12T)': '#22D3EE',  # Cyan - Linh hoạt, sáng
       'Trung hạn (1-5N)': '#3B82F6',  # Blue - Cân bằng
       'Dài hạn (>5N)': '#1E3A8A',  # Navy - Cam kết sâu
       'Không xác định': '#6B7280'  # Gray - Trung tính
   }


   # ═══════════════════════════════════════════════════════════════
   # TẠO STACKED BAR CHART
   # ═══════════════════════════════════════════════════════════════
   fig = go.Figure()


   for col in pivot.columns:
       if pivot[col].sum() > 0:
           fig.add_trace(go.Bar(
               name=col,
               x=pivot.index,
               y=pivot[col],
               marker=dict(
                   color=colors.get(col, '#64748b'),
                   line=dict(color='rgba(255,255,255,0.2)', width=1)
               ),
               hovertemplate='<b>%{x}</b><br>' + col + ': %{y:.2f} tỷ<extra></extra>',
               text=pivot[col].round(1),
               textposition='inside',
               textfont=dict(color='white', size=10, family='Inter, sans-serif'),
               texttemplate='%{text}'
           ))


   # ═══════════════════════════════════════════════════════════════
   # LAYOUT - DARK THEME
   # ═══════════════════════════════════════════════════════════════
   fig.update_layout(
       title={
           'text': '⏱️ Phân bổ Kỳ hạn theo Chi nhánh (Top 10)<br>' +
                   '<sub style="color: rgba(255,255,255,0.6);">',
           'font': {'size': 20, 'color': 'white', 'family': 'Inter, sans-serif'},
           'x': 0.5,
           'xanchor': 'center'
       },
       barmode='stack',
       plot_bgcolor='rgba(0,0,0,0)',
       paper_bgcolor='rgba(0,0,0,0)',
       font=dict(color='white', family='Inter, sans-serif'),
       height=500,
       margin=dict(l=70, r=40, t=110, b=130),


       # ✅ Legend styling
       legend=dict(
           orientation='h',
           yanchor='bottom',
           y=1.02,
           xanchor='center',
           x=0.5,
           bgcolor='rgba(255,255,255,0.05)',
           bordercolor='rgba(255,255,255,0.2)',
           borderwidth=1,
           font=dict(color='white', size=12, family='Inter, sans-serif')
       ),


       # ✅ Hover styling
       hoverlabel=dict(
           bgcolor='rgba(27, 19, 77, 0.95)',
           font_size=13,
           font_family='Inter, sans-serif',
           font_color='white',
           bordercolor='#22D3EE'  # Cyan border cho ocean theme
       )
   )


   # ✅ X-axis styling
   fig.update_xaxes(
       title=dict(
           text='Mã Chi nhánh',
           font=dict(color='white', size=14, family='Inter, sans-serif')
       ),
       showgrid=False,
       tickangle=-45,
       tickfont=dict(color='white', size=11),
       linecolor='rgba(255,255,255,0.2)',
       linewidth=1
   )


   # ✅ Y-axis styling
   fig.update_yaxes(
       title=dict(
           text='Dư nợ (Tỷ VNĐ)',
           font=dict(color='white', size=14, family='Inter, sans-serif')
       ),
       showgrid=True,
       gridcolor='rgba(255,255,255,0.1)',
       gridwidth=1,
       tickfont=dict(color='white', size=11),
       linecolor='rgba(255,255,255,0.2)',
       linewidth=1,
       zeroline=True,
       zerolinecolor='rgba(255,255,255,0.2)',
       zerolinewidth=1
   )


   return fig




def create_disbursement_trend(df):
   """
   Area Chart: Giải ngân theo NĂM 2014-2024
   Tối ưu cho Dark Theme với gradient nổi bật
   """
   from colors_config import THEME


   if 'Nam_giai_ngan' not in df.columns:
       st.warning("Không có dữ liệu thời gian giải ngân")
       return None


   # Loại bỏ năm không hợp lệ
   df_temp = df[
       (df['Nam_giai_ngan'] >= 2014) &
       (df['Nam_giai_ngan'] <= 2024)
       ].copy()


   if len(df_temp) == 0:
       st.warning("Không có dữ liệu giải ngân từ 2014-2024")
       return None


   # Group theo NĂM
   trend_data = df_temp.groupby('Nam_giai_ngan').agg({
       'Goc_vay_giai_ngan': 'sum',
       'Ma_khach_hang': 'count'
   }).reset_index()


   trend_data.columns = ['Nam', 'Giai_ngan', 'So_HD']
   trend_data['Giai_ngan_ty'] = trend_data['Giai_ngan'] / 1e9
   trend_data = trend_data.sort_values('Nam')


   # Tính metrics
   total = trend_data['Giai_ngan_ty'].sum()
   first_year = trend_data.iloc[0]['Nam'] if len(trend_data) > 0 else 2014
   last_year = trend_data.iloc[-1]['Nam'] if len(trend_data) > 0 else 2024
   num_years = last_year - first_year
   first_val = trend_data.iloc[0]['Giai_ngan_ty'] if len(trend_data) > 0 else 0
   last_val = trend_data.iloc[-1]['Giai_ngan_ty'] if len(trend_data) > 0 else 0


   # CAGR
   if first_val > 0 and num_years > 0:
       cagr = ((last_val / first_val) ** (1 / num_years) - 1) * 100
   else:
       cagr = 0


   # ═══════════════════════════════════════════════════════════════
   # TẠO AREA CHART
   # ═══════════════════════════════════════════════════════════════
   fig = go.Figure()


   # ✅ Area fill với gradient tím-xanh nổi bật
   fig.add_trace(go.Scatter(
       x=trend_data['Nam'],
       y=trend_data['Giai_ngan_ty'],
       fill='tozeroy',
       fillcolor='rgba(16, 185, 129, 0.3)',  # Emerald trong suốt
       line=dict(
           color='#10B981',  # Emerald sáng
           width=3,
           shape='spline'
       ),
       mode='lines+markers',
       marker=dict(
           size=10,
           color='#10B981',
           line=dict(color='white', width=2),
           symbol='circle'
       ),
       name='Giải ngân',
       hovertemplate='<b>Năm %{x}</b><br>' +
                     'Giải ngân: %{y:.2f} tỷ<br>' +
                     'Số HĐ: %{customdata:,}<extra></extra>',
       customdata=trend_data['So_HD']
   ))


   # ═══════════════════════════════════════════════════════════════
   # LAYOUT - DARK THEME
   # ═══════════════════════════════════════════════════════════════
   fig.update_layout(
       title={
           'text': f'📈 Lịch sử Giải ngân {int(first_year)}-{int(last_year)}<br>' +
                   f'<sub style="color: rgba(255,255,255,0.7);">Tổng: {total:.1f} tỷ | CAGR: {cagr:+.1f}%/năm</sub>',
           'font': {'size': 20, 'color': 'white', 'family': 'Inter, sans-serif'},
           'x': 0.5,
           'xanchor': 'center'
       },
       plot_bgcolor='rgba(0,0,0,0)',
       paper_bgcolor='rgba(0,0,0,0)',
       font=dict(color='white', family='Inter, sans-serif'),
       height=450,
       margin=dict(l=70, r=40, t=110, b=80),
       hovermode='x unified',
       showlegend=False,


       # ✅ Hover styling
       hoverlabel=dict(
           bgcolor='rgba(27, 19, 77, 0.95)',
           font_size=13,
           font_family='Inter, sans-serif',
           font_color='white',
           bordercolor='#8B5CF6'
       )
   )


   # ✅ X-axis styling
   fig.update_xaxes(
       title=dict(
           text='Năm',
           font=dict(color='white', size=14, family='Inter, sans-serif')
       ),
       showgrid=True,
       gridcolor='rgba(255,255,255,0.1)',
       gridwidth=1,
       tickmode='linear',
       dtick=1,
       tickangle=0,
       tickfont=dict(color='white', size=11),
       linecolor='rgba(255,255,255,0.2)',
       linewidth=1
   )


   # ✅ Y-axis styling
   fig.update_yaxes(
       title=dict(
           text='Giải ngân (Tỷ VNĐ)',
           font=dict(color='white', size=14, family='Inter, sans-serif')
       ),
       showgrid=True,
       gridcolor='rgba(255,255,255,0.1)',
       gridwidth=1,
       rangemode='tozero',
       tickfont=dict(color='white', size=11),
       linecolor='rgba(255,255,255,0.2)',
       linewidth=1,
       zeroline=True,
       zerolinecolor='rgba(255,255,255,0.2)',
       zerolinewidth=1
   )


   # ✅ Annotations cho năm đầu và cuối
   annotations = [
       dict(
           x=first_year,
           y=first_val,
           text=f"<b>{first_val:.1f}T</b>",
           showarrow=True,
           arrowhead=2,
           arrowcolor='#10B981',
           arrowwidth=2,
           ax=0,
           ay=-40,
           font=dict(size=13, color='#10B981', family='Inter, sans-serif'),
           bgcolor='rgba(16, 185, 129, 0.2)',
           bordercolor='#10B981',
           borderwidth=1,
           borderpad=4,
           opacity=0.9
       ),
       dict(
           x=last_year,
           y=last_val,
           text=f"<b>{last_val:.1f}T</b>",
           showarrow=True,
           arrowhead=2,
           arrowcolor='#10B981',
           arrowwidth=2,
           ax=0,
           ay=-40,
           font=dict(size=13, color='#10B981', family='Inter, sans-serif'),
           bgcolor='rgba(16, 185, 129, 0.2)',
           bordercolor='#10B981',
           borderwidth=1,
           borderpad=4,
           opacity=0.9
       )
   ]


   fig.update_layout(annotations=annotations)


   return fig




def show_overview_section(df):
   # ✅ CSS để chỉnh màu text trong Plotly charts
   st.markdown("""
       <style>
       /* Màu trắng cho title và text trong Plotly charts */
       .js-plotly-plot .plotly text {
           fill: white !important;
       }


       /* Màu trắng cho gauge chart titles */
       .js-plotly-plot .gtitle {
           fill: white !important;
       }


       /* Màu trắng cho số trong gauge */
       .js-plotly-plot .number {
           fill: white !important;
       }
       </style>
   """, unsafe_allow_html=True)


   kpis = calculate_kpis(df)


   # ═══════════════════════════════════════════════════════════════════
   # CSS CHO KPI CARDS VỚI GRADIENT THEO MÀU BẠN ĐỀ XUẤT
   # ═══════════════════════════════════════════════════════════════════
   st.markdown("""
       <style>
       /* Base style cho tất cả KPI cards */
       .kpi-card {
           border-radius: 16px;
           padding: 1.5rem;
           box-shadow: 0 4px 12px rgba(0,0,0,0.3);
           transition: all 0.3s ease;
           position: relative;
           overflow: hidden;
           min-height: 160px;
           display: flex;
           flex-direction: column;
           justify-content: space-between;
       }


       .kpi-card:hover {
           transform: translateY(-5px);
           box-shadow: 0 8px 24px rgba(0,0,0,0.4);
       }


       /* === NHÓM 1: QUY MÔ - Xanh dương === */
       .kpi-scale {
           background: linear-gradient(135deg, #2563EB, #3B82F6);
           color: white;
       }


       /* === NHÓM 2: LỢI NHUẬN - Xanh lá === */
       .kpi-profit {
           background: linear-gradient(135deg, #10B981, #34D399);
           color: white;
       }


       /* === NHÓM 3: RỦI RO - Đỏ === */
       .kpi-risk {
           background: linear-gradient(135deg, #EF4444, #F87171);
           color: white;
       }


       /* === NHÓM 4: HIỆU QUẢ - Vàng/Cam === */
       .kpi-efficiency {
           background: linear-gradient(135deg, #F59E0B, #FBBF24);
           color: white;
       }


       /* Icon trong card */
       .kpi-icon {
           font-size: 36px;
           opacity: 0.9;
           margin-bottom: 0.5rem;
       }


       /* Label */
       .kpi-label {
           font-size: 14px;
           opacity: 0.95;
           margin-bottom: 0.5rem;
           font-weight: 500;
           letter-spacing: 0.5px;
       }


       /* Value */
       .kpi-value {
           font-size: 32px;
           font-weight: 700;
           margin-bottom: 0.5rem;
           text-shadow: 0 2px 4px rgba(0,0,0,0.1);
       }


       /* Status badge */
       .kpi-status {
           display: inline-block;
           padding: 4px 12px;
           border-radius: 12px;
           font-size: 12px;
           font-weight: 600;
           background: rgba(255,255,255,0.25);
           backdrop-filter: blur(10px);
       }


       /* Progress circle decoration */
       .progress-circle {
           position: absolute;
           bottom: 15px;
           right: 15px;
           width: 50px;
           height: 50px;
           border-radius: 50%;
           border: 3px solid rgba(255,255,255,0.3);
           border-top-color: rgba(255,255,255,0.8);
           opacity: 0.6;
       }


       /* Section headers */
       .section-header {
           font-size: 20px;
           font-weight: 700;
           margin: 1.5rem 0 1rem 0;
           padding-left: 0.5rem;
           border-left: 4px solid;
           display: flex;
           align-items: center;
           gap: 10px;
       }


       .header-scale { border-color: #3B82F6; color: #3B82F6; }
       .header-profit { border-color: #10B981; color: #10B981; }
       .header-risk { border-color: #EF4444; color: #EF4444; }
       .header-efficiency { border-color: #F59E0B; color: #F59E0B; }
       </style>
   """, unsafe_allow_html=True)
   # ═══════════════════════════════════════════════════════════════════
   # HÀNG 1: NHÓM 1 (QUY MÔ) + NHÓM 2 (LỢI NHUẬN)
   # ═══════════════════════════════════════════════════════════════════


   row1_col_left, row1_col_right = st.columns([1, 1])


   # --- NHÓM 1: QUY MÔ (Bên trái) ---
   with row1_col_left:
       st.markdown('<div class="section-header header-scale">📊 NHÓM 1: QUY MÔ</div>', unsafe_allow_html=True)


       col1, col2, col3 = st.columns(3)


       with col1:
           st.markdown(f"""
               <div class="kpi-card kpi-scale">
                   <div class="kpi-icon">📊</div>
                   <div class="kpi-label">Tổng Dư nợ</div>
                   <div class="kpi-value">{kpis['Tổng Dư nợ (Tỷ VNĐ)']:.2f} tỷ</div>
                   <div class="kpi-status">Gốc còn lại</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


       with col2:
           st.markdown(f"""
               <div class="kpi-card kpi-scale">
                   <div class="kpi-icon">💵</div>
                   <div class="kpi-label">Tổng Giải ngân</div>
                   <div class="kpi-value">{kpis['Tổng Giải ngân (Tỷ VNĐ)']:.2f} tỷ</div>
                   <div class="kpi-status">Tổng GN</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


       with col3:
           st.markdown(f"""
               <div class="kpi-card kpi-scale">
                   <div class="kpi-icon">📋</div>
                   <div class="kpi-label">Số lượng HĐ</div>
                   <div class="kpi-value">{kpis['Số lượng HĐ']:,}</div>
                   <div class="kpi-status">Hợp đồng</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


   # --- NHÓM 2: LỢI NHUẬN (Bên phải) ---
   with row1_col_right:
       st.markdown('<div class="section-header header-profit">💰 NHÓM 2: LỢI NHUẬN</div>', unsafe_allow_html=True)


       col4, col5 = st.columns(2)


       with col4:
           rate = kpis["Lợi suất TB (%)"]
           if 9 <= rate <= 13:
               status = "✓ Tốt"
           elif rate < 9:
               status = "↓ Thấp"
           else:
               status = "! Cao"


           st.markdown(f"""
               <div class="kpi-card kpi-profit">
                   <div class="kpi-icon">📈</div>
                   <div class="kpi-label">Lợi suất TB</div>
                   <div class="kpi-value">{rate:.2f}%</div>
                   <div class="kpi-status">{status} (9-13%)</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


       with col5:
           st.markdown(f"""
               <div class="kpi-card kpi-profit">
                   <div class="kpi-icon">💸</div>
                   <div class="kpi-label">Thu nhập Lãi DK</div>
                   <div class="kpi-value">{kpis['Thu nhập Lãi dự kiến (Tỷ VNĐ)']:.2f} tỷ</div>
                   <div class="kpi-status">Lãi còn thu</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


   st.markdown("<br>", unsafe_allow_html=True)


   # ═══════════════════════════════════════════════════════════════════
   # HÀNG 2: NHÓM 3 (RỦI RO) + NHÓM 4 (HIỆU QUẢ)
   # ═══════════════════════════════════════════════════════════════════


   row2_col_left, row2_col_right = st.columns([1, 1])


   # --- NHÓM 3: RỦI RO (Bên trái) ---
   with row2_col_left:
       st.markdown('<div class="section-header header-risk">⚠️ NHÓM 3: RỦI RO</div>', unsafe_allow_html=True)


       col6, col7 = st.columns(2)


       with col6:
           npl = kpis["Tỷ lệ NPL (%)"]
           if npl < 2:
               status = "✓ An toàn"
           elif npl < 3:
               status = "! Cảnh báo"
           else:
               status = "⚠ Cao"


           st.markdown(f"""
               <div class="kpi-card kpi-risk">
                   <div class="kpi-icon">📊</div>
                   <div class="kpi-label">Tỷ lệ NPL</div>
                   <div class="kpi-value">{npl:.2f}%</div>
                   <div class="kpi-status">{status} (<2%)</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


       with col7:
           penalty = kpis["Lãi phạt phải thu (Triệu VNĐ)"]
           if penalty < 500:
               status = "✓ Tốt"
           elif penalty < 1000:
               status = "! Chú ý"
           else:
               status = "⚠ Cao"


           st.markdown(f"""
               <div class="kpi-card kpi-risk">
                   <div class="kpi-icon">⚠️</div>
                   <div class="kpi-label">Lãi phạt PT</div>
                   <div class="kpi-value">{penalty:.0f} tr</div>
                   <div class="kpi-status">{status} (<500)</div>
                   <div class="progress-circle"></div>
               </div>
           """, unsafe_allow_html=True)


   # --- NHÓM 4: HIỆU QUẢ (Bên phải) ---
   with row2_col_right:
       st.markdown('<div class="section-header header-efficiency">✓ NHÓM 4: HIỆU QUẢ</div>', unsafe_allow_html=True)


       collection = kpis["Collection Rate (%)"]
       if collection >= 95:
           status = "★ Xuất sắc"
       elif collection >= 90:
           status = "✓ Tốt"
       else:
           status = "! Cải thiện"


       st.markdown(f"""
           <div class="kpi-card kpi-efficiency">
               <div class="kpi-icon">✓</div>
               <div class="kpi-label">Collection Rate</div>
               <div class="kpi-value">{collection:.2f}%</div>
               <div class="kpi-status">{status} (≥95%)</div>
               <div class="progress-circle"></div>
           </div>
       """, unsafe_allow_html=True)


   st.markdown("---")
   # =================================================================
   # 3 GAUGE CHARTS - DARK THEME WITH GRADIENTS
   # =================================================================
   st.markdown("---")
   st.markdown("### 📊 Bảng Điều khiển Chỉ số Quan trọng")
   st.caption("⚡ 3 Gauge Charts - 100% từ dữ liệu thực tế")


   col_g1, col_g2, col_g3 = st.columns(3)


   # ─────────────────────────────────────────────────────────────────
   # GAUGE 1: NPL RATIO (Đỏ - Cảnh báo rủi ro)
   # ─────────────────────────────────────────────────────────────────
   with col_g1:
       fig_npl = create_gauge_chart(
           value=kpis["Tỷ lệ NPL (%)"],
           title="🎯 NPL Ratio",
           min_val=0,
           max_val=10,
           threshold_warning=2,
           threshold_good=3,
           reverse=True
       )
       st.plotly_chart(fig_npl, use_container_width=True)


       # ✅ Info box với gradient đỏ nổi bật
       st.markdown(f"""
       <div style='
           text-align: center;
           background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(248, 113, 113, 0.15));
           border: 1px solid rgba(239, 68, 68, 0.3);
           border-left: 4px solid #EF4444;
           padding: 1rem;
           border-radius: 12px;
           box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
       '>
           <div style='font-size: 18px; font-weight: 700; color: #FCA5A5; margin-bottom: 0.5rem;'>
               Target: <2%
           </div>
           <div style='font-size: 13px; color: rgba(255, 255, 255, 0.7);'>
               Tỷ lệ nợ xấu (Nhóm 3+4+5)
           </div>
           <div style='font-size: 24px; font-weight: 700; color: white; margin-top: 0.5rem;'>
               {kpis["Tỷ lệ NPL (%)"]:.2f}%
           </div>
       </div>
       """, unsafe_allow_html=True)


   # ─────────────────────────────────────────────────────────────────
   # GAUGE 2: COLLECTION RATE (Xanh lá - Hiệu quả thu hồi)
   # ─────────────────────────────────────────────────────────────────
   with col_g2:
       fig_collection = create_gauge_chart(
           value=kpis["Collection Rate (%)"],
           title="💰 Collection Rate",
           min_val=0,
           max_val=100,
           threshold_warning=90,
           threshold_good=95,
           reverse=False
       )
       st.plotly_chart(fig_collection, use_container_width=True)


       # ✅ Info box với gradient xanh lá nổi bật
       st.markdown(f"""
       <div style='
           text-align: center;
           background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(52, 211, 153, 0.15));
           border: 1px solid rgba(16, 185, 129, 0.3);
           border-left: 4px solid #10B981;
           padding: 1rem;
           border-radius: 12px;
           box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
       '>
           <div style='font-size: 18px; font-weight: 700; color: #6EE7B7; margin-bottom: 0.5rem;'>
               Target: ≥95%
           </div>
           <div style='font-size: 13px; color: rgba(255, 255, 255, 0.7);'>
               Tỷ lệ thu hồi lãi
           </div>
           <div style='font-size: 24px; font-weight: 700; color: white; margin-top: 0.5rem;'>
               {kpis["Collection Rate (%)"]:.2f}%
           </div>
       </div>
       """, unsafe_allow_html=True)


   # ─────────────────────────────────────────────────────────────────
   # GAUGE 3: PORTFOLIO QUALITY (Vàng/Cam - Chất lượng danh mục)
   # ─────────────────────────────────────────────────────────────────


   with col_g3:
       fig_quality = create_gauge_chart(
           value=kpis["Portfolio Quality (%)"],
           title="⭐ Portfolio Quality",
           min_val=0,
           max_val=100,
           threshold_warning=85,
           threshold_good=95,
           reverse=False
       )
       st.plotly_chart(fig_quality, use_container_width=True)


       # ✅ Info box với gradient vàng/cam nổi bật
       st.markdown(f"""
       <div style='
           text-align: center;
           background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(251, 191, 36, 0.15));
           border: 1px solid rgba(245, 158, 11, 0.3);
           border-left: 4px solid #F59E0B;
           padding: 1rem;
           border-radius: 12px;
           box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
       '>
           <div style='font-size: 18px; font-weight: 700; color: #FCD34D; margin-bottom: 0.5rem;'>
               Target: ≥95%
           </div>
           <div style='font-size: 13px; color: rgba(255, 255, 255, 0.7);'>
               % Hợp đồng nhóm 1+2
           </div>
           <div style='font-size: 24px; font-weight: 700; color: white; margin-top: 0.5rem;'>
               {kpis["Portfolio Quality (%)"]:.2f}%
           </div>
       </div>
       """, unsafe_allow_html=True)


   # =================================================================
   # DONUT + BAR
   # =================================================================
   st.markdown("---")
   st.markdown("### 💰 Cấu trúc Tài sản")
   fig_structure = create_debt_structure_chart(df)
   st.plotly_chart(fig_structure, use_container_width=True)


   # =================================================================
   # HEATMAP
   # =================================================================
   st.markdown("---")
   st.markdown("### 🔥 Phân tích Rủi ro theo Chi nhánh")
   fig_heatmap = create_npl_heatmap(df)
   st.plotly_chart(fig_heatmap, use_container_width=True)


   st.markdown("---")
   col_insight1, col_insight2, col_insight3 = st.columns(3)


   with col_insight1:
       st.info("""
       **📊 Cách đọc Heatmap**


       **Màu sắc theo Nhóm:**
       - 🟢 **Nhóm 1:** Xanh (tốt) - càng đậm = càng nhiều HĐ chất lượng
       - 🟡 **Nhóm 2:** Vàng (trung bình)
       - 🔴 **Nhóm 3-5:** Đỏ đậm dần - càng đậm = càng nhiều NPL


       **Màu trắng:** Không có HĐ (0)
       """)


   with col_insight2:
       st.warning("""
       **⚠️ Chi nhánh cần chú ý**


       **Dấu hiệu rủi ro:**
       - Đỏ đậm ở Nhóm 3, 4, 5
       - Ít hoặc không có xanh ở Nhóm 1
       - Tỷ lệ NPL cao


       **Hành động:**
       - Kiểm tra ngay lập tức
       - Tăng cường giám sát
       - Xem xét chính sách tín dụng
       """)


   with col_insight3:
       st.success("""
       **✅ Chi nhánh xuất sắc**


       **Đặc điểm:**
       - 🟢 Xanh đậm ở Nhóm 1 (nhiều HĐ tốt)
       - 🟡 Vàng vừa phải ở Nhóm 2
       - ⚪ Trắng hoặc đỏ nhạt ở Nhóm 3-5 (ít/không NPL)


       **Kết quả:** Danh mục tín dụng chất lượng cao
       """)


   # =================================================================
   # STACKED BAR
   # =================================================================
   st.markdown("---")
   st.markdown("### ⏱️ Phân bổ Kỳ hạn Tín dụng")


   fig_term = create_term_distribution_chart(df)
   if fig_term:
       st.plotly_chart(fig_term, use_container_width=True)


       col_t1, col_t2, col_t3 = st.columns(3)
       with col_t1:
           st.info("""
           **📊 Ngắn hạn (≤12T)**
           - Xanh: Dễ thanh khoản
           - Rủi ro thấp
           - Thu hồi nhanh
           """)
       with col_t2:
           st.warning("""
           **⚠️ Trung hạn (1-5N)**
           - Xanh dương: Cân bằng
           - Rủi ro vừa phải
           - Thu nhập ổn định
           """)
       with col_t3:
           st.success("""
           **✅ Dài hạn (>5N)**
           - Tím: Thu nhập cao
           - Rủi ro cao hơn
           - Cần giám sát sát
           """)
   else:
       st.warning("Không có dữ liệu kỳ hạn để hiển thị")


   # =================================================================
   # PERFORMANCE TRENDS
   # =================================================================
   st.markdown("---")
   st.markdown("### 📈 Performance Trends")
   st.markdown("#### 📈 Giải ngân Momentum 2014-2024")


   fig_disbursement = create_disbursement_trend(df)
   if fig_disbursement:
       st.plotly_chart(fig_disbursement, use_container_width=True)


       if 'Nam_giai_ngan' in df.columns:
           df_temp = df[(df['Nam_giai_ngan'] >= 2014) & (df['Nam_giai_ngan'] <= 2024)]
           if len(df_temp) > 0:
               trend_data = df_temp.groupby('Nam_giai_ngan')['Goc_vay_giai_ngan'].sum().sort_index()
               if len(trend_data) > 1:
                   first_val = trend_data.iloc[0] / 1e9
                   last_val = trend_data.iloc[-1] / 1e9
                   num_years = trend_data.index[-1] - trend_data.index[0]


                   if first_val > 0 and num_years > 0:
                       cagr = ((last_val / first_val) ** (1 / num_years) - 1) * 100
                       if cagr > 10:
                           st.success(
                               f"💡 **Insight:** Tăng trưởng mạnh với CAGR {cagr:.1f}%/năm - Đạt mục tiêu mở rộng quy mô")
                       elif cagr > 5:
                           st.info(f"💡 **Insight:** Tăng trưởng ổn định với CAGR {cagr:.1f}%/năm - Duy trì momentum")
                       elif cagr > 0:
                           st.warning(f"💡 **Insight:** Tăng trưởng chậm ({cagr:.1f}%/năm) - Cần review chiến lược")
                       else:
                           st.error(f"⚠️ **Cảnh báo:** Giải ngân giảm ({cagr:.1f}%/năm) - Cần hành động ngay")
   else:
       st.warning("⚠️ Không có dữ liệu giải ngân để hiển thị")


   # =================================================================
   # STORYLINE
   # =================================================================
   st.markdown("---")
   st.markdown("#### 🔍 Phân tích Tổng quan")


   npl_status = "an toàn" if npl < 2 else "cần theo dõi" if npl < 3 else "rủi ro cao"
   collection_status = "xuất sắc" if collection >= 95 else "tốt" if collection >= 90 else "cần cải thiện"


   st.success(f"""
   **Quy mô:** Hệ thống quản lý **{kpis['Số lượng HĐ']:,} hợp đồng** với tổng dư nợ **{kpis['Tổng Dư nợ (Tỷ VNĐ)']:.2f} tỷ**.


   **Lợi nhuận:** Lợi suất TB **{kpis['Lợi suất TB (%)']:.2f}%**, thu nhập lãi dự kiến **{kpis['Thu nhập Lãi dự kiến (Tỷ VNĐ)']:.2f} tỷ**.


   **Rủi ro:** NPL **{kpis['Tỷ lệ NPL (%)']:.2f}%** ({npl_status}), Portfolio Quality **{kpis['Portfolio Quality (%)']:.1f}%**.


   **Hiệu quả:** Collection Rate **{kpis['Collection Rate (%)']:.2f}%** ({collection_status}).
   """)


   with st.expander("🧮 Công thức tính 3 Gauge Charts (100% từ dữ liệu thực)"):
       st.markdown("""
       ### ✅ TẤT CẢ ĐỀU TÍNH TỪ FILE .XLSX


       **1. NPL Ratio (Tỷ lệ Nợ xấu)**
       ```
       NPL = (Dư nợ nhóm 3 + nhóm 4 + nhóm 5) / Tổng dư nợ × 100%
       ```
       - Nguồn: Cột "Nhóm nợ KH" + "Gốc vay còn lại"
       - Target: <2% (An toàn)


       **2. Collection Rate (Tỷ lệ Thu hồi)**
       ```
       Collection Rate = (Lãi đã thu / Lãi phải thu) × 100%
       ```
       - Nguồn: "Lãi thông thường - Đã trả" / "Lãi thông thường - Phải trả"
       - Target: ≥95% (Xuất sắc)


       **3. Portfolio Quality (Chất lượng Danh mục)**
       ```
       Portfolio Quality = (Số HĐ nhóm 1 + nhóm 2) / Tổng HĐ × 100%
       ```
       - Nguồn: Count hợp đồng có "Nhóm nợ KH" = 1 hoặc 2
       - Target: ≥95% (Hầu hết HĐ đều tốt)


       ---


       ### 📊 Ý nghĩa màu sắc:
       - 🟢 **Xanh lá**: Đạt target, an toàn
       - 🟡 **Vàng**: Gần đạt, cần chú ý
       - 🔴 **Đỏ**: Dưới target, cần cải thiện
       """)




def main():
   st.set_page_config(page_title="Dashboard Tín dụng", layout="wide", page_icon="🏦")
   df = load_data()
   if not df.empty:
       show_overview_section(df)
   else:
       st.error("Không thể tải dữ liệu")




if __name__ == "__main__":
   main()




