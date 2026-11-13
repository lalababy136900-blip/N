import random
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="台指期 盤差與大單紅綠監控", page_icon="📈", layout="centered"
)

# 極簡黑底與紅綠燈樣式 CSS
st.markdown(
    """
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .metric-card { background-color: #1e1e1e; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 10px; }
    .up-price { color: #ff4d4d; font-size: 24px; font-weight: bold; }
    .down-price { color: #00cc66; font-size: 24px; font-weight: bold; }
    
    /* 大單高亮背景 */
    .big-red-box { background-color: rgba(255, 77, 77, 0.2); border-left: 4px solid #ff4d4d; padding: 6px; margin: 3px 0; }
    .big-green-box { background-color: rgba(0, 204, 102, 0.2); border-left: 4px solid #00cc66; padding: 6px; margin: 3px 0; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚡ 台指期 1分盤差與大單紅綠監控")
st.markdown("---")

# 側邊欄：設定大單張數門檻
st.sidebar.header("⚙️ 警示設定")
threshold = st.sidebar.slider(
    "大單門檻 (張數)", min_value=10, max_value=100, value=30, step=5
)
st.sidebar.info(f"💡 單筆大單門檻：**{threshold} 張**")

# 初始化 Session State
if "start_time" not in st.session_state:
  st.session_state.start_time = time.time()
  st.session_state.accumulated_spread = 0
  st.session_state.minute_volume = 0
  st.session_state.trade_log = []

placeholder = st.empty()

# 模擬即時跳動迴圈
for _ in range(300):
  current_time = time.time()
  elapsed = current_time - st.session_state.start_time

  # ⏱️ 每 60 秒自動歸零 1 分鐘累積數據
  if elapsed >= 60:
    st.session_state.start_time = current_time
    st.session_state.accumulated_spread = 0
    st.session_state.minute_volume = 0

  # 模擬成交：is_red = True (外盤買進/紅), is_red = False (內盤賣出/綠)
  is_red = random.choice([True, False])
  tick_vol = random.randint(1, 50)  # 隨機成交張數
  base_price = 23450
  curr_price = base_price + random.randint(-3, 3)

  # 累積盤差與總量
  spread_delta = tick_vol if is_red else -tick_vol
  st.session_state.accumulated_spread += spread_delta
  st.session_state.minute_volume += tick_vol

  is_big = tick_vol >= threshold
  time_str = time.strftime("%H:%M:%S", time.localtime(current_time))

  # 達到大單門檻時右下角彈出提示
  if is_big:
    color_name = "紅燈(買)" if is_red else "綠燈(賣)"
    st.toast(
        f"🚨【大單警示】成交 {tick_vol} 張 ({color_name})！價格：{curr_price}",
        icon="⚡",
    )

  # 記錄到成交明細
  st.session_state.trade_log.insert(
      0,
      {
          "時間": time_str,
          "價格": curr_price,
          "張數": tick_vol,
          "is_red": is_red,
          "is_big": is_big,
      },
  )

  if len(st.session_state.trade_log) > 15:
    st.session_state.trade_log.pop()

  acc_spread = st.session_state.accumulated_spread
  min_vol = st.session_state.minute_volume
  spread_color = "#ff4d4d" if acc_spread >= 0 else "#00cc66"
  seconds_left = max(0, int(60 - elapsed))

  with placeholder.container():
    col1, col2, col3 = st.columns(3)

    with col1:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div>台指期最新價</div>
                    <div class="up-price">{curr_price}</div>
                    <div style="font-size:14px; color:#ff4d4d;">+120 (+0.51%)</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div>🔥 1分累積盤差</div>
                    <div style="color: {spread_color}; font-size: 24px; font-weight: bold;">{acc_spread:+d} 張</div>
                    <div style="font-size:12px; color:#888;">倒數 {seconds_left} 秒重置</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    with col3:
      st.markdown(
          f"""
                <div class="metric-card">
                    <div>1分成交量</div>
                    <div style="font-size:24px; font-weight:bold;">{min_vol:,}</div>
                    <div style="font-size:12px; color:#888;">本分K累計張數</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

    # 左右並排：五檔與即時明細
    col_depth, col_trades = st.columns([1, 1])

    with col_depth:
      st.markdown("### 📊 委買委賣五檔")
      p = curr_price
      sell_df = pd.DataFrame(
          {
              "賣價": [p + 5, p + 4, p + 3, p + 2, p + 1],
              "張數": [
                  random.randint(5, 30),
                  random.randint(10, 50),
                  random.randint(20, 80),
                  random.randint(5, 30),
                  random.randint(1, 20),
              ],
          }
      )
      st.dataframe(sell_df, hide_index=True, use_container_width=True)

      buy_df = pd.DataFrame(
          {
              "買價": [p - 1, p - 2, p - 3, p - 4, p - 5],
              "張數": [
                  random.randint(5, 30),
                  random.randint(20, 80),
                  random.randint(10, 50),
                  random.randint(5, 30),
                  random.randint(1, 20),
              ],
          }
      )
      st.dataframe(buy_df, hide_index=True, use_container_width=True)

    with col_trades:
      st.markdown(f"### ⚡ 即時成交明細 (大單門檻: {threshold}張)")

      for trade in st.session_state.trade_log:
        t_time = trade["時間"]
        t_price = trade["價格"]
        t_vol = trade["張數"]
        is_red = trade["is_red"]
        is_big = trade["is_big"]

        color_hex = "#ff4d4d" if is_red else "#00cc66"

        if is_big:
          box_style = "big-red-box" if is_red else "big-green-box"
          st.markdown(
              f"""
                    <div class="{box_style}">
                        <span style="color:#aaa; font-size:12px;">{t_time}</span> | 
                        價格: <span style="color:{color_hex}; font-weight:bold;">{t_price}</span> | 
                        張數: <span style="color:{color_hex}; font-weight:bold; font-size:16px;">{t_vol} ⚡</span>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
        else:
          st.markdown(
              f"""
                    <div style="padding: 2px 0; border-bottom: 1px solid #222; font-size: 14px;">
                        <span style="color:#aaa; font-size:12px;">{t_time}</span> | 
                        價格: <span style="color:{color_hex};">{t_price}</span> | 
                        張數: <span style="color:{color_hex}; font-weight:bold;">{t_vol}</span>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

    st.caption("⏱️ 紅字代表外盤買進，綠字代表內盤賣出。超過門檻會自動彈出通知！")

  time.sleep(1)
  st.rerun()
