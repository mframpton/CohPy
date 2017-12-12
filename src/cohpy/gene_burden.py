import pandas as pd
import numpy as np
import statsmodels.discrete.discrete_model as sm
from scipy import stats
stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)
import sys
from misc import Logger


class CMC(object):
    
    def __init__(self, sample_dict, gene_col, frq_col_l, frq_grp_name_l=["rare","mod_rare"], frq_grp_range_ll=[[0.0,0.01],[0.01,0.05]]):
    
        self.logger = Logger()    
        self.sample_dict = sample_dict
        self.gene_col = gene_col
        self.frq_col_l = frq_col_l
        self.frq_grp_name_l=frq_grp_name_l
        self.frq_grp_range_ll=frq_grp_range_ll
    
    
    def do_multivariate_tests(self, geno_df, covar_df):
        
        self.logger.log("# variants: {0}".format(len(geno_df.index)))
        self.logger.log("# genes to test: {0} ".format(len(pd.unique(geno_df[self.gene_col]))))
        #Collapse the genotypes.
        self.logger.log("Collapsing genotypes...")
        geno_collapsed_df = self.get_geno_collapsed_df(geno_df)
        #Do the multivariate tests.
        self.logger.log("Doing multivariate tests...")
        y = np.array([1 if sample in self.sample_dict["case"] else 0 for sample in self.sample_dict["all"]])
        result_df = geno_collapsed_df[self.sample_dict["all"]].groupby(level=[self.gene_col]).apply(self.do_multivariate_test, y=y, covar_df=covar_df)
        #Merge the results with the collapsed variant counts.
        self.logger.log("Merge the results with the collapsed variant counts...")
        collapsed_var_count_df = self.get_collapsed_var_count_df(geno_collapsed_df)
        result_df = collapsed_var_count_df.join(result_df)
        return result_df
    
    
    def get_geno_collapsed_df(self, geno_df):
        
        geno_df[self.frq_col_l] = geno_df[self.frq_col_l].apply(pd.to_numeric, axis=1)
        geno_df[self.sample_dict["all"]] = geno_df[self.sample_dict["all"]].apply(pd.to_numeric, errors='coerce', downcast='integer', axis=1)
        geno_df[self.sample_dict["all"]].fillna(0, inplace=True)
        geno_collapsed_df = self.collapse_vars_in_frq_ranges(geno_df=geno_df)
        return geno_collapsed_df
    
        
    def collapse_vars_in_frq_ranges(self, geno_df):

        self.logger.log("Assign variants to a population frequency group.")
        geno_df["collapsed_var"] = geno_df.apply(axis=1, func=self.assign_collapse_group)
        self.logger.log("For each gene, count the # of variants in each population frequency category.")
        collapse_group_n_df = geno_df.groupby(self.gene_col)["collapsed_var"].value_counts().to_frame("n")
        self.logger.log("In each gene, aggregate sample genotypes by variant population frequency group.")
        geno_collapsed_df = geno_df.groupby([self.gene_col] + ["collapsed_var"]).apply(func=self.collapse_vars_in_samples)
        #print geno_collapsed_df[self.sample_dict["all"][:2]].to_string()
        #sys.exit()
        geno_collapsed_df = geno_collapsed_df.merge(collapse_group_n_df, left_index=True, right_index=True)
        return geno_collapsed_df


    def assign_collapse_group(self, geno_s):
        '''Return each variant's collapse group. If the variant is not within a collapse group, just return the variant ID.'''
        
        var_frq = filter(lambda x: np.isnan(x) == False, geno_s.ix[self.frq_col_l].tolist()+[0.0])[0]
        for i in xrange(len(self.frq_grp_name_l)):
            if var_frq >= self.frq_grp_range_ll[i][0] and var_frq <= self.frq_grp_range_ll[i][1]:
                return self.frq_grp_name_l[i]
        return geno_s.name

    
    def collapse_vars_in_samples(self, gene_pop_frq_group_df):
        '''For each sample, aggregate the genotypes of variants in a "gene - pop-freq-cat" group.'''

        return gene_pop_frq_group_df[self.sample_dict["all"]].apply(lambda col_s: 1 if col_s.sum() > 0 else 0, axis=0)
       
    
    def do_multivariate_test(self, geno_collapsed_gene_df, y, covar_df=None):
        
        return_data_l,return_index_l = [],[]
        
        [degf,llf,llr_p] = self.fit_logit_model(geno_collapsed_gene_df,y)
        return_data_l.append(llr_p)
        return_index_l.append("llr_p")
        
        if covar_df is not None:
            '''Model with only covariates'''
            [h0_degf,h0_llf,h0_llr_p] = self.fit_logit_model(covar_df,y)
            '''Model with covariates plus collapsed variant independent variables.'''
            [h1_degf,h1_llf,h1_llr_p] = self.fit_logit_model(pd.concat([geno_collapsed_gene_df, covar_df]),y)
            #print h0_llf,h1_llf,h0_degf,h1_degf,2*(h1_llf-h0_llf),h1_degf-h0_degf
            llr_cov_p = stats.chisqprob(2*(h1_llf-h0_llf),h1_degf-h0_degf)
            return_data_l.append(llr_cov_p)
            return_index_l.append("llr_cov_p")
            
        return pd.Series(data=return_data_l, index=return_index_l) 

    
    def fit_logit_model(self, X_df, y):
        
        X = np.transpose(X_df.values)
        logit_model = sm.Logit(y,X)
        result = logit_model.fit(method='bfgs')
        degf = result.df_model
        llf = result.llf
        llr_p = result.llr_pvalue
        return [degf,llf,llr_p]
    
    
    def get_collapsed_var_count_df(self, geno_collapsed_df):
        
        collapsed_var_count_df = geno_collapsed_df['n'].reset_index()
        collapsed_var_count_df["collapsed_var"] = collapsed_var_count_df["collapsed_var"].apply(lambda x: x if x in self.frq_grp_name_l else "other")
        collapsed_var_count_df = pd.pivot_table(data=collapsed_var_count_df, values='n', index=self.gene_col, columns='collapsed_var')
        collapsed_var_count_col_l = collapsed_var_count_df.columns.tolist()
        collapsed_var_count_col_l.sort(key = lambda x: len(self.frq_grp_name_l) if x=="other" else self.frq_grp_name_l.index(x))
        collapsed_var_count_df = collapsed_var_count_df.reindex(columns=collapsed_var_count_col_l)
        collapsed_var_count_df.fillna(0, inplace=True)
        collapsed_var_count_df = collapsed_var_count_df.apply(pd.to_numeric, downcast='integer', axis=1)
        return collapsed_var_count_df
    