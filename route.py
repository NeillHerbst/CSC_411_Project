
##CSC 411 project 
from __future__ import division
from numpy import array, datetime64, histogram, zeros_like, linspace, size
from scipy.stats import gaussian_kde as gkde
from flask import render_template, Flask, request

from bokeh.plotting import figure, gridplot
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, CustomJS
from bokeh.models.tools import BoxSelectTool
from bokeh.embed import components #autoload_server
#from bokeh.client import push_session, show_session

#To read files and pasrse
from pandas import read_csv

#For upload
from werkzeug.utils import secure_filename
import os

#Constants
ALLOWED_EXTENSIONS = set(['csv']) 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = "".join([APP_ROOT, "/uploads"])  
    
def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#Set up Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route('/upload', methods=['GET','POST'])
def upload():      
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER) #make upload folder if folder does not exist
    
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save("/".join([UPLOAD_FOLDER, filename]))
            return plot()
                        
    return render_template("uploads.html")
    
@app.route("/plot")
def plot():
    def datetime(x): #function to change data tipe of dates to dates
        return array(x, dtype=datetime64) #can remove after correct use of padas
        
    #data scraped from yahoo finacne
    Stock_data = read_csv("uploads/AAPL.csv")
    source = ColumnDataSource(data=dict(x=datetime(Stock_data['Date']),y=Stock_data['Adj Close']))
    
    Stock_data = read_csv("uploads/SBUX.csv")
    source2 = ColumnDataSource(data=dict(x=datetime(Stock_data['Date']),y=Stock_data['Adj Close']))
        
    # Figure plotting function
    def make_figure():
        #Create scatter plot of data
        #set up figure
        #plot_tools = ['crosshair']
        time_plot = figure(plot_height= 400, plot_width= 800, title="", x_axis_label ='Time', 
                    y_range = (min(source.data["y"]-5),max(source.data["y"]+5)), tools='',  #need to add crosshair tool (messing up inds in update function)
                    y_axis_label = 'AAPL', toolbar_location="left",  x_axis_type="datetime")
                    
        #Customize time_plot grid lines
        time_plot.xgrid.grid_line_color = None
        time_plot.ygrid.grid_line_alpha = 0.2
        
        #modify the BoxSelectTool 
        #dimensions = specify the dimension in which the box selection is free in
        #select_every_mousemove = select points as box moves over
        time_plot.add_tools(BoxSelectTool(dimensions = ["width"], select_every_mousemove = True))
        
        #add anther axis
        time_plot.extra_y_ranges = {"foo": Range1d(start = min(source2.data["y"] - 5),
                                                  end = max(source2.data["y"] + 5))}
                                                  
        #add data to scatter plot (data points on time plot)
        time_scat = time_plot.scatter("x", "y", source = source,size = 1, color = "green")
        time_scat2 = time_plot.scatter("x", "y", source = source2,size= 1, color = "blue", y_range_name = "foo")
           
        #add time series line
        time_plot.line("x","y",source=source,color = time_scat.glyph.fill_color,
                                   alpha=0.5)
                                   
        time_plot.line("x","y",source=source2,color= time_scat2.glyph.fill_color,
                                    alpha=0.5,y_range_name="foo")   
        
        #First axes styling
        time_plot.yaxis.axis_line_color = time_scat.glyph.fill_color
        time_plot.yaxis.minor_tick_line_color = time_scat.glyph.fill_color
        time_plot.yaxis.major_tick_line_color = time_scat.glyph.fill_color
        time_plot.yaxis.axis_label_text_color = time_scat.glyph.fill_color
        time_plot.yaxis.major_label_text_color = time_scat.glyph.fill_color
        
        #add second axis to time_plot and styling
        time_plot.add_layout(LinearAxis(y_range_name = "foo",
                                        axis_line_color = str(time_scat2.glyph.fill_color),
                                        major_label_text_color = str(time_scat2.glyph.fill_color), 
                                        axis_label_text_color = str(time_scat2.glyph.fill_color),
                                        major_tick_line_color = str(time_scat2.glyph.fill_color),
                                        minor_tick_line_color = str(time_scat2.glyph.fill_color),
                                        axis_label= "SBUX"), "left") 
                
        #Create marginal histogram for y-axis data density
        #set up figure
                #static total selection displayed as outline
        hist_plot = figure(plot_height = 400, plot_width = 200, y_range = time_plot.y_range)
        
        #Customize hist_plot grid lines
        hist_plot.xgrid.grid_line_alpha = 0.2
        hist_plot.ygrid.grid_line_alpha = 0.5
                
        #get histogram data 
        hist, edges = histogram(source.data["y"], density = True, bins = 20)
        
        #contruct histogram
        hist_plot.quad(top=edges[1:], bottom = edges[:-1], left = 0, right = hist,
                       fill_color = "white", alpha = 0.3)
        #styleing histograms axises              
        hist_plot.xaxis.axis_label = ""
        hist_plot.yaxis.axis_label = ""
#        hist_plot.xaxis.visible = None
                    
        #add gaussian kernel density estomator
        y_span = linspace(min(source.data["y"]),
                             max(source.data["y"]), size(source.data["y"]))
        kde = gkde(source.data["y"]).evaluate(y_span)
        
        #construct gaussian kernel density estomator lines    
        hist_plot.line(kde, y_span, line_color = "#ff6666", line_width = 1, alpha = 0.5)
            
        #Create updateable plots
        u_hist_source = ColumnDataSource(data=dict(top=edges[1:],bottom=edges[:-1],left=zeros_like(edges),right=hist))
        u_kde_source = ColumnDataSource(data=dict(x = kde, y = y_span))
        scat_data = ColumnDataSource(data=dict(x=[0],y=[0]))

        #Updateble histogram
        hist_plot.quad(top = 'top', bottom = 'bottom', left = 'left', right = 'right', source = u_hist_source,#need to be updated on selection
                                fill_color = time_scat.glyph.fill_color, alpha = 0.5)
        #Updateble kde line
        hist_plot.line('x', 'y', source=u_kde_source ,line_color = "red")
        
        #Updateble scatter plot
        scat_plot = figure(plot_height = 400, plot_width = 400, title = "", x_axis_label = '', 
                    y_axis_label = '')
        
        scat_plot.scatter('x', 'y', source=scat_data,size=2)
            
        source.callback = CustomJS(args=dict(hist_data=u_hist_source, kde_d = u_kde_source,
                                sc=scat_data, source2=source2, s_data = source),
                                code="""
                            Update_ALL_Figures(cb_obj, hist_data, kde_d, s_data, sc, source2)
                                    """)          
        #create plot layout
        layout = gridplot([[time_plot, hist_plot], [scat_plot, None]])
        return layout #need to return the layout
        
    # Calling plotting Function
    p = make_figure()
          
    # Extracting HTML elements
    script, div = components(p)
    
    return render_template("plot.html", script=script, div=div)
    
if __name__ == "__main__":
    app.run(debug=True)