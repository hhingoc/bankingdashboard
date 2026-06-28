# ==============================================
# File: dashboard_filters.py (FIXED)
# ==============================================


import pandas as pd




def apply_filters(
       df,
       vung_list, khu_vuc_list, branch_list,
       product_list, term_list,
       year_list, quarter_list, risk_list
):
   """Apply các filter đã chọn từ sidebar vào dataframe"""


   filtered = df.copy()


   # Filter Địa lý
   if vung_list and 'Vung' in df.columns:
       filtered = filtered[filtered['Vung'].isin(vung_list)]


   if khu_vuc_list and 'Khu_vuc' in df.columns:
       filtered = filtered[filtered['Khu_vuc'].isin(khu_vuc_list)]


   if branch_list and 'Ma_chi_nhanh' in df.columns:
       filtered = filtered[filtered['Ma_chi_nhanh'].isin(branch_list)]


   # Filter Sản phẩm
   if product_list and 'Sub_productTen_san_pham' in df.columns:
       filtered = filtered[filtered['Sub_productTen_san_pham'].isin(product_list)]


   if term_list and 'Phan_theo_ky_han_NHTDDH' in df.columns:
       filtered = filtered[filtered['Phan_theo_ky_han_NHTDDH'].isin(term_list)]


   # Filter Thời gian
   if year_list and 'Year' in df.columns:
       filtered = filtered[filtered['Year'].isin(year_list)]


   if quarter_list and 'Quarter' in df.columns:
       filtered = filtered[filtered['Quarter'].isin(quarter_list)]


   # ✅ FIX: Filter Rủi ro - Xử lý đúng kiểu dữ liệu
   if risk_list and 'Nhom_no_KH' in df.columns:
       # Convert risk_list về int để match với df['Nhom_no_KH']
       risk_list_int = [int(x) for x in risk_list]
       filtered = filtered[filtered['Nhom_no_KH'].isin(risk_list_int)]


   return filtered




