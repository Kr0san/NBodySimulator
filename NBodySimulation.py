import rebound
import numpy as np


class NBodySimulation:
    def __init__(self, duration=1000, steps=5000, integrator='IAS15', center=False):
        self.sim = rebound.Simulation()
        self.duration = duration
        self.steps = steps
        self.sim.integrator = integrator
        self.center = center

    @property
    def objects(self):
        """
        Returns the number of objects

        Returns
        -------
            int
        """
        return len(self.sim.particles)

    def add_particle(self, mass, x, y, z, vx, vy, vz):
        """
        This method adds a new particle to the simulation.

        Parameters
        ----------
        mass    :   float
            Mass of the object in solar masses.
        x       :   float
            Positional coordinate of x.
        y       :   float
            Positional coordinate of y.
        z       :   float
            Positional coordinate of z.
        vx      :   float
            Velocity of x coordinate.
        vy      :   float
            Velocity of y coordinate.
        vz      :   float
            Velocity of z coordinate.
        """
        self.sim.add(m=mass, x=x, y=y, z=z, vx=vx, vy=vy, vz=vz)

    def simulate(self):
        """
        This method runs simulation for the given duration.
        """
        if self.center:
            self.sim.move_to_com()
        self.sim.integrate(self.duration)

    def simulation(self):
        """
        This method simulates Nbody trajectories for the given duration and step size and returns a three-dimensional
        array of x, y and z values that can be used for 3d plotting.

        Returns
        -------
            list, list, list
        """
        if self.center:
            self.sim.move_to_com()

        x_pos = np.empty((self.objects, self.steps))
        y_pos = np.empty((self.objects, self.steps))
        z_pos = np.empty((self.objects, self.steps))
        times = np.linspace(0, self.duration, self.steps)

        for i, t in enumerate(times):
            self.sim.integrate(t)
            for k in range(self.objects):
                x_pos[k, i] = self.sim.particles[k].x
                y_pos[k, i] = self.sim.particles[k].y
                z_pos[k, i] = self.sim.particles[k].z

        return x_pos, y_pos, z_pos

    def output(self):
        """
        Returns the output of the simulation

        Returns
        -------
            str
        """
        return self.sim.status()
