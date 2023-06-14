from topo_opt import TopoOpt
import taichi as tc

# Initialize
version = 0
n = 600
volume_fraction = 0.08
narrow_band = True

opt = TopoOpt(res=(n,n,n),
              version=version,
              volume_fraction=volume_fraction,
              grid_update_start=5 if narrow_band else 1000000,
              fix_cells_near_force=False,
              fix_cells_at_dirichlet=False,
              progressive_vol_frac=0,
              connectivity_filtering=True,
              fixed_cell_density=1,
              boundary_smoothing_iters=3,
              smoothing_iters=1,
              cg_max_iterations=50,
              custom_name='frac0.08_r600_mirror')


opt.populate_grid(domain_type='box', size=(0.5, 0.5, 0.05), mirror='xy')

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, -0.5, -0.5), bound1=(0.5, -0.45, 0.14))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, -0.5, -0.5), bound1=(-0.45, -0.45, 0.14))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, 0.45, -0.5), bound1=(0.5, 0.5, 0.14))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, 0.45, -0.5), bound1=(-0.45, 0.5, 0.14))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xy', bound0=(0.49, -0.5, -0.05), bound1=(0.5, 0.5, -0.04))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xy', bound0=(-0.5, 0.49, -0.05), bound1=(0.5, 0.5, -0.04))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xy', bound0=(-0.5, -0.5, -0.05), bound1=(-0.49, 0.5, -0.04))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xy', bound0=(-0.5, -0.5, -0.05), bound1=(0.5, -0.49, -0.04))

opt.add_plane_load(force=(0.0, 0.0, -10000.0),axis=2,extreme=-1,bound1=(-0.5, -0.5, -0.5),bound2=(0.5, 0.5, 0.5))


# Optimize
opt.run()

