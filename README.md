# Seqfam

Documentation is at http://seqfam.readthedocs.io/en/latest/ .

Requirements
============

*Seqfam* is compatible with Windows, Mac OS X and Linux operating systems. It is coded using Python 3.6 but can also be run by Python 2.7. It requires the following packages:

* pandas==0.20.3
* scipy==0.19.1
* natsort==5.1.1
* numpy==1.13.3
* setuptools==38.4.0
* statsmodels==0.8.0

Run the following commands to clone and install from GitHub.

```
$ git clone https://github.com/mframpton/seqfam
$ cd seqfam
$ pip install -r requirements.txt
$ python setup.py install
```

Modules
=======

*Seqfam* has 5 modules:
1.	*gene_drop.py*: Monte Carlo gene dropping;
2.	*pof.py*: variant pattern of occurrence in families;
3.	*gene_burden.py*: regression-based gene burden testing;
4.	*relatedness.py*: identification of duplicates and verification of ascertained pedigree information via kinship coefficients;
5.	*sge.py*: Sun Grid Engine (SGE) array job creation.

Example scripts
===============

The repository contains additional scripts in *src/examples* which demonstrate the functionality of the modules on example data, including files in the *data* directory. They are *1_example_gene_drop.py*, *2_example_pof.py*, *3_example_gene_burden.py*, *4_example_relatedness.py*, and *5_example_sge.py*.

If the package is used to generate data for a publication, then please cite this article:

Matthew Frampton, Elena R. Schiff, Nikolas Pontikos, Anthony W. Segal, Adam P. Levine (2018) Seqfam: a python package for analysis of next generation sequencing DNA data in families. *F1000Research* https://f1000research.com/articles/7-281/v1
