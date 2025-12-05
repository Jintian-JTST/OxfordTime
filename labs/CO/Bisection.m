f = @(x)   3 * exp(-x) - x + 3;

x0 =3;
x1 =5;
tolerance = 1e-6;
max_iterations = 100;

iteration = 0;
a=3;
while abs(x1 - x0) > tolerance
    fx0 = f(x0);
    fx1 = f(x1);

    x2=(x0+x1)/2;
    fx2=f(x2);

    if fx0 * fx2 < 0 
        x1 = x2; 
    else
        x0 = x2; 
    end

    %iteration = iteration + 1;
end

root = fzero(f, a);% inbuilt func in matlab
fprintf('The root is: %.6f\n', root);

fprintf('The root is: %.6f\n',(x0+x1)/2);