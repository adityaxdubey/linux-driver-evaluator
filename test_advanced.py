import sys
sys.path.append('src')

from src.evaluator.advanced_evaluator import AdvancedDriverEvaluator

test_code = '''
#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

#define DEVICE_NAME "testdev"
#define BUFFER_SIZE 1024

static int major_number;
static char *device_buffer;

static int device_open(struct inode *inode, struct file *file) {
    return 0;
}

static int device_release(struct inode *inode, struct file *file) {
    return 0;
}

static ssize_t device_read(struct file *file, char __user *user_buffer, size_t size, loff_t *offset) {
    if (copy_to_user(user_buffer, device_buffer, size)) {
        return -EFAULT;
    }
    return size;
}

static ssize_t device_write(struct file *file, const char __user *user_buffer, size_t size, loff_t *offset) {
    if (size > BUFFER_SIZE) {
        return -EINVAL;
    }
    if (copy_from_user(device_buffer, user_buffer, size)) {
        return -EFAULT;
    }
    return size;
}

static struct file_operations fops = {
    .open = device_open,
    .release = device_release,
    .read = device_read,
    .write = device_write,
};

static int __init driver_init(void) {
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        return major_number;
    }
    
    device_buffer = kmalloc(BUFFER_SIZE, GFP_KERNEL);
    if (!device_buffer) {
        unregister_chrdev(major_number, DEVICE_NAME);
        return -ENOMEM;
    }
    
    return 0;
}

static void __exit driver_exit(void) {
    kfree(device_buffer);
    unregister_chrdev(major_number, DEVICE_NAME);
}

module_init(driver_init);
module_exit(driver_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("test");
'''

def test_advanced_evaluation():
    evaluator = AdvancedDriverEvaluator()
    
    prompt_info = {
        'id': 'advanced_test',
        'difficulty': 'intermediate'
    }
    
    results = evaluator.comprehensive_evaluation(test_code, prompt_info)
    
    print("=== advanced evaluation results ===")
    print(f"comprehensive score: {results['comprehensive_score']}")
    
    if 'ast_analysis' in results and 'error' not in results['ast_analysis']:
        ast = results['ast_analysis']
        print(f"\nsecurity analysis:")
        print(f"  total issues: {ast.get('security_analysis', {}).get('total_issues', 0)}")
        print(f"  risk score: {ast.get('security_analysis', {}).get('risk_score', 0)}")
        
        print(f"\nperformance analysis:")
        print(f"  performance score: {ast.get('performance_analysis', {}).get('performance_score', 0)}")
        
        print(f"\nmemory analysis:")
        print(f"  memory score: {ast.get('memory_analysis', {}).get('memory_score', 0)}")
        allocs = ast.get('memory_analysis', {}).get('allocations', {})
        print(f"  allocated vars: {allocs.get('allocated', [])}")
        print(f"  freed vars: {allocs.get('freed', [])}")
        
        print(f"\ncontrol flow:")
        cf = ast.get('control_flow_analysis', {})
        print(f"  average complexity: {cf.get('average_complexity', 0):.1f}")
        print(f"  function complexities: {cf.get('function_complexities', {})}")
        
        print(f"\nkernel compliance:")
        comp = ast.get('kernel_compliance', {})
        print(f"  compliance score: {comp.get('compliance_score', 0)}/{comp.get('max_compliance_score', 45)}")
    
    if 'runtime_analysis' in results:
        runtime = results['runtime_analysis']
        print(f"\nruntime analysis:")
        print(f"  memory operations: {runtime.get('memory_operations', 0)}")
        print(f"  io operations: {runtime.get('io_operations', 0)}")
        print(f"  sync operations: {runtime.get('synchronization_operations', 0)}")
        print(f"  estimated memory usage: {runtime.get('estimated_memory_usage', 0)} bytes")

if __name__ == "__main__":
    test_advanced_evaluation()
