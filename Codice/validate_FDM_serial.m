xL = 0;
xR = 1;
N = 1000;
h = (xR-xL)/(N+1);
f = @(x) -exp(x);
u_exact = @(x) exp(x);
uL = u_exact(xL);
uR = u_exact(xR);
x_bc = linspace(xL,xR,N+2)';
x = x_bc(2:end-1);
slope = (uR-uL)/(xR-xL);
u0 = slope*(x-xL)+uL;

b = h*h*f(x);
b(1) = b(1) + uL;
b(end) = b(end) + uR;

e = ones(N,1);
A = spdiags([-e, 2*e, -e],-1:1,N,N);
M1 = speye(size(A));
M2 = speye(size(A));
tol = 1e-8;
maxit = 2*N;
tic();
[u,flag,relres,iter,resvec] = pcg(A,b,tol,maxit,[],[],u0);
dt = toc();
fprintf("Time per iteration per unknown: %f ns\n", 1e9 * dt / (iter * N));

err = u - u_exact(x);
err_Linf = max(abs(err));
fprintf("Error in Linf norm: %e\n",err_Linf);


