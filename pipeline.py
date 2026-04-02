
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import requests
import time
import os
import shutil
from datetime import datetime, timedelta

BASE_PATH  = '.'
APP_PATH   = './streamlit_app'
API_KEY    = os.environ.get('DART_API_KEY', '')

EPS_ACCOUNT_NAMES = {
    '기본주당이익', '기본주당순이익', '기본주당순이익(손실)',
    '기본 주당순이익(손실)', '주당순이익', '주당이익',
    '기본주당이익(손실)', '보통주기본주당이익(손실)',
    '보통주기본주당이익', '보통주 기본주당이익',
    '보통주 기본및희석주당이익', '1. 기본주당이익',
    '기본주당보통주순이익(손실)', '기본주당이익(손실) 합계',
    '기본주당이익(단위: 원)', '지배기업 소유주 기본주당이익',
    '계속영업기본주당이익(손실)',
}

def update_current_prices(df):
    prices = {}
    for _, row in df.iterrows():
        try:
            df_p = fdr.DataReader(
                row['Code'],
                datetime.now() - timedelta(days=5)
            )
            if len(df_p) > 0:
                prices[row['Code']] = df_p['Close'].iloc[-1]
        except:
            pass
        time.sleep(0.03)
    df['price'] = df['Code'].map(prices)
    print(f"현재가 수집: {len(prices)}개")
    return df

def recalculate_gaps(df):
    df['PER'] = df['price'] / df['EPS']
    df = df[df['PER'] > 0].copy()

    market_per    = df['PER'].median()
    sector_per    = df.groupby('Sector')['PER'].median()
    df['sector_median_per'] = df['Sector'].map(sector_per)

    df['fair_price_market'] = df['EPS'] * market_per
    df['fair_price_sector'] = df['EPS'] * df['sector_median_per']
    df['gap_market'] = (df['price'] - df['fair_price_market']) / df['fair_price_market']
    df['gap_sector'] = (df['price'] - df['fair_price_sector'])  / df['fair_price_sector']

    ADJUST_FACTOR = 0.5
    def adjust(gap, yoy):
        if pd.isna(gap): return None
        if pd.isna(yoy) or yoy <= 0: return round(gap, 4)
        yoy_d = min(yoy, 100.0) / 100.0
        return round(gap - (gap * yoy_d * ADJUST_FACTOR), 4) if gap > 0 else round(gap, 4)

    df['gap_market_v2'] = df.apply(lambda r: adjust(r['gap_market'], r.get('yoy_growth_pct')), axis=1)
    df['gap_sector_v2'] = df.apply(lambda r: adjust(r['gap_sector'],  r.get('yoy_growth_pct')), axis=1)

    def signal(row):
        gm, gs = row['gap_market_v2'], row['gap_sector_v2']
        if pd.isna(gm) or pd.isna(gs): return 'UNKNOWN'
        avg = (gm + gs) / 2
        if avg <= -0.30:   return '강력매수'
        elif avg <= -0.15: return '매수'
        elif avg >= 0.30:  return '강력매도'
        elif avg >= 0.15:  return '매도'
        else:              return '중립'

    df['signal_v2']  = df.apply(signal, axis=1)
    df['updated_at'] = datetime.now().strftime('%Y-%m-%d')
    print(f"괴리율 재계산 완료: {len(df)}개 | 시장PER: {market_per:.2f}")
    return df

def rerun_screening(df):
    c1 = (df['gap_market_v2'] < -0.15) & (df['gap_sector_v2'] < -0.15)
    c2 = (df['yoy_growth_pct'] > 0) | (df['yoy_growth_pct'].isna())
    c3 = (df['debt_ratio'] < 200) | (df['debt_ratio'].isna())
    df_final = df[c1 & c2 & c3].sort_values('gap_market_v2').copy()
    print(f"스크리닝 완료: {len(df_final)}개")
    return df_final

def run_pipeline():
    print(f"파이프라인 시작: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    df = pd.read_csv(
        f'{BASE_PATH}/streamlit_app/data/output/gap_v2.csv',
        dtype={'Code': str, 'corp_code': str}
    )
    df['corp_code'] = df['corp_code'].str.zfill(8)

    df       = update_current_prices(df)
    df       = recalculate_gaps(df)
    df_final = rerun_screening(df)

    df.to_csv(f'{APP_PATH}/data/output/gap_v2.csv',
              index=False, encoding='utf-8-sig')
    df_final.to_csv(f'{APP_PATH}/data/output/gap_v2_final.csv',
                    index=False, encoding='utf-8-sig')

    print(f"파이프라인 완료! 저평가: {len(df_final)}개")

if __name__ == '__main__':
    run_pipeline()
