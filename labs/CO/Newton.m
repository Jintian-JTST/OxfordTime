%Newton Raphson Method

f = @(x)   3 * exp(-x) - x + 3;
df = @(x)   -3 * exp(-x) - 1;

x0 = 3;

tolerance = 1e-6;
max_iterations = 100;

iteration = 0;

while iteration < max_iterations
    fx0 = f(x0);
    dfx0 = df(x0);
    if dfx0 == 0
        error('Derivative is zero. No solution found.');
    end
    x1 = x0 - fx0 / dfx0;
    if abs(x1 - x0) < tolerance
        break;
    end
    
    x0 = x1;
    iteration = iteration + 1;
end

root = fzero(f, a);
fprintf('The root is: %.6f\n', root);
fprintf('The root is: %.6f\n',(x0+x1)/2);