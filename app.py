import streamlit as st
import math

def get_specific_dep_deduction(child_annual_salary):
    """特定親族特別控除の計算 (2026年度改正・65万円控除想定版)"""
    # 額面年収から65万円を引いて判定用の「所得」を算出
    total_income = max(0, child_annual_salary - 650_000)
    
    # 国税庁の判定表に基づいた所得税の控除額
    if total_income <= 850_000:
        return 630_000
    elif total_income <= 900_000:
        return 610_000
    elif total_income <= 950_000:
        return 510_000
    elif total_income <= 1_000_000:
        return 410_000
    elif total_income <= 1_050_000:
        return 310_000
    elif total_income <= 1_100_000:
        return 210_000
    elif total_income <= 1_150_000:
        return 110_000
    elif total_income <= 1_200_000:
        return 60_000
    elif total_income <= 1_230_000:
        return 30_000
    else:
        return 0

def calculate_tax_details(annual_income, allowance_monthly, social_ins, life_ins, earthquake_ins, ideco, dep_itax, dep_res):
    """個人の税金と手取り額を計算する"""
    # 扶養手当を年収に加算（通常は課税対象）
    total_gross = annual_income + (allowance_monthly * 12)
    
    # 1. 給与所得控除 (2026年改正想定)
    if total_gross <= 1_625_000:
        salary_ded = 550_000
    elif total_gross <= 1_800_000:
        salary_ded = total_gross * 0.40 - 100_000
    elif total_gross <= 3_600_000:
        salary_ded = total_gross * 0.30 + 80_000
    elif total_gross <= 6_600_000:
        salary_ded = total_gross * 0.20 + 440_000
    elif total_gross <= 8_500_000:
        salary_ded = total_gross * 0.10 + 1_100_000
    else:
        salary_ded = 1_950_000
    
    salary_income = max(0, total_gross - salary_ded)
    basic_itax, basic_res = 530_000, 480_000
    
    # 2. 所得控除
    eq_itax = min(50_000, earthquake_ins)
    eq_res = min(25_000, int(earthquake_ins / 2))
    total_common_ded_itax = social_ins + life_ins + eq_itax + ideco
    
    # 3. 課税所得と所得税
    taxable_itax = max(0, salary_income - (total_common_ded_itax + dep_itax + basic_itax))
    taxable_itax = (taxable_itax // 1000) * 1000
    
    if taxable_itax <= 1_950_000:
        itax = taxable_itax * 0.05
    elif taxable_itax <= 3_300_000:
        itax = taxable_itax * 0.10 - 97_500
    elif taxable_itax <= 6_950_000:
        itax = taxable_itax * 0.20 - 427_500
    elif taxable_itax <= 9_000_000:
        itax = taxable_itax * 0.23 - 636_000
    else:
        itax = taxable_itax * 0.33 - 1_536_000
    itax_total = math.floor(itax * 1.021)
    
    # 4. 住民税
    life_ins_res = min(28_000, int(life_ins * 0.7)) 
    taxable_res = max(0, salary_income - (social_ins + life_ins_res + eq_res + ideco + dep_res + basic_res))
    taxable_res = (taxable_res // 1000) * 1000
    res_tax_total = math.floor(taxable_res * 0.10 + 5_000)
    
    # 手取り額 = 総収入 - (社保 + 所得税 + 住民税)
    net_income = total_gross - (social_ins + itax_total + res_tax_total)
    
    return {
        "taxable_income": taxable_itax,
        "social_ins": social_ins,
        "income_tax": itax_total,
        "resident_tax": res_tax_total,
        "allowance_annual": allowance_monthly * 12,
        "net_income": net_income,
        "tax_subtotal": itax_total + res_tax_total
    }

# --- UI設定 ---
st.set_page_config(page_title="手取り最大化シミュレーター", layout="wide")
st.title("⚖️ 手取り最大化シミュレーター（2026年改正・特定親族対応版）")

with st.sidebar:
    st.header("子の条件設定")
    count_gen = st.number_input("一般扶養（高校生など）", min_value=0, value=1)
    count_spec = st.number_input("特定扶養（19〜22歳の大学生など）", min_value=0, value=0)
    
    spec_dep_itax = 0
    if count_spec > 0:
        st.subheader("大学生の年収設定")
        for i in range(count_spec):
            c_salary = st.number_input(f"子の年収：額面（{i+1}人目）", value=1_030_000, step=10_000)
            c_income = max(0, c_salary - 650_000)
            st.caption(f"判定用所得: {c_income:,}円")
            if c_income > 850_000:
                 st.warning("⚠️ 所得85万円超：親の控除額が段階的に減っています")
            spec_dep_itax += get_specific_dep_deduction(c_salary)
    
    # 扶養控除の合計（所得税・住民税）
    dep_itax = (count_gen * 380_000) + spec_dep_itax
    dep_res = (count_gen * 330_000) + (count_spec * 450_000)

col1, col2 = st.columns(2)
with col1:
    st.subheader("夫の条件")
    h_inc = st.number_input("基本の年収（夫）", value=6_000_000, step=10_000)
    h_allowance = st.number_input("会社の扶養手当：月額（夫）", value=0, step=1_000)
    h_soc = st.number_input("社会保険料（夫）", value=int(h_inc * 0.15))
    h_life = st.number_input("生命保険料控除（夫）", value=0)
    h_eq = st.number_input("地震保険料（夫）", value=0)
    h_ideco = st.number_input("iDeCo年間掛金（夫）", value=0, step=12_000)

with col2:
    st.subheader("妻の条件")
    w_inc = st.number_input("基本の年収（妻）", value=4_500_000, step=10_000)
    w_allowance = st.number_input("会社の扶養手当：月額（妻）", value=0, step=1_000)
    w_soc = st.number_input("社会保険料（妻）", value=int(w_inc * 0.15))
    w_life = st.number_input("生命保険料控除（妻）", value=0)
    w_eq = st.number_input("地震保険料（妻）", value=0)
    w_ideco = st.number_input("iDeCo年間掛金（妻）", value=0, step=12_000)

# パターンA: 夫が扶養する
res_h_a = calculate_tax_details(h_inc, h_allowance, h_soc, h_life, h_eq, h_ideco, dep_itax, dep_res)
res_w_a = calculate_tax_details(w_inc, 0, w_soc, w_life, w_eq, w_ideco, 0, 0)
total_net_a = res_h_a['net_income'] + res_w_a['net_income']

# パターンB: 妻が扶養する
res_h_b = calculate_tax_details(h_inc, 0, h_soc, h_life, h_eq, h_ideco, 0, 0)
res_w_b = calculate_tax_details(w_inc, w_allowance, w_soc, w_life, w_eq, w_ideco, dep_itax, dep_res)
total_net_b = res_h_b['net_income'] + res_w_b['net_income']

# --- 結果の表示 ---
st.divider()
net_diff = abs(total_net_a - total_net_b)
winner = "夫" if total_net_a > total_net_b else "妻"
st.success(f"💡 **{winner}** が扶養に入れる方が、世帯全体の手取り額が年間 **{net_diff:,}円** 多くなります。")

st.subheader("📊 世帯手取り額と内訳の比較")

def get_row_data(h, w):
    """表の1列分のデータを作成する"""
    return [
        f"**{h['net_income'] + w['net_income']:,}円**", # 世帯手取り合計
        f"{h['allowance_annual'] + w['allowance_annual']:,}円", # 扶養手当合計
        f"{h['social_ins'] + w['social_ins']:,}円", # 社会保険料合計
        f"{h['tax_subtotal'] + w['tax_subtotal']:,}円", # 納税額合計
        f"{h['taxable_income']:,}円", # 夫の課税所得
        f"{h['tax_subtotal']:,}円", # 夫の納税額
        f"　(所得税:{h['income_tax']:,} / 住民税:{h['resident_tax']:,})",
        f"{w['taxable_income']:,}円", # 妻の課税所得
        f"{w['tax_subtotal']:,}円", # 妻の納税額
        f"　(所得税:{w['income_tax']:,} / 住民税:{w['resident_tax']:,})"
    ]

st.table({
    "項目": [
        "夫婦の手取り合計（年収+手当-税金-社保）",
        "支給された扶養手当の合計",
        "社会保険料の世帯合計",
        "納税額の世帯合計",
        "夫の課税所得",
        "夫の納税額(所得税+住民税)",
        "　内訳：夫の税金",
        "妻の課税所得",
        "妻の納税額(所得税+住民税)",
        "　内訳：妻の税金"
    ],
    "パターンA (夫が扶養)": get_row_data(res_h_a, res_w_a),
    "パターンB (妻が扶養)": get_row_data(res_h_b, res_w_b),
})