import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 🎯 티커 정의
tickers = {
    'QQQ (USD)': 'QQQ',
    'SPY (USD)': 'SPY',
    'USD/KRW': 'KRW=X'
}

# 📅 30일 조회
end_date = datetime.today()
start_date = end_date - timedelta(days=30)

# 📥 데이터 다운로드
data = {}
for label, ticker in tickers.items():
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    if not df.empty and 'Close' in df.columns and df['Close'].dropna().shape[0] > 1:
        data[label] = df['Close'].squeeze()
    else:
        print(f"⚠️ No valid data for {label} ({ticker})")

# 📊 병합
df_all = pd.DataFrame(data)
if df_all.empty:
    raise ValueError("No valid data was fetched.")

# 💱 환율 적용
usd_to_krw = df_all['USD/KRW'].ffill()
converted = df_all.copy()
for col in df_all.columns:
    if '(USD)' in col:
        converted[col + ' (KRW)'] = df_all[col] * usd_to_krw

# 📈 세로형 subplot (3행 1열, 마지막 행은 환율)
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=False, vertical_spacing=0.12,
    subplot_titles=[
        'QQQ: USD vs KRW',
        'SPY: USD vs KRW',
        'USD/KRW 환율 (최근 30일)'
    ],
    specs=[
        [{"secondary_y": True}],
        [{"secondary_y": True}],
        [{}]
    ]
)

# ▶️ QQQ
fig.add_trace(go.Scatter(
    x=converted.index, y=converted['QQQ (USD)'],
    name='QQQ (USD)', line=dict(color='blue')
), row=1, col=1, secondary_y=False)

fig.add_trace(go.Scatter(
    x=converted.index, y=converted['QQQ (USD) (KRW)'],
    name='QQQ (KRW)', line=dict(color='red', dash='dot')
), row=1, col=1, secondary_y=True)

# ▶️ SPY
fig.add_trace(go.Scatter(
    x=converted.index, y=converted['SPY (USD)'],
    name='SPY (USD)', line=dict(color='green')
), row=2, col=1, secondary_y=False)

fig.add_trace(go.Scatter(
    x=converted.index, y=converted['SPY (USD) (KRW)'],
    name='SPY (KRW)', line=dict(color='orange', dash='dot')
), row=2, col=1, secondary_y=True)

# ▶️ 환율
fig.add_trace(go.Scatter(
    x=converted.index, y=converted['USD/KRW'],
    name='USD/KRW 환율', line=dict(color='purple')
), row=3, col=1)

# 🛠️ 레이아웃
fig.update_layout(
    title='QQQ, SPY 가격 및 USD/KRW 환율 비교 (최근 30일)',
    height=1200,  # 길이 충분히 확보
    template='plotly_white',
    hovermode='x unified',
    legend=dict(orientation='h', y=-0.1, x=0.5, xanchor='center'),
    margin=dict(t=60, b=60, l=60, r=60)
)

# 🧭 Y축 라벨
fig.update_yaxes(title_text="USD", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="KRW", row=1, col=1, secondary_y=True)
fig.update_yaxes(title_text="USD", row=2, col=1, secondary_y=False)
fig.update_yaxes(title_text="KRW", row=2, col=1, secondary_y=True)
fig.update_yaxes(title_text="원화 환율 (1USD)", row=3, col=1)

fig.show()

# 그래프를 HTML로 저장
# fig.write_html("index.html")