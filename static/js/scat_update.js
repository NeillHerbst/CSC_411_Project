function UpdateScatterplot(cb_obj, scat,source2) {
	var inds = cb_obj.get('selected')['1d'].indices;
    var d1 = cb_obj.get('data');
    var ds2 = source2.get('data');
    var d2 = scat.get('data');
    
    d2['x'] = [];
    d2['y'] = [];
    
    for (i = 0; i < inds.length; i++) {
    	d2['x'].push(d1['y'][inds[i]]);
    	d2['y'].push(ds2['y'][inds[i]]);
    };
    scat.trigger('change');
};