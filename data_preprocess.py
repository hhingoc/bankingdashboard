# ==============================================
# File: data_preprocess.py
# Đọc, làm sạch, chuẩn hóa dữ liệu tín dụng
# ==============================================




import pandas as pd
import numpy as np
from datetime import datetime








# ❌ BỎ: import unidecode








def standardize_column_name(col):
   """Chuẩn hóa tên cột: bỏ dấu tiếng Việt thủ công"""
   col = str(col).strip()




   # ✅ BỎ DẤU TIẾNG VIỆT THỦ CÔNG
   vietnamese_map = {
       'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
       'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
       'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
       'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
       'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
       'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
       'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
       'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
       'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
       'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
       'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
       'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
       'đ': 'd', 'Đ': 'D'
   }




   for viet, ascii_char in vietnamese_map.items():
       col = col.replace(viet, ascii_char)
       col = col.replace(viet.upper(), ascii_char.upper())




   # Thay thế ký tự đặc biệt
   col = col.replace(" ", "_")
   col = col.replace("-", "_").replace("/", "_").replace("\\", "_")
   col = col.replace("(", "").replace(")", "")
   col = col.replace(".", "")




   # Chỉ giữ chữ cái, số và _
   col = "".join([c for c in col if c.isalnum() or c == "_"])




   # Loại bỏ _ liên tiếp và ở đầu/cuối
   while "__" in col:
       col = col.replace("__", "_")
   col = col.strip("_")




   return col








def load_and_clean_data(file_path: str) -> pd.DataFrame:
   """Đọc, làm sạch, chuẩn hóa dữ liệu tín dụng ngân hàng."""




   # B1. Đọc file CSV (hoặc Excel nếu bạn linh hoạt)
   if file_path.endswith(".csv"):
       raw_data = pd.read_csv(
           file_path,
           encoding="utf-8-sig",
           na_filter=False,
           header=1
       )
   else:
       raw_data = pd.read_excel(
           file_path,
           header=1
       )




   print(f"📂 File đã đọc: {file_path}")
   print(f"📏 Kích thước ban đầu: {raw_data.shape}")




   # B2. Chuẩn hóa tên cột (CSV đã có header sẵn)
   data = raw_data.copy()
   data.columns = [standardize_column_name(str(col)) for col in data.columns]
   data.replace(["NaN", "nan", "None", ""], np.nan, inplace=True)




   # B3. Drop cột trống hoàn toàn
   data = data.dropna(axis=1, how="all")




   # B4. Đổi tên cột nếu muốn viết gọn (optional)
   # Ví dụ: data = data.rename(columns={"Lai_Suat": "Interest_Rate"})




   # B5. Chuyển các cột ngày sang datetime
   for col in data.columns:
       if col.startswith("Ngay") or "ngay" in col.lower():
           data[col] = pd.to_datetime(data[col], errors="coerce")




   # B6. Chuyển các cột số sang float
   possible_numeric = [
       "Goc_vay_giai_ngan", "Goc_vay_con_lai_no_trong_han_no_qua_han",
       "Goc_qua_han", "Lai_Suat", "Lai_thong_thuong_Phai_tra",
       "Lai_thong_thuong_Da_tra", "Lai_phat_tren_goc_Phai_tra",
       "Lai_phat_tren_lai_Phai_tra"
   ]
   for col in possible_numeric:
       if col in data.columns:
           data[col] = (
               data[col].astype(str)
               .str.replace(",", "")
               .str.replace(" ", "")
               .str.replace("VND", "", case=False)
               .str.extract("([-+]?[0-9]*\\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", expand=False)
               .astype(float)
           )
           # B6.5: XỬ LÝ CỘT NGÀY GIẢI NGÂN (cho Area Chart & Vintage Analysis)
           # ================================================================




           # Tìm cột ngày giải ngân
       disbursement_date_col = None
       possible_cols = ['ngay_giai_ngan', 'disbursement_date', 'ngay_gn', 'Ngay_giai_ngan']




       for col in data.columns:
           col_lower = col.lower()
           if any(x in col_lower for x in possible_cols):
               disbursement_date_col = col
               break




       if disbursement_date_col:
           # Chuyển sang datetime
           data[disbursement_date_col] = pd.to_datetime(data[disbursement_date_col], errors='coerce')




           # Tạo cột phụ để phân tích
           data['Nam_giai_ngan'] = data[disbursement_date_col].dt.year
           data['Quy_giai_ngan'] = data[disbursement_date_col].dt.quarter
           data['Thang_giai_ngan'] = data[disbursement_date_col].dt.month
           data['Nam_Quy'] = (
                   data['Nam_giai_ngan'].astype(str) + '-Q' +
                   data['Quy_giai_ngan'].astype(str)
           )




           # Lọc dữ liệu hợp lệ (loại bỏ năm lỗi)
           data = data[
               (data['Nam_giai_ngan'] >= 2000) &
               (data['Nam_giai_ngan'] <= 2030)
               ]




           print(f"✅ Đã xử lý cột ngày giải ngân: {disbursement_date_col}")
           print(f"   - Khoảng thời gian: {int(data['Nam_giai_ngan'].min())} - {int(data['Nam_giai_ngan'].max())}")
           print(f"   - Số năm có dữ liệu: {data['Nam_giai_ngan'].nunique()}")
           print(f"   - Phân bổ theo năm:")
           year_dist = data['Nam_giai_ngan'].value_counts().sort_index()
           for year, count in year_dist.items():
               print(f"     {int(year)}: {count:,} HĐ")




       else:
           print("⚠️ CẢNH BÁO: Không tìm thấy cột ngày giải ngân!")
           print("   Các cột có sẵn:")
           for i, col in enumerate(data.columns[:20], 1):
               print(f"     {i:2d}. {col}")




           # Fallback: tạo cột giả (để tránh lỗi)
           print("\n   ➡️ Tạo dữ liệu giả (fallback)")
           data['Nam_giai_ngan'] = 2024
           data['Quy_giai_ngan'] = 1
           data['Thang_giai_ngan'] = 1
           data['Nam_Quy'] = '2024-Q1'




   # B7. Loại bỏ dòng lỗi/trống
   id_cols = [c for c in ["Ma_chi_nhanh", "Ma_khach_hang"] if c in data.columns]
   data = data.dropna(subset=id_cols, how="any")




   if "Goc_vay_con_lai_no_trong_han_no_qua_han" in data.columns:
       data = data[data["Goc_vay_con_lai_no_trong_han_no_qua_han"].fillna(0) >= 0]




   if "Trang_thai_khe_uoc" in data.columns:
       data["Trang_thai_khe_uoc"] = data["Trang_thai_khe_uoc"].fillna("").str.upper()
       valid_status = ["CUR", "ACT", "RUN"]
       data["Trang_thai_hieu_luc"] = data["Trang_thai_khe_uoc"].apply(lambda x: x in valid_status)




   # B8. Tính lãi dự báo cuối năm nếu đủ cột
   current_date = pd.to_datetime("2025-08-06")
   end_of_year = pd.to_datetime("2025-12-31")




   if "Ngay_het_han" not in data.columns and "Ngay_het_han_ban_dau_cua_khoan_vay_orig_mat_date" in data.columns:
       data["Ngay_het_han"] = data["Ngay_het_han_ban_dau_cua_khoan_vay_orig_mat_date"]

   if "Ngay_het_han" in data.columns:
       data["Ngay_het_han"] = pd.to_datetime(
           data["Ngay_het_han"],
           errors="coerce"
       )
   else:
       data["Ngay_het_han"] = pd.NaT



   if "Ngay_het_han_ban_dau_cua_khoan_vay_orig_mat_date" in data.columns:
       data["Ngay_du_bao_toi"] = data["Ngay_het_han_ban_dau_cua_khoan_vay_orig_mat_date"].apply(
           lambda x: min(x, end_of_year) if pd.notnull(x) else end_of_year
       )
   else:
       data["Ngay_du_bao_toi"] = end_of_year




   data["So_ngay_con_lai"] = (data["Ngay_du_bao_toi"] - current_date).dt.days.clip(lower=0)




   if "Lai_Suat" in data.columns:
       data["Lai_du_thu_cuoi_nam"] = (
               data["Goc_vay_con_lai_no_trong_han_no_qua_han"]
               * (data["Lai_Suat"].fillna(0) / 100 / 365)
               * data["So_ngay_con_lai"]
       )




   data = data.reset_index(drop=True)




   print("✅ Dữ liệu đã làm sạch thành công!")
   print(f"📊 Số dòng: {len(data)}")
   print("📋 Tên cột sau chuẩn hóa (10 cột đầu):")
   for i, col in enumerate(data.columns[:10], 1):
       print(f"   {i:2d}. {col}")




   return data








if __name__ == "__main__":
   FILE = "DSKH_BANK_ABCDEF.csv"
   df = load_and_clean_data(FILE)
   print("\n" + "=" * 80)
   print("PREVIEW DỮ LIỆU (5 dòng đầu):")
   print("=" * 80)
   print(df.head().T)




   # ✅ Xuất ra CSV để dùng cho dashboard
   csv_path = FILE.replace(".xlsx", ".csv")
   df.to_csv(csv_path, index=False, encoding="utf-8-sig")
   print(f"\n💾 Đã lưu file sạch: {csv_path}")












