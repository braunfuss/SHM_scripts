import numpy as num
import os
try:
    from pyrocko import cake
except:
    print("Pyrocko is not installed, please Please follow the instructions at https://pyrocko.org/docs/current/install/system/linux/index.html")
km = 1000.


def convert2shm_ttt(mod, phase, distances, depths,
                    ngridp_x, ngrid_z,
                    name="model_name"):
    """
    Calculate the traveltimes for a single given phase and for for given distaces
    and depths using the cake module from pyrocko and save the output in SHM TTT format.

    Parameters
    ----------
    mod : Object, loaded velocity model in cake format (see example_mod.pf)
    phase : String, name of phase to be used, suitable are pyrocko cake classic Names:
                    Pg, P, S, Sg,
                    PmP, PmS, PcP, PcS, SmP, ...,
                    PP, SS, PS, SP, PPP, ...,
                    Pc, Pdiff, Sc, ...,
    distances: List of two floats, minimum distance and maximum distance in km
    depths: List of two floats, minimum depth and maximum depth in km
    ngridp_x: int, number of grid points in x direction [km]
    ngridp_z: int, number of grid points in z direction [km]
    name: str, optional, the model name to be used for saving
    Returns
    -------
    None

    Output
    -------
    Saves a texfile with the traveltime table for SHM
    """
    # define cake phase to be used
    phases = cake.PhaseDef.classic(phase)

    # define distances and depth (both in km)
    distances = num.linspace(distances[0], distances[1], ngridp_x)*km
    distances = distances * cake.m2d
    depths = num.linspace(depths[0], depths[1], ngrid_z)*km

    fobj = open('%s_%s.TTT' % (name, phase), 'w')

    # make header
    fobj.write('TTT\n')
    fobj.write('distance bounds\n')
    fobj.write('%s %s \n' % (num.min(distances), num.max(distances)))
    fobj.write('depth steps\n')
    for depth in depths:
        fobj.write('%02s ' % num.round(depth/1000, 1))
    fobj.write('\n')

    # write out time per distance/depth
    data = []
    for distance in distances:
        fobj.write(' %02s ' % distance)

        for depth in depths:
            rays = mod.arrivals(
                phases=phases, distances=[distance], zstart=depth)
            for ray in rays[:1]:
                data.append((distance, ray.t))
                ttt = ray.t
            try:
                fobj.write('%s ' % num.round(ttt, 2))
            except:
                print("Phase %s is not defined for this distance %s and depth %s" % (phase, distance, depth))
        fobj.write('\n')
    fobj.close()


def convert2locsat_ttt(mod, phase, distances, depths,
                       ngridp_x, ngrid_z, name="model_name"):
    """
    Calculate the traveltimes for a single given phase and for for given distances
    and depths using the cake module from pyrocko and save the output in locsat format.

    Parameters
    ----------
    mod : Object, loaded velocity model in cake format (see example_mod.pf)
    phase : String, name of phase to be used, suitable are pyrocko cake classic Names:
                    Pg, P, S, Sg,
                    PmP, PmS, PcP, PcS, SmP, ...,
                    PP, SS, PS, SP, PPP, ...,
                    Pc, Pdiff, Sc, ...,
    distances: List of two floats, minimum distance and maximum distance in km
    depths: List of two floats, minimum depth and maximum depth in km
    ngridp_x: int, number of grid points in x direction [km]
    ngridp_z: int, number of grid points in z direction [km]
    name: str, optional, the model name to be used for saving
    Returns
    -------
    None

    Output
    -------
    Saves a texfile with the traveltime table for locsat
    """
    # define phase
    phases = cake.PhaseDef.classic(phase)

    # define distances and depth (both in km)
    distances = num.linspace(distances[0]*km, distances[1]*km, ngridp_x*km)
    distances = distances * cake.m2d
    depths = num.linspace(depths[0]*km, depths[1]*km, ngrid_z*km)
    fobj = open('%s.%s' % (name, phase), 'w')

    # make header
    fobj.write('n # %s     travel-time (and amplitude) tables \n' % phase)
    fobj.write(' %s # number of depth samples\n' % len(depths))
    fobj.write('    ')

    for depth in depths:
        depth = num.round(depth/1000, 2)
        fobj.write('%s   ' % (depth))
    fobj.write('\n')
    fobj.write('%s # number of distance samples\n' % len(distances))
    fobj.write('    ')
    for distance in distances:
        fobj.write('%s   ' % num.round(distance, 2))
    # write out time per distance/depth
    data = []
    fobj.write('\n')

    for depth in depths:
        depth_print = num.round(depth/1000, 2)
        fobj.write('# Travel-time/amplitude for z =    %s \n' % depth_print)

        for distance in distances:

            rays = mod.arrivals(
                phases=phases, distances=[distance], zstart=depth)

            for ray in rays[:1]:
                data.append((distance, ray.t))
                ttt = ray.t
            if ttt is None:
                ttt = 0
            fobj.write('     %s ' % num.round(ttt, 3))
            fobj.write('\n')
    fobj.close()


def main(phases_calc, distances, depths, ngridp_x, ngrid_z, model=None, plot=False, sdepth_plot=10):
    # define Earth structure model in cake format to be used
    mod = cake.load_model(model)
    if plot is True:
        os.system("cake plot-model --model=%s" % model)

    #for phase in phases_calc:
    if plot is True:
        sdepth = sdepth_plot # depth of source to plot
        phases_plot = ""
        for phase in phases_calc:
            phases_plot = phases_plot+"%s," %phase
        os.system("cake plot-rays --model=%s --classic=%s --sdepth=%s --distances=%s:%s:%s" %(model, phases_plot[:-1], sdepth, distances[0], distances[1], ngridp_x))

    for phase in phases_calc:
        convert2shm_ttt(mod, phase, distances, depths, ngridp_x, ngrid_z,
                        name="example_output")


'''
Example configuration
'''
# calculate two grids, one for Pg and one for Sg
# Use cake print to discover the suitable classic phase names.
# E.g. classic names: Pg, P, S, Sg, PmP, PmS, PcP, PcS, SmP, ...,
# PP, SS, PS, SP, PPP, ..., Pc, Pdiff, Sc, ...,
phases_calc = ["Pg"]

distances = [10, 100]
depths = [10, 20]

ngridp_x = 10
ngrid_z = 10
main(phases_calc, distances, depths, ngridp_x, ngrid_z, model="example_vel.mod", plot=True,)
