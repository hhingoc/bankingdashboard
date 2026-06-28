# ==============================================
# File: dashboard_operational.py
# Module: Tầng 3 - Operational Dashboard
# ==============================================


import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime




def show_operational_dashboard(df):
   """
   ⚙️ Tầng 3: Operational Dashboard
   4 Modules: Chi nhánh | Khách hàng | Hợp đồng | Export
   """


   st.header("⚙️ Tầng 3: Operational Dashboard - Vận hành Chi tiết")
   st.caption(f"📊 Quản lý {len(df):,} hợp đồng | Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


   # =====================================================================
   # TABS NGANG - 4 MODULES
   # =====================================================================
   tab1, tab2, tab3, tab4 = st.tabs([
       "🏢 1. CHI NHÁNH DRILL-DOWN",
       "👤 2. KHÁCH HÀNG INDIVIDUAL",
       "📋 3. HỢP ĐỒNG TRACKING",
       "📊 4. EXPORT & REPORTING"
   ])


   with tab1:
       show_branch_drilldown(df)


   with tab2:
       show_customer_profile(df)


   with tab3:
       show_contract_tracking(df)


   with tab4:
       show_export_reporting(df)




# ═════════════════════════════════════════════════════════════════════
# MODULE 1: CHI NHÁNH DRILL-DOWN (CẢI TIẾN - HIERARCHY)
# ═════════════════════════════════════════════════════════════════════


def show_branch_drilldown(df):
   """Module 1: Drill-down Chi nhánh (Cha → Con)"""


   st.markdown("### 🏢 Module 1: Chi nhánh Drill-Down (Hierarchical)")
   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # KIỂM TRA CÓ CỘT CHI NHÁNH CHA
   # ─────────────────────────────────────────────────────────────────


   # Tìm cột Chi nhánh Cha
   parent_branch_col = None
   for col in df.columns:
       if any(x in str(col).lower() for x in ['chi_nhanh_cha', 'ma_chi_nhanh_cha', 'parent_branch']):
           parent_branch_col = col
           break


   # ─────────────────────────────────────────────────────────────────
   # HIERARCHICAL SELECTION: CHA → CON
   # ─────────────────────────────────────────────────────────────────


   if parent_branch_col and parent_branch_col in df.columns:
       st.success("✅ Phát hiện cấu trúc Chi nhánh Cha-Con")


       # BƯỚC 1: Chọn Chi nhánh Cha
       all_parent_branches = sorted(df[parent_branch_col].dropna().unique())


       col_parent, col_child = st.columns(2)


       with col_parent:
           selected_parent = st.selectbox(
               "🏢 Bước 1: Chọn Chi nhánh Cha",
               options=all_parent_branches,
               index=0,
               key="parent_branch_select"
           )


       # BƯỚC 2: Filter Chi nhánh Con theo Cha đã chọn
       df_parent_filtered = df[df[parent_branch_col] == selected_parent]
       all_child_branches = sorted(df_parent_filtered['Ma_chi_nhanh'].dropna().unique())


       with col_child:
           if len(all_child_branches) > 0:
               selected_branch = st.selectbox(
                   "🏪 Bước 2: Chọn Chi nhánh Con",
                   options=all_child_branches,
                   index=0,
                   key="child_branch_select"
               )
           else:
               st.warning("⚠️ Không có Chi nhánh Con")
               selected_branch = None


       # Hiển thị breadcrumb
       st.markdown("---")
       st.markdown(f"📍 **Đường dẫn:** {selected_parent} → **{selected_branch}**")


   else:
       # Fallback: Không có cột Cha, chọn trực tiếp Chi nhánh
       st.info("ℹ️ Không phát hiện cấu trúc Chi nhánh Cha-Con, hiển thị danh sách phẳng")


       all_branches = sorted(df['Ma_chi_nhanh'].dropna().unique())


       selected_branch = st.selectbox(
           "🔍 Chọn Chi nhánh:",
           options=all_branches,
           index=0
       )


       selected_parent = None


   # ─────────────────────────────────────────────────────────────────
   # FILTER DATA THEO BRANCH ĐÃ CHỌN
   # ─────────────────────────────────────────────────────────────────


   if selected_branch is None:
       st.error("⚠️ Vui lòng chọn Chi nhánh")
       return


   df_branch = df[df['Ma_chi_nhanh'] == selected_branch].copy()


   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # ═══════════════════════════════════════════════════════════════
   # KPI CHI NHÁNH - ORANGE-AMBER GRADIENT (OPERATIONAL)
   # ═══════════════════════════════════════════════════════════════
   st.markdown(f"#### 📊 KPI Chi nhánh: **{selected_branch}**")


   # DARK THEME COLORS
   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   total_debt = df_branch['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum()
   total_income = df_branch['Lai_thong_thuong_Da_tra'].sum()
   total_contracts = len(df_branch)


   # NPL
   df_branch['Nhom_no_KH'] = pd.to_numeric(df_branch['Nhom_no_KH'], errors='coerce')
   npl_debt = df_branch[df_branch['Nhom_no_KH'].isin([3, 4, 5])]['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum()
   npl_ratio = (npl_debt / total_debt * 100) if total_debt > 0 else 0


   # ─── ROW 1: KPIs Chính với ORANGE-AMBER GRADIENT ───
   col1, col2, col3, col4 = st.columns(4)


   # Card 1: Dư nợ (Orange gradient)
   with col1:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #f97316, #ea580c);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💰 Dư nợ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_debt / 1e9:.2f}T</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Chi nhánh {selected_branch}</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 2: Thu lãi (Amber gradient)
   with col2:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #fbbf24, #f59e0b);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(251, 191, 36, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💸 Thu lãi</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_income / 1e9:.2f}T</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Đã thu</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 3: Số HĐ (Deep Orange gradient)
   with col3:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #fb923c, #f97316);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(251, 146, 60, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📋 Số HĐ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_contracts:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Hợp đồng</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 4: NPL (Red/Green conditional)
   npl_color = '#ef4444' if npl_ratio >= 3 else '#10b981'
   npl_color_dark = '#dc2626' if npl_ratio >= 3 else '#059669'
   npl_status = 'High ⚠️' if npl_ratio >= 3 else 'OK ✅'


   with col4:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, {npl_color}, {npl_color_dark});
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>⚠️ NPL</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{npl_ratio:.2f}%</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>{npl_status}</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # ROW 2: SO SÁNH VỚI PARENT - ORANGE-AMBER GRADIENT
   # ═══════════════════════════════════════════════════════════════
   if selected_parent:
       st.markdown("---")
       st.markdown(f"#### 📊 So sánh với Chi nhánh Cha: **{selected_parent}**")


       DARK_COLORS = {
           'text_white': '#f8fafc',
           'text_light': '#94a3b8',
           'grid': '#334155',
           'bg_card': '#0f172a'
       }


       # Tính KPI của Parent
       df_parent = df[df[parent_branch_col] == selected_parent]
       parent_total_debt = df_parent['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum()
       parent_contracts = len(df_parent)


       # % đóng góp
       contribution_debt = (total_debt / parent_total_debt * 100) if parent_total_debt > 0 else 0
       contribution_contracts = (total_contracts / parent_contracts * 100) if parent_contracts > 0 else 0


       # Ranking
       siblings = df[df[parent_branch_col] == selected_parent].groupby('Ma_chi_nhanh')[
           'Goc_vay_con_lai_no_trong_han_no_qua_han'].sum().sort_values(ascending=False)
       rank = list(siblings.index).index(selected_branch) + 1 if selected_branch in siblings.index else 0


       col_comp1, col_comp2, col_comp3 = st.columns(3)


       # Card 1: Đóng góp Dư nợ (Orange gradient)
       with col_comp1:
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(234, 88, 12, 0.2));
               border: 2px solid #f97316;
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(249, 115, 22, 0.2);
           '>
               <div style='color: {DARK_COLORS['text_light']}; font-size: 13px; margin-bottom: 0.5rem;'>📊 Đóng góp Dư nợ</div>
               <div style='color: #f97316; font-size: 28px; font-weight: 800;'>{contribution_debt:.1f}%</div>
               <div style='color: {DARK_COLORS['text_light']}; font-size: 11px; margin-top: 0.5rem;'>
                   So với {parent_total_debt / 1e9:.2f}T (Parent)
               </div>
           </div>
           """, unsafe_allow_html=True)


       # Card 2: Đóng góp Số HĐ (Amber gradient)
       with col_comp2:
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.2));
               border: 2px solid #fbbf24;
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(251, 191, 36, 0.2);
           '>
               <div style='color: {DARK_COLORS['text_light']}; font-size: 13px; margin-bottom: 0.5rem;'>📊 Đóng góp Số HĐ</div>
               <div style='color: #fbbf24; font-size: 28px; font-weight: 800;'>{contribution_contracts:.1f}%</div>
               <div style='color: {DARK_COLORS['text_light']}; font-size: 11px; margin-top: 0.5rem;'>
                   So với {parent_contracts:,} HĐ (Parent)
               </div>
           </div>
           """, unsafe_allow_html=True)


       # Card 3: Ranking (Gold gradient)
       with col_comp3:
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(249, 115, 22, 0.2));
               border: 2px solid #fb923c;
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(251, 146, 60, 0.2);
           '>
               <div style='color: {DARK_COLORS['text_light']}; font-size: 13px; margin-bottom: 0.5rem;'>🏆 Xếp hạng</div>
               <div style='color: #fb923c; font-size: 28px; font-weight: 800;'>#{rank}/{len(siblings)}</div>
               <div style='color: {DARK_COLORS['text_light']}; font-size: 11px; margin-top: 0.5rem;'>
                   Trong {len(siblings)} CN con
               </div>
           </div>
           """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # DANH SÁCH HĐ CHI TIẾT - DARK THEME TABLE
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📋 Danh sách Hợp đồng Chi tiết")
   st.caption(f"📍 {len(df_branch):,} hợp đồng tại chi nhánh **{selected_branch}**")


   # Chọn columns hiển thị
   display_cols = [
       'Ma_khach_hang',
       'Nhom_no_KH',
       'Goc_vay_con_lai_no_trong_han_no_qua_han',
       'Goc_qua_han',
       'Lai_Suat',
       'Lai_thong_thuong_Da_tra'
   ]


   # Rename
   df_display = df_branch[display_cols].copy()
   df_display.columns = ['Mã KH', 'Nhóm nợ', 'Dư nợ (VNĐ)', 'Gốc quá hạn (VNĐ)', 'Lãi suất (%)', 'Lãi đã thu (VNĐ)']


   # Format
   df_display['Dư nợ (Tỷ)'] = (df_display['Dư nợ (VNĐ)'] / 1e9).round(3)
   df_display['Gốc QH (Tr)'] = (df_display['Gốc quá hạn (VNĐ)'] / 1e6).round(1)
   df_display['Lãi thu (Tr)'] = (df_display['Lãi đã thu (VNĐ)'] / 1e6).round(1)


   # Sort by NPL risk
   df_display = df_display.sort_values('Nhóm nợ', ascending=False)


   # Display with conditional formatting
   st.dataframe(
       df_display[['Mã KH', 'Nhóm nợ', 'Dư nợ (Tỷ)', 'Gốc QH (Tr)', 'Lãi suất (%)', 'Lãi thu (Tr)']].style
       .background_gradient(cmap='Oranges', subset=['Nhóm nợ'])  # Orange gradient for NPL
       .background_gradient(cmap='YlOrRd', subset=['Gốc QH (Tr)'])  # Yellow-Orange-Red for overdue
       .format({
           'Dư nợ (Tỷ)': '{:.3f}',
           'Gốc QH (Tr)': '{:.1f}',
           'Lãi suất (%)': '{:.2f}',
           'Lãi thu (Tr)': '{:.1f}'
       }),
       use_container_width=True,
       height=400
   )


   # Download button with Orange theme
   col_download, col_summary = st.columns([1, 3])


   with col_download:
       csv_data = df_display.to_csv(index=False).encode('utf-8')
       st.download_button(
           label="⬇️ Download CSV",
           data=csv_data,
           file_name=f"HD_{selected_branch}_{datetime.now().strftime('%Y%m%d')}.csv",
           mime='text/csv',
           use_container_width=True
       )


   with col_summary:
       # Summary insight box
       high_risk_count = len(df_display[df_display['Nhóm nợ'] >= 3])
       high_risk_pct = (high_risk_count / len(df_display) * 100) if len(df_display) > 0 else 0


       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
           border-left: 5px solid #f97316;
           border-radius: 12px;
           padding: 1rem;
           box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
       '>
           <div style='color: #f97316; font-size: 14px; font-weight: 700; margin-bottom: 0.5rem;'>
               📊 Tóm tắt:
           </div>
           <div style='color: {DARK_COLORS['text_white']}; font-size: 13px; line-height: 1.8;'>
               • <b style='color: #fbbf24;'>Tổng HĐ:</b> {len(df_display):,} hợp đồng<br>
               • <b style='color: #fb923c;'>Nợ xấu:</b> {high_risk_count} HĐ (<b>{high_risk_pct:.1f}%</b>)<br>
               • <b style='color: #f97316;'>Cảnh báo:</b> {'⚠️ Cần xem xét' if high_risk_pct > 5 else '✅ Ổn định'}
           </div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # ACTION ITEMS - RED-ORANGE-YELLOW ALERT SYSTEM
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### ⚡ Action Items - Cần xử lý ngay")
   st.caption("📍 Tự động phát hiện các vấn đề cần ưu tiên")


   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   # High NPL contracts
   high_risk = df_branch[df_branch['Nhom_no_KH'].isin([4, 5])]


   # Overdue contracts
   overdue = df_branch[df_branch['Goc_qua_han'] > 0]


   col_alert1, col_alert2, col_alert3 = st.columns(3)


   # Alert 1: High Risk (Red)
   with col_alert1:
       if len(high_risk) > 0:
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, #ef4444, #dc2626);
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
           '>
               <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>🚨 High Risk</div>
               <div style='color: white; font-size: 28px; font-weight: 800;'>{len(high_risk)} HĐ</div>
               <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.5rem;'>Nhóm 4-5 cần xử lý</div>
           </div>
           """, unsafe_allow_html=True)
       else:
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, #10b981, #059669);
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
           '>
               <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>✅ Status</div>
               <div style='color: white; font-size: 28px; font-weight: 800;'>OK</div>
               <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.5rem;'>Không có HĐ High Risk</div>
           </div>
           """, unsafe_allow_html=True)


   # Alert 2: Overdue (Orange/Yellow)
   with col_alert2:
       if len(overdue) > 0:
           total_overdue = overdue['Goc_qua_han'].sum()
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, #f97316, #ea580c);
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
           '>
               <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>⚠️ Gốc quá hạn</div>
               <div style='color: white; font-size: 28px; font-weight: 800;'>{len(overdue)} HĐ</div>
               <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.5rem;'>Tổng: {total_overdue / 1e9:.2f}T</div>
           </div>
           """, unsafe_allow_html=True)
       else:
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, #10b981, #059669);
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
           '>
               <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>✅ Status</div>
               <div style='color: white; font-size: 28px; font-weight: 800;'>OK</div>
               <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.5rem;'>Không có Gốc quá hạn</div>
           </div>
           """, unsafe_allow_html=True)


   # Alert 3: NPL Ratio (Red/Yellow/Green)
   with col_alert3:
       if npl_ratio > 5:
           alert_color = '#ef4444'
           alert_color_dark = '#dc2626'
           alert_icon = '🔴'
           alert_text = 'NPL > 5% - Cần review ngay!'
       elif npl_ratio > 3:
           alert_color = '#fbbf24'
           alert_color_dark = '#f59e0b'
           alert_icon = '🟡'
           alert_text = 'NPL > 3% - Theo dõi sát'
       else:
           alert_color = '#10b981'
           alert_color_dark = '#059669'
           alert_icon = '✅'
           alert_text = 'NPL trong kiểm soát'


       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, {alert_color}, {alert_color_dark});
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>{alert_icon} NPL Status</div>
           <div style='color: white; font-size: 28px; font-weight: 800;'>{npl_ratio:.2f}%</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.5rem;'>{alert_text}</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # CHI TIẾT ACTION ITEMS - EXPANDABLE
   # ═══════════════════════════════════════════════════════════════


   if len(high_risk) > 0:
       with st.expander(f"🔍 Chi tiết **{len(high_risk)} HĐ High Risk** (Nhóm 4-5)", expanded=False):
           high_risk_display = high_risk[
               ['Ma_khach_hang', 'Nhom_no_KH', 'Goc_vay_con_lai_no_trong_han_no_qua_han', 'Goc_qua_han']
           ].copy()
           high_risk_display.columns = ['Mã KH', 'Nhóm nợ', 'Dư nợ (VNĐ)', 'Gốc quá hạn (VNĐ)']
           high_risk_display['Dư nợ (Tỷ)'] = (high_risk_display['Dư nợ (VNĐ)'] / 1e9).round(3)
           high_risk_display['Gốc QH (Tr)'] = (high_risk_display['Gốc quá hạn (VNĐ)'] / 1e6).round(1)


           # Sort by risk level
           high_risk_display = high_risk_display.sort_values('Nhóm nợ', ascending=False)


           st.dataframe(
               high_risk_display[['Mã KH', 'Nhóm nợ', 'Dư nợ (Tỷ)', 'Gốc QH (Tr)']].style
               .background_gradient(cmap='Reds', subset=['Nhóm nợ'])
               .background_gradient(cmap='OrRd', subset=['Gốc QH (Tr)'])
               .format({
                   'Dư nợ (Tỷ)': '{:.3f}',
                   'Gốc QH (Tr)': '{:.1f}'
               }),
               use_container_width=True,
               height=300
           )


           # Action recommendation
           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
               border-left: 5px solid #ef4444;
               border-radius: 12px;
               padding: 1rem;
               margin-top: 1rem;
               box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
           '>
               <div style='color: #ef4444; font-size: 14px; font-weight: 700; margin-bottom: 0.5rem;'>
                   🚨 Khuyến nghị hành động:
               </div>
               <div style='color: {DARK_COLORS['text_white']}; font-size: 13px; line-height: 1.8;'>
                   • <b style='color: #fbbf24;'>Nhóm 5:</b> Xử lý ngay, xem xét khởi kiện<br>
                   • <b style='color: #fb923c;'>Nhóm 4:</b> Đàm phán tái cơ cấu, theo dõi sát<br>
                   • <b style='color: #f97316;'>Báo cáo:</b> Gửi Ban Giám đốc trong 24h
               </div>
           </div>
           """, unsafe_allow_html=True)


   if len(overdue) > 0:
       with st.expander(f"⚠️ Chi tiết **{len(overdue)} HĐ** có Gốc quá hạn", expanded=False):
           overdue_display = overdue[
               ['Ma_khach_hang', 'Nhom_no_KH', 'Goc_qua_han', 'Goc_vay_con_lai_no_trong_han_no_qua_han']
           ].copy()
           overdue_display.columns = ['Mã KH', 'Nhóm nợ', 'Gốc QH (VNĐ)', 'Dư nợ (VNĐ)']
           overdue_display['Gốc QH (Tr)'] = (overdue_display['Gốc QH (VNĐ)'] / 1e6).round(1)
           overdue_display['Dư nợ (Tỷ)'] = (overdue_display['Dư nợ (VNĐ)'] / 1e9).round(3)


           # Sort by overdue amount
           overdue_display = overdue_display.sort_values('Gốc QH (VNĐ)', ascending=False)


           st.dataframe(
               overdue_display[['Mã KH', 'Nhóm nợ', 'Gốc QH (Tr)', 'Dư nợ (Tỷ)']].style
               .background_gradient(cmap='Oranges', subset=['Gốc QH (Tr)'])
               .format({
                   'Gốc QH (Tr)': '{:.1f}',
                   'Dư nợ (Tỷ)': '{:.3f}'
               }),
               use_container_width=True,
               height=300
           )




# ═════════════════════════════════════════════════════════════════════
# MODULE 2: KHÁCH HÀNG INDIVIDUAL - 360° VIEW
# ═════════════════════════════════════════════════════════════════════


def show_customer_profile(df):
   """Module 2: Profile Khách hàng với Cyan-Blue theme"""


   st.markdown("### 👤 Module 2: Khách hàng Individual - 360° View")
   st.markdown("---")


   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   # ═══════════════════════════════════════════════════════════════
   # SEARCH KHÁCH HÀNG
   # ═══════════════════════════════════════════════════════════════
   all_customers = sorted(df['Ma_khach_hang'].dropna().unique())


   col_search, col_info = st.columns([2, 1])


   with col_search:
       selected_customer = st.selectbox(
           "🔍 Tìm kiếm Khách hàng:",
           options=all_customers,
           index=0,
           key="customer_search"
       )


   with col_info:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.2));
           border: 2px solid #06b6d4;
           border-radius: 12px;
           padding: 1rem;
           margin-top: 1.7rem;
       '>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 12px;'>📊 Tổng KH trong hệ thống</div>
           <div style='color: #06b6d4; font-size: 22px; font-weight: 800;'>{len(all_customers):,}</div>
       </div>
       """, unsafe_allow_html=True)


   # Filter
   df_customer = df[df['Ma_khach_hang'] == selected_customer].copy()


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # CUSTOMER PROFILE - CYAN-BLUE GRADIENT
   # ═══════════════════════════════════════════════════════════════
   st.markdown(f"#### 📋 Profile: Khách hàng **{selected_customer}**")


   total_debt_cust = df_customer['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum()
   total_contracts_cust = len(df_customer)
   avg_rate = df_customer['Lai_Suat'].mean()


   # NPL status của KH
   df_customer['Nhom_no_KH'] = pd.to_numeric(df_customer['Nhom_no_KH'], errors='coerce')
   has_npl = (df_customer['Nhom_no_KH'] >= 3).any()


   col1, col2, col3, col4 = st.columns(4)


   # Card 1: Tổng Dư nợ (Cyan gradient)
   with col1:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #06b6d4, #0891b2);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💰 Tổng Dư nợ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_debt_cust / 1e9:.3f}T</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Across {total_contracts_cust} HĐ</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 2: Số HĐ (Sky Blue gradient)
   with col2:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #0ea5e9, #0284c7);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📋 Số HĐ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_contracts_cust}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Hợp đồng</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 3: Lãi suất TB (Blue gradient)
   with col3:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #3b82f6, #2563eb);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📈 Lãi suất TB</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{avg_rate:.2f}%</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Per annum</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 4: Risk Status (Conditional)
   risk_color = '#ef4444' if has_npl else '#10b981'
   risk_color_dark = '#dc2626' if has_npl else '#059669'
   risk_text = '⚠️ Có NPL' if has_npl else '✅ Healthy'


   with col4:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, {risk_color}, {risk_color_dark});
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>🎯 Risk Status</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{risk_text}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Credit quality</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # DANH SÁCH HỢP ĐỒNG CỦA KH - STYLED TABLE
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📊 Danh sách Hợp đồng")
   st.caption(f"📍 Chi tiết {total_contracts_cust} hợp đồng của khách hàng **{selected_customer}**")


   display_cols_cust = [
       'Ma_chi_nhanh',
       'Nhom_no_KH',
       'Goc_vay_con_lai_no_trong_han_no_qua_han',
       'Lai_Suat',
       'Lai_thong_thuong_Da_tra'
   ]


   df_display_cust = df_customer[display_cols_cust].copy()
   df_display_cust.columns = ['Chi nhánh', 'Nhóm nợ', 'Dư nợ (VNĐ)', 'Lãi suất (%)', 'Lãi đã thu (VNĐ)']


   df_display_cust['Dư nợ (Tỷ)'] = (df_display_cust['Dư nợ (VNĐ)'] / 1e9).round(3)
   df_display_cust['Lãi thu (Tr)'] = (df_display_cust['Lãi đã thu (VNĐ)'] / 1e6).round(1)


   # Sort by NPL risk
   df_display_cust = df_display_cust.sort_values('Nhóm nợ', ascending=False)


   st.dataframe(
       df_display_cust[['Chi nhánh', 'Nhóm nợ', 'Dư nợ (Tỷ)', 'Lãi suất (%)', 'Lãi thu (Tr)']].style
       .background_gradient(cmap='Blues', subset=['Dư nợ (Tỷ)'])  # Cyan-Blue for amounts
       .background_gradient(cmap='RdYlGn_r', subset=['Nhóm nợ'])  # Red-Yellow-Green for risk
       .format({
           'Dư nợ (Tỷ)': '{:.3f}',
           'Lãi suất (%)': '{:.2f}',
           'Lãi thu (Tr)': '{:.1f}'
       }),
       use_container_width=True,
       height=350
   )


   # Customer Summary
   col_summary, col_action = st.columns([2, 1])


   with col_summary:
       total_income_cust = df_customer['Lai_thong_thuong_Da_tra'].sum()
       branches_count = df_customer['Ma_chi_nhanh'].nunique()


       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
           border-left: 5px solid #06b6d4;
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
       '>
           <div style='color: #06b6d4; font-size: 14px; font-weight: 700; margin-bottom: 0.5rem;'>
               📊 Tóm tắt Khách hàng:
           </div>
           <div style='color: {DARK_COLORS['text_white']}; font-size: 13px; line-height: 1.8;'>
               • <b style='color: #0ea5e9;'>Tổng lãi đã thu:</b> {total_income_cust / 1e9:.3f} tỷ VNĐ<br>
               • <b style='color: #3b82f6;'>Số chi nhánh:</b> {branches_count} chi nhánh<br>
               • <b style='color: #06b6d4;'>Đánh giá:</b> {'⚠️ Cần theo dõi' if has_npl else '✅ Khách hàng tốt'}
           </div>
       </div>
       """, unsafe_allow_html=True)


   with col_action:
       # Download button
       csv_data_cust = df_display_cust.to_csv(index=False).encode('utf-8')
       st.download_button(
           label="⬇️ Download Profile",
           data=csv_data_cust,
           file_name=f"Customer_{selected_customer}_{datetime.now().strftime('%Y%m%d')}.csv",
           mime='text/csv',
           use_container_width=True
       )


   st.markdown("---")


   # ─────────────────────────────────────────────────────────────────
   # ═══════════════════════════════════════════════════════════════
   # RISK ASSESSMENT - GRADIENT ALERT SYSTEM
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### ⚠️ Risk Assessment")
   st.caption("📍 Đánh giá rủi ro tổng thể của khách hàng")


   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   df_customer['Nhom_no_KH'] = pd.to_numeric(df_customer['Nhom_no_KH'], errors='coerce')
   worst_group = df_customer['Nhom_no_KH'].max()


   # Calculate risk metrics
   npl_contracts = len(df_customer[df_customer['Nhom_no_KH'] >= 3])
   total_contracts = len(df_customer)
   npl_ratio = (npl_contracts / total_contracts * 100) if total_contracts > 0 else 0


   # Risk score (1-5, where 5 is worst)
   risk_score = int(worst_group) if pd.notna(worst_group) else 1


   # Risk color mapping
   risk_configs = {
       5: {
           'color': '#dc2626',
           'color_dark': '#991b1b',
           'icon': '🔴',
           'status': 'CRITICAL',
           'message': 'Khách hàng có HĐ Nhóm 5 - Cần xử lý ngay!',
           'action': 'Khởi kiện, xử lý tài sản đảm bảo'
       },
       4: {
           'color': '#ef4444',
           'color_dark': '#dc2626',
           'icon': '🚨',
           'status': 'HIGH RISK',
           'message': 'Khách hàng có HĐ Nhóm 4 - High Risk!',
           'action': 'Tái cơ cấu, theo dõi sát'
       },
       3: {
           'color': '#f59e0b',
           'color_dark': '#d97706',
           'icon': '⚠️',
           'status': 'MEDIUM RISK',
           'message': 'Khách hàng có HĐ Nhóm 3 - Cần theo dõi',
           'action': 'Nhắc nhở, làm việc trực tiếp'
       },
       2: {
           'color': '#3b82f6',
           'color_dark': '#2563eb',
           'icon': '🔵',
           'status': 'LOW RISK',
           'message': 'Khách hàng có HĐ Nhóm 2 - Ổn định',
           'action': 'Theo dõi định kỳ'
       },
       1: {
           'color': '#10b981',
           'color_dark': '#059669',
           'icon': '✅',
           'status': 'EXCELLENT',
           'message': 'Khách hàng chất lượng tốt',
           'action': 'Duy trì quan hệ'
       }
   }


   config = risk_configs.get(risk_score, risk_configs[1])


   # Main risk card
   st.markdown(f"""
   <div style='
       background: linear-gradient(135deg, {config['color']}, {config['color_dark']});
       border-radius: 12px;
       padding: 1.5rem;
       box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
       margin-bottom: 1rem;
   '>
       <div style='display: flex; justify-content: space-between; align-items: center;'>
           <div>
               <div style='color: rgba(255,255,255,0.9); font-size: 14px; margin-bottom: 0.5rem;'>
                   {config['icon']} Risk Status
               </div>
               <div style='color: white; font-size: 32px; font-weight: 800; margin-bottom: 0.5rem;'>
                   {config['status']}
               </div>
               <div style='color: rgba(255,255,255,0.85); font-size: 14px;'>
                   {config['message']}
               </div>
           </div>
           <div style='text-align: right;'>
               <div style='color: rgba(255,255,255,0.7); font-size: 13px; margin-bottom: 0.3rem;'>
                   Risk Score
               </div>
               <div style='color: white; font-size: 48px; font-weight: 800;'>
                   {risk_score}
               </div>
               <div style='color: rgba(255,255,255,0.7); font-size: 11px;'>
                   / 5
               </div>
           </div>
       </div>
   </div>
   """, unsafe_allow_html=True)


   # Risk details row
   col_risk1, col_risk2, col_risk3 = st.columns(3)


   with col_risk1:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
           border: 2px solid {config['color']};
           border-radius: 12px;
           padding: 1rem;
           box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
       '>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 12px; margin-bottom: 0.5rem;'>
               📊 NPL Contracts
           </div>
           <div style='color: {config['color']}; font-size: 24px; font-weight: 800;'>
               {npl_contracts}/{total_contracts}
           </div>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 11px; margin-top: 0.3rem;'>
               {npl_ratio:.1f}% NPL ratio
           </div>
       </div>
       """, unsafe_allow_html=True)


   with col_risk2:
       overdue_count = len(df_customer[df_customer['Goc_qua_han'] > 0])
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
           border: 2px solid #f59e0b;
           border-radius: 12px;
           padding: 1rem;
           box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
       '>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 12px; margin-bottom: 0.5rem;'>
               ⏰ Overdue
           </div>
           <div style='color: #f59e0b; font-size: 24px; font-weight: 800;'>
               {overdue_count}
           </div>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 11px; margin-top: 0.3rem;'>
               Contracts with overdue
           </div>
       </div>
       """, unsafe_allow_html=True)


   with col_risk3:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(8, 145, 178, 0.2));
           border: 2px solid #06b6d4;
           border-radius: 12px;
           padding: 1rem;
           box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
       '>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 12px; margin-bottom: 0.5rem;'>
               🎯 Action Required
           </div>
           <div style='color: #06b6d4; font-size: 24px; font-weight: 800;'>
               {config['action'][:15]}
           </div>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 11px; margin-top: 0.3rem;'>
               Next steps
           </div>
       </div>
       """, unsafe_allow_html=True)


   # Recommendation box
   st.markdown(f"""
   <div style='
       background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
       border-left: 5px solid {config['color']};
       border-radius: 12px;
       padding: 1.2rem;
       margin-top: 1rem;
       box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
   '>
       <div style='color: {config['color']}; font-size: 14px; font-weight: 700; margin-bottom: 0.5rem;'>
           💡 Khuyến nghị:
       </div>
       <div style='color: {DARK_COLORS['text_white']}; font-size: 13px; line-height: 1.8;'>
           • <b style='color: #06b6d4;'>Hành động:</b> {config['action']}<br>
           • <b style='color: #0ea5e9;'>Ưu tiên:</b> {'CAO' if risk_score >= 4 else 'TRUNG BÌNH' if risk_score == 3 else 'THẤP'}<br>
           • <b style='color: #3b82f6;'>Tần suất review:</b> {'Hàng ngày' if risk_score >= 4 else 'Hàng tuần' if risk_score == 3 else 'Hàng tháng'}
       </div>
   </div>
   """, unsafe_allow_html=True)


   st.markdown("---")




# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# MODULE 3: HỢP ĐỒNG TRACKING - PURPLE-MAGENTA THEME
# ═════════════════════════════════════════════════════════════════════


def show_contract_tracking(df):
   """Module 3: Tracking Hợp đồng với Purple-Magenta theme"""


   st.markdown("### 📋 Module 3: Hợp đồng Tracking")
   st.markdown("---")


   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   # Development status banner
   st.markdown(f"""
   <div style='
       background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(192, 132, 252, 0.2));
       border: 2px solid #a855f7;
       border-radius: 12px;
       padding: 1.2rem;
       margin-bottom: 1.5rem;
       box-shadow: 0 4px 12px rgba(168, 85, 247, 0.2);
   '>
       <div style='color: #a855f7; font-size: 15px; font-weight: 700; margin-bottom: 0.5rem;'>
           💡 Module đang phát triển
       </div>
       <div style='color: {DARK_COLORS['text_light']}; font-size: 13px; line-height: 1.6;'>
           Sẽ bổ sung: <b style='color: #c084fc;'>Search HĐ</b> • <b style='color: #d8b4fe;'>Chi tiết thanh toán</b> • <b style='color: #e9d5ff;'>Alert system</b>
       </div>
   </div>
   """, unsafe_allow_html=True)


   # ═══════════════════════════════════════════════════════════════
   # SUMMARY STATS
   # ═══════════════════════════════════════════════════════════════
   df['Nhom_no_KH'] = pd.to_numeric(df['Nhom_no_KH'], errors='coerce')


   total_contracts = len(df)
   high_risk_count = len(df[df['Nhom_no_KH'].isin([4, 5])])
   medium_risk_count = len(df[df['Nhom_no_KH'] == 3])
   overdue_count = len(df[df['Goc_qua_han'] > 0])


   col1, col2, col3, col4 = st.columns(4)


   # Card 1: Total contracts (Purple gradient)
   with col1:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #a855f7, #9333ea);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📋 Tổng HĐ</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_contracts:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Hợp đồng</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 2: High risk (Magenta gradient)
   with col2:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #d946ef, #c026d3);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(217, 70, 239, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>🚨 High Risk</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{high_risk_count:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Nhóm 4-5</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 3: Medium risk (Fuchsia gradient)
   with col3:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #e879f9, #d946ef);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(232, 121, 249, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>⚠️ Medium Risk</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{medium_risk_count:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Nhóm 3</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 4: Overdue (Pink gradient)
   with col4:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #f0abfc, #e879f9);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(240, 171, 252, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>⏰ Overdue</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{overdue_count:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Gốc quá hạn</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # HIGH RISK CONTRACTS TABLE
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🚨 Danh sách HĐ High Risk (Nhóm 4-5)")
   st.caption(f"📍 {high_risk_count:,} hợp đồng cần theo dõi sát")


   high_risk_contracts = df[df['Nhom_no_KH'].isin([4, 5])][
       ['Ma_chi_nhanh', 'Ma_khach_hang', 'Nhom_no_KH', 'Goc_vay_con_lai_no_trong_han_no_qua_han', 'Goc_qua_han']
   ].copy()


   high_risk_contracts.columns = ['Chi nhánh', 'Mã KH', 'Nhóm nợ', 'Dư nợ (VNĐ)', 'Gốc QH (VNĐ)']
   high_risk_contracts['Dư nợ (Tỷ)'] = (high_risk_contracts['Dư nợ (VNĐ)'] / 1e9).round(3)
   high_risk_contracts['Gốc QH (Tr)'] = (high_risk_contracts['Gốc QH (VNĐ)'] / 1e6).round(1)


   # Sort by risk level and debt
   high_risk_contracts = high_risk_contracts.sort_values(['Nhóm nợ', 'Dư nợ (VNĐ)'], ascending=[False, False])


   if len(high_risk_contracts) > 0:
       st.dataframe(
           high_risk_contracts[['Chi nhánh', 'Mã KH', 'Nhóm nợ', 'Dư nợ (Tỷ)', 'Gốc QH (Tr)']].head(50).style
           .background_gradient(cmap='RdPu', subset=['Nhóm nợ'])  # Red-Purple gradient
           .background_gradient(cmap='OrRd', subset=['Gốc QH (Tr)'])
           .format({
               'Dư nợ (Tỷ)': '{:.3f}',
               'Gốc QH (Tr)': '{:.1f}'
           }),
           use_container_width=True,
           height=400
       )


       # Summary insight
       col_summary, col_download = st.columns([2, 1])


       with col_summary:
           total_high_risk_debt = high_risk_contracts['Dư nợ (VNĐ)'].sum()
           group5_count = len(high_risk_contracts[high_risk_contracts['Nhóm nợ'] == 5])


           st.markdown(f"""
           <div style='
               background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
               border-left: 5px solid #a855f7;
               border-radius: 12px;
               padding: 1.2rem;
               box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
           '>
               <div style='color: #a855f7; font-size: 14px; font-weight: 700; margin-bottom: 0.5rem;'>
                   📊 Tóm tắt High Risk:
               </div>
               <div style='color: {DARK_COLORS['text_white']}; font-size: 13px; line-height: 1.8;'>
                   • <b style='color: #d946ef;'>Tổng dư nợ:</b> {total_high_risk_debt / 1e9:.2f} tỷ VNĐ<br>
                   • <b style='color: #e879f9;'>Nhóm 5:</b> {group5_count} HĐ (CRITICAL)<br>
                   • <b style='color: #f0abfc;'>Khuyến nghị:</b> Xử lý ngay, báo cáo Ban Giám đốc
               </div>
           </div>
           """, unsafe_allow_html=True)


       with col_download:
           csv_data = high_risk_contracts.to_csv(index=False).encode('utf-8')
           st.download_button(
               label="⬇️ Download High Risk",
               data=csv_data,
               file_name=f"HighRisk_Contracts_{datetime.now().strftime('%Y%m%d')}.csv",
               mime='text/csv',
               use_container_width=True
           )
   else:
       st.success("✅ Không có hợp đồng High Risk!")


   st.markdown("---")




# ═════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════
# MODULE 4: EXPORT & REPORTING - PURPLE GRADIENT THEME
# ═════════════════════════════════════════════════════════════════════


def show_export_reporting(df):
   """Module 4: Export & Reporting với Purple theme"""


   st.markdown("### 📊 Module 4: Export & Reporting")
   st.markdown("---")


   DARK_COLORS = {
       'text_white': '#f8fafc',
       'text_light': '#94a3b8',
       'grid': '#334155',
       'bg_card': '#0f172a'
   }


   # ═══════════════════════════════════════════════════════════════
   # STATS OVERVIEW - PURPLE GRADIENT
   # ═══════════════════════════════════════════════════════════════
   total_records = len(df)
   total_branches = df['Ma_chi_nhanh'].nunique()
   total_customers = df['Ma_khach_hang'].nunique()
   total_debt = df['Goc_vay_con_lai_no_trong_han_no_qua_han'].sum()


   col1, col2, col3, col4 = st.columns(4)


   # Card 1: Total Records (Deep Purple gradient)
   with col1:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #7c3aed, #6d28d9);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>📋 Total Records</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_records:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Rows in dataset</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 2: Branches (Violet gradient)
   with col2:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #8b5cf6, #7c3aed);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>🏢 Branches</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_branches:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Unique branches</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 3: Customers (Purple gradient)
   with col3:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #a78bfa, #8b5cf6);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>👥 Customers</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_customers:,}</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Unique customers</div>
       </div>
       """, unsafe_allow_html=True)


   # Card 4: Total Value (Light Purple gradient)
   with col4:
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, #c4b5fd, #a78bfa);
           border-radius: 12px;
           padding: 1.2rem;
           box-shadow: 0 4px 12px rgba(196, 181, 253, 0.3);
       '>
           <div style='color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 0.5rem;'>💰 Total Value</div>
           <div style='color: white; font-size: 26px; font-weight: 800;'>{total_debt / 1e12:.2f}T</div>
           <div style='color: rgba(255,255,255,0.7); font-size: 11px; margin-top: 0.3rem;'>Trillion VNĐ</div>
       </div>
       """, unsafe_allow_html=True)


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # EXPORT OPTIONS - PURPLE THEME
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 📥 Export dữ liệu")


   col_exp1, col_exp2 = st.columns(2)


   with col_exp1:
       st.markdown("##### 📄 Export Full Dataset")


       # Info box
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(109, 40, 217, 0.2));
           border: 2px solid #7c3aed;
           border-radius: 12px;
           padding: 1rem;
           margin-bottom: 1rem;
       '>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 12px; line-height: 1.6;'>
               • <b style='color: #7c3aed;'>Rows:</b> {total_records:,}<br>
               • <b style='color: #8b5cf6;'>Columns:</b> {len(df.columns)}<br>
               • <b style='color: #a78bfa;'>Format:</b> CSV (UTF-8)
           </div>
       </div>
       """, unsafe_allow_html=True)


       # Convert to CSV
       csv_data = df.to_csv(index=False).encode('utf-8')


       st.download_button(
           label="⬇️ Download Full Data (CSV)",
           data=csv_data,
           file_name=f"bank_data_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
           mime='text/csv',
           use_container_width=True,
           type="primary"
       )


   with col_exp2:
       st.markdown("##### 📊 Export Summary Report")


       # Summary data
       summary_data = df.groupby('Ma_chi_nhanh').agg({
           'Goc_vay_con_lai_no_trong_han_no_qua_han': ['sum', 'mean', 'count'],
           'Ma_khach_hang': 'nunique'
       }).reset_index()


       summary_data.columns = ['Branch', 'Total_Debt', 'Avg_Debt', 'Contract_Count', 'Customer_Count']


       # Info box
       st.markdown(f"""
       <div style='
           background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(124, 58, 237, 0.2));
           border: 2px solid #8b5cf6;
           border-radius: 12px;
           padding: 1rem;
           margin-bottom: 1rem;
       '>
           <div style='color: {DARK_COLORS['text_light']}; font-size: 12px; line-height: 1.6;'>
               • <b style='color: #7c3aed;'>Branches:</b> {total_branches}<br>
               • <b style='color: #8b5cf6;'>Metrics:</b> Debt, Contracts, Customers<br>
               • <b style='color: #a78bfa;'>Format:</b> Aggregated CSV
           </div>
       </div>
       """, unsafe_allow_html=True)


       summary_csv = summary_data.to_csv(index=False).encode('utf-8')


       st.download_button(
           label="⬇️ Download Summary by Branch (CSV)",
           data=summary_csv,
           file_name=f"branch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
           mime='text/csv',
           use_container_width=True,
           type="primary"
       )


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # NPL EXPORT - PURPLE ACCENTS
   # ═══════════════════════════════════════════════════════════════
   st.markdown("#### 🚨 Export Risk Reports")


   col_risk1, col_risk2, col_risk3 = st.columns(3)


   df['Nhom_no_KH'] = pd.to_numeric(df['Nhom_no_KH'], errors='coerce')


   with col_risk1:
       npl_data = df[df['Nhom_no_KH'] >= 3][
           ['Ma_chi_nhanh', 'Ma_khach_hang', 'Nhom_no_KH', 'Goc_vay_con_lai_no_trong_han_no_qua_han', 'Goc_qua_han']
       ].copy()


       st.metric("📊 NPL Records", f"{len(npl_data):,}")


       if len(npl_data) > 0:
           npl_csv = npl_data.to_csv(index=False).encode('utf-8')
           st.download_button(
               label="⬇️ NPL Report",
               data=npl_csv,
               file_name=f"npl_report_{datetime.now().strftime('%Y%m%d')}.csv",
               mime='text/csv',
               use_container_width=True
           )


   with col_risk2:
       high_risk_data = df[df['Nhom_no_KH'].isin([4, 5])][
           ['Ma_chi_nhanh', 'Ma_khach_hang', 'Nhom_no_KH', 'Goc_vay_con_lai_no_trong_han_no_qua_han']
       ].copy()


       st.metric("🚨 High Risk", f"{len(high_risk_data):,}")


       if len(high_risk_data) > 0:
           high_risk_csv = high_risk_data.to_csv(index=False).encode('utf-8')
           st.download_button(
               label="⬇️ High Risk Report",
               data=high_risk_csv,
               file_name=f"high_risk_{datetime.now().strftime('%Y%m%d')}.csv",
               mime='text/csv',
               use_container_width=True
           )


   with col_risk3:
       overdue_data = df[df['Goc_qua_han'] > 0][
           ['Ma_chi_nhanh', 'Ma_khach_hang', 'Goc_qua_han', 'Goc_vay_con_lai_no_trong_han_no_qua_han']
       ].copy()


       st.metric("⏰ Overdue", f"{len(overdue_data):,}")


       if len(overdue_data) > 0:
           overdue_csv = overdue_data.to_csv(index=False).encode('utf-8')
           st.download_button(
               label="⬇️ Overdue Report",
               data=overdue_csv,
               file_name=f"overdue_{datetime.now().strftime('%Y%m%d')}.csv",
               mime='text/csv',
               use_container_width=True
           )


   st.markdown("---")


   # ═══════════════════════════════════════════════════════════════
   # FUTURE FEATURES - PURPLE THEME
   # ═══════════════════════════════════════════════════════════════
   st.markdown(f"""
   <div style='
       background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
       border-left: 5px solid #7c3aed;
       border-radius: 12px;
       padding: 1.5rem;
       box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
   '>
       <div style='color: #7c3aed; font-size: 16px; font-weight: 700; margin-bottom: 1rem;'>
           💡 Upcoming Features:
       </div>
       <div style='color: {DARK_COLORS['text_white']}; font-size: 14px; line-height: 2;'>
           • <b style='color: #8b5cf6;'>PDF Report Generator:</b> Professional formatted reports<br>
           • <b style='color: #a78bfa;'>Email Schedule:</b> Auto-send reports daily/weekly<br>
           • <b style='color: #c4b5fd;'>Custom Report Builder:</b> Drag-and-drop report designer<br>
           • <b style='color: #7c3aed;'>Excel Export:</b> Multi-sheet workbooks with formatting
       </div>
   </div>
   """, unsafe_allow_html=True)



