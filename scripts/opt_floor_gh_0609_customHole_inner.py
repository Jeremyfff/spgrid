import topo_opt
from topo_opt import TopoOpt
import taichi as tc
from imp import reload

def run(res, fraction, mirror, bound1, bound2, max_iterations, name):
    reload(topo_opt)

    # Initialize
    version = 0
    n = res
    volume_fraction = fraction
    narrow_band = True

    opt = TopoOpt(res=(n, n, n), version=version, volume_fraction=volume_fraction,
                  grid_update_start=5 if narrow_band else 1000000, fix_cells_near_force=False,
                  fix_cells_at_dirichlet=True, progressive_vol_frac=0, connectivity_filtering=True,
                  fixed_cell_density=0, boundary_smoothing_iters=3, smoothing_iters=1, cg_max_iterations=50,
                  custom_name=name)

    opt.populate_grid(domain_type='box', size=(0.5, 0.5, 0.1), mirror=mirror)

    opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, -0.5, -0.5),
                       bound1=(0.5, -0.45, 0.16))

    opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, -0.5, -0.5),
                       bound1=(-0.45, -0.45, 0.16))

    opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, 0.45, -0.5),
                       bound1=(0.5, 0.5, 0.16))

    opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, 0.45, -0.5),
                       bound1=(-0.45, 0.5, 0.16))

    opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='', bound0=bound1,
                       bound1=bound2)

    opt.add_plane_load(force=(0.0, 0.0, -10000.0), axis=2, extreme=-1, bound1=(-0.5, -0.5, -0.5),
                       bound2=(0.5, 0.5, 0.5))

    opt.max_iterations = max_iterations

    # Optimize
    opt.run()

    opt = None




