var consumptionserie = {};
var consumptiony = 0;
var productiony = 0

function load_charts() {
	Highcharts.chart('top_left', {
			chart: {
				type: 'areaspline',
				height : 300
			},
			credits: {
		      enabled: false
		  	},
			title: {
				text: 'Last Day'
			},
			subtitle: {
				text: 'Prodution VS consumption'
			},
			xAxis: {
				allowDecimals: false,
				labels: {
					formatter: function () {
						return this.value; // clean, unformatted number for year
					}
				}
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
				pointFormat: '{series.name} produced <b>{point.y:,.0f}</b><br/>warheads in {point.x}'
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
			series: [{
				name: 'Consumption [W]',
				color: '#DF5353',
				data: [null, null, null, null, null, 6, 11, 32, 110, 235, 369, 640,
					1005, 1436, 2063, 3057, 4618, 6444, 9822, 15468, 20434, 24126,
					27387, 29459, 31056, 31982, 32040, 31233, 29224, 27342, 26662,
					26956, 27912, 28999, 28965, 27826, 25579, 25722, 24826, 24605,
					24304, 23464, 23708, 24099, 24357, 24237, 24401, 24344, 23586,
					22380, 21004, 17287, 14747, 13076, 12555, 12144, 11009, 10950,
					10871, 10824, 10577, 10527, 10475, 10421, 10358, 10295, 10104]
			}, {
				name: 'Production [W]',
				color: '#55BF3B',
				data: [null, null, null, null, null, null, null, null, null, null,
					5, 25, 50, 120, 150, 200, 426, 660, 869, 1060, 1605, 2471, 3322,
					4238, 5221, 6129, 7089, 8339, 9399, 10538, 11643, 13092, 14478,
					15915, 17385, 19055, 21205, 23044, 25393, 27935, 30062, 32049,
					33952, 35804, 37431, 39197, 45000, 43000, 41000, 39000, 37000,
					35000, 33000, 31000, 29000, 27000, 25000, 24000, 23000, 22000,
					21000, 20000, 19000, 18000, 18000, 17000, 16000]
			}] 
		});
		Highcharts.setOptions({
		global: {
			useUTC: false
		}
	});

	Highcharts.chart('top_right', {
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
				var data = []
				for (var i = 0; i < consumptionserie['ts_ms_since_epoch'].length; i++) {
						var point = { 
							x: consumptionserie['ts_ms_since_epoch'][i], 
							y: consumptionserie['c_W'][i]
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
				// generate an array of random data
				var data = [],
					time = (new Date()).getTime(),
					i,
					productiony = 0;
				
				for (i = -360; i <= 0; i += 1) {
					$.getJSON("/data/production/live", function(data){productiony = data});
					data.push({
						x: time + i * 1000,
						y: productiony
					});
				}
				return data;
			}())
		}]
	});


	Highcharts.chart('gauge_production', 
		{
		    chart: {
		        type: 'gauge',
		        plotBackgroundColor: null,
		        plotBackgroundImage: null,
		        plotBorderWidth: 0,
		        plotShadow: false,
		        height : 250
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
		        height : 250
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

	Highcharts.chart('daily_energy', {
	    chart: {
	        type: 'column',
	        height:250
	    },
	    title: {
	        text: 'Daily KWh'
	    },
	    xAxis: {
	        categories: ['15/11','16/11']
	    },
	    yAxis: {
	        min: 0,
	        title: {
	            text: '[KWh]',
	           
	        },
	        labels: {
	            overflow: 'justify'
	        }
	    },
	    tooltip: {
	        valueSuffix: ' millions'
	    },
	    plotOptions: {
	        bar: {
	            dataLabels: {
	                enabled: true
	            }
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
	        name: 'Produced',
	        data: [107, 200],
	        color: 'rgba(0,165,0,0.5)',
	        pointPlacement: 0.15,
	        pointPadding: 0.3
	    }, {
	        name: 'Auto-consumed',
	        data: [40, 30],
	        color: 'rgba(0,165,0,0.8)'
	    }, {
	        name: 'Consumed',
	        data: [145, 80],
	        color: 'rgba(165,0,0,0.5)',
	        pointPadding: 0.3
	    }, {
	        name: 'Bought',
	        data: [105, 50],
	        color: 'rgba(165,0,0,0.8)',
	        pointPlacement: -0.15
	    }]
	});
}

$.getJSON("/data/latest_live_data", function(data){
	consumptionserie = data
	load_charts();
});
