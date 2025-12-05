N  = 1000;      
Nx = N;
Ny = 0;
Nz = 0;

T= 50;   
deltaT = 0.1;  
Nt = T / deltaT;

T_half_X = 2;
T_half_Y = 16;
alphaX   = log(2) / T_half_X;
alphaY  = log(2) / T_half_Y;
px= 1 - exp(-alphaX * deltaT);   
py= 1 - exp(-alphaY * deltaT);  



result = zeros(Nt+1, 4);
result(1,:)  = [0, Nx, Ny, Nz];


fprintf(' t(yr)      NX          NY          NZ\n');
fprintf('%5.1f   %10d  %10d  %10d\n', 0, Nx, Ny, Nz);

for k = 1:Nt
    Nx1=iteration(Nx, px);     
    decayX = Nx - Nx1;               
    Ny = Ny + decayX;

    Ny=iteration(Ny, py);      


    Nx = Nx1;
    Nz = N - Nx - Ny;                

    t_now = k * deltaT;

    fprintf('%5.1f   %10d  %10d  %10d\n', t_now, Nx, Ny, Nz);

    result(k+1, :) = [t_now, Nx, Ny, Nz];
end



figure;
plot(result(:,1), result(:,2), 'r');
hold on;
plot(result(:,1), result(:,3), 'g');
plot(result(:,1), result(:,4), 'b');

xlabel('T/yr');
ylabel('N');
legend('N_X','N_Y','N_Z','Location','best');
title('X Y Z');
grid on;



function Num = iteration(N, p)
    Num = 0;
    for i = 1:N
        if  rand() > p
            Num = Num + 1;
        end
    end
end

