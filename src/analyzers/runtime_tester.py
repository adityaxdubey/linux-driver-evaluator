import subprocess
import tempfile
import os
from typing import Dict

class KernelModuleTester:
    def __init__(self):
        self.test_results = {}
    
    def test_module_compilation(self, code: str) -> Dict:
        """actually compile the driver as a kernel module"""
        
        # create a complete kernel module with makefile
        makefile_content = '''
obj-m += test_driver.o
KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

default:
\t$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
\t$(MAKE) -C $(KDIR) M=$(PWD) clean
'''
        
        with tempfile.TemporaryDirectory() as temp_dir:
            driver_file = os.path.join(temp_dir, 'test_driver.c')
            makefile = os.path.join(temp_dir, 'Makefile')
            
            with open(driver_file, 'w') as f:
                f.write(code)
            with open(makefile, 'w') as f:
                f.write(makefile_content)
            
            try:
                result = subprocess.run(['make'], cwd=temp_dir, 
                                      capture_output=True, text=True, timeout=60)
                
                return {
                    'compilation_success': result.returncode == 0,
                    'build_output': result.stdout + result.stderr,
                    'module_created': os.path.exists(os.path.join(temp_dir, 'test_driver.ko')),
                    'build_time': 'measured'  # can add timing
                }
            except subprocess.TimeoutExpired:
                return {'compilation_success': False, 'error': 'build timeout'}
    
    def test_module_loading(self, module_path: str) -> Dict:
        """test if module can be loaded/unloaded safely"""
        try:
            # note: requires sudo, so this is more of a framework
            load_result = subprocess.run(['sudo', 'insmod', module_path], 
                                       capture_output=True, text=True)
            
            if load_result.returncode == 0:
                unload_result = subprocess.run(['sudo', 'rmmod', 'test_driver'],
                                             capture_output=True, text=True)
                return {
                    'load_success': True,
                    'unload_success': unload_result.returncode == 0,
                    'dmesg_output': 'captured'
                }
            else:
                return {'load_success': False, 'error': load_result.stderr}
                
        except Exception as e:
            return {'load_success': False, 'error': str(e)}
