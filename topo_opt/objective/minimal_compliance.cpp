#include "../spgrid_topo_opt.h"
#include <unordered_map>
#include <mutex>
#include <string>
#include <iostream>
#include <fstream>

TC_NAMESPACE_BEGIN

class MinimalCompliance : public Objective {
 public:
  using Base = Objective;

  TC_IO_DECL {
    TC_IO(config);
  }

  MinimalCompliance() : Objective() {
  }

  MinimalCompliance(const Dict &config) : Objective(config) {
  }

  void fem_solve() {
  }

  float64 compute(const Dict &param) override {
    fem_solve();
    auto &opt = config.get<SPGridTopologyOptimization3D &>("opt");
    //std::string working_directory = config.get("working_directory", "/tmp/");
    TC_INFO("=======WORKING DIRECTORY=======");
    std::string working_directory = param.get<std::string>("working_directory");
    TC_INFO(working_directory);
    TC_INFO("=======WORKING DIRECTORY=======");
    auto force_field = opt.config.get<real>("force_field", 0.0_f);
    auto height_reward = opt.config.get<real>("height_reward", 0.0_f);
    auto progressive_height_reward =
        opt.config.get<real>("progressive_height_reward", 0.0_f);
    int iter = param.get<int>("iter");

    auto forces = this->forces;

    auto get_force = [&](Vector3i i) -> Vector3 {
      return Vector3::axis(1) * (opt.i2f(i).y + 0.5_f);
    };
    auto &grid = opt.grid;
    auto dc0 = grid->dc0();

    auto sparse_u0 = grid->u0();
    auto sparse_u1 = grid->u1();
    auto sparse_u2 = grid->u2();

    TC_INFO("=======FORCES SIZE BEFORE=======");
    TC_P(forces.size());

    auto sparse_flags = grid->flags();
    auto sparse_density = grid->density();
    float64 objective = 0.0_f;
    if (force_field != 0) {
      // Note: this is not accurate
      for (auto ind : opt.get_cell_region()) {
        auto d = sparse_density(ind.get_ipos());
        auto f = get_force(ind.get_ipos()) * d;
        // forces.push_back(
        //    fem_interface::ForceOnNode{{ind.i, ind.j, ind.k}, {f.x, f.y,
        //    f.z}});
        auto p = opt.i2f(ind.get_ipos());
        auto y = p.y + 0.5_f;
        if (length(Vector2(p.x, p.z)) < 10.05) {
          objective += -y * d * height_reward;
        }

      }
    }
    TC_INFO("=======FORCES SIZE=======");
    TC_P(forces.size());

    bool success;
    TC_PROFILE(
        "fem solve",
        success = opt.fem_solve(iter, false, forces, boundary_condition));
    TC_ERROR_IF(!success, "FEM solve has failed.");

    constexpr int dim = Opt::dim;
    std::mutex mut;
    real penalty = opt.get_penalty(iter);
    std::atomic<int> has_negative_dc(0);
    std::cout << "=============================penalty: " << penalty << std::endl;
    std::cout << "=============================opt.minimum_stiffness: " << opt.minimum_stiffness << std::endl;



    //custom code start
    TC_INFO("=======CUSTOM CODE START=======");
    bool save_sum = false;
    if(iter % 10 == 0){
      save_sum = true;
    }
    //std::map<Opt::Vectori, float64> coord_sum_map;
    std::map<std::string, float64> coord_sum_map;
    std::mutex coord_sum_map_mutex;
    // std::mutex count_mutex;
    // int count = 0;


    //custom code end

    opt.parallel_for_each_block(  // 对于每一个block，默认情况下每个block包含4*4*4个单元
        opt.fat_page_map, // 使用的是扩展一圈的page map
        [&](int block_id, uint64 _, const Vector3i &base_coord) {
          Opt::Region region(Opt::Vectori(0), opt.block_size);
          float64 local_objective = 0.0_f;


          for (auto ind : region) {  // 对于block内的每个单元

            // count_mutex.lock();
            // count++;
            // count_mutex.unlock();

            Opt::Vectori coord = base_coord + ind.get_ipos(); // 获取坐标

            if (!sparse_flags(coord).get_inside_container()) {
              continue;
            }

            Opt::Region offset_region(Opt::Vectori(0), Opt::Vectori(2));
            float64 sum = 0.0f;
            std::vector<float64> row_sum(3, 0);

            // FEM kernel
            for (auto &offset_Kx : offset_region) {
              Opt::Vectori a = coord + offset_Kx.get_ipos();
              float64 a_u[3];
              auto offset_a = Opt::ChannelMask::Linear_Offset(a);
              a_u[0] = sparse_u0(offset_a);
              a_u[1] = sparse_u1(offset_a);
              a_u[2] = sparse_u2(offset_a);
              for (auto &offset_x : offset_region) {
                Opt::Vectori b = coord + offset_x.get_ipos();
                auto offset_b = Opt::ChannelMask::Linear_Offset(b);
                float64 b_u[3];
                b_u[0] = sparse_u0(offset_b);
                b_u[1] = sparse_u1(offset_b);
                b_u[2] = sparse_u2(offset_b);

                for (int i = 0; i < dim; i++) {
                  for (int j = 0; j < dim; j++) {
                    int row = opt.fem->get_index(offset_Kx, i);
                    int column = opt.fem->get_index(offset_x, j);
                    float64 coeff = opt.fem->Ke(row, column);
                    sum += a_u[i] * coeff * b_u[j];
                  }
                }
              }
            }
            float64 d = sparse_density(coord);
            // End of FEM kernel
            float64 dc = sum * std::pow(d, penalty - 1.0_f64) * penalty *
                         (1 - opt.minimum_stiffness);
            // https://link.springer.com/content/pdf/10.1007%2Fs001580050176.pdf
            // Eqn(4) Note: It is negative here. Let's stick to the standard.

            //custom code start
            if(save_sum){
              std::string coord_str = std::to_string(coord.x) + "," + std::to_string(coord.y) + "," + std::to_string(coord.z);
              coord_sum_map_mutex.lock();
              coord_sum_map[coord_str] = sum;
              coord_sum_map_mutex.unlock();
            }

            //custom code end
            auto grad = -dc;
            if (force_field != 0) {
              auto offset = Opt::ChannelMask::Linear_Offset(coord);
              Vector3 u;
              u[0] = sparse_u0(offset);
              u[1] = sparse_u1(offset);
              u[2] = sparse_u2(offset);
              auto f = get_force(coord);

              // grad -= 2 * dot(u, f);
              auto p = opt.i2f(coord);
              auto y = p.y + 0.5_f;
              if (length(Vector2(p.x, p.z)) < 110.1) {
                grad -= y * height_reward *
                        std::max(1 - 1.0_f * iter / progressive_height_reward,
                                 0.0_f);
              }
            }
            dc0(coord) += grad * weight;
            if (dc < 0) {
              has_negative_dc++;
            }
            local_objective +=
                sum * (opt.minimum_stiffness +
                       std::pow(d, penalty) * (1 - opt.minimum_stiffness));
          }
          {
            std::lock_guard<std::mutex> _(mut);
            objective += local_objective;
          }
        });


    //custom code start
    //after parallel
    // std::cout << "count: " << count << std::endl;
    // for (const auto& kvp : coord_sum_map) {
    //   const std::string& coord = kvp.first;
    //   float64 sum = kvp.second;
    //   std::cout << "Coord: [" << coord << "], Sum: " << sum << std::endl;
    // }

    if(save_sum){
      TC_INFO("========Start writing sum=========");
      FILE* sum_file;
      char sum_fn[200];
      sprintf(sum_fn,"%s/fem/%05d.sum",working_directory.c_str(),iter);
      sum_file = std::fopen(sum_fn,"w"); //打开文件
      for (const auto& kvp : coord_sum_map) {
        const std::string& coord = kvp.first;
        float64 sum = kvp.second;
        std::string output_str = fmt::format("{},{}\n",coord, sum);
        char output_char[output_str.size() + 1];
        std::strcpy(output_char, output_str.c_str());
        std::fwrite(output_char,1,sizeof(output_char),sum_file); //写入操作
      }
      std::fclose(sum_file); // close file
      TC_INFO("========writing complete=========");
    }




    //custom code end


    if (has_negative_dc) {
      TC_WARN("Negative dc detected {} ({:.2f}%)", has_negative_dc,
              100.0_f * has_negative_dc / opt.total_container_voxels);
    }
    // objective *= pow<2>(opt.dx);
    objective *= weight;
    TC_P(objective);
    return objective;
  }

  TC_NAME("minimal_compliance");
};

TC_IMPLEMENTATION_NEW(Objective, MinimalCompliance);

TC_NAMESPACE_END
