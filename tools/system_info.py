import logging
import psutil
import platform
import shutil
import GPUtil

class SystemInfoTool:
    def __init__(self):
        self.name = "system_info"
        self.description = "Get current system resource usage (CPU, Memory, Disk, GPU, OS)."
        self.logger = logging.getLogger("SystemInfoTool")

    def execute(self, query_type="all"):
        try:
            results = []

            
            logger_prefix = f"[SystemInfoTool] Query: '{query_type}'"
            self.logger.info(logger_prefix)
            
            qt = query_type.lower()
            fetch_all = "all" in qt or "system" in qt or "spec" in qt or "specs" in qt

            if fetch_all or "os" in qt or "platform" in qt or "machine" in qt or "processor" in qt or "cpu" in qt:
                uname = platform.uname()
                os_info = (
                    f"System: {uname.system}\n"
                    f"Platform: {platform.platform()}\n"
                    f"Processor: {uname.processor}"
                )
                results.append("--- System/OS Info ---\n" + os_info)

            if fetch_all or "memory" in qt or "ram" in qt:
                mem = psutil.virtual_memory()
                total_mem_gb = mem.total / (1024 ** 3)
                available_mem_gb = mem.available / (1024 ** 3)
                mem_percent = mem.percent
                
                mem_str = (
                    f"Total Memory: {total_mem_gb:.2f} GB\n"
                    f"Available Memory: {available_mem_gb:.2f} GB\n"
                    f"Memory Used: {mem_percent}%"
                )
                results.append("--- Memory Info ---\n" + mem_str)

            if fetch_all or "disk" in qt or "storage" in qt or "space" in qt:
                path = "/"
                if platform.system() == "Windows":
                    path = "C:\\"
                
                disk = shutil.disk_usage(path)
                total_disk_gb = disk.total / (1024 ** 3)
                free_disk_gb = disk.free / (1024 ** 3)
                used_disk_gb = disk.used / (1024 ** 3)
                disk_percent = (disk.used / disk.total) * 100

                disk_str = (
                    f"Total Disk Space: {total_disk_gb:.2f} GB\n"
                    f"Free Disk Space: {free_disk_gb:.2f} GB\n"
                    f"Disk Used: {disk_percent:.1f}%"
                )
                results.append(f"--- Disk Info ({path}) ---\n" + disk_str)

            # --- GPU Info ---
            if fetch_all or "gpu" in qt or "graphics" in qt or "card" in qt:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        for gpu in gpus:
                            gpu_str = (
                                f"GPU: {gpu.name}\n"
                                f"VRAM Used: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB\n"
                                f"Load: {gpu.load*100:.1f}%"
                            )
                            results.append("--- GPU Info ---\n" + gpu_str)
                    elif "gpu" in qt: 
                        results.append("--- GPU Info ---\nNo dedicated NVIDIA GPU detected.")
                except Exception as e:
                    self.logger.error(f"Error fetching GPU info: {e}")
                    if "gpu" in qt:
                        results.append(f"--- GPU Info ---\nError fetching GPU info.")

            if not results:
                cpu_usage = psutil.cpu_percent(interval=0.1)
                return f"CPU Usage: {cpu_usage}% (Specify 'os', 'memory', 'disk' for more info)"

            return "\n\n".join(results)

        except Exception as e:
            self.logger.error(f"Error fetching system stats: {e}")
            return f"Error gathering system stats: {e}"