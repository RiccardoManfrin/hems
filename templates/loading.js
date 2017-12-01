var consumptionserie = {};

$.getJSON("/data/latest_live_data", function(data){
	consumptionserie = data
});