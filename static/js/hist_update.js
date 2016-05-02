function UpdateHistogram(cb_obj, hist_data) {
    /*cb_obj is the source data (data that is being selected)*/
    var inds = cb_obj.get('selected')['1d'].indices; /*get the indices of the selected dataa*/
    var d1 = cb_obj.get('data'); /*push source data to d*/
    var d2 = [];
    var data = hist_data.get('data');

    d2['x'] = [];
    d2['y'] = [];

    data['x'] = [];
    data['y'] = [];

    if (inds.length == 0) {return;}
    for (i=0; i<inds.length; i++) {
        d2['x'].push(d1['x'][inds[i]]);
        d2['y'].push(d1['y'][inds[i]]);
    };

    /*use d3 to calculate the histogram*/
    var histogram = d3.layout.histogram()
                    .frequency(false)
                    .bins(20) 
                    (d2['y']);
                    
    for (i=0; i<20;i++) {
        data['x'].push(0)
        data['y'].push(histogram[i].y)    
    }

    hist_data.trigger('change');
}

/*histogram[i].y*/