SAMPLE_PROMPTS = [
    {
        "id": "basic_char_driver",
        "prompt": "Create a simple character device driver that supports basic read/write operations with a 1KB internal buffer.",
        "expected_patterns": [
            "file_operations",
            "cdev_init",
            "copy_from_user",
            "copy_to_user",
            "module_init",
            "module_exit",
            "MODULE_LICENSE"
        ],
        "difficulty": "beginner",
        "max_score": 100
    },
    {
        "id": "platform_driver",
        "prompt": "Implement a platform device driver for a memory-mapped GPIO controller with interrupt support.",
        "expected_patterns": [
            "platform_driver",
            "ioremap",
            "request_irq",
            "free_irq",
            "iounmap",
            "module_init",
            "module_exit"
        ],
        "difficulty": "intermediate",
        "max_score": 100
    },
    {
        "id": "proc_interface",
        "prompt": "Create a kernel module that creates a /proc entry for reading system information.",
        "expected_patterns": [
            "proc_create",
            "proc_remove",
            "seq_file",
            "module_init",
            "module_exit"
        ],
        "difficulty": "beginner",
        "max_score": 100
    }
]

# Sample good and bad driver codes for testing
SAMPLE_CODES = {
    "good_basic_driver": '''
#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

#define DEVICE_NAME "mydriver"
#define BUFFER_SIZE 1024

static int major_number;
static struct cdev my_cdev;
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
MODULE_AUTHOR("Test Author");
MODULE_DESCRIPTION("A simple character driver");
''',
    
    "bad_basic_driver": '''
#include <stdio.h>
#include <stdlib.h>

char buffer[1000];

int main() {
    char input[2000];  // Potential overflow
    printf("Enter data: ");
    gets(input);  // Dangerous function
    strcpy(buffer, input);  // No bounds checking
    printf("Data: %s", buffer);
    return 0;
}
'''
}
