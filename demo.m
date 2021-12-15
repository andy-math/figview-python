clc();
clear();
m = py.importlib.import_module('client');
send = m.send;
for i = 1:50
	clf();
	hold on
	grid on
	plot(cumsum(randn(1,1000)));
	plot(cumsum(randn(1,1000)));
	plot(cumsum(randn(1,1000)));
	plot(cumsum(randn(1,1000)));
	plot(cumsum(randn(1,1000)));
	a = gca;
	[a.Children.LineWidth] = deal(1);
	legend('line1', 'line2', 'line3', 'line4', 'line5')
	print('-dsvg', 'test2.svg')
	send('test2.svg',i);
end