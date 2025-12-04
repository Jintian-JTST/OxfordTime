data = readmatrix('linear.csv');

x = data(:,1);
y = data(:,2);
N = length(x);

X = [N      sum(x);
     sum(x) sum(x.^2)];

Y = [sum(y);
     sum(x.*y)];

coe = X \ Y;   
fprintf('coefficient a = %.6f, b = %.6f\n', coe(1), coe(2));
