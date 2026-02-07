import FinanceDataReader as fdr
import pandas as pd
import requests
from datetime import datetime

# 시작 알림
print("🚀 [PC 버전] 구름대 돌파 및 정밀 분석을 시작합니다 (상위 500종목)...")

# 본인의 디스코드 웹훅 URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1469518453634367508/NP72-1cMzuidSJuzP6-r-c1p-R4odLkQg7WcH9HmGuAmu02zuIRtQ5_SyOzMj7rZdRAK"

def send_discord_message(payload):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"디스코드 전송 실패: {e}")

def get_pro_stocks():
    # KRX 전체 종목을 가져와서 시가총액 상위 1,000개 분석 (코스닥 포함)
    df_krx = fdr.StockListing('KRX')
    results = []
    
    for i, row in df_krx.head(500).iterrows():
        symbol = row['Code']
        name = row['Name']
        
        try:
            df = fdr.DataReader(symbol).tail(100)
            if len(df) < 80: continue
            
            c, h, l, o, v = df['Close'], df['High'], df['Low'], df['Open'], df['Volume']
            curr_price = c.iloc[-1]
            prev_price = c.iloc[-2]
            change_rate = ((curr_price - prev_price) / prev_price) * 100
            
            # 필터 1: 상승률(7~20%) & 거래량(3배)
            if not (7 <= change_rate < 20): continue
            avg_vol = v.iloc[-21:-1].mean()
            if v.iloc[-1] < avg_vol * 3: continue
            
            # 필터 2: 정배열(5>20>60) & 20일 신고가
            ma5 = c.rolling(5).mean().iloc[-1]
            ma20 = c.rolling(20).mean().iloc[-1]
            ma60 = c.rolling(60).mean().iloc[-1]
            if not (ma5 > ma20 > ma60): continue
            if curr_price <= h.iloc[-21:-1].max(): continue

            # 필터 3: 일목균형표 구름대 돌파
            high_9 = h.rolling(9).max()
            low_9 = l.rolling(9).min()
            tenkan_sen = (high_9 + low_9) / 2
            high_26 = h.rolling(26).max()
            low_26 = l.rolling(26).min()
            kijun_sen = (high_26 + low_26) / 2
            
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            high_52 = h.rolling(52).max()
            low_52 = l.rolling(52).min()
            senkou_span_b = ((high_52 + low_52) / 2).shift(26)
            
            cloud_max = max(senkou_span_a.iloc[-1], senkou_span_b.iloc[-1])
            if curr_price <= cloud_max: continue

            # 필터 4: 이격도 (과열 방지)
            if (curr_price / ma20) * 100 > 115: continue

            # 타점 계산
            buy_price = curr_price
            target_price = buy_price * 1.10
            stop_loss = buy_price * 0.95

            results.append(
                f"💎 **{name}({symbol})**\n"
                f"✅ **상승 추세 확정 (구름대 돌파)**\n"
                f"💰 **매수: {buy_price:,}원** / 🎯 **목표: {int(target_price):,}원** / 🛑 **손절: {int(stop_loss):,}원**\n"
                f"- 거래량: {v.iloc[-1]/avg_vol:.1f}배 / 상승률: {change_rate:.2f}%"
            )
        except: continue
    return results

if __name__ == "__main__":
    candidates = get_pro_stocks()
    if candidates:
        content = "\n\n".join(candidates)
        payload = {"content": f"🚨 **[VIP 리포트] 오늘의 A급 종목**\n\n{content}"}
    else:
        payload = {"content": "✅ 분석 완료: 오늘은 조건을 모두 만족하는 종목이 없습니다."}
    
    send_discord_message(payload)
    print("✨ 분석 완료! 디스코드를 확인하세요.")