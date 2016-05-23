function mean(x) {
        sum_x = 0;
        for (i = 0; i < x.length; i++) {
            sum_x += x[i];
        };
       return sum_x/x.length;
    };

function std(x) {
        num = 0;
        mu = mean(x);
        for (i = 0; i < x.length; i++) {
            num += Math.pow(x[i] - mu,2);
        };
        return num/x.length;
    };


function Update_ALL_Figures(cb_obj, hist_data, hist_data2, kde_d, kde_d2, scat) {
    /*cb_obj is the source data (data that is being selected)*/
    var inds = cb_obj.get('selected')['1d'].indices,
        d1 = cb_obj.get('data'),
        d2 = [],
		dd = [],
        /*Histogram plot data*/
        data = hist_data.get('data'),
		data2 = hist_data2.get('data'),
        bin_thresholds = [],
		bin_thresholds2 = [],
        /*KDE data*/
        kde_data = kde_d.get('data'),
		kde_data2 = kde_d2.get('data'),
        /*Scatter plot data*/
        ds_data = scat.get('data');
    console.log(d1['x'].length)

    d2['x'] = [];
    d2['y'] = [];
	dd['x'] = [];
    dd['y'] = [];
    data['right'] = [];
	data2['right'] = [];
    kde_data['x'] = [];
    kde_data['y'] = [];
	kde_data2['x'] = [];
    kde_data2['y'] = [];
    ds_data['x'] = [];
    ds_data['y'] = [];

    if (inds.length == 0) {
        data['right'] = [];
		data2['right'] = [];
        kde_data['x'] = [];
        kde_data['y'] = [];
		kde_data2['x'] = [];
        kde_data2['y'] = [];
        ds_data['x'] = [0];
        ds_data['y'] = [0]
    }

    /*Update Histogram*/
    for (i=0; i<inds.length; i++) {
        d2['x'].push(d1['x'][inds[i]]);
        d2['y'].push(d1['y1'][inds[i]]);
		dd['x'].push(d1['x'][inds[i]]);
        dd['y'].push(d1['y2'][inds[i]]);
    };

    /*use d3 to calculate the histogram*/
    bin_dx = (Math.max(...d1['y1']) - Math.min(...d1['y1']))/20; //20 is the number of bins
	bin_dx2 = (Math.max(...d1['y2']) - Math.min(...d1['y2']))/20;
    
    for (i=0; i<21;i++) {
        if (bin_thresholds.length == 0) {
            bin_thresholds.push(Math.min(...d1['y1']));
        } else {bin_thresholds.push(bin_thresholds[i-1] + bin_dx)};
        
    };
    
	for (i=0; i<21;i++) {
        if (bin_thresholds2.length == 0) {
            bin_thresholds2.push(Math.min(...d1['y2']));
        } else {bin_thresholds2.push(bin_thresholds2[i-1] + bin_dx2)};
        
    };
	
    var histogram = d3.layout.histogram()
                    .frequency(false)
                    .bins(bin_thresholds) 
                    (d2['y']);
	
	var histogram2 = d3.layout.histogram()
                    .frequency(false)
                    .bins(bin_thresholds2) 
                    (dd['y']);

    for (i=0; i<20;i++) {
        data['right'].push((histogram[i].y)/(histogram[i].dx));
		data2['right'].push((histogram2[i].y)/(histogram2[i].dx));		
    };

    /*Update scatter plot*/  
    for (i = 0; i < inds.length; i++) {
        ds_data['x'].push(d1['y1'][inds[i]]);
        ds_data['y'].push(d1['y2'][inds[i]]);
    };

    /*kernel density estimator*/
    if (inds.length > 2) {
    var h = 1000/d2['y'].length*std(d2['y'])*Math.pow(d2['y'].length,1/5),
        kde = science.stats.kde().sample(d2['y']),
        kde_bandwidth_set = d3.values(science.stats.bandwidth),
        kde_line = kde.bandwidth(h)(d3.range(Math.min(...d2['y']), Math.max(...d2['y']), 0.0001)),
		h2  = 1000/dd['y'].length*std(dd['y'])*Math.pow(d2['y'].length,1/5),
        kde2 = science.stats.kde().sample(dd['y']),
        kde_bandwidth_set2 = d3.values(science.stats.bandwidth),
        kde_line2 = kde2.bandwidth(h2)(d3.range(Math.min(...dd['y']), Math.max(...dd['y']), 0.0001));

    for (i=0; i<kde_line.length; i++) {
        kde_data['x'].push(kde_line[i][1]);
        kde_data['y'].push(kde_line[i][0]);
    };
	
	for (i=0; i<kde_line2.length; i++) {
        kde_data2['x'].push(kde_line2[i][1]);
        kde_data2['y'].push(kde_line2[i][0]);
    };
	};
	
    hist_data.trigger('change');
	hist_data2.trigger('change');
    scat.trigger('change');
    kde_d.trigger('change');
	kde_d2.trigger('change');
};