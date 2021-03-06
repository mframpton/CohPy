import os, sys
from seqfam.gene_drop import Cohort


#Create cohort object from cohort.tsv file.
data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","data"))
cohort_fam = os.path.join(data_dir,"cohort.fam")
cohort = Cohort(cohort_fam)
#print(help(cohort))
#print(help(cohort.gene_drop))
#cohort.fam_tree_l[0].log_all_info()
#sys.exit()

#Get a list of genotyped individuals.
cohort_sample_l = cohort.get_all_sample_l()
sample_genotyped_l = list(filter(lambda sample: sample.find("p") == -1,cohort_sample_l))

#Do gene dropping.
for cohort_af in [0.025,0.03,0.035,0.04]:
    p = cohort.gene_drop(0.025, cohort_af, sample_genotyped_l, 1000)
