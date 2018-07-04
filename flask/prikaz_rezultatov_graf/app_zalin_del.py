# -*- coding: utf-8 -*-

#@app.route('/jadralci/<tekmovalec_id>')
#def tekmovalec_view(tekmovalec_id):
#    id = int(tekmovalec_id)
#    cur.execute("SELECT *, (SELECT ime FROM KLUB WHERE idklub = klub_idklub) FROM regata WHERE idregata = {}".format(id))
#
#    return render_template('jadralci.html')

"""
Created on Thu Jun  7 10:27:28 2018

@author: ASUS
"""

import numpy as np
import matplotlib.pyplot as plt
import math as math

from scipy import optimize
from scipy.optimize import curve_fit
from scipy.integrate import quad
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from cycler import cycler
plt.rc('text', usetex = False)
plt.rc('font', size = 13, family = 'serif', serif = ['Computer Modern'])
plt.rc('xtick', labelsize = 'medium')
plt.rc('ytick', labelsize = 'medium')
plt.rc('legend', frameon = False, fontsize = 'medium')
plt.rc('figure', figsize = (12,10))
plt.rc('lines', linewidth=2.0)
plt.rc('axes', prop_cycle=(cycler('color', plt.cm.get_cmap('viridis')(np.linspace(0,1,5)))))

'''s pyplot-om'''
df=pd.read_csv('test_data.txt')
#df.rename(columns={0: 'ime', 1: 'sailno', 2: 'id', 3: 'plov_idplov', 4:'tocke'}, inplace=True);
#df = df.sort(['tocke'], ascending=[1]);
tekmovalec = df['ime'][0]
jadro = df['sailno'][0]
plt.grid()
plt.scatter(df['plov_idplov'],df['tocke'])
#df.plot(x='plov_idplov', y='tocke', style='o')
plt.xlabel(r'Plov')
plt.ylabel(r'Mesto')
plt.title(r'$Rezultati$ $regate$ %s $za$ $tekmovalca:$ %s - $št.jadra:$ %s'%(1,tekmovalec,jadro))

#%%
import plotly.plotly as py
from plotly.graph_objs import *
'''s plotly-jem'''
df=pd.read_csv('test_data.txt')
tekmovalec = df['ime'][0]
jadro = df['sailno'][0]
plt.grid()
trace1 = Scatter(x=df['plov_idplov'],y=df['tocke'])
layout = Layout(xaxis=XAxis( title='Plov' ), yaxis=YAxis( title='Mesto' ))
data = Data([trace1])
fig = Figure(data=data, layout=layout)
py.iplot(fig, filename=r'$Rezultati$ $regate$ %s $za$ $tekmovalca:$ %s - $št.jadra:$ %s'%(1,tekmovalec,jadro))
