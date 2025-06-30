import sys
sys.path.append('src')

from src.evaluator.enhanced_evaluator import EnhancedDriverEvaluator

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

def test_enhanced_evaluation():
    evaluator = EnhancedDriverEvaluator()
    
    prompt_info = {
        'id': 'enhanced_test',
        'difficulty': 'intermediate'
    }
    
    results = evaluator.comprehensive_evaluation(test_code, prompt_info)
    
    print("=== enhanced evaluation results ===")
    print(f"enhanced score: {results['enhanced_score']}")
    print(f"clang available: {results['metadata']['clang_available']}")
    
    # clang results
    clang_results = results.get('clang_analysis', {})
    if clang_results.get('analysis_successful'):
        summary = clang_results.get('summary', {})
        print(f"\nclang analysis:")
        print(f"  total issues: {summary.get('total_issues', 0)}")
        print(f"  clang score: {summary.get('clang_score', 0)}")
        print(f"  by severity: {summary.get('by_severity', {})}")
        print(f"  by category: {summary.get('by_category', {})}")
    else:
        print(f"\nclang analysis: {clang_results.get('error', 'failed')}")
    
    # detailed report
    report = results.get('detailed_report', {})
    exec_summary = report.get('executive_summary', {})
    print(f"\nexecutive summary:")
    print(f"  overall quality: {exec_summary.get('overall_quality', 'unknown')}")
    print(f"  primary strengths: {exec_summary.get('primary_strengths', [])}")
    print(f"  primary concerns: {exec_summary.get('primary_concerns', [])}")
    
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"\nrecommendations:")
        for rec in recommendations[:5]:
            print(f"  - {rec}")

if __name__ == "__main__":
    test_enhanced_evaluation()
