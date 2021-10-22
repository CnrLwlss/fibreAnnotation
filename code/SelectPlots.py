import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.request
import os.path
from Selecting import *
 
# Download data
url = "https://raw.githubusercontent.com/CnrLwlss/Warren_2019/master/shiny/dat.txt"
outfile = "dat_py.txt"
mitoprot = "VDAC1"

if not os.path.isfile(outfile):
    urllib.request.urlretrieve(url,outfile)
data = pd.read_csv(outfile,sep="\t")

# Drop unwanted columns
chans = data.channel.unique()
chans = [c for c in chans if ("LOG_" not in c) and ("MED_" not in c)]
data = data[data["channel"].isin(chans)]

# Group data by subject type
subjids = data.patient_id.unique()
subjids.sort()

patids = [id for id in subjids if "P" in id]
ctrlids = [id for id in subjids if "C" in id]

# Long to wide
wide = data.pivot_table(index=["cell_id","id","patient_id","subject_group"],values="value",columns="channel").reset_index()
cwide = wide[wide["patient_id"].isin(ctrlids)]

# Plotting options
alpha = 0.2
def_col = (1,0,0,alpha)
norm_col = (0,1,0,alpha)
pos_col = (0,0,1,alpha)

# Manually classify fibres by each protein
prots = ['NDUFB8', 'GRIM19', 'SDHA', 'UqCRC2', 'COX4+4L2',  'MTCO1', 'OSCP']
for prot in prots:
    cols = [(0,0,0,alpha) for pt in wide[mitoprot]]
    fig,ax = plt.subplots(num = "Select fibres below controls")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    pts = plt.scatter(np.log(wide[mitoprot]),np.log(wide[prot]),color=cols,edgecolors="none")
    cnts = sns.kdeplot(x=np.log(cwide[mitoprot]),y=np.log(cwide[prot]),levels=[0.1,0.25,0.5,0.75,0.95],color="yellow")
    ax.set_xlabel("log("+mitoprot+")")
    ax.set_ylabel("log("+prot+")")
    sel_def = SelectFromCollection(ax,pts,colour_sel=def_col)
    plt.show()

    cols = [def_col if i in sel_def.ind else col for i,col in enumerate(cols)]
    fig,ax = plt.subplots(num = "Select fibres above controls")
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()
    pts = plt.scatter(wide[mitoprot],wide[prot],color=cols,edgecolors="none")
    cnts = sns.kdeplot(x=cwide[mitoprot],y=cwide[prot],levels=[0.1,0.25,0.5,0.75,0.95],color="yellow")
    ax.set_xlabel("log("+mitoprot+")")
    ax.set_ylabel("log("+prot+")")
    sel_pos = SelectFromCollection(ax,pts,colour_sel=pos_col)
    plt.show()

    wide[prot+"_down"] = [i in sel_def.ind for i,val in enumerate(wide[prot])]
    wide[prot+"_up"] = [i in sel_pos.ind for i,val in enumerate(wide[prot])]

wide.to_csv("ClassifiedWide.csv")

# Summarise classifications
clcols = ["patient_id","subject_group"]+[col for col in wide.columns if ("_up" in col) or ("_down" in col)]
cl = wide[clcols]
pid = cl.groupby("patient_id").mean()
sub = cl.groupby("subject_group").mean()
pid.to_csv("SummaryByPatient.csv", float_format='%.2f')
sub.to_csv("SummaryByType.csv", float_format='%.2f')



