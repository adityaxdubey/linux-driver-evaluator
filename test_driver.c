// test_driver.c - A simple test driver
#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "testdriver"
#define BUFFER_SIZE 1024

static int major_number;
static char device_buffer[BUFFER_SIZE];

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
    return 0;
}

static void __exit driver_exit(void) {
    unregister_chrdev(major_number, DEVICE_NAME);
}

module_init(driver_init);
module_exit(driver_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Test Author");
MODULE_DESCRIPTION("A test character driver");
