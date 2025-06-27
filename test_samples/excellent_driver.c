#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/slab.h>

#define DEVICE_NAME "excellent_driver"
#define BUFFER_SIZE 1024
#define MINOR_COUNT 1

static dev_t dev_number;
static struct cdev char_cdev;
static struct class *device_class;
static struct device *char_device;
static char *device_buffer;

static int device_open(struct inode *inode, struct file *file) {
    return 0;
}

static int device_release(struct inode *inode, struct file *file) {
    return 0;
}

static ssize_t device_read(struct file *file, char __user *user_buffer, 
                          size_t count, loff_t *offset) {
    if (*offset >= BUFFER_SIZE)
        return 0;
    
    if (*offset + count > BUFFER_SIZE)
        count = BUFFER_SIZE - *offset;
    
    if (copy_to_user(user_buffer, device_buffer + *offset, count))
        return -EFAULT;
    
    *offset += count;
    return count;
}

static ssize_t device_write(struct file *file, const char __user *user_buffer,
                           size_t count, loff_t *offset) {
    if (*offset >= BUFFER_SIZE)
        return -ENOSPC;
    
    if (*offset + count > BUFFER_SIZE)
        count = BUFFER_SIZE - *offset;
    
    if (copy_from_user(device_buffer + *offset, user_buffer, count))
        return -EFAULT;
    
    *offset += count;
    return count;
}

static const struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = device_open,
    .release = device_release,
    .read = device_read,
    .write = device_write,
};

static int __init excellent_init(void) {
    int ret;
    
    ret = alloc_chrdev_region(&dev_number, 0, MINOR_COUNT, DEVICE_NAME);
    if (ret < 0) {
        pr_err("Failed to allocate device number\n");
        return ret;
    }
    
    cdev_init(&char_cdev, &fops);
    char_cdev.owner = THIS_MODULE;
    
    ret = cdev_add(&char_cdev, dev_number, MINOR_COUNT);
    if (ret < 0) {
        pr_err("Failed to add character device\n");
        goto cleanup_chrdev;
    }
    
    device_buffer = kmalloc(BUFFER_SIZE, GFP_KERNEL);
    if (!device_buffer) {
        ret = -ENOMEM;
        goto cleanup_cdev;
    }
    
    pr_info("Excellent driver loaded successfully\n");
    return 0;

cleanup_cdev:
    cdev_del(&char_cdev);
cleanup_chrdev:
    unregister_chrdev_region(dev_number, MINOR_COUNT);
    return ret;
}

static void __exit excellent_exit(void) {
    kfree(device_buffer);
    cdev_del(&char_cdev);
    unregister_chrdev_region(dev_number, MINOR_COUNT);
    pr_info("Excellent driver unloaded\n");
}

module_init(excellent_init);
module_exit(excellent_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Expert Developer");
MODULE_DESCRIPTION("High-quality character device driver");
MODULE_VERSION("1.0");