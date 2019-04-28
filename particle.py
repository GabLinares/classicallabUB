

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as pltanim
from numpy.polynomial.polynomial import Polynomial
from scipy.interpolate import interp1d
from potentials import *



L = 200


T = 30
dt = 0.1
nt = int(T/dt) 


class Phi():
    
    def __init__(self):
        self.functions = np.array([])
        self.dfunctionsx = np.array([])
        self.dfunctionsy = np.array([])
    def add_function(self,fun,dfunx,dfuny,param):
        self.functions = np.append(self.functions,(fun,param))
#        self.functions = np.append(self.functions,param)
        self.dfunctionsx = np.append(self.dfunctionsx,(dfunx,param))
#        self.derivatives = np.append(self.derivatives,param)
        self.dfunctionsy = np.append(self.dfunctionsy,(dfuny,param))
        return
    def val(self,x,y):
        value = 0
        r = (x,y)
        for i in range(0,self.functions.shape[0],2):
            value = value + self.functions[0](r,self.functions[i+1])
        return value
    def dvalx(self,x,y):
        value = 0
        r = (x,y)
        for i in range(0,self.dfunctionsx.shape[0],2):
            value = value + self.dfunctionsx[0](r,self.dfunctionsx[i+1])
        return value
    def dvaly(self,x,y):
        value = 0
        r = (x,y)
        for i in range(0,self.dfunctionsy.shape[0],2):
            value = value + self.dfunctionsy[0](r,self.dfunctionsy[i+1])
        return value

    def clear(self):
        self.functions = np.array([])
        self.dfunctionsx = np.array([])
        self.dfunctionsy = np.array([])
        


class Particle():
    
    def __init__(self,mass,charge,tra,dt):
        self.mass = mass
        self.charge = charge
        self.trajectory = tra
        self.dt = dt
        self.steps = np.array([0])
        self.h = 1
    
    def RightHand(self,r):

        f = np.zeros([4])
        f[0] = r[2]
        f[1] = r[3]
        f[2] = -pot.dvalx(r[0],r[1])/self.mass
        f[3] = -pot.dvaly(r[0],r[1])/self.mass
        return f
    
    def RK4(self,t,dt,r):
        k1 = self.RightHand(r)
        k2 = self.RightHand(r+k1*self.dt/2)
        k3 = self.RightHand(r+k2*self.dt/2)
        k4 = self.RightHand(r+k3*self.dt)
    
        rlater = r + self.dt/6 * (k1 + 2*k2 + 2*k3 + k4)
        return rlater
    
    def RKF(self,r):
        eps = 0.000001
        hnew = dt
        safety = 0
        while(hnew<self.h):
            safety += 1
            if(safety>10):
                break
            
            self.h = hnew
            k0 = self.RightHand(r)
            k1 = self.RightHand(r + self.h/4.*k0)
            k2 = self.RightHand(r + (3.*self.h/32.)*k0 + (9.*self.h/32.)*k1)
            k3 = self.RightHand(r + (1932.*self.h/2197.)*k0 - (7200.*self.h/2197.)*k1 + (7296.*self.h/2197.)*k2)
            k4 = self.RightHand(r + (439.*self.h/216.)*k0 - 8.*self.h*k1 + (3680.*self.h/513.)*k2 - (845.*self.h/4104.)*k3)
            k5 = self.RightHand(r - (8.*self.h/27.)*k0 + 2.*self.h*k1 - (3544.*self.h/2565.)*k2 + (1859.*self.h/4104.)*k3 - (11.*self.h/40.)*k4)
#            rnext = r + h*(25*k0/256 + 1408*k2/2565 + 2197*k3*4104 - k4/5)
            rnexthat = r + (16.*self.h/135.)*k0 + (6656.*self.h/12825.)*k2 + (28561.*self.h/56430.)*k3 - (9.*self.h/50.)*k4 + (2.*self.h/55.)*k5
            delta = self.h*((1./360.)*k0 - (128./4275.)*k2 - (2197./75240.)*k3 + (1./50.)*k4 + (2./55.)*k5)
#            '''
            if(np.sqrt(np.sum(delta**2))>eps):
#            try:
                hnew = 0.9*self.h*(np.abs(self.h)*eps/np.sqrt(np.sum(delta**2)))**(1./4.)
#            except RuntimeWarning:
            else:
                hnew = dt
            
            if(hnew>dt):
                hnew = dt
        self.h = hnew
        hfinal = hnew
        rlater = rnexthat
        return rlater,hfinal
    
    
    
    
    def ComputeTrajectory(self,r0):
        self.trajectory[0,:] = r0
        self.steps = np.array([0])
        for i in range(0,nt):
            try:
                tranext = self.RK4(i*self.dt,self.dt,self.trajectory[i,:])
                if(np.abs(tranext[0]) >= L/2 or np.abs(tranext[1]) >= L/2):
                    break
                else:
                    self.trajectory = np.append(self.trajectory,tranext.reshape(1,4),axis=0)
            except IndexError:
                break
            
    def ComputeTrajectoryF(self,r0):
        self.trajectory[0,:] = r0
        i = 0
        while(self.steps.sum() < T):
            self.h = 1
            try:
                tranext , newstep = self.RKF(self.trajectory[i,:])
                if(np.abs(tranext[0]) >= L/2 or np.abs(tranext[1]) >= L/2):
                    break
                else:
                    self.trajectory = np.append(self.trajectory,tranext.reshape(1,4),axis=0)
                    self.steps = np.append(self.steps,newstep)
                    i += 1
            except IndexError:
                break
                
    def KEnergy(self):
        KEnergy = np.zeros([self.trajectory.shape[0]])
        for i in range(0,self.trajectory.shape[0]):
            KEnergy[i] = self.mass/2. * (self.trajectory[i,2]**2+self.trajectory[i,3]**2)
        return KEnergy
    
    def PEnergy(self):
        PEnergy = np.zeros(self.trajectory.shape[0])
        for k in range(0,self.trajectory.shape[0]):
            PEnergy[k] = pot.val(self.trajectory[k,0],self.trajectory[k,1])
        return PEnergy 
            
    def Energy(self):
        E = np.zeros([self.trajectory.shape[0]])
        for i in range(0,self.trajectory.shape[0]):
            E[i] = self.KEnergy()[i] + self.PEnergy()[i]
        return E
    
pot = Phi()



#pot.add_function(woodsaxon,dwoodsaxonx,dwoodsaxony,[50,-10,-500,10,0.3])
#pot.add_function(woodsaxon,dwoodsaxonx,dwoodsaxony,[0,75,-500,10,0.3])
pot.add_function(gauss,dgaussx,dgaussy,[50,-2,100,5])
pot.add_function(gauss,dgaussx,dgaussy,[5,70,100,5])
pot.add_function(gauss,dgaussx,dgaussy,[-75,3,100,5])
#pot.add_function(rect,drectx,drecty,[25,0,100,20,20])



dx = 1
nx = int(L/dx)
xx,yy, = np.meshgrid(np.linspace(-L/2,L/2,nx,endpoint=True),np.linspace(-L/2,L/2,nx,endpoint=True))
im = np.zeros((nx,nx))
for i in range(0,nx):
    for j in range(0,nx):
        im[i,j] = pot.val(xx[i,j],yy[i,j])

p = Particle(1,1,np.ones([1,4]),dt)
p.ComputeTrajectoryF(np.array([0,0,10,0]))    
a = p.trajectory
b = p.steps
t = p.steps.cumsum()
#t = dt*np.ones(a.shape[0]).cumsum()

'''
fun = np.zeros(nx)
xs = np.zeros(nx)
for i in range(0,nx):
    x = i*dx - L/2
    y = 0
    xs[i] = x 
    fun[i] = pot.dvalx(x,y)
plt.figure()
plt.plot(xs,fun)
'''

#'''
plt.figure()
plt.subplot(3,3,1)
plt.contourf(xx,yy,im,cmap="inferno")
plt.colorbar()
plt.axis("square")
plt.xlabel('x([L])')
plt.ylabel('y([L])')

plt.subplot(3,3,2)
plt.plot(t,p.KEnergy(),"r-",t,p.PEnergy(),"b-",t,p.Energy(),"g-")
plt.legend(('EC','EP','EM'),loc='best')
plt.xlabel('t([T])')
plt.ylabel('Energy([M]*[L]^2*[T]^-2)')

plt.subplot(3,3,3)
plt.plot(a[:,0],a[:,1])
plt.xlabel('x([L])')
plt.ylabel('y([L])')
plt.axis((-100,100,-100,100),'square')

plt.subplot(3,2,3)
plt.plot(t,a[:,0])
plt.xlabel('t([T])')
plt.ylabel('x([L])')

plt.subplot(3,2,4)
plt.plot(t,a[:,1])
plt.xlabel('t([T])')
plt.ylabel('y([L])')

plt.subplot(3,2,5)
plt.plot(a[:,0],a[:,2])
plt.xlabel('x([L])')
plt.ylabel('x([L][T]^-1)')
plt.axis((-100,100,-100,100),'square')

plt.subplot(3,2,6)
plt.plot(a[:,1],a[:,3])
plt.xlabel('y([L])')
plt.ylabel('vy([L][T]^-1)')
plt.axis((-100,100,-100,100),'square')

#plt.tight_layout()
plt.show()


'''
#trax = np.poly1d(np.polyfit(t,a[:,0],2))
#trax = Polynomial.fit(t,a[:,0],1)
times = interp1d(t,t)
trax = interp1d(t,a[:,0],kind='quadratic')
tray = interp1d(t,a[:,1],kind='quadratic')


def background():
    plt.contourf(xx,yy,im,cmap="inferno")
    plt.colorbar()
    return image,



def animation(frame):
    inst = frame*(1./25.)
    image.set_data(trax(inst),tray(inst))
    return image,


fps = 25
freqms = (1./25.)*1000
totalframes = int(fps*t.max()) + 1



Writer = pltanim.writers['ffmpeg']
writer = Writer(fps=fps, metadata=dict(artist='Me'), bitrate=3600)


anim = plt.figure()
image, = plt.plot([],[],'w.',markersize=10)
plt.axis((-100,100,-100,100),'square')
video = FuncAnimation(anim,animation,init_func=background,frames=totalframes,interval=freqms,blit='True')

video.save('video.mp4',writer=writer)
'''

