# -*- coding: utf-8 -*-
"""
Created on Sun Mar 06 19:05:28 2016

@author: Ruan
"""
##CSC 411 project 
import numpy as np

from flask import Flask, render_template

from bokeh.plotting import figure, show, gridplot, output_server
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.tools import BoxSelectTool
#from bokeh.io import vform
from bokeh.embed import components

#create random data points
N = 100
x = 100*np.random.rand(N)
y = 100*np.random.rand(N)

source = ColumnDataSource(data=dict(x=x,y=y))

#Interaction tools
TOOLS = "box_select,crosshair, help, reset"

# Figure plotting function
def make_figure():
    #Create scatter plot of data
    #set up figure
    scat_plot = figure(plot_height=400, plot_width=800, title="Scatter plot",
                  tools=TOOLS, x_axis_label = "x", y_axis_label = "y",
                  toolbar_location= "left")
                  
    #modify the BoxSelectTool to only select on the x-axis
    scat_plot.add_tools(BoxSelectTool(dimensions=["width"]))
    
    #add data to scatter plot
    scat_plot.scatter("x","y", source=source,size=5)
    
    #Create reggression line (slectable tool)
    
    
    #Create marginal histogram for y-axis data density
    #set up figure
    hist_plot = figure(plot_height=400, plot_width=200)
    #get histogram data 
    hist, edges = np.histogram(y, density=True, bins=10)
    #add create and add data for histograme
    hist_plot.quad(top=edges[1:], bottom=edges[:-1], left=0, right=hist,
                   fill_color="#036564", line_color="#033649")
    #styleing histograms               
    hist_plot.xaxis.axis_label = ""
    hist_plot.yaxis.axis_label = ""
    hist_plot.axis.visible = None
    
    #add probibility density function line to histogram data (smooth)
    #calculate arithmetic mean
    mu = np.mean(y)
    #calculating standard deviation
    sigma = np.std(y)
    #calculating normal distribution (probability density function)
    y_span = np.linspace(np.min(y),np.max(y),np.size(y))
    nd = 1/(2*np.pi*sigma)*np.exp(-(y_span - mu)**2/(2*sigma**2))
    #construct line
    hist_plot.line(nd,y_span,line_color="#D95B43", line_width=1,alpha=0.7)
    cent = [(edges[1] - edges[0])/2]
    for i in range(np.size(edges)):          
          cent.append((edges[1] - edges[0])/2 + edges[i])   
    
    hist_plot.line(hist,cent,line_color="red", line_width=1,alpha=1)
    #create plot layout
    layout = gridplot([[scat_plot,hist_plot]])
    output_server('plot')
    show(layout)
    return layout #need to return the layout
        
# Calling plotting Function
p = make_figure()
      
# Extracting HTML elements
script, div = components(p)

#Set up Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/plot')
def plot():
   return render_template('plot.html', script=script, div=div)
    
if __name__ == '__main__':
    app.run(debug=True)