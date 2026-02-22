import streamlit as st
import math

def calculate_tax_details(annual_income, allowance_monthly, social_ins, life_ins, earthquake_ins, ideco, dep_itax, dep_res):
    # 手当を年収に加算（手当も通常は課税対象）
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
    
    # 3. 課税所得と税金
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
    
    life_ins_res = min(28_000, int(life_ins * 0.7)) 
    taxable_res = max(0, salary_income - (social_ins + life_ins_res + eq_res + ideco + dep_res + basic_res))
    taxable_res = (taxable_res // 1000) * 1000
    res_tax_total = math.floor(taxable_res * 0.10 + 5_000)
    
    # 手取り額 = (年収 + 手当) - (社保 + 所得税 + 住民税)
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

st.set_page_config(page_title="扶養控除シミュレーター", layout="wide")
st.title("⚖️ 手取り最大化シミュレーター（扶養手当対応版）")

with st.sidebar:
    st.header("子の人数設定")
    count_gen = st.number_input("高校生など（一般扶養）", min_value=0, value=1)
    count_spec = st.number_input("大学生など（特定扶養）", min_value=0, value=0)
    dep_itax = (count_gen * 380_000) + (count_spec * 630_000)
    dep_res = (count_gen * 330_000) + (count_spec * 450_000)

col1, col2 = st.columns(2)
with col1:
    st.subheader("夫の条件")
    h_inc = st.number_input("基本の年収（夫）", value=6_000_000, step=10_000)
    h_allowance = st.number_input("会社の扶養手当：月額（夫）", value=0, step=1_000, help="扶養している場合に支給される月額")
    h_soc = st.number_input("社会保険料（夫）", value=int(h_inc * 0.15))
    h_life = st.number_input("生命保険料控除（夫）", value=40_000)
    h_eq = st.number_input("地震保険料（夫）", value=0)
    h_ideco = st.number_input("iDeCo年間掛金（夫）", value=0, step=12_000)

with col2:
    st.subheader("妻の条件")
    w_inc = st.number_input("基本の年収（妻）", value=4_500_000, step=10_000)
    w_allowance = st.number_input("会社の扶養手当：月額（妻）", value=0, step=1_000)
    w_soc = st.number_input("社会保険料（妻）", value=int(w_inc * 0.15))
    w_life = st.number_input("生命保険料控除（妻）", value=40_000)
    w_eq = st.number_input("地震保険料（妻）", value=0)
    w_ideco = st.number_input("iDeCo年間掛金（妻）", value=144_000, step=12_000)

# パターンA: 夫が扶養（夫が手当をもらう）
res_h_a = calculate_tax_details(h_inc, h_allowance, h_soc, h_life, h_eq, h_ideco, dep_itax, dep_res)
res_w_a = calculate_tax_details(w_inc, 0, w_soc, w_life, w_eq, w_ideco, 0, 0)
total_net_a = res_h_a['net_income'] + res_w_a['net_income']

# パターンB: 妻が扶養（妻が手当をもらう）
res_h_b = calculate_tax_details(h_inc, 0, h_soc, h_life, h_eq, h_ideco, 0, 0)
res_w_b = calculate_tax_details(w_inc, w_allowance, w_soc, w_life, w_eq, w_ideco, dep_itax, dep_res)
total_net_b = res_h_b['net_income'] + res_w_b['net_income']

st.divider()
net_diff = abs(total_net_a - total_net_b)
winner = "夫" if total_net_a > total_net_b else "妻"
st.success(f"💡 **{winner}** が扶養に入れる方が、世帯全体の最終的な手取り額が年間 **{net_diff:,}円** 多くなります。")

st.subheader("📊 世帯手取り額と内訳の比較")

def get_row_data(h, w):
    return [
        f"**{h['net_income'] + w['net_income']:,}円**", # 世帯手取り合計
        f"{h['allowance_annual'] + w['allowance_annual']:,}円", # 扶養手当の合計
        f"{h['social_ins'] + w['social_ins']:,}円", # 社会保険料の合計
        f"{h['tax_subtotal'] + w['tax_subtotal']:,}円", # 納税額の合計
        f"{h['taxable_income']:,}円", # 夫の課税所得
        f"{h['tax_subtotal']:,}円", # 夫の納税額
        f"　(所得税:{h['income_tax']:,} / 住民税:{h['resident_tax']:,})",
        f"{w['taxable_income']:,}円", # 妻の課税所得
        f"{w['tax_subtotal']:,}円", # 妻の納税額
        f"　(所得税:{w['income_tax']:,} / 住民税:{w['resident_tax']:,})"
    ]

st.table({
    "項目": [
        "世帯手取り合計（年収+手当-税金-社保）",
        "支給された扶養手当の合計",
        "社会保険料の世帯合計",
        "納税額の世帯合計",
        "夫の課税所得",
        "夫の納税額(所得税+住民税)",
        "　夫の税金内訳",
        "妻の課税所得",
        "妻の納税額(所得税+住民税)",
        "　妻の税金内訳"
    ],
    "パターンA (夫が扶養)": get_row_data(res_h_a, res_w_a),
    "パターンB (妻が扶養)": get_row_data(res_h_b, res_w_b),
})