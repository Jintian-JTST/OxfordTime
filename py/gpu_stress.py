"""
Intel GPU 超强压力测试程序
专为 Intel Arc Graphics 优化 - 多线程并行压榨 GPU
"""

import numpy as np
import time
import sys
from threading import Thread
from multiprocessing import Process, cpu_count

# 检查 PyOpenCL
try:
    import pyopencl as cl
    print("✓ PyOpenCL 已安装")
except ImportError:
    print("❌ 未安装 PyOpenCL")
    print("请运行: pip install pyopencl")
    sys.exit(1)


class IntelGPUStressTest:
    def __init__(self, intensity=50, worker_id=0):
        self.intensity = intensity
        self.running = False
        self.worker_id = worker_id
        self.ctx = None
        self.queue = None
        self.setup_opencl()
    
    def setup_opencl(self):
        """设置 OpenCL 环境"""
        platforms = cl.get_platforms()
        intel_device = None
        
        for platform in platforms:
            devices = platform.get_devices()
            for device in devices:
                if "Intel" in device.vendor or "Intel" in device.name:
                    if device.type == cl.device_type.GPU:
                        intel_device = device
                        break
            if intel_device:
                break
        
        if intel_device is None:
            intel_device = platforms[0].get_devices()[0]
        
        self.ctx = cl.Context([intel_device])
        # 创建多个命令队列以增加并发
        self.queues = [cl.CommandQueue(self.ctx) for _ in range(4)]
        
        if self.worker_id == 0:
            print(f"\n使用设备: {intel_device.name}")
            print(f"计算单元: {intel_device.max_compute_units}")
            print(f"全局内存: {intel_device.global_mem_size / 1024**3:.2f} GB")
    
    def run_stress_test(self):
        """运行超强 GPU 压力测试"""
        if self.worker_id == 0:
            print(f"\n{'='*60}")
            print(f"开始 Intel GPU 超强压力测试 (强度: {self.intensity}%)")
            print(f"{'='*60}\n")
        
        # 更激进的 OpenCL 内核
        kernel_code = """
        __kernel void extreme_compute(
            __global float* data,
            const int iterations,
            const float time_offset)
        {
            int gid = get_global_id(0);
            float val = data[gid];
            
            // 极其密集的计算
            for (int i = 0; i < iterations; i++) {
                // 多重三角函数嵌套
                val = sin(val * 3.14159f + time_offset) * cos(val * 2.71828f);
                val = tan(val * 0.5f) + sin(val * val);
                
                // 指数和对数运算
                val = exp(val * 0.1f) - exp(-val * 0.1f);
                val = log(fabs(val) + 1.0f) * sqrt(fabs(val) + 1.0f);
                
                // 幂运算
                val = pow(fabs(val) + 0.1f, 0.7f);
                val = pow(fabs(val), 1.3f) * 0.5f;
                
                // 复杂的数学组合
                val = sinh(val * 0.3f) * cosh(val * 0.2f);
                val = atan(val) * asin(val * 0.5f);
            }
            
            data[gid] = val;
        }
        
        __kernel void matrix_multiply_heavy(
            __global const float* A,
            __global const float* B,
            __global float* C,
            const int N)
        {
            int row = get_global_id(0);
            int col = get_global_id(1);
            
            if (row < N && col < N) {
                float sum = 0.0f;
                // 多次矩阵乘法
                for (int repeat = 0; repeat < 3; repeat++) {
                    for (int k = 0; k < N; k++) {
                        float a_val = A[row * N + k];
                        float b_val = B[k * N + col];
                        sum += a_val * b_val * sin(a_val) * cos(b_val);
                    }
                }
                C[row * N + col] = sum;
            }
        }
        
        __kernel void mandelbrot_extreme(
            __global float* output,
            const int width,
            const int height,
            const int max_iter,
            const float zoom,
            const float offset_x,
            const float offset_y)
        {
            int x = get_global_id(0);
            int y = get_global_id(1);
            
            if (x >= width || y >= height) return;
            
            float cx = (x - width/2.0f) * 4.0f / (width * zoom) + offset_x;
            float cy = (y - height/2.0f) * 4.0f / (height * zoom) + offset_y;
            
            float zx = 0.0f, zy = 0.0f;
            int iter = 0;
            
            // 更多迭代次数
            while (zx*zx + zy*zy < 16.0f && iter < max_iter) {
                float tmp = zx*zx - zy*zy + cx;
                zy = 2.0f * zx * zy + cy;
                zx = tmp;
                
                // 额外计算增加负载
                zx = sin(zx * 0.1f) + zx;
                zy = cos(zy * 0.1f) + zy;
                
                iter++;
            }
            
            output[y * width + x] = (float)iter / max_iter;
        }
        
        __kernel void crypto_hash_simulation(
            __global float* data,
            const int rounds)
        {
            int gid = get_global_id(0);
            float val = data[gid];
            
            // 模拟加密哈希计算
            for (int r = 0; r < rounds; r++) {
                val = fmod(val * 1103515245.0f + 12345.0f, 2147483648.0f);
                val = sin(val * 0.001f) * 1000.0f;
                val = pow(fabs(val), 0.333f);
            }
            
            data[gid] = val;
        }
        """
        
        prg = cl.Program(self.ctx, kernel_code).build()
        
        # 超大规模参数
        scale = self.intensity / 50.0  # 归一化比例
        matrix_size = int(1500 * scale)
        compute_size = int(10000000 * scale)  # 1000万元素
        compute_iters = int(200 * scale)
        mandelbrot_size = int(2000 * scale)
        max_mandelbrot_iter = int(500 * scale)
        crypto_rounds = int(100 * scale)
        
        iteration = 0
        start_time = time.time()
        
        try:
            while self.running:
                iter_start = time.time()
                mf = cl.mem_flags
                
                # 并行执行多个任务
                tasks = []
                
                # ========== 任务 1: 超大矩阵乘法 (多个) ==========
                for q_idx in range(len(self.queues)):
                    N = matrix_size
                    A = np.random.rand(N, N).astype(np.float32)
                    B = np.random.rand(N, N).astype(np.float32)
                    C = np.zeros((N, N), dtype=np.float32)
                    
                    A_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=A)
                    B_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=B)
                    C_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, C.nbytes)
                    
                    prg.matrix_multiply_heavy(
                        self.queues[q_idx], 
                        (N, N), 
                        None, 
                        A_buf, B_buf, C_buf, np.int32(N)
                    )
                    tasks.append((A_buf, B_buf, C_buf))
                
                # ========== 任务 2: 超大规模计算密集型操作 ==========
                data = np.random.rand(compute_size).astype(np.float32)
                data_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=data)
                
                for q_idx in range(len(self.queues)):
                    prg.extreme_compute(
                        self.queues[q_idx], 
                        (compute_size,), 
                        None,
                        data_buf, 
                        np.int32(compute_iters),
                        np.float32(iteration * 0.1)
                    )
                
                # ========== 任务 3: 多个 Mandelbrot 分形 ==========
                width = height = mandelbrot_size
                for q_idx in range(len(self.queues)):
                    mandel_output = np.zeros(width * height, dtype=np.float32)
                    mandel_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, mandel_output.nbytes)
                    
                    prg.mandelbrot_extreme(
                        self.queues[q_idx], 
                        (width, height), 
                        None,
                        mandel_buf, 
                        np.int32(width), 
                        np.int32(height),
                        np.int32(max_mandelbrot_iter),
                        np.float32(1.0 + iteration * 0.01),
                        np.float32(np.sin(iteration * 0.1)),
                        np.float32(np.cos(iteration * 0.1))
                    )
                
                # ========== 任务 4: 加密哈希模拟 ==========
                crypto_data = np.random.rand(compute_size).astype(np.float32)
                crypto_buf = cl.Buffer(self.ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=crypto_data)
                
                for q_idx in range(len(self.queues)):
                    prg.crypto_hash_simulation(
                        self.queues[q_idx],
                        (compute_size,),
                        None,
                        crypto_buf,
                        np.int32(crypto_rounds)
                    )
                
                # 等待所有队列完成
                for queue in self.queues:
                    queue.finish()
                
                iteration += 1
                iter_time = time.time() - iter_start
                elapsed = time.time() - start_time
                
                if self.worker_id == 0:
                    print(f"Worker {self.worker_id} | 迭代 {iteration:4d} | "
                          f"耗时: {iter_time:.3f}s | "
                          f"总时间: {elapsed:.1f}s | "
                          f"数据量: {compute_size/1e6:.1f}M元素")
                
                # 清理
                for buf_tuple in tasks:
                    for buf in buf_tuple:
                        buf.release()
                data_buf.release()
                crypto_buf.release()
                
        except KeyboardInterrupt:
            if self.worker_id == 0:
                print("\n收到停止信号...")
        except Exception as e:
            print(f"\nWorker {self.worker_id} 错误: {e}")
        finally:
            if self.worker_id == 0:
                total_time = time.time() - start_time
                print(f"\n{'='*60}")
                print(f"Worker {self.worker_id} 完成: {iteration} 次迭代, {total_time:.2f} 秒")
                print(f"{'='*60}")
    
    def start(self):
        self.running = True
        self.run_stress_test()
    
    def stop(self):
        self.running = False


def worker_process(intensity, worker_id):
    """工作进程"""
    test = IntelGPUStressTest(intensity=intensity, worker_id=worker_id)
    test.start()


def main():
    print("=" * 60)
    print("Intel GPU 超强压力测试工具".center(60))
    print("=" * 60)
    
    try:
        intensity = input("\n输入强度 (10-100，默认80): ").strip()
        intensity = int(intensity) if intensity else 80
        intensity = max(10, min(100, intensity))
    except ValueError:
        intensity = 80
    
    try:
        num_workers = input(f"输入并行工作进程数 (1-{cpu_count()}, 默认4): ").strip()
        num_workers = int(num_workers) if num_workers else 4
        num_workers = max(1, min(cpu_count(), num_workers))
    except ValueError:
        num_workers = 4
    
    print(f"\n使用强度: {intensity}%")
    print(f"并行进程: {num_workers} 个")
    print("⚠️  警告: 这将极大地压榨 GPU，请确保散热良好！")
    print("按 Ctrl+C 停止测试\n")
    
    input("按 Enter 开始测试...")
    
    # 创建多个工作进程
    processes = []
    for i in range(num_workers):
        p = Process(target=worker_process, args=(intensity, i))
        p.start()
        processes.append(p)
        time.sleep(0.2)  # 错开启动
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n\n正在停止所有进程...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()


if __name__ == "__main__":
    main()