function UpdateHistogram(cb_obj, hist_data, s_data) {
    /*cb_obj is the source data (data that is being selected)*/
    var inds = cb_obj.get('selected')['1d'].indices; /*get the indices of the selected dataa*/
    var d1 = cb_obj.get('data'); /*push source data to d*/
    var d2 = [];
    var data = hist_data.get('data');
    var source_data = s_data.get('data');
    var bin_thresholds = [];

    d2['x'] = [];
    d2['y'] = [];

    data['right'] = [];

    if (inds.length == 0) {
        d2['x'] = [];
        d2['y'] = [];
    }
    for (i=0; i<inds.length; i++) {
        d2['x'].push(d1['x'][inds[i]]);
        d2['y'].push(d1['y'][inds[i]]);
    };

    /*use d3 to calculate the histogram*/
    bin_dx = (Math.max(...source_data['y']) - Math.min(...source_data['y']))/20; //20 is the number of bins
    
    for (i=0; i<21;i++) {
        if (bin_thresholds.length == 0) {
            bin_thresholds.push(Math.min(...source_data['y']));
        } else {bin_thresholds.push(bin_thresholds[i-1] + bin_dx)};
        
    };
     
    var histogram = d3.layout.histogram()
                    .frequency(false)
                    .bins(bin_thresholds) 
                    (d2['y']);
    console.log(histogram)

    for (i=0; i<20;i++) {
        data['right'].push((histogram[i].y)/(histogram[i].dx));   
    };
    
    hist_data.trigger('change');
};

/*histogram[i].y*/