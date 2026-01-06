"""
Intel GPU 压力测试程序
支持 Intel Arc Graphics 和其他 Intel 集成显卡
使用 PyOpenCL (支持 Intel GPU)
"""

import numpy as np
import time
import sys

# 检查 PyOpenCL
try:
    import pyopencl as cl
    print("✓ PyOpenCL 已安装")
except ImportError:
    print("❌ 未安装 PyOpenCL")
    print("请运行: pip install pyopencl")
    sys.exit(1)


class IntelGPUStressTest:
    def __init__(self, intensity=50):
        self.intensity = intensity
        self.running = False
        self.ctx = None
        self.queue = None
        self.setup_opencl()
    
    def setup_opencl(self):
        """设置 OpenCL 环境，选择 Intel GPU"""
        print("\n正在查找 Intel GPU...")
        
        platforms = cl.get_platforms()
        intel_device = None
        
        # 查找 Intel GPU
        for platform in platforms:
            print(f"\n平台: {platform.name}")
            devices = platform.get_devices()
            
            for device in devices:
                print(f"  设备: {device.name}")
                print(f"    类型: {cl.device_type.to_string(device.type)}")
                print(f"    供应商: {device.vendor}")
                
                # 选择 Intel GPU
                if "Intel" in device.vendor or "Intel" in device.name:
                    if device.type == cl.device_type.GPU:
                        intel_device = device
                        print(f"  ✓ 选中此设备")
                        break
            
            if intel_device:
                break
        
        if intel_device is None:
            print("\n❌ 未找到 Intel GPU，使用第一个可用设备")
            intel_device = platforms[0].get_devices()[0]
        
        # 创建上下文和队列
        self.ctx = cl.Context([intel_device])
        self.queue = cl.CommandQueue(self.ctx)
        
        print(f"\n使用设备: {intel_device.name}")
        print(f"最大计算单元: {intel_device.max_compute_units}")
        print(f"最大工作组大小: {intel_device.max_work_group_size}")
        print(f"全局内存: {intel_device.global_mem_size / 1024**3:.2f} GB")
    
    def run_stress_test(self):
        """运行 GPU 压力测试"""
        print(f"\n{'='*60}")
        print(f"开始 Intel GPU 压力测试 (强度: {self.intensity}%)")
        print(f"{'='*60}")
        print("按 Ctrl+C 停止测试\n")
        
        # OpenCL 内核代码 - 多种计算密集型操作
        kernel_code = """
        // 矩阵乘法
        __kernel void matrix_multiply(
            __global const float* A,
            __global const float* B,
            __global float* C,
            const int N)
        {
            int row = get_global_id(0);
            int col = get_global_id(1);
            
            if (row < N && col < N) {
                float sum = 0.0f;
                for (int k = 0; k < N; k++) {
                    sum += A[row * N + k] * B[k * N + col];
                }
                C[row * N + col] = sum;
            }
        }
        
        // 计算密集型操作
        __kernel void compute_intensive(
            __global float* data,
            const int iterations)
        {
            int idx = get_global_id(0);
            float val = data[idx];
            
            // 大量三角函数和数学运算
            for (int i = 0; i < iterations; i++) {
                val = sin(val) * cos(val);
                val = exp(val * 0.1f);
                val = sqrt(fabs(val));
                val = log(fabs(val) + 1.0f);
                val = pow(fabs(val), 0.5f);
            }
            
            data[idx] = val;
        }
        
        // Mandelbrot 分形计算
        __kernel void mandelbrot(
            __global float* output,
            const int width,
            const int height,
            const int max_iter)
        {
            int x = get_global_id(0);
            int y = get_global_id(1);
            
            if (x >= width || y >= height) return;
            
            float cx = (x - width/2.0f) * 4.0f / width;
            float cy = (y - height/2.0f) * 4.0f / height;
            
            float zx = 0.0f, zy = 0.0f;
            int iter = 0;
            
            while (zx*zx + zy*zy < 4.0f && iter < max_iter) {
                float tmp = zx*zx - zy*zy + cx;
                zy = 2.0f * zx * zy + cy;
                zx = tmp;
                iter++;
            }
            
            output[y * width + x] = (float)iter / max_iter;
        }
        """
        
        # 编译内核
        prg = cl.Program(self.ctx, kernel_code).build()
        
        # 根据强度调整参数
        base_size = 800
        matrix_size = int(base_size + (self.intensity * 10))
        compute_iters = int(50 + (self.intensity * 2))
        mandelbrot_size = int(1000 + (self.intensity * 20))
        max_mandelbrot_iter = int(100 + self.intensity * 5)
        
        iteration = 0
        start_time = time.time()
        
        try:
            while self.running:
                iter_start = time.time()
                
                # ========== 任务 1: 矩阵乘法 ==========
                N = matrix_size
                A = np.random.rand(N, N).astype(np.float32)
                B = np.random.rand(N, N).astype(np.float32)
                C = np.zeros((N, N), dtype=np.float32)
                
                mf = cl.mem_flags
                A_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
                B_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=B)
                C_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, C.nbytes)
                
                prg.matrix_multiply(self.queue, (N, N), None, A_buf, B_buf, C_buf, np.int32(N))
                
                # ========== 任务 2: 计算密集型操作 ==========
                data_size = N * N
                data = np.random.rand(data_size).astype(np.float32)
                data_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=data)
                
                prg.compute_intensive(self.queue, (data_size,), None, data_buf, np.int32(compute_iters))
                
                # ========== 任务 3: Mandelbrot 分形 ==========
                width = height = mandelbrot_size
                mandel_output = np.zeros(width * height, dtype=np.float32)
                mandel_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, mandel_output.nbytes)
                
                prg.mandelbrot(
                    self.queue, 
                    (width, height), 
                    None,
                    mandel_buf, 
                    np.int32(width), 
                    np.int32(height),
                    np.int32(max_mandelbrot_iter)
                )
                
                # 等待所有操作完成
                self.queue.finish()
                
                iteration += 1
                iter_time = time.time() - iter_start
                elapsed = time.time() - start_time
                
                # 输出状态
                print(f"迭代 {iteration:4d} | "
                      f"耗时: {iter_time:.3f}s | "
                      f"总时间: {elapsed:.1f}s | "
                      f"矩阵: {N}x{N} | "
                      f"分形: {width}x{height}")
                
                # 清理缓冲区
                A_buf.release()
                B_buf.release()
                C_buf.release()
                data_buf.release()
                mandel_buf.release()
                
        except KeyboardInterrupt:
            print("\n\n收到停止信号...")
        except Exception as e:
            print(f"\n错误: {e}")
        finally:
            total_time = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"测试完成")
            print(f"总迭代次数: {iteration}")
            print(f"总运行时间: {total_time:.2f} 秒")
            print(f"平均每次迭代: {total_time/iteration:.3f} 秒" if iteration > 0 else "")
            print(f"{'='*60}")
    
    def start(self):
        """启动测试"""
        self.running = True
        self.run_stress_test()
    
    def stop(self):
        """停止测试"""
        self.running = False


def main():
    print("=" * 60)
    print("Intel GPU 压力测试工具".center(60))
    print("=" * 60)
    
    # 获取用户输入
    try:
        intensity = input("\n输入强度 (10-100，默认50): ").strip()
        intensity = int(intensity) if intensity else 50
        intensity = max(10, min(100, intensity))
    except ValueError:
        intensity = 50
    
    print(f"\n使用强度: {intensity}%")
    print("提示: 强度越高，GPU 负载越大，发热也会增加")
    
    # 创建并启动测试
    test = IntelGPUStressTest(intensity=intensity)
    
    try:
        test.start()
    except KeyboardInterrupt:
        print("\n\n正在停止...")
        test.stop()


if __name__ == "__main__":
    main()