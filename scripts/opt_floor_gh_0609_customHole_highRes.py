from topo_opt import TopoOpt
import taichi as tc

# Initialize
version = 0
n = 600
volume_fraction = 0.2
narrow_band = True

opt = TopoOpt(res=(n,n,n),version=version,volume_fraction=volume_fraction,grid_update_start=5 if narrow_band else 1000000,fix_cells_near_force=False,fix_cells_at_dirichlet=True,progressive_vol_frac=0,connectivity_filtering=True,fixed_cell_density=0,boundary_smoothing_iters=3,smoothing_iters=1,cg_max_iterations=50,
              custom_name='opt_customHole_highRes_600')


opt.populate_grid(domain_type='box', size=(0.5, 0.5, 0.1), mirror='xy')

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, -0.5, -0.5), bound1=(0.5, -0.45, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, -0.5, -0.5), bound1=(-0.45, -0.45, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, 0.45, -0.5), bound1=(0.5, 0.5, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, 0.45, -0.5), bound1=(-0.45, 0.5, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='y', bound0=(-0.12, -0.5, -0.05), bound1=(0.12, 0.5, 0.05))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='x', bound0=(-0.5, -0.12, -0.05), bound1=(0.5, 0.12, 0.05))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='', bound0=(-0.5, 0.26, -0.03), bound1=(0.5, 0.34, 0.03))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='', bound0=(-0.5, -0.34, -0.03), bound1=(0.5, -0.26, 0.03))

opt.add_plane_load(force=(0.0, 0.0, -10000.0),axis=2,extreme=-1,bound1=(-0.5, -0.5, -0.5),bound2=(0.5, 0.5, 0.5))


opt.max_iterations = 151

# Optimize
opt.run()

