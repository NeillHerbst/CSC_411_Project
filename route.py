from __future__ import division #To allow for dividing with a / in python 2.7.x

#Flask web framework
from flask import render_template, Flask, request, flash, redirect, url_for

#For calculations and plotting
from numpy import histogram, zeros_like, linspace, size
from scipy.stats import gaussian_kde as gkde

from bokeh.plotting import figure, gridplot
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, CustomJS
from bokeh.models.tools import BoxSelectTool
from bokeh.embed import components

#To reading files 
from pandas import read_csv

#For uploading files
from werkzeug.utils import secure_filename
import os


#Set up Flask app
app = Flask(__name__)
app.secret_key = '154254'
@app.route("/")
def home():
    return redirect(url_for('upload'))
    
@app.route('/upload', methods=['GET','POST'])
def upload():      
    ALLOWED_EXTENSIONS = set(['csv']) 
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = "".join([APP_ROOT, "/uploads"])  
        
    def allowed_file(filename):
            return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS    
    
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save("/".join([UPLOAD_FOLDER, filename]))
            return redirect(url_for('.plot', filename=filename))
        else:
			 flash('No file was selected.')
                        
    return render_template("uploads.html")
    
@app.route("/plot", methods=['GET'])
def plot():
    filename = request.args.get('filename')
    flash(filename + ' successfully uploaded, and data visualized.')
    data_file = read_csv("uploads/" + filename, parse_dates = ['timestamp'])
    data_source = ColumnDataSource(data=dict(x = data_file['timestamp'],
                    y1 = data_file['l1013aspv'],y2 = data_file['l1015asop']))
            
    # Figure plotting function
    def make_figure():
#%% Create Time Series Graph
        #Create Time Series plot area
        time_plot = figure(plot_height= 400, plot_width= 800, title="", x_axis_label ='Time', 
                    tools='', y_axis_label = 'l1013aspv', toolbar_location="left",
                    x_axis_type="datetime",
                    y_range=(min(data_source.data["y1"]) -min(data_source.data["y1"]*0.1 ),
                             max(data_source.data["y1"]) + max(data_source.data["y1"]*0.1)))
                       
        #modify the BoxSelectTool 
        #dimensions = specify the dimension in which the box selection is free in
        #select_every_mousemove = select points as box moves over
        time_plot.add_tools(BoxSelectTool(dimensions = ["width"], select_every_mousemove = True))

        #add anther axis
        time_plot.extra_y_ranges = {"foo": Range1d(start = min(data_source.data["y2"]) 
                                                        - min(data_source.data["y1"]*0.1),
                                                  end = max(data_source.data["y2"]) + max(data_source.data["y1"]*0.1))}
                                                  
        #add data to scatter plot (data points on time plot)
        time_scat = time_plot.scatter("x", "y1", source = data_source,size = 1, color = "green")
        time_scat2 = time_plot.scatter("x", "y2", source = data_source,size= 1, color = "blue", y_range_name = "foo")
           
        #add time series line
        time_plot.line("x","y1",source=data_source,color = time_scat.glyph.fill_color,
                                   alpha=0.5)
                                   
        time_plot.line("x","y2",source=data_source,color= time_scat2.glyph.fill_color,
                                    alpha=0.5,y_range_name="foo")
                                    
        #Customize time_plot grid lines
        time_plot.xgrid.grid_line_color = None
        time_plot.ygrid.grid_line_alpha = 0.2
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
                                        axis_label= "l1015asop"), "left")
                                    
#%% Create Marginal Histogram and KDE
       #Create marginal histogram for y-axis data density
        #set up figure
        hist_plot = figure(plot_height = 400, plot_width = 200, y_range = time_plot.y_range)
        
        #add second axis to histogram
        hist_plot.extra_y_ranges = {"foo": 
            Range1d(start = min(data_source.data["y2"]) - min(data_source.data["y1"]*0.1),
                    end = max(data_source.data["y2"]) + max(data_source.data["y1"]*0.1))}
        
        #Customize hist_plot grid lines
        hist_plot.xgrid.grid_line_alpha = 0.2
        hist_plot.ygrid.grid_line_alpha = 0.5
                
        #get histogram data 
        hist, edges = histogram(data_source.data["y1"], density = True, bins = 20)
        hist2, edges2 = histogram(data_source.data["y2"], density = True, bins = 20)
        
        #styleing histograms axises              
        hist_plot.xaxis.axis_label = ""
        hist_plot.yaxis.axis_label = ""
        hist_plot.xaxis.visible = None
                    
        #add gaussian kernel density estomator
        y_span = linspace(min(data_source.data["y1"]),
                             max(data_source.data["y1"]), size(data_source.data["y1"]))
        kde = gkde(data_source.data["y1"]).evaluate(y_span)
        
        y_span2 = linspace(min(data_source.data["y2"]),
                             max(data_source.data["y2"]), size(data_source.data["y2"]))
        kde2 = gkde(data_source.data["y2"]).evaluate(y_span2)                             
                                    
                                    
        #Histogram First axes styling
        hist_plot.yaxis.axis_line_color = time_scat.glyph.fill_color
        hist_plot.yaxis.minor_tick_line_color = time_scat.glyph.fill_color
        hist_plot.yaxis.major_tick_line_color = time_scat.glyph.fill_color
        hist_plot.yaxis.axis_label_text_color = time_scat.glyph.fill_color
        hist_plot.yaxis.major_label_text_color = time_scat.glyph.fill_color        
        #Histogram second axes styling
        hist_plot.add_layout(LinearAxis(y_range_name = "foo",
                                        axis_line_color = str(time_scat2.glyph.fill_color),
                                        major_label_text_color = str(time_scat2.glyph.fill_color), 
                                        axis_label_text_color = str(time_scat2.glyph.fill_color),
                                        major_tick_line_color = str(time_scat2.glyph.fill_color),
                                        minor_tick_line_color = str(time_scat2.glyph.fill_color)), "left")
                                        
#%% Create Scatter Graph       
        scat_plot = figure(plot_height = 400, plot_width = 400, title = "", x_axis_label = 'l1015asop', 
                    y_axis_label = 'l1013aspv')
        
        #scatter plot axis cutomization
        scat_plot.yaxis.axis_line_color = time_scat.glyph.fill_color
        scat_plot.yaxis.minor_tick_line_color = time_scat.glyph.fill_color
        scat_plot.yaxis.major_tick_line_color = time_scat.glyph.fill_color
        scat_plot.yaxis.axis_label_text_color = time_scat.glyph.fill_color
        scat_plot.yaxis.major_label_text_color = time_scat.glyph.fill_color
        
        scat_plot.xaxis.axis_line_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.minor_tick_line_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.major_tick_line_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.axis_label_text_color = time_scat2.glyph.fill_color
        scat_plot.xaxis.major_label_text_color = time_scat2.glyph.fill_color 
                
        
#%% Add data to Histogram and scatter plot (this data is updated in callback fuction)       
        #Create updateable plots
        u_hist_source = ColumnDataSource(data=dict(top=edges[1:],bottom=edges[:-1],left=zeros_like(edges),right=hist))
        u_hist_source2 = ColumnDataSource(data=dict(top=edges2[1:],bottom=edges2[:-1],left=zeros_like(edges2),right=hist2))
        u_kde_source = ColumnDataSource(data=dict(x = kde, y = y_span))
        u_kde_source2 = ColumnDataSource(data=dict(x = kde2, y = y_span2))
        scat_data = ColumnDataSource(data=dict(x=[0],y=[0]))

        #Updateble histogram
        hist_plot.quad(top = 'top', bottom = 'bottom', left = 'left', right = 'right', source = u_hist_source,
                                fill_color = time_scat.glyph.fill_color, alpha = 0.5)
                                
        hist_plot.quad(top = 'top', bottom = 'bottom', left = 'left', right = 'right', source = u_hist_source2,
                                fill_color = time_scat2.glyph.fill_color, alpha = 0.3, y_range_name = "foo")
        #Updateble kde line
        hist_plot.line('x', 'y', source=u_kde_source ,line_color = "#008000")
        hist_plot.line('x', 'y', source=u_kde_source2 ,line_color = "#000099", y_range_name = "foo")
        
        
        
        #Updateble scatter plot 
        scat_plot.scatter('x', 'y', source=scat_data,size=2, alpha=0.3)

#%% Updating fuction            
        data_source.callback = CustomJS(args=dict(hist_data=u_hist_source, hist_data2=u_hist_source2,
                                        kde_d = u_kde_source, kde_d2 = u_kde_source2, sc=scat_data),
                                code="""
                            Update_ALL_Figures(cb_obj, hist_data, hist_data2, kde_d, kde_d2, sc)
                                    """)
#%% create plot layout
                                    
        layout = gridplot([[time_plot, hist_plot], [scat_plot, None]])
        return layout #need to return the layout
        
    # Calling plotting Function
    p = make_figure()
          
    # Extracting HTML elements
    script, div = components(p)
    
    return render_template("plot.html", script=script, div=div)
    
if __name__ == "__main__":
    app.run(debug=True)