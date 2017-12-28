#set logscale y 10
set grid
plot 'time_data.txt' using 2  w lines title 'ADC [Volts]', '' using 3 w lines title '[Watt]' 

pause 1
reread