from topo_opt import TopoOpt
import taichi as tc

# Initialize
version = 0
n = 500
volume_fraction = 0.8
narrow_band = True

opt = TopoOpt(res=(n,n,n),version=version,volume_fraction=volume_fraction,grid_update_start=5 if narrow_band else 1000000,fix_cells_near_force=False,fix_cells_at_dirichlet=True,progressive_vol_frac=0,connectivity_filtering=True,fixed_cell_density=0.5)


tex = tc.Texture('mesh',translate=(0.5,0.5,0.5),scale=(1, 1, 1),adaptive=False,filename='projects/spgrid/data/floor_test3_result.obj')


opt.populate_grid(domain_type='texture', tex_id=tex.id, mirror='xy')

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.38, -0.5, -0.5), bound1=(0.5, -0.38, 0.28))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.38, 0.38, -0.5), bound1=(0.5, 0.5, 0.28))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, 0.38, -0.5), bound1=(-0.38, 0.5, 0.28))

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(-0.5, -0.5, -0.5), bound1=(-0.38, -0.38, 0.28))

opt.general_action(action='add_mesh_normal_force',mesh_fn='projects/spgrid/data/floor_test3_result.obj',magnitude=-1,center=(0,0,0),falloff=5000,maximum_distance=0.015,override=(0,0,0))



# Optimize
opt.run()

