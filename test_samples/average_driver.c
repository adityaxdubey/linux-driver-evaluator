#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>

#define DEVICE_NAME "average_driver"
static int major_number;

static int device_open(struct inode *inode, struct file *file) {
    return 0;
}

static int device_release(struct inode *inode, struct file *file) {
    return 0;
}

static struct file_operations fops = {
    .open = device_open,
    .release = device_release,
};

static int __init average_init(void) {
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        return major_number;
    }
    return 0;
}

static void __exit average_exit(void) {
    unregister_chrdev(major_number, DEVICE_NAME);
}

module_init(average_init);
module_exit(average_exit);
MODULE_LICENSE("GPL");