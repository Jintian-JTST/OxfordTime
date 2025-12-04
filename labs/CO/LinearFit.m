data = readmatrix('linear.csv');

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

coe=Linear_Fit(data);

fprintf('coefficient a = %.6f, b = %.6f\n', coe(1), coe(2));

figure;
plot(x, y_err, 'o', 'DisplayName', 'data with noise');
hold on;
legend show;
grid on;
plot(x, y_fit, '-', 'LineWidth', 1.5, 'DisplayName', 'fitted curve');
xlabel('x');
ylabel('y');
title(sprintf('Polynomial fit of order m = %d', m));
