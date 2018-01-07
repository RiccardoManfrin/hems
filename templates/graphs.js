var five_mins_initial_data = {};
var last_24 = {};
var last_24_ts = {};
var last_24_p_Wh = {};
var last_24_c_Wh = {};
var last_24_a_Wh = {};
var last_24_s_Wh = {};
var last_24_b_Wh = {};
var daily = {};

var consumptiony = 0;
var productiony = 0

Highcharts.setOptions({
	global: {
		useUTC: false
	}
});

function load_last_day_chart() {
	Highcharts.chart('hourly', {
		chart: {
			type: 'column',
			height : 300
		},
		credits: {
	      enabled: false
	  	},
		title: {
			text: 'Last day'
		},
		subtitle: {
			text: 'Prodution VS consumption'
		},
		xAxis: {
			type: 'datetime',
			gridLineWidth: 1
		},
		yAxis: {
			title: {
				text: '[W]'
			},
			labels: {
				formatter: function () {
					return this.value / 1000 + 'k';
				}
			}
		},
		legend: {
			align: 'left',
			verticalAlign: 'top',
			layout: 'vertical',
			borderColor:'#999999',
			borderRadius:5,
			borderWidth:0.5,
			x: 50,
			y: 50,
			floating: true
		},
		tooltip: {
			pointFormat: '{series.name}: <b>{point.y:,.0f}</b>'
		},
		plotOptions: {
			area: {
				pointStart: 1940,
				marker: {
					enabled: false,
					symbol: 'circle',
					radius: 2,
					states: {
						hover: {
							enabled: true
						}
					}
				}
			}
		},
		series: [
		{
			name: 'Consumed [Wh]',
			color: 'rgba(165,0,0,0.5)',
			//data: [last_24_c_Wh]
			data: (function () {
				var data = [];
				for (var i = 0; i < last_24_ts.length; i++) {
						var point = { 
							x: last_24_ts[i], 
							y: last_24_c_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		},
		{
			name: 'Produced [Wh]',
			color: 'rgba(0,165,0,0.5)',
			//data: [last_24_c_Wh]
			data: (function () {
				var data = [];
				for (var i = 0; i < last_24_ts.length; i++) {
						var point = { 
							x: last_24_ts[i], 
							y: last_24_p_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		},
		{
			name: 'Auto-consumed [Wh]',
			color: 'rgba(0,165,0,0.8)',
			//data: [last_24_c_Wh]
			data: (function () {
				var data = [];
				for (var i = 0; i < last_24_ts.length; i++) {
						var point = { 
							x: last_24_ts[i], 
							y: last_24_a_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		},
		{
			name: 'Sold [Wh]',
			color: '#ffd200',
			//data: [last_24_c_Wh]
			data: (function () {
				var data = [];
				for (var i = 0; i < last_24_ts.length; i++) {
						var point = { 
							x: last_24_ts[i], 
							y: last_24_s_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		},
		{
			name: 'Bought [Wh]',
			color: 'rgba(165,0,0,0.8)',
			data: (function () {
				var data = [];
				for (var i = 0; i < last_24_ts.length; i++) {
						var point = { 
							x: last_24_ts[i], 
							y: last_24_b_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		}] 
	});
}

function load_5mins_chart() {
	Highcharts.chart('five_mins', {
		chart: {
			type: 'areaspline',
			animation: Highcharts.svg, // don't animate in old IE
			marginRight: 10,
			height : 300,
			events: {
				load: function () {
					
					var consumption = this.series[0];
					var production = this.series[1];
					setInterval(function () {
						$.getJSON("/data/consumption/live", function(data){consumptiony = data});
						$.getJSON("/data/production/live", function(data){productiony = data});
						var x = (new Date()).getTime();
							
						consumption.addPoint([x, consumptiony], true, true);
						production.addPoint([x, productiony], true, true);	
					}, 1000);
				}
			}
		},
		credits: {
	      enabled: false
	  	},
		title: {
			text: 'Last 5 minutes'
		},
		subtitle: {
			text: 'Prodution VS consumption'
		},
		xAxis: {
			type: 'datetime',
			tickPixelInterval: 150,
			gridLineWidth: 1
		},
		yAxis: {
			title: {
				text: '[W]'
			},
			plotLines: [{
				value: 0,
				width: 0.5,
				color: '#808080'
			}]
		},
		tooltip: {
			formatter: function () {
				return '<b>' + this.series.name + '</b><br/>' +
					Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
					Highcharts.numberFormat(this.y, 2);
			}
		},
		legend: {
			align: 'left',
			verticalAlign: 'top',
			layout: 'vertical',
			borderColor:'#999999',
			borderRadius:5,
			borderWidth:0.5,
			x: 50,
			y: 50,
			floating: true
		},
		series: [{
			name: 'Consumption [W]',
			color: '#DF5353',
			data: (function () {
				var data = [];
				for (var i = 0; i < five_mins_initial_data['ts_ms_since_epoch'].length; i++) {
						var point = { 
							x: five_mins_initial_data['ts_ms_since_epoch'][i], 
							y: five_mins_initial_data['c_W'][i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		},
		{
			name: 'Prodution [W]',
			color: '#55BF3B',
			data: (function () {
				var data = [];
				for (var i = 0; i < five_mins_initial_data['ts_ms_since_epoch'].length; i++) {
						var point = { 
							x: five_mins_initial_data['ts_ms_since_epoch'][i], 
							y: five_mins_initial_data['p_W'][i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
		}]
	});
}

function load_daily_chart() {
	Highcharts.chart('daily_energy', {
	    chart: {
	        type: 'areaspline',
	        height:250
	    },
	    title: {
	        text: 'Daily KWh'
	    },
	    xAxis: {
			type: 'datetime',
			gridLineWidth: 1
	    },
	    yAxis: {
	        min: 0,
	        title: {
	            text: '[Wh]',
	           
	        },
	        labels: {
	            overflow: 'justify'
	        }
	    },
	    tooltip: {
	        valueSuffix: '[Wh]'
	    },
	    plotOptions: {
	 		areaspline: {
	            stacking: 'normal',
	            fillOpacity : 0.4	
	        }
	    },
	    credits: {
	      enabled: false
	  	},
	    legend: {
	        layout: 'vertical',
	        align: 'left',
	        verticalAlign: 'top',
	        x: 50,
	        y: 20,
	        floating: true,
	        borderWidth: 1,
	        backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
	        shadow: true
	    },
	    credits: {
	        enabled: false
	    },
	    series: [{
	        name: 'Consumed [Wh]',
	        color: 'rgba(165,0,0,0.5)',
	        pointPadding: 0.3,
	        data: (function () {
	        	var data = [];
				daily_ts = daily['daily_epoch_ms']
				daily_p_Wh = daily['daily_p_Wh']
				daily_c_Wh = daily['daily_c_Wh']
				daily_a_Wh = daily['daily_a_Wh']
				daily_s_Wh = daily['daily_s_Wh']
				daily_b_Wh = daily['daily_b_Wh']
				for (var i = 0; i < daily_ts.length; i++) {
						var point = { 
							x: daily_ts[i], 
							y: daily_c_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
	    }, {
	        name: 'Bought [Wh]',
	        color: 'rgba(165,0,0,0.8)',
	        pointPlacement: -0.15,
	        data: (function () {
	        	var data = [];
				daily_ts = daily['daily_epoch_ms']
				daily_p_Wh = daily['daily_p_Wh']
				daily_c_Wh = daily['daily_c_Wh']
				daily_a_Wh = daily['daily_a_Wh']
				daily_s_Wh = daily['daily_s_Wh']
				daily_b_Wh = daily['daily_b_Wh']
				for (var i = 0; i < daily_ts.length; i++) {
						var point = { 
							x: daily_ts[i], 
							y: daily_b_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
	    },{
	        name: 'Produced [Wh]',
	        color: 'rgba(0,165,0,0.5)',
	        pointPlacement: 0.15,
	        pointPadding: 0.3,
	        data: (function () {
	        	var data = [];
				daily_ts = daily['daily_epoch_ms']
				daily_p_Wh = daily['daily_p_Wh']
				daily_c_Wh = daily['daily_c_Wh']
				daily_a_Wh = daily['daily_a_Wh']
				daily_s_Wh = daily['daily_s_Wh']
				daily_b_Wh = daily['daily_b_Wh']
				for (var i = 0; i < daily_ts.length; i++) {
						var point = { 
							x: daily_ts[i], 
							y: daily_p_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
	    }, {
	        name: 'Auto-consumed [Wh]',
	        color: 'rgba(0,165,0,0.8)',
	        data: (function () {
	        	var data = [];
				daily_ts = daily['daily_epoch_ms']
				daily_p_Wh = daily['daily_p_Wh']
				daily_c_Wh = daily['daily_c_Wh']
				daily_a_Wh = daily['daily_a_Wh']
				daily_s_Wh = daily['daily_s_Wh']
				daily_b_Wh = daily['daily_b_Wh']
				for (var i = 0; i < daily_ts.length; i++) {
						var point = { 
							x: daily_ts[i], 
							y: daily_a_Wh[i]
						}

						//console.log("Data point " + JSON.stringify(point))
						data.push(point);
				}

				return data;
			}())
	    }]
	});
}

Highcharts.chart('gauge_production', 
	{
	    chart: {
	        type: 'gauge',
	        plotBackgroundColor: null,
	        plotBackgroundImage: null,
	        plotBorderWidth: 0,
	        plotShadow: false,
	        height : 300
	    },
	    credits: {
	      enabled: false
	  	},
	    title: {
	        text: 'Live production'
	    },

	    pane: {
	        startAngle: -150,
	        endAngle: 150,
	        background: [{
	            backgroundColor: {
	                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
	                stops: [
	                    [0, '#FFF'],
	                    [1, '#333']
	                ]
	            },
	            borderWidth: 0,
	            outerRadius: '109%'
	        }, {
	            backgroundColor: {
	                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
	                stops: [
	                    [0, '#333'],
	                    [1, '#FFF']
	                ]
	            },
	            borderWidth: 1,
	            outerRadius: '107%'
	        }, {
	            // default background
	        }, {
	            backgroundColor: '#DDD',
	            borderWidth: 0,
	            outerRadius: '105%',
	            innerRadius: '103%'
	        }]
	    },

	    // the value axis
	    yAxis: {
	        min: 0,
	        max: 6000,

	        minorTickInterval: 'auto',
	        minorTickWidth: 1,
	        minorTickLength: 10,
	        minorTickPosition: 'inside',
	        minorTickColor: '#666',

	        tickPixelInterval: 30,
	        tickWidth: 2,
	        tickPosition: 'inside',
	        tickLength: 10,
	        tickColor: '#666',
	        labels: {
	            step: 2,
	            rotation: 'auto'
	        },
	        title: {
	            text: '[W]'
	        },
	        plotBands: [{
	            from: 0,
	            to: 6000,
	            color: '#55BF3B' // green
	        }]
	    },
	    exporting: {
			enabled: false
		},
	    series: [{
	        name: 'Watt',
	        data: [0],
	        tooltip: {
	            valueSuffix: ' [W]'
	        }
	    }]

	},
	// Add some life
	function (chart) {
	    if (!chart.renderer.forExport) {
	        setInterval(function () {
	            var point = chart.series[0].points[0];
	            point.update(productiony);
	        }, 1000);
	    }
	});


Highcharts.chart('gauge_consumption', 
	{
	    chart: {
	        type: 'gauge',
	        plotBackgroundColor: null,
	        plotBackgroundImage: null,
	        plotBorderWidth: 0,
	        plotShadow: false,
	        height : 300
	    },
	    credits: {
	      enabled: false
	  	},
	    title: {
	        text: 'Live consumption'
	    },

	    pane: {
	        startAngle: -150,
	        endAngle: 150,
	        background: [{
	            backgroundColor: {
	                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
	                stops: [
	                    [0, '#FFF'],
	                    [1, '#333']
	                ]
	            },
	            borderWidth: 0,
	            outerRadius: '109%'
	        }, {
	            backgroundColor: {
	                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
	                stops: [
	                    [0, '#333'],
	                    [1, '#FFF']
	                ]
	            },
	            borderWidth: 1,
	            outerRadius: '107%'
	        }, {
	            // default background
	        }, {
	            backgroundColor: '#DDD',
	            borderWidth: 0,
	            outerRadius: '105%',
	            innerRadius: '103%'
	        }]
	    },

	    // the value axis
	    yAxis: {
	        min: 0,
	        max: 6000,

	        minorTickInterval: 'auto',
	        minorTickWidth: 1,
	        minorTickLength: 10,
	        minorTickPosition: 'inside',
	        minorTickColor: '#666',

	        tickPixelInterval: 30,
	        tickWidth: 2,
	        tickPosition: 'inside',
	        tickLength: 10,
	        tickColor: '#666',
	        labels: {
	            step: 2,
	            rotation: 'auto'
	        },
	        title: {
	            text: '[W]'
	        },
	        plotBands: [{
	            from: 0,
	            to: 6000,
	            color: '#DF5353' // red
	        }]
	    },
	    exporting: {
			enabled: false
		},
	    series: [{
	        name: 'Watt',
	        data: [0],
	        tooltip: {
	            valueSuffix: ' [W]'
	        }
	    }]

	},
	// Add some life
	function (chart) {
	    if (!chart.renderer.forExport) {
	        setInterval(function () {
	            var point = chart.series[0].points[0];
	            point.update(consumptiony);
	        }, 1000);
	    }
	});

	


$.getJSON("/data/latest_live_data", function(data){
	five_mins_initial_data = data
	load_5mins_chart();
});

$.getJSON("/data/last_day", function(data){
	last_24 = data;
	last_24_ts = last_24['aggregate_ts_ms_since_epoch']
	last_24_p_Wh = last_24['p_Wh']
	last_24_c_Wh = last_24['c_Wh']
	last_24_a_Wh = last_24['a_Wh']
	last_24_s_Wh = last_24['s_Wh']
	last_24_b_Wh = last_24['b_Wh']

	load_last_day_chart();
});

$.getJSON("/data/daily", function(data){
	daily = data;
	load_daily_chart();
});