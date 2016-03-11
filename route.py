# -*- coding: utf-8 -*-
"""
Created on Sun Mar 06 19:05:28 2016

@author: Ruan
"""
##CSC 411 project 
import numpy as np

from flask import Flask, render_template

from bokeh.plotting import figure, show, gridplot, output_file
from bokeh.models import ColumnDataSource, CustomJS, VBoxForm, HBox
from bokeh.models.widgets import Slider
#from bokeh.io import vform
from bokeh.embed import components

#create random data points
N = 100
x = 100*np.random.rand(N)
y = 100*np.random.rand(N)

source = ColumnDataSource(data=dict(x=x,y=y))

#Interaction tools
TOOLS = 'box_select, crosshair, help, reset, resize'

# Figure plotting function
def make_figure():
    #set up plot
    scat_plot = figure(plot_height=400, plot_width=800, title="Scatter plot",
                  tools=TOOLS, x_axis_label ='x', y_axis_label = 'y')

    scat_plot.scatter('x','y', source=source,size=5)
           
    show(scat_plot)
    return scat_plot #need to return the layout
        
# Calling plotting Function
p = make_figure()
      
# Extracting HTML elements
script, div = components(p)

#Set up Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/scatter_plot')
def plot():
   return render_template('scatter_plot.html', script=script, div=div)
    
if __name__ == '__main__':
    app.run(debug=True)