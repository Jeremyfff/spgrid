from topo_opt import TopoOpt
import taichi as tc

# Initialize
version = 0
n = 1200
volume_fraction = 0.05
narrow_band = True

opt = TopoOpt(res=(n,n,n),version=version,volume_fraction=volume_fraction,grid_update_start=5 if narrow_band else 1000000,fix_cells_near_force=False,fix_cells_at_dirichlet=False,progressive_vol_frac=5,connectivity_filtering=True,fixed_cell_density=0.5,boundary_smoothing_iters=3,smoothing_iters=1,cg_max_iterations=100)


opt.populate_grid(domain_type='box', size=(0.5, 0.5, 0.025), mirror='xy')

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, -0.5, -0.5), bound1=(0.5, -0.45, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.025, -0.5, -0.5), bound1=(0.025, -0.45, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, -0.5, -0.5), bound1=(-0.45, -0.45, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, -0.025, -0.5), bound1=(0.5, 0.025, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.025, -0.025, -0.5), bound1=(0.025, 0.025, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, -0.025, -0.5), bound1=(-0.45, 0.025, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.45, 0.45, -0.5), bound1=(0.5, 0.5, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.025, 0.45, -0.5), bound1=(0.025, 0.5, 0.16))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, 0.45, -0.5), bound1=(-0.45, 0.5, 0.16))

opt.add_plane_load(force=(0.0, 0.0, 10000.0),axis=2,extreme=-1,bound1=(-0.5, -0.5, -0.5),bound2=(0.5, 0.5, 0.5))



# Optimize
opt.run()
