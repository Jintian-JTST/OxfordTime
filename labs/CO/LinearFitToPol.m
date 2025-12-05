function data = curvefit_generate(n, m, a, e)
    x = linspace(-5, 5, n).';

    y = zeros(n,1);
    for k = 0:m
        y = y + a(k+1) * x.^k;
    end
    y_err = y + e * randn(n,1);
    data = [x, y_err];
end





function coe=Linear_Fit(data)

    x = data(:,1);
    y = data(:,2);
    N = length(x);
    
    X = [N      sum(x);
         sum(x) sum(x.^2)];
    
    Y = [sum(y);
         sum(x.*y)];
    
    coe = X \ Y;   


end

n = input('Enter number of data points n: ');
m = input('Enter order of polynomial m: ');
fprintf('Enter the %d coefficients a0, a1, ..., a_m as a row vector:\n', m+1);
a_true = input('e.g. [1.5 -2.5 0.7 -1.2]: ');
e = input('Enter experimental rms value e: ');

data=curvefit_generate(n,m,a_true,e);






coe=Linear_Fit(data);

fprintf('coefficient a = %.6f, b = %.6f\n', coe(1), coe(2));
x= data(:,1);
y_err = data(:,2);
a_fit =coe;
N = length(x);
A = ones(N, m+1);
for k = 1:m
    A(:, k+1) = x.^k;
end
y_fit = A * a_fit;



figure;
plot(x, y_err, 'o', 'DisplayName', 'data with noise');
hold on;
legend show;
grid on;
plot(x, y_fit, '-', 'LineWidth', 1.5, 'DisplayName', 'fitted curve');
xlabel('x');
ylabel('y');
title(sprintf('Polynomial fit of order m = %d', m));
