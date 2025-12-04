f = @(x)   3 * exp(-x) - x + 3;

x0 = 3;
x1 =5;
tolerance = 1e-6;
max_iterations = 100;

iteration = 0;

while iteration < max_iterations
    fx0 = f(x0);
    fx1 = f(x1);
    if fx1 == fx0
        break;
    end
    
    if abs(x1 - x0) < tolerance
        break;
    end
    
    x2=(x0+x1)/2;
    fx2=f(x2);

    if fx2 == 0
        break;
    elseif fx0 * fx2 < 0
        x1 = x2; 
    else
        x0 = x2; 
    end

    iteration = iteration + 1;
end

root = fzero(f, a);
fprintf('The root is: %.6f\n', root);
fprintf('The root is: %.6f\n',(x0+x1)/2);