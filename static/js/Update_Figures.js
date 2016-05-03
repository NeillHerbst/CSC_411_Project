function Update_ALL_Figures(cb_obj, hist_data, kde_d, s_data, scat, source2) {
    /*cb_obj is the source data (data that is being selected)*/
    var inds = cb_obj.get('selected')['1d'].indices,
        d1 = cb_obj.get('data'),
        d2 = [],
        data = hist_data.get('data'),
        source_data = s_data.get('data'),
        bin_thresholds = [],
        /*KDE data*/
        kde_data = kde_d.get('data'),
        /*Scatter plot data*/
        ds2 = source2.get('data'),
        ds_data = scat.get('data');


    d2['x'] = [];
    d2['y'] = [];
    data['right'] = [];
    kde_data['x'] = [];
    kde_data['y'] = [];
    ds_data['x'] = [];
    ds_data['y'] = [];

    /*Update Histogram*/
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

    for (i=0; i<20;i++) {
        data['right'].push((histogram[i].y)/(histogram[i].dx));   
    };


    /*Update scatter plot*/  
    for (i = 0; i < inds.length; i++) {
        ds_data['x'].push(d1['y'][inds[i]]);
        ds_data['y'].push(ds2['y'][inds[i]]);
    };
    scat.trigger('change');

    /*kernel density estimator*/
    var h = 4.5, /*4.5 best to fit python kde*/
        kde = science.stats.kde().sample(d2['y']),
        kde_bandwidth_set = d3.values(science.stats.bandwidth),
        kde_line = kde.bandwidth(h)(d3.range(Math.min(...d2['y']), Math.max(...d2['y']), .2));


    for (i=0; i<inds.length; i++) {
        kde_data['x'].push(kde_line[i][1]);
        kde_data['y'].push(kde_line[i][0]);
    };

    console.log(kde_data);
    hist_data.trigger('change');
    kde_d.trigger('change');
};

/*histogram[i].y*/