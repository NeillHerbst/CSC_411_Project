# -*- coding: utf-8 -*-
"""
Created on Sun Mar 06 19:05:28 2016

@author: Ruan
"""
##CSC 411 project 
import numpy as np
from scipy.stats import gaussian_kde as gkde
from flask import Flask, render_template

from bokeh.plotting import figure, show, gridplot, output_server
from bokeh.models import ColumnDataSource
from bokeh.models.tools import BoxSelectTool
from bokeh.embed import components
import pandas as pd

def datetime(x):
    return np.array(x, dtype=np.datetime64)
    
Stock_data = pd.read_csv("APLE.csv")
    
source = ColumnDataSource(data=dict(x=datetime(Stock_data['Date']),y=Stock_data['Adj Close']))

#Interaction tools
TOOLS = "box_select,crosshair, help, reset"

# Figure plotting function
def make_figure():
    #Create scatter plot of data
    #set up figure
    plot = figure(plot_height=400, plot_width=800, title="Scatter plot",
                  tools=TOOLS, x_axis_label = "Time", y_axis_label = "Stock", x_axis_type="datetime",
                  toolbar_location= "left")
                  
    #modify the BoxSelectTool 
    #dimensions = specify the dimension in which the box selection is free in
    #select_every_mousemove = select points as box moves over
    plot.add_tools(BoxSelectTool(dimensions=["width"],select_every_mousemove=True))
    
    #add data to scatter plot
    plot.scatter("x","y", source=source,size=0)
    
    #add time series line
    plot.line("x","y",source=source,color="navy",alpha=0.5)
    
    #Create reggression line (slectable tool)   
    #Create marginal histogram for y-axis data density
    #set up figure
    hist_plot = figure(plot_height=400, plot_width=200)
    #get histogram data 
    hist, edges = np.histogram(source.data["y"], density=True, bins=10)
    #add create and add data for histograme
    hist_plot.quad(top=edges[1:], bottom=edges[:-1], left=0, right=hist,
                   fill_color="#036564", line_color="#033649")
    #styleing histograms axises              
    hist_plot.xaxis.axis_label = ""
    hist_plot.yaxis.axis_label = ""
    hist_plot.xaxis.visible = None
    
    #add probibility density function line to histogram data (smooth)
    #calculate arithmetic mean
    mu = np.mean(source.data["y"])
    
    #calculating standard deviation
    sigma = np.std(source.data["y"])
    
    #calculating normal distribution (probability density function)
    y_span = np.linspace(np.min(source.data["y"]),np.max(source.data["y"]),np.size(source.data["y"]))
    nd = 1/(2*np.pi*sigma)*np.exp(-(y_span - mu)**2/(2*sigma**2))
    
    #add KDE
    kde = gkde(source.data["y"]).evaluate(y_span)
    
    #construct lines
    hist_plot.line(nd,y_span,line_color="#D95B43", line_width=1,alpha=0.5)
    hist_plot.line(kde,y_span,line_color="red",line_width=1,alpha=0.5)
    #create plot layout
    layout = gridplot([[plot,hist_plot]])
#    output_server("plot")
    show(layout)
    return layout #need to return the layout
        
# Calling plotting Function
p = make_figure()
      
# Extracting HTML elements
script, div = components(p)

#Set up Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/plot")
def plot():
   return render_template("plot.html", script=script, div=div)
    
if __name__ == "__main__":
    app.run(debug=True)