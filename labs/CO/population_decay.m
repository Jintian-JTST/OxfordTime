halflife_data = readmatrix('halflife.txt');
[num_cases, cols] = size(halflife_data);
N0 = 100;



function [Nx, Ny, Nz] = decay_populations(AX, AY, t, N0)
    t = t(:);         
    Nx = N0 * exp(-AX .* t);
    if abs(AX - AY) < 1e-10  
        A = AX;
        Ny = N0 * A .* t .* exp(-A .* t);
    else
        Ny = N0 * AX .* (exp(-AX .* t) - exp(-AY .* t))  ./ (AY - AX);
    end

    Nz = N0 - Nx - Ny;
end






for k = 1:num_cases
    T_half_X = halflife_data(k, 1);
    T_half_Y = halflife_data(k, 2);

    AX = log(2) / T_half_X;
    AY = log(2) / T_half_Y;
    
    t = (0:50).';
    
    [Nx, Ny, Nz] = decay_populations(AX, AY, t, N0);
    
    fprintf(' t(yr)      NX          NY          NZ\n');
    fprintf('%5d   %10.3f  %10.3f  %10.3f\n', [t Nx Ny Nz].');
    
    figure;
    plot(t, Nx, '-r', 'LineWidth', 1.5); 
    hold on;
    plot(t, Ny, '-g', 'LineWidth', 1.5);
    plot(t, Nz, '-b', 'LineWidth', 1.5);
    xlabel('T/yr');
    ylabel('N');
    legend('N_X','N_Y','N_Z','Location','best');
    title(sprintf('Nuclear decay: T_X = %.1f y, T_Y = %.1f y', T_half_X, T_half_Y));
    grid on;
    
    



    
    outfile = sprintf('decay_TX%.2g_TY%.2g.csv', T_half_X, T_half_Y);
    
    fid = fopen(outfile, 'w');
    fprintf(fid, 't_years,Nx,Ny,Nz\n');
    writematrix([t,Nx, Ny, Nz], outfile, 'WriteMode', 'append');
    fclose(fid);



end