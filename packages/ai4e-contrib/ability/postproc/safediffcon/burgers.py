"""上游 Burgers 差分求解器；原控制回放误差约1e-6。"""
import math
import numpy as np
import scipy.sparse as sp
import torch
import torch.nn.functional as F
import tqdm

def Diff_mat_1D(Nx, device='cpu'):
    # I tried to change the implementation to torch dense matrix here, but kept the original implem.
    # First derivative
    D_1d = sp.diags([-1, 1], [-1, 1], shape = (Nx,Nx)) # A division by (2*dx) is required later.
    D_1d = sp.lil_matrix(D_1d)
    D_1d[0,[0,1,2]] = [-3, 4, -1]               # this is 2nd order forward difference (2*dx division is required)
    D_1d[Nx-1,[Nx-3, Nx-2, Nx-1]] = [1, -4, 3]  # this is 2nd order backward difference (2*dx division is required)

    # Second derivative
    D2_1d = sp.diags([1, -2, 1], [-1,0,1], shape = (Nx, Nx)) # division by dx^2 required
    D2_1d = sp.lil_matrix(D2_1d)                  
    D2_1d[0,[0,1,2,3]] = [2, -5, 4, -1]                    # this is 2nd order forward difference. division by dx^2 required. 
    D2_1d[Nx-1,[Nx-4, Nx-3, Nx-2, Nx-1]] = [-1, 4, -5, 2]  # this is 2nd order backward difference. division by dx^2 required.
    

    return D_1d, D2_1d

def burgers_numeric_solve_free(u0, f, visc, T, dt=1e-4, num_t=10, mode=None):
    '''
    Simulates trajectories based on u0 and f. Trajectory i is based on u0[i, :]
    and f[i, :, :]

    Args:
        u0: (N,s), N is the number of samples (every sample has different u0 and f)
        f: (N,Nt,s)
        T: physical simulation time
        dt: physical simulation stepsize
        num_t: 
            number of sampling of times
            num of controllable forces (forces f_[i: i + T / dt] are the same)
    Returns:
        simulated u: (N_{u0 and f}, num_t, n_spatial_grids)
    '''
    if mode!='const':
        assert f.size()[1]==num_t, 'check number of time interval'
    else:
        raise ValueError


    #Grid size
    s = u0.size(-1)
    Nt = f.size(1)

    Nu0 = u0.size(0)
    Nf = f.size(0)
    assert Nu0 == Nf
    N = Nf
     
    xmin = 0.0; xmax = 1.0
    delta_x = (xmax-xmin)/(s+1)

    #Number of steps to final time
    steps = math.ceil(T/dt)

    u = u0.reshape(N, s)
    u = F.pad(u, (1,1))
    f = f.reshape(N, Nt, s)
    f = F.pad(f, (1,1))
    
    #Record solution every this number of steps
    record_time = math.floor(steps / Nt)
    
    D_1d, D2_1d = Diff_mat_1D(s + 2, device=u0.device)
    #remedy?
    D_1d.rows[0] = D_1d.rows[0][:2]
    D_1d.rows[-1] = D_1d.rows[-1][-2:]
    D_1d.data[0] = D_1d.data[0][:2]
    D_1d.data[-1] = D_1d.data[-1][-2:]
    
    D2_1d.rows[0] = D2_1d.rows[0][:3]
    D2_1d.rows[-1] = D2_1d.rows[-1][-3:]
    D2_1d.data[0] = D2_1d.data[0][:3]
    D2_1d.data[-1] = D2_1d.data[-1][-3:]
    
    t_sys_ind = list(D_1d.rows)
    t_sys = torch.FloatTensor(np.stack(D_1d.data)/(2*delta_x)).to(u0.device)
    d_sys_ind = list(D2_1d.rows)
    d_sys = torch.FloatTensor(visc*np.stack(D2_1d.data)/delta_x**2).to(u0.device)
    
    #Saving solution and time
    sol = torch.zeros(N, s, Nt, device=u0.device)
    
    #Record counter
    c = 0
    #Physical time
    t = 0.0
    f_idx = -1
    for j in tqdm.trange(steps):
        u = u[...,1:-1]
        u = F.pad(u, (1,1))
        
        u_s = u**2
        transport = torch.einsum('nsi,si->ns', u_s[...,t_sys_ind], t_sys)
        diffusion = torch.einsum('nsi,si->ns', u[...,d_sys_ind], d_sys)
        if j % record_time == 0:
            f_idx += 1
        u = u + dt * (-(1 / 2) * transport + diffusion + f[:, f_idx, :])
        
        #Update real time (used only for recording)
        t += dt

        if (j+1) % record_time == 0:

            #Record solution and time
            sol[...,c] = u[...,1:-1]
            c += 1

    sol = sol.permute(0, 2, 1) #(N, Nt, s)
    trajectory = torch.cat((u0.reshape(N, 1, s), sol), dim=1)
    return trajectory
