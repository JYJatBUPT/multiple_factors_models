# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 21:48:18 2018

@author: wuwangchuxin
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import math
#import matplotlib.pyplot as plt
import os
os.chdir('D:/multiple_factors_models/')
#import date_process_class as dpc
from scipy import stats as ss
import matplotlib.pyplot as plt

# 添加路径，方便导入自定义模块，比如 import date_process_class as dpc
import sys
sys.path.append('D:/multiple_factors_models')

from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

add_winddata = 'C:/Users/wuwangchuxin/Desktop/TF_SummerIntern/MF_data/wind/'
add_ready = 'C:/Users/wuwangchuxin/Desktop/TF_SummerIntern/MF_data/prepared_data/del_cixin/'
add_pic = 'C:/Users/wuwangchuxin/Desktop/TF_SummerIntern/20190326pic/'

# load data
##################################################################################
## 估值指标
#pe = np.load(add_ready+'windfactors_pe.npy')
ep = np.load(add_ready+'windfactors_ep.npy')
#pb = np.load(add_ready+'windfactors_pb.npy')
bp = np.load(add_ready+'windfactors_bp.npy')
#ps = np.load(add_ready+'windfactors_ps.npy')
sp = np.load(add_ready+'windfactors_sp.npy')
pcf_ocf = np.load(add_ready+'windfactors_pcf_ocf.npy') #市现率
dividendyield = np.load(add_ready+'windfactors_dividendyield.npy') #股息率
evtoebitda = np.load(add_ready+'windfactors_evtoebitda.npy')  #企业倍数

#盈利能力
roe = np.load(add_ready+'windfactors_roe.npy') #净资产收益率（TTM）
roa = np.load(add_ready+'windfactors_roaebit.npy') #总资产收益率（TTM）
roic = np.load(add_ready+'windfactors_roicebit.npy') #投入资本回报率ROIC(TTM)
gpmgr = np.load(add_ready+'windfactors_gpmgr.npy') #增长率_毛利率(TTM)
grossprofitmargin = np.load(add_ready+'windfactors_grossprofitmargin.npy') #销售毛利率(TTM)
orgr = np.load(add_ready+'windfactors_orgr.npy') #增长率_营业收入(TTM)
cfogr = np.load(add_ready+'windfactors_cfogr.npy') #增长率_经营活动产生的现金流量净额(TTM)
#经营效率
invturn = np.load(add_ready+'windfactors_invturn.npy') #存货周转率(TTM)
arturn = np.load(add_ready+'windfactors_arturn.npy') #应收账款周转率(TTM)
taturn = np.load(add_ready+'windfactors_taturn.npy') #总资产周转率(TTM)
#盈余质量
profittomv = np.load(add_ready+'windfactors_profittomv.npy') #收益市值比(TTM)
#投融资决策
tagr = np.load(add_ready+'windfactors_tagr.npy') #增长率-总资产
#无形资产
stmnote_RDexptosales = np.load(add_ready+'windfactors_stmnote_RDexptosales.npy') #研发支出总额占营业收入比例
#杠杆因子
debttoasset = np.load(add_ready+'windfactors_debttoasset.npy') #资产负债率
current = np.load(add_ready+'windfactors_current.npy') #流动比率

#利用市场信号修正策略
#市场参与者行为
netprofit_fy1_6m = np.load(add_ready+'windfactors_netprofit_fy1_6m.npy') #一致预测净利润（FY1）的变化率_6M
#市场价格信号
revs60 = np.load(add_ready+'windfactors_revs60.npy') #过去3个月的价格动量
#市场情绪信号
rstr12 = np.load(add_ready+'windfactors_rstr12.npy') #12月相对强势

#其它指标
#float_mv = np.load(add_ready+'wind_float_mv.npy') #流动市值
#
#return_month = np.load(add_ready+'wind_return_month.npy') #月收益率
#
#stockcode = np.load(add_ready+'stockscode.npy').reshape(-1,1) #股票代码
#trade_date = np.load(add_ready+'month_end_tdate.npy').reshape(1,-1) #月末交易日
#
#industry_sw1 = np.load(add_ready+'industry_sw1.npy') #申万一级行业哑变量
#industry_sw1_name = np.load(add_ready+'industry_sw1_name.npy').reshape(1,-1) #申万一级行业分类名称
##industry = pd.read_excel(add_winddata+'industry_sw1_class.xlsx')  #原始数据
#
#start_date = np.load(add_ready+'stock_tdate_start.npy').reshape(-1,1) #个股有效期起始时间
#end_date = np.load(add_ready+'stock_tdate_end.npy').reshape(-1,1) #个股有效期终止时间
# 
#weights_000300 = np.load(add_ready+'weights_000300.npy') #沪深300指数个股权重
#weights_000300_stocklist = np.load(add_ready+'weights_000300_stocklist.npy')
#
#hs300_sw_1class_weight = np.load(add_ready+'hs300_sw_1class_weight') #沪深300指数申万一级行业分类权重
#hs300_sw_1class_weight_industrynames = np.save(add_ready+'hs300_sw_1class_weight_industrynames')
##################################################################################

class Clean_Data:
    #数据格式：ndarray，3225*115,3225只个股，115个月
    def __init__(self,arr):
        self.arr=arr
        self.trade_date = np.load(add_ready+'matcol_month_end_tdate.npy').reshape(1,-1) #月末交易日
        self.start_date = np.load(add_ready+'stock_tdate_start.npy').reshape(-1,1) #个股有效期起始时间
        self.end_date = np.load(add_ready+'stock_tdate_end.npy').reshape(-1,1) #个股有效期终止时间
    
    def Median_deextremum(self,n=5):
        '''中位数去极值法'''
        med = np.nanmedian(self.arr,axis=0)
        mad = np.nanmedian(np.abs(self.arr - med),axis=0)
        res = np.where(self.arr>(med+n*mad),(med+n*mad),
                       np.where(self.arr<(med-n*mad),(med-n*mad),self.arr))
        return res

    def Ordinal_values(self):
        # 求数据集的排序值
        # argsort 不能忽略nan值
        res = self.arr.copy()
        not_nan_num = np.sum(~np.isnan(self.arr),axis=0) #非空值数量
        #将nan值赋值为大数字然后排序
        mid = np.argsort(np.where(np.isnan(self.arr),99999,self.arr),axis=0) 
        #末尾插入一列递增数列，作为名次标记
        mid2 = np.insert(mid,mid.shape[1],values=np.arange(1,mid.shape[0]+1),axis=1) 
        # 逐列进行计算
        for n in np.arange(self.arr.shape[1]):
            mid_tmp = mid2[:,[n,self.arr.shape[1]]] #当前列和标记列，即所在列的位置和排名
            #第一列排序，其位置归位，标记列为排名。得到原来所在位置的元素在所在列的排名
            mid_tmp2 = mid_tmp[mid_tmp[:,0].argsort(axis=0)][:,1]
            #恢复为空值的列
            mid_tmp3 = np.where(mid_tmp2>=not_nan_num[n]+1,np.nan,mid_tmp2)
            res[:,n] = mid_tmp3
        return res

    def Z_score(self):
        '''z_score标准化'''
        return (self.arr - np.nanmean(self.arr))/np.nanstd(self.arr)
    
    def Fill_na(self):
        '''将本来应该有但是却为nan值的位置填充为0'''
        mid = np.where((self.trade_date>=self.start_date) & (self.trade_date<=self.end_date),
                       self.arr,99999)
        res = np.where(np.isnan(mid),0,self.arr)
        return res
    
    @staticmethod
    def Round_df(df_factor):
        return df_factor.applymap(lambda x:'%.4f'%x)

class Single_factors_test_regression:
    '''单因子测试之回归法'''
    def __init__(self,factor_arr):
        def Data_preposs(f_arr):
            '''完整的数据预处理流程'''
            f_a1 = Clean_Data(f_arr).Median_deextremum()
            f_a2 = Clean_Data(f_a1).Z_score()
            f_a3 = Clean_Data(f_a2).Fill_na()
            f_a4 = np.around(f_a3,decimals=4)
            return f_a4
        self.factor_arr=Data_preposs(factor_arr) #3171*115
        self.industry_sw1 = np.load(add_ready+'industry_sw1.npy') #3171*28
        self.float_mv = np.load(add_ready+'wind_float_mv.npy') #3171*115
        r_month = np.load(add_ready+'wind_return_month.npy')
        self.return_month = Data_preposs(r_month) #月收益率 #3171*115
        self.trade_date = np.load(add_ready+'matcol_month_end_tdate.npy').reshape(1,-1) #月末交易日 115
    
    @staticmethod
    def OLS_regression(x,y):
        # 普通最小二乘法回归
        X = sm.add_constant(x)
        regr = sm.OLS(y, X).fit() #regr.resid,残差；regr.params，beta值;regr.tvalues,T值
        return regr
    
    @staticmethod
    def WLS_regression(x,y,w):
        #加权最小二乘法回归
        #w=data.iloc[:,2].tolist()
        #w=np.array([i**0.5 for i in w])
        X = sm.add_constant(x)
        regr = sm.WLS(y,X,weights=w).fit()
        #results.tvalues T值 regr.resid,残差；regr.params，beta值;results.t_test([1,0])
        return regr

    def single_factor_regress(self):
        ''' 单因子回归，包含OLS和WLS回归，回归自变量加入申万一级行业哑变量，WLS以流通市值的平方根作为权值'''
        res_regr=pd.DataFrame(index=np.arange(self.factor_arr.shape[1]-1),
                              columns=['trade_month','Beta_OLS','Tvalue_OLS',
                                       'Beta_WLS','Tvalue_WLS','IC','RANKIC'])
        for n in np.arange(self.factor_arr.shape[1]-1):
            #剔除空值
            nona_index = (~np.isnan(self.factor_arr[:,n])) & (~np.isnan(self.return_month[:,n+1]))
            factor_arr_nona = self.factor_arr[nona_index,n][:,np.newaxis]
            return_month_nona = self.return_month[nona_index,n+1][:,np.newaxis]
            industry_sw1_nona = self.industry_sw1[nona_index,:]
            X = np.hstack((industry_sw1_nona,factor_arr_nona))
            #OLS
            res_ols = self.OLS_regression(X,return_month_nona)
            #WLS
            w=self.float_mv[:,n][nona_index]
            w = np.where(np.isnan(w),np.nanmean(w),w) #用均值填充nan值
            w=np.array([i**0.5 for i in w])
            res_wls = self.WLS_regression(X,return_month_nona,w)
            # IC,先用因子值对行业和市值回归取残差，然后再和次月收益求IC
            float_mv_nona = self.float_mv[nona_index,n][:,np.newaxis]
            float_mv_nona=np.where(np.isnan(float_mv_nona),np.nanmean(float_mv_nona),float_mv_nona)
            X_IC = np.hstack((industry_sw1_nona,float_mv_nona))
            res_ols_IC = self.OLS_regression(X_IC,factor_arr_nona)
            mid_ic = np.corrcoef(res_ols_IC.resid,return_month_nona[:,0])[0,1]
            # RANKIC，同IC值，先取残差再求值
            rank_ic = pd.DataFrame([res_ols_IC.resid,
                                    return_month_nona[:,0]]).T.corr('spearman').iloc[0,1]
            #结果
            res_regr.iloc[n,:] = [self.trade_date[0,n],res_ols.params[-1],res_ols.tvalues[-1],
                                  res_wls.params[-1],res_wls.tvalues[-1],mid_ic,rank_ic]
        return res_regr
    
    @staticmethod
    def T_analysis(regress_df):
        # T abs mean
        T_res = pd.DataFrame(index=['OLS','WLS'],
                              columns=['t_abs_mean','port_greater_2','beta_mean',
                                       'beta_t','t_mean_div_std'])
        L1 = ['Tvalue_OLS','Tvalue_WLS']
        for col1 in L1:
            t_abs_mean = np.mean(regress_df[col1].apply(lambda x:abs(x)))
            port_greater_2 = np.sum(regress_df[col1].apply(lambda x:abs(x))>2)/len(regress_df[col1])
#            t_mean_div_std = t_abs_mean/np.std(regress_df[col1].apply(lambda x:abs(x)))
            t_mean_div_std = abs(np.mean(regress_df[col1]))/np.std(regress_df[col1])
            T_res.loc[col1[-3:],'t_abs_mean'] = t_abs_mean
            T_res.loc[col1[-3:],'port_greater_2'] = port_greater_2
            T_res.loc[col1[-3:],'t_mean_div_std'] = t_mean_div_std
            
        L2 = ['Beta_OLS','Beta_WLS']
        for col2 in L2:
            beta_mean = np.mean(regress_df[col2])
            beta_t = ss.ttest_1samp(regress_df[col2], popmean = 0)[0]
            T_res.loc[col2[-3:],'beta_mean'] = beta_mean
            T_res.loc[col2[-3:],'beta_t'] = beta_t 
        return T_res
    
    @staticmethod        
    def IC_analysis(regress_df):
        IC_res=pd.DataFrame(index=['fac'],columns=['IC_mean','IC_std','IC_IR','IC_positive_port',
                            'RANKIC_mean','RANKIC_std','RANKIC_IR','RANKIC_positive_port'])
        IC_mean = regress_df['IC'].mean()
        IC_std = regress_df['IC'].std()
        IC_IR = IC_mean/IC_std
        IC_positive_port = np.sum(regress_df['IC']>0)/len(regress_df['IC'])
        
        RANKIC_mean = regress_df['RANKIC'].mean()
        RANKIC_std = regress_df['RANKIC'].std()
        RANKIC_IR = RANKIC_mean/RANKIC_std
        RANKIC_positive_port = np.sum(regress_df['RANKIC']>0)/len(regress_df['RANKIC'])        
        
        IC_res.loc['fac',:] = IC_mean,IC_std,IC_IR,IC_positive_port,RANKIC_mean,RANKIC_std,RANKIC_IR,RANKIC_positive_port
        return IC_res
    
    @staticmethod
    def Style_rotation(regress_df):
        '''风格因子显著性正负和方向转换统计'''
        SR_res = pd.DataFrame(index=['OLS','WLS'],
                              columns=['pos_cor_sig_port','neg_cor_sig_port',
                                       'syn_sig_port','exch_sig_port'])
        L3 = ['Tvalue_OLS','Tvalue_WLS']
        for col3 in L3:
            pos_port = sum(regress_df[col3]>2)/len(regress_df[col3])
            neg_port = sum(regress_df[col3]<-2)/len(regress_df[col3])
            SR_res.loc[col3[-3:],'pos_cor_sig_port'] = pos_port
            SR_res.loc[col3[-3:],'neg_cor_sig_port'] = neg_port
            
            mid_Tvalues = regress_df[np.logical_or(regress_df[col3]>2,regress_df[col3]<-2)]
            mid_Tvalues.reset_index(drop=True,inplace=True)
            syn_sig_num=0
            exch_sig_num=0
            for mid_index in range(1,mid_Tvalues.shape[0]):
                # 同向
                if mid_Tvalues.loc[mid_index,col3]*mid_Tvalues.loc[mid_index-1,col3]>0:
                    syn_sig_num+=1
                else:
                    exch_sig_num+=1
            SR_res.loc[col3[-3:],'syn_sig_port'] = syn_sig_num/(len(regress_df[col3])-1)
            SR_res.loc[col3[-3:],'exch_sig_port'] = exch_sig_num/(len(regress_df[col3])-1)      
        return SR_res

class Single_factors_test_group:
    '''单因子测试之分组法
       数据格式：ndarray，3225*115,3225只个股，115个月 self=Single_factors_test_group(ep)'''
    capital_initial = 100000000
    def __init__(self,factor_arr):
        self.factor_arr=factor_arr
        self.return_month = np.load(add_ready+'wind_return_month.npy') #月收益率
        self.trade_date = np.load(add_ready+'matcol_month_end_tdate.npy')#.reshape(1,-1) #月末交易日
        self.industry = pd.read_excel(add_winddata+'industry_sw1_class.xlsx')
        self.stockcode = np.load(add_ready+'matind_stockscode.npy')#.reshape(-1,1) #股票代码
        self.hs300_sw_1class_weight = np.load(add_ready+'hs300_sw_1class_weight.npy') #沪深300指数申万一级行业分类权重
        self.industrynames = np.load(add_ready+'hs300_sw_1class_weight_industrynames.npy')
        self.hs300_mkt = pd.read_csv(add_winddata+'market_data_hs300.csv')
        self.zz500_mkt = pd.read_csv(add_winddata+'market_data_zz500.csv')
        self.szzz_mkt = pd.read_csv(add_winddata+'market_data_szzz.csv')
        
    def group_net_value(self):
        '''行业中性分组，行业所占权重和hs300相同，行业内个股等权重；
           按单因子值排序分五组构建投资组合，因此每个中性分组的权重之和都是20%
           并构建多空组合，添加沪深300和中证500指数作为比较'''
        # hs300指数申万一级行业分类权重
        industry_w_df=pd.DataFrame(self.hs300_sw_1class_weight,index=self.industrynames,
                                  columns= self.trade_date)
        industry_w_df.fillna(0,inplace=True)
                                 
        factor_df = pd.DataFrame(self.factor_arr,index=self.stockcode,columns=self.trade_date) 
        return_month_df = pd.DataFrame(self.return_month,index=self.stockcode,columns=self.trade_date)
        #资金变化结果df
        capital_df = pd.DataFrame(index = self.trade_date,
                                   columns=['group1','group2','group3','group4','group5']) 
        capital_df.iloc[0,:]=self.capital_initial
        for n in range(len(factor_df.columns)-1):
            mid_df=pd.merge(factor_df[[factor_df.columns[n]]],
                        return_month_df[[factor_df.columns[n+1]]],
                        left_index=True,right_index=True)
            mid_df = pd.merge(mid_df,self.industry,left_index=True,right_on='code',how='inner')
            mid_df.rename(columns={factor_df.columns[n]:'factor',
                                   factor_df.columns[n+1]:'return_month'},inplace = True)
            mid_df.dropna(inplace=True)
            grouped =mid_df.groupby(by='industry_1class') #按行业分组
            grouped_df = pd.DataFrame(columns=['factor','return_month','group_NO','weight_stock'])
            #hs300指数申万一级行业中性分组，被分组隔断的个股权重按照比例分配
            for indus_name,value in grouped:
                base_weight_stock = industry_w_df.loc[indus_name][n]/value.shape[0]
                value.sort_values(by='factor',ascending=False,inplace=True) #因子倒序排列
                value.reset_index(drop=True,inplace=True)
                group_amount = value.shape[0]/5 #每组股票数量
                if group_amount>=1:
                    if int(group_amount)==group_amount:
                        for group_n in range(5):
                            mid_indus_group = value.loc[group_n*group_amount:(group_n+1)*group_amount-1,
                                                        ['factor','return_month']]
                            mid_indus_group['group_NO'] = group_n+1
                            mid_indus_group['weight_stock'] = base_weight_stock
                            grouped_df = grouped_df.append(mid_indus_group)
                    else:
                        for group_n in range(5):
                            int_start =  int(group_amount*group_n)
                            int_end = int(group_amount*(group_n+1))
                            dec_start = 1-math.modf(group_amount*group_n)[0]
                            dec_end = math.modf(group_amount*(group_n+1))[0]
                            if group_n==0:                        
                                mid_indus_group = value.loc[:int_end,['factor','return_month']]
                                mid_indus_group['group_NO'] = 1
                                # 正常的
                                mid_indus_group.loc[:int_end-1,'weight_stock']= base_weight_stock
                                # 最后一个分隔的
                                mid_indus_group.loc[int_end,'weight_stock']= base_weight_stock*dec_end
                                grouped_df = grouped_df.append(mid_indus_group)
                            elif group_n == 4:
                                mid_indus_group = value.loc[int_start:,['factor','return_month']]
                                mid_indus_group['group_NO'] = group_n+1
                                mid_indus_group.loc[int_start+1:,'weight_stock']= base_weight_stock
                                mid_indus_group.loc[int_start,'weight_stock']=base_weight_stock*dec_start
                                grouped_df = grouped_df.append(mid_indus_group)
                            else:
                                mid_indus_group = value.loc[int_start:int_end,['factor','return_month']]
                                mid_indus_group['group_NO'] = group_n+1
                                mid_indus_group['weight_stock'] = [x*base_weight_stock for x in 
                                              [dec_start]+[1]*(int_end-int_start-1)+[dec_end]]
                                grouped_df = grouped_df.append(mid_indus_group)
                else:
                    midl = [x*group_amount for x in range(1,6)]
                    for group_n in range(5):
                        int_start =  int(group_amount*group_n)
                        int_end = int(group_amount*(group_n+1))
                        dec_start = 1-math.modf(group_amount*group_n)[0]
                        dec_end = math.modf(group_amount*(group_n+1))[0]
                        if group_n==0:
                            mid_indus_group = pd.DataFrame(value.loc[0,['factor','return_month']]).T
                            mid_indus_group['group_NO'] = 1
                            mid_indus_group.loc[0,'weight_stock']= base_weight_stock*group_amount
                        elif group_n == 4:
                            mid_indus_group = pd.DataFrame(value[['factor','return_month']].iloc[-1,:]).T
                            mid_indus_group['group_NO'] = 5
                            mid_indus_group['weight_stock']= base_weight_stock*group_amount
                        else:
                            if int(midl[group_n])>int(midl[group_n-1]):
                                mid_indus_group = value.loc[int_start:int_end,['factor','return_month']]
                                mid_indus_group['group_NO'] = group_n+1
                                mid_indus_group['weight_stock'] = [x*base_weight_stock for x in 
                                                  [dec_start,dec_end]]
                            elif int(midl[group_n])==int(midl[group_n-1]):
                                mid_indus_group = pd.DataFrame(value.loc[int_start,['factor','return_month']]).T
                                mid_indus_group['group_NO'] = group_n+1
                                mid_indus_group['weight_stock'] = base_weight_stock*group_amount                               
                        grouped_df = grouped_df.append(mid_indus_group)
            grouped_df.reset_index(drop=True,inplace=True)
            #资金等权,即每个分组的资金都是1亿；因为每个分组的权重一样，所以总资金1亿每个分组2千万和每个分组1亿相同
            for group_num in range(5):
                grouped_indus = grouped_df[grouped_df['group_NO']==(group_num+1)]
                capital_df.iloc[n+1,group_num] = sum(capital_df.iloc[n,group_num]*(
                         grouped_indus['weight_stock']/grouped_indus['weight_stock'].sum())
                         *(1+grouped_indus['return_month']/100))
            print (n,'done')
        # 计算多空组合
        if capital_df.iloc[-1,0]>capital_df.iloc[-1,-1]:
            capital_df['long_short'] = capital_df['group1']-capital_df['group5']+self.capital_initial
        else:
            capital_df['long_short'] = capital_df['group5']-capital_df['group1']+self.capital_initial
        netvalue_df = capital_df/self.capital_initial
        # 加上基准  
        netvalue_df['hs300']=(self.hs300_mkt['chg']/100+1).cumprod().values/(self.hs300_mkt['chg'][0]/100+1)
#        netvalue_df['zz500']=(self.zz500_mkt['chg']/100+1).cumprod().values/(self.zz500_mkt['chg'][0]/100+1)
        netvalue_df['szzz']=(self.szzz_mkt['chg']/100+1).cumprod().values/(self.szzz_mkt['chg'][0]/100+1)        
        return netvalue_df
    
    @staticmethod
    def backtest_indicates(netvalue_df):
        #年化收益，最大回撤，sharp ratio
        return_monthly = (netvalue_df/netvalue_df.shift(1)-1).fillna(0)
        res = pd.DataFrame(columns=['annual_return','sharp_ratio','max_drawdown','volatility','win_rate'],
                           index = netvalue_df.columns)
        for column_name in netvalue_df.columns:
            mkt_series = netvalue_df[column_name]
            res.loc[column_name,'annual_return']=pow(mkt_series[-1],1/(9+7/12))-1 #年化收益
            res.loc[column_name,'sharp_ratio'] = \
              np.sqrt(12)*return_monthly[column_name].mean()/return_monthly[column_name].std() #sharp
            # 最大回撤
            Drawdown = []
            for nn in range(1,len(mkt_series)):
                max_s = max(mkt_series[:nn])
                if max_s>mkt_series[nn]:
                    DD = (max_s-mkt_series[nn])/max_s
                else:
                    DD = 0
                Drawdown.append(DD*100)
            res.loc[column_name,'max_drawdown']= max(Drawdown)
        res['volatility'] = np.sqrt(12)*return_monthly.std()*100 #波动率
        res['win_rate'] = (netvalue_df.iloc[1:] - netvalue_df.shift(1).iloc[1:]>0) \
                            .sum()/netvalue_df.iloc[1:].shape[0] #胜率
        return res.applymap(lambda x:'%.4f'%x)

    @staticmethod
    def draw(netvalue_df,pic_name):
#         画图
        ax1 = plt.figure(figsize=(16, 9)).add_subplot(1,1,1)
        netvalue_df.plot(ax=ax1,grid=True)
        ax1.set_xlabel('交易日期', fontsize=16) #x轴名称
        ax1.set_ylabel('净值', fontsize=16) #x轴名称
        plt.title("%s分组净值曲线"%pic_name,fontsize=20) #标题
        plt.legend(loc='best')
        plt.savefig(add_pic+pic_name+'.png',dpi=400,bbox_inches='tight')
 
if __name__=='__main__':
    
    #因子倒数值
    # 回归法

    # 估值指标
    #ep #市盈率
    #bp #市净率
    #sp #市销率
    #pcf_ocf #市现率
    #dividendyield #股息率
    #evtoebitda #企业倍数    
    #盈利能力
    #roe #净资产收益率（TTM）
    #roa #总资产收益率（TTM）
    #roic #投入资本回报率ROIC(TTM)
    #gpmgr #增长率_毛利率(TTM)
    #grossprofitmargin #销售毛利率(TTM)
    #orgr #增长率_营业收入(TTM)
    #cfogr #增长率_经营活动产生的现金流量净额(TTM)
    ##经营效率
    #invturn #存货周转率(TTM)
    #arturn #应收账款周转率(TTM)
    #taturn #总资产周转率(TTM)
    ##盈余质量
    #profittomv #收益市值比(TTM)
    ##投融资决策
    #tagr #增长率-总资产
    ##无形资产
    #stmnote_RDexptosales #研发支出总额占营业收入比例
    ##杠杆因子
    #debttoasset #资产负债率
    #current #流动比率
    ##市场参与者行为
    #netprofit_fy1_6m #一致预测净利润（FY1）的变化率_6M
    #revs60 #过去3个月的价格动量
    #rstr12 #12月相对强势
    
    factors_origin = ['ep','bp','sp','pcf_ocf','dividendyield','evtoebitda'] #估值因子
    factors_origin = ['roe','roa','roic','gpmgr','grossprofitmargin','orgr','cfogr']#盈利能力
    factors_origin = ['invturn','arturn','taturn'] #经营效率
    factors_origin = ['profittomv','tagr','stmnote_RDexptosales']#盈余质量#投融资决策#无形资产stmnote_RDexptosales无数据
    factors_origin = ['debttoasset','current'] #杠杆因子
    factors_origin = ['netprofit_fy1_6m','revs60','rstr12'] #市场参与者行为

    sf_res_num_T = pd.DataFrame()
    sf_res_num_IC = pd.DataFrame()
    sf_res_num_exch = pd.DataFrame()
    for fac_str in factors_origin:
        fac = eval(fac_str)
        # 数据清洗
        fac_med_de = Clean_Data(fac).Median_deextremum()
        fac_m_zscore = Clean_Data(fac_med_de).Z_score()
        fac_num = Clean_Data(fac_m_zscore).Fill_na()
        # 单因子回归
        Single_factors_test_ins = Single_factors_test_regression(fac_num)
        res_fac_num = Single_factors_test_ins.single_factor_regress()
        # T值分析
        T_fac_num_res = Single_factors_test_ins.T_analysis(res_fac_num)
        T_fac_num_res = Clean_Data.Round_df(T_fac_num_res) #保留四位小数
        T_fac_num_res['factor'] = fac_str #添加因子名称
        # IC值分析
        IC_fac_num_res = Single_factors_test_ins.IC_analysis(res_fac_num)
        IC_fac_num_res = Clean_Data.Round_df(IC_fac_num_res)
        IC_fac_num_res['factor'] = fac_str
        #方向转换统计
        exch_fac_num_res = Single_factors_test_ins.Style_rotation(res_fac_num)
        exch_fac_num_res = Clean_Data.Round_df(exch_fac_num_res) #保留四位小数
        exch_fac_num_res['factor'] = fac_str #添加因子名称
        #结果
        sf_res_num_T = sf_res_num_T.append(T_fac_num_res)
        sf_res_num_IC = sf_res_num_IC.append(IC_fac_num_res)
        sf_res_num_exch = sf_res_num_exch.append(exch_fac_num_res)

    #因子倒数
    #分组法
    sf_res_group = pd.DataFrame()
    for fac_str in factors_origin:
        fac = eval(fac_str)
        
        sf_group_ins = Single_factors_test_group(fac)
        sf_netvalue_df = sf_group_ins.group_net_value()
        #分组回测结果指标
        sf_group_res = sf_group_ins.backtest_indicates(sf_netvalue_df)
        sf_group_res['factor'] = fac_str
        sf_res_group = sf_res_group.append(sf_group_res)
        #画图
        sf_group_ins.draw(sf_netvalue_df,fac_str)

    sf_res_group = sf_res_group.reset_index()    
    
#    #因子倒数序数值
#    #回归法
#    sf_res_ord_T = pd.DataFrame()
#    sf_res_ord_IC = pd.DataFrame()
#    sf_res_ord_exch = pd.DataFrame()
#    for fac_str in factors_origin:
#        fac = eval(fac_str)
#        # 数据清洗
#        fac_ord = Clean_Data(fac).Ordinal_values()
#        fac_o_zscore = Clean_Data(fac_ord).Z_score()
#        fac_ordinal = Clean_Data(fac_o_zscore).Fill_na()
#        # 单因子回归
#        res_fac_ord = Single_factors_test_regression(fac_ordinal).single_factor_regress()
#        # T值分析
#        T_fac_ord_res = Single_factors_test_ins.T_analysis(res_fac_ord)
#        T_fac_ord_res = Clean_Data.Round_df(T_fac_ord_res) #保留四位小数
#        T_fac_ord_res['factor'] = fac_str #添加因子名称
#        # IC值分析
#        IC_fac_ord_res = Single_factors_test_ins.IC_analysis(res_fac_ord)
#        IC_fac_ord_res = Clean_Data.Round_df(IC_fac_ord_res)
#        IC_fac_ord_res['factor'] = fac_str
#        #方向转换统计
#        exch_fac_ord_res = Single_factors_test_ins.Style_rotation(res_fac_ord)
#        exch_fac_ord_res = Clean_Data.Round_df(exch_fac_ord_res) #保留四位小数
#        exch_fac_ord_res['factor'] = fac_str #添加因子名称
#        #结果
#        sf_res_ord_T = sf_res_ord_T.append(T_fac_ord_res)
#        sf_res_ord_IC = sf_res_ord_IC.append(IC_fac_ord_res)
#        sf_res_ord_exch = sf_res_ord_exch.append(exch_fac_ord_res)
    






