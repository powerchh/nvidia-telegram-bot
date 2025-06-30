# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_macd(close, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_diff = macd_line - signal_line
    return macd_line, signal_line, macd_diff

def analyze_macd_signals(df):
    """分析MACD买卖信号"""
    if len(df) < 2:
        return []
    
    signals = []
    
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        previous_row = df.iloc[i-1]
        
        try:
            current_macd = float(current_row['MACD'].iloc[0]) if hasattr(current_row['MACD'], 'iloc') else float(current_row['MACD'])
            current_signal = float(current_row['Signal'].iloc[0]) if hasattr(current_row['Signal'], 'iloc') else float(current_row['Signal'])
            current_diff = float(current_row['MACD_diff'].iloc[0]) if hasattr(current_row['MACD_diff'], 'iloc') else float(current_row['MACD_diff'])
            current_close = float(current_row['Close'].iloc[0]) if hasattr(current_row['Close'], 'iloc') else float(current_row['Close'])
            
            previous_macd = float(previous_row['MACD'].iloc[0]) if hasattr(previous_row['MACD'], 'iloc') else float(previous_row['MACD'])
            previous_signal = float(previous_row['Signal'].iloc[0]) if hasattr(previous_row['Signal'], 'iloc') else float(previous_row['Signal'])
            previous_diff = float(previous_row['MACD_diff'].iloc[0]) if hasattr(previous_row['MACD_diff'], 'iloc') else float(previous_row['MACD_diff'])
            previous_close = float(previous_row['Close'].iloc[0]) if hasattr(previous_row['Close'], 'iloc') else float(previous_row['Close'])
        except (ValueError, KeyError) as e:
            continue
        
        signal_type = ""
        signal_strength = ""
        description = ""
        
        # 1. 金叉死叉信号
        if current_diff > 0 and previous_diff <= 0:
            if current_macd > 0:
                signal_type = "强烈买入"
                signal_strength = "5星"
                description = "零轴上方金叉 - 强烈看涨信号"
            else:
                signal_type = "买入"
                signal_strength = "3星"
                description = "零轴下方金叉 - 谨慎看涨信号"
                
        elif current_diff < 0 and previous_diff >= 0:
            if current_macd < 0:
                signal_type = "强烈卖出"
                signal_strength = "5星"
                description = "零轴下方死叉 - 强烈看跌信号"
            else:
                signal_type = "卖出"
                signal_strength = "3星"
                description = "零轴上方死叉 - 谨慎看跌信号"
        
        # 2. 零轴穿越信号
        elif current_macd > 0 and previous_macd <= 0:
            signal_type = "多头确认"
            signal_strength = "4星"
            description = "MACD突破零轴 - 趋势转多"
            
        elif current_macd < 0 and previous_macd >= 0:
            signal_type = "空头确认"
            signal_strength = "4星"
            description = "MACD跌破零轴 - 趋势转空"
        
        # 3. 柱状图趋势信号
        elif abs(current_diff) > abs(previous_diff):
            if current_diff > 0:
                signal_type = "动能增强"
                signal_strength = "2星"
                description = "多头动能加强"
            else:
                signal_type = "动能增强"
                signal_strength = "2星"
                description = "空头动能加强"
        
        # 4. 背离信号检测
        if i >= 5:
            try:
                price_5_days_ago = float(df.iloc[i-5]['Close'].iloc[0]) if hasattr(df.iloc[i-5]['Close'], 'iloc') else float(df.iloc[i-5]['Close'])
                macd_5_days_ago = float(df.iloc[i-5]['MACD'].iloc[0]) if hasattr(df.iloc[i-5]['MACD'], 'iloc') else float(df.iloc[i-5]['MACD'])
                
                price_trend = current_close - price_5_days_ago
                macd_trend = current_macd - macd_5_days_ago
                
                price_std = df['Close'].std()
                
                if price_trend > 0 and macd_trend < 0 and abs(price_trend) > price_std * 0.5:
                    signal_type = "顶背离"
                    signal_strength = "4星"
                    description = "价格新高但MACD走低 - 警惕回调"
                elif price_trend < 0 and macd_trend > 0 and abs(price_trend) > price_std * 0.5:
                    signal_type = "底背离"
                    signal_strength = "4星"
                    description = "价格新低但MACD走高 - 关注反弹"
            except (ValueError, KeyError):
                pass
        
        if signal_type:
            signals.append({
                'date': current_row.name.strftime('%Y-%m-%d') if hasattr(current_row.name, 'strftime') else str(current_row.name),
                'price': round(current_close, 2),
                'macd': round(current_macd, 3),
                'signal': round(current_signal, 3),
                'diff': round(current_diff, 3),
                'signal_type': signal_type,
                'strength': signal_strength,
                'description': description
            })
    
    return signals

def get_current_status(df):
    """获取当前市场状态"""
    if len(df) == 0:
        return {
            'trend': "无数据",
            'momentum': "无数据",
            'position': "无数据"
        }
    
    latest = df.iloc[-1]
    status = {}
    
    try:
        latest_macd = float(latest['MACD'].iloc[0]) if hasattr(latest['MACD'], 'iloc') else float(latest['MACD'])
        latest_diff = float(latest['MACD_diff'].iloc[0]) if hasattr(latest['MACD_diff'], 'iloc') else float(latest['MACD_diff'])
    except (ValueError, KeyError):
        return {
            'trend': "数据错误",
            'momentum': "数据错误",
            'position': "数据错误"
        }
    
    # 当前趋势
    if latest_macd > 0:
        if latest_diff > 0:
            status['trend'] = "强势多头"
        else:
            status['trend'] = "多头调整"
    else:
        if latest_diff < 0:
            status['trend'] = "强势空头"
        else:
            status['trend'] = "空头反弹"
    
    # 动能状态
    if len(df) >= 2:
        try:
            prev = df.iloc[-2]
            prev_diff = float(prev['MACD_diff'].iloc[0]) if hasattr(prev['MACD_diff'], 'iloc') else float(prev['MACD_diff'])
            if abs(latest_diff) > abs(prev_diff):
                status['momentum'] = "动能增强"
            else:
                status['momentum'] = "动能减弱"
        except (ValueError, KeyError):
            status['momentum'] = "动能数据异常"
    else:
        status['momentum'] = "数据不足"
    
    # 位置分析
    try:
        latest_signal = float(latest['Signal'].iloc[0]) if hasattr(latest['Signal'], 'iloc') else float(latest['Signal'])
        if latest_macd > latest_signal:
            status['position'] = "MACD在信号线上方"
        else:
            status['position'] = "MACD在信号线下方"
    except (ValueError, KeyError):
        status['position'] = "位置数据异常"
    
    return status

def analyze_stock(symbol, days=90, interval="1d", verbose=True):
    """
    分析指定股票的MACD指标和交易信号
    
    参数:
    symbol (str): 股票代码 (例如: "NVDA", "AAPL", "TSLA")
    days (int): 分析的天数，默认90天
    interval (str): 数据间隔，默认"1d" (日线)
    verbose (bool): 是否打印详细信息，默认True
    
    返回:
    dict: 包含分析结果的字典
    """
    try:
        # 获取数据
        if verbose:
            print(f"正在获取 {symbol} 股票数据...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        df = yf.download(symbol, start=start_date, end=end_date, interval=interval, auto_adjust=True)
        
        if df.empty:
            error_msg = f"未能获取 {symbol} 股票数据，请检查网络连接或股票代码"
            if verbose:
                print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'symbol': symbol
            }
        
        if verbose:
            print(f"总共获取 {len(df)} 个交易日数据")
            print(f"数据范围：{df.index[0].strftime('%Y-%m-%d')} 到 {df.index[-1].strftime('%Y-%m-%d')}")
        
        # 计算MACD
        df['MACD'], df['Signal'], df['MACD_diff'] = calculate_macd(df['Close'])
        df = df.dropna()
        
        if verbose:
            print(f"有效MACD数据：{len(df)} 天")
        
        # 分析买卖信号
        signals = analyze_macd_signals(df)
        
        # 当前市场状态
        current_status = get_current_status(df)
        latest = df.iloc[-1]
        
        if verbose:
            print(f"当前市场状态分析：")
            print("="*50)
            print(f"日期：{latest.name.strftime('%Y-%m-%d')}")
        
        # 确保数值格式化不会出错
        try:
            close_price = float(latest['Close'].iloc[0]) if hasattr(latest['Close'], 'iloc') else float(latest['Close'])
            macd_value = float(latest['MACD'].iloc[0]) if hasattr(latest['MACD'], 'iloc') else float(latest['MACD'])
            signal_value = float(latest['Signal'].iloc[0]) if hasattr(latest['Signal'], 'iloc') else float(latest['Signal'])
            diff_value = float(latest['MACD_diff'].iloc[0]) if hasattr(latest['MACD_diff'], 'iloc') else float(latest['MACD_diff'])
            
            if verbose:
                print(f"收盘价：${close_price:.2f}")
                print(f"MACD：{macd_value:.3f}")
                print(f"信号线：{signal_value:.3f}")
                print(f"差值：{diff_value:.3f}")
        except (ValueError, KeyError) as e:
            if verbose:
                print(f"数据格式化错误: {str(e)}")
            close_price = macd_value = signal_value = diff_value = None
        
        if verbose:
            print(f"趋势：{current_status['trend']}")
            print(f"动能：{current_status['momentum']}")
            print(f"位置：{current_status['position']}")
        
        # 操作建议
        recommendation = ""
        try:
            latest_diff = float(latest['MACD_diff'].iloc[0]) if hasattr(latest['MACD_diff'], 'iloc') else float(latest['MACD_diff'])
            if latest_diff > 0.5:
                recommendation = "强烈建议：持有或买入，多头动能强劲"
            elif latest_diff > 0:
                recommendation = "谨慎乐观：可以持有，关注后续发展"
            elif latest_diff > -0.5:
                recommendation = "保持警惕：考虑减仓，等待明确信号"
            else:
                recommendation = "建议谨慎：考虑卖出或观望，空头动能较强"
        except (ValueError, KeyError):
            recommendation = "无法给出操作建议，MACD数据异常"
        
        if verbose:
            print(f"操作建议：")
            print("="*50)
            print(recommendation)
            print("风险提示：MACD是滞后指标，建议结合其他技术指标和基本面分析！")
        
        # 返回分析结果
        return {
            'success': True,
            'symbol': symbol,
            'data_points': len(df),
            'date_range': {
                'start': df.index[0].strftime('%Y-%m-%d'),
                'end': df.index[-1].strftime('%Y-%m-%d')
            },
            'current_data': {
                'date': latest.name.strftime('%Y-%m-%d'),
                'close_price': close_price,
                'macd': macd_value,
                'signal': signal_value,
                'diff': diff_value
            },
            'status': current_status,
            'signals': signals,
            'recommendation': recommendation,
            'raw_data': df
        }
        
    except Exception as e:
        error_msg = f"分析 {symbol} 时出错: {str(e)}"
        if verbose:
            print(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'symbol': symbol
        }

def analyze_multiple_stocks(symbols, days=90, interval="1d", verbose=True):
    """
    批量分析多个股票
    
    参数:
    symbols (list): 股票代码列表
    days (int): 分析的天数，默认90天
    interval (str): 数据间隔，默认"1d"
    verbose (bool): 是否打印详细信息，默认True
    
    返回:
    list: 每个股票的分析结果列表
    """
    results = []
    
    for symbol in symbols:
        if verbose:
            print(f"\n{'='*60}")
            print(f"正在分析 {symbol}")
            print(f"{'='*60}")
        
        result = analyze_stock(symbol, days, interval, verbose)
        results.append(result)
        
        if verbose:
            print(f"{symbol} 分析完成")
    
    return results

def run_demo():
    # 单个股票分析
    print("=== 单个股票分析示例 ===")
    result = analyze_stock("NVDA", days=90, verbose=True)
    
    # 批量分析示例
    print("\n\n=== 批量股票分析示例 ===")
    symbols = ["AAPL", "TSLA", "MSFT"]
    results = analyze_multiple_stocks(symbols, days=60, verbose=False)
    
    # 打印批量分析摘要
    print("\n批量分析摘要:")
    print("="*80)
    print(f"{'股票代码':<10} | {'状态':<8} | {'收盘价':<10} | {'MACD':<10} | {'趋势':<15} | {'建议':<20}")
    print("-"*80)
    
    for result in results:
        if result['success']:
            symbol = result['symbol']
            status = "成功"
            close_price = f"${result['current_data']['close_price']:.2f}" if result['current_data']['close_price'] else "N/A"
            macd = f"{result['current_data']['macd']:.3f}" if result['current_data']['macd'] else "N/A"
            trend = result['status']['trend']
            recommendation = result['recommendation'][:20] + "..." if len(result['recommendation']) > 20 else result['recommendation']
        else:
            symbol = result['symbol']
            status = "失败"
            close_price = macd = trend = recommendation = "N/A"
        print(f"{symbol:<10} | {status:<8} | {close_price:<10} | {macd:<10} | {trend:<15} | {recommendation:<20}")
    print("="*80)

if __name__ == "__main__":
    run_demo() 