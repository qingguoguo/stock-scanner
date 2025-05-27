import pandas as pd
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from utils.logger import get_logger

# 获取日志器
logger = get_logger()

class StockDataProvider:
    """
    异步股票数据提供服务
    负责获取股票、基金等金融产品的历史数据
    """
    
    def __init__(self):
        """初始化数据提供者服务"""
        logger.debug("初始化StockDataProvider")
    
    async def get_stock_data(self, stock_code: str, market_type: str = 'A', 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        异步获取股票或基金数据
        
        Args:
            stock_code: 股票代码
            market_type: 市场类型，默认为'A'股
            start_date: 开始日期，格式YYYYMMDD，默认为一年前
            end_date: 结束日期，格式YYYYMMDD，默认为今天
            
        Returns:
            包含历史数据的DataFrame
        """
        # 使用线程池执行同步的akshare调用
        return await asyncio.to_thread(
            self._get_stock_data_sync, 
            stock_code, 
            market_type, 
            start_date, 
            end_date
        )
    
    def _get_stock_data_sync(self, stock_code: str, market_type: str = 'A', 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> pd.DataFrame:
        """
        同步获取股票数据的实现
        将被异步方法调用
        """
        import akshare as ak
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        # 确保日期格式统一（移除可能的'-'符号）
        if isinstance(start_date, str) and '-' in start_date:
            start_date = start_date.replace('-', '')
        if isinstance(end_date, str) and '-' in end_date:
            end_date = end_date.replace('-', '')
            
        # 🔍 添加详细的请求日志
        logger.info(f"🔍 [AKSHARE请求] 开始获取股票数据")
        logger.info(f"📊 [AKSHARE请求] 股票代码: {stock_code}, 市场: {market_type}")
        logger.info(f"📅 [AKSHARE请求] 请求日期范围: {start_date} 到 {end_date}")
        logger.info(f"🕐 [AKSHARE请求] 当前系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            if market_type == 'A':
                logger.info(f"📈 [AKSHARE-A股] 调用 ak.stock_zh_a_hist(symbol={stock_code}, start_date={start_date}, end_date={end_date}, adjust='qfq')")
                
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
                # 🔍 添加A股原始数据日志
                logger.info(f"📊 [AKSHARE-A股] 原始数据形状: {df.shape}")
                logger.info(f"📋 [AKSHARE-A股] 原始列名: {df.columns.tolist()}")
                
                if not df.empty:
                    logger.info(f"✅ [AKSHARE-A股] 数据获取成功")
                    logger.info(f"🔍 [AKSHARE-A股] 原始索引类型: {type(df.index)}")
                    logger.info(f"📅 [AKSHARE-A股] 原始索引范围: {df.index[0]} 到 {df.index[-1]}")
                    
                    # 显示原始数据样本
                    logger.info(f"📋 [AKSHARE-A股] 最新3行原始数据:")
                    for i, (idx, row) in enumerate(df.tail(3).iterrows()):
                        logger.info(f"   第{i+1}行: 日期={idx}, 收盘={row.get('收盘', 'N/A')}, 涨跌幅={row.get('涨跌幅', 'N/A')}")
                else:
                    logger.warning(f"⚠️  [AKSHARE-A股] 获取到空数据，可能原因：股票代码不存在、停牌、或数据源问题")
                    # 直接返回空DataFrame，避免后续处理错误
                    return pd.DataFrame()
                
            elif market_type in ['HK']:
                logger.info(f"📈 [AKSHARE-港股] 调用 ak.stock_hk_daily(symbol={stock_code}, adjust='qfq')")
                df = ak.stock_hk_daily(
                    symbol=stock_code,
                    adjust="qfq"
                )
                
                # 🔍 添加港股原始数据日志
                logger.info(f"📊 [AKSHARE-港股] 原始数据形状: {df.shape}")
                logger.info(f"📋 [AKSHARE-港股] 原始列名: {df.columns.tolist()}")
                
                if not df.empty:
                    logger.info(f"✅ [AKSHARE-港股] 数据获取成功")
                    logger.info(f"🔍 [AKSHARE-港股] 原始索引类型: {type(df.index)}")
                    
                    # 🔧 修复港股日期索引问题
                    if 'date' in df.columns:
                        logger.info(f"🔧 [AKSHARE-港股] 发现date列，准备设置为索引")
                        # 显示原始date列的样本
                        logger.info(f"📅 [AKSHARE-港股] 原始date列样本: {df['date'].tail(3).tolist()}")
                        
                        # 将date列转换为日期时间类型并设为索引
                        df['date'] = pd.to_datetime(df['date'])
                        df.set_index('date', inplace=True)
                        logger.info(f"🔧 [AKSHARE-港股] 已将date列设置为索引")
                        logger.info(f"📅 [AKSHARE-港股] 日期索引范围: {df.index.min()} 到 {df.index.max()}")
                        
                        # 显示处理后的数据样本
                        logger.info(f"📋 [AKSHARE-港股] 最新3行数据（已设置日期索引）:")
                        for i, (idx, row) in enumerate(df.tail(3).iterrows()):
                            close_val = row.get('close', 'N/A')
                            date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
                            logger.info(f"   第{i+1}行: 日期={date_str}, 收盘={close_val}")
                    else:
                        logger.warning(f"⚠️  [AKSHARE-港股] 未找到date列，使用数字索引")
                        logger.info(f"📅 [AKSHARE-港股] 数字索引范围: {df.index.min()} 到 {df.index.max()}")
                else:
                    logger.warning(f"⚠️  [AKSHARE-港股] 获取到空数据")
                    return pd.DataFrame()
                
                # 在获取数据后进行日期过滤（如果已经设置了日期索引）
                if isinstance(df.index, pd.DatetimeIndex):
                    try:
                        # 转换日期字符串为日期对象
                        if start_date.isdigit() and len(start_date) == 8:
                            start_date_dt = pd.to_datetime(start_date, format='%Y%m%d')
                        else:
                            start_date_dt = pd.to_datetime(start_date)
                            
                        if end_date.isdigit() and len(end_date) == 8:
                            end_date_dt = pd.to_datetime(end_date, format='%Y%m%d')
                        else:
                            end_date_dt = pd.to_datetime(end_date)
                        
                        # 过滤日期范围
                        original_len = len(df)
                        df = df[(df.index >= start_date_dt) & (df.index <= end_date_dt)]
                        logger.info(f"🔧 [AKSHARE-港股] 日期过滤: {original_len} -> {len(df)} 条记录")
                        
                    except Exception as e:
                        logger.warning(f"⚠️  [AKSHARE-港股] 日期过滤出错: {str(e)}，使用原始数据")
                
            elif market_type in ['US']:
                logger.info(f"📈 [AKSHARE-美股] 调用 ak.stock_us_daily(symbol={stock_code}, adjust='qfq')")
                try:
                    df = ak.stock_us_daily(
                        symbol=stock_code,
                        adjust="qfq"
                    )
                    
                    # 🔍 添加美股原始数据日志
                    if not df.empty:
                        logger.info(f"✅ [AKSHARE-美股] 数据获取成功，原始数据形状: {df.shape}")
                        logger.info(f"📋 [AKSHARE-美股] 原始列名: {df.columns.tolist()}")
                        logger.info(f"🔍 [AKSHARE-美股] 原始索引类型: {type(df.index)}")
                        if hasattr(df.index, 'min') and hasattr(df.index, 'max'):
                            logger.info(f"📅 [AKSHARE-美股] 原始索引范围: {df.index.min()} 到 {df.index.max()}")
                    else:
                        logger.warning(f"⚠️  [AKSHARE-美股] 获取到空数据")
                    
                    # 计算美股的成交额（Amount）= 成交量（Volume）× 收盘价（Close）
                    volume_col = next((col for col in df.columns if col.lower() == 'volume'), None)
                    close_col = next((col for col in df.columns if col.lower() == 'close'), None)
                    
                    if volume_col and close_col:
                        df['amount'] = df[volume_col] * df[close_col]
                        logger.debug("已为美股数据计算成交额(amount)字段")
                    else:
                        logger.warning(f"美股数据缺少volume或close列，无法计算amount。当前列: {df.columns.tolist()}")
                        # 添加空的amount列，避免后续处理错误
                        df['amount'] = 0.0
                        
                    # 将所有列名转为小写以进行统一处理
                    df.columns = [col.lower() for col in df.columns]
                    
                except Exception as e:
                    logger.error(f"获取美股数据失败 {stock_code}: {str(e)}")
                    raise ValueError(f"获取美股数据失败 {stock_code}: {str(e)}")
                
                # 将字符串日期转换为日期时间对象进行比较
                try:
                    # 尝试多种格式解析日期
                    # 如果日期是数字格式（20220101），使用适当的格式
                    if start_date.isdigit() and len(start_date) == 8:
                        start_date_dt = pd.to_datetime(start_date, format='%Y%m%d')
                    else:
                        # 否则让pandas自动推断格式
                        start_date_dt = pd.to_datetime(start_date)
                        
                    if end_date.isdigit() and len(end_date) == 8:
                        end_date_dt = pd.to_datetime(end_date, format='%Y%m%d')
                    else:
                        end_date_dt = pd.to_datetime(end_date)
                except Exception as e:
                    logger.warning(f"日期转换出错: {str(e)}，使用默认值")
                    # 如果转换失败，使用合理的默认值
                    start_date_dt = pd.to_datetime('20000101', format='%Y%m%d')
                    end_date_dt = pd.to_datetime(datetime.now().strftime('%Y%m%d'), format='%Y%m%d')
                
                # 过滤日期
                try:
                    df = df[(df.index >= start_date_dt) & (df.index <= end_date_dt)]
                    logger.debug(f"日期过滤后数据点数: {len(df)}")
                except Exception as e:
                    logger.warning(f"日期过滤出错: {str(e)}，返回原始数据")
                    
            elif market_type in ['ETF']:
                logger.info(f"📈 [AKSHARE-ETF] 调用 ak.fund_etf_hist_em(symbol={stock_code}, start_date={start_date}, end_date={end_date})")
                df = ak.fund_etf_hist_em(
                    symbol=stock_code,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', '')
                )
                
                logger.info(f"📊 [AKSHARE-ETF] 原始数据形状: {df.shape}")
                logger.info(f"📋 [AKSHARE-ETF] 原始列名: {df.columns.tolist()}")
                
                if not df.empty:
                    logger.info(f"✅ [AKSHARE-ETF] 数据获取成功")
                else:
                    logger.warning(f"⚠️  [AKSHARE-ETF] 获取到空数据")
                    return pd.DataFrame()
                
            elif market_type in ['LOF']:
                logger.debug(f"获取{market_type}基金数据: {stock_code}")
                df = ak.fund_lof_hist_em(
                    symbol=stock_code,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', '')
                )
                
            else:
                error_msg = f"不支持的市场类型: {market_type}"
                logger.error(f"[市场类型错误] {error_msg}")
                raise ValueError(error_msg)
                
            # 🔍 检查数据是否为空
            if df.empty:
                logger.warning(f"⚠️  [数据为空] {market_type}数据为空，跳过标准化处理")
                return df
                
            # 🔍 数据标准化前的日志
            logger.info(f"🔧 [数据标准化] 开始标准化列名，当前数据形状: {df.shape}")
            logger.info(f"🔧 [数据标准化] 当前列名: {df.columns.tolist()}")
                
            # 标准化列名
            if market_type == 'A':
                # 检查列数是否匹配
                expected_columns = ['Date', 'Code', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_pct', 'Change', 'Turnover']
                if len(df.columns) != len(expected_columns):
                    logger.error(f"❌ [列数不匹配] A股数据列数 {len(df.columns)} 不等于期望列数 {len(expected_columns)}")
                    logger.error(f"❌ [列数不匹配] 实际列名: {df.columns.tolist()}")
                    logger.error(f"❌ [列数不匹配] 期望列名: {expected_columns}")
                    # 返回空DataFrame避免错误
                    return pd.DataFrame()
                
                original_columns = df.columns.tolist()
                df.columns = expected_columns
                logger.info(f"🔧 [数据标准化-A股] 列名映射: {dict(zip(original_columns, df.columns))}")
                
            elif market_type in ['HK', 'US']:
                # 港股/美股数据列映射处理
                columns_mapping = {
                    'open': 'Open',
                    'high': 'High', 
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume',
                    'amount': 'Amount'
                }
                
                # 创建新的DataFrame以确保列顺序和存在性
                new_df = pd.DataFrame(index=df.index)
                
                # 遍历映射，填充新DataFrame
                for orig_col, new_col in columns_mapping.items():
                    if orig_col in df.columns:
                        new_df[new_col] = df[orig_col]
                        logger.info(f"🔧 [数据标准化-{market_type}] 映射列: {orig_col} -> {new_col}")
                    else:
                        # 如果原始列不存在，创建一个填充0的列
                        logger.warning(f"⚠️  [数据标准化-{market_type}] 缺少{orig_col}列，使用0值填充")
                        new_df[new_col] = 0.0
                
                # 替换原始df
                df = new_df
                logger.info(f"🔧 [数据标准化-{market_type}] 列名标准化完成")
                
            elif market_type in ['ETF', 'LOF']:
                # 检查列数是否匹配
                expected_columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'Change_pct', 'Change', 'Turnover']
                if len(df.columns) != len(expected_columns):
                    logger.error(f"❌ [列数不匹配] {market_type}数据列数 {len(df.columns)} 不等于期望列数 {len(expected_columns)}")
                    logger.error(f"❌ [列数不匹配] 实际列名: {df.columns.tolist()}")
                    logger.error(f"❌ [列数不匹配] 期望列名: {expected_columns}")
                    # 返回空DataFrame避免错误
                    return pd.DataFrame()
                
                original_columns = df.columns.tolist()
                df.columns = expected_columns
                logger.info(f"🔧 [数据标准化-{market_type}] 列名映射: {dict(zip(original_columns, df.columns))}")
                
            # 确保日期列是日期类型
            if market_type in ['A', 'ETF', 'LOF'] and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                logger.info(f"🔧 [数据标准化] 已将Date列设置为索引")
            elif market_type in ['HK', 'US']:
                # 港股和美股已经在前面处理了日期索引
                logger.info(f"🔧 [数据标准化] {market_type}数据日期索引已处理")
                
            # 确保按日期升序排序
            df.sort_index(inplace=True)
                
            # 🔍 最终数据验证日志
            if not df.empty:
                # 获取最新数据信息
                if isinstance(df.index, pd.DatetimeIndex):
                    latest_date = df.index[-1]
                    latest_date_str = latest_date.strftime('%Y-%m-%d')
                    is_date_index = True
                else:
                    latest_date = df.index[-1]
                    latest_date_str = str(latest_date)
                    is_date_index = False
                
                latest_close = df.iloc[-1]['Close'] if 'Close' in df.columns else 'N/A'
                latest_change_pct = df.iloc[-1].get('Change_pct', 'N/A')
                
                logger.info(f"✅ [数据验证] 数据处理完成")
                logger.info(f"📊 [数据验证] 最终数据形状: {df.shape}")
                logger.info(f"📋 [数据验证] 最终列名: {df.columns.tolist()}")
                logger.info(f"📅 [数据验证] 最新数据日期: {latest_date_str}")
                logger.info(f"💰 [数据验证] 最新收盘价: {latest_close}")
                logger.info(f"📈 [数据验证] 最新涨跌幅: {latest_change_pct}")
                logger.info(f"🔍 [数据验证] 索引类型: {'日期索引' if is_date_index else '数字索引'}")
                
                # 🔍 日期异常检查（仅对日期索引进行检查）
                if is_date_index:
                    current_date = datetime.now().date()
                    if hasattr(latest_date, 'date'):
                        latest_date_obj = latest_date.date()
                    else:
                        latest_date_obj = pd.to_datetime(latest_date).date()
                        
                    days_diff = (latest_date_obj - current_date).days
                    if days_diff > 0:
                        logger.warning(f"⚠️  [日期异常] 最新数据日期 {latest_date_obj} 超前于当前日期 {current_date} {days_diff} 天")
                    elif days_diff < -7:
                        logger.warning(f"⚠️  [日期异常] 最新数据日期 {latest_date_obj} 滞后于当前日期 {current_date} {abs(days_diff)} 天")
                    else:
                        logger.info(f"✅ [日期验证] 数据日期正常，距离当前日期 {abs(days_diff)} 天")
                else:
                    logger.info(f"ℹ️  [日期验证] 使用数字索引，跳过日期验证")
                
                # 🔍 显示最近几天的数据
                logger.info(f"📋 [数据样本] 最近3天数据:")
                recent_data = df.tail(3)
                for i, (idx, row) in enumerate(recent_data.iterrows()):
                    if is_date_index:
                        date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
                    else:
                        date_str = str(idx)
                    close_price = row.get('Close', 'N/A')
                    change_pct = row.get('Change_pct', 'N/A')
                    logger.info(f"   第{i+1}天: {date_str}, 收盘={close_price}, 涨跌幅={change_pct}%")

            logger.info(f"✅ [AKSHARE完成] 成功获取{market_type}数据 {stock_code}, 数据点数: {len(df)}")
            return df
            
        except Exception as e:
            error_msg = f"获取{market_type}数据失败 {stock_code}: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            # 使用空的DataFrame并添加错误信息，而不是抛出异常
            # 这样上层调用者可以检查是否有错误并适当处理
            df = pd.DataFrame()
            df.error = error_msg  # 添加错误属性
            return df
            
    async def get_multiple_stocks_data(self, stock_codes: List[str], 
                                     market_type: str = 'A',
                                     start_date: Optional[str] = None, 
                                     end_date: Optional[str] = None,
                                     max_concurrency: int = 5) -> Dict[str, pd.DataFrame]:
        """
        异步批量获取多只股票数据
        
        Args:
            stock_codes: 股票代码列表
            market_type: 市场类型，默认为'A'股
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            max_concurrency: 最大并发数，默认为5
            
        Returns:
            字典，键为股票代码，值为对应的DataFrame
        """
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def get_with_semaphore(code):
            async with semaphore:
                try:
                    return code, await self.get_stock_data(code, market_type, start_date, end_date)
                except Exception as e:
                    logger.error(f"获取股票 {code} 数据时出错: {str(e)}")
                    return code, None
        
        # 创建异步任务
        tasks = [get_with_semaphore(code) for code in stock_codes]
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        # 构建结果字典，过滤掉失败的请求
        return {code: df for code, df in results if df is not None}