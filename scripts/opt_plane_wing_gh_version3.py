from topo_opt import TopoOpt
import taichi as tc

# Initialize
version = 0
n = 80
volume_fraction = 0.15
narrow_band = True

opt = TopoOpt(res=(n,n,n),version=version,volume_fraction=volume_fraction,grid_update_start=5 if narrow_band else 1000000,fix_cells_near_force=True,fix_cells_at_dirichlet=True,progressive_vol_frac=0,connectivity_filtering=True,fixed_cell_density=0.21)


tex = tc.Texture('mesh',translate=(0.5,0.5,0.5),scale=(1, 1, 1),adaptive=False,filename='projects/spgrid/data/box_test.obj')


opt.populate_grid(domain_type='texture', tex_id=tex.id)

opt.general_action(action='add_box_dirichlet_bc', axis_to_fix='xyz', bound0=(0.28, -0.48, -0.48), bound1=(0.48, 0.48, 0.48))

opt.add_plane_load(force=(0.0, 0.0, -10000.0),axis=2,extreme=-1,bound1=(-0.5, -0.5, -0.5),bound2=(-0.34, 0.5, 0.5))



# Optimize
opt.run()
